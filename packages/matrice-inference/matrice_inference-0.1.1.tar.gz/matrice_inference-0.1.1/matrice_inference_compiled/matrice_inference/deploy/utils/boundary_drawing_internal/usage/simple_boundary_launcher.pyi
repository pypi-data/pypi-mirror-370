"""Auto-generated stub for module: simple_boundary_launcher."""
from typing import Any, List

from matrice_inference.deploy.utils.boundary_drawing_internal import EasyBoundaryTool
from pathlib import Path
import os
import sys

# Constants
current_dir: Any
matrice_path: Any
src_path: Any

# Functions
def launch_boundary_tool(video_path: Any, custom_zones: Any = None) -> Any: ...
    """
    Launch the boundary drawing tool for any video file.
    
    Args:
        video_path (str): Path to the video file
        custom_zones (list): List of zone names to use
    """
