import time
import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Dict, Any, Optional, List, Union, Generator
from enum import Enum
from dataclasses import dataclass

# Database drivers
try:
    import psycopg2
    from psycopg2 import pool as pg_pool
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    pg_pool = None
    RealDictCursor = None

try:
    import pyodbc
except ImportError:
    pyodbc = None

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = None

from common_utils import _log, config_loader

logger = _log()
config_dict = config_loader()


class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MSSQL = "mssql"
    AWS_TIMESTREAM = "aws_timestream"


@dataclass
class ConnectionConfig:
    """Database connection configuration."""
    db_type: DatabaseType
    host: str
    port: int
    db_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    # AWS Timestream specific
    credentials: Optional[str] = None
    table_name: Optional[str] = None
    # Connection pool settings
    min_connections: int = 1
    max_connections: int = 10
    connection_timeout: int = 30
    idle_timeout: int = 300


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass


class DatabaseOperationError(Exception):
    """Custom exception for database operation errors."""
    pass


class BaseDatabaseConnector(ABC):
    """Abstract base class for database connectors."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._pool = None
        self._lock = threading.Lock()
        self._last_health_check = 0
        self._health_check_interval = 60  # seconds
    
    @abstractmethod
    def _create_connection(self) -> Any:
        """Create a single database connection."""
        pass
    
    @abstractmethod
    def _create_pool(self) -> Any:
        """Create connection pool."""
        pass
    
    @abstractmethod
    def _get_connection_from_pool(self) -> Any:
        """Get connection from pool."""
        pass
    
    @abstractmethod
    def _return_connection_to_pool(self, conn: Any) -> None:
        """Return connection to pool."""
        pass
    
    @abstractmethod
    def _close_pool(self) -> None:
        """Close connection pool."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results."""
        pass
    
    @abstractmethod
    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check database connection health."""
        pass
    
    def initialize_pool(self) -> None:
        """Initialize connection pool."""
        with self._lock:
            if self._pool is None:
                try:
                    self._pool = self._create_pool()
                    logger.info(f"Database pool initialized for {self.config.db_type.value}")
                except Exception as e:
                    logger.error(f"Failed to initialize database pool: {str(e)}")
                    raise DatabaseConnectionError(f"Pool initialization failed: {str(e)}")
    
    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """Context manager for database connections."""
        if self._pool is None:
            self.initialize_pool()
        
        conn = None
        try:
            conn = self._get_connection_from_pool()
            yield conn
        except Exception as e:
            logger.error(f"Database operation error: {str(e)}")
            raise DatabaseOperationError(f"Operation failed: {str(e)}")
        finally:
            if conn is not None:
                self._return_connection_to_pool(conn)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        with self._lock:
            if self._pool is not None:
                self._close_pool()
                self._pool = None
                logger.info(f"Database pool closed for {self.config.db_type.value}")


class PostgreSQLConnector(BaseDatabaseConnector):
    """PostgreSQL database connector."""
    
    def __init__(self, config: ConnectionConfig):
        if psycopg2 is None:
            raise ImportError("psycopg2 is required for PostgreSQL connections")
        super().__init__(config)
    
    def _create_connection(self) -> Any:
        """Create PostgreSQL connection."""
        return psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.db_name,
            user=self.config.username,
            password=self.config.password,
            connect_timeout=self.config.connection_timeout
        )
    
    def _create_pool(self) -> Any:
        """Create PostgreSQL connection pool."""
        return pg_pool.ThreadedConnectionPool(
            minconn=self.config.min_connections,
            maxconn=self.config.max_connections,
            host=self.config.host,
            port=self.config.port,
            database=self.config.db_name,
            user=self.config.username,
            password=self.config.password,
            connect_timeout=self.config.connection_timeout
        )
    
    def _get_connection_from_pool(self) -> Any:
        """Get connection from PostgreSQL pool."""
        return self._pool.getconn()
    
    def _return_connection_to_pool(self, conn: Any) -> None:
        """Return connection to PostgreSQL pool."""
        self._pool.putconn(conn)
    
    def _close_pool(self) -> None:
        """Close PostgreSQL pool."""
        self._pool.closeall()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
    
    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
    
    def health_check(self) -> bool:
        """Check PostgreSQL connection health."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.warning(f"PostgreSQL health check failed: {str(e)}")
            return False


class MSSQLConnector(BaseDatabaseConnector):
    """Microsoft SQL Server database connector."""
    
    def __init__(self, config: ConnectionConfig):
        if pyodbc is None:
            raise ImportError("pyodbc is required for MSSQL connections")
        super().__init__(config)
        self._connection_string = self._build_connection_string()
        self._available_connections = []
        self._used_connections = set()
    
    def _build_connection_string(self) -> str:
        """Build MSSQL connection string."""
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.config.host},{self.config.port};"
            f"DATABASE={self.config.db_name};"
            f"UID={self.config.username};"
            f"PWD={self.config.password};"
            f"Connection Timeout={self.config.connection_timeout};"
        )
    
    def _create_connection(self) -> Any:
        """Create MSSQL connection."""
        return pyodbc.connect(self._connection_string)
    
    def _create_pool(self) -> Any:
        """Create MSSQL connection pool (manual implementation)."""
        # pyodbc doesn't have built-in pooling, so we implement our own
        for _ in range(self.config.min_connections):
            conn = self._create_connection()
            self._available_connections.append(conn)
        return self._available_connections
    
    def _get_connection_from_pool(self) -> Any:
        """Get connection from MSSQL pool."""
        with self._lock:
            if self._available_connections:
                conn = self._available_connections.pop()
                self._used_connections.add(conn)
                return conn
            elif len(self._used_connections) < self.config.max_connections:
                conn = self._create_connection()
                self._used_connections.add(conn)
                return conn
            else:
                raise DatabaseConnectionError("Connection pool exhausted")
    
    def _return_connection_to_pool(self, conn: Any) -> None:
        """Return connection to MSSQL pool."""
        with self._lock:
            if conn in self._used_connections:
                self._used_connections.remove(conn)
                # Check if connection is still valid
                try:
                    conn.execute("SELECT 1")
                    self._available_connections.append(conn)
                except:
                    conn.close()
    
    def _close_pool(self) -> None:
        """Close MSSQL pool."""
        with self._lock:
            for conn in self._available_connections + list(self._used_connections):
                try:
                    conn.close()
                except:
                    pass
            self._available_connections.clear()
            self._used_connections.clear()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
    
    def health_check(self) -> bool:
        """Check MSSQL connection health."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"MSSQL health check failed: {str(e)}")
            return False


class AWSTimestreamConnector(BaseDatabaseConnector):
    """AWS Timestream database connector."""
    
    def __init__(self, config: ConnectionConfig):
        if boto3 is None:
            raise ImportError("boto3 is required for AWS Timestream connections")
        super().__init__(config)
        self._client = None
    
    def _create_connection(self) -> Any:
        """Create AWS Timestream client."""
        # AWS SDK handles connection pooling internally
        return boto3.client('timestream-query')
    
    def _create_pool(self) -> Any:
        """Create Timestream client (no pooling needed)."""
        self._client = self._create_connection()
        return self._client
    
    def _get_connection_from_pool(self) -> Any:
        """Get Timestream client."""
        return self._client
    
    def _return_connection_to_pool(self, conn: Any) -> None:
        """Return connection (no-op for Timestream)."""
        pass
    
    def _close_pool(self) -> None:
        """Close Timestream client."""
        if self._client:
            self._client.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute Timestream query."""
        try:
            with self.get_connection() as client:
                response = client.query(QueryString=query)
                
                # Parse Timestream response
                results = []
                column_info = response['ColumnInfo']
                
                for row in response['Rows']:
                    row_dict = {}
                    for i, data in enumerate(row['Data']):
                        column_name = column_info[i]['Name']
                        # Handle different data types
                        if 'ScalarValue' in data:
                            row_dict[column_name] = data['ScalarValue']
                        elif 'NullValue' in data:
                            row_dict[column_name] = None
                        else:
                            row_dict[column_name] = str(data)
                    results.append(row_dict)
                
                return results
        except ClientError as e:
            logger.error(f"Timestream query error: {str(e)}")
            raise DatabaseOperationError(f"Timestream query failed: {str(e)}")
    
    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute Timestream write operation."""
        # Timestream uses different APIs for writes
        raise NotImplementedError("Use write_records method for Timestream writes")
    
    def write_records(self, records: List[Dict[str, Any]]) -> bool:
        """Write records to Timestream."""
        try:
            write_client = boto3.client('timestream-write')
            
            # Convert records to Timestream format
            timestream_records = []
            for record in records:
                ts_record = {
                    'Time': str(int(time.time() * 1000)),  # Current timestamp in milliseconds
                    'TimeUnit': 'MILLISECONDS',
                    'Dimensions': [],
                    'MeasureName': record.get('measure_name', 'default'),
                    'MeasureValue': str(record.get('measure_value', 0)),
                    'MeasureValueType': record.get('measure_value_type', 'DOUBLE')
                }
                
                # Add dimensions
                for key, value in record.items():
                    if key not in ['measure_name', 'measure_value', 'measure_value_type', 'time']:
                        ts_record['Dimensions'].append({
                            'Name': key,
                            'Value': str(value)
                        })
                
                timestream_records.append(ts_record)
            
            # Write to Timestream
            response = write_client.write_records(
                DatabaseName=self.config.db_name,
                TableName=self.config.table_name,
                Records=timestream_records
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"Timestream write error: {str(e)}")
            raise DatabaseOperationError(f"Timestream write failed: {str(e)}")
    
    def health_check(self) -> bool:
        """Check Timestream connection health."""
        try:
            with self.get_connection() as client:
                # Simple query to check connectivity
                client.query(QueryString="SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"Timestream health check failed: {str(e)}")
            return False


class DatabaseConnectionManager:
    """Database connection manager factory."""
    
    _instances: Dict[str, BaseDatabaseConnector] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_connector(cls, connection_id: str, connection_config: dict) -> BaseDatabaseConnector:
        """Get database connector instance."""
        with cls._lock:
            if connection_id not in cls._instances:
                cls._instances[connection_id] = cls._create_connector(connection_id, connection_config)
            return cls._instances[connection_id]
    
    @classmethod
    def _create_connector(cls, connection_id: str, connection_config: dict) -> BaseDatabaseConnector:
        """Create database connector based on configuration."""
        try:
            if connection_config:
                if connection_config['dbtype'] in ('postgresql', 'mssql'):
                    config = ConnectionConfig(
                        db_type=DatabaseType(connection_config['dbtype']),
                        host=connection_config['host'],
                        port=connection_config['port'],
                        db_name=connection_config['db_name'],
                        username=connection_config.get('username'),
                        password=connection_config.get('password')
                    )
                else:
                    config = ConnectionConfig(
                        db_type=DatabaseType.AWS_TIMESTREAM,
                        host='',  # Not used for Timestream
                        port=0,  # Not used for Timestream
                        db_name=connection_config['db_name'],
                        table_name=connection_config['table_name'],
                        credentials=connection_config['credentials']
                    )
            else:
                # Load configuration
                if connection_id in config_dict['connections']['database']:
                    db_config = config_dict['connections']['database'][connection_id]
                    config = ConnectionConfig(
                        db_type=DatabaseType(db_config['dbtype']),
                        host=db_config['host'],
                        port=db_config['port'],
                        db_name=db_config['db_name'],
                        username=db_config.get('username'),
                        password=db_config.get('password')
                    )
                elif connection_id in config_dict['connections']['aws_timestream']:
                    ts_config = config_dict['connections']['aws_timestream'][connection_id]
                    config = ConnectionConfig(
                        db_type=DatabaseType.AWS_TIMESTREAM,
                        host='',  # Not used for Timestream
                        port=0,   # Not used for Timestream
                        db_name=ts_config['db_name'],
                        table_name=ts_config['table_name'],
                        credentials=ts_config['credentials']
                    )
                else:
                    raise ValueError(f"Connection configuration not found: {connection_id}")
            
            # Create appropriate connector
            if config.db_type == DatabaseType.POSTGRESQL:
                return PostgreSQLConnector(config)
            elif config.db_type == DatabaseType.MSSQL:
                return MSSQLConnector(config)
            elif config.db_type == DatabaseType.AWS_TIMESTREAM:
                return AWSTimestreamConnector(config)
            else:
                raise ValueError(f"Unsupported database type: {config.db_type}")
                
        except Exception as e:
            logger.error(f"Failed to create connector for {connection_id}: {str(e)}")
            raise DatabaseConnectionError(f"Connector creation failed: {str(e)}")
    
    @classmethod
    def cleanup_all(cls) -> None:
        """Clean up all database connections."""
        with cls._lock:
            for connector in cls._instances.values():
                try:
                    connector.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up connector: {str(e)}")
            cls._instances.clear()
    
    @classmethod
    def health_check_all(cls) -> Dict[str, bool]:
        """Perform health check on all connections."""
        results = {}
        with cls._lock:
            for conn_id, connector in cls._instances.items():
                try:
                    results[conn_id] = connector.health_check()
                except Exception as e:
                    logger.error(f"Health check failed for {conn_id}: {str(e)}")
                    results[conn_id] = False
        return results


# Convenience functions
def get_database_connector(connection_id: str, connection_config: dict) -> BaseDatabaseConnector:
    """Get database connector instance."""
    return DatabaseConnectionManager.get_connector(connection_id, connection_config)


def execute_query(connection_id: str, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute query on specified database."""
    connector = get_database_connector(connection_id)
    return connector.execute_query(query, params)


def execute_non_query(connection_id: str, query: str, params: Optional[tuple] = None) -> int:
    """Execute non-query on specified database."""
    connector = get_database_connector(connection_id)
    return connector.execute_non_query(query, params)


# Example usage
if __name__ == "__main__":
    try:
        # PostgreSQL example
        pg_connector = get_database_connector("aws_db_eh080")
        results = pg_connector.execute_query("SELECT version()")
        logger.info(f"PostgreSQL version: {results}")
        # 修改这一行：使用 execute_non_query 而不是 execute_query
        affected_rows = pg_connector.execute_non_query("UPDATE pod_information SET status = 'running', updated_at = '2025-07-30 09:53:00' WHERE pod_name = 'database_pod';")
        print(type(affected_rows))
        print(f"Affected rows: {affected_rows}")
        
        # MSSQL example
        # mssql_connector = get_database_connector("point_db")
        # results = mssql_connector.execute_query("SELECT @@VERSION")
        # logger.info(f"MSSQL version: {results}")
        #
        # # AWS Timestream example
        # ts_connector = get_database_connector("timestream-otdhl")
        # results = ts_connector.execute_query("SELECT 1 as test")
        # logger.info(f"Timestream test: {results}")
        
        # Health check all connections
        health_status = DatabaseConnectionManager.health_check_all()
        logger.info(f"Health check results: {health_status}")
        
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}")
    finally:
        # Cleanup all connections
        DatabaseConnectionManager.cleanup_all()