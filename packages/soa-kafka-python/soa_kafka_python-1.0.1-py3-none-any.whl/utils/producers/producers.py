import sys
from pathlib import Path

# Add parent directory to Python path using pathlib
current_file = Path(__file__)
src_dir = current_file.parent.parent.parent  # Go up 3 levels: producers -> utils -> src
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import cv2
import numpy as np
import socket
from confluent_kafka import Producer
from typing import Optional, Dict, Any
import avro.schema

# Use absolute imports
from utils.common_utils import _log, config_loader, delivery_callback
from utils.schema_registry_utils import SchemaRegistryHTTPClient
from utils.serialization_utils import AvroSerializer


logger = _log()
config_dict = config_loader()


class BaseProducer:
    """
    Generic base producer class for publishing messages to Kafka topics.
    
    This class provides common functionality for Kafka message publishing including:
    - Avro serialization support
    - Configurable producer settings
    - Schema registry integration
    - Error handling and logging
    """
    
    def __init__(self, producer_id: str):
        """
        Initialize BaseProducer.
        
        Args:
            producer_id: Producer configuration ID corresponding to producers_configs in config.yaml
            
        Raises:
            KeyError: Raised when producer_id is not found in configuration
        """
        # Load configuration
        self.connection = config_dict['connections']
        self.producer_config = config_dict['producers_configs'][producer_id]
        
        # Extract configuration values
        self.bootstrap_servers = self.connection['kafka']['bootstrap_servers']
        self.schema_registry_url = self.connection['kafka']['schema_registry_url']
        
        # Initialize Schema Registry client
        self.schema_registry_client = SchemaRegistryHTTPClient(
            self.schema_registry_url, 
            verify_ssl=False
        )
        
        # Get and initialize Avro serializer
        schema_info = self.schema_registry_client.get_schema(
            self.producer_config['schema_subject_name']
        )
        self.serializer = AvroSerializer(
            schema_info['id'],
            avro.schema.parse(schema_info['schema'])
        )
        
        # Configure Kafka producer
        producer_conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': self.producer_config.get("client_id", socket.gethostname()),
            'acks': self.producer_config['acks'],
            'compression.type': self.producer_config['compression_type'],
            'retries': self.producer_config['retries'],
            'retry.backoff.ms': self.producer_config['retry_backoff_ms'],
            'batch.size': self.producer_config['batch_size'],
            'linger.ms': self.producer_config['linger_ms'],
            'enable.idempotence': self.producer_config['enable_idempotence']
        }
        
        # Initialize Kafka producer
        self.producer = Producer(producer_conf)
        
        logger.info(f"BaseProducer initialized for producer_id: {producer_id}")
    
    def publish_message(self, message_data: Dict[str, Any], timestamp: Optional[float] = None, 
                       partition: Optional[int] = None, key: Optional[str] = None) -> None:
        """
        Publish a generic message to Kafka.
        
        Args:
            message_data: Dictionary containing message data
            timestamp: Optional timestamp, if not provided, current time will be used
            partition: Optional partition number to send message to
            key: Optional message key for partitioning
            
        Raises:
            Exception: Raised when message publishing fails
        """
        try:
            # Add timestamp if not provided
            if timestamp is not None:
                message_data['timestamp'] = float(timestamp)
            
            # Prepare producer arguments
            produce_args = {
                'topic': self.producer_config['pub_topic'],
                'value': self.serializer.serialize(message_data),
                'on_delivery': delivery_callback
            }
            
            # Only add partition if it's not None
            if partition is not None:
                produce_args['partition'] = partition
            
            # Only add key if it's not None
            if key is not None:
                produce_args['key'] = key.encode('utf-8')
            
            # Publish to Kafka
            logger.debug(f"Publishing message to topic: {self.producer_config['pub_topic']}, partition: {partition}")
            self.producer.produce(**produce_args)
            
            # Trigger delivery report callbacks
            self.producer.poll(0)
            
        except Exception as e:
            logger.error(f"Error publishing message: {str(e)}")
            raise
    
    def flush(self, timeout: float = 10.0) -> None:
        """
        Wait for all messages to be sent.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        try:
            self.producer.flush(timeout=timeout)
            logger.info("Producer flushed successfully")
        except Exception as e:
            logger.error(f"Error during producer flush: {str(e)}")
            raise
    
    def cleanup(self) -> None:
        """
        Clean up producer resources.
        """
        try:
            if self.producer is not None:
                self.producer.flush(timeout=10)
                logger.info("Producer cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


class RTSPVideoFrameProducer(BaseProducer):
    """
    Specialized video frame producer class for capturing video frames from RTSP sources and pushing to Kafka topics.
    
    This class extends BaseProducer with RTSP-specific functionality including:
    - RTSP stream connection and management
    - Video frame capture and encoding
    - Automatic reconnection on stream failure
    - Frame quality configuration
    - Enhanced video metadata tracking
    """
    
    def __init__(self, camera_id: str, producer_id: str):
        """
        Initialize RTSPVideoFrameProducer.
        
        Args:
            camera_id: Camera ID corresponding to rtsp configuration in config.yaml
            producer_id: Producer configuration ID corresponding to producers_configs in config.yaml
            
        Raises:
            RuntimeError: Raised when unable to open RTSP stream
        """
        # Initialize base producer
        super().__init__(producer_id)
        
        # Store camera information
        self.camera_id = camera_id
        
        # Extract RTSP-specific configuration
        self.rtsp_url = self.connection['rtsp'][camera_id]['url']
        self.frame_quality = self.producer_config['frame_quality']
        
        # Initialize frame counter for unique frame IDs
        self.frame_id_counter = 0
        
        # Initialize video metadata
        self.video_width = 0
        self.video_height = 0
        self.video_channels = 3  # Default to 3 for RGB/BGR
        self.video_fps = 0.0
        
        # Initialize video capture
        logger.info(f"Initializing video capture from {self.rtsp_url}")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        
        if not self.cap.isOpened():
            error_msg = f"Failed to open RTSP stream: {self.rtsp_url}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        # Set video capture parameters and extract metadata
        self._configure_capture()
        
        logger.info(f"RTSPVideoFrameProducer initialized successfully")
    
    def _configure_capture(self) -> None:
        """
        Configure video capture parameters and extract video metadata.
        
        Can set buffer size, frame rate and other parameters as needed.
        """
        # Set buffer size to 1 to reduce latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Get video stream information and store as instance variables
        self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Get a sample frame to determine channels
        ret, sample_frame = self.cap.read()
        if ret and sample_frame is not None:
            self.video_channels = sample_frame.shape[2] if len(sample_frame.shape) == 3 else 1
        else:
            logger.warning("Could not read sample frame to determine channels, using default value 3")
            self.video_channels = 3
        
        logger.info(
            f"Video stream info - FPS: {self.video_fps}, "
            f"Resolution: {self.video_width}x{self.video_height}, "
            f"Channels: {self.video_channels}, "
            f"Source: {self.rtsp_url}"
        )
    
    def publish_frame(self, frame: np.ndarray, timestamp: float) -> None:
        """
        Publish a single video frame to Kafka with enhanced metadata.
        
        Args:
            frame: Video frame array
            timestamp: Timestamp
            
        Raises:
            Exception: Raised when frame publishing fails
        """
        try:
            logger.debug("Encoding and compressing frame")
            
            # Increment frame ID counter
            self.frame_id_counter += 1
            
            # Update video metadata from current frame if needed
            if frame is not None:
                current_height, current_width = frame.shape[:2]
                current_channels = frame.shape[2] if len(frame.shape) == 3 else 1
                
                # Update metadata if frame dimensions changed
                if (current_width != self.video_width or 
                    current_height != self.video_height or 
                    current_channels != self.video_channels):
                    
                    self.video_width = current_width
                    self.video_height = current_height
                    self.video_channels = current_channels
                    
                    logger.info(f"Video metadata updated: {self.video_width}x{self.video_height}x{self.video_channels}")
            
            # Set JPEG encoding parameters
            encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.frame_quality]
            success, buffer = cv2.imencode('.jpg', frame, encode_params)
            
            if not success:
                raise RuntimeError("Failed to encode frame as JPEG")
            
            # Prepare enhanced message data with video metadata
            message_data = {
                'timestamp': float(timestamp),
                'frame': buffer.tobytes(),
                # Video metadata
                'video_width': self.video_width,
                'video_height': self.video_height,
                'video_channels': self.video_channels,
                'video_source': self.rtsp_url,
                'frame_id': self.frame_id_counter,
                'source_attributes': {
                    'source_type': 'rtsp',
                    'fps': self.video_fps,
                    'quality': self.frame_quality,
                    'encoding': 'jpeg'
                }
            }
            
            # Use base class method to publish
            self.publish_message(message_data)
            
        except Exception as e:
            logger.error(f"Error publishing frame: {str(e)}")
            raise
    
    def run(self, max_frames: Optional[int] = 100) -> None:
        """
        Main loop for capturing and publishing video frames.
        
        Args:
            max_frames: Maximum number of frames to process, None means unlimited
        """
        frame_count = 0
        
        try:
            logger.info(f"Starting video frame capture and publishing")
            logger.info(f"Video metadata - Resolution: {self.video_width}x{self.video_height}x{self.video_channels}, "
                       f"Source: {self.camera_id}")
            
            while max_frames is None or frame_count < max_frames:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to grab frame from video source")
                    # Try to reconnect
                    if not self._reconnect():
                        logger.error("Failed to reconnect to video source")
                        break
                    continue
                
                # Get current timestamp
                timestamp = cv2.getTickCount() / cv2.getTickFrequency()
                
                # Publish frame
                try:
                    self.publish_frame(frame, timestamp)
                    frame_count += 1
                    
                    # Periodic statistics output
                    if frame_count % 10 == 0:
                        logger.info(f"Processed {frame_count} frames, Current frame ID: {self.frame_id_counter}")
                        
                except Exception as e:
                    logger.error(f"Failed to publish frame {frame_count}: {str(e)}")
                    # Continue processing next frame
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping video capture...")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
        finally:
            self.cleanup()
            logger.info(f"Producer stopped. Total frames processed: {frame_count}, Final frame ID: {self.frame_id_counter}")
    
    def _reconnect(self) -> bool:
        """
        Attempt to reconnect to video source.
        
        Returns:
            bool: Whether reconnection was successful
        """
        try:
            logger.info("Attempting to reconnect to video source...")
            self.cap.release()
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if self.cap.isOpened():
                self._configure_capture()
                logger.info("Successfully reconnected to video source")
                return True
            else:
                logger.error("Failed to reconnect to video source")
                return False
                
        except Exception as e:
            logger.error(f"Error during reconnection: {str(e)}")
            return False
    
    def reset_frame_counter(self) -> None:
        """
        Reset the frame ID counter to 0.
        
        Useful when restarting capture or switching sources.
        """
        self.frame_id_counter = 0
        logger.info("Frame ID counter reset to 0")
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        Release video capture object and call parent cleanup.
        """
        try:
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()
                logger.info("Video capture released")
            
            # Call parent cleanup
            super().cleanup()
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


class NotificationProducer(BaseProducer):
    """
    通知消息生产者类，用于发布各种类型的通知信息到Kafka topics。
    支持邮件、PLC、SMS和系统通知类型。
    """
    
    def __init__(self, producer_id: str):
        """
        初始化通知生产者。
        
        Args:
            producer_id: 生产者配置ID
        """
        super().__init__(producer_id)
        logger.info(f"NotificationProducer initialized for producer_id: {producer_id}")
    
    def publish_email_notification(self, app_id: str, notification_id: str, 
                                 title: str, message: str, recipients: list,
                                 subject: str, html_content: Optional[str] = None,
                                 attachments: Optional[list] = None,
                                 cc_recipients: Optional[list] = None,
                                 bcc_recipients: Optional[list] = None,
                                 sender: Optional[str] = None,
                                 priority: str = "MEDIUM",
                                 metadata: Optional[Dict[str, str]] = None,
                                 retry_count: Optional[int] = None,
                                 expiry_timestamp: Optional[float] = None,
                                 partition: Optional[int] = None) -> None:
        """
        发布邮件通知消息。
        
        Args:
            app_id: 应用程序标识符
            notification_id: 通知唯一标识符
            title: 通知标题
            message: 通知内容
            recipients: 接收者邮箱列表
            subject: 邮件主题
            html_content: HTML格式邮件内容（可选）
            attachments: 附件文件路径列表（可选）
            cc_recipients: 抄送接收者列表（可选）
            bcc_recipients: 密送接收者列表（可选）
            sender: 发送者信息（可选）
            priority: 优先级（LOW, MEDIUM, HIGH, CRITICAL）
            metadata: 额外元数据（可选）
            retry_count: 重试次数（可选）
            expiry_timestamp: 过期时间戳（可选）
            partition: 可选分区号
        """
        try:
            import time
            
            email_details = {
                "subject": subject,
                "html_content": html_content,
                "attachments": attachments,
                "cc_recipients": cc_recipients,
                "bcc_recipients": bcc_recipients
            }
            
            message_data = {
                "app_id": app_id,
                "notification_id": notification_id,
                "timestamp": float(time.time()),
                "notification_type": "EMAIL",
                "priority": priority,
                "title": title,
                "message": message,
                "recipients": recipients,
                "sender": sender,
                "email_details": email_details,
                "plc_details": None,
                "metadata": metadata,
                "retry_count": retry_count,
                "expiry_timestamp": expiry_timestamp
            }
            
            logger.info(f"Publishing email notification: app_id={app_id}, notification_id={notification_id}, partition={partition}")
            self.publish_message(message_data, partition=partition, key=notification_id)
            
        except Exception as e:
            logger.error(f"Error publishing email notification: {str(e)}")
            raise
    
    def publish_plc_notification(self, app_id: str, notification_id: str,
                               title: str, message: str, recipients: list,
                               plc_address: str, command_type: str,
                               parameters: Optional[Dict[str, str]] = None,
                               expected_response: Optional[str] = None,
                               timeout_ms: Optional[int] = None,
                               sender: Optional[str] = None,
                               priority: str = "MEDIUM",
                               metadata: Optional[Dict[str, str]] = None,
                               retry_count: Optional[int] = None,
                               expiry_timestamp: Optional[float] = None,
                               partition: Optional[int] = None) -> None:
        """
        发布PLC通知消息。
        
        Args:
            app_id: 应用程序标识符
            notification_id: 通知唯一标识符
            title: 通知标题
            message: 通知内容
            recipients: PLC地址列表
            plc_address: PLC设备地址
            command_type: PLC命令类型
            parameters: PLC命令参数（可选）
            expected_response: 期望的PLC响应（可选）
            timeout_ms: 超时时间毫秒（可选）
            sender: 发送者信息（可选）
            priority: 优先级（LOW, MEDIUM, HIGH, CRITICAL）
            metadata: 额外元数据（可选）
            retry_count: 重试次数（可选）
            expiry_timestamp: 过期时间戳（可选）
            partition: 可选分区号
        """
        try:
            import time
            
            plc_details = {
                "plc_address": plc_address,
                "command_type": command_type,
                "parameters": parameters,
                "expected_response": expected_response,
                "timeout_ms": timeout_ms
            }
            
            message_data = {
                "app_id": app_id,
                "notification_id": notification_id,
                "timestamp": float(time.time()),
                "notification_type": "PLC",
                "priority": priority,
                "title": title,
                "message": message,
                "recipients": recipients,
                "sender": sender,
                "email_details": None,
                "plc_details": plc_details,
                "metadata": metadata,
                "retry_count": retry_count,
                "expiry_timestamp": expiry_timestamp
            }
            
            logger.info(f"Publishing PLC notification: app_id={app_id}, notification_id={notification_id}, partition={partition}")
            self.publish_message(message_data, partition=partition, key=notification_id)
            
        except Exception as e:
            logger.error(f"Error publishing PLC notification: {str(e)}")
            raise
    
    def publish_system_notification(self, app_id: str, notification_id: str,
                                  title: str, message: str, recipients: list,
                                  sender: Optional[str] = None,
                                  priority: str = "MEDIUM",
                                  metadata: Optional[Dict[str, str]] = None,
                                  retry_count: Optional[int] = None,
                                  expiry_timestamp: Optional[float] = None,
                                  partition: Optional[int] = None) -> None:
        """
        发布系统通知消息。
        
        Args:
            app_id: 应用程序标识符
            notification_id: 通知唯一标识符
            title: 通知标题
            message: 通知内容
            recipients: 接收者列表
            sender: 发送者信息（可选）
            priority: 优先级（LOW, MEDIUM, HIGH, CRITICAL）
            metadata: 额外元数据（可选）
            retry_count: 重试次数（可选）
            expiry_timestamp: 过期时间戳（可选）
            partition: 可选分区号
        """
        try:
            import time
            
            message_data = {
                "app_id": app_id,
                "notification_id": notification_id,
                "timestamp": float(time.time()),
                "notification_type": "SYSTEM",
                "priority": priority,
                "title": title,
                "message": message,
                "recipients": recipients,
                "sender": sender,
                "email_details": None,
                "plc_details": None,
                "metadata": metadata,
                "retry_count": retry_count,
                "expiry_timestamp": expiry_timestamp
            }
            
            logger.info(f"Publishing system notification: app_id={app_id}, notification_id={notification_id}, partition={partition}")
            self.publish_message(message_data, partition=partition, key=notification_id)
            
        except Exception as e:
            logger.error(f"Error publishing system notification: {str(e)}")
            raise


if __name__ == "__main__":
    try:
        # Create producer instance
        camera1_integration_producer_client = RTSPVideoFrameProducer(
            camera_id="camera1", 
            producer_id="camera1_integration"
        )
        
        # Run producer
        camera1_integration_producer_client.run()
        
    except Exception as e:
        logger.error(f"Failed to start producer: {str(e)}")
    except KeyboardInterrupt:
        logger.info("Producer interrupted by user")
