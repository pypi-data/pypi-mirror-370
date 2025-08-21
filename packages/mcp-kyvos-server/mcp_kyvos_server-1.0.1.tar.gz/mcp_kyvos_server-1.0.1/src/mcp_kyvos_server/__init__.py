import asyncio
import os
import sys
import click
from dotenv import load_dotenv

from mcp_kyvos_server.database.db import init_db, DB_PATH
from mcp_kyvos_server.utils.logging import setup_logger, set_global_log_level
from .exceptions import EnvironmentLoadError, ServerStartError
from .utils.constants import DebugLogs, ExceptionMessages, ErrorLogs, InfoLogs, EnvironmentVariables, Descriptions

__version__ = "1.0.1"

@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (can be used multiple times)",
)
@click.option(
    "--env-file", type=click.Path(exists=True, dir_okay=False), help=Descriptions.ENV_FILE_DESCRIPTION
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help=Descriptions.TRANSPORT_DESCRIPTION,
)
@click.option(
    "--port",
    default=8000,
    help=Descriptions.PORT_DESCRIPTION,
)
@click.option(
    "--kyvos-url",
    help=Descriptions.KYVOS_URL_DESCRIPTION,
)
@click.option("--kyvos-username", help=Descriptions.KYVOS_USERNAME_DESCRIPTION)
@click.option("--kyvos-password", help=Descriptions.KYVOS_PASSWORD_DESCRIPTION)
@click.option("--prompt-file", help=Descriptions.KYVOS_PROMPT_FILE_DESCRIPTION)
@click.option("--verify-ssl", help=Descriptions.VERIFY_SSL_DESCRIPTION)
@click.option("--max-rows", help=Descriptions.MAX_ROWS)
@click.option("--ssl-key-file", help=Descriptions.SSL_KEY_FILE)
@click.option("--ssl-certificate-file", help=Descriptions.SSL_CERTIFICATE_FILE)
@click.option("--kyvos-default-folder", help=Descriptions.KYVOS_DEFAULT_FOLDER_DESCRIPTION)
@click.option("--kyvos-version", help=Descriptions.KYVOS_DEFAULT_FOLDER_DESCRIPTION)
@click.option("--server-auth-type", help=Descriptions.AUTH_TYPE)
@click.option("--mcp-server-url", help=Descriptions.MCP_SERVER_URL)
@click.option("--log-level", default="DEBUG", help=Descriptions.LOG_LEVEL)
def main(
    verbose: bool,
    env_file: str | None,
    transport: str,
    port: int,
    kyvos_url: str | None,
    kyvos_username: str | None,
    kyvos_password: str | None,
    verify_ssl: bool | None,
    prompt_file: str | None,
    max_rows: str|None,
    ssl_key_file: str|None,
    ssl_certificate_file: str|None,
    kyvos_default_folder: str|None,
    kyvos_version: str|None,
    server_auth_type: str|None,
    mcp_server_url: str|None,
    log_level: str
) -> None:
    """MCP Kyvos Server - Kyvos functionality for MCP. Supports Kyvos deployments."""
    set_global_log_level(log_level)
    logger, log_path = setup_logger(port=port)

    logger.info(InfoLogs.INIT_MCP_SERVER.format(version=__version__))
    logger.info(InfoLogs.LOG_FILE_CREATED.format(log_path=log_path))
    try:
        # Load environment variables from file if specified, otherwise try default .env
        try:
            if env_file:
                logger.debug(DebugLogs.LOADING_ENV_FROM_FILE.format(env_file=env_file))
                load_dotenv(env_file)
            else:
                logger.debug(DebugLogs.LOADING_DEFAULT_ENV)
                load_dotenv()
        except Exception as e:
            # Environment loading failed, raise specific error for clarity
            logger.error(ExceptionMessages.FAILED_ENV_LOAD)
            raise EnvironmentLoadError(str(e)) from e

        # Override environment variables from CLI if provided
        try:
            if kyvos_url:
                if not isinstance(kyvos_url, str) or not kyvos_url.strip():
                    raise ValueError("KYVOS_URL must be a non-empty string")
                os.environ[EnvironmentVariables.KYVOS_URL] = kyvos_url
                logger.info(InfoLogs.KYVOS_URL_SET)

            if kyvos_username:
                if not isinstance(kyvos_username, str) or not kyvos_username.strip():
                    raise ValueError("KYVOS_USERNAME must be a non-empty string")
                os.environ[EnvironmentVariables.KYVOS_USERNAME] = kyvos_username
                logger.info(InfoLogs.KYVOS_USERNAME_SET)

            if kyvos_password:
                if not isinstance(kyvos_password, str) or not kyvos_password.strip():
                    raise ValueError("KYVOS_PASSWORD must be a non-empty string")
                os.environ[EnvironmentVariables.KYVOS_PASSWORD] = kyvos_password
                logger.info(InfoLogs.KYVOS_PASSWORD_SET)

            if verify_ssl:
                if not isinstance(verify_ssl, bool):
                    raise ValueError("VERIFY_SSL must be a boolean")
                os.environ[EnvironmentVariables.VERIFY_SSL] = str(verify_ssl)
                logger.info(InfoLogs.VERIFY_SSL_SET)

            if prompt_file:
                if not isinstance(prompt_file, str) or not prompt_file.strip():
                    raise ValueError("KYVOS_PROMPT_FILE must be a non-empty string")
                os.environ[EnvironmentVariables.KYVOS_PROMPT_FILE] = prompt_file
                logger.info(InfoLogs.KYVOS_PROMPT_FILE_SET)

            if max_rows:
                if not isinstance(max_rows, str) or not max_rows.strip():
                    raise ValueError("MAX_ROWS must be a non-empty string")
                os.environ[EnvironmentVariables.MAX_ROWS] = max_rows
                logger.info(InfoLogs.KYVOS_MAX_ROWS.format(max_rows=max_rows))
            
            if ssl_key_file:
                if not isinstance(ssl_key_file, str) or not ssl_key_file.strip():
                    raise ValueError("SSL_KEY_FILE must be a non-empty string")
                os.environ[EnvironmentVariables.SSL_KEY_FILE] = ssl_key_file
                logger.info(InfoLogs.SSL_KEY_FILE)
            
            if ssl_certificate_file:
                if not isinstance(ssl_certificate_file, str) or not ssl_certificate_file.strip():
                    raise ValueError("SSL_CERTIFILE must be a non-empty string")
                os.environ[EnvironmentVariables.SSL_CERTIFICATE_FILE] = ssl_certificate_file
                logger.info(InfoLogs.SSL_CERTIFICATE_FILE)
            
            if kyvos_default_folder:
                if not isinstance(kyvos_default_folder, str) or not kyvos_default_folder.strip():
                    raise ValueError("kyvos_default_folder must be a non-empty string")
                os.environ[EnvironmentVariables.KYVOS_DEFAULT_FOLDER] = kyvos_default_folder
                logger.info(InfoLogs.KYVOS_DEFAULT_FOLDER)
            
            if kyvos_version:
                if not isinstance(kyvos_version, str) or not kyvos_version.strip():
                    raise ValueError("kyvos_version must be a non-empty string")
                os.environ[EnvironmentVariables.KYVOS_VERSION] = kyvos_version
                logger.info(InfoLogs.KYVOS_VERSION)
            
            if server_auth_type:
                if not isinstance(server_auth_type, str) or not server_auth_type.strip():
                    raise ValueError("server_auth_type must be a non-empty string")
                os.environ[EnvironmentVariables.SERVER_AUTH_TYPE] = server_auth_type
            
            if port and transport == "sse":
                if isinstance(port, int):
                    os.environ[EnvironmentVariables.PORT] = str(port)  
                    logger.info(InfoLogs.PORT_LOGS.format(port=port))

            if mcp_server_url:
                if not isinstance(mcp_server_url, str) or not mcp_server_url.strip():
                    raise ValueError("mcp_server_url must be a non-empty string")
                os.environ[EnvironmentVariables.MCP_SERVER_URL] = mcp_server_url
                logger.info(InfoLogs.MCP_SERVER_URL_LOGS.format(address=mcp_server_url))

        except ValueError as ve:
            logger.error(ErrorLogs.INVALID_KYVOS_ENV_INPUT.format(error=ve))
            raise
        except Exception as e:
            logger.error(ErrorLogs.UNEXPECTED_KYVOS_ENV_ERROR.format(error=e))
            raise

        from . import server
        # Run the server with specified transport
        try:
            logger.info(InfoLogs.STARTING_SERVER)
            auth_type = server_auth_type or os.getenv('SERVER_AUTH_TYPE')

            if transport == "sse" and auth_type == "oauth":
                init_db()
                logger.info(InfoLogs.DATABASE_CREATED.format(DB_PATH=DB_PATH))

            if auth_type == None:
                auth_type = "basic"
            asyncio.run(server.run_server(transport=transport,port=port,sslkeyfile=ssl_key_file or os.getenv('SSL_KEY_FILE'),sslcertifile=ssl_certificate_file or os.getenv('SSL_CERTIFICATE_FILE'),auth_type=auth_type))
        except Exception as e:
            # Server failed to launch, raise custom error
            logger.error(ExceptionMessages.START_SERVER_FAILED)
            raise ServerStartError(str(e)) from e

    except Exception as e:
        # Final catch-all for startup failure
        logger.critical(ErrorLogs.STARTUP_FATAL_ERROR.format(error=e))
        sys.exit(1)


__all__ = ["main", "server", "__version__"]