"""Auto-generated stub for module: frame_difference."""
from typing import Any, Dict, Optional, Tuple, Union

from PIL import Image
import base64
import cv2
import logging
import numpy as np

# Constants
logger: Any

# Classes
class FrameDifferenceProcessor:
    """
    Handles frame difference calculation and reconstruction for intelligent caching.
    """

    def __init__(self: Any) -> None: ...
        """
        Initialize frame difference processor.
        """

    def calculate_frame_difference(self: Any, reference_frame: Any, current_frame: Any) -> Tuple[np.ndarray, Dict[str, Any]]: ...
        """
        Calculate difference between reference and current frame.
        
                Args:
                    reference_frame: Reference frame (RGB, cv2 image as np.ndarray)
                    current_frame: Current frame to compare (RGB, cv2 image as np.ndarray)
        
                Returns:
                    Tuple of (difference_data, metadata)
        """

    def decode_base64_to_frame(self: Any, encoded_frame: str) -> Optional[np.ndarray]: ...
        """
        Decode base64 string to frame.
        
                Args:
                    encoded_frame: Base64 encoded frame
        
                Returns:
                    Decoded frame as numpy array or None if failed
        """

    def decode_frame_difference(self: Any, encoded_diff: str) -> Optional[np.ndarray]: ...
        """
        Decode base64 frame difference data.
        
                Args:
                    encoded_diff: Base64 encoded difference data
        
                Returns:
                    Decoded difference as numpy array or None if failed
        """

    def encode_frame_difference(self: Any, difference_data: Any, metadata: Dict[str, Any], compression_quality: int = 85) -> str: ...
        """
        Encode frame difference data to base64.
        
                Args:
                    difference_data: Frame difference as numpy array
                    metadata: Difference metadata
                    compression_quality: JPEG compression quality (1-100)
        
                Returns:
                    Base64 encoded difference data
        """

    def encode_frame_to_base64(self: Any, frame: Any, quality: int = 95) -> str: ...
        """
        Encode frame to base64 string.
        
                Args:
                    frame: Frame as numpy array
                    quality: JPEG quality (1-100)
        
                Returns:
                    Base64 encoded frame
        """

    def reconstruct_frame(self: Any, reference_frame: Any, difference_data: Any, metadata: Dict[str, Any]) -> Optional[np.ndarray]: ...
        """
        Reconstruct frame from reference frame and difference data.
        
                Args:
                    reference_frame: Reference frame (RGB, cv2 image as np.ndarray)
                    difference_data: Frame difference data
                    metadata: Difference metadata
        
                Returns:
                    Reconstructed frame or None if failed
        """

class IntelligentFrameCache:
    """
    Intelligent frame cache with two-threshold logic.
    """

    def __init__(self: Any, threshold_a: float = 0.95, threshold_b: float = 0.85, max_cache_size: int = 50) -> None: ...
        """
        Initialize intelligent frame cache.
        
                Args:
                    threshold_a: High similarity threshold for cache reuse
                    threshold_b: Medium similarity threshold for difference-based reconstruction
                    max_cache_size: Maximum number of cached frames per stream
        """

    def cache_frame_result(self: Any, stream_key: str, frame: Any, model_result: Any, input_hash: Optional[str] = None) -> None: ...
        """
        Cache frame and its model result.
        
                Args:
                    stream_key: Stream identifier
                    frame: Frame that was processed
                    model_result: Result from model inference
                    input_hash: Optional input hash for additional indexing
        """

    def clear_cache(self: Any, stream_key: Optional[str] = None) -> None: ...
        """
        Clear cache for specific stream or all streams.
        
                Args:
                    stream_key: Stream to clear, or None to clear all
        """

    def get_cache_stats(self: Any) -> Dict[str, Any]: ...
        """
        Get cache statistics.
        
                Returns:
                    Dictionary with cache statistics
        """

    def get_cached_result(self: Any, stream_key: str, action_data: Dict[str, Any]) -> Any: ...
        """
        Get cached result based on action data.
        
                Args:
                    stream_key: Stream identifier
                    action_data: Data from should_use_cache decision
        
                Returns:
                    Cached model result or None
        """

    def should_use_cache(self: Any, current_frame: Any, stream_key: str, ssim_comparator: Any) -> Tuple[str, Dict[str, Any]]: ...
        """
        Determine caching strategy based on frame similarity.
        
                Args:
                    current_frame: Current frame to analyze
                    stream_key: Stream identifier
                    ssim_comparator: SSIM comparator for similarity calculation
        
                Returns:
                    Tuple of (action, data) where action is:
                    - "use_cache": Use cached result (Threshold A)
                    - "use_difference": Use difference-based reconstruction (Threshold B)
                    - "process_new": Process as new frame (exceeds both thresholds)
        """

