"""Auto-generated stub for module: video_buffer."""
from typing import Any, Dict, List, Optional

from collections import defaultdict, deque
from datetime import datetime, timezone
import asyncio
import base64
import cv2
import logging
import numpy as np
import os
import tempfile

# Functions
def base64_frames_to_video_bytes_cv2(base64_frames: Any, fps: Any = 10, output_format: Any = 'mp4') -> Any: ...
    """
    Convert base64-encoded JPEG frames to a video using OpenCV,
    and return the video bytes by writing to a temp file.
    """

# Classes
class FrameBuffer:
    """
    Buffer for collecting frames into video chunks.
    """

    def __init__(self: Any, stream_key: str, buffer_config: Dict[str, Any]) -> None: ...
        """
        Initialize frame buffer for a specific stream.
        
                Args:
                    stream_key: Unique identifier for the stream
                    buffer_config: Configuration for buffering (fps, duration, etc.)
        """

    def add_frame(self: Any, base64_frame: str, metadata: Dict[str, Any]) -> bool: ...
        """
        Add a frame to the buffer.
        
                Args:
                    base64_frame: Base64 encoded frame data
                    metadata: Frame metadata
        
                Returns:
                    True if buffer is ready for processing, False otherwise
        """

    def clear(self: Any) -> Any: ...
        """
        Clear the buffer.
        """

    def create_video_chunk(self: Any) -> Optional[Dict[str, Any]]: ...
        """
        Create a video chunk from buffered frames.
        
                Returns:
                    Dictionary containing video data and metadata, or None if failed
        """

    def is_expired(self: Any, max_idle_time: float = 30.0) -> bool: ...
        """
        Check if buffer has been idle too long.
        """

    def is_ready(self: Any) -> bool: ...
        """
        Check if buffer is ready for processing.
        """

class VideoBufferManager:
    """
    Manages multiple frame buffers for different streams.
    """

    def __init__(self: Any, default_fps: int = 10, default_chunk_duration: float = 5.0, default_timeout: float = 10.0, max_idle_time: float = 30.0, cleanup_interval: float = 60.0) -> None: ...
        """
        Initialize video buffer manager.
        
                Args:
                    default_fps: Default FPS for video chunks
                    default_chunk_duration: Default chunk duration in seconds
                    default_timeout: Default timeout for buffering in seconds
                    max_idle_time: Maximum idle time before buffer cleanup
                    cleanup_interval: Interval for cleanup tasks
        """

    async def add_frame(self: Any, stream_key: str, base64_frame: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...
        """
        Add a frame to the appropriate buffer.
        
                Args:
                    stream_key: Stream identifier
                    base64_frame: Base64 encoded frame data
                    metadata: Frame metadata
        
                Returns:
                    Video chunk data if buffer is ready, None otherwise
        """

    def get_metrics(self: Any) -> Dict[str, Any]: ...
        """
        Get buffer manager metrics.
        """

    def reset_metrics(self: Any) -> Any: ...
        """
        Reset metrics.
        """

    async def start(self: Any) -> Any: ...
        """
        Start the buffer manager.
        """

    async def stop(self: Any) -> Any: ...
        """
        Stop the buffer manager.
        """

