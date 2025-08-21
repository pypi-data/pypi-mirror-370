"""Configuration module for Kyvos API interactions."""

import os
from dataclasses import dataclass
from mcp_kyvos_server.utils.logging import setup_logger
from ..utils.constants import ErrorLogs, EnvironmentVariables

logger, log_path = setup_logger()

@dataclass
class KyvosConfig:
    """
    Kyvos API configuration.
    Handles authentication for Kyvos REST API using basic authentication.
    """

    url: str                                                     # Base URL for Kyvos
    username: str                                                # Username for authentication
    password: str                                                # Password for authentication
    default_folder: str                                          # Default folder for queries
    version: int
    max_rows: int
    verify_ssl: bool = True


    @classmethod
    def from_env(cls) -> "KyvosConfig":
        """Create configuration from environment variables.

        Returns:
            KyvosConfig with values from environment variables

        Raises:
            ValueError: If required environment variables are missing
        """
        url = os.getenv(EnvironmentVariables.KYVOS_URL)
        if not url:
            logger.error(ErrorLogs.MISSING_URL)
            raise ValueError(ErrorLogs.MISSING_URL)
        
        # Get authentication credentials
        username = os.getenv(EnvironmentVariables.KYVOS_USERNAME)
        if not username:
            logger.error(ErrorLogs.MISSING_USERNAME)
            raise ValueError(ErrorLogs.MISSING_USERNAME)

        password = os.getenv(EnvironmentVariables.KYVOS_PASSWORD)
        if not password:
            logger.error(ErrorLogs.MISSING_PASSWORD)
            raise ValueError(ErrorLogs.MISSING_PASSWORD)

        # Get default folder if specified, otherwise use BUSINESS_CATALOG
        default_folder = os.getenv(EnvironmentVariables.KYVOS_DEFAULT_FOLDER)
        version_str = os.getenv("KYVOS_VERSION")
        try:
            version = int(version_str) if version_str else 2
        except ValueError:
            logger.warning(f"Invalid version '{version_str}', defaulting to 2.")
            version = 2

        verify_ssl = os.getenv(EnvironmentVariables.VERIFY_SSL, "true").lower() in ("true", "1", "yes")
        max_rows = int(os.getenv('MAX_ROWS', "1000"))
        return cls(
            url=url,
            username=username,
            password=password,
            default_folder=default_folder,
            verify_ssl=verify_ssl,
            version =version,
            max_rows=max_rows
        )