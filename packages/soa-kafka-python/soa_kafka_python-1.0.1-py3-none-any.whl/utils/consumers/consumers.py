import sys
from pathlib import Path

# Add parent directory to Python path using pathlib
current_file = Path(__file__)
src_dir = current_file.parent.parent.parent  # Go up 3 levels: consumers -> utils -> src
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import cv2
import numpy as np
import time
from confluent_kafka import Consumer, KafkaError
from typing import Optional, Callable, Dict, Any
import avro.schema
import socket

# Use absolute imports
from utils.common_utils import _log, config_loader
from utils.schema_registry_utils import SchemaRegistryHTTPClient
from utils.serialization_utils import AvroSerializer

logger = _log()
config_dict = config_loader()

from abc import ABC, abstractmethod
from confluent_kafka import TopicPartition
from typing import List

class BaseKafkaConsumer(ABC):
    """
    Base Kafka consumer class providing common functionality for all consumer types.
    """
    
    def __init__(self, consumer_id: str, partitions: Optional[List[int]] = None):
        """
        Initialize base Kafka consumer.
        
        Args:
            consumer_id: Consumer configuration ID
            partitions: Optional list of specific partitions to consume from
        """
        # Load configuration
        self.connection = config_dict['connections']
        self.consumer_config = config_dict['consumers_configs'][consumer_id]
        
        # Extract configuration values
        self.bootstrap_servers = self.connection['kafka']['bootstrap_servers']
        self.schema_registry_url = self.connection['kafka']['schema_registry_url']
        self.sub_topic = self.consumer_config['sub_topic']
        self.group_id = self.consumer_config['group_id']
        
        # Initialize Schema Registry client and serializer
        self._setup_schema_registry()
        
        # Configure and initialize Kafka consumer
        self._setup_kafka_consumer(partitions)
        
        # Initialize statistics
        self.processed_count = 0
        self.start_time = None
        
        logger.info(f"{self.__class__.__name__} initialized for topic: {self.sub_topic}")
    
    def _setup_schema_registry(self):
        """Setup Schema Registry client and Avro serializer."""
        self.schema_registry_client = SchemaRegistryHTTPClient(
            self.schema_registry_url, 
            verify_ssl=False
        )
        
        schema_info = self.schema_registry_client.get_schema(
            self.consumer_config['schema_subject_name']
        )
        self.serializer = AvroSerializer(
            schema_info['id'],
            avro.schema.parse(schema_info['schema'])
        )
    
    def _setup_kafka_consumer(self, partitions: Optional[List[int]] = None):
        """Setup Kafka consumer with configuration."""
        consumer_conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'client.id': self.consumer_config.get('client_id', socket.gethostname()),
            'auto.offset.reset': self.consumer_config['auto_offset_reset'],
            'enable.auto.commit': self.consumer_config['enable_auto_commit'],
            'max.poll.interval.ms': self.consumer_config['max_poll_interval_ms'],
            'heartbeat.interval.ms': self.consumer_config['heartbeat_interval_ms'],
            'session.timeout.ms': self.consumer_config['session_timeout_ms']
        }
        
        self.consumer = Consumer(consumer_conf)
        
        # Subscribe to specific partitions or all partitions
        if partitions:
            topic_partitions = [TopicPartition(self.sub_topic, p) for p in partitions]
            self.consumer.assign(topic_partitions)
            logger.info(f"Assigned to specific partitions: {partitions}")
        else:
            self.consumer.subscribe([self.sub_topic])
            logger.info(f"Subscribed to all partitions of topic: {self.sub_topic}")
    
    def _poll_and_handle_message(self, timeout: float = 1.0):
        """Poll for messages and handle common error cases."""
        msg = self.consumer.poll(timeout=timeout)
        
        if msg is None:
            return None
        
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.info(f"Reached end of partition {msg.partition()}")
                return None
            else:
                logger.error(f"Consumer error: {msg.error()}")
                raise Exception(f"Consumer error: {msg.error()}")
        
        return msg
    
    def _deserialize_message(self, msg):
        """Deserialize Kafka message using Avro."""
        return self.serializer.deserialize(msg.value())
    
    def _update_statistics(self, metric_name: str = "items"):
        """Update processing statistics."""
        self.processed_count += 1
        
        if self.processed_count % 10 == 0:
            elapsed_time = time.time() - self.start_time
            rate = self.processed_count / elapsed_time if elapsed_time > 0 else 0

    
    @abstractmethod
    def _process_message_data(self, data: Dict[str, Any]) -> None:
        """Process deserialized message data. Must be implemented by subclasses."""
        pass
    
    def consume(self, max_items: Optional[int] = None, timeout: float = 1.0, 
               metric_name: str = "items") -> None:
        """Start consuming messages."""
        self.start_time = time.time()
        
        try:
            logger.info(f"Starting to consume {metric_name} from topic: {self.sub_topic}")
            
            while max_items is None or self.processed_count < max_items:
                try:
                    msg = self._poll_and_handle_message(timeout)
                    if msg is None:
                        continue
                    
                    # Deserialize and process message
                    data = self._deserialize_message(msg)
                    self._process_message_data(data)
                    
                    self._update_statistics(metric_name)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    continue
                    
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal, stopping consumer...")
                    break
                    
        finally:
            self.cleanup(metric_name)
    
    def cleanup(self, metric_name: str = "items") -> None:
        """Clean up resources."""
        if hasattr(self, 'consumer') and self.consumer is not None:
            self.consumer.close()
        
        # Cleanup additional resources in subclasses
        self._cleanup_additional_resources()
        
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            rate = self.processed_count / elapsed_time if elapsed_time > 0 else 0

    
    def _cleanup_additional_resources(self) -> None:
        """Override in subclasses to cleanup additional resources."""
        pass


class VideoFrameConsumer(BaseKafkaConsumer):
    """Video frame consumer with frame-specific processing."""
    
    def __init__(self, consumer_id: str, 
                 frame_processor: Optional[Callable[[np.ndarray, float, ...], None]] = None):
        super().__init__(consumer_id)
        self.frame_processor = frame_processor
    
    def _decode_frame(self, frame_data: bytes) -> np.ndarray:
        """Decode video frame data."""
        try:
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Failed to decode frame data")
                
            return frame
        except Exception as e:
            logger.error(f"Error decoding frame: {str(e)}")
            raise
    
    def _process_message_data(self, data: Dict[str, Any]) -> None:
        """Process video frame message data."""
        timestamp = data['timestamp']
        frame_data = data['frame']
        
        # Extract video metadata
        video_metadata = {
            'video_width': data.get('video_width'),
            'video_height': data.get('video_height'),
            'video_channels': data.get('video_channels'),
            'video_source': data.get('video_source'),
            'frame_id': data.get('frame_id'),
            'source_attributes': data.get('source_attributes')
        }
        
        # Decode and process frame
        frame = self._decode_frame(frame_data)
        
        if self.frame_processor:
            self.frame_processor(frame, timestamp, video_metadata)
    
    def consume_frames(self, max_frames: Optional[int] = None, timeout: float = 1.0) -> None:
        """Start consuming video frames."""
        self.consume(max_frames, timeout, "frames")


class NotificationConsumer(BaseKafkaConsumer):
    """
    通知消息消费者类，用于接收和处理各种类型的通知信息。
    支持邮件、PLC、SMS和系统通知的处理。
    """
    
    def __init__(self, consumer_id: str,
                 notification_processor: Optional[Callable[[Dict[str, Any]], None]] = None,
                 partitions: Optional[List[int]] = None):
        """
        初始化通知消费者。
        
        Args:
            consumer_id: 消费者配置ID
            notification_processor: 自定义通知处理器（可选）
            partitions: 指定消费的分区列表（可选）
        """
        super().__init__(consumer_id, partitions)
        self.notification_processor = notification_processor
        
        # 初始化通知处理统计
        self.notification_stats = {
            "EMAIL": 0,
            "PLC": 0,
            "SMS": 0,
            "SYSTEM": 0
        }
        
        logger.info(f"NotificationConsumer initialized for consumer_id: {consumer_id}")
    
    def _process_message_data(self, data: Dict[str, Any]) -> None:
        """
        处理通知消息数据。
        
        Args:
            data: 反序列化的消息数据
        """
        try:
            notification_type = data.get('notification_type')
            
            # 更新统计信息
            if notification_type in self.notification_stats:
                self.notification_stats[notification_type] += 1
            
            # 根据通知类型进行处理
            if notification_type == "EMAIL":
                self._process_email_notification(data)
            elif notification_type == "PLC":
                self._process_plc_notification(data)
            elif notification_type == "SMS":
                self._process_sms_notification(data)
            elif notification_type == "SYSTEM":
                self._process_system_notification(data)
            else:
                logger.warning(f"Unknown notification type: {notification_type}")
            
            # 如果有自定义处理器，也调用它
            if self.notification_processor:
                self.notification_processor(data)
                
        except Exception as e:
            logger.error(f"Error processing notification message: {str(e)}")
            raise
    
    def _process_email_notification(self, data: Dict[str, Any]) -> None:
        """
        处理邮件通知。
        
        Args:
            data: 邮件通知数据
        """
        try:
            app_id = data.get('app_id')
            notification_id = data.get('notification_id')
            title = data.get('title')
            message = data.get('message')
            recipients = data.get('recipients', [])
            email_details = data.get('email_details', {})
            priority = data.get('priority', 'MEDIUM')
            
            logger.info(f"Processing email notification {notification_id} from app {app_id}")
            logger.info(f"Subject: {email_details.get('subject', title)}")
            logger.info(f"Recipients: {recipients}")
            logger.info(f"Priority: {priority}")
            
            # 这里可以集成实际的邮件发送服务
            # 例如：SMTP服务器、SendGrid、AWS SES等
            self._send_email(
                recipients=recipients,
                subject=email_details.get('subject', title),
                message=message,
                html_content=email_details.get('html_content'),
                attachments=email_details.get('attachments'),
                cc_recipients=email_details.get('cc_recipients'),
                bcc_recipients=email_details.get('bcc_recipients')
            )
            
            logger.info(f"Email notification {notification_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing email notification: {str(e)}")
            raise
    
    def _process_plc_notification(self, data: Dict[str, Any]) -> None:
        """
        处理PLC通知。
        
        Args:
            data: PLC通知数据
        """
        try:
            app_id = data.get('app_id')
            notification_id = data.get('notification_id')
            title = data.get('title')
            message = data.get('message')
            recipients = data.get('recipients', [])
            plc_details = data.get('plc_details', {})
            priority = data.get('priority', 'MEDIUM')
            
            logger.info(f"Processing PLC notification {notification_id} from app {app_id}")
            logger.info(f"PLC Address: {plc_details.get('plc_address')}")
            logger.info(f"Command Type: {plc_details.get('command_type')}")
            logger.info(f"Priority: {priority}")
            
            # 这里可以集成实际的PLC通信服务
            # 例如：Modbus、OPC UA、Ethernet/IP等
            self._send_plc_command(
                plc_address=plc_details.get('plc_address'),
                command_type=plc_details.get('command_type'),
                parameters=plc_details.get('parameters'),
                expected_response=plc_details.get('expected_response'),
                timeout_ms=plc_details.get('timeout_ms')
            )
            
            logger.info(f"PLC notification {notification_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing PLC notification: {str(e)}")
            raise
    
    def _process_sms_notification(self, data: Dict[str, Any]) -> None:
        """
        处理SMS通知。
        
        Args:
            data: SMS通知数据
        """
        try:
            app_id = data.get('app_id')
            notification_id = data.get('notification_id')
            title = data.get('title')
            message = data.get('message')
            recipients = data.get('recipients', [])
            priority = data.get('priority', 'MEDIUM')
            
            logger.info(f"Processing SMS notification {notification_id} from app {app_id}")
            logger.info(f"Recipients: {recipients}")
            logger.info(f"Priority: {priority}")
            
            # 这里可以集成实际的SMS发送服务
            # 例如：Twilio、AWS SNS、阿里云短信等
            self._send_sms(
                recipients=recipients,
                message=message
            )
            
            logger.info(f"SMS notification {notification_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing SMS notification: {str(e)}")
            raise
    
    def _process_system_notification(self, data: Dict[str, Any]) -> None:
        """
        处理系统通知。
        
        Args:
            data: 系统通知数据
        """
        try:
            app_id = data.get('app_id')
            notification_id = data.get('notification_id')
            title = data.get('title')
            message = data.get('message')
            recipients = data.get('recipients', [])
            priority = data.get('priority', 'MEDIUM')
            
            logger.info(f"Processing system notification {notification_id} from app {app_id}")
            logger.info(f"Title: {title}")
            logger.info(f"Message: {message}")
            logger.info(f"Recipients: {recipients}")
            logger.info(f"Priority: {priority}")
            
            # 这里可以集成系统通知服务
            # 例如：写入日志、更新数据库、触发其他系统事件等
            self._handle_system_notification(
                title=title,
                message=message,
                recipients=recipients,
                priority=priority,
                metadata=data.get('metadata')
            )
            
            logger.info(f"System notification {notification_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing system notification: {str(e)}")
            raise
    
    def _send_email(self, recipients: list, subject: str, message: str,
                   html_content: Optional[str] = None,
                   attachments: Optional[list] = None,
                   cc_recipients: Optional[list] = None,
                   bcc_recipients: Optional[list] = None) -> None:
        """
        发送邮件的实际实现。
        
        Args:
            recipients: 收件人列表
            subject: 邮件主题
            message: 邮件内容
            html_content: HTML内容（可选）
            attachments: 附件列表（可选）
            cc_recipients: 抄送列表（可选）
            bcc_recipients: 密送列表（可选）
        """
        # TODO: 集成实际的邮件发送服务
        logger.info(f"Sending email to {recipients} with subject: {subject}")
        # 示例：可以使用smtplib、sendgrid、boto3等库
    
    def _send_plc_command(self, plc_address: str, command_type: str,
                         parameters: Optional[Dict[str, str]] = None,
                         expected_response: Optional[str] = None,
                         timeout_ms: Optional[int] = None) -> None:
        """
        发送PLC命令的实际实现。
        
        Args:
            plc_address: PLC地址
            command_type: 命令类型
            parameters: 命令参数（可选）
            expected_response: 期望响应（可选）
            timeout_ms: 超时时间（可选）
        """
        # TODO: 集成实际的PLC通信服务
        logger.info(f"Sending PLC command to {plc_address}: {command_type}")
        # 示例：可以使用pymodbus、opcua等库
    
    def _send_sms(self, recipients: list, message: str) -> None:
        """
        发送SMS的实际实现。
        
        Args:
            recipients: 收件人列表
            message: 短信内容
        """
        # TODO: 集成实际的SMS发送服务
        logger.info(f"Sending SMS to {recipients}: {message}")
        # 示例：可以使用twilio、boto3等库
    
    def _handle_system_notification(self, title: str, message: str,
                                  recipients: list, priority: str,
                                  metadata: Optional[Dict[str, str]] = None) -> None:
        """
        处理系统通知的实际实现。
        
        Args:
            title: 通知标题
            message: 通知内容
            recipients: 接收者列表
            priority: 优先级
            metadata: 元数据（可选）
        """
        # TODO: 实现系统通知处理逻辑
        logger.info(f"Handling system notification: {title}")
        # 示例：写入数据库、触发webhook、更新监控系统等

    def _cleanup_additional_resources(self) -> None:
        """
        清理额外资源。
        """
        # 打印最终统计信息
        logger.info(f"Final notification processing stats: {self.notification_stats}")


    def consume_notifications(self, max_notifications: Optional[int] = None, 
                            timeout: float = 1.0) -> None:
        """
        开始消费通知消息。
        
        Args:
            max_notifications: 最大处理通知数量（可选）
            timeout: 轮询超时时间
        """
        self.consume(max_notifications, timeout, "notifications")
    
    def get_notification_stats(self) -> Dict[str, int]:
        """
        获取通知处理统计信息。
        
        Returns:
            Dict[str, int]: 各类型通知的处理数量
        """
        return self.notification_stats.copy()
    
