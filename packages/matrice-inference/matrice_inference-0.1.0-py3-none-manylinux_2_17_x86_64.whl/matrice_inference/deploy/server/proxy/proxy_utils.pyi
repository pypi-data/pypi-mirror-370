"""Auto-generated stub for module: proxy_utils."""
from typing import Any, Dict, Set

from datetime import datetime
from queue import Queue
import logging
import numpy as np
import requests
import threading
import time

# Classes
class AuthKeyValidator:
    """
    Validates authentication keys for deployments.
    """

    def __init__(self: Any, deployment_id: str, session: Any) -> None: ...
        """
        Initialize the AuthKeyValidator.
        
                Args:
                    deployment_id: ID of the deployment
                    session: Session object containing RPC client
        """

    def start(self: Any) -> None: ...
        """
        Start the auth key update loop in a background thread.
        """

    def stop(self: Any) -> None: ...
        """
        Stop the auth key update loop.
        """

    def update_auth_keys(self: Any) -> None: ...
        """
        Fetch and validate auth keys for the deployment.
        """

    def update_auth_keys_loop(self: Any) -> None: ...
        """
        Run continuous loop to update auth keys.
        """

class RequestsLogger:
    """
    Logs prediction requests and handles drift monitoring.
    """

    def __init__(self: Any, deployment_id: str, session: Any) -> None: ...
        """
        Initialize the RequestsLogger.
        
                Args:
                    deployment_id: ID of the deployment
                    session: Session object containing RPC client
        """

    def add_log_to_queue(self: Any, prediction: Any, latency: float, request_time: str, input_data: Any, deployment_instance_id: str, auth_key: str) -> None: ...
        """
        Add prediction log to queue for async processing.
        
                Args:
                    prediction: The model prediction
                    latency: Request latency in seconds
                    request_time: Timestamp of the request
                    input_data: Raw input data bytes
                    deployment_instance_id: ID of deployment instance
                    auth_key: Authentication key used
        """

    def log_prediction_info(self: Any, prediction: Any, latency: float, request_time: str, input_data: Any, deployment_instance_id: str, auth_key: str) -> Dict: ...
        """
        Log prediction information to the server.
        
                Args:
                    prediction: The model prediction
                    latency: Request latency in seconds
                    request_time: Timestamp of the request
                    input_data: Raw input data bytes
                    deployment_instance_id: ID of deployment instance
                    auth_key: Authentication key used
        
                Returns:
                    Dict: Response from logging endpoint
        """

    def log_prediction_info_thread(self: Any) -> None: ...
        """
        Background thread for processing prediction logs.
        """

    def start(self: Any) -> None: ...
        """
        Start the prediction logging thread.
        """

    def stop(self: Any) -> None: ...
        """
        Stop the prediction logging thread.
        """

    def upload_input_for_drift_monitoring(self: Any, log_response: Dict, input_data: Any) -> None: ...
        """
        Upload input data for drift monitoring.
        
                Args:
                    log_response: Response from logging endpoint
                    input_data: Raw input data bytes
        """

