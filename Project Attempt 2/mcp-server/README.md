# MCP Server (OpenAPI Navigator)

This tiny MCP server exposes tools that read `../openapi/openapi.yaml` so an agent/IDE can quickly look up endpoints and schemas.

## Run

```bash
cd mcp-server
python -m venv .venv
source .venv/bin/activate
pip install fastmcp pyyaml
python server.py
```

## Tools
- `list_paths()` → returns available OpenAPI paths
- `get_path(path, method)` → returns operation info (summary, params, request/response schemas)
