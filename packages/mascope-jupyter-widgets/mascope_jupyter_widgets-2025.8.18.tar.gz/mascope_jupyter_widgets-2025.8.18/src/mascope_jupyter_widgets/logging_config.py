import sys
import loguru
from mascope_jupyter_widgets.mascope_data.access import (
    get_mjw_mode,
)

# Configure logging
original_stderr = sys.__stderr__  # Collect the original stderr stream
MJW_DEV_MODE = get_mjw_mode()  # Get the MJW_DEV_MODE environment variable
loguru.logger.remove()
loguru.logger.add(
    original_stderr,
    level="DEBUG" if MJW_DEV_MODE else "INFO",
    format="{time} - {level} - {message}",
)  # Log to the console
logger = loguru.logger  # Create a shared logger
