"""Auto-generated stub for module: cache_manager."""
from typing import Any, Dict

from collections import OrderedDict

# Classes
class CacheManager:
    def __init__(self: Any, max_cache_size: int = 5) -> None: ...

    def clear_cache(self: Any, stream_key: str = None) -> Any: ...

    def get_cached_result(self: Any, input_hash: str, stream_key: str = None) -> Any: ...

    def set_cached_result(self: Any, input_hash: str, value: dict, stream_key: str = None) -> Any: ...

