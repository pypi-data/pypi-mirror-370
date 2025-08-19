# Google Drive MCP

A Model Context Protocol (MCP) server that provides Google Drive integration for AI assistants like Claude.


```json

{
  "mcpServers": {
    "google-drive": {
      "env": {
        "GOOGLE_ACCESS_TOKEN": "GOOGLE_ACCESS_TOKEN",
        "GOOGLE_REFRESH_TOKEN": "GOOGLE_REFRESH_TOKEN",
        "GOOGLE_CLIENT_ID": "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET": "GOOGLE_CLIENT_SECRET"
      },
      "command": "uvx",
      "args": [
        "google-drive-mcpserver"
      ]
    }
  }
}
```