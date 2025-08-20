"""Auto-generated stub for module: transmission."""
from typing import Any, Dict, Optional, Tuple

from datetime import datetime, timezone
from frame_comparators import SSIMComparator
from frame_difference import FrameDifferenceProcessor
import base64
import cv2
import hashlib
import logging
import numpy as np

# Constants
logger: Any

# Classes
class ClientTransmissionHandler:
    """
    Client-side transmission handler implementing two-threshold logic.
    
        Responsibilities:
        - Maintain last frame per stream for SSIM reference
        - Decide strategy: full, difference, or skip
        - Produce difference payload (base64-encoded JPEG) and metadata
        - Track last full-frame input hash for server cache linking
    """

    def __init__(self: Any, threshold_a: float = 0.95, threshold_b: float = 0.85) -> None: ...

    def compute_and_store_full_frame_hash(self: Any, stream_key: str, full_jpeg_bytes: Any) -> str: ...
        """
        Compute deterministic MD5 (non-security) and store it for reference.
        """

    def decide_transmission(self: Any, frame: Any, stream_key: str) -> Tuple[str, Dict[str, Any]]: ...
        """
        Determine transmission strategy for a frame.
        
                Returns: (strategy, data)
                  strategy in {"full", "difference", "skip"}
                  data contains similarity and optional diff payload metadata
        """

    def encode_difference(self: Any, difference_data: Any, difference_metadata: Dict[str, Any], quality: int) -> Any: ...
        """
        Encode difference np.ndarray to raw bytes suitable for transport.
        """

    def prepare_transmission(self: Any, frame: Any) -> Tuple[bytes, Dict[str, Any], str]: ...
        """
        Prepare bytes payload and metadata for transport.
        
                Returns (input_bytes, metadata, strategy)
        """

class ServerTransmissionHandler:
    """
    Server-side transmission handler for intelligent input handling.
    
        Responsibilities:
        - Interpret transmission_strategy from client (skip/difference/full)
        - Resolve cache hits for skip signals
        - Reconstruct frames for difference payloads
        - Perform SSIM similarity checks for optional skipping
    """

    def __init__(self: Any, ssim_threshold: float = 0.95) -> None: ...

    def decide_action(self: Any, message: Dict[str, Any], cache_manager: Any, frame_cache: Dict[str, np.ndarray]) -> Tuple[str, Optional[Dict[str, Any]]]: ...
        """
        Decide how to handle an incoming message.
        
                Returns (action, payload):
                  - ("cached", cached_result)
                  - ("similar", None)
                  - ("process_difference", None) -> call reconstruct() then process
                  - ("process", None)
        """

    def process_input_message(self: Any, raw_message_value: Dict[str, Any], message_key: Optional[str], consumer_worker_id: str) -> Dict[str, Any]: ...
        """
        Normalize raw Kafka message 'value' into a processed message structure.
        
                Handles transmission_strategy: 'skip', 'difference', 'full'.
                Decodes content accordingly and carries through strategy metadata.
        """

    def reconstruct_from_difference(self: Any, message: Dict[str, Any], frame_cache: Dict[str, np.ndarray]) -> Tuple[Optional[bytes], Optional[str]]: ...
        """
        Reconstruct full frame from difference; returns (jpeg_bytes, effective_hash).
        """

    def update_frame_cache_from_message(self: Any, message: Dict[str, Any], frame_cache: Dict[str, np.ndarray]) -> None: ...
        """
        If message has image bytes, decode and store for SSIM reference.
        """

