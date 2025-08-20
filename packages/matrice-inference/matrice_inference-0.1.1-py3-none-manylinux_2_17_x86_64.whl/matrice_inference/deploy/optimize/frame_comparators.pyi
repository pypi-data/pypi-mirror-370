"""Auto-generated stub for module: frame_comparators."""
from typing import Any, Optional, Tuple

from PIL import Image
from imagehash import average_hash, phash, dhash
from skimage.metrics import structural_similarity
import cv2
import logging
import numpy as np

# Classes
class AbsDiffComparator(FrameComparator):
    """
    Compare frames using absolute difference.
    """

    def __init__(self: Any, threshold: float = 10.0) -> None: ...
        """
        Initialize with threshold for mean absolute difference.
        
                Args:
                    threshold: Mean difference threshold (default: 10.0).
        
                Raises:
                    ValueError: If threshold is negative.
        """

    def compare(self: Any, static_frame: Any, new_frame: Any, stream_key: Optional[str] = None) -> Tuple[bool, float]: ...
        """
        Compare frames using mean absolute difference.
        
                Args:
                    static_frame: Reference frame (RGB, cv2 image as np.ndarray).
                    new_frame: New frame to compare (RGB, cv2 image as np.ndarray).
                    stream_key: Optional identifier for the video stream (e.g., camera ID).
        
                Returns:
                    Tuple[bool, float]: (is_similar, mean_difference)
        """

class AverageHashComparator(FrameComparator):
    """
    Compares frames using average hashing (aHash).
    """

    def __init__(self: Any, threshold: int = 5) -> None: ...
        """
        Initialize with threshold for hash difference.
        
                Args:
                    threshold: Hash difference threshold (default: 5).
        
                Raises:
                    ValueError: If threshold is negative.
        """

    def compare(self: Any, static_frame: Any, new_frame: Any, stream_key: Optional[str] = None) -> Tuple[bool, float]: ...
        """
        Compare frames using average hash difference.
        
                Args:
                    static_frame: Reference frame (RGB, cv2 image as np.ndarray).
                    new_frame: New frame to compare (RGB, cv2 image as np.ndarray).
                    stream_key: Optional identifier for the video stream (e.g., camera ID).
        
                Returns:
                    Tuple[bool, float]: (is_similar, hash_difference)
        """

class DifferenceHashComparator(FrameComparator):
    """
    Compares frames using difference hashing (dHash).
    """

    def __init__(self: Any, threshold: int = 5) -> None: ...
        """
        Initialize with threshold for hash difference.
        
                Args:
                    threshold: Hash difference threshold (default: 5).
        
                Raises:
                    ValueError: If threshold is negative.
        """

    def compare(self: Any, static_frame: Any, new_frame: Any, stream_key: Optional[str] = None) -> Tuple[bool, float]: ...
        """
        Compare frames using difference hash difference.
        
                Args:
                    static_frame: Reference frame (RGB, cv2 image as np.ndarray).
                    new_frame: New frame to compare (RGB, cv2 image as np.ndarray).
                    stream_key: Optional identifier for the video stream (e.g., camera ID).
        
                Returns:
                    Tuple[bool, float]: (is_similar, hash_difference)
        """

class FrameComparator:
    """
    Base class for frame comparison methods.
    """

    def compare(self: Any, static_frame: Any, new_frame: Any, stream_key: Optional[str] = None) -> Tuple[bool, float]: ...
        """
        Compare frames and determine if they are similar.
        
                Args:
                    static_frame: Reference frame (RGB, cv2 image as np.ndarray).
                    new_frame: New frame to compare (RGB, cv2 image as np.ndarray).
                    stream_key: Optional identifier for the video stream (e.g., camera ID).
        
                Returns:
                    Tuple[bool, float]: (is_similar, similarity_score)
        """

class HistogramComparator(FrameComparator):
    """
    Compare frames using histogram correlation.
    """

    def __init__(self: Any, threshold: float = 0.9) -> None: ...
        """
        Initialize with threshold for histogram correlation.
        
                Args:
                    threshold: Correlation score threshold (default: 0.9).
        
                Raises:
                    ValueError: If threshold is not in [0, 1].
        """

    def compare(self: Any, static_frame: Any, new_frame: Any, stream_key: Optional[str] = None) -> Tuple[bool, float]: ...
        """
        Compare frames using histogram correlation.
        
                Args:
                    static_frame: Reference frame (RGB, cv2 image as np.ndarray).
                    new_frame: New frame to compare (RGB, cv2 image as np.ndarray).
                    stream_key: Optional identifier for the video stream (e.g., camera ID).
        
                Returns:
                    Tuple[bool, float]: (is_similar, correlation_score)
        """

class PerceptualHashComparator(FrameComparator):
    """
    Compares frames using perceptual hashing (pHash).
    """

    def __init__(self: Any, threshold: int = 6) -> None: ...
        """
        Initialize with threshold for hash difference.
        
                Args:
                    threshold: Hash difference threshold (default: 6).
        
                Raises:
                    ValueError: If threshold is negative.
        """

    def compare(self: Any, static_frame: Any, new_frame: Any, stream_key: Optional[str] = None) -> Tuple[bool, float]: ...
        """
        Compare frames using perceptual hash difference.
        
                Args:
                    static_frame: Reference frame (RGB, cv2 image as np.ndarray).
                    new_frame: New frame to compare (RGB, cv2 image as np.ndarray).
                    stream_key: Optional identifier for the video stream (e.g., camera ID).
        
                Returns:
                    Tuple[bool, float]: (is_similar, hash_difference)
        """

class SSIMComparator(FrameComparator):
    """
    Compare frames using Structural Similarity Index (SSIM).
    """

    def __init__(self: Any, threshold: float = 0.9) -> None: ...
        """
        Initialize with threshold for SSIM score.
        
                Args:
                    threshold: SSIM score threshold (default: 0.9).
        
                Raises:
                    ValueError: If threshold is not in [0, 1].
        """

    def compare(self: Any, static_frame: Any, new_frame: Any, stream_key: Optional[str] = None) -> Tuple[bool, float]: ...
        """
        Compare frames using SSIM.
        
                Args:
                    static_frame: Reference frame (RGB, cv2 image as np.ndarray).
                    new_frame: New frame to compare (RGB, cv2 image as np.ndarray).
                    stream_key: Optional identifier for the video stream (e.g., camera ID).
        
                Returns:
                    Tuple[bool, float]: (is_similar, ssim_score)
        """

