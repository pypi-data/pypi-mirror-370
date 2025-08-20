"""Auto-generated stub for module: kafka_stream."""
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.consumer.subscription_state import ConsumerRebalanceListener
from aiokafka.errors import KafkaError
from collections import deque
from confluent_kafka import Consumer, Producer, KafkaError, TopicPartition, OFFSET_INVALID
from confluent_kafka.admin import AdminClient, NewTopic
from datetime import datetime, timezone
import asyncio
import json
import logging
import threading
import time
import uuid

# Classes
class AsyncKafkaUtils:
    """
    Utility class for asynchronous Kafka operations.
    """

    def __init__(self: Any, bootstrap_servers: str, sasl_mechanism: Optional[str] = 'SCRAM-SHA-256', sasl_username: Optional[str] = 'matrice-sdk-user', sasl_password: Optional[str] = 'matrice-sdk-password', security_protocol: str = 'SASL_PLAINTEXT') -> None: ...
        """
        Initialize async Kafka utils with bootstrap servers and SASL configuration.
        
                Args:
                    bootstrap_servers: Comma-separated list of Kafka broker addresses
                    sasl_mechanism: SASL mechanism for authentication
                    sasl_username: Username for SASL authentication
                    sasl_password: Password for SASL authentication
                    security_protocol: Security protocol for Kafka connection
        """

    async def close(self: Any) -> None: ...
        """
        Close async Kafka producer and consumer connections.
        """

    def configure_metrics_reporting(self: Any, rpc_client: Any, service_id: str = None, interval: int = 60, batch_size: int = 1000) -> None: ...
        """
        Configure background metrics reporting to backend API.
        
                Args:
                    rpc_client: RPC client instance for API communication
                    deployment_id: Deployment identifier for metrics context
                    interval: Reporting interval in seconds (default: 60)
                    batch_size: Maximum metrics per batch (default: 1000)
        """

    async def consume_message(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Consume a single message from Kafka.
        
                Args:
                    timeout: Maximum time to wait for message in seconds
        
                Returns:
                    Message dictionary if available, None if no message received
        
                Raises:
                    RuntimeError: If consumer is not initialized
                    AsyncKafkaError: If message consumption fails
        """

    def get_metrics(self: Any, clear_after_read: bool = False) -> List[Dict]: ...
        """
        Get collected metrics for aggregation and reporting.
        
                Args:
                    clear_after_read: Whether to clear metrics after reading
        
                Returns:
                    List of metric dictionaries
        """

    async def produce_message(self: Any, topic: str, value: Union[dict, str, bytes, Any], key: Optional[Union[str, bytes, Any]] = None, headers: Optional[List[Tuple[str, bytes]]] = None, timeout: float = 30.0) -> None: ...
        """
        Produce a message to a Kafka topic.
        
                Args:
                    topic: Topic to produce to
                    value: Message value (dict will be converted to JSON)
                    key: Optional message key
                    headers: Optional message headers
                    timeout: Maximum time to wait for message delivery in seconds
        
                Raises:
                    RuntimeError: If producer is not initialized
                    ValueError: If topic or value is invalid
                    AsyncKafkaError: If message production fails
        """

    async def setup_consumer(self: Any, topics: List[str], group_id: str, group_instance_id: str = None, config: Optional[Dict] = None) -> None: ...
        """
        Set up async Kafka consumer.
        
                Args:
                    topics: List of topics to subscribe to
                    group_id: Consumer group ID
                    group_instance_id: Consumer group instance ID for static membership
                    config: Additional consumer configuration
        
                Raises:
                    ValueError: If topics list is empty
                    AsyncKafkaError: If consumer initialization fails
        """

    async def setup_producer(self: Any, config: Optional[Dict] = None) -> None: ...
        """
        Set up async Kafka producer.
        
                Args:
                    config: Additional producer configuration
        
                Raises:
                    AsyncKafkaError: If producer initialization fails
        """

    def stop_metrics_reporting(self: Any) -> None: ...
        """
        Stop the background metrics reporting thread (async version).
        """

class KafkaUtils:
    """
    Utility class for synchronous Kafka operations.
    """

    def __init__(self: Any, bootstrap_servers: str, sasl_mechanism: Optional[str] = 'SCRAM-SHA-256', sasl_username: Optional[str] = 'matrice-sdk-user', sasl_password: Optional[str] = 'matrice-sdk-password', security_protocol: str = 'SASL_PLAINTEXT') -> None: ...
        """
        Initialize Kafka utils with bootstrap servers and SASL configuration.
        
                Args:
                    bootstrap_servers: Comma-separated list of Kafka broker addresses
                    sasl_mechanism: SASL mechanism for authentication
                    sasl_username: Username for SASL authentication
                    sasl_password: Password for SASL authentication
                    security_protocol: Security protocol for Kafka connection
        """

    def close(self: Any) -> None: ...
        """
        Close Kafka producer and consumer connections.
        """

    def configure_metrics_reporting(self: Any, rpc_client: Any, service_id: str = None, interval: int = 60, batch_size: int = 1000) -> None: ...
        """
        Configure background metrics reporting to backend API.
        
                Args:
                    rpc_client: RPC client instance for API communication
                    deployment_id: Deployment identifier for metrics context
                    interval: Reporting interval in seconds (default: 60)
                    batch_size: Maximum metrics per batch (default: 1000)
        """

    def consume_message(self: Any, timeout: float = 1.0) -> Optional[Dict]: ...
        """
        Consume single message from subscribed topics.
        
                Args:
                    timeout: Maximum time to block waiting for message in seconds
        
                Returns:
                    Message dict if available, None if timeout. Dict contains:
                        - topic: Topic name
                        - partition: Partition number
                        - offset: Message offset
                        - key: Message key (if present)
                        - value: Message value
                        - headers: Message headers (if present)
                        - timestamp: Message timestamp
        
                Raises:
                    RuntimeError: If consumer is not set up
                    KafkaError: If message consumption fails
        """

    def create_topic_dynamic(self: Any, topic: str, partitions: int, replication: int, kafka_ip: str = None, kafka_port: str = None) -> bool: ...
        """
        Create a Kafka topic dynamically - equivalent to Go CreateTopic().
        
                Args:
                    topic: Topic name to create
                    partitions: Number of partitions
                    replication: Replication factor
                    kafka_ip: Kafka server IP (optional, uses existing bootstrap_servers if None)
                    kafka_port: Kafka server port (optional, uses existing bootstrap_servers if None)
        
                Returns:
                    bool: True if topic was created successfully, False otherwise
        """

    def get_consumer(self: Any, topic: str = None, group_id: str = None, ip: str = None, port: str = None) -> Optional[Consumer]: ...
        """
        Get existing consumer instance or create new one - equivalent to Go GetConsumer().
        
                Args:
                    topic: Topic to subscribe to (optional if consumer already set up)
                    group_id: Consumer group ID (optional if consumer already set up)
                    ip: Kafka server IP (ignored if consumer already set up)
                    port: Kafka server port (ignored if consumer already set up)
        
                Returns:
                    Consumer instance (existing self.consumer) or newly created consumer
        """

    def get_metrics(self: Any, clear_after_read: bool = False) -> List[Dict]: ...
        """
        Get collected metrics for aggregation and reporting.
        
                Args:
                    clear_after_read: Whether to clear metrics after reading
        
                Returns:
                    List of metric dictionaries
        """

    def produce_message(self: Any, topic: str, value: Union[dict, str, bytes, Any], key: Optional[Union[str, bytes, Any]] = None, headers: Optional[List[Tuple]] = None, timeout: float = 30.0, wait_for_delivery: bool = False) -> None: ...
        """
        Produce message to Kafka topic.
        
                Args:
                    topic: Topic to produce to
                    value: Message value (dict will be converted to JSON)
                    key: Optional message key
                    headers: Optional list of (key, value) tuples for message headers
                    timeout: Maximum time to wait for message delivery in seconds
                    wait_for_delivery: Whether to wait for delivery confirmation
        
                Raises:
                    RuntimeError: If producer is not set up
                    KafkaError: If message production fails
                    ValueError: If topic is empty or value is None
        """

    def publish_message_with_timestamp(self: Any, topic: str, key: Any, value: Any, ip: str = None, port: str = None) -> bool: ...
        """
        Publish message using Kafka message timestamp (no headers) - equivalent to Go Publish().
        
                Args:
                    topic: Topic to publish to
                    key: Message key as bytes
                    value: Message value as bytes
                    ip: Kafka server IP (ignored if producer already set up)
                    port: Kafka server port (ignored if producer already set up)
        
                Returns:
                    bool: True if message was published successfully, False otherwise
        """

    def read_consumer_with_latency(self: Any, consumer: Any = None, ip: str = None, port: str = None) -> Tuple[Optional[Dict], Optional[float], Optional[str]]: ...
        """
        Read message from consumer with latency calculation - equivalent to Go ReadConsumer().
        
                Args:
                    consumer: Consumer instance to read from (uses self.consumer if None)
                    ip: Kafka server IP (ignored, for Go compatibility)
                    port: Kafka server port (ignored, for Go compatibility)
        
                Returns:
                    Tuple of (message_dict, latency_seconds, error_string)
        """

    def setup_consumer(self: Any, topics: List[str], group_id: str, group_instance_id: str = None, config: Optional[Dict] = None) -> None: ...
        """
        Set up Kafka consumer for given topics.
        
                Args:
                    topics: List of topics to subscribe to
                    group_id: Consumer group ID
                    group_instance_id: Consumer group instance ID for static membership
                    config: Additional consumer configuration
        
                Raises:
                    KafkaError: If consumer initialization or subscription fails
                    ValueError: If topics list is empty
        """

    def setup_producer(self: Any, config: Optional[Dict] = None) -> None: ...
        """
        Set up Kafka producer with optional config.
        
                Args:
                    config: Additional producer configuration
        
                Raises:
                    KafkaError: If producer initialization fails
        """

    def stop_metrics_reporting(self: Any) -> None: ...
        """
        Stop the background metrics reporting thread.
        """

class MatriceKafkaDeployment:
    """
    Class for managing Kafka deployments for Matrice streaming API.
    """

    def __init__(self: Any, session: Any, service_id: str, type: str, consumer_group_id: str = None, consumer_group_instance_id: str = None, sasl_mechanism: Optional[str] = 'SCRAM-SHA-256', sasl_username: Optional[str] = 'matrice-sdk-user', sasl_password: Optional[str] = 'matrice-sdk-password', security_protocol: str = 'SASL_PLAINTEXT', custom_request_service_id: str = None, custom_result_service_id: str = None, enable_metrics: bool = True, metrics_interval: int = 60) -> None: ...
        """
        Initialize Kafka deployment with deployment ID.
        
                Args:
                    session: Session object for authentication and RPC
                    service_id: ID of the deployment/service (used as deployment_id for metrics)
                    type: Type of deployment ("client" or "server")
                    consumer_group_id: Kafka consumer group ID
                    consumer_group_instance_id: Kafka consumer group instance ID for static membership
                    sasl_mechanism: SASL mechanism for authentication
                    sasl_username: Username for SASL authentication
                    sasl_password: Password for SASL authentication
                    security_protocol: Security protocol for Kafka connection
                    custom_request_service_id: Custom request service ID
                    custom_result_service_id: Custom result service ID
                    enable_metrics: Enable metrics reporting
                    metrics_interval: Metrics reporting interval in seconds
                Raises:
                    ValueError: If type is not "client" or "server"
        """

    async def async_consume_message(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Consume a message from Kafka asynchronously.
        
                Args:
                    timeout: Maximum time to wait for message in seconds
        
                Returns:
                    Message dictionary if available, None if no message received
        
                Raises:
                    RuntimeError: If consumer is not initialized
                    AsyncKafkaError: If message consumption fails
        """

    async def async_produce_message(self: Any, message: dict, timeout: float = 60.0, key: Optional[str] = None) -> None: ...
        """
        Produce a message to Kafka asynchronously.
        
                Args:
                    message: Message to produce
                    timeout: Maximum time to wait for message delivery in seconds
                    key: Optional key for message partitioning (stream_id/camera_id)
        
                Raises:
                    RuntimeError: If producer is not initialized or event loop is unavailable
                    ValueError: If message is invalid
                    AsyncKafkaError: If message production fails
        """

    def check_setup_success(self: Any) -> bool: ...
        """
        Check if the Kafka setup is successful and attempt to recover if not.
        
                Returns:
                    bool: True if setup was successful, False otherwise
        """

    async def close(self: Any) -> None: ...
        """
        Close Kafka producer and consumer connections.
        
                This method gracefully closes all Kafka connections without raising exceptions
                to ensure proper cleanup during shutdown.
        """

    def configure_metrics_reporting(self: Any, interval: int = 60, batch_size: int = 1000) -> None: ...
        """
        Configure background metrics reporting for both sync and async Kafka utilities.
        
                This method enables automatic metrics collection and reporting to the backend API
                for all Kafka operations performed through this deployment.
        
                Args:
                    interval: Reporting interval in seconds (default: 60)
                    batch_size: Maximum metrics per batch (default: 1000)
        """

    def consume_message(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Consume a message from Kafka.
        
                Args:
                    timeout: Maximum time to wait for message in seconds
        
                Returns:
                    Message dictionary if available, None if no message received
        
                Raises:
                    RuntimeError: If consumer is not initialized
                    KafkaError: If message consumption fails
        """

    def get_all_metrics(self: Any) -> Dict: ...
        """
        Get aggregated metrics from all Kafka utilities.
        
                Returns:
                    Dict: Combined metrics from sync and async Kafka utilities
        """

    def get_kafka_info(self: Any) -> Any: ...
        """
        Get Kafka setup information from the API.
        
                Returns:
                    Tuple containing (setup_success, bootstrap_server, request_topic, result_topic)
        
                Raises:
                    ValueError: If API requests fail or return invalid data
        """

    def get_metrics_summary(self: Any) -> Dict: ...
        """
        Get a summary of metrics from all Kafka utilities.
        
                Returns:
                    Dict: Summarized metrics with counts and statistics
        """

    def produce_message(self: Any, message: dict, timeout: float = 60.0, key: Optional[str] = None) -> None: ...
        """
        Produce a message to Kafka.
        
                Args:
                    message: Message to produce
                    timeout: Maximum time to wait for message delivery in seconds
                    key: Optional key for message partitioning (stream_id/camera_id)
        
                Raises:
                    RuntimeError: If producer is not initialized
                    ValueError: If message is invalid
                    KafkaError: If message production fails
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the Kafka producer and consumer connections.
        """

