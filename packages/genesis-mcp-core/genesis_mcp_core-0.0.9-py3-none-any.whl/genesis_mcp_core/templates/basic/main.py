#!/usr/bin/env python3
"""
{{ project_name | title }} - MCP Server built with Genesis MCP Core

This server provides MCP 2025-06-18 compliant endpoints with healthcare connector support.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from genesis_mcp_core import GenesisMCPServer, Settings, get_logger

logger = get_logger("{{ project_name_normalized }}")


async def main():
    """Main server entry point."""
    # Load environment variables from .env file in the service directory
    service_dir = Path(__file__).parent
    env_file = service_dir / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from {env_file}")
    else:
        logger.warning(f"No .env file found at {env_file}")
    
    # Point to connector configurations
    connector_config_dir = service_dir / "connectors"
    
    # Create settings
    settings = Settings(connector_config_dir=connector_config_dir)
    
    # Log startup info
    logger.info(f"Starting {{ project_name | title }}")
    logger.info(f"Connector config directory: {connector_config_dir}")
    
    # Create and run server
    server = GenesisMCPServer(settings=settings)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
