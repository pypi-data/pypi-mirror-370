from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

def set_mcp(app: FastAPI, operations: list[str] = None, tags: list[str] = None) -> None:
    """
    Configura el MCP (Model Context Protocol) para la aplicación FastAPI.
    
    Args:
        app (FastAPI): La instancia de la aplicación FastAPI.
    """

    mcp = FastApiMCP(
        app,
        name="mcp-server",
        description="Server para el MCP de la aplicación",
        include_operations=operations,
        include_tags=tags
    )

    mcp.mount_http()