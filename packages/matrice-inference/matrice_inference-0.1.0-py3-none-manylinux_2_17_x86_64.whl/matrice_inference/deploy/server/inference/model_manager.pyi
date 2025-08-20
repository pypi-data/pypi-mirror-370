"""Auto-generated stub for module: model_manager."""
from typing import Any, Tuple

import gc
import logging
import torch

# Classes
class ModelManager:
    """
    Minimal ModelManager that focuses on model lifecycle and prediction calls.
    """

    def __init__(self: Any, model_id: str, internal_server_type: str, internal_port: int, internal_host: str, load_model: Any = None, predict: Any = None, batch_predict: Any = None, action_tracker: Any = None, num_model_instances: int = 1) -> None: ...
        """
        Initialize the ModelManager
        
                Args:
                    model_id: ID of the model
                    internal_server_type: Type of internal server
                    internal_port: Internal port number
                    internal_host: Internal host address
                    load_model: Function to load the model
                    predict: Function to run predictions
                    batch_predict: Function to run batch predictions
                    action_tracker: Tracker for monitoring actions
                    num_model_instances: Number of model instances to create
        """

    def batch_inference(self: Any, input1: Any, input2: Any = None, extra_params: Any = None, stream_key: Any = None, stream_info: Any = None, input_hash: Any = None) -> Tuple[dict, bool]: ...
        """
        Run batch inference on the provided input data.
        
                Args:
                    input1: Primary input data
                    input2: Secondary input data (optional)
                    extra_params: Additional parameters for inference (optional)
                    stream_key: Stream key for the inference
                    stream_info: Stream info for the inference
                    input_hash: Input hash for the inference
                Returns:
                    Tuple of (results, success_flag)
        
                Raises:
                    ValueError: If input data is invalid
        """

    def get_model(self: Any) -> Any: ...
        """
        Get the model instance in round-robin fashion
        """

    def inference(self: Any, input1: Any, input2: Any = None, extra_params: Any = None, stream_key: Any = None, stream_info: Any = None, input_hash: Any = None) -> Tuple[dict, bool]: ...
        """
        Run inference on the provided input data.
        
                Args:
                    input1: Primary input data (can be image bytes or numpy array)
                    input2: Secondary input data (optional)
                    extra_params: Additional parameters for inference (optional)
                    stream_key: Stream key for the inference
                    stream_info: Stream info for the inference
                    input_hash: Input hash for the inference
                Returns:
                    Tuple of (results, success_flag)
        
                Raises:
                    ValueError: If input data is invalid
        """

    def scale_down(self: Any) -> Any: ...
        """
        Unload the model from memory (scale down)
        """

    def scale_up(self: Any) -> Any: ...
        """
        Load the model into memory (scale up)
        """

