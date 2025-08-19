import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def load_mascope_token() -> str:
    """
    Load Mascope access token from .env file.
    The .env file should be located in the root directory of the project.

    :return: The access token string or empty string if not found
    :rtype: str
    """

    # Get access token
    access_token = os.getenv("MASCOPE_ACCESS_TOKEN", "")

    if not access_token:
        raise RuntimeError("Mascope API token is not found in .env file")
    return access_token


def load_url() -> list:
    """
    Load Mascope URL-address from .env file.
    The .env file should be located in the root directory of the project.

    :return: URL-address list or None if not found any variables containing 'URL' in name
    :rtype: list
    """

    # Collect URLs from environment variables to list
    mascope_url = os.getenv("MASCOPE_URL")
    if mascope_url is None:
        raise RuntimeError(
            "No environment variables containing 'MASCOPE_URL' were found!"
        )
    return [mascope_url]


def get_mjw_mode() -> bool:
    """
    Get the MJW_DEV_MODE environment variable.
    This variable is used to determine if the application is running in development mode.

    :return: True if in development mode, False otherwise
    :rtype: bool
    """

    mjw_dew_mode = os.getenv("MJW_DEV_MODE", "False").lower() in (
        "true",
        "1",
        "yes",
    )  # Collect the MJW_DEV_MODE environment variable

    return mjw_dew_mode
