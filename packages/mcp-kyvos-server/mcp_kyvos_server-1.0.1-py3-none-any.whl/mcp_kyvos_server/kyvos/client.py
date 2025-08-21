"""Base client module for Kyvos API interactions."""
import os
from tarfile import version
from typing import Any, Dict, List, Optional
import json

import ssl
import truststore
import httpx
from httpx import BasicAuth

from .config import KyvosConfig
from ..exceptions import ConfigurationError
from ..utils.constants import KyvosEndpoints, DebugLogs, ExceptionMessages, ErrorLogs, InfoLogs, HeaderKeys, Tools
from mcp_kyvos_server.utils.logging import setup_logger


logger, log_path = setup_logger()

class KyvosClient:
    """Base client for Kyvos API interactions."""

    def __init__(self, config: KyvosConfig | None = None) -> None:
        """Initialize the Kyvos client with configuration options.

        Args:
            config: Optional configuration object (will use env vars if not provided)

        Raises:
            ValueError: If configuration is invalid or required credentials are missing
        """
        try:
            # Load configuration from environment variables if not provided
            self.config = config or KyvosConfig.from_env()
            
            # Store the base URL and authentication credentials
            self.base_url = self.config.url.rstrip("/")
            self.auth = BasicAuth(username=self.config.username, password=self.config.password)
            self.default_folder = self.config.default_folder
            self.version = self.config.version
            self.verify_ssl = self.config.verify_ssl
            self.max_rows=self.config.max_rows
            self.flag = False
            self.all_tables = None

            
            logger.debug(DebugLogs.KYVOS_CLIENT_INITIALIZED.format(url=self.base_url))

        except ValueError as ve:
            logger.error(ErrorLogs.INVALID_KYVOS_CONFIG.format(error=ve), exc_info=True)
            raise ConfigurationError(ExceptionMessages.INVALID_CONFIG_EXCEPTION) from ve
        
        except Exception as e:
            logger.error(ErrorLogs.UNEXPECTED_KYVOS_ERROR.format(error=e), exc_info=True)
            raise ConfigurationError(ExceptionMessages.INIT_CLIENT_EXCEPTION) from e
    

    async def list_semantic_models_all(self, auth_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tables from a specified folder in Kyvos.
        
        Args:
            auth_token: Optional authentication token
            
        Returns:
            List of table objects with their metadata
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        version= self.version
        url = f"{self.base_url}{KyvosEndpoints.ENTITY_SEARCH.format(version=version)}"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        if auth_token:
            headers[HeaderKeys.AUTHORIZATION] = auth_token
            headers["appType"] = "PUBLIC"
        else:
            headers[HeaderKeys.AUTHORIZATION] = self.auth._auth_header
                           
        params = {
            "maxRows": 1000,
            "filterJSON": json.dumps([
                {"fieldName": "entityType", "value": "SMODEL", "operation": "INLIST"}
            ]),
            "fetchProcessedStatus": "true",
            "queryableModelsOnly": "true"
        }

        logger.debug(InfoLogs.KYVOS_API_REQUEST_URL.format(tool=Tools.LIST_SEMANTIC_MODELS_ALL, url=url))
        logger.debug(InfoLogs.KYVOS_API_REQUEST_PAYLOAD.format(tool=Tools.LIST_SEMANTIC_MODELS_ALL, payload=params))
        
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if self.verify_ssl else False   
        
        try:
            async with httpx.AsyncClient(timeout=None,verify=ctx) as client:
                response = await client.post(
                    url, 
                    headers=headers,
                    data=params
                )

                if response.is_error:
                    try:
                        error_json = response.json()
                        error_message = error_json.get("MESSAGE", response.text)
                    except ValueError:
                        error_message = response.text

                    if response.status_code == 401 and "token has expired" in error_message.lower():
                        logger.info(InfoLogs.REFRESHING_ACCESS_TOKEN)
                        return error_message.lower()

                    raise httpx.HTTPError(f"Failed to list models: {error_message}")
                
                data = response.json()
                filtered_cubes = [
                    {
                        "NAME": cube["NAME"],
                        "DESC": cube.get("DESC", ""),
                        "FOLDER": cube.get("FOLDER_NAME", "")
                    }
                    for cube in data["IROS"]
                ]

                self.all_tables = data["IROS"]

                logger.debug(InfoLogs.KYVOS_API_RESPONSE.format(tool=Tools.LIST_SEMANTIC_MODELS_ALL, response=data))
                return filtered_cubes
                
        except httpx.RequestError as e:
            logger.error(ErrorLogs.NETWORK_ERROR_LISTING_TABLES.format(error=e), exc_info=True)
            raise ConnectionError(ExceptionMessages.NETWORK_ERROR_LISTING_TABLES) from e

    async def list_semantic_models(self, folder_name_or_id: Optional[str] = None, auth_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tables from a specified folder in Kyvos.
        
        Args:
            folder_name_or_id: The name or ID of the folder to list tables from.
                               Defaults to the configured default folder.
            
        Returns:
            List of table objects with their metadata
            
        Raises:
            httpx.HTTPError: If the API request fails
        """

        folder = folder_name_or_id or self.default_folder
        version = self.version
        url = f"{self.base_url}{KyvosEndpoints.FOLDER_MODELS.format(folder=folder, version=version)}"

        headers = {"Accept": "application/json"}
        
        if auth_token:
            headers[HeaderKeys.AUTHORIZATION] = auth_token
            headers["appType"] = "PUBLIC"
        else:
            headers[HeaderKeys.AUTHORIZATION] = self.auth._auth_header

        logger.debug(InfoLogs.KYVOS_API_REQUEST_URL.format(tool=Tools.LIST_SEMANTIC_MODELS, url=url))
        logger.info(InfoLogs.FETCHING_TABLES.format(folder=folder))

        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if self.verify_ssl else False  

        try:
            async with httpx.AsyncClient(timeout=None,verify=ctx) as client:
                response = await client.get(
                    url, 
                    headers=headers,
                )
                
                if response.is_error:
                    try:
                        error_json = response.json()
                        error_message = error_json.get("MESSAGE", response.text)
                    except ValueError:
                        error_message = response.text

                    if response.status_code == 401 and "token has expired" in error_message.lower():
                        logger.info(InfoLogs.REFRESHING_ACCESS_TOKEN)
                        return error_message.lower()

                    logger.error(ErrorLogs.CLIENT_ERROR_LOG.format(response_text=response.text))
                    raise ValueError(ErrorLogs.CLIENT_ERROR_EXCEPTION.format(error_message=error_message, url=url))
                                    
                data = response.json()
                filtered_cubes = [
                    {
                        "NAME": cube["NAME"],
                        "DESC": cube.get("DESC", ""),
                        "FOLDER":folder
                    }
                    for cube in data["RESPONSE"]["CUBES"]
                ]

                self.all_tables = data["RESPONSE"]["CUBES"]

                logger.debug(InfoLogs.KYVOS_API_RESPONSE.format(tool=Tools.LIST_SEMANTIC_MODELS, response=data))
                logger.info(InfoLogs.FETCHED_TABLES_FROM_FOLDER.format(count=len(filtered_cubes), folder=folder))
                return filtered_cubes
            
        except httpx.HTTPStatusError as e:
            logger.error(ErrorLogs.HTTP_ERROR_FETCHING_TABLES.format(url=url, error=e), exc_info=True)
            raise ValueError(ExceptionMessages.HTTP_ERROR_FETCHING_TABLES.format(error_message=e.response.text)) from e

        except httpx.RequestError as e:
            logger.error(ErrorLogs.NETWORK_CONNECTION_ERROR.format(url=url, error=e), exc_info=True)
            raise ConnectionError(ExceptionMessages.NETWORK_CONNECTION_ERROR) from e

        except Exception as e:
            logger.error(ErrorLogs.UNEXPECTED_ERROR_LISTING_TABLES, exc_info=True)
            raise RuntimeError(ExceptionMessages.UNEXPECTED_ERROR_LISTING_TABLES) from e
    
    async def list_semantic_model_columns(self, table_name: str, folder_name: Optional[str] = None, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """List all columns for a given table and folder in Kyvos.
        
        Args:
            table_name: Name of the semantic model (table)
            folder_name: Name of the folder containing the semantic model.
                         Defaults to the configured default folder.
            
        Returns:
            Dictionary containing column metadata for the specified table
            
        Raises:
            httpx.HTTPError: If the API request fails
        """

        folder = folder_name or self.default_folder

        raw_data_query = False  # default fallback

        if self.all_tables is None:
            logger.debug(DebugLogs.ALL_TABLES_NONE.format(table_name))
            logger.debug(DebugLogs.RAW_QUERY_DEFAULT_VALUE)
        elif not isinstance(self.all_tables, list):
            logger.debug(DebugLogs.ALL_TABLES_NOT_LIST.format(table_name))
            logger.debug(DebugLogs.RAW_QUERY_DEFAULT_VALUE)
        elif not self.all_tables:
            logger.debug(DebugLogs.ALL_TABLES_EMPTY.format(table_name))
            logger.debug(DebugLogs.RAW_QUERY_DEFAULT_VALUE)
        else:
            logger.debug(DebugLogs.CHECKING_RAW_QUERY_PERMISSION.format(table_name))

            for table in self.all_tables:
                if table.get('NAME') == table_name:
                    if 'ALLOW_RAW_DATA_QUERY' not in table:
                        logger.debug(DebugLogs.RAW_QUERY_DEFAULT_VALUE)
                        raw_data_query = False
                    else:
                        value = table.get('ALLOW_RAW_DATA_QUERY', None) 

                        logger.debug(DebugLogs.TABLE_MATCHED_WITH_FLAG.format(table_name=table_name, value=repr(value)))
                        
                        # Strict check: only treat `True` (boolean True) as true
                        if isinstance(value, bool):
                            raw_data_query = value
                            logger.info(DebugLogs.RAW_QUERY_PERMISSION_SET.format(table_name=table_name, raw_data_query=raw_data_query))
                        else:
                            logger.debug(DebugLogs.RAW_QUERY_UNEXPECTED_VALUE.format(value=repr(value)))
                            raw_data_query = False
                    break
        
        version= self.version
        url = f"{self.base_url}{KyvosEndpoints.SQL_METADATA.format(version=version)}"
        
        params = {
            "smodelName": table_name,
            "folderName": folder
        }
        
        headers = {"Accept": "application/json"}

        if auth_token:
            headers[HeaderKeys.AUTHORIZATION] = auth_token
            headers["appType"] = "PUBLIC"
        else:
            headers[HeaderKeys.AUTHORIZATION] = self.auth._auth_header

        logger.debug(InfoLogs.KYVOS_API_REQUEST_URL.format(tool=Tools.LIST_SEMANTIC_MODEL_COLUMNS, url=url))
        logger.debug(InfoLogs.KYVOS_API_REQUEST_PAYLOAD.format(tool=Tools.LIST_SEMANTIC_MODEL_COLUMNS, payload=params))
        logger.info(InfoLogs.FETCHING_COLUMNS.format(table_name=table_name, folder=folder))
        
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if self.verify_ssl else False 

        try:
            async with httpx.AsyncClient(timeout= None,verify=ctx) as client:
                response = await client.get(
                    url, 
                    params=params, 
                    headers=headers, 
                )

                if response.is_error:
                    try:
                        error_json = response.json()
                        error_message = error_json.get("MESSAGE", response.text)
                    except ValueError:
                        error_message = response.text

                    logger.error(
                        ErrorLogs.CLIENT_ERROR_EXCEPTION.format(error_message=error_message, url=url),
                        exc_info=True
                    )

                    if response.status_code == 401 and "token has expired" in error_message.lower():
                        logger.info(InfoLogs.REFRESHING_ACCESS_TOKEN)
                        return error_message.lower()

                    raise ValueError(ErrorLogs.CLIENT_ERROR_EXCEPTION.format(error_message=error_message, url=url))
            
                data = response.json()
                filtered_columns = []

                for column in data:
                    if column.get("visible", False):
                        filtered_column = {
                            "name": column["name"]
                        }
                        description = column.get("description", "")
                        if description.strip():  # Only add if non-empty and not just whitespace
                            filtered_column["description"] = description
                        summaryFunction = column.get("summaryFunction", "")
                        if summaryFunction.strip():  # Only add if non-empty and not just whitespace
                            filtered_column["summaryFunction"] = summaryFunction
                        dataType = column.get("dataType", "")
                        if dataType.strip():  # Only add if non-empty and not just whitespace
                            filtered_column["dataType"] = dataType
                        filtered_columns.append(filtered_column)

                logger.debug(InfoLogs.KYVOS_API_RESPONSE.format(tool=Tools.LIST_SEMANTIC_MODEL_COLUMNS, response=data))
                logger.info(InfoLogs.FETCHED_COLUMNS.format(table_name=table_name, columns=filtered_columns))
                return filtered_columns, raw_data_query
                
        except httpx.HTTPStatusError as e:
            logger.error(ErrorLogs.HTTP_ERROR_COLUMNS.format(table_name=table_name, error=e), exc_info=True)
            raise ValueError(ExceptionMessages.HTTP_ERROR_COLUMNS.format(details=e.response.text)) from e

        except httpx.RequestError as e:
            logger.error(ErrorLogs.NETWORK_ERROR_COLUMNS.format(table_name=table_name, error=e), exc_info=True)
            raise ConnectionError(ExceptionMessages.NETWORK_ERROR_COLUMNS) from e

        except Exception as e:
            logger.error(ErrorLogs.UNEXPECTED_ERROR_COLUMNS.format(table_name=table_name, error=e), exc_info=True)
            raise RuntimeError(ExceptionMessages.UNEXPECTED_ERROR_COLUMNS) from e
    
    async def execute_query(self, query: str, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Execute an SQL query on Kyvos.
        
        Args:
            query: SQL query to execute
            auth_token: Optional authentication token
            
        Returns:
            Dictionary containing the query results
            
        Raises:
            httpx.HTTPError: If the API request fails
        """

        url = f"{self.base_url}{KyvosEndpoints.EXPORT_QUERY.format(version=version)}"
    
        headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        
        if auth_token:
            headers[HeaderKeys.AUTHORIZATION] = auth_token
            headers["appType"] = "PUBLIC"
        else:
            headers[HeaderKeys.AUTHORIZATION] = self.auth._auth_header
        
        max_rows= self.max_rows
        data = {
            "queryType": "SQL",
            "outputFormat" : "JSON",
            "query": query,
            "maxRows": max_rows
        }

        if self.flag:
            logger.info(InfoLogs.QUERY_RETRYING)
        
        logger.debug(InfoLogs.KYVOS_API_REQUEST_URL.format(tool=Tools.EXECUTE_QUERY, url=url))
        logger.debug(InfoLogs.KYVOS_API_REQUEST_PAYLOAD.format(tool=Tools.EXECUTE_QUERY, payload=data))
        logger.info(InfoLogs.QUERY_EXECUTING.format(query=query))

        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if self.verify_ssl else False 
        
        try:
            async with httpx.AsyncClient(timeout=None,verify=ctx) as client:
                response = await client.post(
                    url, 
                    data=data, 
                    headers=headers, 
                )

                if response.is_error:
                    error_json = response.json()
                    error_message = error_json.get("MESSAGE", response.text)
                    
                    if response.status_code == 401 and "token has expired" in error_message.lower():
                        logger.info(InfoLogs.REFRESHING_ACCESS_TOKEN)
                        return error_message.lower()
                    
                    logger.error(ErrorLogs.SQL_ERROR_WITH_RESPONSE.format(response=response.text, query=query))
                    logger.error(ErrorLogs.QUERY_EXECUTION_FAILED)
                    self.flag = True
                    return f"Last time the SQL you generated failed with error : '{response.text}'. Please generate another spark SQL that works as per guidance."
                
                try:
                    result = response.json()
                    logger.debug(InfoLogs.KYVOS_API_RESPONSE.format(tool=Tools.EXECUTE_QUERY, response=result))
                    logger.info(InfoLogs.QUERY_SUCCESS)
                    return result
                except Exception:
                    raise ValueError("Failed to parse response JSON.")
                 
        except httpx.HTTPStatusError as e:
            logger.error(ErrorLogs.HTTP_ERROR_EXECUTING_QUERY.format(query=query, error=e.response.text), exc_info=True)
            raise ValueError(ExceptionMessages.HTTP_STATUS_ERROR.format(code=e.response.status_code, text=e.response.text)) from e

        except httpx.RequestError as e:
            logger.error(ErrorLogs.NETWORK_ERROR_EXECUTING_QUERY.format(query=query, error=e), exc_info=True)
            raise ConnectionError(ExceptionMessages.NETWORK_ERROR) from e

        except Exception as e:
            logger.error(ErrorLogs.UNEXPECTED_ERROR_EXECUTING_QUERY.format(query=query, error=e), exc_info=True)
            raise RuntimeError(ExceptionMessages.UNEXPECTED_ERROR) from e