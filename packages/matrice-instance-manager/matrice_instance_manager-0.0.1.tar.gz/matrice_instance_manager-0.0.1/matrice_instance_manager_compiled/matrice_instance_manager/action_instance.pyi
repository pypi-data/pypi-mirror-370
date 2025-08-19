"""Auto-generated stub for module: action_instance."""
from typing import Any

from matrice_common.utils import log_errors
from matrice_instance_manager.instance_utils import get_gpu_with_sufficient_memory_for_action, get_decrypted_access_key_pair, get_max_file_system
from matrice_instance_manager.scaling import Scaling
from matrice_instance_manager.task_utils import setup_workspace_and_run_task
import logging
import os
import shlex
import signal
import subprocess
import threading
import time
import urllib.request

# Functions
def augmentation_server_creation_execute(self: Any) -> Any: ...
    """
    Create Augmentation Server
    """
def data_preparation_execute(self: Any) -> Any: ...
    """
    Execute data preparation task.
    """
def data_processing_execute(self: Any) -> Any: ...
    """
    Execute data processing task.
    """
def data_split_execute(self: Any) -> Any: ...
    """
    Execute data split task.
    """
def dataset_annotation_execute(self: Any) -> Any: ...
    """
    Execute dataset annotation task.
    """
def dataset_augmentation_execute(self: Any) -> Any: ...
    """
    Execute dataset augmentation task.
    """
def deploy_aggregator_execute(self: Any) -> Any: ...
    """
    Execute deploy aggregator task.
    """
def image_build_execute(self: Any) -> Any: ...
    """
    Execute image building task.
    """
def kafka_setup_execute(self: Any) -> Any: ...
    """
    Execute kafka server task.
    """
def model_deploy_execute(self: Any) -> Any: ...
    """
    Execute model deployment task.
    """
def model_eval_execute(self: Any) -> Any: ...
    """
    Execute model evaluation task.
    """
def model_export_execute(self: Any) -> Any: ...
    """
    Execute model export task.
    """
def model_train_execute(self: Any) -> Any: ...
    """
    Execute model training task.
    """
def resource_clone_execute(self: Any) -> Any: ...
    """
    Execute resource clone task.
    """

# Classes
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

