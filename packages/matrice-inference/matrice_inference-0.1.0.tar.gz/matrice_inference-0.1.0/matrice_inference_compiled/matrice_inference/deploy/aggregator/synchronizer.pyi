"""Auto-generated stub for module: synchronizer."""
from typing import Any, Dict, List, Tuple

from collections import defaultdict
from queue import Queue, Empty, PriorityQueue
import logging
import threading
import time

# Classes
class ResultsSynchronizer:
    """
    Handles synchronization of results from multiple deployments by stream_key and input_order.
    Ensures consistent structure and proper error handling for the aggregation pipeline.
    """

    def __init__(self: Any, results_queues: Dict[str, PriorityQueue], sync_timeout: float = 60.0) -> None: ...
        """
        Initialize the results synchronizer.
        
        Args:
            results_queues: Dictionary of priority queues containing results from deployments
            sync_timeout: Maximum time to wait for input_order synchronization (in seconds)
        """

    def cleanup(self: Any) -> None: ...
        """
        Clean up resources.
        """

    def force_sync_pending(self: Any) -> int: ...
        """
        Force synchronization of all pending results regardless of completeness.
        """

    def get_health_status(self: Any) -> Dict: ...
        """
        Get health status of the synchronizer.
        """

    def get_stats(self: Any) -> Dict: ...
        """
        Get current synchronization statistics.
        """

    def start_synchronization(self: Any) -> bool: ...
        """
        Start the results synchronization process.
        
        Returns:
            bool: True if synchronization started successfully, False otherwise
        """

    def stop_synchronization(self: Any) -> Any: ...
        """
        Stop the results synchronization process.
        """

