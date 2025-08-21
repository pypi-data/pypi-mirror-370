from mcp.client.streamable_http import streamablehttp_client
from mcp.client.auth import OAuthClientProvider
from mcp import ClientSession
import asyncio

from mcp_oauth import OAuthClient


def get_session_data(
    http: str,
    oauth_client: OAuthClient,
    headers: dict[str, str] = None,
) -> dict:
    try:
        loop = asyncio.get_event_loop()
        future = asyncio.run_coroutine_threadsafe(
            async_get_session(
                http=http,
                oauth_client=oauth_client,
                headers=headers,
            ),
            loop,
        )
        result = future.result()  # Espera el resultado
        return result
    except RuntimeError:
        return asyncio.run(
            async_get_session(
                http=http,
                oauth_client=oauth_client,
                headers=headers,
            )
        )


async def async_get_session(
    http: str,
    oauth_client: OAuthClient,
    headers: dict[str, str] = None,
):
    # Connect to a streamable HTTP server
    oauth: OAuthClientProvider = (
        oauth_client.oauth if oauth_client is not None else None
    )
    async with streamablehttp_client(url=http, auth=oauth, headers=headers) as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # Generate data
            tools = await session.list_tools()
            resources = await session.list_resource_templates()
            prompts = await session.list_prompts()
            data: dict = {
                "tools": tools.tools,
                "resources": resources.resourceTemplates,
                "prompts": prompts.prompts,
            }
        return data
