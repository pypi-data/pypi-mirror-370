## MCP Kyvos Server

The **MCP Kyvos Server** enables agentic applications to interact with the Kyvos platform for querying business data. It supports two transport modes:

- **SSE (Server-Sent Events)**: This transport is suited for remote integrations. It uses HTTP requests for communication. It allows servers to handle multiple client connections efficiently. SSE mode supports both Basic and OAuth authorization. OAuth requires users to authenticate using their Kyvos credentials before establishing a connection, providing a secure and standardized login mechanism.
- **STDIO (Standard I/O)**: This transport is primarily used for inter-process communication within the same system. It’s particularly suitable for command-line tools and local integrations where the client and server operate within the same process. Only Basic authorization is supported in this mode.

---

## Tools

The MCP Kyvos server exposes the following tools:

1. **`kyvos_list_semantic_model`**
   - **Description:** Lists available semantic model with schema details.

2. **`kyvos_list_semantic_model_columns`**
   - **Description:** Retrieves column metadata for a specified semantic model.

3. **`kyvos_sql_generation_prompt`**
   - **Description:** Provides the system prompt template for SQL generation.

4. **`kyvos_execute_query`**
   - **Description:** Executes a Spark SQL query on Kyvos and returns a json based result set.

## Installation

### Using uv (Recommended)

When using uv, no specific installation is needed. We will use `uvx` to directly run `mcp-kyvos-server`.

> **Note:** Make sure you have `uv` installed. See the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Using pip

Install the `mcp-kyvos-server` package from pip:

```bash
pip install mcp-kyvos-server
```

## Configuration & Parameters

The server can be configured via environment variables or command-line flags. CLI flags override environment variables.

| Parameter                      | Environment Variable   | CLI Flag                             | Required | Default Value                 | Description                                                                                                                                                            |
|--------------------------------|------------------------|--------------------------------------|:--------:|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Kyvos URL                      | `KYVOS_URL`            | `--kyvos-url <url>`                  |   Yes    | —                             | The base URL of the Kyvos server. Example: `https://<server-address>:<port>/kyvos`                                                                                     |
| Kyvos Username                 | `KYVOS_USERNAME`       | `--kyvos-username <username>`        |   Yes    | —                             | The Kyvos account username used to authenticate and log in to the Kyvos application. Will be overridden if using OAuth or basic-auth flow                              |
| Kyvos Password                 | `KYVOS_PASSWORD`       | `--kyvos-password <password>`        |   Yes    | —                             | The corresponding password for the provided `KYVOS_USERNAME`, used for authentication with the Kyvos application. Will be overridden if using OAuth or basic-auth flow |
| Prompt File Path               | `KYVOS_PROMPT_FILE`    | `--kyvos-prompt-file <file_path>`    |    No    | —                             | Path to the `.txt` file containing the prompt for Spark SQL generation                                                                                                 |
| Default Folder                 | `KYVOS_DEFAULT_FOLDER` | `--kyvos-default-folder <folder>`    |    No    | —                             | Folder containing multiple semantic models used for querying and metadata management in the Kyvos platform                                                             |
| Transport                      | —                      | `--transport <stdio or sse>`         |    No    | `stdio`                       | The type of communication transport to use: `stdio` for standard input/output or `sse` for Server-Sent Events                                                          |
| SSL Verification               | `VERIFY_SSL`           | `--verify-ssl <true or false>`       |    No    | `false`                       | Flag to enable or disable SSL certificate verification when making HTTP requests to Kyvos                                                                              |
| Max Rows                       | `MAX_ROWS`             | `--max-rows <max_rows>`              |    No    | 1000                          | Limit the number of rows in the query response                                                                                                                         |
| Environment File               | —                      | `--env-file <file_path>`             |    No    | —                             | Path to an `.env` file from which to load environment variables                                                                                                        |
| SSL Key                        | `SSL_KEY_FILE`         | `--ssl-key-file <file_path>`         |    No    | —                             | Path to the SSL private key file used to enable HTTPS on the server                                                                                                    |
| SSL Certificate                | `SSL_CERTIFICATE_FILE` | `--ssl-certificate-file <file_path>` |    No    | —                             | Path to the SSL certificate file used to enable HTTPS on the server                                                                                                    |
| Auth Type                      | `SERVER_AUTH_TYPE`     | `--server-auth-type <basic/oauth>`   |    No    | `basic`                       | Type of authorization to start the server with                                                                                                                         |
| Port                           | —                      | `--port <port>`                      |    No    | 8000                          | Port on which to run the server                                                                                                                                        |
| MCP Server URL                 | `MCP_SERVER_URL`       | `--mcp-server-url <url>`             |   Yes    | -                             | The full URL where the MCP server will run (e.g., http://mcp.server:9090)                                                                                                    |
| MCP Kyvos Server Database Path | `MCP_KYVOS_DB_PATH`    | —                                    |    No    | `HOME_PATH/.mcp_kyvos_server` | The path where the MCP server database will be created                                                                                                                 |
| Log Level                      | —                      | `--log-level`                        |    No    | `DEBUG`                       | Specifies the log level to use (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).                                                                                          |

## Sample `.env` File

Create a `.env` file with the required parameters for your MCP-Kyvos server:

```env
KYVOS_URL=https://kyvos.cloud/kyvos
KYVOS_USERNAME=your-username
KYVOS_PASSWORD=your-password
KYVOS_DEFAULT_FOLDER=Business Catalog
```

## Usage

### SSE Mode

1. **Start the MCP server** with SSE transport.

   Using env file:
   ```bash
   mcp-kyvos-server --transport sse --env-file /path/to/.env
   ```

   Or provide arguments directly:
   ```bash
   mcp-kyvos-server \
     --kyvos-url https://your-kyvos-endpoint \
     --kyvos-username user123 \
     --kyvos-password pass123 
   ```

2. **Configure your client application** to include the SSE server in its MCP server configuration:

   ```json
   {
     "mcpServers": {
       "kyvos-sse": {
         "url": "http://<machine_ip>:<port>/sse"
       }
     }
   }
   ```

### STDIO Mode

Configure your client application as follows:

#### Using uvx:

```json
{
  "mcpServers": {
    "kyvos-stdio": {
      "command": "uvx",
      "args": [
        "mcp-kyvos-server",
        "--env-file", 
        "/path/to/.env"
      ]
    }
  }
}
```

#### Using pip:

```json
{
  "mcpServers": {
    "kyvos-stdio": {
      "command": "python3",
      "args": [
        "-m", 
        "mcp_kyvos_server", 
        "--env-file", 
        "/path/to/.env"
      ]
    }
  }
}
```

> **Note:** If using a virtual environment, provide the full path to the environment's `python` executable (`/path/to/venv/python3`). On Windows, replace `python3` with `python`.


## Claude Desktop Usage

### STDIO Mode Configuration

#### Using `uvx` 

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kyvos-stdio": {
      "command": "uvx",
      "args": [
        "mcp-kyvos-server", 
        "--env-file", 
        "/full/path/to/.env"
      ]
    }
  }
}
```

#### Using `pip`

If you've installed `mcp-kyvos-server` via `pip`:
```
pip install mcp-kyvos-server
```
**Use Python module directly**

```json
{
  "mcpServers": {
    "kyvos-stdio": {
      "command": "python3",
      "args": [
        "-m", 
        "mcp_kyvos_server", 
        "--env-file", 
        "/full/path/to/.env"
      ]
    }
  }
}
```

> **Note:** If using a virtual environment, provide the full path to the environment's `python` executable (`/path/to/venv/python3`). On Windows, replace `python3` with `python`.


### SSE Mode Support (Remote)

> **Important:** Claude Desktop does *not* natively support SSE (Server-Sent Events). It only supports `stdio` transport.

To connect Claude Desktop to a **remote SSE MCP server**, use [`mcp-remote`](https://github.com/geelen/mcp-remote), a CLI tool that bridges remote SSE servers to local stdio clients.

#### Setup with `mcp-remote`

1. **Install Node.js (v18 or higher)** - [Download here](https://nodejs.org)

2. **Configure Claude Desktop to use `mcp-remote` via `npx`:**

   ```json
   {
     "mcpServers": {
       "mcp-server": {
         "command": "npx",
         "args": [
           "mcp-remote",
           "http://<your-machine-ip>:<port>/sse",
           "--allow-http"
         ]
       }
     }
   }
   ```
   
   > **Note:** Replace `<your-machine-ip>` and `<port>` with the actual address of your SSE server. Use the `--allow-http` flag if using HTTP-based MCP server URL.

> After saving the configuration file, completely quit Claude Desktop and restart it. The application needs to restart to load the new configuration and start the MCP server.

**Note**: If you encounter an **OAuth authorization error**, try the following steps:
1. **Delete the `.mcp-auth` folder**  
    - On **Linux/macOS**:  
      ```bash
      ~/.mcp-auth
      ```  
    - On **Windows** (Command Prompt):  
      ```
      C:\Users\<your-username>\.mcp-auth
      ```

2. **Restart the `mcp-kyvos-server`**

## Gemini CLI Usage

### STDIO Mode Configuration

To integrate `mcp-kyvos-server` with **Gemini CLI**, use the STDIO transport mode. This allows Gemini to spawn and communicate with the MCP Kyvos server locally.

#### Using `uvx`

In your Gemini CLI configuration file (e.g., `~/.gemini/config.json`), add the following MCP server entry:

```json
{
  "mcpServers": {
    "kyvos-stdio": {
      "command": "uvx",
      "args": [
        "mcp-kyvos-server", 
        "--env-file", 
        "/full/path/to/.env"
      ]
    }
  }, 
  "theme": "Default",
  "selectedAuthType": "oauth-personal"
}
```

#### Using `pip`

If you've installed `mcp-kyvos-server` via `pip`:
```
pip install mcp-kyvos-server
```
** Use Python module directly**

```json
{
  "mcpServers": {
    "kyvos-stdio": {
      "command": "python3",
      "args": [
        "-m", 
        "mcp_kyvos_server", 
        "--env-file", 
        "/full/path/to/.env"
      ]
    }
  },
  "theme": "Default",
  "selectedAuthType": "oauth-personal"
}
```


### SSE Mode Support (Remote)

> **Important:** Gemini Cli does *not* natively support SSE (Server-Sent Events). It only supports `stdio` transport.

To connect Gemini Cli to a **remote SSE MCP server**, use [`mcp-remote`](https://github.com/geelen/mcp-remote), a CLI tool that bridges remote SSE servers to local stdio clients.

#### Setup with `mcp-remote`

1. **Install Node.js (v18 or higher)** - [Download here](https://nodejs.org)

2. **Configure Claude Desktop to use `mcp-remote` via `npx`:**

   ```json
   {
     "mcpServers": {
       "mcp-server": {
         "command": "npx",
         "args": [
           "mcp-remote",
           "http://<your-machine-ip>:<port>/sse",
           "--allow-http"
         ]
       }
     },
     "theme": "Default",
     "selectedAuthType": "oauth-personal"
   }
   ```

   > **Note:** Replace `<your-machine-ip>` and `<port>` with the actual address of your SSE server. Use the `--allow-http` flag if using HTTP-based MCP server URL.

**Note**: If you encounter an **OAuth authorization error**, try the following steps:
1. **Delete the `.mcp-auth` folder**  
    - On **Linux/macOS**:  
      ```bash
      ~/.mcp-auth
      ```  
    - On **Windows** (Command Prompt):  
      ```
      C:\Users\<your-username>\.mcp-auth
      ```

2. **Restart the `mcp-kyvos-server`**

## License

This project is licensed under the MIT License.