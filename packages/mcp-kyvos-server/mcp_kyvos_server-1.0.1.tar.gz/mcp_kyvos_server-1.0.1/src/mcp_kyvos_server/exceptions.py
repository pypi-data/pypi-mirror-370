class MCPKyvosAuthenticationError(Exception):
    """Raised when Kyvos API authentication fails (401/403)."""
    pass

class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    pass

class EnvironmentLoadError(MCPError):
    """Raised when environment variables fail to load."""
    pass

class ServerStartError(MCPError):
    """Raised when the server fails to start."""
    pass

class ServiceInitializationError(Exception):
    """Raised when a service (e.g., Kyvos) fails to initialize."""
    pass

class MCPProjectError(Exception):
    """Base exception class for MCP Project errors."""
    pass

class ConfigurationError(MCPProjectError):
    """Raised when configuration or environment setup fails."""
    pass

class ServiceExecutionError(MCPProjectError):
    """Raised when a service (e.g., Kyvos) fails during execution."""
    pass

class ResourceNotFoundError(MCPProjectError):
    """Raised when a requested resource is not found."""
    pass

class AuthenticationError(MCPProjectError):
    """Raised when authentication with a service fails."""
    pass

class ExpiredTokenError(Exception):
    """Raised when a bearer token is expired and needs to be refreshed."""
    pass