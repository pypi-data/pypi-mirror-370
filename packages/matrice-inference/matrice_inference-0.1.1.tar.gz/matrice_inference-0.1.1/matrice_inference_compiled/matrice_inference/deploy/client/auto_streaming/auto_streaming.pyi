"""Auto-generated stub for module: auto_streaming."""
from typing import Any, Dict, List, Optional

from auto_streaming_utils import AutoStreamingUtils
from matrice_inference.deploy.client.streaming_gateway import StreamingGateway, ModelInputType, OutputConfig, InputConfig
from matrice_inference.deployment.camera_manager import CameraManager
from matrice_inference.deployment.streaming_gateway_manager import StreamingGateway
from matrice_inference.deployment.streaming_gateway_manager import StreamingGatewayManager
import logging
import threading
import time

# Classes
class AutoStreaming:
    """
    Handles automatic streaming setup and management using streaming gateway configurations.
    
    This class manages multiple streaming gateways, automatically configures cameras
    based on the gateway's camera group assignments, and handles the streaming lifecycle.
    
    Example usage:
        # Method 1: From service IDs (auto-discovers all gateways)
        auto_streaming = AutoStreaming(
            session=session,
            service_ids=["service_id_123", "service_id_456"],
            model_input_type=ModelInputType.FRAMES
        )
    
        # Method 2: From specific gateway IDs
        auto_streaming = AutoStreaming(
            session=session,
            streaming_gateway_ids=["gateway1", "gateway2"],
            model_input_type=ModelInputType.FRAMES
        )
    
        # Start auto streaming
        success = auto_streaming.start()
    
        # Stop auto streaming
        auto_streaming.stop()
    
        # Get statistics
        stats = auto_streaming.get_statistics()
    """

    def __init__(self: Any, session: Any, service_ids: List[str] = None, streaming_gateway_ids: List[str] = None, model_input_type: Any = ModelInputType.FRAMES, output_configs: Optional[Dict[str, OutputConfig]] = None, result_callback: Optional[Callable] = None, strip_input_from_result: bool = True, default_fps: int = 30, default_quality: int = 80, default_video_chunk_duration: int = 10, default_video_format: str = 'mp4', simulate_video_file_stream: bool = False) -> None: ...
        """
        Initialize AutoStreaming with service IDs or streaming gateway IDs.
        
        Args:
            session: Session object for authentication
            service_ids: List of Service IDs (deployment or inference pipeline ID) - will auto-discover gateways
            streaming_gateway_ids: List of specific streaming gateway IDs to use
            model_input_type: Model input type (FRAMES or VIDEO)
            output_configs: Optional output configurations per streaming gateway
            result_callback: Optional callback for processing results
            strip_input_from_result: Whether to strip input from results
            default_fps: Default FPS for camera streams
            default_quality: Default quality for camera streams
            default_video_chunk_duration: Default video chunk duration for video input type
            default_video_format: Default video format for video input type
            simulate_video_file_stream: Whether to restream videos
        Note:
            Either service_ids OR streaming_gateway_ids must be provided, not both.
            If service_ids is provided, all gateways for those services will be auto-discovered.
        """

    def add_streaming_gateway(self: Any, gateway_id: str) -> bool: ...
        """
        Add a new streaming gateway to auto streaming.
        
        Args:
            gateway_id: ID of the streaming gateway to add
        
        Returns:
            bool: True if gateway was added successfully
        """

    def get_gateway_status(self: Any, gateway_id: str) -> Optional[Dict]: ...
        """
        Get status for a specific streaming gateway.
        
        Args:
            gateway_id: Streaming gateway ID
        
        Returns:
            Dict with gateway status or None if not found
        """

    def get_statistics(self: Any) -> Dict: ...
        """
        Get auto streaming statistics.
        
        Returns:
            Dict with comprehensive statistics
        """

    def refresh_camera_configs(self: Any) -> bool: ...
        """
        Refresh camera configurations for all streaming gateways.
        
        Returns:
            bool: True if configurations were refreshed successfully
        """

    def remove_streaming_gateway(self: Any, gateway_id: str) -> bool: ...
        """
        Remove a streaming gateway from auto streaming.
        
        Args:
            gateway_id: ID of the streaming gateway to remove
        
        Returns:
            bool: True if gateway was removed successfully
        """

    def setup_streaming_gateways(self: Any, gateway_input_configs: Dict[str, List[InputConfig]] = None) -> Dict[str, StreamingGateway]: ...
        """
        Setup StreamingGateway instances for each streaming gateway ID.
        
        Returns:
            bool: True if all gateways were setup successfully, False otherwise
        """

    def setup_streaming_gateways_input_configs(self: Any) -> Optional[Dict[str, List[InputConfig]]]: ...
        """
        Setup input configurations for each streaming gateway ID.
        
        Returns:
            bool: True if all gateway input configs were setup successfully, False otherwise
        """

    def start(self: Any, send_to_api: bool = False) -> bool: ...
        """
        Start auto streaming for all configured streaming gateways.
        
        Returns:
            bool: True if streaming started successfully, False otherwise
        """

    def stop(self: Any) -> Any: ...
        """
        Stop auto streaming for all gateways.
        """

