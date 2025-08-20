import smtplib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
from .common_utils import config_loader, LOG

# Optional PLC dependencies
try:
    from opcua import Client as OPCClient
    from opcua import ua
    OPCUA_AVAILABLE = True
except ImportError:
    OPCUA_AVAILABLE = False
    LOG.warning("OPC-UA library not available. PLC notifications will be disabled.")


class NotificationType(Enum):
    """Supported notification types."""
    EMAIL = "email"
    PLC = "plc"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class NotificationMessage:
    """Notification message structure."""
    title: str
    content: str
    level: AlertLevel
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EmailConfig:
    """Email notification configuration."""
    smtp_server: str
    smtp_port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True
    sender_email: Optional[str] = None
    recipients: List[str] = None
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []


@dataclass
class PLCConfig:
    """PLC notification configuration."""
    server_url: str
    namespace_index: int = 2
    alarm_node_id: Optional[str] = None
    connection_timeout: int = 30
    session_timeout: int = 60000
    

class NotificationProvider(ABC):
    """Abstract base class for notification providers."""
    
    @abstractmethod
    def send_notification(self, message: NotificationMessage) -> bool:
        """Send notification message.
        
        Args:
            message: The notification message to send
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the notification provider is available.
        
        Returns:
            bool: True if provider is ready to send notifications
        """
        pass


class EmailNotificationProvider(NotificationProvider):
    """Email notification provider using SMTP."""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self._lock = threading.Lock()
        
    def send_notification(self, message: NotificationMessage) -> bool:
        """Send email notification."""
        if not self.config.recipients:
            LOG.warning("No email recipients configured")
            return False
            
        try:
            with self._lock:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.config.sender_email or self.config.username
                msg['To'] = ', '.join(self.config.recipients)
                msg['Subject'] = f"[{message.level.value.upper()}] {message.title}"
                
                # Email body
                body = self._format_email_body(message)
                msg.attach(MIMEText(body, 'html'))
                
                # Send email
                with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                    if self.config.use_tls:
                        server.starttls()
                    
                    if self.config.username and self.config.password:
                        server.login(self.config.username, self.config.password)
                    
                    server.send_message(msg)
                    
                LOG.info(f"Email notification sent successfully: {message.title}")
                return True
                
        except Exception as e:
            LOG.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def _format_email_body(self, message: NotificationMessage) -> str:
        """Format email body with HTML."""
        level_colors = {
            AlertLevel.INFO: "#17a2b8",
            AlertLevel.WARNING: "#ffc107", 
            AlertLevel.ERROR: "#dc3545",
            AlertLevel.CRITICAL: "#6f42c1"
        }
        
        color = level_colors.get(message.level, "#6c757d")
        
        html_body = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
                    <h2 style="margin: 0;">{message.title}</h2>
                    <p style="margin: 5px 0 0 0;">Level: {message.level.value.upper()}</p>
                </div>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #dee2e6;">
                    <h3>Message:</h3>
                    <p>{message.content}</p>
                    <hr>
                    <p><strong>Timestamp:</strong> {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    {self._format_metadata(message.metadata)}
                </div>
            </div>
        </body>
        </html>
        """
        return html_body
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for email display."""
        if not metadata:
            return ""
        
        metadata_html = "<h4>Additional Information:</h4><ul>"
        for key, value in metadata.items():
            metadata_html += f"<li><strong>{key}:</strong> {value}</li>"
        metadata_html += "</ul>"
        return metadata_html
    
    def is_available(self) -> bool:
        """Check if email service is available."""
        try:
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=10) as server:
                server.noop()
            return True
        except Exception as e:
            LOG.warning(f"Email service not available: {str(e)}")
            return False


class PLCNotificationProvider(NotificationProvider):
    """PLC notification provider using OPC-UA."""
    
    def __init__(self, config: PLCConfig):
        self.config = config
        self._client = None
        self._lock = threading.Lock()
        
    def send_notification(self, message: NotificationMessage) -> bool:
        """Send PLC notification via OPC-UA."""
        if not OPCUA_AVAILABLE:
            LOG.error("OPC-UA library not available for PLC notifications")
            return False
            
        try:
            with self._lock:
                if not self._ensure_connection():
                    return False
                
                # Write alarm data to PLC
                alarm_data = self._format_plc_data(message)
                
                if self.config.alarm_node_id:
                    node = self._client.get_node(self.config.alarm_node_id)
                    node.set_value(alarm_data)
                else:
                    # Default behavior: write to a standard alarm node
                    # This would need to be customized based on your PLC setup
                    LOG.warning("No alarm node ID configured for PLC notification")
                    
                LOG.info(f"PLC notification sent successfully: {message.title}")
                return True
                
        except Exception as e:
            LOG.error(f"Failed to send PLC notification: {str(e)}")
            self._disconnect()
            return False
    
    def _ensure_connection(self) -> bool:
        """Ensure PLC connection is established."""
        try:
            if self._client is None:
                self._client = OPCClient(self.config.server_url)
                self._client.set_session_timeout(self.config.session_timeout)
                
            if not self._client.get_session():
                self._client.connect()
                
            return True
            
        except Exception as e:
            LOG.error(f"Failed to connect to PLC: {str(e)}")
            return False
    
    def _disconnect(self):
        """Disconnect from PLC."""
        try:
            if self._client:
                self._client.disconnect()
                self._client = None
        except Exception as e:
            LOG.warning(f"Error during PLC disconnect: {str(e)}")
    
    def _format_plc_data(self, message: NotificationMessage) -> str:
        """Format message data for PLC."""
        # Simple string format - customize based on your PLC requirements
        return f"{message.level.value}|{message.title}|{message.content}|{message.timestamp.isoformat()}"
    
    def is_available(self) -> bool:
        """Check if PLC service is available."""
        if not OPCUA_AVAILABLE:
            return False
            
        try:
            with self._lock:
                return self._ensure_connection()
        except Exception:
            return False
    
    def __del__(self):
        """Cleanup on object destruction."""
        self._disconnect()


class NotificationManager:
    """Central notification manager supporting multiple providers."""
    
    def __init__(self):
        self.providers: Dict[NotificationType, NotificationProvider] = {}
        self._config = config_loader()
        self._setup_providers()
        
    def _setup_providers(self):
        """Setup notification providers based on configuration."""
        connections = self._config.get('connections', {})
        
        # Setup Email provider
        if 'smtp' in connections:
            smtp_config = connections['smtp']
            email_config = EmailConfig(
                smtp_server=smtp_config.get('server', 'localhost'),
                smtp_port=smtp_config.get('port', 587),
                username=smtp_config.get('username'),
                password=smtp_config.get('password'),
                use_tls=smtp_config.get('use_tls', True),
                sender_email=smtp_config.get('sender_email'),
                recipients=smtp_config.get('recipients', [])
            )
            self.providers[NotificationType.EMAIL] = EmailNotificationProvider(email_config)
            LOG.info("Email notification provider initialized")
        
        # Setup PLC provider
        if 'plc' in connections:
            plc_config = connections['plc']
            plc_notification_config = PLCConfig(
                server_url=plc_config.get('broadcast_plc_address', 'opc.tcp://localhost:4840'),
                namespace_index=plc_config.get('namespace_index', 2),
                alarm_node_id=plc_config.get('alarm_node_id'),
                connection_timeout=plc_config.get('connection_timeout', 30),
                session_timeout=plc_config.get('session_timeout', 60000)
            )
            self.providers[NotificationType.PLC] = PLCNotificationProvider(plc_notification_config)
            LOG.info("PLC notification provider initialized")
    
    def send_notification(self, 
                         message: NotificationMessage, 
                         notification_types: List[NotificationType] = None) -> Dict[NotificationType, bool]:
        """Send notification through specified providers.
        
        Args:
            message: The notification message to send
            notification_types: List of notification types to use. If None, uses all available.
            
        Returns:
            Dict mapping notification types to success status
        """
        if notification_types is None:
            notification_types = list(self.providers.keys())
        
        results = {}
        
        for notification_type in notification_types:
            provider = self.providers.get(notification_type)
            if provider:
                if provider.is_available():
                    results[notification_type] = provider.send_notification(message)
                else:
                    LOG.warning(f"{notification_type.value} provider is not available")
                    results[notification_type] = False
            else:
                LOG.warning(f"No provider configured for {notification_type.value}")
                results[notification_type] = False
        
        return results
    
    def send_alert(self, 
                  title: str, 
                  content: str, 
                  level: AlertLevel = AlertLevel.INFO,
                  metadata: Dict[str, Any] = None,
                  notification_types: List[NotificationType] = None) -> Dict[NotificationType, bool]:
        """Convenience method to send alert.
        
        Args:
            title: Alert title
            content: Alert content/description
            level: Alert severity level
            metadata: Additional metadata
            notification_types: List of notification types to use
            
        Returns:
            Dict mapping notification types to success status
        """
        message = NotificationMessage(
            title=title,
            content=content,
            level=level,
            metadata=metadata or {}
        )
        
        return self.send_notification(message, notification_types)
    
    def get_provider_status(self) -> Dict[NotificationType, bool]:
        """Get status of all notification providers.
        
        Returns:
            Dict mapping notification types to availability status
        """
        return {nt: provider.is_available() for nt, provider in self.providers.items()}


# Singleton instance for global use
_notification_manager = None
_manager_lock = threading.Lock()


def get_notification_manager() -> NotificationManager:
    """Get singleton notification manager instance."""
    global _notification_manager
    
    if _notification_manager is None:
        with _manager_lock:
            if _notification_manager is None:
                _notification_manager = NotificationManager()
    
    return _notification_manager


# Convenience functions
def send_email_alert(title: str, content: str, level: AlertLevel = AlertLevel.INFO, 
                    metadata: Dict[str, Any] = None) -> bool:
    """Send email alert only."""
    manager = get_notification_manager()
    results = manager.send_alert(title, content, level, metadata, [NotificationType.EMAIL])
    return results.get(NotificationType.EMAIL, False)


def send_plc_alert(title: str, content: str, level: AlertLevel = AlertLevel.INFO,
                  metadata: Dict[str, Any] = None) -> bool:
    """Send PLC alert only."""
    manager = get_notification_manager()
    results = manager.send_alert(title, content, level, metadata, [NotificationType.PLC])
    return results.get(NotificationType.PLC, False)


def send_all_alerts(title: str, content: str, level: AlertLevel = AlertLevel.INFO,
                   metadata: Dict[str, Any] = None) -> Dict[NotificationType, bool]:
    """Send alert through all available notification types."""
    manager = get_notification_manager()
    return manager.send_alert(title, content, level, metadata)


if __name__ == "__main__":
    # Example usage
    manager = get_notification_manager()
    
    # Check provider status
    status = manager.get_provider_status()
    print(f"Provider status: {status}")
    
    # Send test alerts
    test_metadata = {
        "source": "notification_utils_test",
        "component": "camera1",
        "error_code": "CAM001"
    }
    
    # Send warning alert to all providers
    results = manager.send_alert(
        title="Camera Connection Warning",
        content="Camera1 connection is unstable. Frame rate dropped below threshold.",
        level=AlertLevel.WARNING,
        metadata=test_metadata
    )
    
    print(f"Alert results: {results}")
    
    # Send critical alert via email only
    email_result = send_email_alert(
        title="System Critical Error",
        content="Database connection lost. Immediate attention required.",
        level=AlertLevel.CRITICAL,
        metadata={"database": "aws_db_eh080", "retry_count": 3}
    )
    
    print(f"Email alert result: {email_result}")