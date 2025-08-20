"""Auto-generated stub for module: inference_pipeline."""
from typing import Any, Dict, List, Optional, Set, Tuple

from camera_manager import CameraManager, Camera, CameraGroup, CameraGroupConfig, CameraConfig
from dataclasses import dataclass
from matrice_common.utils import handle_response
from streaming_gateway_manager import StreamingGatewayManager, StreamingGateway, StreamingGatewayConfig
import time

# Classes
class Aggregator:
    """
    Aggregator configuration for inference pipelines.
    
    Attributes:
        id: Unique identifier for the aggregator (MongoDB ObjectID)
        action_id: ID of the associated action (MongoDB ObjectID)
        status: Status of the aggregator
        is_running: Whether the aggregator is currently running
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create an Aggregator instance from API response data.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert the aggregator to a dictionary for API calls.
        """

class ApplicationDeployment:
    """
    Application deployment configuration for inference pipelines.
    
    Attributes:
        application_id: ID of the application
        application_version: Version of the application
        deployment_id: ID of the deployment (optional)
        status: Status of the application deployment
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create an ApplicationDeployment instance from API response data.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert the application deployment to a dictionary for API calls.
        """

class InferencePipeline:
    """
    Inference pipeline instance for managing a specific ML model deployment orchestration.
    
    This class provides methods to start, stop, monitor, and manage a single inference pipeline
    that orchestrates the deployment and execution of machine learning models for
    real-time data processing and inference.
    
    Example:
        Working with a specific inference pipeline:
        ```python
        from matrice import Session
        from matrice_inference.deployment.inference_pipeline import InferencePipeline
    
        session = Session(account_number="...", access_key="...", secret_key="...")
    
        # Load existing pipeline
        pipeline = InferencePipeline(session, pipeline_id="664ab1df23abcf1c33123456")
    
        # Start the pipeline
        result, error, message = pipeline.start()
        if not error:
            print("Pipeline started successfully")
    
        # Check status
        status, error, message = pipeline.get_status()
        if not error:
            print(f"Pipeline status: {status}")
    
        # Stop the pipeline
        result, error, message = pipeline.stop()
        ```
    """

    def __init__(self: Any, session: Any, config: Any = None, pipeline_id: str = None) -> None: ...
        """
        Initialize an InferencePipeline instance.
        
        Args:
            session: Session object containing RPC client for API communication
            config: InferencePipelineConfig object (for new pipelines)
            pipeline_id: The ID of an existing pipeline to load
        """

    def add_camera_groups_to_streaming_gateway(self: Any, gateway_id: str, camera_group_ids: List[str]) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Add camera groups to a streaming gateway.
        
        Args:
            gateway_id: The ID of the streaming gateway
            camera_group_ids: List of camera group IDs to add
        
        Returns:
            tuple: (result, error, message)
        """

    def add_cameras_to_group(self: Any, group_id: str, camera_configs: List[CameraConfig]) -> Tuple[Optional[List['Camera']], Optional[str], str]: ...
        """
        Add multiple cameras to a camera group in this inference pipeline.
        
        Args:
            group_id: The ID of the camera group
            camera_configs: List of CameraConfig objects
        
        Returns:
            tuple: (camera_instances, error, message)
        """

    def aggregators(self: Any) -> List[Aggregator]: ...
        """
        Get the pipeline aggregators.
        """

    def aggregators(self: Any, value: List[Aggregator]) -> Any: ...
        """
        Set the pipeline aggregators.
        """

    def applications(self: Any) -> List[ApplicationDeployment]: ...
        """
        Get the pipeline applications.
        """

    def applications(self: Any, value: List[ApplicationDeployment]) -> Any: ...
        """
        Set the pipeline applications.
        """

    def config(self: Any) -> Optional[InferencePipelineConfig]: ...
        """
        Get the pipeline configuration.
        """

    def config(self: Any, value: Any) -> Any: ...
        """
        Set the pipeline configuration.
        """

    def create_camera(self: Any, camera_config: Any) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Create a camera for this inference pipeline.
        
        Args:
            camera_config: CameraConfig object containing the camera configuration
        
        Returns:
            tuple: (camera_instance, error, message)
        """

    def create_camera_group(self: Any, group: Any) -> Tuple[Optional['CameraGroup'], Optional[str], str]: ...
        """
        Create a camera group for this inference pipeline.
        
        Args:
            group: CameraGroupConfig object containing the group configuration
        
        Returns:
            tuple: (camera_group_instance, error, message)
        """

    def create_streaming_gateway(self: Any, gateway_config: Any) -> Tuple[Optional['StreamingGateway'], Optional[str], str]: ...
        """
        Create a streaming gateway for this inference pipeline.
        
        Args:
            gateway_config: StreamingGatewayConfig object containing the gateway configuration
        
        Returns:
            tuple: (streaming_gateway, error, message)
        """

    def delete(self: Any, force: bool = False) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete this inference pipeline and clean up all associated resources.
        
        Args:
            force: Force delete even if active
        
        Returns:
            tuple: (result, error, message)
        """

    def delete_streaming_gateway(self: Any, gateway_id: str, force: bool = False) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete a streaming gateway by its ID.
        
        Args:
            gateway_id: The ID of the streaming gateway to delete
            force: Force delete even if active
        
        Returns:
            tuple: (result, error, message)
        """

    def deployment_ids(self: Any) -> List[str]: ...
        """
        Get the deployment IDs.
        """

    def description(self: Any) -> str: ...
        """
        Get the pipeline description.
        """

    def description(self: Any, value: str) -> Any: ...
        """
        Set the pipeline description.
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
        Get camera groups for this inference pipeline.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
        
        Returns:
            tuple: (camera_group_instances, error, message)
        """

    def get_cameras(self: Any, page: int = 1, limit: int = 10, search: str = None, group_id: str = None) -> Tuple[Optional[List['Camera']], Optional[str], str]: ...
        """
        Get cameras for this inference pipeline.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
            group_id: Optional filter by camera group ID
        
        Returns:
            tuple: (camera_instances, error, message)
        """

    def get_details(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Retrieve detailed information about this inference pipeline.
        
        Returns:
            tuple: (pipeline_details, error, message)
        """

    def get_status(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Retrieve the current status of this inference pipeline.
        
        Returns:
            tuple: (result, error, message)
        """

    def get_streaming_gateway_by_id(self: Any, gateway_id: str) -> Tuple[Optional['StreamingGateway'], Optional[str], str]: ...
        """
        Get a streaming gateway by its ID.
        
        Args:
            gateway_id: The ID of the streaming gateway to retrieve
        
        Returns:
            tuple: (streaming_gateway, error, message)
        """

    def get_streaming_gateways(self: Any, page: int = 1, limit: int = 10, search: str = None) -> Tuple[Optional[List['StreamingGateway']], Optional[str], str]: ...
        """
        Get streaming gateways for this inference pipeline.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
        
        Returns:
            tuple: (streaming_gateways, error, message)
        """

    def id(self: Any) -> Optional[str]: ...
        """
        Get the pipeline ID.
        """

    def name(self: Any) -> str: ...
        """
        Get the pipeline name.
        """

    def name(self: Any, value: str) -> Any: ...
        """
        Set the pipeline name.
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the pipeline configuration from the backend.
        """

    def remove_camera_groups_from_streaming_gateway(self: Any, gateway_id: str, camera_group_ids: List[str]) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Remove camera groups from a streaming gateway.
        
        Args:
            gateway_id: The ID of the streaming gateway
            camera_group_ids: List of camera group IDs to remove
        
        Returns:
            tuple: (result, error, message)
        """

    def save(self: Any, project_id: str = None) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Save this inference pipeline to the backend.
        
        Args:
            project_id: The ID of the project (optional if set in config)
        
        Returns:
            tuple: (result, error, message)
        """

    def start(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Start this inference pipeline for real-time processing.
        
        Returns:
            tuple: (result, error, message)
        """

    def status(self: Any) -> Optional[str]: ...
        """
        Get the pipeline status.
        """

    def stop(self: Any, force: bool = False) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Stop this inference pipeline and clean up resources.
        
        Args:
            force: Force stop even if active streams exist
        
        Returns:
            tuple: (result, error, message)
        """

    def update(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update this inference pipeline with the current configuration.
        
        Returns:
            tuple: (result, error, message)
        """

    def update_streaming_gateway(self: Any, gateway_id: str, gateway_config: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update an existing streaming gateway.
        
        Args:
            gateway_id: The ID of the streaming gateway to update
            gateway_config: StreamingGatewayConfig object with updated configuration
        
        Returns:
            tuple: (result, error, message)
        """

    def wait_for_active(self: Any, timeout: int = 300, poll_interval: int = 10) -> Tuple[bool, Optional[str], str]: ...
        """
        Wait for this pipeline to reach 'active' status.
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
        
        Returns:
            tuple: (is_active, error, message)
        """

    def wait_for_ready(self: Any, timeout: int = 300, poll_interval: int = 10) -> Tuple[bool, Optional[str], str]: ...
        """
        Wait for this pipeline to reach 'ready' status.
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
        
        Returns:
            tuple: (is_ready, error, message)
        """

class InferencePipelineConfig:
    """
    Inference pipeline configuration data class.
    
    Attributes:
        name: Name of the inference pipeline
        description: Description of the inference pipeline
        applications: List of application deployments
        aggregators: List of aggregators (optional)
        id: Unique identifier for the pipeline (MongoDB ObjectID)
        project_id: Project ID this pipeline belongs to
        user_id: User ID who created the pipeline
        status: Status of the pipeline
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create an InferencePipelineConfig instance from API response data.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert the inference pipeline config to a dictionary for API calls.
        """

class InferencePipelineManager:
    """
    Manager for inference pipeline operations.
    
    This class provides methods to create, list, and manage multiple inference pipelines
    within a project. It handles the overall management of inference pipelines while
    individual pipelines are managed through the InferencePipeline class.
    
    Example:
        Managing multiple inference pipelines:
        ```python
        from matrice import Session
        from matrice_inference.deployment.inference_pipeline import InferencePipelineManager, InferencePipelineConfig, ApplicationDeployment
    
        session = Session(account_number="...", access_key="...", secret_key="...")
        manager = InferencePipelineManager(session)
    
        # Create a new pipeline
        apps = [
            ApplicationDeployment(
                application_id="664ab1df23abcf1c33123456",
                application_version="v1.0"
            )
        ]
    
        config = InferencePipelineConfig(
            name="Multi-App Pipeline",
            description="Pipeline for multiple applications",
            applications=apps
        )
    
        pipeline, error, message = manager.create_inference_pipeline(config)
        if not error:
            print(f"Created pipeline: {pipeline.id}")
    
        # List all pipelines
        pipelines, error, message = manager.get_inference_pipelines()
        if not error:
            print(f"Found {len(pipelines)} pipelines")
        ```
    """

    def __init__(self: Any, session: Any, project_id: str = None) -> None: ...
        """
        Initialize the InferencePipelineManager.
        
        Args:
            session: Session object containing RPC client for API communication
            project_id: The ID of the project (optional, can be inferred from session)
        """

    def create_inference_pipeline(self: Any, config: Any, project_id: str = None) -> Tuple[Optional['InferencePipeline'], Optional[str], str]: ...
        """
        Create a new inference pipeline.
        
        Args:
            config: InferencePipelineConfig object containing the pipeline configuration
            project_id: The ID of the project (optional, uses manager's project_id if not provided)
        
        Returns:
            tuple: (inference_pipeline_instance, error, message)
        """

    def get_inference_pipeline_by_id(self: Any, pipeline_id: str) -> Tuple[Optional['InferencePipeline'], Optional[str], str]: ...
        """
        Get an inference pipeline by its ID.
        
        Args:
            pipeline_id: The ID of the inference pipeline to retrieve
        
        Returns:
            tuple: (inference_pipeline_instance, error, message)
        """

    def get_inference_pipelines(self: Any, page: int = 1, limit: int = 10, search: str = None, project_id: str = None) -> Tuple[Optional[List['InferencePipeline']], Optional[str], str]: ...
        """
        Get all inference pipelines for a project.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
            project_id: The ID of the project (optional, uses manager's project_id if not provided)
        
        Returns:
            tuple: (inference_pipeline_instances, error, message)
        """

