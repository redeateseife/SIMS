# utils/system_utils.py
# Server-lifecycle utilities only.
# The shutdown *screen* (visual) lives in ui/components.py so it inherits
# the design tokens from ui/theme.py automatically.

from os     import getpid, kill
from signal import SIGTERM
from time   import sleep


def shutdown_server(delay: int = 1) -> None:
    """Wait *delay* seconds then send SIGTERM to the current process."""
    sleep(delay)
    kill(getpid(), SIGTERM)