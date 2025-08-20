"""Base settings for Axmp MCP and Axmp Studio."""

from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict

from axmp_openapi_mcp_server.openapi_mcp_server import TransportType


class AxmpMcpSettings(BaseSettings):
    """Settings for Axmp MCP."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="AXMP_MCP_", env_file=".env", extra="ignore"
    )

    server_name: str
    port: int
    transport_type: TransportType = TransportType.STREAMABLE_HTTP
    profile_base_path: str
    profile_id: str


axmp_mcp_settings = AxmpMcpSettings()
