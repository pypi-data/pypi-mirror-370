"""Auto-generated stub for module: resources_tracker."""
from typing import Any, Dict, List, Optional, Tuple

from datetime import datetime, timezone
from matrice_common.utils import log_errors
from matrice_instance_manager.instance_utils import has_gpu, get_gpu_info, calculate_time_difference
from matrice_instance_manager.scaling import Scaling
import docker
import logging
import os
import psutil
import subprocess

# Classes
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

