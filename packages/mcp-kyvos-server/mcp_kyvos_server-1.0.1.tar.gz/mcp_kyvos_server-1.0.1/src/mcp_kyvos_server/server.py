import json
import os
from uuid import UUID
import httpx 
import uvicorn
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from http.client import HTTPException
from typing import Any, Optional
from pydantic import AnyUrl, ValidationError

from mcp.server import Server
from mcp.types import Resource, TextContent, Tool, JSONRPCMessage
from mcp.shared.message import SessionMessage
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send
from starlette.responses import PlainTextResponse

from fastapi import FastAPI, Request
from fastapi import FastAPI
from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from mcp_kyvos_server.utils.logging import setup_logger

from mcp_kyvos_server.kyvos import KyvosFetcher
from mcp_kyvos_server.utils.io import is_read_only_mode, load_prompt_from_env
from mcp_kyvos_server.database.token_store import get_tokens, get_email_by_client_access_token
from mcp_kyvos_server.exceptions import ServiceInitializationError, ServiceExecutionError
from mcp_kyvos_server.utils.constants import DebugLogs, ExceptionMessages, ErrorLogs, InfoLogs, WarningLogs, EnvironmentVariables
from mcp_kyvos_server.oauth.services.oauth_client_authorization_service import OAuthClientAuthorizationService


logger, log_path = setup_logger()

@dataclass
class AppContext:
    """Application context for MCP Kyvos."""
    kyvos: KyvosFetcher | None = None


def get_available_services() -> dict[str, bool | None]:
    """Determine which services are available based on environment variables."""

    # Check for Kyvos authentication (URL + username + password)
    try:
        kyvos_url = os.getenv(EnvironmentVariables.KYVOS_URL)
        if not kyvos_url or not isinstance(kyvos_url, str) or not kyvos_url.strip():
            raise ValueError("KYVOS_URL must be a non-empty string")
    except ValueError as ve:
        logger.error(ExceptionMessages.KYVOS_URL_MISSING.format(error=ve))
        raise
    except Exception as e:
        logger.error(ExceptionMessages.KYVOS_URL_READ_ERROR.format(error=e))
        raise

    if kyvos_url:
        kyvos_username = os.getenv(EnvironmentVariables.KYVOS_USERNAME)
        kyvos_password = os.getenv(EnvironmentVariables.KYVOS_PASSWORD)

        if not kyvos_username or not kyvos_password:
            raise ValueError("KYVOS_USERNAME or KYVOS_PASSWORD is missing or empty")

        kyvos_is_setup = all([
            kyvos_url,
            kyvos_username,
            kyvos_password
        ])
        if kyvos_is_setup:
            logger.info(InfoLogs.KYVOS_AUTH_METHOD)
        else:
            logger.warning(WarningLogs.KYVOS_CONFIG_INCOMPLETE)
    else:
        kyvos_is_setup = False
        logger.info(InfoLogs.KYVOS_URL_NOT_SET)

    return {"kyvos": kyvos_is_setup}


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[AppContext]:
    """Initialize and clean up application resources."""

    # Get available services
    services = get_available_services()

    try:
        # Attempt to initialize Kyvos service (if configured)
        kyvos = KyvosFetcher() if services["kyvos"] else None
    except Exception as e:
        logger.error(ErrorLogs.KYVOS_FETCHER_INITIALIZATION_FAILED)
        raise ServiceInitializationError("Error initializing Kyvos service.") from e

    try:
        # Log the startup information
        logger.info(InfoLogs.MCP_KYVOS_SERVER_STARTED)

        try:
            if kyvos:
                kyvos_url = kyvos.base_url
        except Exception as e:
            logger.error(ErrorLogs.KYVOS_BASE_URL_FETCH_FAILED)
            raise ServiceInitializationError("Error accessing Kyvos base URL") from e

        # Provide context to the application
        yield AppContext(kyvos=kyvos)

    except ServiceInitializationError as e:
        # Already logged in individual blocks above, re-raise
        logger.debug(DebugLogs.SERVICE_INIT_ERROR_RERAISED, exc_info=True)
        raise
    except Exception as e:
        # Catch-all fallback
        logger.error(ErrorLogs.UNEXPECTED_SERVER_STARTUP_ERROR)
        raise ServiceInitializationError("Unhandled error during server startup") from e

    finally:
        logger.info(InfoLogs.MCP_KYVOS_SERVER_SHUTDOWN)


# Create server instance
app = Server("mcp-kyvos", lifespan=server_lifespan)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Kyvos tools."""

    tools = []
    ctx = app.request_context.lifespan_context

    try:
        # Add Kyvos tools if Kyvos is configured
        if ctx:
            # Add Kyvos tools
            tools.extend(
                [
                    # Tool 1: listTables - Get all tables from a folder
                    Tool(
                        name="kyvos_list_semantic_models",
                        description="List all tables in database from Kyvos for sql query generation and select the most relevant table to the user query.",
                        inputSchema={
                            "type": "object",
                            "properties": {

                            }
                        }
                    ),

                    # Tool 2: listTableColumns - Get columns for a specific table
                    Tool(
                        name="kyvos_list_semantic_model_columns",
                        description="List all columns for a given table and folder in Kyvos for spark sql query generation. If the folder is not provided, determine the correct folder associated with the table.",
                        inputSchema={
                            "type": "object",
                            "required": ["table_name"],
                            "properties": {
                                "table_name": {
                                    "type": "string",
                                    "description": "Name of the table"
                                },
                                "folder_name": {
                                    "type": "string",
                                    "description": "Name of the folder containing the table."
                                }
                            }
                        }
                    ),

                    # Tool 3: Sql GenerationPrompt
                    Tool(
                        name="kyvos_sql_generation_prompt",
                        description="You must use this prompt for generating SQL query and must call this tool `kyvos_execute_query` before executing SQL",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {
                                    "type": "string",
                                    "description": "Name of the table"
                                },
                                "folder_name": {
                                    "type": "string",
                                    "description": "Name of the folder containing the table."
                                }
                            },
                            "required": ["table_name"]
                        }
                    ),

                    # Tool 4: executeQuery - Execute SQL queries
                    Tool(
                        name="kyvos_execute_query",
                        description="Strictly ensure to use the prompt tool before executing this tool. Execute an Spark SQL query on Kyvos and only SPARK SQL query syntax will be supported.",
                        inputSchema={
                            "type": "object",
                            "required": ["query"],
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "SQL query to execute"
                                }
                            }
                        }
                    )
                ]
            )




    except Exception as e:
        logger.error(ErrorLogs.ERROR_ADDING_TOOLS.format(error_message=str(e)), exc_info=True)

    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Kyvos operations."""
    ctx = app.request_context.lifespan_context

    # Check if we're in read-only mode for write operations
    read_only = is_read_only_mode()

    try:
        auth_token = arguments.get("auth_token", "")
        # Handle Kyvos operations
        if name == "kyvos_list_semantic_models" and ctx and ctx.kyvos:
            folder_name = arguments.get("folder_name", ctx.kyvos.default_folder)

            # Get tables from the specified folder
            if folder_name:
                tables = await ctx.kyvos.list_semantic_models(folder_name, auth_token)
            else:
                try:
                    tables = await ctx.kyvos.list_semantic_models_all(auth_token)
                except httpx.HTTPError as e:
                    error_msg = str(e)

                    if "404" in error_msg:
                        raise httpx.HTTPError("Upgrade to Kyvos version 2025.5 Alpha 2 or later, or set the KYVOS_DEFAULT_FOLDER environment variable, or pass it via the --kyvos-default-folder argument.") from e
                    else:
                        raise error_msg
            
            return [TextContent(
                type="text",
                text=json.dumps({"tables": tables}, indent=2, ensure_ascii=False)
            )]
        
        elif name == "kyvos_list_semantic_model_columns" and ctx and ctx.kyvos:
            table_name = arguments.get("table_name")
            folder_name = arguments.get("folder_name", ctx.kyvos.default_folder)

            if not folder_name:
                return (
                    f"The 'folder_name' argument is missing for the table_name = '{table_name}'. "
                    "Please retrieve the appropriate FOLDER_NAME from the metadata returned by the tool 'kyvos_list_semantic_models', add it to the arguments, "
                    "and re-run the tool 'kyvos_list_semantic_model_columns' with the updated request."
                    "If the 'folder_name' is still missing then re-run the tool 'kyvos_list_semantic_models' get the appropriate folder name and send it in the arguments."
                )
            
            if not table_name:
                raise ValueError("table_name is required")

            # Get columns for the specified table
            columns_data, raw_data_query = await ctx.kyvos.list_semantic_model_columns(table_name, folder_name, auth_token)
        
            ctx.kyvos._raw_data_query = raw_data_query
        
            return [TextContent(
                type="text",
                text=json.dumps(columns_data, indent=2, ensure_ascii=False)
            )]

        elif name == "kyvos_sql_generation_prompt" and ctx and ctx.kyvos:
            raw_data_query = getattr(ctx.kyvos, "_raw_data_query", False)

            table_name = arguments.get("table_name")

            folder_name = arguments.get("folder_name", ctx.kyvos.default_folder)

            table = f"`{folder_name}`.`{table_name}`"

            prompt_template = load_prompt_from_env(EnvironmentVariables.KYVOS_PROMPT_FILE, raw_data_query)

            input_values = {
                "Tablename": table,
            }

            prompt_filled = prompt_template.format(**input_values)

            # Load the prompt from the environment
            return [TextContent(
                type="text",
                text=prompt_filled
            )]

        elif name == "kyvos_execute_query" and ctx and ctx.kyvos:
            # Check if we're in read-only mode
            if read_only:
                return [TextContent(
                    type="text",
                    text="Operation 'kyvos_execute_query' is not available in read-only mode."
                )]

            query = arguments.get("query")

            if not query:
                raise ValueError("query is required")

            # Execute the SQL query
            result = await ctx.kyvos.execute_query(query, auth_token)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        # If we get here, the tool name is unknown
        raise ValueError(f"Unknown tool: {name}")

    except ValueError as ve:
        logger.error(ErrorLogs.TOOL_EXECUTION_ERROR.format(error=str(ve)))
        return [TextContent(type="text", text=f"Error: {str(ve)}")]

    except KeyError as ke:
        logger.error(ErrorLogs.MISSING_ARGUMENT.format(error=str(ke)), exc_info=True)
        return [TextContent(type="text", text=f"Error: Missing argument {str(ke)}")]

    except Exception as e:
        logger.error(ErrorLogs.TOOL_EXECUTION_ERROR.format(error=str(e)), exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def client_authorization(request):
    client_auth_service = OAuthClientAuthorizationService()

    auth_token = request.headers.get("Authorization")

    if (not auth_token or not auth_token.startswith("Bearer ")):
        logger.warning(WarningLogs.MISSING_OR_MALFORMED_AUTH_HEADER)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing or invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_token.split("Bearer ")[1]
    
    email = get_email_by_client_access_token(access_token)  

    if not email:
        logger.warning(WarningLogs.EMAIL_EXTRACTION_FAILED)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = get_tokens(email)
    user_access_token = tokens.get("access_token")

    if not user_access_token:
        logger.warning(WarningLogs.ACCESS_TOKEN_RETRIEVAL_FAILED.format(email=email))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid token for user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if client_auth_service.is_client_access_token_expired(user_access_token):
        logger.warning(WarningLogs.INVALID_TOKEN_MESSAGE)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing or invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(InfoLogs.ACCESS_TOKEN_VALIDATED)


async def run_server(transport: str = "stdio", port: int = 8000, sslkeyfile: Optional[str] = None,
                     sslcertifile: Optional[str] = None, auth_type: str="basic") -> None:
    """Run the MCP Kyvos server with the specified transport."""
    logger.info(InfoLogs.SERVER_STARTED)
    try:
        if transport == "sse":
            sse = SseServerTransport("/messages/")

            async def handle_sse(request: Request) -> None:
                if auth_type == "oauth":
                    await client_authorization(request)

                async with sse.connect_sse(
                        request.scope, request.receive, request._send
                ) as streams:
                    await app.run(
                        streams[0], streams[1], app.create_initialization_options()
                    )
                # Return empty response to avoid NoneType error
                return Response()

            async def handle_post_message(scope: Scope, receive: Receive, send: Send) -> None:
                request = Request(scope, receive)

                if auth_type == "oauth":
                    await client_authorization(request)

                session_id_param = request.query_params.get("session_id")
                if session_id_param is None:
                    logger.warning(WarningLogs.RECEIVED_REQUEST_WITHOUT_SESSION_ID)
                    response = Response("session_id is required", status_code=400)
                    return await response(scope, receive, send)

                try:
                    session_id = UUID(hex=session_id_param)
                    logger.debug(DebugLogs.PARSED_SESSION_ID.format(session_id=session_id))
                except ValueError:
                    logger.warning(WarningLogs.RECEIVED_INVALID_SESSION_ID.format(session_id=session_id_param))
                    response = Response("Invalid session ID", status_code=400)
                    return await response(scope, receive, send)

                writer = sse._read_stream_writers.get(session_id)
                if not writer:
                    logger.warning(WarningLogs.NO_SESSION_FOR_ID.format(session_id=session_id))
                    response = Response("Could not find session", status_code=404)
                    return await response(scope, receive, send)

                body = await request.body()
                logger.debug(DebugLogs.RAW_REQUEST_BODY.format(body=body))

                try:
                    message = JSONRPCMessage.model_validate_json(body)
                    logger.debug(DebugLogs.PARSED_JSONRPC_MESSAGE.format(message=message))

                    auth_token = request.headers.get("Authorization")
                    
                    if auth_type == "basic":
                        if hasattr(message, "root") and message.root:
                            root = message.root
                            if hasattr(root, "params") and isinstance(root.params, dict):
                                params = root.params
                                if "arguments" in params and isinstance(params["arguments"], dict):
                                    params["arguments"]["auth_token"] = auth_token
                                else:
                                    params["arguments"] = {"auth_token": auth_token}
                                logger.info(InfoLogs.UPDATED_MESSAGE_WITH_TOKEN_BASIC)
                            else:
                                logger.warning(WarningLogs.MISSING_PARAMS_FIELD)
                        else:
                            logger.warning(WarningLogs.MISSING_ROOT_FIELD)
                    
                    elif auth_type == "oauth":
                        access_token = auth_token.split("Bearer ")[1]

                        if hasattr(message, "root") and message.root:
                            root = message.root
                            if hasattr(root, "params") and isinstance(root.params, dict):
                                params = root.params
                                if "arguments" in params and isinstance(params["arguments"], dict):
                                    params["arguments"]["auth_token"] = f"Bearer {access_token}"
                                else:
                                    params["arguments"] = {"auth_token": f"Bearer {access_token}"}
                                logger.info(InfoLogs.UPDATED_MESSAGE_WITH_TOKEN_OAUTH)
                            else:
                                logger.warning(WarningLogs.MISSING_PARAMS_FIELD)
                        else:
                            logger.warning(WarningLogs.MISSING_ROOT_FIELD)

                except ValidationError as err:
                    logger.error(ErrorLogs.FAILED_TO_PARSE_MESSAGE.format(error_message=err))
                    response = Response("Could not parse message", status_code=400)
                    await response(scope, receive, send)
                    await writer.send(err)
                    return

                except HTTPException as http_exc:
                    response = Response(http_exc.detail, status_code=http_exc.status_code)
                    await response(scope, receive, send)
                    return

                session_message = SessionMessage(message)
                logger.debug(DebugLogs.SENDING_MESSAGE.format(message=session_message))
                response = Response("Accepted", status_code=202)
                await response(scope, receive, send)
                await writer.send(session_message)
                

            fastapi_app = FastAPI()

            @fastapi_app.options("/sse")
            async def options_sse(request:Request):
                auth_from_client = request.headers.get("auth_type").lower()
                if auth_type and auth_from_client != auth_type:
                    return PlainTextResponse(
                        f"Auth-type mismatch: got '{auth_from_client}', expected '{auth_type}'",
                        status_code=400
                    )
                return Response(
                    status_code=204,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "Auth-Type, Authorization, Accept",
                        "Access-Control-Max-Age": "3600",
                    },
                )

            fastapi_app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            from mcp_kyvos_server.oauth.routes.auth import auth_router

            fastapi_app.add_route("/sse", handle_sse, methods=["GET"])
            fastapi_app.mount("/messages", app=handle_post_message)
            fastapi_app.include_router(auth_router)

            config_kwargs = {
                "app": fastapi_app,
                "host": "0.0.0.0",
                "port": port,
            }

            if sslkeyfile and sslcertifile:
                config_kwargs["ssl_keyfile"] = sslkeyfile
                config_kwargs["ssl_certfile"] = sslcertifile

            config = uvicorn.Config(**config_kwargs)
            server = uvicorn.Server(config)
            await server.serve()
        else:
            async with stdio_server() as (read_stream, write_stream):
                await app.run(
                    read_stream, write_stream, app.create_initialization_options()
                )

    except Exception as e:
        logger.error(ErrorLogs.SERVER_ERROR.format(error_message=str(e)), exc_info=True)
        print(f"An error occurred: {str(e)}")