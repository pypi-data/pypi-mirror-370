"""Auto-generated stub for module: triton_utils."""
from typing import Any, Dict, Optional, Union

from PIL import Image
from datetime import datetime, timezone
from io import BytesIO
from matrice.docker_utils import pull_docker_image
from matrice_common.utils import dependencies_check
from matrice_common.utils import dependencies_check
import httpx
import logging
import logging
import numpy as np
import os
import shlex
import subprocess
import threading
import torch
import torch
import tritonclient.grpc as tritonclientclass
import tritonclient.http as tritonclientclass
import zipfile

# Constants
BASE_PATH: str
TRITON_DOCKER_IMAGE: str

# Classes
class MatriceTritonServer:
    def __init__(self: Any, action_tracker: Any) -> None: ...

    def check_triton_docker_image(self: Any) -> Any: ...
        """
        Check if docker image download is complete and wait for it to finish
        """

    def create_model_repository(self: Any) -> Any: ...
        """
        Create the model repository directory structure
        """

    def download_model(self: Any, model_version_dir: Any) -> Any: ...
        """
        Download and extract the model files
        """

    def get_config_params(self: Any) -> Any: ...

    def setup(self: Any) -> Any: ...

    def start_server(self: Any) -> Any: ...
        """
        Start the Triton Inference Server
        """

    def write_config_file(self: Any, model_dir: Any, max_batch_size: Any = 0, num_model_instances: Any = 1, image_size: Any = [224, 224], num_classes: Any = 10, input_data_type: str = 'TYPE_FP32', output_data_type: str = 'TYPE_FP32', dynamic_batching: bool = False, preferred_batch_size: list = [2, 4, 8], max_queue_delay_microseconds: int = 100, input_pinned_memory: bool = True, output_pinned_memory: bool = True, **kwargs: Any) -> Any: ...
        """
        Write the model configuration file for Triton Inference Server
        """

class TritonInference:
    """
    Class for making Triton inference requests.
    """

    def __init__(self: Any, server_type: str, model_id: str, internal_port: int = 80, internal_host: str = 'localhost') -> None: ...
        """
        Initialize Triton inference client.
        
                Args:
                    server_type: Type of server (grpc/rest)
                    model_id: ID of model to use
                    internal_port: Port number for internal API
                    internal_host: Hostname for internal API
        """

    async def async_inference(self: Any, input_data: Any) -> Any: ...
        """
        Make an asynchronous inference request.
        
                Args:
                    input_data: Input data as bytes
        
                Returns:
                    Model prediction as numpy array
        
                Raises:
                    Exception: If inference fails
        """

    def format_response(self: Any, response: Any) -> Dict[str, Any]: ...
        """
        Format model response for consistent logging.
        
                Args:
                    response: Raw model output
        
                Returns:
                    Formatted response dictionary
        """

    def inference(self: Any, input_data: Any) -> Any: ...
        """
        Make a synchronous inference request.
        
                Args:
                    input_data: Input data as bytes
        
                Returns:
                    Model prediction as numpy array
        
                Raises:
                    Exception: If inference fails
        """

