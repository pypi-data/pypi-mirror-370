import sys
from pathlib import Path
import threading
import time
import uuid
import json  # 添加这行导入
from typing import Dict, Any, Optional, Callable, List
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import re

# Add parent directory to Python path
current_file = Path(__file__)
src_dir = current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from utils.common_utils import _log, config_loader
from utils.producers.producers import BaseProducer
from utils.consumers.consumers import BaseKafkaConsumer
from utils.db_conn_utils import get_database_connector

import re

logger = _log()
config_dict = config_loader()


class QueryRequestConsumer(BaseKafkaConsumer):
    """处理查询请求的消费者"""
    
    def __init__(self, consumer_id: str, query_processor: Callable[[Dict[str, Any]], Dict[str, Any]]):
        super().__init__(consumer_id)
        self.query_processor = query_processor
        
    def _process_message_data(self, data: Dict[str, Any]) -> None:
        """处理查询请求消息"""
        try:
            logger.info(f"Processing query request: {data.get('query_id', 'unknown')}")
            # 调用查询处理器
            self.query_processor(data)
        except Exception as e:
            logger.error(f"Error processing query request: {str(e)}")


class QueryResponseConsumer(BaseKafkaConsumer):
    """处理查询响应的消费者"""
    
    def __init__(self, consumer_id: str, response_handler: Callable[[Dict[str, Any]], None]):
        super().__init__(consumer_id)
        self.response_handler = response_handler
        
    def _process_message_data(self, data: Dict[str, Any]) -> None:
        """处理查询响应消息"""
        try:
            logger.info(f"Processing query response: {data.get('query_id', 'unknown')}")
            # 调用响应处理器
            self.response_handler(data)
        except Exception as e:
            logger.error(f"Error processing query response: {str(e)}")


class SOADataQueryManager:
    """SOA数据查询管理器
    
    实现以下功能：
    1. 启动两个consumer监听query request和response topics
    2. 启动一个producer发布SQL查询到request topic
    3. 处理查询请求，连接数据库执行查询，并发布结果到response topic
    4. 获取查询结果
    """
    
    def __init__(self, db_connection_id, db_connection_config):
        """
        初始化SOA数据查询管理器
        
        Args:
            db_connection_id: 数据库连接ID，对应config.yaml中的database配置
        """
        self.db_connection_id = db_connection_id
        self.db_connection_config = db_connection_config
        self.db_connector = None
        
        # 初始化producers和consumers
        self.query_request_producer = None
        self.query_response_producer = None
        self.query_request_consumer = None
        self.query_response_consumer = None
        
        # 线程池和控制变量
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False
        self.consumer_threads = []
        
        # 查询结果存储
        self.query_results = {}
        self.result_queues = {}
        self.query_lock = threading.Lock()

        # 初始化生产者和消费者，其中生产者用于往request和response主题中生产数据 消费者1消费request并且放到response中 消费者2消费response并放到队列中
        self.initialize()
        # 启动消费者
        self.start_consumers()
        
        logger.info("SOADataQueryManager initialized")
    
    def initialize(self):
        """初始化所有组件"""
        try:
            # 初始化数据库连接
            self.db_connector = get_database_connector(self.db_connection_id, self.db_connection_config)
            logger.info(f"Database connector initialized for: {self.db_connection_id}")
            
            # 初始化producers
            self.query_request_producer = BaseProducer("query_request")
            self.query_response_producer = BaseProducer("query_response")
            logger.info("Producers initialized")
            
            # 初始化consumers
            self.query_request_consumer = QueryRequestConsumer(
                "query_request", 
                self._handle_query_request
            )

            self.query_response_consumer = QueryResponseConsumer(
                "query_response", 
                self._handle_query_response
            )
            logger.info("Consumers initialized")
            
        except Exception as e:
            logger.error(f"Error initializing SOADataQueryManager: {str(e)}")
            raise
    
    def start_consumers(self):
        """启动消费者线程"""
        if self.running:
            logger.warning("Consumers are already running")
            return
            
        self.running = True

        logger.warning("多线程代码启动")
        
        # 启动query request consumer线程
        request_thread = threading.Thread(
            target=self._run_consumer,
            args=(self.query_request_consumer, "query_request"),
            daemon=True
        )
        request_thread.start()
        self.consumer_threads.append(request_thread)
        
        # 启动query response consumer线程
        response_thread = threading.Thread(
            target=self._run_consumer,
            args=(self.query_response_consumer, "query_response"),
            daemon=True
        )
        response_thread.start()
        self.consumer_threads.append(response_thread)
        
        logger.info("All consumers started")
    
    def _run_consumer(self, consumer: BaseKafkaConsumer, consumer_name: str):
        """运行消费者的内部方法"""
        try:
            logger.info(f"Starting {consumer_name} consumer")
            while self.running:
                try:
                    # 使用较短的超时时间以便能够响应停止信号
                    msg = consumer._poll_and_handle_message(timeout=1.0)
                    logger.info(msg)
                    if msg is None:
                        continue
                    
                    # 反序列化并处理消息
                    data = consumer._deserialize_message(msg)
                    consumer._process_message_data(data)
                    
                except Exception as e:
                    logger.error(f"Error in {consumer_name} consumer: {str(e)}")
                    time.sleep(1)  # 避免快速重试
                    
        except Exception as e:
            logger.error(f"Fatal error in {consumer_name} consumer: {str(e)}")
        finally:
            logger.info(f"{consumer_name} consumer stopped")
    
    def _is_select_query(self, sql_query: str) -> bool:
        """
        判断SQL语句是否为SELECT查询（返回结果集的查询）
        
        Args:
            sql_query: SQL查询语句
            
        Returns:
            bool: True表示是SELECT查询，False表示是非查询操作
        """
        # 移除注释和多余空白字符
        cleaned_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
        cleaned_query = re.sub(r'--.*?\n', '\n', cleaned_query)
        cleaned_query = cleaned_query.strip()
        
        # 检查是否以SELECT开头（忽略大小写）
        select_pattern = r'^\s*(SELECT|WITH)\s+'
        return bool(re.match(select_pattern, cleaned_query, re.IGNORECASE))
    
    def _handle_query_request(self, request_data: Dict[str, Any]):
        """处理查询请求"""
        try:
            # 从请求数据中提取字段（与schema保持一致）
            app_id = request_data.get('app_id', 'unknown')
            query_id = request_data.get('query_id')
            query_statement = request_data.get('query_statement')  # 使用schema中的字段名
            query_type = request_data.get('query_type')
            parameters = request_data.get('parameters', {})
            
            if not query_id or not query_statement:
                logger.error("Invalid query request: missing query_id or query_statement")
                return
            
            logger.info(f"Executing query {query_id} from app {app_id}: {query_statement}")
            
            # 记录开始时间
            start_time = time.time()
            
            try:
                # 判断是SELECT查询还是非查询操作
                is_select = self._is_select_query(query_statement)
                
                if is_select:
                    # SELECT查询：使用execute_query方法
                    results = self.db_connector.execute_query(query_statement)
                    result_data = json.dumps(results, ensure_ascii=False) if results else None
                    row_count = len(results) if results else 0
                    status = "success"
                    error_message = None
                else:
                    # 非查询操作（INSERT/UPDATE/DELETE等）：使用execute_non_query方法
                    affected_rows = self.db_connector.execute_non_query(query_statement)
                    result_data = json.dumps({"affected_rows": affected_rows}, ensure_ascii=False)
                    row_count = affected_rows
                    status = "success"
                    error_message = None
                    
            except Exception as e:
                logger.error(f"Database query failed for {query_id}: {str(e)}")
                result_data = None
                row_count = None
                status = "error"
                error_message = str(e)
            
            # 计算执行时间
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # 构建响应消息（与schema结构保持一致）
            response_data = {
                'app_id': app_id,
                'query_id': query_id,
                'timestamp': time.time(),
                'status': status,
                'result_data': result_data,
                'error_message': error_message,
                'execution_time_ms': execution_time_ms,
                'row_count': row_count,
                'metadata': {
                    'query_type': query_type or ('select' if self._is_select_query(query_statement) else 'non_query'),
                    'original_query': query_statement[:100] + '...' if len(query_statement) > 100 else query_statement
                } if query_type or query_statement else None
            }
            
            # 发布响应到response topic
            self.query_response_producer.publish_message(response_data)
            logger.info(f"Query response published for {query_id} with status: {status}")
            
        except Exception as e:
            logger.error(f"Error handling query request: {str(e)}")
    
    def submit_query(self, sql_query: str, query_id: Optional[str] = None, app_id: str = "soa_data_utils", query_type: Optional[str] = None) -> str:
        """提交SQL查询
        
        Args:
            sql_query: 要执行的SQL查询语句
            query_id: 可选的查询ID，如果不提供将自动生成
            app_id: 应用程序标识符
            query_type: 查询类型分类
            
        Returns:
            str: 查询ID
        """
        if not self.query_request_producer:
            raise RuntimeError("SOADataQueryManager not initialized. Call initialize() first.")
        
        if query_id is None:
            query_id = str(uuid.uuid4())
        
        # 构建查询请求消息（与schema结构保持一致）
        request_data = {
            'app_id': app_id,
            'query_id': query_id,
            'timestamp': time.time(),
            'query_statement': sql_query,  # 使用schema中的字段名
            'query_type': query_type,
            'parameters': None  # 可以根据需要扩展参数支持
        }
        
        # 发布查询请求
        self.query_request_producer.publish_message(request_data)
        logger.info(f"Query submitted with ID: {query_id} from app: {app_id}")
        
        return query_id
    
    def _handle_query_response(self, response_data: Dict[str, Any]):
        """处理查询响应"""
        try:
            query_id = response_data.get('query_id')
            if not query_id:
                logger.error("Invalid query response: missing query_id")
                return
            
            with self.query_lock:
                # 存储查询结果
                self.query_results[query_id] = response_data
                
                # 如果有等待的队列，通知结果
                if query_id in self.result_queues:
                    self.result_queues[query_id].put(response_data)
            
            logger.info(f"Query response processed for {query_id}")
            
        except Exception as e:
            logger.error(f"Error handling query response: {str(e)}")
    
    def get_query_result(self, query_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """获取查询结果
        
        Args:
            query_id: 查询ID
            timeout: 超时时间（秒）
            
        Returns:
            Dict[str, Any]: 查询结果，如果超时或出错返回None
        """
        # 首先检查是否已经有结果
        with self.query_lock:
            if query_id in self.query_results:
                return self.query_results[query_id]
            
            # 创建结果队列用于等待
            if query_id not in self.result_queues:
                self.result_queues[query_id] = Queue()
        
        # 等待结果
        try:
            result = self.result_queues[query_id].get(timeout=timeout)
            return result
        except Empty:
            logger.warning(f"Query {query_id} timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error getting query result for {query_id}: {str(e)}")
            return None
        finally:
            # 清理队列
            with self.query_lock:
                if query_id in self.result_queues:
                    del self.result_queues[query_id]
    
    def execute_query_sync(self, sql_query: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """同步执行查询（提交查询并等待结果）
        
        Args:
            sql_query: 要执行的SQL查询语句
            timeout: 超时时间（秒）
            
        Returns:
            Dict[str, Any]: 查询结果
        """
        query_id = self.submit_query(sql_query)
        return self.get_query_result(query_id, timeout)
    
    def stop_consumers(self):
        """停止消费者"""
        if not self.running:
            logger.warning("Consumers are not running")
            return
        
        logger.info("Stopping consumers...")
        self.running = False
        
        # 等待所有消费者线程结束
        for thread in self.consumer_threads:
            thread.join(timeout=5.0)
        
        self.consumer_threads.clear()
        logger.info("All consumers stopped")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 停止消费者
            self.stop_consumers()
            
            # 清理producers
            if self.query_request_producer:
                self.query_request_producer.cleanup()
            if self.query_response_producer:
                self.query_response_producer.cleanup()
            
            # 清理consumers
            if self.query_request_consumer:
                self.query_request_consumer.cleanup()
            if self.query_response_consumer:
                self.query_response_consumer.cleanup()
            
            # 关闭线程池
            self.executor.shutdown(wait=True)
            
            logger.info("SOADataQueryManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def __del__(self):
        """对象退出出口"""
        self.cleanup()
    
    # def __enter__(self):
    #     """上下文管理器入口"""
    #     # 初始化生产者和消费者，其中生产者用于往request和response主题中生产数据 消费者1消费request并且放到response中 消费者2消费response并放到队列中
    #     self.initialize()
    #     # 启动消费者
    #     self.start_consumers()
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     """上下文管理器出口"""
    #     self.cleanup()


# 使用示例
if __name__ == "__main__":
    # 使用上下文管理器确保资源正确清理
    query_manager = SOADataQueryManager(db_connection_id="aws_db_eh080", db_connection_config=None)

    result = query_manager.execute_query_sync(
        "SELECT version();",
        timeout=10.0
    )

    if result:
        if result['status'] == 'success':
            print(f"Query results: {result}")
        else:
            print(f"Query failed: {result}")
    else:
        print("Query timed out")

    # query_manager.cleanup()

    # # # 或者异步方式
    # query_id = query_manager.submit_query("SELECT COUNT(*) FROM public.pod_information;")
    # print(f"Submitted query with ID: {query_id}")
    #
    # # 稍后获取结果
    # time.sleep(2)
    # result = query_manager.get_query_result(query_id)
    # if result:
    #     print(f"Async query result: {result}")