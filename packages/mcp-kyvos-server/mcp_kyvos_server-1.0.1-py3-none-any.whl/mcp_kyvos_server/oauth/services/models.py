from mcp_kyvos_server.kyvos.auth_config import config
from mcp_kyvos_server.oauth.services.oauth_server_authorization_service import OAuthServerAuthorizationService

server_auth_service = OAuthServerAuthorizationService()

class PKCEManager:
    @staticmethod
    async def create_code_challenge_pair():
        code_verifier = await server_auth_service.generate_code_verifier()
        code_challenge = await server_auth_service.generate_code_challenge(code_verifier)
        return code_verifier, code_challenge