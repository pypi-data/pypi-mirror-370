"""Auto-generated stub for module: stream_manager."""
from typing import Any, Dict, Optional

from matrice_inference.deploy.server.inference.inference_interface import InferenceInterface
from matrice_inference.deploy.server.stream.inference_worker import InferenceWorker
from matrice_inference.deploy.server.stream.kafka_consumer_worker import KafkaConsumerWorker
from matrice_inference.deploy.server.stream.kafka_producer_worker import KafkaProducerWorker
from matrice_inference.deploy.server.stream.stream_debug_logger import StreamDebugLogger
import asyncio
import logging
import uuid

# Classes
class StreamManager:
    """
    Stream manager with asyncio queues and integrated debug logging.
    """

    def __init__(self: Any, session: Any, deployment_id: str, deployment_instance_id: str, inference_interface: Any, num_consumers: int = 1, num_inference_workers: int = 1, num_producers: int = 1, app_name: str = '', app_version: str = '', inference_pipeline_id: str = '', debug_logging_enabled: bool = False, debug_log_interval: float = 30.0, input_queue_maxsize: int = 0, output_queue_maxsize: int = 0) -> None: ...
        """
        Initialize stream manager.
        
                Args:
                    session: Session object for authentication and RPC
                    deployment_id: ID of the deployment
                    deployment_instance_id: ID of the deployment instance
                    inference_interface: Inference interface to use for inference
                    num_consumers: Number of consumer workers
                    num_inference_workers: Number of inference workers
                    num_producers: Number of producer workers
                    app_name: Application name for result formatting
                    app_version: Application version for result formatting
                    inference_pipeline_id: ID of the inference pipeline
                    debug_logging_enabled: Whether to enable debug logging
                    debug_log_interval: Interval for debug logging in seconds
                    input_queue_maxsize: Maximum size for input queue (0 = unlimited)
                    output_queue_maxsize: Maximum size for output queue (0 = unlimited)
        """

    def disable_debug_logging(self: Any) -> Any: ...
        """
        Disable debug logging.
        """

    def enable_debug_logging(self: Any, log_interval: Optional[float] = None) -> Any: ...
        """
        Enable debug logging.
        """

    def get_debug_summary(self: Any) -> Dict[str, Any]: ...
        """
        Get debug logging summary.
        """

    def get_metrics(self: Any) -> Dict[str, Any]: ...
        """
        Get comprehensive metrics.
        """

    async def start(self: Any) -> None: ...
        """
        Start the stream manager and all workers.
        """

    async def stop(self: Any) -> None: ...
        """
        Stop the stream manager and all workers.
        """

