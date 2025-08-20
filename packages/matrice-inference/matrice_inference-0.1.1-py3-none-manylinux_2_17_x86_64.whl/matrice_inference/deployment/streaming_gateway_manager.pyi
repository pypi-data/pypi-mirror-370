"""Auto-generated stub for module: streaming_gateway_manager."""
from typing import Any, Dict, List, Optional, Set, Tuple

from dataclasses import dataclass, asdict
import logging

# Classes
class StreamingGateway:
    """
    Streaming gateway instance class for managing individual streaming gateways.
    
    This class represents a single streaming gateway and provides methods to manage
    its configuration, camera groups, and operational status.
    
    Example:
        Basic usage:
        ```python
        from matrice import Session
        from matrice_inference.deployment.streaming_gateway_manager import StreamingGateway, StreamingGatewayConfig
    
        session = Session(account_number="...", access_key="...", secret_key="...")
    
        # Create gateway config
        config = StreamingGatewayConfig(
            name="Main Gateway",
            description="Primary streaming gateway",
            camera_group_ids=["group1", "group2"]
        )
    
        # Create gateway instance
        gateway = StreamingGateway(session, config)
    
        # Save to backend
        result, error, message = gateway.save()
        if not error:
            print(f"Gateway created with ID: {gateway.id}")
    
        # Update configuration
        gateway.description = "Updated description"
        result, error, message = gateway.update()
        ```
    """

    def __init__(self: Any, session: Any, config: Any = None, gateway_id: str = None) -> None: ...
        """
        Initialize a StreamingGateway instance.
        
        Args:
            session: Session object containing RPC client for API communication
            config: StreamingGatewayConfig object (for new gateways)
            gateway_id: ID of existing gateway to load (mutually exclusive with config)
        """

    def add_camera_groups(self: Any, camera_group_ids: List[str]) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Add camera groups to this gateway.
        
        Args:
            camera_group_ids: List of camera group IDs to add
        
        Returns:
            tuple: (result, error, message)
        """

    def camera_group_ids(self: Any) -> List[str]: ...
        """
        Get the camera group IDs.
        """

    def camera_group_ids(self: Any, value: List[str]) -> Any: ...
        """
        Set the camera group IDs.
        """

    def delete(self: Any, force: bool = False) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete the gateway from the backend.
        
        Args:
            force: Force delete even if active
        
        Returns:
            tuple: (result, error, message)
        """

    def description(self: Any) -> Optional[str]: ...
        """
        Get the gateway description.
        """

    def description(self: Any, value: str) -> Any: ...
        """
        Set the gateway description.
        """

    def id(self: Any) -> Optional[str]: ...
        """
        Get the gateway ID.
        """

    def id_service(self: Any) -> Optional[str]: ...
        """
        Get the service ID (deployment or inference pipeline ID).
        """

    def id_service(self: Any, value: str) -> Any: ...
        """
        Set the service ID (deployment or inference pipeline ID).
        """

    def name(self: Any) -> str: ...
        """
        Get the gateway name.
        """

    def name(self: Any, value: str) -> Any: ...
        """
        Set the gateway name.
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the gateway configuration from the backend.
        """

    def remove_camera_groups(self: Any, camera_group_ids: List[str]) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Remove camera groups from this gateway.
        
        Args:
            camera_group_ids: List of camera group IDs to remove
        
        Returns:
            tuple: (result, error, message)
        """

    def save(self: Any, service_id: str = None) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Save the gateway configuration to the backend (create new).
        
        Args:
            service_id: The deployment or inference pipeline ID to associate with
        
        Returns:
            tuple: (result, error, message)
        """

    def status(self: Any) -> Optional[str]: ...
        """
        Get the gateway status.
        """

    def update(self: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update the gateway configuration in the backend.
        
        Returns:
            tuple: (result, error, message)
        """

class StreamingGatewayConfig:
    """
    Streaming gateway configuration data class.
    
    Attributes:
        id: Unique identifier for the streaming gateway (MongoDB ObjectID)
        id_service: Deployment ID this gateway belongs to (MongoDB ObjectID)
        name: Name of the streaming gateway
        description: Description of the streaming gateway
        camera_group_ids: List of camera group IDs associated with this gateway
        status: Status of the streaming gateway (e.g., "active", "inactive")
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def from_dict(cls: Any, data: Dict) -> Any: ...
        """
        Create a StreamingGatewayConfig instance from API response data.
        """

    def to_dict(self: Any) -> Dict: ...
        """
        Convert the streaming gateway config to a dictionary for API calls.
        """

class StreamingGatewayManager:
    """
    Streaming gateway manager client for handling streaming gateway configurations in deployments.
    
    This class provides methods to create, read, update, and delete streaming gateway configurations
    that manage collections of camera groups for efficient video processing and distribution.
    
    Example:
        Basic usage:
        ```python
        from matrice import Session
        from matrice_inference.deployment.streaming_gateway_manager import StreamingGatewayManager, StreamingGatewayConfig
    
        session = Session(account_number="...", access_key="...", secret_key="...")
        gateway_manager = StreamingGatewayManager(session, service_id="deployment_id")
    
        # Create a streaming gateway config
        config = StreamingGatewayConfig(
            name="Main Streaming Gateway",
            description="Primary gateway for building A camera groups",
            camera_group_ids=["group1_id", "group2_id"]
        )
    
        # Create gateway through manager
        gateway, error, message = gateway_manager.create_streaming_gateway(config)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Streaming gateway created: {gateway.name}")
    
        # Get all gateways for a deployment
        gateways, error, message = gateway_manager.get_streaming_gateways()
        if not error:
            for gateway in gateways:
                print(f"Gateway: {gateway.name} - {len(gateway.camera_group_ids)} camera groups")
        ```
    """

    def __init__(self: Any, session: Any, service_id: str = None) -> None: ...
        """
        Initialize the StreamingGatewayManager client.
        
        Args:
            session: Session object containing RPC client for API communication
            service_id: The ID of the deployment or the ID of the inference pipeline
        """

    def create_streaming_gateway(self: Any, config: Any) -> Tuple[Optional['StreamingGateway'], Optional[str], str]: ...
        """
        Create a new streaming gateway from configuration.
        
        Args:
            config: StreamingGatewayConfig object containing the gateway configuration
        
        Returns:
            tuple: (streaming_gateway, error, message)
                - streaming_gateway: StreamingGateway instance if successful, None otherwise
                - error: Error message if failed, None otherwise
                - message: Status message
        """

    def get_streaming_gateway_by_id(self: Any, gateway_id: str) -> Tuple[StreamingGateway, Optional[str], str]: ...
        """
        Get a streaming gateway by its ID.
        
        Args:
            gateway_id: The ID of the streaming gateway to retrieve
        
        Returns:
            tuple: (streaming_gateway, error, message)
        """

    def get_streaming_gateways(self: Any, page: int = 1, limit: int = 10, search: str = None) -> Tuple[Optional[List['StreamingGateway']], Optional[str], str]: ...
        """
        Get all streaming gateways for a specific deployment.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
        
        Returns:
            tuple: (streaming_gateways, error, message)
        """

    def handle_response(self: Any, response: Dict, success_message: str, failure_message: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Handle API response and return standardized tuple.
        """

