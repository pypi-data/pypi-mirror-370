import os
from dotenv import load_dotenv

LOG_FILE = "failed_requests.log"

def load_and_validate_env_vars(required_vars):
    """
    Load environment variables from .env file and validate required variables.

    Args:
        required_vars (list): List of required environment variable names.

    Returns:
        dict: Dictionary of loaded environment variables.

    Raises:
        EnvironmentError: If any required environment variables are missing.
    """
    load_dotenv(override=True)
    
    env_vars = {var: os.getenv(var) for var in required_vars}
    missing_vars = [var for var, value in env_vars.items() if value is None]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return env_vars
