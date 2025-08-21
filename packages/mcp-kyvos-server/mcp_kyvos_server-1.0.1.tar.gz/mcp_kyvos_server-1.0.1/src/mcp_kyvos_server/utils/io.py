"""I/O utility functions for MCP Kyvos."""

import os
from mcp_kyvos_server.utils.logging import setup_logger
from ..utils.constants import InfoLogs, DebugLogs

logger, log_path = setup_logger()

def is_read_only_mode() -> bool:
    """Check if the server is running in read-only mode.

    Read-only mode prevents all write operations (create, update, delete)
    while allowing all read operations. This is useful for working with
    production Kyvos instances where you want to prevent accidental
    modifications.

    Returns:
        True if read-only mode is enabled, False otherwise
    """
    value = os.getenv("READ_ONLY_MODE", "false")
    return value.lower() in ("true", "1", "yes", "y", "on")


def load_prompt_from_env(env_var_name: str, raw_data_query: bool) -> str:
    """
    Loads a prompt from a file path specified in an environment variable.

    Args:
        env_var_name (str): The name of the environment variable that contains the file path.

    Returns:
        str: The contents of the prompt file.

    Raises:
        FileNotFoundError: If the file path doesn't exist.
        ValueError: If the environment variable is not set.
    """
    logger.debug(InfoLogs.RAW_DATA_QUERY_FLAG.format(raw_data_query=raw_data_query))

    prompt_path = os.environ.get(env_var_name)

    if not prompt_path:
        base_dir = os.path.dirname(__file__)

        if raw_data_query:
            prompt_path = os.path.join(base_dir, '..', 'kyvos', 'prompt', 'fsm_system_prompt.txt')
            logger.debug(DebugLogs.USING_FLEXIBLE_PROMPT.format(path=prompt_path))
        else:
            prompt_path = os.path.join(base_dir, '..', 'kyvos', 'prompt', 'kyvos_prompt.txt')
            logger.debug(DebugLogs.USING_STANDARD_PROMPT.format(path=prompt_path))
        
        prompt_path = os.path.abspath(prompt_path)
        logger.info(InfoLogs.PROMPT_FILE_LOADED_DEFAULT)
    else:
        logger.info(InfoLogs.PROMPT_FILE_LOADED_ENV)
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file '{prompt_path}' does not exist.")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()