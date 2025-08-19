"""Auto-generated stub for module: instance_utils."""
from typing import Any, List

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime
from matrice_common.utils import log_errors
import base64
import logging
import os
import psutil
import socket
import subprocess
import urllib.request

# Functions
def calculate_time_difference(start_time_str: Any, finish_time_str: Any) -> Any: ...
    """
    Calculate time difference between start and finish times.
    
    Args:
        start_time_str (str): Start time string
        finish_time_str (str): Finish time string
    
    Returns:
        int: Time difference in seconds
    """
def check_public_port_exposure(port: Any) -> Any: ...
    """
    Check if port is publicly accessible.
    
    Args:
        port (int): Port number to check
    
    Returns:
        bool: True if port is publicly accessible
    """
def cleanup_docker_storage() -> Any: ...
    """
    Clean up Docker storage if space is low.
    """
def get_cpu_memory_usage() -> Any: ...
    """
    Get CPU memory usage.
    
    Returns:
        float: Memory usage between 0 and 1
    """
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
def get_disk_space_usage() -> Any: ...
    """
    Get disk space usage for all filesystems.
    
    Returns:
        list: List of disk usage information dictionaries
    """
def get_docker_disk_space_usage() -> Any: ...
    """
    Get disk space usage for Docker storage.
    
    Returns:
        dict: Docker disk usage information
    """
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
def get_gpu_info() -> Any: ...
    """
    Get GPU information.
    
    Returns:
        list: GPU information strings
    """
def get_gpu_memory_usage() -> Any: ...
    """
    Get GPU memory usage percentage.
    
    Returns:
        float: Memory usage between 0 and 1
    """
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
def get_instance_id() -> str: ...
    """
    Get instance ID.
    
    Returns:
        str: Instance ID or empty string
    """
def get_instance_info() -> Any: ...
    """
    Get instance provider and ID information.
    
    Returns:
        tuple: (service_provider, instance_id) strings
    """
def get_max_file_system() -> Any: ...
    """
    Get filesystem with maximum available space.
    
    Returns:
        str: Path to filesystem with most space or None
    """
def get_mem_usage() -> Any: ...
    """
    Get memory usage for either GPU or CPU.
    
    Returns:
        float: Memory usage between 0 and 1
    """
def get_required_gpu_memory(action_details: Any) -> Any: ...
    """
    Get required GPU memory from action details.
    
    Args:
        action_details (dict): Action details
    
    Returns:
        int: Required GPU memory
    """
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
def has_gpu() -> bool: ...
    """
    Check if the system has a GPU.
    
    Returns:
        bool: True if GPU is present, False otherwise
    """
def is_allowed_gpu_device(gpu_index: Any) -> Any: ...
    """
    Check if GPU device is allowed.
    
    Args:
        gpu_index (int): GPU device index
    
    Returns:
        bool: True if GPU is allowed
    """
def is_docker_running() -> Any: ...
    """
    Check if Docker is running.
    
    Returns:
        bool: True if Docker containers are running
    """
def prune_docker_images() -> Any: ...
    """
    Prune Docker images.
    """
