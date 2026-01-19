from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = ROOT / "openapi" / "openapi.yaml"

mcp = FastMCP("OpenAPI Navigator")


def _load() -> dict[str, Any]:
    return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))


@mcp.tool
def list_paths() -> list[str]:
    """List all API paths from openapi.yaml"""
    spec = _load()
    return sorted(list((spec.get("paths") or {}).keys()))


@mcp.tool
def get_operation(path: str, method: str) -> dict[str, Any]:
    """Return the OpenAPI operation object for (path, method)."""
    spec = _load()
    paths = spec.get("paths") or {}
    item = paths.get(path)
    if not item:
        return {"error": "path not found", "path": path}
    op = item.get(method.lower())
    if not op:
        return {"error": "method not found", "path": path, "method": method}
    return op


if __name__ == "__main__":
    mcp.run()
