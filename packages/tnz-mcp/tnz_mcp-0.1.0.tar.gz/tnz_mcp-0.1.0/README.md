# TNZ MCP Server

A Python package to run an MCP (Model Context Protocol) server for TNZ API, enabling integration with Claude Desktop and Gemini CLI.

## User Installation Guide

This guide provides step-by-step instructions to install and configure the TNZ MCP server for use with Claude Desktop and Gemini CLI, including how to set up a `config.json` file to register the MCP server.

### Step 1: Install Python
Ensure you have Python 3.9, 3.10, 3.11, or 3.12 installed. Verify with:
```bash
python --version
```
Download Python from [python.org](https://www.python.org) if needed.

### Step 2: Install the Package
Install the `tnz_mcp` package using pip:
```bash
pip install tnz_mcp
```
This installs the package and its dependencies (`tnzapi>=2.4.1`, `mcp>=1.0.0`).

### Step 3: Set TNZ AuthToken
The TNZ MCP server requires a TNZ API AuthToken. Set it via:
- **Environment Variable**:
  ```bash
  export TNZ_AUTH_TOKEN="Your-Auth-Token-Here"
  ```
  Replace `Your-Auth-Token-Here` with your actual TNZ API token.
- **Config File** (alternative):
  Create a `tnz_mcp.ini` file in your working directory:
  ```ini
  [TNZ]
  AuthToken = Your-Auth-Token-Here
  ```

### Step 4: Run the MCP Server
The server can run in **stdio** (default, for local CLI integration) or **HTTP** (for remote access).

- **Stdio Mode**:
  ```bash
  tnz-mcp
  ```
  This starts the server using stdio, ideal for local use with Gemini CLI or Claude Desktop.

- **HTTP Mode**:
  ```bash
  tnz-mcp --transport streamable-http --host localhost --port 8000
  ```
  This starts the server on `http://localhost:8000`, suitable for remote or multi-client access.

### Step 5: Configure Claude Desktop
Claude Desktop supports MCP servers via a `config.json` file or its settings UI. Verify Claude Desktop’s documentation for stdio support, as HTTP is more commonly used.

1. **Locate or Create `config.json`**:
   - Check Claude Desktop’s settings UI or documentation for the configuration file path (e.g., `~/.anthropic/config.json` on Linux/Mac or `%USERPROFILE%\.anthropic\config.json` on Windows).
   - If it doesn’t exist, create a `config.json` file in the specified directory.

2. **Add TNZ MCP Server**:
   - **Via `config.json`**:
     - For **Stdio**:
       ```json
        {
          "mcpServers": {
            "tnz-mcp": {
              "command": "tnz-mcp",
              "transport": "stdio",
              "env": {
                "TNZ_AUTH_TOKEN": "Your-Auth-Token-Here"
              }
            }
          }
        }
       ```
       Ensure `tnz-mcp` is installed and accessible in your PATH.
     - For **HTTP**:
       ```json
       {
         "mcpServers": {
           "tnz-mcp": {
             "command": "tnz-mcp",
             "transport": "http",
             "url": "http://localhost:8000",
             "env": {
                "TNZ_AUTH_TOKEN": "Your-Auth-Token-Here"
             }
           }
         }
       }
       ```
       Ensure the server is running with `tnz-mcp --transport streamable-http --host localhost --port 8000`.
   - **Via Settings UI** (alternative):
     - Open Claude Desktop’s settings or preferences.
     - Navigate to the tools or integrations section.
     - Add a new MCP tool with:
       - Name: `tnz_mcp`
       - Transport: `stdio` or `http`
       - Command: `tnz-mcp` (for stdio) or URL: `http://localhost:8000` (for HTTP)
     - Save the configuration.

3. **Restart Claude Desktop**:
   Restart Claude to load the configuration.

4. **Verify Integration**:
   Test with a command like:
   - **Natural Language**:
     ```
     Send an SMS to +64211231234 with message "Test from Claude" using TNZ
     ```
   - **Structured Tool Call** (if supported):
     ```json
     {
       "tool": "tnz_mcp.send_sms",
       "parameters": {
         "reference": "Test",
         "message_text": "Test from Claude",
         "recipients": ["+64211231234"]
       }
     }
     ```
   Check Claude’s documentation for exact syntax.

5. **Troubleshooting**:
   - Ensure the server is running before launching Claude.
   - Verify the AuthToken is valid (check `tnz_mcp.ini` or environment variable).
   - If stdio fails, try HTTP mode, as it’s more widely supported.
   - Consult Anthropic’s documentation for error logs or advanced configuration.

### Step 6: Configure Gemini CLI
Gemini CLI supports MCP servers via a `config.json` file or command-line options.

1. **Locate or Create `config.json`**:
   - Find Gemini CLI’s configuration directory (e.g., `~/.gemini/config.json` on Linux/Mac or `%USERPROFILE%\.gemini\config.json` on Windows). Refer to Gemini CLI’s documentation for the exact path.
   - Create a `config.json` file if it doesn’t exist.

2. **Add TNZ MCP Server**:
   - For **Stdio**:
     ```json
     {
       "mcpServers": [
         {
           "name": "tnz_mcp",
           "transport": "stdio",
           "command": "tnz-mcp"
         }
       ]
     }
     ```
     This tells Gemini CLI to run `tnz-mcp` as a stdio-based MCP server.

   - For **HTTP**:
     ```json
     {
       "mcpServers": [
         {
           "name": "tnz_mcp",
           "transport": "http",
           "url": "http://localhost:8000"
         }
       ]
     }
     ```
     Ensure the server is running in HTTP mode.

3. **Run Gemini CLI**:
   Connect to the MCP server:
   ```bash
   gemini connect mcp tnz_mcp
   ```
   Alternatively, use direct commands if supported:
   ```bash
   gemini run --mcp stdio --command tnz-mcp
   ```
   Check Gemini CLI’s documentation for exact syntax.

4. **Verify Integration**:
   Test with a command like:
   ```bash
   gemini run --mcp tnz_mcp --tool send_sms --args '{"reference": "Test", "message_text": "Test from Gemini", "recipients": ["+64211231234"]}'
   ```
   Adjust based on Gemini CLI’s tool-calling syntax.

**Note**: The `config.json` key names (`tools` for Claude Desktop, `mcpServers` for Gemini CLI) may vary depending on the tool’s version or configuration. Verify the exact key names in the respective documentation for Claude Desktop and Gemini CLI.

### Step 7: Test the Server
Test the MCP server using MCP Inspector:
```bash
npx @modelcontextprotocol/inspector --transport stdio
```
Or for HTTP:
```bash
npx @modelcontextprotocol/inspector --transport http --url http://localhost:8000
```
This verifies the server’s tools and responses.

## Usage

### Stdio Mode (Default)
Run the MCP server using stdio for local CLI-based integration:
```bash
tnz-mcp
```
This starts the server in stdio mode, suitable for Gemini CLI or local Claude Desktop integrations.

- **Gemini CLI**: Use `gemini connect mcp stdio` or a compatible wrapper. Check Gemini CLI documentation for exact syntax.
- **Claude Desktop**: Configure Claude to use stdio-based MCP tools (refer to Anthropic's documentation for setup).

### HTTP Mode
Run the server over HTTP for remote access:
```bash
tnz-mcp --transport streamable-http --host localhost --port 8000
```

- **Claude Desktop**: Configure the MCP server URL (e.g., `http://localhost:8000`) in Claude's settings or `config.json`.
- **Gemini CLI**: Use `gemini connect mcp http://localhost:8000` or a compatible wrapper.

## Features

- **Messaging**: Send SMS, Email, Fax, TTS, and Voice messages.
- **Reports**: Check message status, SMS replies, and received messages.
- **Actions**: Abort, resubmit, reschedule jobs, and set pacing for voice/TTS.
- **Addressbook**: Manage contacts, groups, and relationships.
- **Security**: AuthToken loaded securely from environment or config file.

## Testing

Run unit tests:
```bash
python -m unittest discover tests
```

## License

MIT License. See `LICENSE` for details.
