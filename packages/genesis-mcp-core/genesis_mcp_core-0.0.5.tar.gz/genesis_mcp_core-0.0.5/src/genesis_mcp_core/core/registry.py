"""Connector registry for managing and routing MCP tool calls."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from ..core.config import Settings
from .autonomize_bridge import AutonomizeBridge
from ..utils.logging import get_logger


class ConnectorRegistry:
    """Registry for managing connectors and routing tool calls."""
    
    def __init__(
        self, 
        settings: Optional[Settings] = None,
        connector_config_dir: Optional[Union[str, Path]] = None
    ) -> None:
        """Initialize the connector registry."""
        self.settings = settings or Settings(connector_config_dir=connector_config_dir)
        self._autonomize_bridge: Optional[AutonomizeBridge] = None
        self.logger = get_logger("registry")
        
        # Initialize autonomize bridge (handles all JSON-based connectors)
        self._autonomize_bridge = AutonomizeBridge(self.settings)
    
    async def initialize(self) -> None:
        """Initialize all connectors (only JSON-based connectors from autonomize SDK)."""
        self.logger.info("Initializing connector registry")
        
        # Initialize autonomize bridge (handles all JSON-based connectors)
        if self._autonomize_bridge:
            try:
                await self._autonomize_bridge.initialize()
                if self._autonomize_bridge.is_initialized():
                    registered = self._autonomize_bridge.get_registered_connectors()
                    enabled = self._autonomize_bridge.get_enabled_connectors()
                    self.logger.info(f"Connectors: {len(registered)} registered, {len(enabled)} enabled")
                else:
                    self.logger.warning("Bridge initialization returned but not marked as initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize connectors: {e}")
                # Don't fail entire registry initialization
                self._autonomize_bridge = None
        
        total_enabled = len(self._autonomize_bridge.get_enabled_connectors()) if self._autonomize_bridge else 0
        self.logger.info(f"Registry initialized: {total_enabled} connectors enabled")
    
    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from JSON-based connectors."""
        tools = []
        
        # Get tools from autonomize bridge (JSON-based connectors)
        if self._autonomize_bridge and self._autonomize_bridge.is_initialized():
            try:
                tools = await self._autonomize_bridge.get_tools()
                
                # Log connector status
                registered = self._autonomize_bridge.get_registered_connectors()
                enabled = self._autonomize_bridge.get_enabled_connectors()
                self.logger.debug(f"Tools: {len(tools)} from {len(enabled)} enabled connectors")
                
            except Exception as e:
                self.logger.error(f"Failed to get tools from connectors: {e}")
        
        self.logger.info(f"Total tools: {len(tools)}")
        return tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool call, routing to connector."""
        self.logger.info(f"Executing tool: {tool_name}")
        
        # Route to autonomize bridge (handles all JSON-based connectors)
        if self._autonomize_bridge and self._autonomize_bridge.is_initialized():
            try:
                return await self._autonomize_bridge.execute_tool(tool_name, arguments)
            except Exception as e:
                self.logger.error(f"Tool execution failed for {tool_name}: {e}")
                raise
        
        # If no connector can handle this tool, raise error
        raise RuntimeError(f"No connector available to handle tool: {tool_name}")
    
    def get_connector_names(self) -> List[str]:
        """Get list of all enabled connector names."""
        names = []
        
        # Add connector names from JSON configs
        if self._autonomize_bridge and self._autonomize_bridge.is_initialized():
            connectors = self._autonomize_bridge.get_enabled_connectors()
            names.extend(list(connectors))
        
        return names
    
    def get_enabled_connectors(self) -> Set[str]:
        """Get set of enabled connector names."""
        if self._autonomize_bridge and self._autonomize_bridge.is_initialized():
            return self._autonomize_bridge.get_enabled_connectors()
        return set()
    
    def get_all_connectors(self) -> Dict[str, Any]:
        """Get all connectors information."""
        connector_info = {}
        
        # Add connectors from JSON configs
        if self._autonomize_bridge and self._autonomize_bridge.is_initialized():
            enabled = self._autonomize_bridge.get_enabled_connectors()
            registered = self._autonomize_bridge.get_registered_connectors()
            
            for name in enabled:
                connector_info[name] = {
                    "name": name,
                    "enabled": True,
                    "registered": name in registered,
                    "type": "json_connector"
                }
        
        return connector_info
    
    def get_autonomize_bridge(self) -> Optional[AutonomizeBridge]:
        """Get the bridge for JSON-based connectors."""
        return self._autonomize_bridge
    
    async def cleanup(self) -> None:
        """Clean up all connectors."""
        self.logger.info("Cleaning up connector registry")
        
        # Cleanup autonomize bridge
        if self._autonomize_bridge:
            try:
                await self._autonomize_bridge.cleanup()
            except Exception as e:
                self.logger.error(f"Failed to cleanup connectors: {e}")
        
        self._autonomize_bridge = None
        self.logger.info("Registry cleanup complete")
    
    def is_initialized(self) -> bool:
        """Check if the registry is initialized."""
        has_autonomize = self._autonomize_bridge is not None and self._autonomize_bridge.is_initialized()
        return has_autonomize
    
    def __str__(self) -> str:
        """String representation of the registry."""
        autonomize_count = len(self._autonomize_bridge.get_enabled_connectors()) if self._autonomize_bridge else 0
        return f"ConnectorRegistry(autonomize={autonomize_count})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the registry."""
        return self.__str__()