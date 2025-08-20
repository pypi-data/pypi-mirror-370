"""Auto-generated stub for module: deployment."""
from typing import Any, Dict, List, Optional, Tuple

from camera_manager import CameraManager, CameraGroupConfig, CameraConfig, Camera, CameraGroup
from datetime import datetime, timedelta
from matrice_common.utils import handle_response, get_summary
from streaming_gateway_manager import StreamingGatewayManager, StreamingGatewayConfig, StreamingGateway
import json
import sys
import time

# Classes
class Deployment:
    """
    Class to manage deployment-related operations within a project.
    
    The `Deployment` class initializes with a given session and deployment details,
    allowing users to access and manage the deployment attributes such as status,
    configuration, and associated project information.
    
    Parameters
    ----------
    session : object
        The session object containing project and RPC information.
    deployment_id : str, optional
        The ID of the deployment to manage. Default is None.
    deployment_name : str, optional
        The name of the deployment. Default is None.
    
    Attributes
    ----------
    session : object
        The session object for RPC communication.
    rpc : object
        The RPC interface for backend API communication.
    project_id : str
        The project ID associated with the deployment.
    deployment_id : str
        The unique ID of the deployment.
    deployment_name : str
        Name of the deployment.
    model_id : str
        ID of the model associated with the deployment.
    user_id : str
        User ID of the deployment owner.
    user_name : str
        Username of the deployment owner.
    action_id : str
        ID of the action associated with the deployment.
    auth_keys : list
        List of authorization keys for the deployment.
    runtime_framework : str
        Framework used for the runtime of the model in the deployment.
    model_input : dict
        Input format expected by the model.
    model_type : str
        Type of model deployed (e.g., classification, detection).
    model_output : dict
        Output format of the deployed model.
    deployment_type : str
        Type of deployment (e.g., real-time, batch).
    suggested_classes : list
        Suggested classes for classification models.
    running_instances : list
        List of currently running instances.
    auto_shutdown : bool
        Whether the deployment has auto-shutdown enabled.
    auto_scale : bool
        Whether the deployment is configured for auto-scaling.
    gpu_required : bool
        Whether GPU is required for the deployment.
    status : str
        Current status of the deployment.
    hibernation_threshold : int
        Threshold for auto-hibernation in minutes.
    image_store_confidence_threshold : float
        Confidence threshold for storing images.
    image_store_count_threshold : int
        Count threshold for storing images.
    images_stored_count : int
        Number of images currently stored.
    bucket_alias : str
        Alias for the storage bucket associated with the deployment.
    credential_alias : str
        Alias for credentials used in the deployment.
    created_at : str
        Timestamp when the deployment was created.
    updated_at : str
        Timestamp when the deployment was last updated.
    compute_alias : str
        Alias of the compute resource associated with the deployment.
    is_optimized : bool
        Indicates whether the deployment is optimized.
    status_cards : list
        List of status cards related to the deployment.
    total_deployments : int or None
        Total number of deployments in the project.
    active_deployments : int or None
        Number of active deployments in the project.
    total_running_instances_count : int or None
        Total count of running instances in the project.
    hibernated_deployments : int or None
        Number of hibernated deployments.
    error_deployments : int or None
        Number of deployments with errors.
    camera_manager : CameraManager
        Manager for camera groups and configurations.
    streaming_gateway_manager : StreamingGatewayManager
        Manager for streaming gateways.
    
    Example
    -------
    >>> session = Session(account_number="account_number")
    >>> deployment = Deployment(session=session, deployment_id="deployment_id", deployment_name="MyDeployment")
    """

    def __init__(self: Any, session: Any, deployment_id: Any = None, deployment_name: Any = None) -> None: ...

    def add_camera_config(self: Any, config: Any) -> Any: ...
        """
        Legacy method - use create_camera instead.
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
        Add multiple cameras to a camera group in this deployment.
        
        Args:
            group_id: The ID of the camera group
            camera_configs: List of CameraConfig objects
        
        Returns:
            tuple: (camera_instances, error, message)
        """

    def create_auth_key(self: Any, expiry_days: Any) -> Any: ...
        """
        Create a new authentication key for the deployment, valid for the specified number of days.
        The `deployment_id` and `project_id` must be set during initialization.
        
        Parameters
        ----------
        expiry_days : int
            The number of days before the authentication key expires.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with details of the created authentication key,
            including keys such as:
                - `authKey` (str): The newly created authentication key.
                - `expiryDate` (str): Expiration date of the key.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Examples
        --------
        >>> auth_key, err, msg = deployment.create_auth_key(30)
        >>> if err:
        >>>     pprint(err)
        >>> else:
        >>>     pprint(auth_key)
        """

    def create_camera(self: Any, camera_config: Any) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Create a new camera for this deployment.
        
        Args:
            camera_config: CameraConfig object containing the camera configuration
        
        Returns:
            tuple: (camera_instance, error, message)
        """

    def create_camera_group(self: Any, group: Any) -> Tuple[Optional['CameraGroup'], Optional[str], str]: ...
        """
        Create a new camera group for this deployment.
        
        Args:
            group: CameraGroup object containing the group configuration
        
        Returns:
            tuple: (camera_group_instance, error, message)
        """

    def create_dataset(self: Any, dataset_name: Any, is_unlabeled: Any, source: Any, source_url: Any, is_public: Any, dataset_description: Any = '', version_description: Any = '') -> Any: ...
        """
        Create a new dataset from a deployment. Only zip files are supported for upload,
        and the deployment ID must be set for this operation.
        
        Parameters
        ----------
        dataset_name : str
            The name of the new dataset.
        is_unlabeled : bool
            Indicates whether the dataset is unlabeled.
        source : str
            The source of the dataset (e.g., "aws").
        source_url : str
            The URL of the dataset to be created.
        is_public : bool
            Specifies if the dataset is public.
        dataset_description : str, optional
            A description for the dataset. Default is an empty string.
        version_description : str, optional
            A description for this version of the dataset. Default is an empty string.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with details of the dataset creation, structured as:
                - `datasetId` (str): ID of the created dataset.
                - `status` (str): Status of the dataset creation request.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Example
        -------
        >>> from pprint import pprint
        >>> resp, err, msg = deployment.create_dataset(
        ...     dataset_name="New Dataset",
        ...     is_unlabeled=False,
        ...     source="aws",
        ...     source_url="https://example.com/dataset.zip",
        ...     is_public=True,
        ...     dataset_description="Dataset description",
        ...     version_description="Version description"
        ... )
        >>> if err:
        ...     pprint(err)
        >>> else:
        ...     pprint(resp)
        """

    def create_streaming_gateway(self: Any, gateway_config: Any) -> Tuple[Optional['StreamingGateway'], Optional[str], str]: ...
        """
        Create a new streaming gateway for this deployment.
        
        Args:
            gateway_config: StreamingGatewayConfig object containing the gateway configuration
        
        Returns:
            tuple: (streaming_gateway, error, message)
        """

    def delete(self: Any) -> Any: ...
        """
        Delete the specified deployment.
        
        This method deletes the deployment identified by `deployment_id` from the backend system.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response confirming the deletion.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Raises
        ------
        SystemExit
            If `deployment_id` is not set.
        
        Examples
        --------
        >>> delete, err, msg = deployment.delete()
        >>> if err:
        >>>     pprint(err)
        >>> else:
        >>>     pprint(delete)
        """

    def delete_all_cameras(self: Any, confirm: bool = False) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete all cameras for this deployment.
        
        Args:
            confirm: Must be True to confirm bulk deletion
        
        Returns:
            tuple: (result, error, message)
        """

    def delete_auth_key(self: Any, auth_key: Any) -> Any: ...
        """
        Delete a specified authentication key for the current deployment.
        The `deployment_id` must be set during initialization.
        
        Parameters
        ----------
        auth_key : str
            The authentication key to be deleted.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response indicating the result of the delete operation.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Raises
        ------
        SystemExit
            If `deployment_id` is not set.
        
        Examples
        --------
        >>> delete_auth_key, err, msg = deployment.delete_auth_key("abcd1234")
        >>> if err:
        >>>     pprint(err)
        >>> else:
        >>>     pprint(delete_auth_key)
        """

    def delete_camera(self: Any, camera_id: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete a camera by its ID.
        
        Args:
            camera_id: The ID of the camera to delete
        
        Returns:
            tuple: (result, error, message)
        """

    def delete_camera_group(self: Any, group_id: str) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Delete a camera group by its ID.
        
        Args:
            group_id: The ID of the camera group to delete
        
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

    def get_camera_by_id(self: Any, camera_id: str) -> Tuple[Optional['Camera'], Optional[str], str]: ...
        """
        Get a camera by its ID.
        
        Args:
            camera_id: The ID of the camera to retrieve
        
        Returns:
            tuple: (camera_instance, error, message)
        """

    def get_camera_configs(self: Any, page: int = 1, limit: int = 10, search: str = None, group_id: str = None) -> Any: ...
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
        Get all camera groups for this deployment.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
        
        Returns:
            tuple: (camera_group_instances, error, message)
        """

    def get_cameras(self: Any, page: int = 1, limit: int = 10, search: str = None, group_id: str = None) -> Tuple[Optional[List['Camera']], Optional[str], str]: ...
        """
        Get all cameras for this deployment.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
            group_id: Optional filter by camera group ID
        
        Returns:
            tuple: (camera_instances, error, message)
        """

    def get_deployment_server(self: Any, model_train_id: Any, model_type: Any) -> Any: ...
        """
        Fetch information about the deployment server for a specific model.
        
        Parameters
        ----------
        model_train_id : str
            The ID of the model training instance.
        model_type : str
            The type of model (e.g., 'trained', 'exported').
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with details of the deployment server.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Examples
        --------
        >>> deployment_server, err, msg = deployment.get_deployment_server("train123", "trained")
        >>> if err:
        >>>     pprint(err)
        >>> else:
        >>>     pprint(deployment_server)
        """

    def get_prediction(self: Any, input_path: Any = None, auth_key: Any = '', input_url: Any = None, extra_params: Any = {}) -> Any: ...
        """
        Fetch model predictions for a given image using a deployment.
        
        This method sends an image to the deployment for prediction. Either `deployment_id`
        or `deployment_name` must be provided in the instance to locate the deployment.
        
        Parameters
        ----------
        input_path : str
            The path to the input for prediction.
        auth_key : str
            The authentication key required for authorizing the prediction request.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with the prediction results, structured as:
                - `predictions` (list of dict): Each entry contains:
                    - `class` (str): The predicted class label.
                    - `confidence` (float): Confidence score of the prediction.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the prediction request.
        
        Raises
        ------
        ValueError
            If `auth_key` is not provided or if neither `deployment_id` nor `deployment_name` is
                set.
        
        Examples
        --------
        >>> from pprint import pprint
        >>> result, error, message = deployment.get_prediction(
        ...     input_path="/path/to/input.jpg",
        ...     auth_key="auth123"
        ... )
        >>> if error:
        ...     pprint(error)
        >>> else:
        ...     pprint(result)
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
        Get all streaming gateways for this deployment.
        
        Args:
            page: Page number for pagination
            limit: Items per page
            search: Optional search term
        
        Returns:
            tuple: (streaming_gateways, error, message)
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the instance by reinstantiating it with the previous values.
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

    def rename(self: Any, updated_name: Any) -> Any: ...
        """
        Update the deployment name for the current deployment.
        
        Parameters
        ----------
        updated_name : str
            The new name for the deployment.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with details of the rename operation.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Raises
        ------
        SystemExit
            If `deployment_id` is not set.
        
        Examples
        --------
        >>> from pprint import pprint
        >>> deployment = Deployment(session, deployment_id="1234")
        >>> rename, err, msg = deployment.rename("NewDeploymentName")
        >>> if err:
        >>>     pprint(err)
        >>> else:
        >>>     pprint(rename)
        """

    def request_count_monitor(self: Any, start_date: Any, end_date: Any, granularity: Any = 'second') -> Any: ...
        """
        Monitor the count of requests within a specified time range and granularity for the current
            deployment.
        
        Parameters
        ----------
        start_date : str
            The start date of the monitoring period in ISO format (e.g., "YYYY-MM-DDTHH:MM:SSZ").
        end_date : str
            The end date of the monitoring period in ISO format.
        granularity : str, optional
            The time granularity for the request count (e.g., "second", "minute")
            . Default is "second".
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with the request count details, structured as:
                - `counts` (list of dict): Each entry contains:
                    - `timestamp` (str): The timestamp of the request count.
                    - `count` (int): The number of requests at that timestamp.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Examples
        --------
        >>> start = "2024-01-28T18:30:00.000Z"
        >>> end = "2024-02-29T10:11:27.000Z"
        >>> count_monitor, error, message = deployment.request_count_monitor(start, end)
        >>> if error:
        >>>     pprint(error)
        >>> else:
        >>>     pprint(count_monitor)
        """

    def request_latency_monitor(self: Any, start_date: Any, end_date: Any, granularity: Any = 'second') -> Any: ...
        """
        Monitor the request latency within a specified time range and granularity for the current
            deployment.
        
        Parameters
        ----------
        start_date : str
            The start date of the monitoring period in ISO format (e.g., "YYYY-MM-DDTHH:MM:SSZ").
        end_date : str
            The end date of the monitoring period in ISO format.
        granularity : str, optional
            The time granularity for latency tracking (e.g., "second", "minute"). Default is
                "second".
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with latency details, structured as:
                - `latencies` (list of dict): Each entry contains:
                    - `timestamp` (str): The timestamp of the latency record.
                    - `avg_latency` (float): The average latency in seconds for the requests at
                        that timestamp.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Examples
        --------
        >>> from pprint import pprint
        >>> start = "2024-01-28T18:30:00.000Z"
        >>> end = "2024-02-29T10:11:27.000Z"
        >>> result, error, message = deployment.request_latency_monitor(start, end)
        >>> if error:
        >>>     pprint(error)
        >>> else:
        >>>     pprint(result)
        """

    def request_total_monitor(self: Any) -> Any: ...
        """
        Monitor the total number of requests for the current deployment.
        
        This method checks the total request count for a deployment by its `deployment_id`.
        If `deployment_id` is not set, it attempts to fetch it using `deployment_name`.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with the total request count.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Raises
        ------
        SystemExit
            If both `deployment_id` and `deployment_name` are not set.
        
        Examples
        --------
        >>> from pprint import pprint
        >>> monitor, error, message = deployment.request_total_monitor()
        >>> if error:
        >>>     pprint(error)
        >>> else:
        >>>     pprint(monitor)
        """

    def set_auth_key(self: Any, auth_key: Any) -> Any: ...

    def update_camera(self: Any, camera_id: str, camera_config: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update an existing camera.
        
        Args:
            camera_id: The ID of the camera to update
            camera_config: CameraConfig object with updated configuration
        
        Returns:
            tuple: (result, error, message)
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

    def update_streaming_gateway(self: Any, gateway_id: str, gateway_config: Any) -> Tuple[Optional[Dict], Optional[str], str]: ...
        """
        Update an existing streaming gateway.
        
        Args:
            gateway_id: The ID of the streaming gateway to update
            gateway_config: StreamingGatewayConfig object with updated configuration
        
        Returns:
            tuple: (result, error, message)
        """

    def wakeup_deployment_server(self: Any) -> Any: ...
        """
        Wake up the deployment server associated with the current deployment.
        The `deployment_id` must be set during initialization.
        
        Returns
        -------
        tuple
            A tuple containing three elements:
            - dict: The API response with details of the wake-up operation.
            - str or None: Error message if an error occurred, otherwise None.
            - str: Status message indicating success or failure of the API call.
        
        Raises
        ------
        SystemExit
            If `deployment_id` is not set.
        
        Examples
        --------
        >>> wakeup, err, msg = deployment.wakeup_deployment_server()
        >>> if err:
        >>>     pprint(err)
        >>> else:
        >>>     pprint(wakeup)
        """

