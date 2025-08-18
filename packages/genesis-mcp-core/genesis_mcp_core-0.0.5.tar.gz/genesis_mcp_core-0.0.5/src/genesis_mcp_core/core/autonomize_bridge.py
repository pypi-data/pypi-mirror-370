"""
Autonomize Connector SDK Bridge for Genesis MCP Core.

This module bridges the Autonomize Connector SDK with the Genesis MCP server,
converting SDK operations into MCP tools and handling execution routing.
"""

import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import asyncio

from ..utils.logging import get_logger
from .config import Settings


logger = get_logger("autonomize_bridge")


def sanitize_tool_description(description: str) -> str:
    """
    Sanitize tool descriptions to prevent tool poisoning attacks.
    
    Tool poisoning is a critical security vulnerability where malicious actors
    embed hidden instructions in tool descriptions that can hijack LLM behavior.
    
    This function:
    - Removes hidden Unicode characters and control sequences
    - Strips ANSI escape sequences that can hide malicious instructions
    - Removes excessive whitespace and suspicious patterns
    - Prevents prompt injection attempts
    
    Args:
        description: Raw tool description
        
    Returns:
        Sanitized description safe for LLM consumption
    """
    if not description or not isinstance(description, str):
        return "No description available"
    
    # Remove control characters and normalize Unicode
    description = unicodedata.normalize('NFKC', description)
    description = ''.join(char for char in description if not unicodedata.category(char).startswith('C'))
    
    # Remove ANSI escape sequences (used to hide malicious instructions)
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKHFJ]')
    description = ansi_escape.sub('', description)
    
    # Remove suspicious Unicode categories that could hide instructions
    suspicious_patterns = [
        r'[\u200B-\u200F\u202A-\u202E\u2060-\u206F]',  # Zero-width and directional chars
        r'[\uFEFF]',  # Byte order mark
        r'[\u00AD]',  # Soft hyphen
    ]
    
    for pattern in suspicious_patterns:
        description = re.sub(pattern, '', description)
    
    # Remove excessive whitespace
    description = re.sub(r'\s+', ' ', description).strip()
    
    # Prevent common prompt injection patterns
    injection_patterns = [
        r'(?i)(ignore\s+previous\s+instructions?)',
        r'(?i)(system\s*:?\s*you\s+are\s+now)',
        r'(?i)(new\s+instructions?)',
        r'(?i)(forget\s+everything)',
        r'(?i)(\[INST\]|\[\/INST\])',  # Instruction markers
        r'(?i)(assistant\s*:?\s*i\s+will)',
    ]
    
    for pattern in injection_patterns:
        description = re.sub(pattern, '[SANITIZED]', description)
    
    # Limit length to prevent excessively long descriptions
    if len(description) > 500:
        description = description[:497] + "..."
    
    # Final safety check - ensure we have a reasonable description
    if not description.strip() or description.strip() == '[SANITIZED]':
        return "Tool description sanitized for security"
    
    return description.strip()


class AutonomizeBridge:
    """Bridge between Autonomize Connector SDK and MCP tools."""
    
    def __init__(self, config: Settings):
        """Initialize the autonomize bridge."""
        self.config = config
        self.registered_connectors: Set[str] = set()
        self.enabled_connectors: Set[str] = set()
        self.available_tools: List[Dict[str, Any]] = []
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize autonomize connectors using 2-phase approach."""
        if not self.config.autonomize.enabled:
            logger.info("No autonomize connectors enabled")
            return
            
        logger.info("Initializing Autonomize Connector SDK bridge")
        
        try:
            # Import the SDK
            import autonomize_connector as ac
            
            # PHASE 1: Register ALL available connectors from config directory
            await self._register_all_connectors()
            
            # PHASE 2: Generate tools only for enabled connectors
            await self._generate_enabled_tools()
            
            self._initialized = True
            logger.info(f"Autonomize bridge initialized: {len(self.registered_connectors)} registered, {len(self.enabled_connectors)} enabled")
            
        except ImportError as e:
            logger.error(f"Failed to import autonomize_connector: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize autonomize bridge: {e}")
            raise
    
    async def _register_all_connectors(self) -> None:
        """Phase 1: Register ALL available connectors from config directory."""
        import autonomize_connector as ac
        
        # Get the connector config directory
        config_dir = self.config.autonomize.connector_config_dir
        if not config_dir:
            logger.warning("No connector config directory specified")
            return
        
        config_path = Path(config_dir)
        if not config_path.exists() or not config_path.is_dir():
            logger.warning(f"Connector config directory not found: {config_path}")
            return
        
        # Find all JSON configuration files
        json_files = list(config_path.glob("*.json"))
        if not json_files:
            logger.warning(f"No JSON configuration files found in: {config_path}")
            return
        
        logger.info(f"Phase 1: Registering connectors from {len(json_files)} config files...")
        
        for config_file in json_files:
            connector_name = config_file.stem  # filename without .json
            
            try:
                logger.info(f"Registering {connector_name} from {config_file}")
                ac.register_from_file(str(config_file))
                self.registered_connectors.add(connector_name)
                logger.debug(f"Successfully registered {connector_name}")
            except Exception as e:
                logger.error(f"Failed to register {connector_name}: {e}")
        
        logger.info(f"Phase 1 complete: {len(self.registered_connectors)} connectors registered")
    
    async def _generate_enabled_tools(self) -> None:
        """Phase 2: Generate tools only for enabled connectors."""
        import autonomize_connector as ac
        
        logger.info("Phase 2: Generating tools for enabled connectors...")
        
        # Get enabled connectors from config
        enabled_connectors_dict = self.config.autonomize.get_enabled_connectors()
        self.enabled_connectors = {name for name, enabled in enabled_connectors_dict.items() if enabled}
        
        if not self.enabled_connectors:
            logger.warning("No connectors enabled - no tools will be generated")
            return
        
        logger.info(f"Enabled connectors: {self.enabled_connectors}")
        
        # Generate MCP tools for enabled connectors only
        self.available_tools = []
        
        # Get all registered connectors from SDK
        sdk_connectors = ac.list_registered_connectors()
        logger.debug(f"SDK registered connectors: {sdk_connectors}")
        
        for connector_name in self.enabled_connectors:
            if connector_name not in sdk_connectors:
                logger.warning(f"Enabled connector {connector_name} not found in SDK registry")
                continue
                
            try:
                # Get connector info from SDK
                connector_info = ac.get_connector_info(connector_name)
                endpoints = connector_info.get('endpoints', [])
                
                logger.info(f"Generating tools for {connector_name} ({len(endpoints)} endpoints)")
                
                # Generate tools for each endpoint
                for endpoint_name in endpoints:
                    tool_name = f"{connector_name}_{endpoint_name}"
                    
                    # Get validation info if available
                    validation_info = connector_info.get('validation', {}).get(endpoint_name, {})
                    required_fields = validation_info.get('required_fields', [])
                    optional_fields = validation_info.get('optional_fields', [])
                    
                    # Create enhanced descriptions based on connector type
                    description = self._get_tool_description(connector_name, endpoint_name, connector_info)
                    
                    # Create MCP tool schema
                    tool_schema = {
                        "name": tool_name,
                        "description": description,
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": required_fields
                        }
                    }
                    
                    # Add structured output schema if available (MCP 2025-06-18 feature)
                    output_schema = self._get_tool_output_schema(connector_name, endpoint_name)
                    if output_schema:
                        tool_schema["outputSchema"] = output_schema
                    
                    # Add properties for required and optional fields
                    all_fields = required_fields + optional_fields
                    for field in all_fields:
                        tool_schema["inputSchema"]["properties"][field] = {
                            "type": "string",  # Simplified - could be enhanced based on API docs
                            "description": f"{field.replace('_', ' ').title()} parameter"
                        }
                    
                    self.available_tools.append(tool_schema)
                    logger.debug(f"Generated tool: {tool_name}")
                    
            except Exception as e:
                logger.error(f"Failed to generate tools for {connector_name}: {e}")
        
        logger.info(f"Phase 2 complete: {len(self.available_tools)} tools generated from {len(self.enabled_connectors)} connectors")
    
    def _get_tool_description(self, connector_name: str, endpoint_name: str, connector_info: Dict[str, Any]) -> str:
        """Generate a description for a tool based on connector and endpoint info."""
        # Get base description from connector info or create a default
        base_description = connector_info.get('description', f"{connector_name} connector")
        endpoint_description = f"Execute {endpoint_name} operation"
        
        # Combine and sanitize
        full_description = f"{base_description} - {endpoint_description}"
        return sanitize_tool_description(full_description)
    
    def _get_tool_output_schema(self, connector_name: str, endpoint_name: str) -> Optional[Dict[str, Any]]:
        """Get structured output schema for a tool (MCP 2025-06-18 feature)."""
        # This could be enhanced to provide specific schemas based on connector type
        # For now, return a generic schema
        return {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "description": f"Result from {connector_name} {endpoint_name} operation"
                },
                "status": {
                    "type": "string",
                    "description": "Operation status"
                }
            }
        }
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get all available MCP tools."""
        return self.available_tools.copy()
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by routing to the appropriate connector."""
        if not self._initialized:
            raise RuntimeError("Bridge not initialized")
        
        # Parse connector name and endpoint from tool name
        parts = tool_name.split('_', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid tool name format: {tool_name}")
        
        connector_name, endpoint_name = parts
        
        if connector_name not in self.enabled_connectors:
            raise RuntimeError(f"Connector {connector_name} not enabled")
        
        try:
            import autonomize_connector as ac
            
            # Create connector instance
            logger.info(f"Creating connector instance for {connector_name}")
            connector_func = getattr(ac, connector_name)
            connector = connector_func()
            
            # Get connector info to find endpoint details
            connector_info = ac.get_connector_info(connector_name)
            endpoint_config = connector_info.get('endpoints', {}).get(endpoint_name)
            
            if not endpoint_config:
                raise RuntimeError(f"Endpoint {endpoint_name} not found in connector {connector_name}")
            
            # Execute the connector operation
            logger.info(f"Executing {connector_name}.{endpoint_name} with args: {arguments}")
            
            # Use the connector's execute_request method
            method = endpoint_config.get('method', 'GET')
            path = endpoint_config.get('path', f'/{endpoint_name}')
            
            # Replace path parameters
            formatted_path = path
            for key, value in arguments.items():
                formatted_path = formatted_path.replace(f'{{{key}}}', str(value))
            
            # Separate path params from query params
            query_params = {}
            for key, value in arguments.items():
                if f'{{{key}}}' not in path:
                    query_params[key] = value
            
            result = await connector.execute_request(
                method=method,
                endpoint=formatted_path,
                params=query_params if method == 'GET' else None,
                data=query_params if method != 'GET' else None
            )
            
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name}: {e}")
            raise
    
    def get_registered_connectors(self) -> Set[str]:
        """Get set of registered connector names."""
        return self.registered_connectors.copy()
    
    def get_enabled_connectors(self) -> Set[str]:
        """Get set of enabled connector names."""
        return self.enabled_connectors.copy()
    
    def is_initialized(self) -> bool:
        """Check if the bridge is initialized."""
        return self._initialized
    
    async def cleanup(self) -> None:
        """Clean up the bridge resources."""
        logger.info("Cleaning up Autonomize bridge")
        self.available_tools.clear()
        self.registered_connectors.clear()
        self.enabled_connectors.clear()
        self._initialized = False