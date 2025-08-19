"""Auto-generated stub for module: instance_manager."""
from typing import Any, Dict, Optional, Tuple

from matrice_common.session import Session
from matrice_common.utils import log_errors
from matrice_instance_manager.actions_manager import ActionsManager
from matrice_instance_manager.actions_scaledown_manager import ActionsScaleDownManager
from matrice_instance_manager.instance_utils import get_instance_info, get_decrypted_access_key_pair
from matrice_instance_manager.resources_tracker import MachineResourcesTracker, ActionsResourcesTracker
from matrice_instance_manager.scaling import Scaling
from matrice_instance_manager.shutdown_manager import ShutdownManager
import json
import logging
import os
import threading
import time

# Classes
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

