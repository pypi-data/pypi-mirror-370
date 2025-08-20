"""Auto-generated stub for module: auto_streaming_utils."""
from typing import Any, Dict, List, Optional, Tuple

from matrice_inference.deploy.client.streaming_gateway import ModelInputType, InputConfig, InputType
from matrice_inference.deployment.camera_manager import Camera, CameraGroup, CameraManager
from matrice_inference.deployment.streaming_gateway_manager import StreamingGateway
import logging
import time

# Classes
class AutoStreamingUtils:
    """
    Utility class for auto streaming camera configuration and input conversion.
    
    This class provides methods for converting camera configurations to input configurations,
    managing streaming statistics, and validating gateway configurations.
    """

    def __init__(self: Any, default_fps: int = 30, default_quality: int = 80, default_video_chunk_duration: int = 10, default_video_format: str = 'mp4', simulate_video_file_stream: bool = False) -> None: ...
        """
        Initialize AutoStreamingUtils with default configuration values.
        
        Args:
            default_fps: Default FPS for camera streams
            default_quality: Default quality for camera streams
            default_video_chunk_duration: Default video chunk duration for video input type
            default_video_format: Default video format for video input type
            simulate_video_file_stream: Whether to simulate video file stream
        """

    def calculate_runtime_stats(stats: Dict) -> Dict: ...
        """
        Calculate runtime statistics.
        
        Args:
            stats: Statistics dictionary
        
        Returns:
            Updated statistics dictionary with runtime information
        """

    def convert_camera_configs_to_inputs(self: Any, camera_configs: List[Camera], camera_groups: Dict[str, CameraGroup], deployment_id: str, model_input_type: Any = ModelInputType.FRAMES) -> List[InputConfig]: ...
        """
        Convert camera configurations to input configurations for streaming.
        
        Args:
            camera_configs: List of Camera instance objects
            camera_groups: Dictionary mapping group IDs to CameraGroupInstance objects
            deployment_id: Deployment ID for logging
            model_input_type: Model input type (FRAMES or VIDEO)
        
        Returns:
            List of InputConfig objects
        """

    def create_auto_streaming_stats(streaming_gateway_ids: List[str]) -> Dict: ...
        """
        Create initial statistics dictionary for auto streaming.
        
        Args:
            streaming_gateway_ids: List of streaming gateway IDs
        
        Returns:
            Dictionary with initial statistics
        """

    def get_camera_configs_as_inputs(self: Any, camera_manager: Any, deployment_id: str, model_input_type: Any = ModelInputType.FRAMES) -> Tuple[Optional[List[InputConfig]], Optional[str], str]: ...
        """
        Get camera configurations for a deployment and convert them to input configurations.
        
        This method fetches both camera groups and camera configs, then converts them
        to input configs using effective stream settings.
        
        Args:
            camera_manager: CameraManager instance
            deployment_id: The ID of the deployment to get camera configs for
            model_input_type: Model input type (FRAMES or VIDEO)
        
        Returns:
            tuple: (input_configs, error, message)
        """

    def get_gateway_cameras_as_inputs(self: Any, camera_manager: Any, streaming_gateway_config_instance: Any, model_input_type: Any = ModelInputType.FRAMES) -> Tuple[Optional[List[InputConfig]], Optional[str], str]: ...
        """
        Get camera configurations for a specific streaming gateway and convert to input configs.
        
        Args:
            camera_manager: CameraManager instance to use for camera operations
            streaming_gateway_config_instance: StreamingGateway instance to use for gateway operations
            model_input_type: Model input type (FRAMES or VIDEO)
        
        Returns:
            tuple: (input_configs, error, message)
        """

    def record_error(stats: Dict, error_message: str) -> Any: ...
        """
        Record an error in statistics.
        
        Args:
            stats: Statistics dictionary
            error_message: Error message to record
        """

    def update_stream_status(stats: Dict, gateway_id: str, status: str, camera_count: int = None) -> Any: ...
        """
        Update the status of a streaming gateway in statistics.
        
        Args:
            stats: Statistics dictionary
            gateway_id: ID of the streaming gateway
            status: New status (starting, running, stopped, failed)
            camera_count: Number of cameras (optional)
        """

    def validate_streaming_gateway_config(gateway_config: Any) -> Tuple[bool, str]: ...
        """
        Validate streaming gateway configuration.
        
        Args:
            gateway_config:  object
        
        Returns:
            tuple: (is_valid, error_message)
        """

