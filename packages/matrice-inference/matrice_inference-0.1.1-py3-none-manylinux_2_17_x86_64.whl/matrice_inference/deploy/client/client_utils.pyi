"""Auto-generated stub for module: client_utils."""
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
import json
import logging

# Classes
class ClientUtils:
    """
    Utility class for making inference requests to model servers.
    """

    def __init__(self: Any, clients: List[Dict] = None) -> None: ...
        """
        Initialize HTTP clients.
        """

    async def aclose(self: Any) -> None: ...
        """
        Asynchronously close HTTP clients and clean up resources.
        """

    async def async_inference(self: Any, auth_key: str = None, input_path: Optional[str] = None, input_bytes: Optional[bytes] = None, input_url: Optional[str] = None, extra_params: Optional[Dict] = None, apply_post_processing: bool = False, max_retries: int = 2) -> Union[Dict, str]: ...
        """
        Make an asynchronous inference request with retry logic.
        
                Args:
                    auth_key: Authentication key
                    input_path: Path to input file
                    input_bytes: Input as bytes
                    input_url: URL to fetch input from
                    extra_params: Additional parameters to pass to model
                    apply_post_processing: Whether to apply post-processing
                    max_retries: Maximum number of retry attempts per client
        
                Returns:
                    Model prediction result
        
                Raises:
                    ValueError: If no input is provided
                    httpx.HTTPError: If HTTP request fails
                    Exception: If inference request fails
        """

    def close(self: Any) -> None: ...
        """
        Close HTTP clients and clean up resources.
        """

    def inference(self: Any, auth_key: str = None, input_path: Optional[str] = None, input_bytes: Optional[bytes] = None, input_url: Optional[str] = None, extra_params: Optional[Dict] = None, apply_post_processing: bool = False, max_retries: int = 2) -> Union[Dict, str]: ...
        """
        Make a synchronous inference request with retry logic.
        
                Args:
                    auth_key: Authentication key
                    input_path: Path to input file
                    input_bytes: Input as bytes
                    input_url: URL to fetch input from
                    extra_params: Additional parameters to pass to model
                    apply_post_processing: Whether to apply post-processing
                    max_retries: Maximum number of retry attempts per client
        
                Returns:
                    Model prediction result
        
                Raises:
                    ValueError: If no input is provided
                    httpx.HTTPError: If HTTP request fails
                    Exception: If inference request fails
        """

    def refresh_instances_info(self: Any, instances_info: List[Dict]) -> None: ...
        """
        Update clients with new instances info.
        """

