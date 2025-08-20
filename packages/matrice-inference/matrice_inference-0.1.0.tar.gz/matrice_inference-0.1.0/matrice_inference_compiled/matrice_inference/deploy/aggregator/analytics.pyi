"""Auto-generated stub for module: analytics."""
from typing import Any, Dict, List, Optional, Tuple

from confluent_kafka import Producer
from matrice_common.session import Session
import base64
import json
import logging
import threading
import time

# Classes
class AnalyticsSummarizer:
    """
    Buffers aggregated camera_results and emits 5-minute rollups per camera
    focusing on tracking_stats per application.
    
    Output structure example per camera:
        {
          "camera_name": "camera_1",
          "inferencePipelineId": "pipeline-xyz",
          "camera_group": "group_a",
          "location": "Lobby",
          "agg_apps": [
            {
              "application_name": "People Counting",
              "application_key_name": "People_Counting",
              "application_version": "1.3",
              "tracking_stats": {
                "input_timestamp": "00:00:09.9",          # last seen
                "reset_timestamp": "00:00:00",             # earliest seen in window
                "current_counts": [{"category": "person", "count": 4}],  # last seen
                "total_counts": [{"category": "person", "count": 37}]   # max seen in window
              }
            }
          ],
          "summary_metadata": {
            "window_seconds": 300,
            "messages_aggregated": 123,
            "start_time": 1710000000.0,
            "end_time": 1710000300.0
          }
        }
    """

    def __init__(self: Any, session: Session, inference_pipeline_id: str, flush_interval_seconds: int = 300) -> None: ...

    def cleanup(self: Any) -> None: ...

    def get_health_status(self: Any) -> Dict[str, Any]: ...

    def get_stats(self: Any) -> Dict[str, Any]: ...

    def ingest_result(self: Any, aggregated_result: Dict[str, Any]) -> None: ...
        """
        Receive a single aggregated camera_results payload for buffering.
        This is intended to be called by the publisher after successful publish.
        """

    def start(self: Any) -> bool: ...

    def stop(self: Any) -> None: ...

