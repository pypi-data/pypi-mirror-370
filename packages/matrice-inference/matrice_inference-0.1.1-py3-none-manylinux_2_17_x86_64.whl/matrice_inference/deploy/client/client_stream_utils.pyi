"""Auto-generated stub for module: client_stream_utils."""
from typing import Any, Dict, Optional, Tuple, Union

from datetime import datetime, timezone
from matrice_inference.deploy.optimize.transmission import ClientTransmissionHandler
from matrice_inference.deploy.stream.kafka_stream import MatriceKafkaDeployment
import base64
import cv2
import hashlib
import logging
import numpy as np
import threading
import time

# Classes
class ClientStreamUtils:
    def __init__(self: Any, session: Any, service_id: str, consumer_group_id: str = None, consumer_group_instance_id: str = None, threshold_a: float = 0.95, threshold_b: float = 0.85, enable_intelligent_transmission: bool = True) -> None: ...
        """
        Initialize ClientStreamUtils.
        
                Args:
                    session: Session object for making RPC calls
                    service_id: ID of the deployment
                    consumer_group_id: Kafka consumer group ID
                    consumer_group_instance_id: Unique consumer group instance ID to prevent rebalancing
                    threshold_a: High similarity threshold for skipping transmission (default: 0.95)
                    threshold_b: Medium similarity threshold for difference transmission (default: 0.85)
                    enable_intelligent_transmission: Whether to enable intelligent frame transmission
        """

    async def async_consume_result(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Consume the Kafka stream result asynchronously.
        """

    async def async_produce_request(self: Any, input_data: Any, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, metadata: Optional[Dict] = None, timeout: float = 60.0) -> bool: ...
        """
        Produce a unified stream request to Kafka asynchronously.
        """

    async def close(self: Any) -> None: ...
        """
        Close all client connections including Kafka stream.
        """

    def consume_result(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Consume the Kafka stream result.
        """

    def get_transmission_stats(self: Any) -> Dict[str, Any]: ...
        """
        Get intelligent transmission statistics.
        
                Returns:
                    Dictionary with transmission statistics
        """

    def produce_request(self: Any, input_data: Any, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, metadata: Optional[Dict] = None, timeout: float = 60.0) -> bool: ...
        """
        Simple function to produce a stream request to Kafka.
        """

    def reset_transmission_stats(self: Any) -> None: ...
        """
        Reset transmission statistics.
        """

    def start_background_stream(self: Any, input: Union[str, int], fps: int = 10, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, quality: int = 95, width: Optional[int] = None, height: Optional[int] = None, simulate_video_file_stream: bool = False, is_video_chunk: bool = False, chunk_duration_seconds: Optional[float] = None, chunk_frames: Optional[int] = None) -> bool: ...
        """
        Start a stream input to the Kafka stream in a background thread.
        """

    def start_stream(self: Any, input: Union[str, int], fps: int = 10, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, quality: int = 95, width: Optional[int] = None, height: Optional[int] = None, simulate_video_file_stream: bool = False, is_video_chunk: bool = False, chunk_duration_seconds: Optional[float] = None, chunk_frames: Optional[int] = None) -> bool: ...
        """
        Start a stream input to the Kafka stream in the current thread.
        """

    def stop_streaming(self: Any) -> None: ...
        """
        Stop all streaming threads.
        """

