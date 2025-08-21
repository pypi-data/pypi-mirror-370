import os
from mcp_kyvos_server.utils.constants import EnvironmentVariables

class BaseURLMiddleware:
    def __init__(self):
        self.mcp_server_url = os.getenv(EnvironmentVariables.MCP_SERVER_URL)
        if not self.mcp_server_url:
            raise ValueError(f"{EnvironmentVariables.MCP_SERVER_URL} environment variable is not set.")

    def get_mcp_server_url(self):
        return self.mcp_server_url

mcp_server_url_middleware = BaseURLMiddleware()
mcp_server_url = mcp_server_url_middleware.get_mcp_server_url()
