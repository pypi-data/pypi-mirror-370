"""Agent Zero package for ClickHouse database management."""

__version__ = 'v0.0.1a15'

from agent_zero.mcp_server import (
    create_clickhouse_client,
    list_databases,
    list_tables,
    run_select_query,
)
from agent_zero.server_config import ServerConfig

__all__ = [
    "create_clickhouse_client",
    "list_databases",
    "list_tables",
    "run_select_query",
    "ServerConfig",
]
