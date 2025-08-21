"""Fetcher module for Kyvos API interactions."""

from .client import KyvosClient
from .config import KyvosConfig

# Configure logging
from mcp_kyvos_server.utils.logging import setup_logger
from ..utils.constants import DebugLogs

logger, log_path = setup_logger()


class KyvosFetcher(KyvosClient):
    """
    Fetcher for Kyvos API interactions.
    Extends the base KyvosClient with additional functionality for MCP integration.
    """

    def __init__(self, config: KyvosConfig | None = None) -> None:
        """Initialize the Kyvos fetcher with configuration options.

        Args:
            config: Optional configuration object (will use env vars if not provided)

        Raises:
            ValueError: If configuration is invalid or required credentials are missing
        """
        super().__init__(config)
        logger.debug(DebugLogs.KYVOS_FETCHER_INITIALIZED)