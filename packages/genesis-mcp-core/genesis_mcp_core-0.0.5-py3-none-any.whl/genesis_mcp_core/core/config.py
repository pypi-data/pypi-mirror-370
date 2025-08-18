"""Configuration module for Genesis MCP Core SDK."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure .env file is loaded
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not available


class ServerConfig(BaseModel):
    """Server configuration."""
    name: str = Field(default="Genesis MCP Server", description="Server name")
    version: str = Field(default="1.0.0", description="Server version")
    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=8002, description="Server port")  
    debug: bool = Field(default=False, description="Debug mode")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="structured", description="Log format")
    enable_access_logs: bool = Field(default=True, description="Enable access logs")


class AutonomizeConfig(BaseSettings):
    """Configuration for Autonomize Connector SDK integration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Generic connector configuration directory
    connector_config_dir: Optional[Union[str, Path]] = Field(
        default=None, 
        description="Directory containing connector configuration JSON files"
    )
    
    # Dynamic connector enablement - will be populated from config directory
    enabled_connectors_dict: Dict[str, bool] = Field(default_factory=dict, exclude=True)
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to discover connectors from config directory."""
        super().model_post_init(__context)
        if self.connector_config_dir:
            self._discover_connectors()
    
    def _discover_connectors(self) -> None:
        """Discover connector configurations from the config directory."""
        if not self.connector_config_dir:
            return
            
        config_path = Path(self.connector_config_dir)
        if not config_path.exists() or not config_path.is_dir():
            return
        
        # Find all JSON files in the config directory
        json_files = list(config_path.glob("*.json"))
        
        # Enable all discovered connectors by default
        for json_file in json_files:
            connector_name = json_file.stem  # filename without .json
            
            # Check if there's an environment variable to enable/disable this connector
            env_var = f"ENABLE_{connector_name.upper()}"
            is_enabled = os.getenv(env_var, "true").lower() in ("true", "1", "yes", "on")
            
            self.enabled_connectors_dict[connector_name] = is_enabled
    
    def is_connector_enabled(self, connector_name: str) -> bool:
        """Check if a specific connector is enabled."""
        return self.enabled_connectors_dict.get(connector_name, False)
    
    def get_enabled_connectors(self) -> Dict[str, bool]:
        """Get dictionary of all connector enablement flags."""
        return self.enabled_connectors_dict.copy()
    
    def get_available_connectors(self) -> List[str]:
        """Get list of all available connector names."""
        return list(self.enabled_connectors_dict.keys())
    
    @property 
    def enabled(self) -> bool:
        """Check if any autonomize connector is enabled."""
        return any(self.enabled_connectors_dict.values())


class Settings(BaseSettings):
    """Main application settings for Genesis MCP Core."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        case_sensitive=False,
        extra="ignore"
    )
    
    # Core configurations
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    autonomize: AutonomizeConfig = Field(default_factory=AutonomizeConfig)
    
    def __init__(self, connector_config_dir: Optional[Union[str, Path]] = None, **kwargs: Any) -> None:
        """Initialize settings with optional connector config directory."""
        if connector_config_dir:
            # Set the connector config directory in autonomize config
            if "autonomize" not in kwargs:
                kwargs["autonomize"] = {}
            kwargs["autonomize"]["connector_config_dir"] = connector_config_dir
        
        super().__init__(**kwargs)
    
    def is_connector_enabled(self, connector_name: str) -> bool:
        """Check if a connector is enabled."""
        return self.autonomize.is_connector_enabled(connector_name)
    
    def get_enabled_connectors(self) -> Dict[str, bool]:
        """Get all enabled connectors."""
        return self.autonomize.get_enabled_connectors()
    
    def get_available_connectors(self) -> List[str]:
        """Get list of all available connector names."""
        return self.autonomize.get_available_connectors()
    
    def get_connector_count(self) -> int:
        """Get count of enabled connectors."""
        return sum(1 for enabled in self.get_enabled_connectors().values() if enabled)
    
    @property
    def enabled_connectors(self) -> List[str]:
        """Get list of enabled connector names."""
        enabled_dict = self.get_enabled_connectors()
        return [name for name, enabled in enabled_dict.items() if enabled]


def get_settings(connector_config_dir: Optional[Union[str, Path]] = None) -> Settings:
    """Get application settings with optional connector config directory."""
    return Settings(connector_config_dir=connector_config_dir)