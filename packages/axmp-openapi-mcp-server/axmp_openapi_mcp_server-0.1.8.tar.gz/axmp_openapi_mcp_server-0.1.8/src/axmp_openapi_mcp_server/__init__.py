"""This is the MCP server for the ZMP OpenAPI."""

import logging
import logging.config

# for stdio
logging.basicConfig(
    level=logging.INFO,
    # format="[%(asctime)s] [%(levelname)s] [%(name)s] [%(threadName)s:%(thread)d] [%(funcName)s:%(lineno)d] - %(message)s",
    format="[%(asctime)s.%(msecs)d] [%(levelname)s] [%(name)s] [%(threadName)s:%(thread)d] [%(module)s:%(funcName)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

# for streamable-http
# logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

logging.getLogger("httpcore.http11").setLevel(logging.INFO)
logging.getLogger("sse_starlette.sse").setLevel(logging.INFO)
logging.getLogger("axmp_openapi_helper.openapi").setLevel(logging.INFO)
logging.getLogger("axmp_openapi_mcp_server.openapi_mcp_server").setLevel(logging.DEBUG)
