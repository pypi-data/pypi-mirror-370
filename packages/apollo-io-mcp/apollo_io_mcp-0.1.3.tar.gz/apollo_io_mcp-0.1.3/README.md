# Apollo.io MCP

This project provides an MCP server that exposes the Apollo.io API functionalities as tools.
It allows you to interact with the Apollo.io API using the Model Context Protocol (MCP).



```json

{
  "mcpServers": {
    "apollo-io": {
      "env": {
        "APOLLO_API_KEY": "APOLLO_API_KEY"
      },
      "command": "uvx",
      "args": [
        "apollo-io-mcp"
      ]
    }
  }
}
```