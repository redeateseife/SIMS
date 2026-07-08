# utils/system_utils.py
# Server-lifecycle utilities

import os
import sys
from signal import SIGTERM
from time   import sleep


def shutdown_server(delay: int = 1) -> None:
    # Delay (in seconds) before terminating current process    
    sleep(delay)
    try:
        os.kill(os.getpid(), SIGTERM)
    except (OSError, AttributeError):
        sys.exit(0)
