# 远程配置
```json
{
  "mcpServers": {
    "work-tool-mcp": {
      "name": "work-tool-mcp",
      "command": "uvx",
      "args": [ "work-tool-mcp", "stdio" ]
    }
  }
}
```
# 本地配置
```json
{
  "mcpServers": {
    "work-tool-mcp": {
      "name": "work-tool-mcp",
      "command": "uv",
      "args": [ 
        "--directory",
        "/Users/Vint/仓库/mcp/work-tool-mcp-server/src/work_tool_mcp",
        "run" 
      ]
    }
  }
}
```