"""Auto-generated stub for module: inference_worker."""
from typing import Any, Dict, List, Optional

from datetime import datetime, timezone
from matrice_inference.deploy.optimize.cache_manager import CacheManager
from matrice_inference.deploy.optimize.frame_comparators import SSIMComparator
from matrice_inference.deploy.optimize.transmission import ServerTransmissionHandler
from matrice_inference.deploy.server.inference.inference_interface import InferenceInterface
from matrice_inference.deploy.server.stream.video_buffer import VideoBufferManager
import asyncio
import base64
import cv2
import logging
import numpy as np

# Classes
class InferenceWorker:
    """
    Inference worker that processes messages from input queue and adds results to output queue.
    """

    def __init__(self: Any, worker_id: str, inference_interface: Any, input_queue: Any, output_queue: Any, process_timeout: float = 30.0, enable_video_buffering: bool = True, ssim_threshold: float = 0.95, cache_size: int = 100) -> None: ...
        """
        Initialize inference worker.
        
                Args:
                    worker_id: Unique identifier for this worker
                    inference_interface: Inference interface to use for inference
                    input_queue: Queue to get messages from
                    output_queue: Queue to put results into
                    process_timeout: Timeout for inference processing
                    enable_video_buffering: Whether to enable video buffering
                    ssim_threshold: SSIM threshold for frame similarity (default: 0.95)
                    cache_size: Maximum number of cached results per stream
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
        Start the inference worker.
        """

    async def stop(self: Any) -> None: ...
        """
        Stop the inference worker.
        """

