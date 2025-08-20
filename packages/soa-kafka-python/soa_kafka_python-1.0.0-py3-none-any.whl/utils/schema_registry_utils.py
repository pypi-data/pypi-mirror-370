"""Schema Registry utilities using HTTP requests for managing Avro schemas."""

import requests
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import quote
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchemaRegistryHTTPClient:
    """HTTP-based client for Schema Registry operations."""

    def __init__(self, schema_registry_url: str = "http://localhost:8081", verify_ssl: bool = False):
        """
        Initialize Schema Registry HTTP client.
        
        Args:
            schema_registry_url: URL of the Schema Registry
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = schema_registry_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # Disable SSL warnings if verification is disabled
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to Schema Registry."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def create_schema(self, subject: str, schema_dict: Dict[str, Any], compatibility: str = "BACKWARD") -> int:
        """
        Create a new schema for a subject.
        
        Args:
            subject: Subject name
            schema_dict: Avro schema as dictionary
            compatibility: Schema compatibility level
            
        Returns:
            Schema ID
            
        Raises:
            RuntimeError: If schema creation fails
        """
        try:
            # First, set compatibility if specified
            if compatibility:
                self.set_compatibility(subject, compatibility)
            
            # Register the schema
            endpoint = f"/subjects/{quote(subject)}/versions"
            payload = {"schema": json.dumps(schema_dict)}
            
            response = self._make_request("POST", endpoint, json=payload)
            
            if response.status_code == 200:
                schema_id = response.json()["id"]
                logger.info(f"Schema created for subject '{subject}' with ID: {schema_id}")
                return schema_id
            else:
                error_msg = f"Failed to create schema. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error creating schema for subject '{subject}': {str(e)}")
            raise

    def get_schema(self, subject: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Get schema for a subject.
        
        Args:
            subject: Subject name
            version: Schema version (None for latest)
            
        Returns:
            Schema information containing id, version, and schema
            
        Raises:
            RuntimeError: If schema retrieval fails
        """
        try:
            if version is None:
                endpoint = f"/subjects/{quote(subject)}/versions/latest"
            else:
                endpoint = f"/subjects/{quote(subject)}/versions/{version}"
            
            response = self._make_request("GET", endpoint)
            
            if response.status_code == 200:
                schema_data = response.json()
                return {
                    'id': schema_data['id'],
                    'version': schema_data['version'],
                    'schema': schema_data['schema']
                }
            else:
                error_msg = f"Failed to get schema. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error getting schema for subject '{subject}': {str(e)}")
            raise

    def update_schema(self, subject: str, schema_dict: Dict[str, Any]) -> int:
        """
        Update an existing schema for a subject.
        
        Args:
            subject: Subject name
            schema_dict: New Avro schema as dictionary
            
        Returns:
            New schema ID
            
        Raises:
            RuntimeError: If schema update fails
        """
        try:
            endpoint = f"/subjects/{quote(subject)}/versions"
            payload = {"schema": json.dumps(schema_dict)}
            
            response = self._make_request("POST", endpoint, json=payload)
            
            if response.status_code == 200:
                schema_id = response.json()["id"]
                logger.info(f"Schema updated for subject '{subject}' with ID: {schema_id}")
                return schema_id
            else:
                error_msg = f"Failed to update schema. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error updating schema for subject '{subject}': {str(e)}")
            raise

    def delete_schema(self, subject: str, version: Optional[int] = None, permanent: bool = False) -> List[int]:
        """
        Delete schema(s) for a subject.
        
        Args:
            subject: Subject name
            version: Schema version to delete (None for all versions)
            permanent: Whether to permanently delete
            
        Returns:
            List of deleted version numbers
            
        Raises:
            RuntimeError: If schema deletion fails
        """
        try:
            if version is None:
                # Delete all versions
                endpoint = f"/subjects/{quote(subject)}"
                if permanent:
                    endpoint += "?permanent=true"
            else:
                # Delete specific version
                endpoint = f"/subjects/{quote(subject)}/versions/{version}"
                if permanent:
                    endpoint += "?permanent=true"
            
            response = self._make_request("DELETE", endpoint)
            
            if response.status_code == 200:
                deleted_versions = response.json()
                logger.info(f"Schema(s) deleted for subject '{subject}': {deleted_versions}")
                return deleted_versions
            else:
                error_msg = f"Failed to delete schema. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error deleting schema for subject '{subject}': {str(e)}")
            raise

    def list_subjects(self) -> List[str]:
        """
        List all subjects in the Schema Registry.
        
        Returns:
            List of subject names
            
        Raises:
            RuntimeError: If subject listing fails
        """
        try:
            response = self._make_request("GET", "/subjects")
            
            if response.status_code == 200:
                subjects = response.json()
                logger.info(f"Found {len(subjects)} subjects")
                return subjects
            else:
                error_msg = f"Failed to list subjects. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error listing subjects: {str(e)}")
            raise

    def get_schema_versions(self, subject: str) -> List[int]:
        """
        Get all versions of a schema for a subject.
        
        Args:
            subject: Subject name
            
        Returns:
            List of version numbers
            
        Raises:
            RuntimeError: If version listing fails
        """
        try:
            endpoint = f"/subjects/{quote(subject)}/versions"
            response = self._make_request("GET", endpoint)
            
            if response.status_code == 200:
                versions = response.json()
                logger.info(f"Found {len(versions)} versions for subject '{subject}'")
                return versions
            else:
                error_msg = f"Failed to get schema versions. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error getting schema versions for subject '{subject}': {str(e)}")
            raise

    def set_compatibility(self, subject: str, compatibility: str) -> Dict[str, str]:
        """
        Set compatibility level for a subject.
        
        Args:
            subject: Subject name
            compatibility: Compatibility level (BACKWARD, FORWARD, FULL, NONE)
            
        Returns:
            Updated compatibility configuration
            
        Raises:
            RuntimeError: If compatibility setting fails
        """
        try:
            endpoint = f"/config/{quote(subject)}"
            payload = {"compatibility": compatibility}
            
            response = self._make_request("PUT", endpoint, json=payload)
            
            if response.status_code == 200:
                config = response.json()
                logger.info(f"Compatibility set to '{compatibility}' for subject '{subject}'")
                return config
            else:
                error_msg = f"Failed to set compatibility. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error setting compatibility for subject '{subject}': {str(e)}")
            raise

    def get_compatibility(self, subject: str) -> str:
        """
        Get compatibility level for a subject.
        
        Args:
            subject: Subject name
            
        Returns:
            Compatibility level
            
        Raises:
            RuntimeError: If compatibility retrieval fails
        """
        try:
            endpoint = f"/config/{quote(subject)}"
            response = self._make_request("GET", endpoint)
            
            if response.status_code == 200:
                config = response.json()
                compatibility = config.get("compatibilityLevel", "NONE")
                logger.info(f"Compatibility level for subject '{subject}': {compatibility}")
                return compatibility
            else:
                error_msg = f"Failed to get compatibility. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error getting compatibility for subject '{subject}': {str(e)}")
            raise

    def check_compatibility(self, subject: str, schema_dict: Dict[str, Any], version: Optional[int] = None) -> bool:
        """
        Check if a schema is compatible with existing schema for a subject.
        
        Args:
            subject: Subject name
            schema_dict: Schema to check compatibility with
            version: Version to check against (None for latest)
            
        Returns:
            True if compatible, False otherwise
            
        Raises:
            RuntimeError: If compatibility check fails
        """
        try:
            if version is None:
                endpoint = f"/compatibility/subjects/{quote(subject)}/versions/latest"
            else:
                endpoint = f"/compatibility/subjects/{quote(subject)}/versions/{version}"
            
            payload = {"schema": json.dumps(schema_dict)}
            response = self._make_request("POST", endpoint, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                is_compatible = result.get("is_compatible", False)
                logger.info(f"Compatibility check for subject '{subject}': {is_compatible}")
                return is_compatible
            else:
                error_msg = f"Failed to check compatibility. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error checking compatibility for subject '{subject}': {str(e)}")
            raise

    def get_global_compatibility(self) -> str:
        """
        Get global compatibility level.
        
        Returns:
            Global compatibility level
            
        Raises:
            RuntimeError: If global compatibility retrieval fails
        """
        try:
            response = self._make_request("GET", "/config")
            
            if response.status_code == 200:
                config = response.json()
                compatibility = config.get("compatibilityLevel", "NONE")
                logger.info(f"Global compatibility level: {compatibility}")
                return compatibility
            else:
                error_msg = f"Failed to get global compatibility. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error getting global compatibility: {str(e)}")
            raise

    def set_global_compatibility(self, compatibility: str) -> Dict[str, str]:
        """
        Set global compatibility level.
        
        Args:
            compatibility: Compatibility level (BACKWARD, FORWARD, FULL, NONE)
            
        Returns:
            Updated global compatibility configuration
            
        Raises:
            RuntimeError: If global compatibility setting fails
        """
        try:
            payload = {"compatibility": compatibility}
            response = self._make_request("PUT", "/config", json=payload)
            
            if response.status_code == 200:
                config = response.json()
                logger.info(f"Global compatibility set to: {compatibility}")
                return config
            else:
                error_msg = f"Failed to set global compatibility. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            logger.error(f"Error setting global compatibility: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    client = SchemaRegistryHTTPClient("http://localhost:8081", verify_ssl=False)
    
    try:
        # List all subjects
        subjects = client.list_subjects()
        print(f"Available subjects: {subjects}")

        
        # Create video frame schema
        # topic = "data_integration_video_main"
        # schema_id = create_video_frame_schema(client, topic)
        # print(f"Video frame schema created with ID: {schema_id}")
        #
        # # Get the created schema
        # subject = f"data_integration_video_main-video-schema-common"
        # schema_info = client.get_schema(subject)
        # print(f"Schema info: {schema_info}")
        # import avro.schema
        # import json
        # avro.schema.parse(json.dumps(schema_info['schema']))
        
        # Check compatibility
        # is_compatible = client.check_compatibility(subject, schema_info['schema'])
        # print(f"Schema is compatible: {is_compatible}")
        
    except Exception as e:
        print(f"Error: {str(e)}")