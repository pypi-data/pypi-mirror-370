import os
import yaml
import logging
from confluent_kafka import KafkaError

config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/config.yaml')

def _log():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

LOG = _log()

def config_loader():
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except yaml.YAMLError as e:
        LOG.error(f"Error parsing YAML configuration: {str(e)}")
        raise


def delivery_callback(err, msg):
    """
    Callback function for Kafka producer delivery reports.

    This function is triggered when the broker acknowledges a message (successfully or with error).
    It's critical for handling message delivery guarantees in asynchronous operations.

    Args:
        err (KafkaError): Error object if delivery failed, None on success.
        msg (Message): The message object that was produced (or failed).

    Important:
        - This callback executes in the producer's poll() thread
        - Keep processing minimal to avoid blocking the producer
        - Handle retriable errors vs permanent failures appropriately
    """
    if err is not None:
        # Message delivery failed
        LOG.error(f"[ERROR] Delivery failed for message: {err.str()}")

        # Classify error types for proper handling
        if err.code() == KafkaError._MSG_TIMED_OUT:
            # Retriable error: Message timed out (network issues, broker overload)
            LOG.error("  Reason: Request timeout - consider increasing 'message.timeout.ms'")
            # Application logic: Retry or log to dead-letter queue

        elif err.code() == KafkaError._UNKNOWN_TOPIC_OR_PART:
            # Permanent error: Topic doesn't exist
            LOG.error("  Reason: Topic/partition does not exist - check topic configuration")
            # Application logic: Alert admin or create topic

        elif err.code() == KafkaError._MSG_SIZE_TOO_LARGE:
            # Permanent error: Message too large
            max_size = msg.max_size() if hasattr(msg, 'max_size') else "N/A"
            LOG.error(f"  Reason: Message size {len(msg.value())} bytes exceeds broker limit {max_size}")
            # Application logic: Split message or adjust broker config

        elif err.retriable():
            # General retriable error (network blip, not leader)
            LOG.error(f"  Reason: Temporary failure ({err.str()}) - will retry automatically")
        else:
            # Permanent non-retriable error
            LOG.error(f"  Reason: Permanent failure ({err.code()}): {err.str()}")
            # Application logic: Dead-letter queue or admin alert

    else:
        # Message successfully delivered
        LOG.info(f"[SUCCESS] Delivered message to "
              f"topic={msg.topic()} "
              f"partition={msg.partition()} "
              f"offset={msg.offset()} "
              f"timestamp={msg.timestamp()[1] if msg.timestamp() else 'N/A'}")


if __name__ == '__main__':
    LOG.error(config_loader())