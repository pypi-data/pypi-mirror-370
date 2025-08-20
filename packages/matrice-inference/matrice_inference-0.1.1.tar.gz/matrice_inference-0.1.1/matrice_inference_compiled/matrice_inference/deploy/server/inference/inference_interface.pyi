"""Auto-generated stub for module: inference_interface."""
from typing import Any, Dict, List, Optional, Tuple, Union

from datetime import datetime, timezone
from matrice.action_tracker import ActionTracker
from matrice_inference.deploy.optimize.cache_manager import CacheManager
from matrice_inference.deploy.optimize.frame_comparators import SSIMComparator
from matrice_inference.deploy.optimize.frame_difference import IntelligentFrameCache
from matrice_inference.deploy.server.inference.batch_manager import DynamicBatchManager, BatchRequest
from matrice_inference.deploy.server.inference.model_manager import ModelManager
from matrice_inference.deploy.utils.post_processing import PostProcessor, create_config_from_template
from matrice_inference.deploy.utils.post_processing.config import get_usecase_from_app_name, get_category_from_app_name
from matrice_inference.deploy.utils.post_processing.core.config import BaseConfig
import base64
import cv2
import logging
import numpy as np

# Classes
class InferenceInterface:
    """
    Interface for proxying requests to model servers with optional post-processing.
    """

    def __init__(self: Any, action_tracker: Any, model_manager: Any, batch_size: int = 1, dynamic_batching: bool = False, post_processing_config: Optional[Union[Dict[str, Any], BaseConfig, str]] = None, custom_post_processing_fn: Optional[Callable] = None, max_batch_wait_time: float = 0.05, app_name: str = '') -> None: ...
        """
        Initialize the inference interface.
        
        Args:
            action_tracker: Action tracker for category mapping
            model_manager: Model manager for inference
            batch_size: Batch size for processing
            dynamic_batching: Whether to enable dynamic batching
            post_processing_config: Default post-processing configuration
                Can be a dict, BaseConfig object, or use case name string
            custom_post_processing_fn: Custom post-processing function
            max_batch_wait_time: Maximum wait time for batching
            app_name: Application name for automatic config loading
        """

    async def batch_inference(self: Any, batch_input1: List[Any], batch_input2: Optional[List[Any]] = None, batch_extra_params: Optional[List[Dict[str, Any]]] = None, apply_post_processing: bool = False, post_processing_configs: Optional[List[Union[Dict[str, Any], BaseConfig, str]]] = None, stream_key: Optional[str] = None, stream_info: Optional[Dict[str, Any]] = None, input_hash: Optional[str] = None, camera_info: Optional[Dict[str, Any]] = None) -> List[Tuple[Any, Optional[Dict[str, Any]]]]: ...
        """
        Perform batch inference directly without dynamic batching.
        
                Args:
                    batch_input1: List of primary input data
                    batch_input2: List of secondary input data (optional)
                    batch_extra_params: List of additional parameters for each inference (optional)
                    apply_post_processing: Whether to apply post-processing
                    post_processing_configs: List of post-processing configurations for each input
                    stream_key: Stream key for the inference
                    stream_info: Stream info for the inference (optional)
                Returns:
                    List of tuples containing (inference_result, post_processing_result) for each input.
        
                Raises:
                    ValueError: If input data is invalid
                    RuntimeError: If inference fails
        """

    def clear_post_processing_cache(self: Any) -> None: ...
        """
        Clear the post-processing cache in the underlying processor.
        """

    async def flush_batch_queue(self: Any) -> int: ...
        """
        Force process all remaining items in the batch queue.
        
                Returns:
                    Number of items processed
        """

    def get_batch_stats(self: Any) -> Dict[str, Any]: ...
        """
        Get statistics about the current batching state.
        """

    def get_latest_inference_time(self: Any) -> Any: ...
        """
        Get the latest inference time.
        """

    def get_post_processing_cache_stats(self: Any) -> Dict[str, Any]: ...
        """
        Get post-processing cache statistics from the underlying processor.
        
                Returns:
                    Dict[str, Any]: Cache statistics including cached instances and keys
        """

    async def inference(self: Any, input1: Any, input2: Any = None, extra_params: Any = None, apply_post_processing: bool = False, post_processing_config: Optional[Union[Dict[str, Any], BaseConfig, str]] = None, stream_key: Optional[str] = None, stream_info: Optional[Dict[str, Any]] = None, input_hash: Optional[str] = None, camera_info: Optional[Dict[str, Any]] = None) -> Tuple[Any, Optional[Dict[str, Any]]]: ...
        """
        Perform inference using the appropriate client with optional post-processing.
        
                Args:
                    input1: Primary input data
                    input2: Secondary input data (optional)
                    extra_params: Additional parameters for inference (optional)
                    apply_post_processing: Whether to apply post-processing
                    post_processing_config: Post-processing configuration (overrides default)
                    stream_key: Stream key for the inference
                    stream_info: Stream info for the inference (optional)
                    input_hash: Input hash for the inference
                Returns:
                    Tuple containing (inference_result, post_processing_result).
                    If post-processing is not applied, post_processing_result will be None.
                    If post-processing is applied, post_processing_result contains the full post-processing metadata.
        
                Raises:
                    ValueError: If client is not set up
                    RuntimeError: If inference fails
        """

