# Strapi MCP Server

An MCP server for interacting with Strapi CMS.

## Installation

You can install the server using pip:

```bash
pip install strapi-mcp-server
```

## Configuration

Before using the server, you need to create a configuration file at `~/.mcp/strapi-mcp-server.config.json`.

1.  Create the directory:
    ```bash
    mkdir -p ~/.mcp
    ```

2.  Create the configuration file:
    ```bash
    touch ~/.mcp/strapi-mcp-server.config.json
    ```

3.  Add your Strapi server details to the file. You can add multiple servers.

    ```json
    {
      "prodserver": {
        "api_url": "https://your-strapi-instance.com",
        "api_key": "your-strapi-api-key"
      },
      "localserver": {
        "api_url": "http://localhost:1337",
        "api_key": "your-local-api-key"
      }
    }
    ```

## Usage

Once installed and configured, you can run the server from your terminal:

```bash
strapi-mcp-server
```

This will start the MCP server, and you can then interact with it using an MCP client.
