"""Auto-generated stub for module: prechecks."""
from typing import Any, Optional

from matrice.docker_utils import check_docker
from matrice_instance_manager.actions_scaledown_manager import ActionsScaleDownManager
from matrice_instance_manager.instance_utils import get_instance_info, cleanup_docker_storage, get_cpu_memory_usage, get_gpu_memory_usage, get_mem_usage, get_gpu_with_sufficient_memory_for_action, get_max_file_system, has_gpu
from matrice_instance_manager.resources_tracker import ResourcesTracker, MachineResourcesTracker, ActionsResourcesTracker
from matrice_instance_manager.scaling import Scaling
import docker
import logging
import subprocess
import sys
import torch
import torch

# Classes
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

