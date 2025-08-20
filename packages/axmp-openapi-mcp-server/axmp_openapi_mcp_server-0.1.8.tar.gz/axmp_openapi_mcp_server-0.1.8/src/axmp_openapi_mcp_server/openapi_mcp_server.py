"""OpenAPI MCP Server."""

import contextlib
import logging
from enum import Enum
from typing import AsyncIterator, List

import anyio
import uvicorn
from axmp_openapi_helper import (
    APIServerConfig,
    AuthConfig,
    AuthenticationType,
    MultiOpenAPIHelper,
)
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import FileUrl, GetPromptResult, Prompt, Resource, TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

MCP_SERVER_SEPARATOR = "$"
"""Separator for the MCP server's authentication header

  The client should set the authentication header with the following format:
  For the APIKey authentication:
      openapi_server_name$api_key_name=api_key_value
  For the Bearer authentication:
      openapi_server_name$bearer_token=bearer_token
  For the Basic authentication:
      openapi_server_name$username=password
"""

MCP_PROFILE_PREFIX = "mcp_profile_"
BACKEND_SERVER_PREFIX = "backend_server_"


class TransportType(str, Enum):
    """Transport type for MCP and Gateway."""

    SSE = "sse"
    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"


class AuthHeaderKey(str, Enum):
    """Auth header key for the MCP server."""

    BEARER_TOKEN = "bearer_token"
    # USERNAME = "username"
    # PASSWORD = "password"


class OpenAPIMCPServer:
    """OpenAPI MCP Server."""

    def __init__(
        self,
        name: str = "axmp-openapi-mcp-server",
        transport_type: TransportType = TransportType.STREAMABLE_HTTP,
        port: int = 9999,
        multi_openapi_helper: MultiOpenAPIHelper = None,
    ):
        """Initialize the server."""
        self.name = name
        self.port = port
        self.transport_type = transport_type
        self.multi_openapi_helper = multi_openapi_helper
        self.app = Server(self.name)
        self._initialize_app()

    def _initialize_app(self):
        """Initialize the app."""

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Call the tool with the given name and arguments from llm."""
            logger.debug("-" * 100)
            logger.debug(f"::: tool name: {name}")
            logger.debug("::: arguments:")
            for key, value in arguments.items():
                logger.debug(f"\t{key}: {value}")
            logger.debug("-" * 100)

            operation = next(
                (
                    op
                    for op in self.multi_openapi_helper.all_operations
                    if op.name == name
                ),
                None,
            )

            if operation is None:
                # raise ValueError(f"Unknown tool: {name}")
                logger.error(f"MCP Server does not have the tool: {name}")
                return [TextContent(type="text", text=f"Error: Unknown tool: {name}")]

            try:
                result = await self.multi_openapi_helper.run(
                    name=name,
                    args=arguments,
                )

                return [TextContent(type="text", text=f"result: {result}")]
            except Exception as e:
                logger.error(f"Error: {e}")
                return [TextContent(type="text", text=f"Error: {e}")]

        @self.app.list_tools()
        async def list_tools() -> list[Tool]:
            """List all the tools available."""
            tools: List[Tool] = []
            for operation in self.multi_openapi_helper.all_operations:
                tool: Tool = Tool(
                    name=operation.name,
                    description=operation.description,
                    inputSchema=operation.args_schema.model_json_schema(),
                )
                tools.append(tool)

                logger.debug("-" * 100)
                logger.debug(f"::: tool: {tool.name}\n{tool.inputSchema}")

            return tools

        @self.app.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """List all the prompts available."""
            prompts: List[Prompt] = []
            return prompts

        @self.app.get_prompt()
        async def get_prompt(
            name: str, arguments: dict[str, str] | None = None
        ) -> GetPromptResult:
            """Get the prompt with the given name and arguments."""
            return None

        @self.app.list_resources()
        async def list_resources() -> list[Resource]:
            """List all the resources available."""
            resources: List[Resource] = []
            return resources

        @self.app.read_resource()
        async def read_resource(uri: FileUrl) -> str | bytes:
            """Read the resource with the given URI."""
            return None

    def _set_servers_auth_config_from_headers(
        self, headers: list[tuple[bytes, bytes]]
    ) -> None:
        """Set the authentication config for all the servers from the headers."""
        openapi_server_names: list[str] = [
            name.lower()
            for name, _ in self.multi_openapi_helper.openapi_servers.items()
        ]

        for _bytes_key, _bytes_value in headers:
            key = _bytes_key.decode()
            value = _bytes_value.decode()
            logger.info(f"Header {key}: {value}")

            key_parts = key.split(MCP_SERVER_SEPARATOR)
            if len(key_parts) == 2 and key_parts[0].lower() in openapi_server_names:
                server_name = key_parts[0]
                key_name = key_parts[1]

                openapi_server: APIServerConfig = (
                    self.multi_openapi_helper.openapi_servers[server_name]
                )

                # create a new auth config from the existing auth config
                new_auth_config: AuthConfig = openapi_server.auth_config.model_copy()
                logger.info(f"new_auth_config: {new_auth_config.model_dump_json(indent=2)}")

                if new_auth_config.type == AuthenticationType.API_KEY:
                    if key_name.lower() == new_auth_config.api_key_name.lower():
                        new_auth_config.api_key_name = key_name
                        new_auth_config.api_key_value = value
                        logger.info(
                            f"Server {server_name} API Key {key_name} set to {value}"
                        )
                elif new_auth_config.type == AuthenticationType.BEARER:
                    if key_name.lower() == AuthHeaderKey.BEARER_TOKEN.value:
                        new_auth_config.bearer_token = value
                elif new_auth_config.type == AuthenticationType.BASIC:
                    # if key_name.lower() == AuthHeaderKey.USERNAME.value:
                    #     new_auth_config.username = value
                    # elif key_name.lower() == AuthHeaderKey.PASSWORD.value:
                    #     new_auth_config.password = value
                    logger.info(f"key_name: {key_name}, value: {value}")
                    new_auth_config.username = key_name
                    new_auth_config.password = value

                # update the auth config using the new auth config
                self.multi_openapi_helper.update_openapi_server_auth_config(
                    server_name=server_name,
                    auth_config=new_auth_config,
                )

    def run(self):
        """Run the server."""
        # NOTE: SSE has been deprecated in the MCP spec.
        # TODO: remove this after the MCP spec is updated.
        if self.transport_type == TransportType.SSE:
            sse = SseServerTransport("/messages/")

            async def handle_sse(request: Request):
                logger.info(f"::: SSE connection established - request: {request}")
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await self.app.run(
                        streams[0], streams[1], self.app.create_initialization_options()
                    )

            starlette_app = Starlette(
                debug=True,
                routes=[
                    Route("/sse", endpoint=handle_sse),
                    Mount("/messages/", app=sse.handle_post_message),
                ],
            )

            uvicorn.run(starlette_app, host="0.0.0.0", port=self.port)
        elif self.transport_type == TransportType.STREAMABLE_HTTP:
            # Create the session manager with true stateless mode
            session_manager = StreamableHTTPSessionManager(
                app=self.app,
                event_store=None,
                json_response=False,
                stateless=True,
            )

            async def handle_streamable_http(
                scope: Scope, receive: Receive, send: Send
            ) -> None:
                logger.info(f"Client request scope: {scope}")
                logger.info("-" * 100)
                headers: list[tuple[bytes, bytes]] = scope.get("headers")
                logger.info(f"Headers: {headers}")

                # set the authentication headers if the clients are not initialized
                if not self.multi_openapi_helper.clients:
                    self._set_servers_auth_config_from_headers(headers)

                    # check the auth config
                    for (
                        server_name,
                        server,
                    ) in self.multi_openapi_helper.openapi_servers.items():
                        logger.info(
                            f"Server {server_name}: {server.auth_config.model_dump_json()}"
                        )

                    # finally, initialize the clients
                    self.multi_openapi_helper.initialize_clients()

                await session_manager.handle_request(scope, receive, send)

            @contextlib.asynccontextmanager
            async def lifespan(app: Starlette) -> AsyncIterator[None]:
                """Context manager for session manager."""
                async with session_manager.run():
                    logger.info(
                        "Application started with StreamableHTTP session manager!"
                    )
                    try:
                        yield
                    finally:
                        logger.info("Application shutting down...")
                        logger.info("Closing the clients...")
                        # close the clients for releasing the resources
                        await self.multi_openapi_helper.close()

            # Create an ASGI application using the transport
            starlette_app = Starlette(
                debug=True,
                routes=[
                    Mount("/mcp", app=handle_streamable_http),
                ],
                lifespan=lifespan,
            )

            uvicorn.run(starlette_app, host="0.0.0.0", port=self.port)
        else:

            async def arun():
                async with stdio_server() as streams:
                    await self.app.run(
                        streams[0], streams[1], self.app.create_initialization_options()
                    )

            anyio.run(arun)
