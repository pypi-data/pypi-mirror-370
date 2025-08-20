"""Auto-generated stub for module: kafka_consumer_worker."""
from typing import Any, Dict, Optional

from datetime import datetime, timezone
from matrice_inference.deploy.optimize.transmission import ServerTransmissionHandler
from matrice_inference.deploy.stream.kafka_stream import MatriceKafkaDeployment
import asyncio
import base64
import logging

# Classes
class KafkaConsumerWorker:
    """
    Kafka consumer worker that polls from topics and adds to input queue.
    """

    def __init__(self: Any, worker_id: str, session: Any, deployment_id: str, deployment_instance_id: str, input_queue: Any, consumer_group_suffix: str = '', poll_timeout: float = 1.0, max_messages_per_poll: int = 1, inference_pipeline_id: str = '') -> None: ...
        """
        Initialize Kafka consumer worker.
        
                Args:
                    worker_id: Unique identifier for this worker
                    session: Session object for authentication and RPC
                    deployment_id: ID of the deployment
                    deployment_instance_id: ID of the deployment instance
                    input_queue: Queue to put consumed messages into
                    consumer_group_suffix: Optional suffix for consumer group ID
                    poll_timeout: Timeout for Kafka polling
                    max_messages_per_poll: Maximum messages to consume in one poll
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
        Start the consumer worker.
        """

    async def stop(self: Any) -> None: ...
        """
        Stop the consumer worker.
        """

