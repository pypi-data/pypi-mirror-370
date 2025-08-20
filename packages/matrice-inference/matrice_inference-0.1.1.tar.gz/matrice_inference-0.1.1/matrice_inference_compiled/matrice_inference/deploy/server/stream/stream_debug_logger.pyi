"""Auto-generated stub for module: stream_debug_logger."""
from typing import Any, Dict, List

from datetime import datetime, timezone
import logging
import time

# Classes
class StreamDebugLogger:
    """
    Debug logging component for stream processing pipeline.
    """

    def __init__(self: Any, enabled: bool = False, log_interval: float = 30.0) -> None: ...
        """
        Initialize debug logger.
        
                Args:
                    enabled: Whether debug logging is enabled
                    log_interval: Interval between debug log messages in seconds
        """

    def disable(self: Any) -> Any: ...
        """
        Disable debug logging.
        """

    def enable(self: Any) -> Any: ...
        """
        Enable debug logging.
        """

    def get_debug_summary(self: Any) -> Dict[str, Any]: ...
        """
        Get debug logging summary.
        """

    def log_pipeline_status(self: Any, stream_manager: Any) -> Any: ...
        """
        Log pipeline status if enabled and interval passed.
        """

    def should_log(self: Any) -> bool: ...
        """
        Check if we should log based on interval.
        """

