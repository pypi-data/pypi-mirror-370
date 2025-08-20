# 远程配置
```json
{
  "mcpServers": {
    "work-tool-mcp": {
      "name": "work-tool-mcp",
      "command": "uvx",
      "args": [ "work-tool-mcp"]
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
        "xxxx/src/work_tool_mcp",
        "run" 
      ]
    }
  }
}
```