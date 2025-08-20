"""Auto-generated stub for module: camera_manager."""
from typing import Any, Dict, List, Optional, Set, Tuple

from dataclasses import dataclass, asdict
import logging

# Classes
class Camera:
    """
    Camera instance class for managing individual camera configurations.
    
    This class represents a single camera and provides methods to manage
    its configuration, stream settings, and operational status.
    
    Example:
        Basic usage:
        ```python
        from matrice import Session
        from matrice_inference.deployment.camera_manager import Camera, CameraConfig
    
        session = Session(account_number="...", access_key="...", secret_key="...")
    
        # Create camera config
        config = CameraConfig(
            camera_name="entrance_cam_01",
            stream_url="rtsp://192.168.1.100:554/stream1",
            camera_group_id="group_id_123",
            custom_stream_settings={"videoQuality": 90}
        )
    
        # Create camera instance
        camera = Camera(session, config)
    
        # Save to backend
        result, error, message = camera.save(service_id="deployment_id")
        if not error:
            print(f"Camera created with ID: {camera.id}")
    
        # Update configuration
        camera.stream_url = "rtsp://192.168.1.101:554/stream1"
        result, error, message = camera.update()
        ```
    """

    def __init__(self: Any, session: Any, config: Any = None, camera_id: str = None) -> None: ...
        """
        Initialize a Camera instance.
        
        Args:
            session: Session object containing RPC client for API communication
            config: CameraConfig object (for new cameras)
            camera_id: ID of existing camera to load (mutually exclusive with config)
        """

    def camera_group_id(self: Any) -> str: ...
        """
        Get the camera group ID.
        """

    def camera_group_id(self: Any, value: str) -> Any: ...
        """
        Set the camera group ID.
        """

    def camera_name(self: Any) -> str: ...
        """
        Get the camera name.
        """

    def camera_name(self: Any, value: str) -> Any: ...
        """
        Set the camera name.
        """

    def custom_stream_settings(self: Any) -> Dict: ...
        """
        Get the custom stream settings.
        """

    def custom_stream_settings(self: Any, value: Dict) -> Any: ...
        """
        Set the custom stream settings.
        """

    def delete(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete the camera from the backend.
        
        Returns:
            tuple: (result, error, message)
        """

    def get_effective_stream_settings(self: Any, group_defaults: Any) -> Any: ...
        """
        Get the effective stream settings by merging group defaults with custom overrides.
        
        Args:
            group_defaults: Default stream settings from the camera group
        
        Returns:
            StreamSettings with effective values
        """

    def get_stream_url(self: Any) -> str: ...
        """
        Get the camera stream URL.
        """

    def id(self: Any) -> Optional[str]: ...
        """
        Get the camera ID.
        """

    def is_stream_url(self: Any) -> bool: ...
        """
        Get whether the camera stream URL is a valid URL.
        """

    def is_stream_url(self: Any, value: bool) -> Any: ...
        """
        Set whether the camera stream URL is a valid URL.
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the camera configuration from the backend.
        """

    def save(self: Any, service_id: str = None) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Save the camera configuration to the backend (create new).
        
        Args:
            service_id: The deployment or inference pipeline ID to associate with
        
        Returns:
            tuple: (result, error, message)
        """

    def stream_url(self: Any) -> str: ...
        """
        Get the camera stream URL.
        """

    def stream_url(self: Any, value: str) -> Any: ...
        """
        Set the camera stream URL.
        """

    def update(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update the camera configuration in the backend.
        
        Returns:
            tuple: (result, error, message)
        """

class CameraConfig:
    """
    Camera configuration data class.
    
    Attributes:
        id: Unique identifier for the camera config (MongoDB ObjectID)
        id_service: Deployment ID this camera config belongs to (MongoDB ObjectID)
        camera_group_id: ID of the camera group this camera belongs to
        is_stream_url: Whether the stream URL is a valid URL
        camera_name: Name/identifier for the camera
        stream_url: URL for the camera stream
        custom_stream_settings: Custom stream settings that override group defaults
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create a CameraConfig instance from API response data.
        """

    def get_effective_stream_settings(self: Any, group_defaults: Any) -> Any: ...
        """
        Get the effective stream settings by merging group defaults with custom overrides.
        
        Args:
            group_defaults: Default stream settings from the camera group
        
        Returns:
            StreamSettings with effective values
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert the camera config to a dictionary for API calls.
        """

class CameraGroup:
    """
    Camera group instance class for managing individual camera groups and their cameras.
    
    This class represents a single camera group and provides methods to manage
    its configuration, cameras, and operational status.
    
    Example:
        Basic usage:
        ```python
        from matrice import Session
        from matrice_inference.deployment.camera_manager import CameraGroup, CameraGroup, StreamSettings
    
        session = Session(account_number="...", access_key="...", secret_key="...")
    
        # Create camera group config
        default_settings = StreamSettings(
            aspect_ratio="16:9",
            video_quality=80,
            height=1080,
            width=1920,
            fps=30
        )
    
        group_config = CameraGroupConfig(
            name="Indoor Cameras",
            location="Building A - First Floor",
            default_stream_settings=default_settings
        )
    
        # Create camera group instance
        camera_group = CameraGroup(session, group_config)
    
        # Save to backend
        result, error, message = camera_group.save(service_id="deployment_id")
        if not error:
            print(f"Camera group created with ID: {camera_group.id}")
    
        # Add cameras to the group
        camera_config = CameraConfig(
            camera_name="entrance_cam_01",
            stream_url="rtsp://192.168.1.100:554/stream1",
            camera_group_id=camera_group.id
        )
        camera, error, message = camera_group.add_camera(camera_config)
        ```
    """

    def __init__(self: Any, session: Any, config: Any = None, group_id: str = None) -> None: ...
        """
        Initialize a CameraGroup.
        
        Args:
            session: Session object containing RPC client for API communication
            config: CameraGroup object (for new groups)
            group_id: ID of existing group to load (mutually exclusive with config)
        """

    def add_camera(self: Any, camera_config: Any) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Add a camera to this camera group.
        
        Args:
            camera_config: CameraConfig object containing the camera configuration
        
        Returns:
            tuple: (camera_instance, error, message)
        """

    def cameras(self: Any) -> List['Camera']: ...
        """
        Get all cameras in this group.
        """

    def default_stream_settings(self: Any) -> Optional[StreamSettings]: ...
        """
        Get the default stream settings.
        """

    def default_stream_settings(self: Any, value: Any) -> Any: ...
        """
        Set the default stream settings.
        """

    def delete(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete the camera group from the backend.
        
        Returns:
            tuple: (result, error, message)
        """

    def get_cameras(self: Any, page: int = 1, limit: int = 10, search: str = None) -> Tuple[Optional[List['Camera']], Optional[str], str]: ...
        """
        Get all cameras in this camera group.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
        
        Returns:
            tuple: (camera_instances, error, message)
        """

    def id(self: Any) -> Optional[str]: ...
        """
        Get the group ID.
        """

    def location(self: Any) -> str: ...
        """
        Get the group location.
        """

    def location(self: Any, value: str) -> Any: ...
        """
        Set the group location.
        """

    def name(self: Any) -> str: ...
        """
        Get the group name.
        """

    def name(self: Any, value: str) -> Any: ...
        """
        Set the group name.
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the camera group configuration and cameras from the backend.
        """

    def remove_camera(self: Any, camera_id: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Remove a camera from this camera group.
        
        Args:
            camera_id: ID of the camera to remove
        
        Returns:
            tuple: (result, error, message)
        """

    def save(self: Any, service_id: str = None) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Save the camera group configuration to the backend (create new).
        
        Args:
            service_id: The deployment or inference pipeline ID to associate with
        
        Returns:
            tuple: (result, error, message)
        """

    def update(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update the camera group configuration in the backend.
        
        Returns:
            tuple: (result, error, message)
        """

class CameraGroupConfig:
    """
    Camera group data class for managing collections of cameras with shared settings.
    
    Attributes:
        id: Unique identifier for the camera group (MongoDB ObjectID)
        id_service: Deployment ID this group belongs to (MongoDB ObjectID)
        name: Name of the camera group
        location: Physical location description of the group
        default_stream_settings: Default stream settings for cameras in this group
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create a CameraGroup instance from API response data.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert the camera group to a dictionary for API calls.
        """

class CameraManager:
    """
    Camera manager client for handling camera groups and configurations in deployments.
    
    This class provides methods to create, read, update, and delete camera groups and
    camera configurations associated with deployments. It offers a streamlined flow
    for managing camera infrastructure.
    
    Example:
        Basic usage:
        ```python
        from matrice import Session
        from matrice_inference.deployment.camera_manager import CameraManager, CameraGroup, CameraConfig, StreamSettings
    
        session = Session(account_number="...", access_key="...", secret_key="...")
        camera_manager = CameraManager(session, service_id="...")
    
        # Create a camera group with default settings
        default_settings = StreamSettings(
            aspect_ratio="16:9",
            video_quality=80,
            height=1080,
            width=1920,
            fps=30
        )
    
        group = CameraGroup(
            name="Indoor Cameras",
            location="Building A - First Floor",
            default_stream_settings=default_settings
        )
    
        # Create the camera group
        camera_group, error, message = camera_manager.create_camera_group(group)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Camera group created: {camera_group.name}")
    
            # Add cameras to the group
            camera_config = CameraConfig(
                camera_name="main_entrance_cam",
                stream_url="rtsp://192.168.1.100:554/stream1",
                camera_group_id=camera_group.id,
                custom_stream_settings={"videoQuality": 90}
            )
    
            camera, error, message = camera_group.add_camera(camera_config)
            if not error:
                print(f"Camera added: {camera.camera_name}")
        ```
    """

    def __init__(self: Any, session: Any, service_id: str = None) -> None: ...
        """
        Initialize the CameraManager client.
        
        Args:
            session: Session object containing RPC client for API communication
            service_id: The ID of the deployment or the ID of the inference pipeline
        """

    def add_camera_config(self: Any, config: Any) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Legacy method - use create_camera instead.
        """

    def add_camera_configs(self: Any, configs: List[CameraConfig]) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Legacy method - use add_cameras_to_group instead.
        """

    def add_cameras_to_group(self: Any, group_id: str, camera_configs: List[CameraConfig]) -> Tuple[Optional[List['Camera']], Optional[str], str]: ...
        """
        Add multiple cameras to a camera group.
        
        Args:
            group_id: The ID of the camera group
            camera_configs: List of CameraConfig objects
        
        Returns:
            tuple: (camera_instances, error, message)
        """

    def create_camera(self: Any, camera_config: Any) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Create a new camera configuration.
        
        Args:
            camera_config: CameraConfig object containing the camera configuration
        
        Returns:
            tuple: (camera_instance, error, message)
        """

    def create_camera_group(self: Any, group: Any) -> Tuple[Optional['CameraGroup'], Optional[str], str]: ...
        """
        Create a new camera group for a deployment.
        
        Args:
            group: CameraGroup object containing the group configuration
        
        Returns:
            tuple: (camera_group_instance, error, message)
                - camera_group_instance: CameraGroupInstance if successful, None otherwise
                - error: Error message if failed, None otherwise
                - message: Status message
        """

    def delete_all_cameras(self: Any, confirm: bool = False) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete all cameras for a specific deployment.
        
        Args:
            confirm: Must be True to confirm bulk deletion
        
        Returns:
            tuple: (result, error, message)
        """

    def delete_camera(self: Any, camera_id: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete a camera by its ID.
        
        Args:
            camera_id: The ID of the camera to delete
        
        Returns:
            tuple: (result, error, message)
        """

    def delete_camera_config_by_id(self: Any, config_id: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Legacy method - use delete_camera instead.
        """

    def delete_camera_configs(self: Any, confirm: bool = False) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Legacy method - use delete_all_cameras instead.
        """

    def delete_camera_group(self: Any, group_id: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete a camera group by its ID.
        
        Args:
            group_id: The ID of the camera group to delete
        
        Returns:
            tuple: (result, error, message)
        """

    def get_camera_by_id(self: Any, camera_id: str) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Get a camera by its ID.
        
        Args:
            camera_id: The ID of the camera to retrieve
        
        Returns:
            tuple: (camera_instance, error, message)
        """

    def get_camera_config_by_id(self: Any, config_id: str) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Legacy method - use get_camera_by_id instead.
        """

    def get_camera_configs(self: Any, page: int = 1, limit: int = 10, search: str = None, group_id: str = None) -> Tuple[Optional[List['Camera']], Optional[str], str]: ...
        """
        Legacy method - use get_cameras instead.
        """

    def get_camera_group_by_id(self: Any, group_id: str) -> Tuple[Optional['CameraGroup'], Optional[str], str]: ...
        """
        Get a camera group by its ID.
        
        Args:
            group_id: The ID of the camera group to retrieve
        
        Returns:
            tuple: (camera_group_instance, error, message)
        """

    def get_camera_groups(self: Any, page: int = 1, limit: int = 10, search: str = None) -> Tuple[Optional[List['CameraGroup']], Optional[str], str]: ...
        """
        Get all camera groups for a specific deployment.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
        
        Returns:
            tuple: (camera_group_instances, error, message)
        """

    def get_cameras(self: Any, page: int = 1, limit: int = 10, search: str = None, group_id: str = None) -> Tuple[Optional[List['Camera']], Optional[str], str]: ...
        """
        Get all cameras for a specific deployment.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
            group_id: Optional filter by camera group ID
        
        Returns:
            tuple: (camera_instances, error, message)
        """

    def get_stream_url(self: Any, config_id: str) -> Tuple[Optional[str], Optional[str], str]: ...
        """
        Get the stream URL for a camera configuration.
        
        Args:
            config_id: The ID of the camera configuration
        
        Returns:
            tuple: (stream_url, error, message)
        """

    def handle_response(self: Any, response: Dict, success_message: str, failure_message: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Handle API response and return standardized tuple.
        """

    def list_camera_configs(self: Any, page: int = 1, limit: int = 10, search: str = None, group_id: str = None) -> Tuple[Optional[List[Dict]], Optional[str], str]: ...
        """
        List all camera configs for a specific deployment.
        
        Returns:
            tuple: (camera_configs, error, message)
        """

    def update_camera(self: Any, camera_id: str, camera_config: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update an existing camera configuration.
        
        Args:
            camera_id: The ID of the camera to update
            camera_config: CameraConfig object with updated configuration
        
        Returns:
            tuple: (result, error, message)
        """

    def update_camera_config(self: Any, config_id: str, config: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Legacy method - use update_camera instead.
        """

    def update_camera_group(self: Any, group_id: str, group: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update an existing camera group.
        
        Args:
            group_id: The ID of the camera group to update
            group: CameraGroup object with updated configuration
        
        Returns:
            tuple: (result, error, message)
        """

class StreamSettings:
    """
    Stream settings data class for camera configurations.
    
    Attributes:
        aspect_ratio: Aspect ratio of the camera (e.g., "16:9", "4:3")
        video_quality: Video quality setting (0-100)
        height: Video height in pixels
        width: Video width in pixels
        fps: Frames per second
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create a StreamSettings instance from API response data.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert the stream settings to a dictionary for API calls.
        """

