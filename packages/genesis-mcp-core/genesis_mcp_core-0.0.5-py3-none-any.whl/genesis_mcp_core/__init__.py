"""
Genesis MCP Core - A comprehensive SDK for building MCP (Model Context Protocol) servers.

This package provides the core infrastructure for creating MCP servers with support for:
- Autonomize Connector SDK integration
- Healthcare API connectors (Molina, QNXT, etc.)
- MCP 2025-06-18 protocol compliance
- Legacy endpoint support (SSE, messages)
- Built-in project templating system
"""

from genesis_mcp_core.core.server import GenesisMCPServer
from genesis_mcp_core.core.config import Settings, ServerConfig, AutonomizeConfig
from genesis_mcp_core.core.registry import ConnectorRegistry
from genesis_mcp_core.utils.logging import get_logger, setup_logging

__version__ = "0.1.0"
__author__ = "Genesis Team"

# Main exports
__all__ = [
    "GenesisMCPServer",
    "Settings", 
    "ServerConfig",
    "AutonomizeConfig",
    "ConnectorRegistry",
    "get_logger",
    "setup_logging",
]

def get_settings() -> Settings:
    """Get application settings with environment variable loading."""
    return Settings()
