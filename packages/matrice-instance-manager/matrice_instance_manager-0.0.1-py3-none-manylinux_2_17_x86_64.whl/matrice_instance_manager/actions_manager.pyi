"""Auto-generated stub for module: actions_manager."""
from typing import Any, Dict, List, Optional

from matrice_common.utils import log_errors
from matrice_instance_manager.action_instance import ActionInstance
from matrice_instance_manager.instance_utils import has_gpu, get_mem_usage, cleanup_docker_storage
from matrice_instance_manager.scaling import Scaling
import logging
import os
import time

# Classes
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

