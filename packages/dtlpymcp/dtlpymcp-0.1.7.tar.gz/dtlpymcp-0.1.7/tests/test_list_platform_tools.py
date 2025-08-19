import asyncio
import random
import json
import os
from datetime import timedelta
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import dtlpy as dl

dl.setenv('rc')
if dl.token_expired():
    dl.login()
# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="dtlpymcp",  # Executable
    args=["start"],  # Command line arguments
    env={"DATALOOP_API_KEY": dl.token()},  # Optional environment variables
    cwd=os.getcwd()
)

async def test_list_platform_tools():
    print("[TEST CLIENT] Connecting to MCP server and calling test tool...")
    async with stdio_client(server=server_params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
            await session.initialize()
            tools = await session.list_tools()
            for tool in tools.tools:
                tool_str = '   \n'.join([f"{k}: {v}" for k, v in tool.model_dump().items()])
                print(f"Tool: {tool.name}")
                print(tool_str)
                print("-" * 50)

if __name__ == "__main__":

    asyncio.run(test_list_platform_tools()) 
    # asyncio.run(test_ask_dataloop()) 