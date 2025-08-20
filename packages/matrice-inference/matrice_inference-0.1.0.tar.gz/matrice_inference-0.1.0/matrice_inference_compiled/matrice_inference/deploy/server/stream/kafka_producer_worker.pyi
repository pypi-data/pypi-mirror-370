"""Auto-generated stub for module: kafka_producer_worker."""
from typing import Any, Dict, List, Optional

from datetime import datetime, timezone
from matrice_inference.deploy.stream.kafka_stream import MatriceKafkaDeployment
import asyncio
import logging

# Classes
class KafkaProducerWorker:
    """
    Kafka producer worker that consumes from output queue and produces to topics.
    """

    def __init__(self: Any, worker_id: str, session: Any, deployment_id: str, deployment_instance_id: str, output_queue: Any, app_name: str = '', app_version: str = '', produce_timeout: float = 10.0, inference_pipeline_id: str = '') -> None: ...
        """
        Initialize Kafka producer worker.
        
                Args:
                    worker_id: Unique identifier for this worker
                    session: Session object for authentication and RPC
                    deployment_id: ID of the deployment
                    deployment_instance_id: ID of the deployment instance
                    output_queue: Queue to get result messages from
                    app_name: Application name for result formatting
                    app_version: Application version for result formatting
                    produce_timeout: Timeout for producing to Kafka
                    inference_pipeline_id: ID of the inference pipeline
        """

    def get_metrics(self: Any) -> Dict[str, Any]: ...
        """
        Get worker metrics.
        """

    def reset_metrics(self: Any) -> None: ...
        """
        Reset worker metrics.
        """

    async def start(self: Any) -> None: ...
        """
        Start the producer worker.
        """

    async def stop(self: Any) -> None: ...
        """
        Stop the producer worker.
        """

