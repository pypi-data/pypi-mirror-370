# Apollo.io MCP

This project provides an MCP server that exposes the Bannerbear API functionalities as tools.
It allows you to interact with the Bannerbear API using the Model Context Protocol (MCP).



```json

{
  "mcpServers": {
    "bannerbear": {
      "env": {
        "BANNERBEAR_API_KEY": "BANNERBEAR_API_KEY"
      },
      "command": "uvx",
      "args": [
        "bannerbear-mcp"
      ]
    }
  }
}
```