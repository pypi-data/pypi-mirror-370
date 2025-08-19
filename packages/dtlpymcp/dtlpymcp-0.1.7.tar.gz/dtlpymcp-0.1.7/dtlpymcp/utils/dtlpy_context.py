from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase, FuncMetadata
from mcp.client.streamable_http import streamablehttp_client
from typing import Any, List, Tuple, Callable, Optional
from mcp.server.fastmcp.tools.base import Tool
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from pydantic import create_model
from datetime import timedelta
from mcp import ClientSession
import dtlpy as dl
import traceback
import requests
import logging
import asyncio
import time
import jwt
import json
from dtlpymcp import SOURCES_FILEPATH

# Utility to run async code from sync or async context
# If called from a running event loop, returns a Task (caller must handle it)
# If called from sync, blocks and returns result

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running
        return asyncio.run(coro)
    else:
        # Already running event loop
        return loop.create_task(coro)

logger = logging.getLogger(__name__)


class MCPSource(BaseModel):
    dpk_name: Optional[str] = None
    app_url: Optional[str] = None
    server_url: Optional[str] = None
    app_jwt: Optional[str] = None
    tools: Optional[List[Tool]] = []


class DataloopContext:
    """
    DataloopContext manages authentication, tool discovery, and proxy registration for Dataloop MCP servers.
    Handles JWTs, server URLs, and dynamic tool registration for multi-tenant environments.
    """

    def __init__(self, token: str = None, sources_file: str = None, env: str = 'prod'):
        self._token = token
        self.env = env
        self.mcp_sources: List[MCPSource] = []
        logger.info("DataloopContext initialized.")
        if sources_file is None:
            sources_file = SOURCES_FILEPATH
        self.sources_file = sources_file
        self.initialized = False
        
    
    async def initialize(self, force: bool = False):
        if not self.initialized or force:    
            await self.register_sources(self.sources_file)
            self.initialized = True

    async def register_sources(self, sources_file: str):
        with open(sources_file, "r") as f:
            data = json.load(f)
        logger.info(f"Loading MCP sources from {sources_file}")
        for entry in data:
            try:
                if not isinstance(entry, dict):
                    raise ValueError(f"Invalid source entry: {entry}")
                logger.info(f"Adding MCP source: {entry.get('dpk_name')}, url: {entry.get('server_url')}")
                await self.add_mcp_source(MCPSource(**entry))
            except Exception as e:
                logger.error(f"Failed to add MCP source: {entry}\n{traceback.format_exc()}")

    async def add_mcp_source(self, mcp_source: MCPSource):
        self.mcp_sources.append(mcp_source)
        if mcp_source.server_url is None:
            self.load_app_info(mcp_source)
        result = await self.list_source_tools(mcp_source)
        if result is None:
            raise ValueError(f"Failed to discover tools for source {mcp_source.dpk_name}")
        server_name, tools, call_fn = result
        for tool in tools.tools:
            tool_name = tool.name
            ns_tool_name = f"{server_name}.{tool_name}"
            description = tool.description
            input_schema = tool.inputSchema

            def build_handler(tool_name):
                async def inner(**kwargs):
                    fn = call_fn(tool_name, kwargs)
                    return await fn()

                return inner

            dynamic_pydantic_model_params = self.build_pydantic_fields_from_schema(input_schema)
            arguments_model = create_model(
                f"{tool_name}Arguments", **dynamic_pydantic_model_params, __base__=ArgModelBase
            )
            resp = FuncMetadata(arg_model=arguments_model)
            t = Tool(
                fn=build_handler(tool_name),
                name=ns_tool_name,
                description=description,
                parameters=input_schema,
                fn_metadata=resp,
                is_async=True,
                context_kwarg="ctx",
                annotations=None,
            )
            mcp_source.tools.append(t)
        tool_str = ", ".join([tool.name for tool in mcp_source.tools])
        logger.info(f"Added MCP source: {mcp_source.dpk_name}, Available tools: {tool_str}")

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token

    def load_app_info(self, source: MCPSource) -> None:
        """
        Get the source URL and app JWT for a given DPK name using Dataloop SDK.
        """
        try:
            dl.setenv(self.env)
            dl.client_api.token = self.token
            filters = dl.Filters(resource='apps')
            filters.add(field="dpkName", values=source.dpk_name)
            filters.add(field="scope", values="system")
            apps = list(dl.apps.list(filters=filters).all())
            if len(apps) == 0:
                raise ValueError(f"No app found for DPK name: {source.dpk_name}")
            if len(apps) > 1:
                logger.warning(f"Multiple apps found for DPK name: {source.dpk_name}, using first one")
            app = apps[0]
            logger.info(f"App: {app.name}")
            source.app_url = next(iter(app.routes.values()))
            session = requests.Session()
            response = session.get(source.app_url, headers=dl.client_api.auth)
            logger.info(f"App route URL: {response.url}")
            source.server_url = response.url
            source.app_jwt = session.cookies.get("JWT-APP")
        except Exception as e:
            logger.error(f"Failed getting app info: {traceback.format_exc()}")
            raise Exception(f"Failed getting app info: {traceback.format_exc()}") from e

    @staticmethod
    def is_expired(app_jwt: str) -> bool:
        """
        Check if the APP_JWT is expired.
        """
        try:
            decoded = jwt.decode(app_jwt, options={"verify_signature": False})
            if decoded.get("exp") < time.time():
                return True
            return False
        except jwt.ExpiredSignatureError:
            return True
        except Exception as e:
            logger.error(f"Error decoding JWT: {e}")
            return True

    def get_app_jwt(self, source: MCPSource, token: str) -> str:
        """
        Get the APP_JWT from the request headers or refresh if expired.
        """
        if source.app_jwt is None or self.is_expired(source.app_jwt):
            try:
                session = requests.Session()
                response = session.get(source.app_url, headers={'authorization': 'Bearer ' + token})
                source.app_jwt = session.cookies.get("JWT-APP")
            except Exception:
                logger.error(f"Failed getting app JWT from cookies\n{traceback.format_exc()}")
                raise Exception(f"Failed getting app JWT from cookies\n{traceback.format_exc()}") from None
        if not source.app_jwt:
            logger.error(
                "APP_JWT is missing. Please set the APP_JWT environment variable or ensure authentication is working."
            )
            raise ValueError(
                "APP_JWT is missing. Please set the APP_JWT environment variable or ensure authentication is working."
            )
        return source.app_jwt

    @staticmethod
    def user_info(token: str) -> dict:
        """
        Decode a JWT token and return user info.
        """
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded

    async def list_source_tools(self, source: MCPSource) -> Tuple[str, List[dict], Callable]:
        """
        Discover tools for a given source and return (server_name, list_of_tools, call_fn).
        """
        if source.server_url is None:
            logger.error("DataloopContext required for DPK servers")
            raise ValueError("DataloopContext required for DPK servers")
        headers = {"Cookie": f"JWT-APP={source.app_jwt}",
                   "x-dl-info": f"{self.token}"}
        async with streamablehttp_client(source.server_url, headers=headers) as (read, write, _):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
                await session.initialize()
                tools = await session.list_tools()

                def call_fn(tool_name, kwargs):
                    async def inner():
                        async with streamablehttp_client(source.server_url, headers=headers) as (read, write, _):
                            async with ClientSession(
                                read, write, read_timeout_seconds=timedelta(seconds=60)
                            ) as session:
                                await session.initialize()
                                return await session.call_tool(tool_name, kwargs)

                    return inner

                logger.info(f"Discovered {len(tools.tools)} tools for source {source.dpk_name}")
                return (source.dpk_name, tools, call_fn)

    def openapi_type_to_python(self, type_str):
        return {"string": str, "integer": int, "number": float, "boolean": bool, "array": list, "object": dict}.get(
            type_str, str
        )

    def build_pydantic_fields_from_schema(self, input_schema):
        required = set(input_schema.get("required", []))
        properties = input_schema.get("properties", {})
        fields = {}
        for name, prop in properties.items():
            py_type = self.openapi_type_to_python(prop.get("type", "string"))
            if name in required:
                fields[name] = (py_type, Field(...))
            else:
                default = prop.get("default", None)
                fields[name] = (py_type, Field(default=default))
        return fields
