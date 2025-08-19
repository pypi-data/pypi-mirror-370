from pydantic_settings import BaseSettings, SettingsConfigDict
from mcp.server.fastmcp import FastMCP, Context
from typing import Any, Optional
from datetime import datetime
import traceback
import logging
import asyncio
import os
from pathlib import Path

from dtlpymcp.utils.dtlpy_context import DataloopContext, SOURCES_FILEPATH

# Setup logging to both console and file with timestamp
log_dir = Path.home() / ".dataloop" / "mcplogs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

# Remove any existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# File handler with timestamp
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
)

# Console handler (default format)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(fmt="[%(levelname)s] %(name)s: %(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger("[DATALOOP-MCP]")


class ServerSettings(BaseSettings):
    """Settings for the Dataloop MCP server."""

    model_config = SettingsConfigDict(env_prefix="MCP_DATALOOP_")

    def __init__(self, **data):
        super().__init__(**data)


def create_dataloop_mcp_server(settings: ServerSettings, sources_file: str) -> FastMCP:
    """Create a FastMCP server for Dataloop with Bearer token authentication."""
    app = FastMCP(
        name="Dataloop MCP Server",
        instructions="A multi-tenant MCP server for Dataloop with authentication",
        stateless_http=True,
        debug=True,
    )
    dl_context = DataloopContext(token=os.environ.get('DATALOOP_API_KEY'), 
                                 env=os.environ.get('DATALOOP_ENV', 'prod'),
                                 sources_file=sources_file)
    
    # Initialize the Dataloop context
    asyncio.run(dl_context.initialize())
    
    @app.tool(description="Test tool for health checks")
    async def test(ctx: Context, ping: Any = None) -> dict[str, Any]:
        """Health check tool. Returns status ok and echoes ping if provided."""
        result = {"status": "ok"}
        if ping is not None:
            result["ping"] = ping
        return result

    logger.info(f"Adding tools from {len(dl_context.mcp_sources)} sources")

    for source in dl_context.mcp_sources:
        logger.info(f"Adding tools from source: {source.dpk_name}")
        for tool in source.tools:
            app._tool_manager._tools[tool.name] = tool
            logger.info(f"Registered tool: {tool.name}")
    
    return app


def main(sources_file: Optional[str] = None) -> int:
    logger.info("Starting Dataloop MCP server in stdio mode")
    try:
        settings = ServerSettings()
        logger.info("Successfully configured Dataloop MCP server")
    except Exception as e:
        logger.error(f"Unexpected error during startup:\n{e}")
        return 1
    try:
        if sources_file is None:
            sources_file = SOURCES_FILEPATH
        logger.info(f"Using sources file: {sources_file}")
        mcp_server = create_dataloop_mcp_server(settings, sources_file)
        logger.info("Starting Dataloop MCP server in stdio mode")
        mcp_server.run(transport="stdio")
        return 0
    except Exception:
        logger.error(f"Failed to start MCP server: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    main()
