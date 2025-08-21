import os
import time
import base64
import hashlib
import requests
from typing import Dict
from jose import jwt
import httpx
from fastapi import HTTPException

from mcp_kyvos_server.database.token_store import get_tokens, update_token_field
from mcp_kyvos_server.kyvos.auth_config import config
from mcp_kyvos_server.utils.logging import setup_logger
from mcp_kyvos_server.utils.constants import ErrorLogs, DebugLogs, WarningLogs

logger, log_path = setup_logger()

class OAuthServerAuthorizationService:
    def __init__(self):
        pass

    async def get_oauth_access_token(self, code: str, code_verifier: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    config.KYVOS_TOKEN_URL,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "authorization_code",
                        "client_id": config.KYVOS_CLIENT_ID,
                        "code_verifier": code_verifier,
                        "code": code,
                        "redirect_uri": config.REDIRECT_URI,
                    },
                )

            if response.is_success:
                return response.json()

            # Log the OAuth error response body
            logger.error(ErrorLogs.TOKEN_EXCHANGE_FAILED.format(status_code=response.status_code, message=response.text))
            raise ValueError("Failed to exchange code for token")

        except httpx.RequestError as e:
            # Catch networking issues (e.g., DNS failure, connection errors)
            logger.error(ErrorLogs.TOKEN_EXCHANGE_NETWORK_ERROR.format(exception=e))
            raise ValueError("Network error while exchanging code for token")

    async def get_refreshed_oauth_access_token(self, email, refresh_token: str, actor) -> Dict:
        """Refresh access token using a refresh token."""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": config.REDIRECT_URI,
            "scope": config.KYVOS_SCOPE,
            "client_id": config.KYVOS_CLIENT_ID
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as refreshtoken:
                response = await refreshtoken.post(config.KYVOS_TOKEN_URL, data=data, headers=headers)
                response.raise_for_status()
                token_data = response.json()

            # Try decoding to extract expiry
            try:
                decoded = jwt.get_unverified_claims(token_data["id_token"])
                exp = decoded.get("exp", int(time.time()) + token_data.get("expires_in", 3600))
            except Exception:
                exp = int(time.time()) + token_data.get("expires_in", 3600)

            await self._update_server_details_in_database(email, token_data, exp)
            logger.debug(DebugLogs.SERVER_ACCESS_TOKEN_GENERATED)

            return token_data
        
        except requests.HTTPError as http_err:
            try:
                error_response = http_err.response.json()
                error = error_response.get("error")
                error_description = error_response.get("error_description", "")
                
                if error == "invalid_grant":
                    logger.warning(WarningLogs.TOKEN_EXCHANGE_WARNING.format(description=error_description))
                    return {"id_token": None}

            except Exception as parse_error:
                logger.error(ErrorLogs.TOKEN_RESPONSE_PARSING_FAILED.format(parse_error=parse_error))
                raise HTTPException(status_code=400, detail="Invalid or expired refresh token")

        except requests.RequestException as e:
            logger.error(ErrorLogs.TOKEN_REFRESH_FAILED.format(exception=e))
            raise ValueError("Failed to refresh access token")

    async def _update_server_details_in_database(self, email, token_data: Dict, exp: int):
        """Update database with new token data."""
        update_token_field(email=email, field="access_token", value=token_data.get("id_token"))
        update_token_field(email=email, field="id_token", value=token_data.get("id_token"))
        update_token_field(email=email, field="refresh_token", value=token_data.get("refresh_token"))

    @staticmethod
    async def generate_code_verifier() -> str:
        """Generate a secure code verifier (used in PKCE flow)."""
        return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode("utf-8")

    @staticmethod
    async def generate_code_challenge(code_verifier: str) -> str:
        """Generate a code challenge from code verifier."""
        sha256_digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(sha256_digest).rstrip(b"=").decode("utf-8")