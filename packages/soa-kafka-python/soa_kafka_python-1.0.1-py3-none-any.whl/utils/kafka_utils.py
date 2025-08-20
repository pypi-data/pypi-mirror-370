from typing import Dict, List, Optional, Any
from confluent_kafka import admin, KafkaException
from confluent_kafka.admin import NewTopic, ConfigResource, NewPartitions
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KafkaUtils:
    def __init__(
        self,
        bootstrap_servers: str,
        client_id: Optional[str] = None
    ):
        """
        Initialize Kafka utility class with connection parameters.
        
        Args:
            bootstrap_servers: Comma-separated list of Kafka broker addresses
            client_id: Optional client ID for the Kafka client
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id or f"kafka-admin-{datetime.now().timestamp()}"
        self._admin_client = None

    def _get_common_config(self) -> Dict[str, Any]:
        """Get common configuration for Kafka clients."""
        return {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': self.client_id
        }

    def get_admin_client(self) -> admin.AdminClient:
        """Get or create admin client."""
        if self._admin_client is None:
            self._admin_client = admin.AdminClient(self._get_common_config())
        return self._admin_client

    def create_topic(
        self,
        topic_name: str,
        num_partitions: int = 1,
        replication_factor: int = 1,
        configs: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Create a new Kafka topic.
        
        Args:
            topic_name: Name of the topic to create
            num_partitions: Number of partitions
            replication_factor: Replication factor
            configs: Additional topic configurations
        """
        admin_client = self.get_admin_client()
        new_topic = NewTopic(
            topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            config=configs or {}
        )
        
        try:
            result = admin_client.create_topics([new_topic])
            result[topic_name].result()  # Wait for topic creation
            logger.info(f"Topic {topic_name} created successfully")
        except KafkaException as e:
            logger.error(f"Failed to create topic {topic_name}: {str(e)}")
            raise

    def delete_topic(self, topic_name: str) -> None:
        """Delete a Kafka topic."""
        admin_client = self.get_admin_client()
        try:
            result = admin_client.delete_topics([topic_name])
            result[topic_name].result()  # Wait for topic deletion
            logger.info(f"Topic {topic_name} deleted successfully")
        except KafkaException as e:
            logger.error(f"Failed to delete topic {topic_name}: {str(e)}")
            raise

    def list_topics(self) -> List[str]:
        """List all available topics."""
        admin_client = self.get_admin_client()
        try:
            metadata = admin_client.list_topics()
            return list(metadata.topics.keys())
        except KafkaException as e:
            logger.error(f"Failed to list topics: {str(e)}")
            raise

    def get_topic_config(self, topic_name: str) -> Dict[str, str]:
        """Get configuration for a specific topic."""
        admin_client = self.get_admin_client()
        try:
            resource = ConfigResource('topic', topic_name)
            result = admin_client.describe_configs([resource])
            config = result[resource].result()
            return {entry.name: entry.value for entry in config.values()}
        except KafkaException as e:
            logger.error(f"Failed to get config for topic {topic_name}: {str(e)}")
            raise

    def get_topic_partitions(self, topic: str) -> List[Dict[str, Any]]:
        """Get partition information for a topic."""
        admin_client = self.get_admin_client()
        try:
            metadata = admin_client.list_topics(topic)
            topic_metadata = metadata.topics[topic]
            return [
                {
                    'partition_id': partition.id,
                    'leader': partition.leader,
                    'replicas': partition.replicas,
                    'isrs': partition.isrs
                }
                for partition in topic_metadata.partitions.values()
            ]
        except KafkaException as e:
            logger.error(f"Failed to get partitions for topic {topic}: {str(e)}")
            raise

    def get_cluster_metadata(self) -> Dict[str, Any]:
        """Get cluster metadata including brokers and topics."""
        admin_client = self.get_admin_client()
        try:
            metadata = admin_client.list_topics()
            return {
                'brokers': [
                    {
                        'id': broker.id,
                        'host': broker.host,
                        'port': broker.port
                    }
                    for broker in metadata.brokers.values()
                ],
                'topics': [
                    {
                        'name': topic_name,
                        'partitions': len(topic_metadata.partitions),
                        'replication_factor': topic_metadata.replication_factor
                    }
                    for topic_name, topic_metadata in metadata.topics.items()
                ]
            }
        except KafkaException as e:
            logger.error(f"Failed to get cluster metadata: {str(e)}")
            raise

    def increase_partitions(
        self,
        topic_name: str,
        new_partition_count: int
    ) -> None:
        """
        Increase the number of partitions for an existing topic.
        
        Args:
            topic_name: Name of the topic to modify
            new_partition_count: New total number of partitions
        
        Note:
            - Can only increase the number of partitions, not decrease
            - New partition count must be greater than current partition count
            - Operation is not reversible
        """
        admin_client = self.get_admin_client()
        
        try:
            # Get current partition count
            metadata = admin_client.list_topics(topic_name)
            current_partition_count = len(metadata.topics[topic_name].partitions)
            
            if new_partition_count <= current_partition_count:
                raise ValueError(
                    f"New partition count ({new_partition_count}) must be greater than "
                    f"current partition count ({current_partition_count})"
                )
            
            # Create new partitions request
            new_partitions = NewPartitions(
                topic_name,
                new_partition_count
            )
            
            # Execute the partition increase
            result = admin_client.create_partitions([new_partitions])
            result[topic_name].result()  # Wait for operation to complete
            
            logger.info(
                f"Successfully increased partitions for topic {topic_name} "
                f"from {current_partition_count} to {new_partition_count}"
            )
                
        except KafkaException as e:
            logger.error(f"Failed to increase partitions for topic {topic_name}: {str(e)}")
            raise

    def close(self) -> None:
        """Close the admin client."""
        if self._admin_client:
            self._admin_client = None
