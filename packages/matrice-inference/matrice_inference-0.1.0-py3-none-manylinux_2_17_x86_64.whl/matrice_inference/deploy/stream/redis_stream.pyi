"""Auto-generated stub for module: redis_stream."""
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from collections import deque
from datetime import datetime, timezone
from redis.exceptions import ConnectionError, TimeoutError
import aioredis
import asyncio
import json
import logging
import redis
import threading
import time
import uuid

# Classes
class AsyncRedisUtils:
    """
    Utility class for asynchronous Redis operations.
    """

    def __init__(self: Any, host: str = 'localhost', port: int = 6379, password: Optional[str] = None, username: Optional[str] = None, db: int = 0, ssl: bool = False, ssl_verify: bool = True, connection_timeout: int = 30) -> None: ...
        """
        Initialize async Redis utils with connection parameters.
        
                Args:
                    host: Redis server hostname or IP address
                    port: Redis server port
                    password: Password for Redis authentication
                    username: Username for Redis authentication (Redis 6.0+)
                    db: Database number to connect to
                    ssl: Whether to use SSL/TLS connection
                    ssl_verify: Whether to verify SSL certificates
                    connection_timeout: Connection timeout in seconds
        """

    async def close(self: Any) -> None: ...
        """
        Close async Redis client and subscriber connections.
        """

    def configure_metrics_reporting(self: Any, rpc_client: Any, deployment_id: str = None, interval: int = 60, batch_size: int = 1000) -> None: ...
        """
        Configure background metrics reporting to backend API.
        
                Args:
                    rpc_client: RPC client instance for API communication
                    deployment_id: Deployment identifier for metrics context
                    interval: Reporting interval in seconds (default: 60)
                    batch_size: Maximum metrics per batch (default: 1000)
        """

    async def get_message(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Get a single message from subscribed channels asynchronously.
        
                Args:
                    timeout: Maximum time to wait for message in seconds
        
                Returns:
                    Message dictionary if available, None if no message received
        
                Raises:
                    RuntimeError: If subscriber is not initialized
                    RedisConnectionError: If message retrieval fails
        """

    def get_metrics(self: Any, clear_after_read: bool = False) -> List[Dict]: ...
        """
        Get collected metrics for aggregation and reporting.
        
                Args:
                    clear_after_read: Whether to clear metrics after reading
        
                Returns:
                    List of metric dictionaries
        """

    async def listen_for_messages(self: Any, callback: Optional[Callable] = None) -> None: ...
        """
        Listen for messages on subscribed channels asynchronously (blocking).
        
                Args:
                    callback: Optional global callback function for all messages
        
                Raises:
                    RuntimeError: If subscriber is not set up
                    RedisConnectionError: If listening fails
        """

    async def publish_message(self: Any, channel: str, message: Union[dict, str, bytes, Any], timeout: float = 30.0) -> int: ...
        """
        Publish a message to a Redis channel asynchronously.
        
                Args:
                    channel: Channel to publish to
                    message: Message to publish (dict will be converted to JSON)
                    timeout: Maximum time to wait for publish completion in seconds
        
                Returns:
                    Number of subscribers that received the message
        
                Raises:
                    RuntimeError: If client is not initialized
                    ValueError: If channel or message is invalid
                    RedisConnectionError: If message publication fails
        """

    async def setup_client(self: Any, **kwargs: Any) -> None: ...
        """
        Set up async Redis client connection.
        
                Args:
                    **kwargs: Additional Redis client configuration options
        
                Raises:
                    RedisConnectionError: If client initialization fails
        """

    async def setup_subscriber(self: Any, **kwargs: Any) -> None: ...
        """
        Set up async Redis pub/sub subscriber.
        
                Args:
                    **kwargs: Additional pub/sub configuration options
        
                Raises:
                    RedisConnectionError: If subscriber setup fails
        """

    def stop_metrics_reporting(self: Any) -> None: ...
        """
        Stop the background metrics reporting thread (async version).
        """

    async def subscribe_to_channel(self: Any, channel: str, callback: Optional[Callable] = None) -> None: ...
        """
        Subscribe to a Redis channel asynchronously.
        
                Args:
                    channel: Channel to subscribe to
                    callback: Optional callback function for message handling
        
                Raises:
                    RuntimeError: If subscriber is not set up
                    RedisConnectionError: If subscription fails
                    ValueError: If channel is empty
        """

    async def unsubscribe_from_channel(self: Any, channel: str) -> None: ...
        """
        Unsubscribe from a Redis channel asynchronously.
        
                Args:
                    channel: Channel to unsubscribe from
        
                Raises:
                    RuntimeError: If subscriber is not set up
        """

class MatriceRedisDeployment:
    """
    Class for managing Redis deployments for Matrice streaming API.
    """

    def __init__(self: Any, session: Any, service_id: str, type: str, host: str = 'localhost', port: int = 6379, password: Optional[str] = None, username: Optional[str] = None, db: int = 0, ssl: bool = False, ssl_verify: bool = True, enable_metrics: bool = True, metrics_interval: int = 60) -> None: ...
        """
        Initialize Redis deployment with deployment ID.
        
                Args:
                    session: Session object for authentication and RPC
                    service_id: ID of the deployment
                    type: Type of deployment ("client" or "server")
                    host: Redis server hostname or IP address
                    port: Redis server port
                    password: Password for Redis authentication
                    username: Username for Redis authentication (Redis 6.0+)
                    db: Database number to connect to
                    ssl: Whether to use SSL/TLS connection
                    ssl_verify: Whether to verify SSL certificates
                    enable_metrics: Whether to auto-enable metrics reporting (default: True)
                    metrics_interval: Metrics reporting interval in seconds (default: 60)
                Raises:
                    ValueError: If type is not "client" or "server"
        """

    async def async_get_message(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Get a message from Redis asynchronously.
        
                Args:
                    timeout: Maximum time to wait for message in seconds
        
                Returns:
                    Message dictionary if available, None if no message received
        
                Raises:
                    RuntimeError: If subscriber is not initialized
                    RedisConnectionError: If message retrieval fails
        """

    async def async_publish_message(self: Any, message: dict, timeout: float = 60.0) -> int: ...
        """
        Publish a message to Redis asynchronously.
        
                Args:
                    message: Message to publish
                    timeout: Maximum time to wait for message publication in seconds
        
                Returns:
                    Number of subscribers that received the message
        
                Raises:
                    RuntimeError: If client is not initialized
                    ValueError: If message is invalid
                    RedisConnectionError: If message publication fails
        """

    def check_setup_success(self: Any) -> bool: ...
        """
        Check if the Redis setup is successful.
        
                Returns:
                    bool: True if setup was successful, False otherwise
        """

    async def close(self: Any) -> None: ...
        """
        Close Redis client and subscriber connections.
        
                This method gracefully closes all Redis connections without raising exceptions
                to ensure proper cleanup during shutdown.
        """

    def configure_metrics_reporting(self: Any, interval: int = 60, batch_size: int = 1000) -> None: ...
        """
        Configure background metrics reporting for both sync and async Redis utilities.
        
                This method enables automatic metrics collection and reporting to the backend API
                for all Redis operations performed through this deployment.
        
                Args:
                    interval: Reporting interval in seconds (default: 60)
                    batch_size: Maximum metrics per batch (default: 1000)
        """

    def get_all_metrics(self: Any) -> Dict: ...
        """
        Get aggregated metrics from all Redis utilities.
        
                Returns:
                    Dict: Combined metrics from sync and async Redis utilities
        """

    def get_message(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Get a message from Redis.
        
                Args:
                    timeout: Maximum time to wait for message in seconds
        
                Returns:
                    Message dictionary if available, None if no message received
        
                Raises:
                    RuntimeError: If subscriber is not initialized
                    RedisConnectionError: If message retrieval fails
        """

    def get_metrics_summary(self: Any) -> Dict: ...
        """
        Get a summary of metrics from all Redis utilities.
        
                Returns:
                    Dict: Summarized metrics with counts and statistics
        """

    def publish_message(self: Any, message: dict, timeout: float = 60.0) -> int: ...
        """
        Publish a message to Redis.
        
                Args:
                    message: Message to publish
                    timeout: Maximum time to wait for message publication in seconds
        
                Returns:
                    Number of subscribers that received the message
        
                Raises:
                    RuntimeError: If client is not initialized
                    ValueError: If message is invalid
                    RedisConnectionError: If message publication fails
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the Redis client and subscriber connections.
        """

class RedisUtils:
    """
    Utility class for synchronous Redis operations.
    """

    def __init__(self: Any, host: str = 'localhost', port: int = 6379, password: Optional[str] = None, username: Optional[str] = None, db: int = 0, ssl: bool = False, ssl_verify: bool = True, connection_timeout: int = 30) -> None: ...
        """
        Initialize Redis utils with connection parameters.
        
                Args:
                    host: Redis server hostname or IP address
                    port: Redis server port
                    password: Password for Redis authentication
                    username: Username for Redis authentication (Redis 6.0+)
                    db: Database number to connect to
                    ssl: Whether to use SSL/TLS connection
                    ssl_verify: Whether to verify SSL certificates
                    connection_timeout: Connection timeout in seconds
        """

    def close(self: Any) -> None: ...
        """
        Close Redis client and subscriber connections.
        """

    def configure_metrics_reporting(self: Any, rpc_client: Any, deployment_id: str = None, interval: int = 60, batch_size: int = 1000) -> None: ...
        """
        Configure background metrics reporting to backend API.
        
                Args:
                    rpc_client: RPC client instance for API communication
                    deployment_id: Deployment identifier for metrics context
                    interval: Reporting interval in seconds (default: 60)
                    batch_size: Maximum metrics per batch (default: 1000)
        """

    def get_message(self: Any, timeout: float = 1.0) -> Optional[Dict]: ...
        """
        Get a single message from subscribed channels.
        
                Args:
                    timeout: Maximum time to block waiting for message in seconds
        
                Returns:
                    Message dict if available, None if timeout. Dict contains:
                        - type: Message type ('message', 'subscribe', 'unsubscribe', etc.)
                        - channel: Channel name
                        - data: Message data
                        - pattern: Pattern if pattern subscription (None otherwise)
        
                Raises:
                    RuntimeError: If subscriber is not set up
                    RedisConnectionError: If message retrieval fails
        """

    def get_metrics(self: Any, clear_after_read: bool = False) -> List[Dict]: ...
        """
        Get collected metrics for aggregation and reporting.
        
                Args:
                    clear_after_read: Whether to clear metrics after reading
        
                Returns:
                    List of metric dictionaries
        """

    def listen_for_messages(self: Any, callback: Optional[Callable] = None) -> None: ...
        """
        Listen for messages on subscribed channels (blocking).
        
                Args:
                    callback: Optional global callback function for all messages
        
                Raises:
                    RuntimeError: If subscriber is not set up
                    RedisConnectionError: If listening fails
        """

    def publish_message(self: Any, channel: str, message: Union[dict, str, bytes, Any], timeout: float = 30.0) -> int: ...
        """
        Publish message to Redis channel.
        
                Args:
                    channel: Channel to publish to
                    message: Message to publish (dict will be converted to JSON)
                    timeout: Maximum time to wait for publish completion in seconds
        
                Returns:
                    Number of subscribers that received the message
        
                Raises:
                    RuntimeError: If client is not set up
                    RedisConnectionError: If message publication fails
                    ValueError: If channel is empty or message is None
        """

    def setup_client(self: Any, **kwargs: Any) -> None: ...
        """
        Set up Redis client connection.
        
                Args:
                    **kwargs: Additional Redis client configuration options
        
                Raises:
                    RedisConnectionError: If client initialization fails
        """

    def setup_subscriber(self: Any, **kwargs: Any) -> None: ...
        """
        Set up Redis pub/sub subscriber.
        
                Args:
                    **kwargs: Additional pub/sub configuration options
        
                Raises:
                    RedisConnectionError: If subscriber setup fails
        """

    def stop_metrics_reporting(self: Any) -> None: ...
        """
        Stop the background metrics reporting thread.
        """

    def subscribe_to_channel(self: Any, channel: str, callback: Optional[Callable] = None) -> None: ...
        """
        Subscribe to a Redis channel.
        
                Args:
                    channel: Channel to subscribe to
                    callback: Optional callback function for message handling
        
                Raises:
                    RuntimeError: If subscriber is not set up
                    RedisConnectionError: If subscription fails
                    ValueError: If channel is empty
        """

    def unsubscribe_from_channel(self: Any, channel: str) -> None: ...
        """
        Unsubscribe from a Redis channel.
        
                Args:
                    channel: Channel to unsubscribe from
        
                Raises:
                    RuntimeError: If subscriber is not set up
        """

