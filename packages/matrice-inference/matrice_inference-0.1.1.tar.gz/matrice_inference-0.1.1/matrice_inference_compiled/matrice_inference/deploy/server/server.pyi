"""Auto-generated stub for module: server."""
from typing import Any, Optional

from datetime import datetime, timezone
from matrice.action_tracker import ActionTracker
from matrice_inference.deploy.server.inference.inference_interface import InferenceInterface
from matrice_inference.deploy.server.inference.model_manager import ModelManager
from matrice_inference.deploy.server.proxy.proxy_interface import MatriceProxyInterface
from matrice_inference.deploy.server.stream.stream_manager import StreamManager
import asyncio
import atexit
import logging
import os
import signal
import threading
import time
import urllib.request

# Constants
CLEANUP_DELAY_SECONDS: int
DEFAULT_EXTERNAL_PORT: int
DEFAULT_SHUTDOWN_THRESHOLD_MINUTES: int
FINAL_CLEANUP_DELAY_SECONDS: int
HEARTBEAT_INTERVAL_SECONDS: int
IP_FETCH_TIMEOUT_SECONDS: int
MAX_DEPLOYMENT_CHECK_FAILURES_BEFORE_SHUTDOWN: int
MAX_HEARTBEAT_FAILURES_BEFORE_SHUTDOWN: int
MAX_IP_FETCH_ATTEMPTS: int
MIN_SHUTDOWN_THRESHOLD_MINUTES: int
SHUTDOWN_CHECK_INTERVAL_SECONDS: int

# Classes
class MatriceDeployServer:
    """
    Class for managing model deployment and server functionality.
    """

    def __init__(self: Any, load_model: Optional[Callable] = None, predict: Optional[Callable] = None, action_id: str = '', external_port: int = DEFAULT_EXTERNAL_PORT, batch_predict: Optional[Callable] = None, custom_post_processing_fn: Optional[Callable] = None) -> None: ...
        """
        Initialize MatriceDeploy.
        
                Args:
                    load_model (callable, optional): Function to load model. Defaults to None.
                    predict (callable, optional): Function to make predictions. Defaults to None.
                    batch_predict (callable, optional): Function to make batch predictions. Defaults to None.
                    custom_post_processing_fn (callable, optional): Function to get custom post processing config. Defaults to None.
                    action_id (str, optional): ID for action tracking. Defaults to "".
                    external_port (int, optional): External port number. Defaults to 80.
        
                Raises:
                    ValueError: If required parameters are invalid
                    Exception: If initialization fails
        """

    def start(self: Any, block: Any = True) -> Any: ...
        """
        Start the proxy interface and all server components.
        """

    def start_server(self: Any, block: Any = True) -> Any: ...
        """
        Start the server and related components.
        
                Args:
                    block: If True, wait for shutdown signal. If False, return immediately after starting.
        
                Raises:
                    Exception: If unable to initialize server
        """

    def stop_server(self: Any) -> Any: ...
        """
        Stop the server and related components.
        """

class MatriceDeployServerUtils:
    """
    Utility class for managing deployment server operations.
    """

    def __init__(self: Any, action_tracker: Any, inference_interface: Any, external_port: int, main_server: Any = None) -> None: ...
        """
        Initialize utils with reference to the main server.
        
                Args:
                    action_tracker: ActionTracker instance
                    inference_interface: InferenceInterface instance
                    external_port: External port number
                    main_server: Reference to the main MatriceDeployServer instance
        """

    def get_elapsed_time_since_latest_inference(self: Any) -> Any: ...
        """
        Get time elapsed since latest inference.
        
                Returns:
                    float: Elapsed time in seconds
        
                Raises:
                    Exception: If unable to get elapsed time and no fallback available
        """

    def heartbeat_checker(self: Any) -> Any: ...
        """
        Background thread to periodically send heartbeat.
        """

    def ip(self: Any) -> Any: ...
        """
        Get the external IP address with caching and retry logic.
        """

    def is_instance_running(self: Any) -> Any: ...
        """
        Check if deployment instance is running.
        
                Returns:
                    bool: True if instance is running, False otherwise
        """

    def run_background_checkers(self: Any) -> Any: ...
        """
        Start the shutdown checker and heartbeat checker threads as daemons.
        """

    def shutdown(self: Any) -> Any: ...
        """
        Gracefully shutdown the deployment instance.
        """

    def shutdown_checker(self: Any) -> Any: ...
        """
        Background thread to periodically check for idle shutdown condition and deployment status.
        """

    def trigger_shutdown_if_needed(self: Any) -> Any: ...
        """
        Check idle time and trigger shutdown if threshold exceeded.
        """

    def update_deployment_address(self: Any) -> Any: ...
        """
        Update the deployment address in the backend.
        
                Raises:
                    Exception: If unable to update deployment address
        """

    def wait_for_shutdown(self: Any) -> Any: ...
        """
        Wait for shutdown to be initiated by background checkers or external signals.
        
                This method blocks the main thread until shutdown is triggered.
        """

