"""Auto-generated stub for module: shutdown_manager."""
from typing import Any

from matrice_common.utils import log_errors
from matrice_instance_manager.scaling import Scaling
import logging
import os
import platform
import signal
import subprocess
import sys
import time

# Classes
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

