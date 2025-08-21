import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import shutil
from ....config.logger import logging
from ....utils.stdio_session_params import get_stdio_session_params


def get_session_data(server: dict) -> dict:
    try:
        loop = asyncio.get_running_loop()
        return loop.create_task(async_get_session(server=server))
    except RuntimeError:
        return asyncio.run(async_get_session(server=server))


async def async_get_session(server: dict) -> dict:
    """Initialize the server connection."""
    name: str = server["name"]
    server_params: StdioServerParameters = get_stdio_session_params(server=server)

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                resources = await session.list_resource_templates()
                prompts = await session.list_prompts()
                data: dict = {
                    "tools": tools.tools,
                    "resources": resources.resourceTemplates,
                    "prompts": prompts.prompts,
                }
                return data

    except Exception as e:
        logging.error(f"Error initializing server {name}: {e}")
        raise Exception(f"Error initializing server {name}: {e}")
