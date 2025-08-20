"""Auto-generated stub for module: proxy_interface."""
from typing import Any, Optional

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.params import File, Form
from fastapi.responses import JSONResponse
from matrice_inference.deploy.server.inference.inference_interface import InferenceInterface
from matrice_inference.deploy.server.proxy.proxy_utils import AuthKeyValidator, RequestsLogger
import asyncio
import httpx
import logging
import threading
import time
import uvicorn

# Classes
class MatriceProxyInterface:
    """
    Interface for proxying requests to model servers.
    """

    def __init__(self: Any, session: Any, deployment_id: str, deployment_instance_id: str, external_port: int, inference_interface: Any) -> None: ...
        """
        Initialize proxy server.
        
                Args:
                    session: Session object for authentication and RPC
                    deployment_id: ID of the deployment
                    external_port: Port to expose externally
        """

    async def inference(self: Any, input1: Any, input2: Any = None, extra_params: Any = None, apply_post_processing: Any = False) -> Any: ...
        """
        Perform inference using the inference interface.
        
                Args:
                    input1: Primary input data
                    input2: Secondary input data (optional)
                    extra_params: Additional parameters for inference (optional)
                    apply_post_processing: Flag to apply post-processing
        
                Returns:
                    Inference result, Post-processing result
        """

    def log_prediction_info(self: Any, result: Any, start_time: Any, input1: Any, auth_key: Any) -> Any: ...
        """
        Log prediction info.
        
                Args:
                    result: Prediction result
                    start_time: Start time of the request
                    input1: Input data
                    auth    _key: Authentication key used
        """

    def on_start(self: Any) -> Any: ...
        """
        Start the proxy server components.
        """

    async def on_stop(self: Any) -> Any: ...
        """
        Clean up proxy server components.
        """

    def start(self: Any) -> Any: ...
        """
        Start the proxy server in a background thread.
        """

    def stop(self: Any) -> Any: ...
        """
        Stop the proxy server gracefully.
        """

    def validate_auth_key(self: Any, auth_key: Any) -> Any: ...
        """
        Validate auth key.
        
                Args:
                    auth_key: Authentication key to validate
        
                Returns:
                    bool: True if valid, False otherwise
        """

