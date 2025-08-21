import jwt
import uuid
import time
from typing import Optional
from jose import jwt
from mcp_kyvos_server.kyvos.auth_config import config


class InMemoryTokenStore:
    """In-memory token store. Replace with Redis/DB in production."""
    
    def __init__(self):
        self._store = {}

    def set(self, key: str, value: dict):
        self._store[key] = value

    def get(self, key: str) -> Optional[dict]:
        return self._store.get(key)

    def delete(self, key: str):
        if key in self._store:
            del self._store[key]


class OAuthClientAuthorizationService:
    def __init__(self, token_store=None):
        self.token_store = token_store or InMemoryTokenStore()

    async def generate_bound_code(self, access_token: str) -> str:
        bound_code = str(uuid.uuid4())
        expiry = time.time() + config.BOUND_EXPIRY
        self.token_store.set(bound_code, {
            "access_token": access_token,
            "expires_at": expiry
        })
        return bound_code

    async def validate_bound_code(self, bound_code: str) -> Optional[str]:
        entry = self.token_store.get(bound_code)

        if not entry or time.time() > entry["expires_at"]:
            self.token_store.delete(bound_code)
            # Validated the bound authorization code. Expired.
            return True

        # Validated the bound authorization code. Deleted when its used.
        self.token_store.delete(bound_code)

        return False

    @staticmethod
    def is_client_access_token_expired(access_token: str) -> bool:
        """Check if the given access token is expired."""
        try:
            decoded = jwt.get_unverified_claims(access_token)
            exp = decoded.get("exp")
            if not exp:
                return True
            return int(time.time()) >= (exp - config.TOKEN_EXPIRY_GRACE_SECONDS)
        except Exception as e:
            return True