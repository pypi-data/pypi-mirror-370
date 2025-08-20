"""Auto-generated stub for module: streaming_gateway."""
from typing import Any, Dict, List, Optional

from matrice_inference.deploy.client.client import MatriceDeployClient
from matrice_inference.deploy.client.client_stream_utils import ClientStreamUtils
from matrice_inference.deploy.client.streaming_gateway.streaming_gateway_utils import InputConfig, OutputConfig, InputType, ModelInputType, _RealTimeJsonEventPicker
from matrice_inference.deploy.client.streaming_gateway.streaming_results_handler import StreamingResultsHandler
import json
import logging
import threading
import time

# Classes
class StreamingGateway:
    """
    Simplified streaming gateway that leverages MatriceDeployClient's capabilities.
    
        Supports both frame-based streaming (sending individual images) and video-based
        streaming (sending video chunks) based on the model_input_type configuration.
    
        Now includes optional post-processing capabilities for model results.
    
        Prevents multiple deployments or background streams from being started simultaneously
        using simple class-level tracking.
    
        Example usage:
            # Traditional usage with manual input config
            frame_input = create_camera_frame_input(camera_index=0, fps=30)
            video_input = create_camera_video_input(
                camera_index=0,
                fps=30,
                video_duration=5.0,  # 5-second chunks
                video_format="mp4"
            )
    
            gateway = StreamingGateway(
                session=session,
                service_id="your_service_id",
                inputs_config=[video_input],
                output_config=output_config
            )
    
            gateway.start_streaming()
    
            # To stop all streams from any instance:
            StreamingGateway.stop_all_active_streams()
    """

    def __init__(self: Any, session: Any, service_id: str = None, inputs_config: List[InputConfig] = None, output_config: Any = None, json_event_picker: Any = _RealTimeJsonEventPicker(), create_deployment_config: Dict = None, auth_key: str = None, consumer_group_id: str = None, result_callback: Optional[Callable] = None, strip_input_from_result: bool = True, force_restart: bool = False) -> None: ...
        """
        Initialize StreamingGateway.
        
                Args:
                    session: Session object for authentication
                    service_id: ID of existing deployment (optional if create_deployment_config provided)
                    inputs_config: Multiple input configurations (alternative to input_config)
                    output_config: Output configuration
                    create_deployment_config: Configuration for creating new deployment
                    auth_key: Authentication key for deployment
                    consumer_group_id: Kafka consumer group ID
                    result_callback: Optional callback function for processing results
                    strip_input_from_result: Whether to remove 'input' field from results to save space
                    force_restart: Whether to force stop existing streams and restart (use with caution)
        """

    def get_config(self: Any) -> Dict: ...
        """
        Get current configuration.
        
                Returns:
                    Dict with current configuration
        """

    def get_statistics(self: Any) -> Dict: ...
        """
        Get streaming statistics.
        
                Returns:
                    Dict with streaming statistics
        """

    def load_config(cls: Any, filepath: str, session: Any = None, auth_key: str = None) -> Any: ...
        """
        Load configuration from file and create StreamingGateway.
        
                Args:
                    filepath: Path to configuration file
                    session: Session object (required)
                    auth_key: Authentication key
        
                Returns:
                    StreamingGateway instance
        """

    def save_config(self: Any, filepath: str) -> Any: ...
        """
        Save current configuration to file.
        
                Args:
                    filepath: Path to save configuration
        """

    def start_streaming(self: Any, send_to_api: bool = False) -> bool: ...
        """
        Start streaming using MatriceDeployClient's built-in capabilities.
        
                Returns:
                    bool: True if streaming started successfully, False otherwise
        """

    def stop_all_active_streams(self: Any) -> Any: ...
        """
        Stop all active streams across all deployments.
        """

    def stop_streaming(self: Any) -> None: ...
        """
        Stop all streaming operations.
        """

