"""Auto-generated stub for module: client."""
from typing import Any, Dict, Optional, Union

from matrice.projects import Projects
from matrice_inference.deploy.client.client_stream_utils import ClientStreamUtils
from matrice_inference.deploy.client.client_utils import ClientUtils
import logging
import time

# Classes
class MatriceDeployClient:
    """
    Client for interacting with Matrice model deployments.
    
        This client provides both synchronous and asynchronous methods for making
        predictions and streaming video data to deployed models.
    
        Example:
            Basic usage:
            ```python
            from matrice import Session
            from matrice_inference.deploy.client import MatriceDeployClient
    
            session = Session(account_number="...", access_key="...", secret_key="...")
            client = MatriceDeployClient(
                session=session,
                deployment_id="your_deployment_id",
                auth_key="your_auth_key"
            )
    
            # Check if client is healthy
            if client.is_healthy():
                # Make a prediction
                result = client.get_prediction(input_path="image.jpg")
                print(result)
    
            # Clean up resources
            client.close()
            ```
    
        Streaming example:
            ```python
            # Start streaming frames from webcam
            success = client.start_stream(input=0, fps=30, quality=80)
            if success:
                # Consume results
                while True:
                    result = client.consume_result(timeout=10.0)
                    if result:
                        print(f"Received result: {result}")
                    else:
                        break
    
            # Stop streaming
            client.stop_streaming()
            ```
    
        Video streaming example:
            ```python
            # Start streaming video chunks from webcam (5 second chunks)
            success = client.start_video_stream(
                input=0,
                fps=30,
                video_duration=5.0,  # 5 second chunks
                video_format="mp4"
            )
    
            # Or stream video with frame count limit (150 frames per chunk)
            success = client.start_video_stream(
                input=0,
                fps=30,
                max_frames=150,  # 150 frames per chunk
                video_format="mp4"
            )
    
            if success:
                # Consume video results
                while True:
                    result = client.consume_result(timeout=30.0)
                    if result:
                        print(f"Received video result: {result}")
                    else:
                        break
    
            # Stop streaming
            client.stop_streaming()
            ```
    """

    def __init__(self: Any, session: Any, deployment_id: str, auth_key: str = None, create_deployment_config: Dict = None, consumer_group_id: str = None, consumer_group_instance_id: str = None) -> None: ...
        """
        Initialize MatriceDeployClient.
        
                Args:
                    session: Session object for making RPC calls
                    deployment_id: ID of the deployment
                    auth_key: Authentication key
                    create_deployment_config: Deployment configuration
                    consumer_group_id: Kafka consumer group ID
                    consumer_group_instance_id: Unique consumer group instance ID to prevent rebalancing
        
                Raises:
                    ValueError: If required parameters are missing or invalid
                    RuntimeError: If deployment info cannot be retrieved
        """

    async def aclose(self: Any) -> None: ...
        """
        Close all client connections asynchronously and clean up resources.
        
                This method should be called when you're done using the client
                to properly clean up HTTP connections and other resources.
        """

    def close(self: Any) -> None: ...
        """
        Close all client connections and clean up resources.
        
                This method should be called when you're done using the client
                to properly clean up HTTP connections and other resources.
        """

    async def close_stream(self: Any) -> None: ...
        """
        Close streaming connections asynchronously.
        """

    def consume_result(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Consume a result from the streaming session.
        
                Args:
                    timeout: Maximum time to wait for a result in seconds
        
                Returns:
                    Result dictionary if available, None if timeout
        """

    async def consume_result_async(self: Any, timeout: float = 60.0) -> Optional[Dict]: ...
        """
        Consume a result from the streaming session asynchronously.
        
                Args:
                    timeout: Maximum time to wait for a result in seconds
        
                Returns:
                    Result dictionary if available, None if timeout
        """

    def create_auth_key_if_not_exists(self: Any, expiry_days: int = 30) -> str: ...
        """
        Create an authentication key if one doesn't exist.
        
                Args:
                    expiry_days: Number of days until the key expires
        
                Returns:
                    str: The created authentication key
        
                Raises:
                    ValueError: If expiry_days is invalid
                    RuntimeError: If key creation fails
        """

    def create_deployment(self: Any, deployment_name: Any, model_id: Any = '', gpu_required: Any = True, auto_scale: Any = False, auto_shutdown: Any = True, shutdown_threshold: Any = 5, compute_alias: Any = '', model_type: Any = 'trained', deployment_type: Any = 'regular', checkpoint_type: Any = 'pretrained', checkpoint_value: Any = '', checkpoint_dataset: Any = 'COCO', runtime_framework: Any = 'Pytorch', server_type: Any = 'fastapi', deployment_params: Any = {}, model_input: Any = 'image', model_output: Any = 'classification', suggested_classes: Any = [], model_family: Any = '', model_key: Any = '', is_kafka_enabled: Any = False, is_optimized: Any = False, instance_range: Any = [1, 1], custom_schedule: Any = False, schedule_deployment: Any = [], post_processing_config: Any = None, create_deployment_config: Dict = {}, wait_for_deployment: bool = True, max_wait_time: int = 1200) -> Any: ...

    def get_deployment_info(self: Any) -> Dict: ...
        """
        Get deployment information.
        
                Returns:
                    Dict containing deployment information
        
                Raises:
                    RuntimeError: If deployment info cannot be retrieved
        """

    def get_index_to_category(self: Any) -> Dict: ...
        """
        Get index to category mapping.
        
                Returns:
                    Dict mapping indices to category names
        
                Raises:
                    RuntimeError: If category mapping cannot be retrieved
        """

    def get_prediction(self: Any, input_path: Optional[str] = None, input_bytes: Optional[bytes] = None, input_url: Optional[str] = None, extra_params: Optional[Dict] = None, auth_key: Optional[str] = None, apply_post_processing: bool = False) -> Union[Dict, str]: ...
        """
        Get prediction from the deployed model.
        
                Args:
                    input_path: Path to input file
                    input_bytes: Input data as bytes
                    input_url: URL to input data
                    extra_params: Additional parameters for the prediction
                    auth_key: Authentication key (uses instance auth_key if not provided)
                    apply_post_processing: Whether to apply post-processing
        
                Returns:
                    Prediction result from the model
        
                Raises:
                    ValueError: If no input is provided or auth key is missing
                    Exception: If prediction request fails
        """

    async def get_prediction_async(self: Any, input_path: Optional[str] = None, input_bytes: Optional[bytes] = None, input_url: Optional[str] = None, extra_params: Optional[Dict] = None, auth_key: Optional[str] = None, apply_post_processing: bool = False) -> Union[Dict, str]: ...
        """
        Get prediction from the deployed model asynchronously.
        
                Args:
                    input_path: Path to input file
                    input_bytes: Input data as bytes
                    input_url: URL to input data
                    extra_params: Additional parameters for the prediction
                    auth_key: Authentication key (uses instance auth_key if not provided)
                    apply_post_processing: Whether to apply post-processing
        
                Returns:
                    Prediction result from the model
        
                Raises:
                    ValueError: If no input is provided or auth key is missing
                    Exception: If prediction request fails
        """

    def get_status(self: Any) -> Dict: ...
        """
        Get comprehensive status information about the client and deployment.
        
                Returns:
                    Dict containing status information
        """

    def is_healthy(self: Any) -> bool: ...
        """
        Check if the deployment is healthy and ready to serve requests.
        
                Returns:
                    bool: True if deployment is healthy, False otherwise
        """

    def refresh_instances_info(self: Any, force: bool = False) -> Any: ...
        """
        Refresh instances information from the deployment.
        
                Args:
                    force: Whether to force refresh regardless of time elapsed
        """

    def start_background_stream(self: Any, input: Union[str, int], fps: int = 10, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, quality: int = 95, width: Optional[int] = None, height: Optional[int] = None, simulate_video_file_stream: bool = False, is_video_chunk: bool = False, chunk_duration_seconds: Optional[float] = None, chunk_frames: Optional[int] = None) -> bool: ...
        """
        Start a background streaming session.
        
                Args:
                    input: Video source (camera index, file path, or URL)
                    fps: Frames per second to stream
                    stream_key: Unique identifier for the stream
                    quality: JPEG compression quality (1-100)
                    width: Target frame width
                    height: Target frame height
        
                Returns:
                    bool: True if streaming started successfully, False otherwise
        """

    def start_background_video_stream(self: Any, input: Union[str, int], fps: int = 10, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, quality: int = 95, width: Optional[int] = None, height: Optional[int] = None, video_duration: Optional[float] = None, max_frames: Optional[int] = None, video_format: str = 'mp4') -> bool: ...
        """
        Start a background video streaming session that sends video chunks.
        
                Args:
                    input: Video source (camera index, file path, or URL)
                    fps: Frames per second to capture and encode
                    stream_key: Unique identifier for the stream
                    quality: Video compression quality (1-100)
                    width: Target frame width
                    height: Target frame height
                    video_duration: Duration of each video chunk in seconds (optional)
                    max_frames: Maximum number of frames per video chunk (optional)
                    video_format: Video format for encoding ('mp4', 'avi', 'webm')
        
                Returns:
                    bool: True if streaming started successfully, False otherwise
        
                Note:
                    Either video_duration or max_frames should be specified to control chunk size.
                    If neither is provided, defaults to 5 second chunks.
        """

    def start_stream(self: Any, input: Union[str, int], fps: int = 10, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, quality: int = 95, width: Optional[int] = None, height: Optional[int] = None, simulate_video_file_stream: bool = False, is_video_chunk: bool = False, chunk_duration_seconds: Optional[float] = None, chunk_frames: Optional[int] = None) -> bool: ...
        """
        Start a streaming session (blocking).
        
                Args:
                    input: Video source (camera index, file path, or URL)
                    fps: Frames per second to stream
                    stream_key: Unique identifier for the stream
                    quality: JPEG compression quality (1-100)
                    width: Target frame width
                    height: Target frame height
        
                Returns:
                    bool: True if streaming started successfully, False otherwise
        """

    def start_video_stream(self: Any, input: Union[str, int], fps: int = 10, stream_key: Optional[str] = None, stream_group_key: Optional[str] = None, quality: int = 95, width: Optional[int] = None, height: Optional[int] = None, video_duration: Optional[float] = None, max_frames: Optional[int] = None, video_format: str = 'mp4') -> bool: ...
        """
        Start a video streaming session (blocking) that sends video chunks.
        
                Args:
                    input: Video source (camera index, file path, or URL)
                    fps: Frames per second to capture and encode
                    stream_key: Unique identifier for the stream
                    quality: Video compression quality (1-100)
                    width: Target frame width
                    height: Target frame height
                    video_duration: Duration of each video chunk in seconds (optional)
                    max_frames: Maximum number of frames per video chunk (optional)
                    video_format: Video format for encoding ('mp4', 'avi', 'webm')
        
                Returns:
                    bool: True if streaming started successfully, False otherwise
        
                Note:
                    Either video_duration or max_frames should be specified to control chunk size.
                    If neither is provided, defaults to 5 second chunks.
        """

    def stop_streaming(self: Any) -> None: ...
        """
        Stop all streaming sessions.
        """

    def wait_for_deployment(self: Any, timeout: Any = 1200) -> Any: ...

