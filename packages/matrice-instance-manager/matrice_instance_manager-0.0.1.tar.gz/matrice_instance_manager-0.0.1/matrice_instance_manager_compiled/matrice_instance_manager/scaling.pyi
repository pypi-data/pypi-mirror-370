"""Auto-generated stub for module: scaling."""
from typing import Any, Tuple

from matrice_common.utils import log_errors
import logging
import os

# Classes
class Scaling:
    """
    Class providing scaling functionality for compute instances.
    """

    def __init__(self: Any, session: Any, instance_id: Any = None) -> None: ...
        """
        Initialize Scaling instance.
        
                Args:
                    session: Session object for making RPC calls
                    instance_id: ID of the compute instance
        
                Raises:
                    Exception: If instance_id is not provided
        """

    def add_account_compute_instance(self: Any, account_number: Any, alias: Any, service_provider: Any, instance_type: Any, shut_down_time: Any, lease_type: Any, launch_duration: Any) -> Any: ...
        """
        Add a compute instance for an account.
        
                Args:
                    account_number: Account number
                    alias: Instance alias
                    service_provider: Cloud service provider
                    instance_type: Type of instance
                    shut_down_time: Time to shutdown
                    lease_type: Type of lease
                    launch_duration: Duration to launch
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def assign_jobs(self: Any, is_gpu: Any) -> Any: ...
        """
        Assign jobs to the instance.
        
                Args:
                    is_gpu: Whether instance has GPU
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def delete_account_compute(self: Any, account_number: Any, alias: Any) -> Any: ...
        """
        Delete a compute instance for an account.
        
                Args:
                    account_number: Account number
                    alias: Instance alias
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_action_details(self: Any, action_status_id: Any) -> Any: ...
        """
        Get details for a specific action.
        
                Args:
                    action_status_id: ID of the action status
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_all_instances_type(self: Any) -> Any: ...
        """
        Get all instance types.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_compute_details(self: Any) -> Any: ...
        """
        Get compute instance details.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_data_processing_image(self: Any) -> Any: ...
        """
        Get data processing image name.
        
                Returns:
                    Full image name including repository and tag
        """

    def get_docker_hub_credentials(self: Any) -> Any: ...
        """
        Get Docker Hub credentials.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_downscaled_ids(self: Any) -> Any: ...
        """
        Get IDs of downscaled instances.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_internal_api_key(self: Any, action_id: Any) -> Any: ...
        """
        Get internal API key.
        
                Args:
                    action_id: ID of the action
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_model_codebase(self: Any, model_family_id: Any) -> Any: ...
        """
        Get model codebase.
        
                Args:
                    model_family_id: ID of the model family
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_model_codebase_requirements(self: Any, model_family_id: Any) -> Any: ...
        """
        Get model codebase requirements.
        
                Args:
                    model_family_id: ID of the model family
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_model_codebase_script(self: Any, model_family_id: Any) -> Any: ...
        """
        Get model codebase script.
        
                Args:
                    model_family_id: ID of the model family
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_model_secret_keys(self: Any, secret_name: Any) -> Any: ...
        """
        Get model secret keys.
        
                Args:
                    secret_name: Name of the secret
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_open_port(self: Any) -> Any: ...
        """
        Get an available open port.
        
                Returns:
                    Port number if available, None otherwise
        """

    def get_open_ports_config(self: Any) -> Any: ...
        """
        Get open ports configuration.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_shutdown_details(self: Any) -> Any: ...
        """
        Get shutdown details for the instance.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_tasks_details(self: Any) -> Any: ...
        """
        Get task details for the instance.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def get_user_access_key_pair(self: Any, user_id: Any) -> Any: ...
        """
        Get user access key pair.
        
                Args:
                    user_id: ID of the user
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def handle_response(self: Any, resp: Any, success_message: Any, error_message: Any) -> Any: ...
        """
        Helper function to handle API response.
        
                Args:
                    resp: Response from API call
                    success_message: Message to log on success
                    error_message: Message to log on error
        
                Returns:
                    Tuple of (data, error, message)
        """

    def restart_account_compute(self: Any, account_number: Any, alias: Any) -> Any: ...
        """
        Restart a compute instance for an account.
        
                Args:
                    account_number: Account number
                    alias: Instance alias
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def stop_account_compute(self: Any, account_number: Any, alias: Any) -> Any: ...
        """
        Stop a compute instance for an account.
        
                Args:
                    account_number: Account number
                    alias: Instance alias
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def stop_instance(self: Any) -> Any: ...
        """
        Stop the compute instance.
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def update_action(self: Any, id: Any = '', step_code: Any = '', action_type: Any = '', status: Any = '', sub_action: Any = '', status_description: Any = '', service: Any = '', job_params: Any = None) -> Any: ...
        """
        Update an action.
        
                Args:
                    id: ID of the action
                    step_code: Code indicating step in process
                    action_type: Type of action
                    status: Status to update
                    sub_action: Sub-action details
                    status_description: Description of the status
                    service: Service name
                    job_params: Parameters for the job
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def update_action_docker_logs(self: Any, action_record_id: Any, log_content: Any) -> Any: ...
        """
        Update docker logs for an action.
        
                Args:
                    action_record_id: ID of the action record
                    log_content: Content of docker logs
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def update_action_status(self: Any, service_provider: Any = '', action_record_id: Any = '', isRunning: Any = True, status: Any = '', docker_start_time: Any = None, action_duration: Any = 0, cpuUtilisation: Any = 0.0, gpuUtilisation: Any = 0.0, memoryUtilisation: Any = 0.0, gpuMemoryUsed: Any = 0, createdAt: Any = None, updatedAt: Any = None) -> Any: ...
        """
        Update status of an action.
        
                Args:
                    service_provider: Provider of the service
                    action_record_id: ID of the action record
                    isRunning: Whether action is running
                    status: Status of the action
                    docker_start_time: Start time of docker container
                    action_duration: Duration of the action
                    cpuUtilisation: CPU utilization percentage
                    gpuUtilisation: GPU utilization percentage
                    memoryUtilisation: Memory utilization percentage
                    gpuMemoryUsed: GPU memory used
                    createdAt: Creation timestamp
                    updatedAt: Last update timestamp
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def update_available_resources(self: Any, availableCPU: Any = 0, availableGPU: Any = 0, availableMemory: Any = 0, availableGPUMemory: Any = 0) -> Any: ...
        """
        Update available resources for the instance.
        
                Args:
                    availableCPU: Available CPU cores
                    availableGPU: Available GPU units
                    availableMemory: Available memory in bytes
                    availableGPUMemory: Available GPU memory in bytes
        
                Returns:
                    Tuple of (data, error, message) from API response
        """

    def update_jupyter_token(self: Any, token: Any = '') -> Any: ...

    def update_status(self: Any, action_record_id: Any, action_type: Any, service_name: Any, stepCode: Any, status: Any, status_description: Any) -> None: ...
        """
        Update status of an action.
        
                Args:
                    action_record_id: ID of the action record
                    action_type: Type of action
                    service_name: Name of the service
                    stepCode: Code indicating step in process
                    status: Status to update
                    status_description: Description of the status
        """

