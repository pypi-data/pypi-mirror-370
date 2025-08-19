"""Auto-generated stubs for package: matrice_instance_manager."""
from typing import Any, Dict, List, Optional, Set, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime
from datetime import datetime, timezone
from matrice.docker_utils import check_docker
from matrice_common.session import Session
from matrice_common.utils import log_errors
from matrice_instance_manager.action_instance import ActionInstance
from matrice_instance_manager.actions_manager import ActionsManager
from matrice_instance_manager.actions_scaledown_manager import ActionsScaleDownManager
from matrice_instance_manager.instance_utils import get_gpu_with_sufficient_memory_for_action, get_decrypted_access_key_pair, get_max_file_system
from matrice_instance_manager.instance_utils import get_instance_info, cleanup_docker_storage, get_cpu_memory_usage, get_gpu_memory_usage, get_mem_usage, get_gpu_with_sufficient_memory_for_action, get_max_file_system, has_gpu
from matrice_instance_manager.instance_utils import get_instance_info, get_decrypted_access_key_pair
from matrice_instance_manager.instance_utils import has_gpu, get_gpu_info, calculate_time_difference
from matrice_instance_manager.instance_utils import has_gpu, get_mem_usage, cleanup_docker_storage
from matrice_instance_manager.resources_tracker import MachineResourcesTracker, ActionsResourcesTracker
from matrice_instance_manager.resources_tracker import ResourcesTracker, MachineResourcesTracker, ActionsResourcesTracker
from matrice_instance_manager.scaling import Scaling
from matrice_instance_manager.shutdown_manager import ShutdownManager
from matrice_instance_manager.task_utils import setup_workspace_and_run_task
import base64
import docker
import json
import logging
import os
import platform
import psutil
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import torch
import urllib.request
import zipfile

# Functions
# From action_instance
def augmentation_server_creation_execute(self: Any) -> Any: ...
    """
    Create Augmentation Server
    """

# From action_instance
def data_preparation_execute(self: Any) -> Any: ...
    """
    Execute data preparation task.
    """

# From action_instance
def data_processing_execute(self: Any) -> Any: ...
    """
    Execute data processing task.
    """

# From action_instance
def data_split_execute(self: Any) -> Any: ...
    """
    Execute data split task.
    """

# From action_instance
def dataset_annotation_execute(self: Any) -> Any: ...
    """
    Execute dataset annotation task.
    """

# From action_instance
def dataset_augmentation_execute(self: Any) -> Any: ...
    """
    Execute dataset augmentation task.
    """

# From action_instance
def deploy_aggregator_execute(self: Any) -> Any: ...
    """
    Execute deploy aggregator task.
    """

# From action_instance
def image_build_execute(self: Any) -> Any: ...
    """
    Execute image building task.
    """

# From action_instance
def kafka_setup_execute(self: Any) -> Any: ...
    """
    Execute kafka server task.
    """

# From action_instance
def model_deploy_execute(self: Any) -> Any: ...
    """
    Execute model deployment task.
    """

# From action_instance
def model_eval_execute(self: Any) -> Any: ...
    """
    Execute model evaluation task.
    """

# From action_instance
def model_export_execute(self: Any) -> Any: ...
    """
    Execute model export task.
    """

# From action_instance
def model_train_execute(self: Any) -> Any: ...
    """
    Execute model training task.
    """

# From action_instance
def resource_clone_execute(self: Any) -> Any: ...
    """
    Execute resource clone task.
    """

# From instance_utils
def calculate_time_difference(start_time_str: Any, finish_time_str: Any) -> Any: ...
    """
    Calculate time difference between start and finish times.
    
    Args:
        start_time_str (str): Start time string
        finish_time_str (str): Finish time string
    
    Returns:
        int: Time difference in seconds
    """

# From instance_utils
def check_public_port_exposure(port: Any) -> Any: ...
    """
    Check if port is publicly accessible.
    
    Args:
        port (int): Port number to check
    
    Returns:
        bool: True if port is publicly accessible
    """

# From instance_utils
def cleanup_docker_storage() -> Any: ...
    """
    Clean up Docker storage if space is low.
    """

# From instance_utils
def get_cpu_memory_usage() -> Any: ...
    """
    Get CPU memory usage.
    
    Returns:
        float: Memory usage between 0 and 1
    """

# From instance_utils
def get_decrypted_access_key_pair(enc_access_key: Any, enc_secret_key: Any, encryption_key: Any = '') -> Any: ...
    """
    Get decrypted access key pair.
    
    Args:
        enc_access_key (str): Encrypted access key
        enc_secret_key (str): Encrypted secret key
        encryption_key (str): Encryption key
    
    Returns:
        tuple: (access_key, secret_key) strings
    """

# From instance_utils
def get_disk_space_usage() -> Any: ...
    """
    Get disk space usage for all filesystems.
    
    Returns:
        list: List of disk usage information dictionaries
    """

# From instance_utils
def get_docker_disk_space_usage() -> Any: ...
    """
    Get disk space usage for Docker storage.
    
    Returns:
        dict: Docker disk usage information
    """

# From instance_utils
def get_encrypted_access_key_pair(access_key: Any, secret_key: Any, encryption_key: Any = '') -> Any: ...
    """
    Get encrypted access key pair.
    
    Args:
        access_key (str):  access key
        secret_key (str):  secret key
        encryption_key (str): Encryption key
    
    Returns:
        tuple: (encrypted_access_key, encrypted_secret_key) strings
    """

# From instance_utils
def get_gpu_info() -> Any: ...
    """
    Get GPU information.
    
    Returns:
        list: GPU information strings
    """

# From instance_utils
def get_gpu_memory_usage() -> Any: ...
    """
    Get GPU memory usage percentage.
    
    Returns:
        float: Memory usage between 0 and 1
    """

# From instance_utils
def get_gpu_with_sufficient_memory_for_action(action_details: Any) -> Any: ...
    """
    Get GPUs with sufficient memory for action.
    
    Args:
        action_details (dict): Action details
    
    Returns:
        list: List of GPU indices
    
    Raises:
        ValueError: If insufficient GPU memory
    """

# From instance_utils
def get_instance_id() -> str: ...
    """
    Get instance ID.
    
    Returns:
        str: Instance ID or empty string
    """

# From instance_utils
def get_instance_info() -> Any: ...
    """
    Get instance provider and ID information.
    
    Returns:
        tuple: (service_provider, instance_id) strings
    """

# From instance_utils
def get_max_file_system() -> Any: ...
    """
    Get filesystem with maximum available space.
    
    Returns:
        str: Path to filesystem with most space or None
    """

# From instance_utils
def get_mem_usage() -> Any: ...
    """
    Get memory usage for either GPU or CPU.
    
    Returns:
        float: Memory usage between 0 and 1
    """

# From instance_utils
def get_required_gpu_memory(action_details: Any) -> Any: ...
    """
    Get required GPU memory from action details.
    
    Args:
        action_details (dict): Action details
    
    Returns:
        int: Required GPU memory
    """

# From instance_utils
def get_single_gpu_with_sufficient_memory_for_action(action_details: Any) -> Any: ...
    """
    Get single GPU with sufficient memory.
    
    Args:
        action_details (dict): Action details
    
    Returns:
        list: List with single GPU index
    
    Raises:
        ValueError: If no GPU has sufficient memory
    """

# From instance_utils
def has_gpu() -> bool: ...
    """
    Check if the system has a GPU.
    
    Returns:
        bool: True if GPU is present, False otherwise
    """

# From instance_utils
def is_allowed_gpu_device(gpu_index: Any) -> Any: ...
    """
    Check if GPU device is allowed.
    
    Args:
        gpu_index (int): GPU device index
    
    Returns:
        bool: True if GPU is allowed
    """

# From instance_utils
def is_docker_running() -> Any: ...
    """
    Check if Docker is running.
    
    Returns:
        bool: True if Docker containers are running
    """

# From instance_utils
def prune_docker_images() -> Any: ...
    """
    Prune Docker images.
    """

# From task_utils
def setup_workspace_and_run_task(work_fs: Any, action_id: Any, model_codebase_url: Any, model_codebase_requirements_url: Any) -> Any: ...
    """
    Set up workspace and run task with provided parameters.
    
        Args:
            work_fs: Working filesystem path
            action_id: Unique identifier for the action
            model_codebase_url: URL to download model codebase from
            model_codebase_requirements_url: URL to download requirements from
    
        Returns:
            None
    """

# Classes
# From action_instance
class ActionInstance:
    """
    Base class for tasks that run in Action containers.
    """

    def __init__(self: Any, scaling: Any, action_info: dict) -> None: ...
        """
        Initialize an action instance.
        
                Args:
                    scaling (Scaling): Scaling service instance
                    action_info (dict): Action information dictionary
        """

    def execute(self: Any) -> Any: ...
        """
        Execute the task.
        """

    def get_action_details(self: Any) -> Any: ...
        """
        Get action details from scaling service.
        
                Returns:
                    dict: Action details if successful, None otherwise
        """

    def get_base_docker_cmd(self: Any, work_fs: Any = '', use_gpu: Any = '', mount_docker_sock: Any = False, action_id: Any = '', model_key: Any = '', extra_env_vars: Any = None, port_mapping: Any = None, destination_workspace_path: Any = '/usr/src/workspace', docker_workdir: Any = '') -> Any: ...
        """
        Build base Docker command with common options.
        
                Args:
                    work_fs (str): Work filesystem path
                    use_gpu (str): GPU configuration string
                    mount_docker_sock (bool): Whether to mount Docker socket
                    action_id (str): Action ID
                    model_key (str): Model key
                    extra_env_vars (dict): Additional environment variables
                    port_mapping (dict): Port mappings {host_port: container_port}
                    destination_workspace_path (str): Container workspace path
                    docker_workdir (str): Docker working directory
        
                Returns:
                    str: Base Docker command
        """

    def get_gpu_config(self: Any, action_details: Any) -> Any: ...
        """
        Get GPU configuration string based on available GPUs.
        
                Args:
                    action_details (dict): Action details containing GPU requirements
        
                Returns:
                    str: GPU configuration string
        """

    def get_hugging_face_token(self: Any, model_key: Any) -> Any: ...
        """
        Get Hugging Face token for specific model keys.
        
                Args:
                    model_key (str): Model key to check
        
                Returns:
                    str: Hugging Face token if available, empty string otherwise
        """

    def get_internal_api_key(self: Any, action_id: Any) -> Any: ...
        """
        Get internal API key for action.
        
                Args:
                    action_id (str): Action ID
        
                Returns:
                    str: Internal API key if available, empty string otherwise
        """

    def get_log_path(self: Any) -> Any: ...
        """
        Get log directory path, creating if needed.
        
                Returns:
                    str: Path to log directory
        """

    def is_running(self: Any) -> bool: ...
        """
        Check if task process is running.
        
                This method performs a thorough check to determine if the process is still running:
                1. Verifies that the process attribute exists and is not None
                2. Checks if the process has terminated using poll() method
                3. Additional safeguards against zombie processes
                4. Coordinates with log monitoring to ensure all logs are sent before cleanup
        
                Returns:
                    bool: True if process exists and is still running, False if process
                         does not exist or has terminated
        """

    def send_logs_continuously(self: Any) -> Any: ...
        """
        Continuously read and send logs from the log file to the scaling service.
        
                Enhanced version that tracks log position and handles graceful shutdown.
        """

    def setup_action_requirements(self: Any, action_details: Any, work_fs: Any = '', model_family: Any = '', action_id: Any = '') -> Any: ...
        """
        Setup action requirements.
        
                Args:
                    action_details (dict): Action details
                    work_fs (str): Work filesystem path
                    model_family (str): Model family name
                    action_id (str): Action ID
        
                Raises:
                    Exception: If setup fails
        """

    def start(self: Any, cmd: Any, log_name: Any) -> Any: ...
        """
        Start the process and log monitoring thread.
        
                Args:
                    cmd (str): Command to execute
                    log_name (str): Name for log file
        """

    def start_process(self: Any, cmd: Any, log_name: Any) -> Any: ...
        """
        Start the process and initialize logging.
        
                Args:
                    cmd (str): Command to execute
                    log_name (str): Name for log file
        
                Raises:
                    Exception: If process fails to start
        """

    def stop(self: Any) -> Any: ...
        """
        Stop the process and log monitoring thread.
        
                Enhanced version that ensures proper cleanup sequencing and log completion.
        """


# From actions_manager
class ActionsManager:
    """
    Class for managing actions.
    
        Attributes:
            current_actions (Dict[str, ActionInstance]): Dictionary of currently running actions.
            scaling (Scaling): Scaling service instance.
            memory_threshold (float): Memory usage threshold for processing actions.
            poll_interval (int): Interval between action polls in seconds.
            last_actions_check (int): Timestamp of last actions check.
    """

    def __init__(self: Any, scaling: Any) -> None: ...
        """
        Initialize an action manager.
        
                Args:
                    scaling (Scaling): Scaling service instance.
        """

    def fetch_actions(self: Any) -> List[Any]: ...
        """
        Poll for actions and process them if memory threshold is not exceeded.
        
                Returns:
                    List[Any]: List of fetched actions.
        """

    def get_current_actions(self: Any) -> Dict[str, ActionInstance]: ...
        """
        Get the current actions.
        
                This method:
                1. Purges any completed actions using purge_unwanted()
                2. Double-checks remaining actions to ensure they are truly running
                3. Provides detailed logging about current actions state
        
                Returns:
                    Dict[str, ActionInstance]: Current active actions
        """

    def process_action(self: Any, action: Dict[str, Any]) -> Optional[ActionInstance]: ...
        """
        Process the given action.
        
                Args:
                    action (Dict[str, Any]): Action details to process.
        
                Returns:
                    Optional[ActionInstance]: Processed action instance or None if failed.
        """

    def process_actions(self: Any) -> None: ...
        """
        Process fetched actions.
        """

    def purge_unwanted(self: Any) -> None: ...
        """
        Purge completed or failed actions.
        
                This method checks all actions in the current_actions dictionary and removes any that:
                1. Are explicitly reported as not running by the is_running() method
                2. Have invalid or corrupted process objects
        """

    def start_actions_manager(self: Any) -> None: ...
        """
        Start the actions manager main loop.
        """


# From actions_scaledown_manager
class ActionsScaleDownManager:
    """
    Class for managing container scale down operations.
    """

    def __init__(self: Any, scaling: Any) -> None: ...
        """
        Initialize the scale down manager.
        
                Args:
                    scaling (Scaling): Scaling service instance
        """

    def auto_scaledown_actions(self: Any) -> Any: ...
        """
        Start polling for containers that need to be scaled down and stop them.
        """


# From instance_manager
class InstanceManager:
    """
    Class for managing compute instances and their associated actions.
    
        Now includes auto streaming capabilities for specified deployment IDs.
    
        Attributes:
            session (Session): Session object for authentication.
            scaling (Scaling): Scaling service instance.
            current_actions (Dict[str, Any]): Dictionary of current actions.
            actions_manager (ActionsManager): Manager for handling actions.
            scale_down_manager (ActionsScaleDownManager): Manager for scaling down containers.
            shutdown_manager (ShutdownManager): Manager for handling shutdown operations.
            machine_resources_tracker (MachineResourcesTracker): Tracker for machine resources.
            actions_resources_tracker (ActionsResourcesTracker): Tracker for action resources.
            poll_interval (int): Interval between polling operations in seconds.
            encryption_key (Optional[str]): Key used for encryption.
    """

    def __init__(self: Any, matrice_access_key_id: str = '', matrice_secret_access_key: str = '', encryption_key: str = '', instance_id: str = '', service_provider: str = '', env: str = '', gpus: str = '', workspace_dir: str = 'matrice_workspace') -> None: ...
        """
        Initialize an instance manager.
        
                Args:
                    matrice_access_key_id (str): Access key ID for Matrice authentication.
                        Defaults to empty string.
                    matrice_secret_access_key (str): Secret access key for Matrice authentication.
                        Defaults to empty string.
                    encryption_key (str): Key used for encrypting sensitive data.
                        Defaults to empty string.
                    instance_id (str): Unique identifier for this compute instance.
                        Defaults to empty string.
                    service_provider (str): Cloud service provider being used.
                        Defaults to empty string.
                    env (str): Environment name (e.g. dev, prod).
                        Defaults to empty string.
                    gpus (str): GPU configuration string (e.g. "0,1").
                        Defaults to empty string.
                    workspace_dir (str): Directory for workspace files.
                        Defaults to "matrice_workspace".
        """

    def start(self: Any) -> Tuple[Optional[threading.Thread], Optional[threading.Thread]]: ...
        """
        Start the instance manager threads.
        
                Returns:
                    Tuple[Optional[threading.Thread], Optional[threading.Thread]]: A tuple containing
                        the instance manager thread and the actions manager thread.
        """

    def start_instance_manager(self: Any) -> None: ...
        """
        Run the instance manager loop.
        
                This method continuously runs the shutdown, scale-down, and resource tracking operations
                at regular intervals defined by poll_interval.
        """


# From prechecks
class Prechecks:
    """
    Class for running pre-checks before compute operations.
    """

    def __init__(self: Any, session: Any, instance_id: Optional[str] = None) -> None: ...
        """
        Initialize Prechecks.
        
                Args:
                    session: Session object for RPC calls
                    instance_id: Optional instance ID
        """

    def check_credentials(self: Any, access_key: Optional[str] = None, secret_key: Optional[str] = None) -> bool: ...
        """
        Check if access key and secret key are valid.
        
                Args:
                    access_key: Optional access key to validate
                    secret_key: Optional secret key to validate
        
                Returns:
                    bool: True if credentials are valid
        """

    def check_docker(self: Any) -> bool: ...
        """
        Check if docker is installed and working.
        
                Returns:
                    bool: True if docker is working
        """

    def check_fetch_actions(self: Any) -> bool: ...
        """
        Test action fetching and validation.
        
                Returns:
                    bool: True if action fetching works
        """

    def check_filesystem_space(self: Any) -> bool: ...
        """
        Check available filesystem space and usage.
        
                Returns:
                    bool: True if filesystem space is sufficient
        """

    def check_get_gpu_indices(self: Any) -> bool: ...
        """
        Check if get_gpu_indices returns valid indices.
        
                Returns:
                    bool: True if GPU indices are valid
        """

    def check_gpu(self: Any) -> bool: ...
        """
        Check if machine has GPU and it's functioning.
        
                Returns:
                    bool: True if GPU check passes
        """

    def check_instance_id(self: Any, instance_id: Optional[str] = None) -> bool: ...
        """
        Validate instance ID from args or env.
        
                Args:
                    instance_id: Optional instance ID to validate
        
                Returns:
                    bool: True if instance ID is valid
        """

    def check_resources(self: Any) -> bool: ...
        """
        Validate system resource limits and availability.
        
                Returns:
                    bool: True if resource checks pass
        """

    def check_resources_tracking(self: Any) -> bool: ...
        """
        Test resource tracking updates and monitoring.
        
                Returns:
                    bool: True if resource tracking is working
        """

    def check_scaling_status(self: Any) -> bool: ...
        """
        Test scaling service status.
        
                Returns:
                    bool: True if scaling status is ok
        """

    def cleanup_docker_storage(self: Any) -> bool: ...
        """
        Clean up docker storage and verify space freed.
        
                Returns:
                    bool: True if cleanup successful
        """

    def create_docker_volume(self: Any) -> bool: ...
        """
        Create docker volume.
        
        Returns:
            bool: True if volume created successfully
        """

    def get_available_resources(self: Any) -> bool: ...
        """
        Check available system resources are within valid ranges.
        
                Returns:
                    bool: True if resources are within valid ranges
        """

    def get_shutdown_details(self: Any) -> bool: ...
        """
        Get and validate shutdown details from response.
        
                Returns:
                    bool: True if shutdown details are valid
        """

    def run_all_checks(self: Any, instance_id: Optional[str] = None, access_key: Optional[str] = None, secret_key: Optional[str] = None) -> bool: ...
        """
        Run all prechecks in sequence.
        
                Args:
                    instance_id: Optional instance ID to validate
                    access_key: Optional access key to validate
                    secret_key: Optional secret key to validate
        
                Returns:
                    bool: True if all checks pass
        """

    def setup_docker(self: Any) -> bool: ...
        """
        Setup docker.
        
        Returns:
            bool: True if setup successful
        """

    def test_actions_scale_down(self: Any) -> bool: ...
        """
        Test actions scale down.
        
                Returns:
                    bool: True if scale down test passes
        """

    def test_gpu(self: Any) -> bool: ...
        """
        Test if GPU is working and has sufficient memory.
        
                Returns:
                    bool: True if GPU test passes
        """


# From resources_tracker
class ActionsResourcesTracker:
    """
    Tracks Docker container action resources
    """

    def __init__(self: Any, scaling: Any) -> None: ...
        """
        Initialize ActionsResourcesTracker
        """

    def get_current_action_usage(self: Any, container: Any, status: Any) -> Any: ...
        """
        Get current resource usage for a container
        """

    def get_sub_containers_by_label(self: Any, label_key: Any, label_value: Any) -> Any: ...
        """
        Get running containers with specified label key and value
        """

    def update_actions_resources(self: Any) -> Any: ...
        """
        Process both running and exited containers
        """

    def update_max_action_usage(self: Any, action_record_id: Any, current_gpu_utilization: Any, current_gpu_memory: Any, current_cpu_utilization: Any, current_memory_utilization: Any) -> Any: ...
        """
        Update and return maximum resource usage values for an action
        """


# From resources_tracker
class MachineResourcesTracker:
    """
    Tracks machine-level resources like CPU, memory and GPU
    """

    def __init__(self: Any, scaling: Any) -> None: ...
        """
        Initialize MachineResourcesTracker
        """

    def update_available_resources(self: Any) -> Any: ...
        """
        Update available machine resources
        """


# From resources_tracker
class ResourcesTracker:
    """
    Tracks machine and pid resources
    """

    def __init__(self: Any) -> None: ...
        """
        Initialize ResourcesTracker
        """

    def get_available_resources(self: Any) -> Any: ...
        """
        Get available machine resources
        """

    def get_container_cpu_and_memory(self: Any, container: Any) -> Any: ...
        """
        Get CPU and memory usage for a container
        """

    def get_container_cpu_and_memory_with_container_id(self: Any, container_id: Any) -> Any: ...
        """
        Get CPU and memory usage for a specific container
        """

    def get_container_gpu_info(self: Any, container_id: Any) -> Any: ...
        """
        Get GPU usage for a specific container
        """

    def get_container_gpu_memory_usage(self: Any, container_pid: Any) -> Any: ...
        """
        Get GPU memory usage for a container PID
        """

    def get_container_gpu_usage(self: Any, container_pid: Any) -> Any: ...
        """
        Get GPU usage for a container PID
        """

    def get_pid_id_by_container_id(self: Any, container_id: Any) -> Any: ...
        """
        Get PID for a container ID
        """


# From scaling
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


# From shutdown_manager
class ShutdownManager:
    """
    Class for managing compute instance shutdown.
    """

    def __init__(self: Any, scaling: Any) -> None: ...
        """
        Initialize ShutdownManager.
        
                Args:
                    scaling: Scaling instance to manage shutdown
        """

    def do_cleanup_and_shutdown(self: Any) -> Any: ...
        """
        Clean up resources and shut down the instance.
        
                This method attempts a coordinated shutdown with multiple fallback strategies:
                1. API call to notify the scaling service
                2. Graceful OS shutdown command
                3. Aggressive shutdown methods if needed
                4. Emergency forced shutdown as last resort
        
                Returns:
                    bool: True if shutdown was initiated successfully, False otherwise
        """

    def handle_shutdown(self: Any, tasks_running: Any) -> Any: ...
        """
        Check idle time and trigger shutdown if threshold is exceeded.
        
                Args:
                    tasks_running: Boolean indicating if there are running tasks
        """


from . import action_instance, actions_manager, actions_scaledown_manager, instance_manager, instance_utils, prechecks, resources_tracker, scaling, shutdown_manager, task_utils

def __getattr__(name: str) -> Any: ...