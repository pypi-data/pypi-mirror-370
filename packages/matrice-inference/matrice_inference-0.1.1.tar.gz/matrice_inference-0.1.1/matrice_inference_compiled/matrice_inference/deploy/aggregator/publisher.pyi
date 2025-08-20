"""Auto-generated stub for module: publisher."""
from typing import Any, Dict, Optional

from matrice_common.session import Session
from matrice_inference.deploy.stream.kafka_stream import MatriceKafkaDeployment
from queue import Queue, Empty
import logging
import threading
import time

# Classes
class ResultsPublisher:
    """
    Streams final aggregated results from inference pipeline to Kafka.
    Handles result collection, queuing, and distribution with proper error handling
    for the enhanced aggregated result structure.
    """

    def __init__(self: Any, inference_pipeline_id: str, session: Session, final_results_queue: Any, analytics_summarizer: Optional[Any] = None) -> None: ...
        """
        Initialize the final results streamer.
        
        Args:
            inference_pipeline_id: ID of the inference pipeline
            session: Session object for authentication
            final_results_queue: Queue containing final aggregated results
        """

    def get_health_status(self: Any) -> Dict[str, Any]: ...
        """
        Get health status of the publisher.
        """

    def get_stats(self: Any) -> Dict[str, Any]: ...
        """
        Get streaming statistics.
        
        Returns:
            Dict containing statistics
        """

    def is_running(self: Any) -> bool: ...
        """
        Check if the streamer is currently running.
        """

    def start_streaming(self: Any) -> bool: ...
        """
        Start streaming final results to Kafka.
        
        Returns:
            bool: True if streaming started successfully, False otherwise
        """

    def stop_streaming(self: Any) -> None: ...
        """
        Stop streaming final results.
        """

