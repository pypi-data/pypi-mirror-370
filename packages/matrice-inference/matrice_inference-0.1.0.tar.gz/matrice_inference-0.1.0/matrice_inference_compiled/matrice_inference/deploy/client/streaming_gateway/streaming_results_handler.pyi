"""Auto-generated stub for module: streaming_results_handler."""
from typing import Any, Dict, Optional

from confluent_kafka import Producer
from datetime import datetime
from matrice_inference.deploy.client.client_stream_utils import ClientStreamUtils
from matrice_inference.deploy.client.streaming_gateway.streaming_gateway_utils import OutputType, OutputConfig, _RealTimeJsonEventPicker
from matrice_inference.deploy.utils.post_processing import PostProcessor
import json
import logging
import os
import threading
import time

# Classes
class StreamingResultsHandler:
    def __init__(self: Any, client_stream_utils: Any, output_config: Any, json_event_picker: Any, service_id: str = None, strip_input_from_result: bool = True, result_callback: Optional[Callable] = None) -> None: ...

    pass
