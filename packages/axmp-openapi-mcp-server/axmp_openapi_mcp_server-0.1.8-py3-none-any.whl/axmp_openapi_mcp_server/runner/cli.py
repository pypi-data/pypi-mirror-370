"""This is a mcp server."""

import json
import logging
from pathlib import Path

import click
from axmp_openapi_helper import (
    APIServerConfig,
    AuthConfig,
    AuthenticationType,
    MultiOpenAPIHelper,
    MultiOpenAPISpecConfig,
)

from axmp_openapi_mcp_server.openapi_mcp_server import (
    MCP_PROFILE_PREFIX,
    AuthHeaderKey,
    OpenAPIMCPServer,
    TransportType,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="streamable-http",
    help="Transport type",
)
@click.option("--port", default=20000, help="Port to listen on for SSE")
@click.option("--server-name", type=str, required=False, help="Server name")
@click.option(
    "--profile-base-path",
    type=click.Path(exists=True),
    required=True,
    help="Path to the profile base path",
)
@click.option("--profile-id", type=str, required=True, help="Profile id")
@click.option(
    "--backend-server-auth-configs",
    type=str,
    required=False,
    help="backend auth configs e.g.backend-server1$key=value,backend-server2$key=value",
)
def main(
    transport: str,
    port: int,
    server_name: str | None,
    profile_base_path: str,
    profile_id: str,
    backend_server_auth_configs: str | None,
):
    """Run the MCP server."""
    if transport == TransportType.STDIO:
        if backend_server_auth_configs is None:
            raise ValueError(
                "backend-server-auth-configs is required for stdio transport"
            )

    mcp_profile_file = (
        Path(profile_base_path) / f"{MCP_PROFILE_PREFIX}{profile_id}.json"
    )
    if not mcp_profile_file.exists():
        raise ValueError(f"MCP profile file not found: {mcp_profile_file}")

    multi_openapi_spec_config: MultiOpenAPISpecConfig = (
        MultiOpenAPISpecConfig.from_multi_server_spec_file(file_path=mcp_profile_file)
    )

    logger.info(
        f"Multi OpenAPI spec config: \n{json.dumps(multi_openapi_spec_config.model_dump(), indent=2)}"
    )

    # update the spec file path for the backend servers
    for backend_server in multi_openapi_spec_config.backends:
        backend_server.spec_file_path = (
            f"{profile_base_path}/{backend_server.spec_file_path}"
        )

        if not Path(backend_server.spec_file_path).exists():
            raise ValueError(
                f"Backend OpenAPI Spec file not found: {backend_server.spec_file_path}"
            )

    multi_openapi_helper = MultiOpenAPIHelper(
        multi_openapi_spec_config=multi_openapi_spec_config
    )

    logger.info(
        f"Multi OpenAPI spec config: \n{json.dumps(multi_openapi_spec_config.model_dump(), indent=2)}"
    )

    operations = multi_openapi_helper.all_operations
    for i, operation in enumerate(operations):
        logger.info(
            f"Operation {i} -> {operation.server_name}::{operation.method}::{operation.path}::{operation.name}"
        )

    if transport == TransportType.STDIO and backend_server_auth_configs is not None:
        for backend_server_auth_config in backend_server_auth_configs.split(","):
            backend_server_name_and_key, value = backend_server_auth_config.split("=")
            logger.info(
                f"Backend server auth config: {backend_server_name_and_key} = {value}"
            )
            backend_server_name, key_name = backend_server_name_and_key.split(":")
            logger.info(
                f"Backend server name: {backend_server_name}, key: {key_name}, value: {value}"
            )

            openapi_server: APIServerConfig | None = (
                multi_openapi_helper.openapi_servers.get(backend_server_name)
            )

            if openapi_server is None:
                logger.error(
                    f"Backend server not found: {backend_server_name} in {multi_openapi_helper.openapi_servers.keys()}"
                )
                # raise ValueError(
                #     f"Backend server not found: {backend_server_name} in {multi_openapi_helper.openapi_servers.keys()}"
                # )

            else:
                # create a new auth config from the existing auth config
                new_auth_config: AuthConfig = openapi_server.auth_config.model_copy()

                if new_auth_config.type == AuthenticationType.API_KEY:
                    if key_name.lower() == new_auth_config.api_key_name.lower():
                        new_auth_config.api_key_name = key_name
                        new_auth_config.api_key_value = value
                        logger.info(
                            f"Server {backend_server_name} API Key {key_name} set to {value}"
                        )
                elif new_auth_config.type == AuthenticationType.BEARER:
                    if key_name.lower() == AuthHeaderKey.BEARER_TOKEN.value:
                        new_auth_config.bearer_token = value
                elif new_auth_config.type == AuthenticationType.BASIC:
                    if key_name.lower() == AuthHeaderKey.USERNAME.value:
                        new_auth_config.username = value
                    elif key_name.lower() == AuthHeaderKey.PASSWORD.value:
                        new_auth_config.password = value

                # update the auth config using the new auth config
                multi_openapi_helper.update_openapi_server_auth_config(
                    server_name=backend_server_name,
                    auth_config=new_auth_config,
                )

        # check the auth config
        for (
            backend_server_name,
            server,
        ) in multi_openapi_helper.openapi_servers.items():
            logger.info(
                f"Server {backend_server_name}: {server.auth_config.model_dump_json()}"
            )

        # finally, initialize the clients
        try:
            multi_openapi_helper.initialize_clients()
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            return 1

    if server_name is None:
        server_name = f"axmp-openapi-mcp-server-{profile_id}"

    logger.info(f"Server name: {server_name}")

    mcp_server = OpenAPIMCPServer(
        transport_type=transport,
        name=server_name,
        port=port,
        multi_openapi_helper=multi_openapi_helper,
    )

    mcp_server.run()

    return 0
