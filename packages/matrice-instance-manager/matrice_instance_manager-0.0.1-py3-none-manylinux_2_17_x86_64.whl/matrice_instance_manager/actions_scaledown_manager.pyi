"""Auto-generated stub for module: actions_scaledown_manager."""
from typing import Any

from matrice_common.utils import log_errors
from matrice_instance_manager.scaling import Scaling
import docker
import logging

# Classes
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

