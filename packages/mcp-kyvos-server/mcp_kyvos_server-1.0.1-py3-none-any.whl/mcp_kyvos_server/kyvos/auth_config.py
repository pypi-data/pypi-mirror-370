import os
from mcp_kyvos_server.kyvos.mcp_server_url import mcp_server_url

kyvos_url = os.getenv("KYVOS_URL").rstrip("/")

class Config:
    KYVOS_API_URL: str          = f"{kyvos_url}/rest/custom/OAuthConfig"
    REDIRECT_URI: str           = f"{mcp_server_url}/auth/callback"
    KYVOS_TOKEN_URL: str        = None
    KYVOS_SCOPE: str            = None
    KYVOS_CLIENT_ID: str        = None
    KYVOS_AUTHORIZE_URL: str    = None

    BOUND_EXPIRY                = 120       # seconds (2 minutes)
    REFRESH_TOKEN_LIFESPAN      = 24 * 3600 # seconds (24 hours)
    TOKEN_EXPIRY_GRACE_SECONDS  = 30        # seconds 


config = Config()