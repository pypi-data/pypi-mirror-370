"""Auto-generated stub for module: streaming_gateway_utils."""
from typing import Any, Dict, List, Optional, Tuple, Union

from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum
from matrice_inference.deploy.utils.post_processing.core.config import BaseConfig, AlertConfig, TrackingConfig, ZoneConfig
from urllib.parse import urlparse
import json
import os
import os
import re
import requests
import time
import urllib3
import uuid
import warnings

# Functions
def create_camera_frame_input(camera_index: int = 0, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None) -> Any: ...
    """
    Create a camera input for frame-based streaming.
    
        Args:
            camera_index: Camera device index
            fps: Frames per second
            quality: Image quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
    
        Returns:
            InputConfig: Camera input configured for frame streaming
    """
def create_camera_input(camera_index: int = 0, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, model_input_type: Any = ModelInputType.FRAMES, video_duration: float = None, max_frames: int = None, video_format: str = 'mp4') -> Any: ...
    """
    Create a camera input configuration.
    
        Args:
            camera_index: Camera device index (0 for default camera)
            fps: Frames per second to capture
            quality: Video/image quality (1-100)
            stream_key: Unique identifier for the stream
            width: Frame width in pixels
            height: Frame height in pixels
            model_input_type: FRAMES for individual images, VIDEO for video chunks
            video_duration: Duration of video chunks in seconds (only for VIDEO mode)
            max_frames: Maximum frames per video chunk (only for VIDEO mode)
            video_format: Video format for encoding (mp4, avi, webm)
    
        Returns:
            InputConfig: Configured input for camera
    
        Raises:
            ValueError: If parameters are invalid
    """
def create_camera_video_input(camera_index: int = 0, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, video_duration: float = 5.0, video_format: str = 'mp4') -> Any: ...
    """
    Create a camera input for video-based streaming with duration limit.
    
        Args:
            camera_index: Camera device index
            fps: Frames per second
            quality: Video quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
            video_duration: Duration of video chunks in seconds
            video_format: Video format (mp4, avi, webm)
    
        Returns:
            InputConfig: Camera input configured for video streaming
    """
def create_camera_video_input_by_frames(camera_index: int = 0, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, max_frames: int = 150, video_format: str = 'mp4') -> Any: ...
    """
    Create a camera input for video-based streaming with frame count limit.
    
        Args:
            camera_index: Camera device index
            fps: Frames per second
            quality: Video quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
            max_frames: Maximum frames per video chunk
            video_format: Video format (mp4, avi, webm)
    
        Returns:
            InputConfig: Camera input configured for video streaming
    """
def create_detection_post_processing_config(confidence_threshold: float = 0.6, enable_counting: bool = True, enable_alerting: bool = True, map_index_to_category: bool = False, index_to_category: Dict[int, str] = None, category_triggers: List[str] = None, count_threshold: int = None) -> Any: ...
    """
    Create a post-processing configuration optimized for object detection.
    
        Args:
            confidence_threshold: Global confidence threshold for filtering detections
            enable_counting: Whether to enable object counting features
            enable_alerting: Whether to enable alerting features
            map_index_to_category: Whether to map category indices to names
            index_to_category: Mapping from category indices to category names
            category_triggers: List of categories that should trigger alerts
            count_threshold: Threshold for triggering count-based alerts
    
        Returns:
            PostProcessingConfig optimized for detection models
    """
def create_dual_output(file_directory: str, kafka_topic: str, kafka_bootstrap_servers: str, filename_pattern: str = None, max_files: int = None, kafka_key_field: str = 'stream_key', producer_config: Dict = None, post_processing_config: Any = None, apply_post_processing: bool = False, save_original_results: bool = True) -> Any: ...
    """
    Create a dual output configuration (both file and Kafka).
    
        Args:
            file_directory: Directory for file output
            kafka_topic: Kafka topic name
            kafka_bootstrap_servers: Kafka bootstrap servers
            filename_pattern: Pattern for output filenames
            max_files: Maximum number of files to keep
            kafka_key_field: Field to use as Kafka message key
            producer_config: Additional Kafka producer configuration
    
        Returns:
            OutputConfig instance for dual output
    """
def create_file_output(directory: str, filename_pattern: str = None, max_files: int = None, post_processing_config: Any = None, apply_post_processing: bool = False, save_original_results: bool = True) -> Any: ...
    """
    Create a file output configuration.
    
        Args:
            directory: Output directory path
            filename_pattern: Pattern for output filenames
            max_files: Maximum number of files to keep
            post_processing_config: Post-processing configuration (optional)
            apply_post_processing: Whether to apply post-processing (default: False)
            save_original_results: Whether to save original results alongside processed ones (default: True)
    
        Returns:
            OutputConfig instance for file output
    """
def create_http_video_frame_input(video_url: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None) -> Any: ...
    """
    Create an HTTP video file input for frame-based streaming.
    
        Args:
            video_url: HTTP/HTTPS video file URL
            fps: Frames per second
            quality: Image quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
    
        Returns:
            InputConfig: HTTP video input configured for frame streaming
    """
def create_http_video_input(video_url: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, model_input_type: Any = ModelInputType.FRAMES, video_duration: float = None, max_frames: int = None, video_format: str = 'mp4') -> Any: ...
    """
    Create an HTTP video file input configuration.
    
        Args:
            video_url: HTTP/HTTPS video file URL
            fps: Frames per second to process
            quality: Video/image quality (1-100)
            stream_key: Unique identifier for the stream
            width: Frame width in pixels
            height: Frame height in pixels
            model_input_type: FRAMES for individual images, VIDEO for video chunks
            video_duration: Duration of video chunks in seconds (only for VIDEO mode)
            max_frames: Maximum frames per video chunk (only for VIDEO mode)
            video_format: Video format for encoding (mp4, avi, webm)
    
        Returns:
            InputConfig: Configured input for HTTP video file
    
        Raises:
            ValueError: If parameters are invalid
    """
def create_http_video_video_input(video_url: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, video_duration: float = 5.0, video_format: str = 'mp4') -> Any: ...
    """
    Create an HTTP video file input for video-based streaming with duration limit.
    
        Args:
            video_url: HTTP/HTTPS video file URL
            fps: Frames per second
            quality: Video quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
            video_duration: Duration of video chunks in seconds
            video_format: Video format (mp4, avi, webm)
    
        Returns:
            InputConfig: HTTP video input configured for video streaming
    """
def create_http_video_video_input_by_frames(video_url: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, max_frames: int = 150, video_format: str = 'mp4') -> Any: ...
    """
    Create an HTTP video file input for video-based streaming with frame count limit.
    
        Args:
            video_url: HTTP/HTTPS video file URL
            fps: Frames per second
            quality: Video quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
            max_frames: Maximum frames per video chunk
            video_format: Video format (mp4, avi, webm)
    
        Returns:
            InputConfig: HTTP video input configured for video streaming
    """
def create_kafka_output(topic: str, bootstrap_servers: str, key_field: str = 'stream_key', producer_config: Dict = None) -> Any: ...
    """
    Create a Kafka output configuration.
    
        Args:
            topic: Kafka topic name
            bootstrap_servers: Kafka bootstrap servers
            key_field: Field to use as message key
            producer_config: Additional Kafka producer configuration
    
        Returns:
            OutputConfig instance for Kafka output
    """
def create_rtsp_input(rtsp_url: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, model_input_type: Any = ModelInputType.FRAMES, video_duration: float = None, max_frames: int = None, video_format: str = 'mp4') -> Any: ...
    """
    Create an RTSP stream input configuration.
    
        Args:
            rtsp_url: RTSP stream URL
            fps: Frames per second to capture
            quality: Video/image quality (1-100)
            stream_key: Unique identifier for the stream
            width: Frame width in pixels
            height: Frame height in pixels
            model_input_type: FRAMES for individual images, VIDEO for video chunks
            video_duration: Duration of video chunks in seconds (only for VIDEO mode)
            max_frames: Maximum frames per video chunk (only for VIDEO mode)
            video_format: Video format for encoding (mp4, avi, webm)
    
        Returns:
            InputConfig: Configured input for RTSP stream
    
        Raises:
            ValueError: If parameters are invalid
    """
def create_security_post_processing_config(person_confidence_threshold: float = 0.8, vehicle_confidence_threshold: float = 0.7, restricted_zones: Dict[str, List[Tuple[int, int]]] = None, entrance_lines: Dict[str, List[Tuple[int, int]]] = None, alert_on_person: bool = True, max_person_count: int = 5) -> Any: ...
    """
    Create a post-processing configuration optimized for security monitoring.
    
        Args:
            person_confidence_threshold: Confidence threshold for person detection
            vehicle_confidence_threshold: Confidence threshold for vehicle detection
            restricted_zones: Dictionary of restricted zone names to polygon coordinates
            entrance_lines: Dictionary of entrance line names to line coordinates
            alert_on_person: Whether to alert whenever a person is detected
            max_person_count: Maximum allowed person count before triggering alert
    
        Returns:
            PostProcessingConfig optimized for security monitoring
    """
def create_tracking_post_processing_config(confidence_threshold: float = 0.6, enable_tracking: bool = True, enable_counting: bool = True, enable_alerting: bool = True, tracking_zones: Dict[str, List[Tuple[int, int]]] = None, crossing_lines: Dict[str, List[Tuple[int, int]]] = None, map_index_to_category: bool = False, index_to_category: Dict[int, str] = None, category_triggers: List[str] = None) -> Any: ...
    """
    Create a post-processing configuration optimized for object tracking.
    
        Args:
            confidence_threshold: Global confidence threshold for filtering detections
            enable_tracking: Whether to enable tracking features
            enable_counting: Whether to enable object counting features
            enable_alerting: Whether to enable alerting features
            tracking_zones: Dictionary of zone names to polygon coordinates
            crossing_lines: Dictionary of line names to line coordinates
            map_index_to_category: Whether to map category indices to names
            index_to_category: Mapping from category indices to category names
            category_triggers: List of categories that should trigger alerts
    
        Returns:
            PostProcessingConfig optimized for tracking models
    """
def create_video_frame_input(video_path: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None) -> Any: ...
    """
    Create a video file input for frame-based streaming.
    
        Args:
            video_path: Path to video file
            fps: Frames per second
            quality: Image quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
    
        Returns:
            InputConfig: Video input configured for frame streaming
    """
def create_video_input(video_path: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, model_input_type: Any = ModelInputType.FRAMES, video_duration: float = None, max_frames: int = None, video_format: str = 'mp4') -> Any: ...
    """
    Create a video file input configuration.
    
        Args:
            video_path: Path to the video file
            fps: Frames per second to process
            quality: Video/image quality (1-100)
            stream_key: Unique identifier for the stream
            width: Frame width in pixels
            height: Frame height in pixels
            model_input_type: FRAMES for individual images, VIDEO for video chunks
            video_duration: Duration of video chunks in seconds (only for VIDEO mode)
            max_frames: Maximum frames per video chunk (only for VIDEO mode)
            video_format: Video format for encoding (mp4, avi, webm)
    
        Returns:
            InputConfig: Configured input for video file
    
        Raises:
            ValueError: If parameters are invalid
            FileNotFoundError: If video file doesn't exist
    """
def create_video_video_input(video_path: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, video_duration: float = 5.0, video_format: str = 'mp4') -> Any: ...
    """
    Create a video file input for video-based streaming with duration limit.
    
        Args:
            video_path: Path to video file
            fps: Frames per second
            quality: Video quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
            video_duration: Duration of video chunks in seconds
            video_format: Video format (mp4, avi, webm)
    
        Returns:
            InputConfig: Video input configured for video streaming
    """
def create_video_video_input_by_frames(video_path: str, fps: int = 30, quality: int = 95, stream_key: str = None, width: int = None, height: int = None, max_frames: int = 150, video_format: str = 'mp4') -> Any: ...
    """
    Create a video file input for video-based streaming with frame count limit.
    
        Args:
            video_path: Path to video file
            fps: Frames per second
            quality: Video quality (1-100)
            stream_key: Stream identifier
            width: Frame width
            height: Frame height
            max_frames: Maximum frames per video chunk
            video_format: Video format (mp4, avi, webm)
    
        Returns:
            InputConfig: Video input configured for video streaming
    """

# Classes
class FileOutputConfig:
    """
    Configuration for file output.
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create from dictionary.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert to dictionary.
        """

class InputConfig:
    """
    Configuration for input sources.
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create from dictionary.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert to dictionary.
        """

class InputType(Enum):
    """
    Supported input types.
    """

    AUTO: str
    CAMERA: str
    HTTP_STREAM: str
    HTTP_VIDEO_FILE: str
    RTSP_STREAM: str
    VIDEO_FILE: str

    pass
class KafkaOutputConfig:
    """
    Configuration for Kafka output.
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create from dictionary.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert to dictionary.
        """

class ModelInputType(Enum):
    """
    Supported model input types.
    """

    FRAMES: str
    VIDEO: str

    pass
class OutputConfig:
    """
    Configuration for output destinations.
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create from dictionary.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert to dictionary.
        """

class OutputType(Enum):
    """
    Supported output types.
    """

    BOTH: str
    FILE: str
    KAFKA: str

    pass
