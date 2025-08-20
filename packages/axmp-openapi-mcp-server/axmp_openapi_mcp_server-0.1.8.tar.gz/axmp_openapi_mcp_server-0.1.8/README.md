# MCP Inspector CLI for lowlevel server
```bash
$ npx @modelcontextprotocol/inspector uv --directory /Users/kks/IdeaProjects/aiops/axmp-openapi-mcp-server run axmp-openapi-mcp-server --transport stdio --endpoint https://api.ags.cloudzcp.net --access-key xxx --spec-path /Users/kks/IdeaProjects/aiops/axmp-openapi-mcp-server/openapi/zmp_mixed_api_spec.json
```

# fastmcp cli command
```bash
$ mcp dev src/axmp_openapi_mcp_server/fastmcp/zcp_alert_manager.py
$ mcp run src/axmp_openapi_mcp_server/fastmcp/zcp_alert_manager.py -t sse
$ mcp install src/axmp_openapi_mcp_server/fastmcp/zcp_alert_manager.py --name alert-manager --with zmp-openapi-toolkit,pyyaml
```

# How to run the lowlevel.server
## streamable-http
```bash
axmp-openapi-mcp-server --port 21000 --transport streamable-http \
--server-name axmp-mixed-openapi-mcp-server \
--profile-base-path /Users/kks/IdeaProjects/ai_agent_studio/axmp-openapi-mcp-server/mcp_profiles \
--profile-id=683734a65b3c20f3b1a4f721
```

## stdio
first install the axmp-openapi-mcp-server
```bash
pip install axmp-openapi-mcp-server
```

local test
```bash
axmp-openapi-mcp-server \
--transport stdio \
--profile-base-path /Users/kks/IdeaProjects/ai_agent_studio/axmp-openapi-mcp-server/mcp_profiles \
--profile-id 683734a65b3c20f3b1a4f721 \
--backend-server-auth-configs zcp-alert-backend:X-Access-Key=zmp-09bae73d-9f59-491a-ae06-7747e8f79883,zcp-mcm-backend:X-Access-Key=zmp-09bae73d-9f59-491a-ae06-7747e8f79883
```

then configure the mcp server into the mcp host like claude desktop or cursor
```json
{
  "mcpServers": {
    "axmp-openapi-mcp-server": {
      "command": "python3",
      "args": [
        "-m",
        "axmp_openapi_mcp_server",
        "--transport",
        "stdio",
        "--profile-base-path",
        "/Users/kks/IdeaProjects/ai_agent_studio/axmp-openapi-mcp-server/mcp_profiles",
        "--profile-id",
        "683734a65b3c20f3b1a4f721",
        "--backend-server-auth-configs",
        "zcp-alert-backend:X-Access-Key=zmp-09bae73d-9f59-491a-ae06-7747e8f79883,zcp-mcm-backend:X-Access-Key=zmp-09bae73d-9f59-491a-ae06-7747e8f79883"
      ]
    }
  }
}
```


# backup the claude desktop mcp conf
```json
{
  "mcpServers": {
    "axmp-openapi-mcp-server": {
      "command": "python3",
      "args": [
        "-m",
        "axmp_openapi_mcp_server",
        "--transport",
        "stdio",
        "--endpoint",
        "https://api.ags.cloudzcp.net",
        "--access-key",
        "xxxx",
        "--spec-path",
        "/Users/kks/IdeaProjects/aiops/axmp-openapi-mcp-server/openapi/zmp_mixed_api_spec.json"
      ]
    },
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@0.1.4"],
      "env": {
        "TAVILY_API_KEY": "xxxxx"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/kks/Desktop"
      ]
    }
  }
}
 ```