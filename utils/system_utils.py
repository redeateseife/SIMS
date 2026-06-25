# utils/system_utils.py
# Server-lifecycle utilities only.
# The shutdown *screen* (visual) lives in ui/components.py so it inherits
# the design tokens from ui/theme.py automatically.

import os
import sys
from signal import SIGTERM
from time   import sleep


def shutdown_server(delay: int = 1) -> None:
    """
    Wait *delay* seconds then terminate the current process.

    Sends SIGTERM on Linux/macOS. Falls back to sys.exit(0) on Windows,
    where SIGTERM is not supported and raises OSError.
    """
    sleep(delay)
    try:
        os.kill(os.getpid(), SIGTERM)
    except (OSError, AttributeError):
        sys.exit(0)