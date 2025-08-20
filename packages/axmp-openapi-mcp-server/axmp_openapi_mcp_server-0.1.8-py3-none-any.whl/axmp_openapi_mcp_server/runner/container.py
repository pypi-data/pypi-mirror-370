"""This is a container main."""

import json
import logging
from pathlib import Path

from axmp_openapi_helper import (
    MultiOpenAPIHelper,
    MultiOpenAPISpecConfig,
)

from axmp_openapi_mcp_server.openapi_mcp_server import (
    MCP_PROFILE_PREFIX,
    OpenAPIMCPServer,
)
from axmp_openapi_mcp_server.setting import axmp_mcp_settings

logger = logging.getLogger(__name__)


def run():
    """Run the MCP server."""
    mcp_profile_file = (
        Path(axmp_mcp_settings.profile_base_path)
        / f"{MCP_PROFILE_PREFIX}{axmp_mcp_settings.profile_id}.json"
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
            f"{axmp_mcp_settings.profile_base_path}/{backend_server.spec_file_path}"
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

    mcp_server = OpenAPIMCPServer(
        transport_type=axmp_mcp_settings.transport_type,
        name=axmp_mcp_settings.server_name,
        port=axmp_mcp_settings.port,
        multi_openapi_helper=multi_openapi_helper,
    )

    mcp_server.run()
