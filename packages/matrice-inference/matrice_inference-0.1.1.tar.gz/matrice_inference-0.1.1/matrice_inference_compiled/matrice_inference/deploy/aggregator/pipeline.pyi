"""Auto-generated stub for module: pipeline."""
from typing import Any, Dict

from matrice_common.session import Session
from matrice_inference.deploy.aggregator.aggregator import ResultsAggregator
from matrice_inference.deploy.aggregator.analytics import AnalyticsSummarizer
from matrice_inference.deploy.aggregator.ingestor import ResultsIngestor
from matrice_inference.deploy.aggregator.publisher import ResultsPublisher
from matrice_inference.deploy.aggregator.synchronizer import ResultsSynchronizer
from matrice_inference.deployment.inference_pipeline import InferencePipeline
from queue import Queue
import logging
import time

# Classes
class ResultsAggregationPipeline:
    """
    Enhanced deployments aggregator that handles multiple streams, synchronizes results,
    and outputs aggregated results to Kafka topics with consistent structure.
    
    This class orchestrates the complete pipeline for collecting, synchronizing, and
    publishing results from multiple ML model deployments in an inference pipeline,
    ensuring all results follow the same structure as individual deployment results.
    
    Usage Example:
        ```python
        from matrice import Session
        from matrice_inference.deploy.aggregator import ResultsAggregationPipeline
    
        # Initialize session
        session = Session(account_number="...", access_key="...", secret_key="...")
    
        # Create aggregator for an inference pipeline
        aggregator = ResultsAggregationPipeline(session, "your-inference-pipeline-id")
    
        # Setup the aggregation pipeline
        if aggregator.setup_components():
            print(f"Setup complete for {len(aggregator.deployment_ids)} deployments")
    
            # Start streaming and run until keyboard interrupt
            try:
                aggregator.start_streaming()
            except KeyboardInterrupt:
                print("Pipeline stopped by user")
            finally:
                aggregator.cleanup()
        ```
    """

    def __init__(self: Any, session: Session, action_record_id: str) -> None: ...
        """
        Initialize the deployments aggregator.
        
        Args:
            session: Session object for authentication
            action_record_id: Action Record ID
        """

    def cleanup(self: Any) -> None: ...
        """
        Clean up all resources.
        """

    def force_sync_pending_results(self: Any) -> int: ...
        """
        Force synchronization of all pending results.
        
        Returns:
            int: Number of pending results that were synchronized
        """

    def get_deployment_info(self: Any) -> Dict: ...
        """
        Get information about the deployments in this aggregator.
        
        Returns:
            Dict: Deployment information including IDs, count, and status
        """

    def get_health_status(self: Any) -> Dict: ...
        """
        Get health status of all components.
        """

    def get_stats(self: Any) -> Dict: ...
        """
        Get current statistics from all components.
        """

    def setup_components(self: Any) -> bool: ...
        """
        Setup all components and initialize the aggregation pipeline.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
        """

    def start_logging(self: Any, status_interval: int = 30) -> None: ...
        """
        Start the pipeline logging and run until interrupted.
        Args:
            status_interval: Interval in seconds between status log messages
        """

    def start_streaming(self: Any, block: bool = True) -> bool: ...
        """
        Start the complete streaming pipeline: ingestion, synchronization, aggregation, and publishing.
        
        Returns:
            bool: True if streaming started successfully, False otherwise
        """

    def stop_streaming(self: Any) -> None: ...
        """
        Stop all streaming operations in reverse order.
        """

    def update_status(self: Any, step_code: str, status: str, status_description: str) -> None: ...
        """
        Update status of data preparation.
        
                Args:
                    step_code: Code indicating current step
                    status: Status of step
                    status_description: Description of status
        """

    def wait_for_ready(self: Any, timeout: int = 300, poll_interval: int = 10) -> bool: ...
        """
        Wait for the aggregator to be ready and processing results.
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between checks in seconds
        
        Returns:
            bool: True if aggregator is ready, False if timeout
        """

