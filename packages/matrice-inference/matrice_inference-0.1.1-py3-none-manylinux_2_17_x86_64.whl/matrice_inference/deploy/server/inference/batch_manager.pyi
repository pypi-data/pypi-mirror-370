"""Auto-generated stub for module: batch_manager."""
from typing import Any, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass, field
from matrice_inference.deploy.utils.post_processing.core.config import BaseConfig
import asyncio
import logging
import time

# Classes
class BatchRequest:
    """
    Represents a single inference request in a batch
    """

    pass
class DynamicBatchManager:
    """
    Manages dynamic batching for inference requests
    """

    def __init__(self: Any, batch_size: int, max_batch_wait_time: float, model_manager: Any, post_processing_fn: Any) -> None: ...
        """
        Initialize the dynamic batch manager.
        
        Args:
            batch_size: Maximum batch size for processing
            max_batch_wait_time: Maximum wait time for batching
            model_manager: Model manager for inference
            post_processing_fn: Function to apply post-processing
        """

    async def add_request(self: Any, batch_request: Any) -> Tuple[Any, Optional[Dict[str, Any]]]: ...
        """
        Add a request to the batch queue and process if needed
        """

    async def flush_queue(self: Any) -> int: ...
        """
        Force process all remaining items in the batch queue.
        
                Returns:
                    Number of items processed
        """

    def get_stats(self: Any) -> Dict[str, Any]: ...
        """
        Get statistics about the current batching state.
        """

