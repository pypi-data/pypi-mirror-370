"""Auto-generated stub for module: aggregator."""
from typing import Any, Dict, List, Optional

from collections import defaultdict
from queue import Queue, Empty
import copy
import logging
import threading
import time

# Classes
class ResultsAggregator:
    """
    Handles complex aggregation and combination of synchronized results from multiple deployments.
    This component takes synchronized results and combines them into meaningful aggregated outputs
    while maintaining consistent structure with individual deployment results.
    """

    def __init__(self: Any, synchronized_results_queue: Any, aggregate_by_location: bool = False) -> None: ...
        """
        Initialize the results aggregator.
        
        Args:
            synchronized_results_queue: Queue containing synchronized results from synchronizer
            aggregation_strategies: List of aggregation strategies to apply
        """

    def cleanup(self: Any) -> None: ...
        """
        Clean up resources.
        """

    def get_health_status(self: Any) -> Dict[str, Any]: ...
        """
        Get health status of the aggregator.
        """

    def get_stats(self: Any) -> Dict[str, Any]: ...
        """
        Get current aggregation statistics.
        """

    def start_aggregation(self: Any) -> bool: ...
        """
        Start the results aggregation process.
        
        Returns:
            bool: True if aggregation started successfully, False otherwise
        """

    def stop_aggregation(self: Any) -> Any: ...
        """
        Stop the results aggregation process.
        """

