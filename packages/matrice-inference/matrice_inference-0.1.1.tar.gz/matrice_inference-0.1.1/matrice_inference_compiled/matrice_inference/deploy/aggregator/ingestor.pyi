"""Auto-generated stub for module: ingestor."""
from typing import Any, Dict, List, Optional, Tuple

from matrice_common.session import Session
from matrice_inference.deploy.stream.kafka_stream import MatriceKafkaDeployment
from queue import Empty, PriorityQueue, Full
import itertools
import logging
import threading
import time

# Classes
class ResultsIngestor:
    """
    Streams and manages results from multiple deployments.
    Handles result collection, queuing, and distribution with enhanced structure consistency.
    """

    def __init__(self: Any, deployment_ids: List[str], session: Session, consumer_timeout: float = 60) -> None: ...
        """
        Initialize the results streamer.
        
        Args:
            deployment_ids: List of deployment IDs
            session: Session object for authentication
            consumer_timeout: Timeout for consuming results from deployments
        """

    def cleanup(self: Any) -> None: ...
        """
        Clean up all resources.
        """

    def get_all_results(self: Any, timeout: float = 1.0) -> List[Dict]: ...
        """
        Get results from all deployment queues.
        
        Args:
            timeout: Timeout for getting results
        
        Returns:
            List[Dict]: List of result dictionaries
        """

    def get_health_status(self: Any) -> Dict: ...
        """
        Get health status of the results streamer.
        """

    def get_results(self: Any, deployment_id: str, timeout: float = 1.0) -> Optional[Dict]: ...
        """
        Get a result from a specific deployment's priority queue.
        
        Args:
            deployment_id: ID of the deployment
            timeout: Timeout for getting the result
        
        Returns:
            Dict: Result dictionary or None if timeout/no result
        """

    def get_stats(self: Any) -> Dict: ...
        """
        Get current statistics.
        """

    def start_streaming(self: Any) -> bool: ...
        """
        Start streaming results from all deployments.
        
        Returns:
            bool: True if streaming started successfully, False otherwise
        """

    def stop_streaming(self: Any) -> None: ...
        """
        Stop all streaming operations.
        """

