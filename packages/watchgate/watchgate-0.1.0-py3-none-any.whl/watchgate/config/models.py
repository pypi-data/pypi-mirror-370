"""Configuration models for Watchgate MCP Gateway."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Literal
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl, model_validator, field_validator

from watchgate.utils.paths import resolve_config_path


# Pydantic schemas for YAML validation (ADR-005)
class LoggingConfigSchema(BaseModel):
    """Schema for validating logging configuration."""
    level: str = "INFO"
    handlers: List[str] = Field(default_factory=lambda: ["stderr"])
    file_path: Optional[str] = None
    max_file_size_mb: float = 10  # Size limit before rotating to a new log file
    backup_count: int = 5  # Number of rotated log files to keep (log.1, log.2, etc.)
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"  # Standard format, timezone handled by logging configuration


class PluginConfigSchema(BaseModel):
    """Schema for validating plugin configuration."""
    policy: str  # Policy name for plugin (required)
    enabled: bool = True
    priority: int = Field(default=50, ge=0, le=100)  # Plugin execution priority (0-100, lower = higher priority)
    config: Dict[str, Any] = Field(default_factory=dict)


class PluginsConfigSchema(BaseModel):
    """Schema for validating upstream-scoped plugin configurations.
    
    Uses a dictionary-based structure where:
    - `_global` key contains policies for all upstreams (optional)
    - Individual upstream names are keys with their specific policies
    - Upstream-specific policies override global ones with same name
    """
    security: Optional[Dict[str, List[PluginConfigSchema]]] = Field(default_factory=dict)
    auditing: Optional[Dict[str, List[PluginConfigSchema]]] = Field(default_factory=dict)
    
    @field_validator('security', 'auditing')
    @classmethod
    def validate_upstream_keys(cls, v, info):
        """Validate upstream keys - only accepts dictionary format."""
        if not v:  # Empty value is valid
            return {}
            
        # Only accept dictionary format
        if not isinstance(v, dict):
            raise ValueError("Plugin configuration must be a dictionary with upstream keys (e.g., {'_global': [...]})")
            
        validated_dict = {}
        
        for key, policies in v.items():
            # Skip special keys
            if key.startswith('_'):
                if key == '_global':
                    validated_dict[key] = policies  # Valid special key
                    continue  
                else:
                    # Ignored keys (e.g., for YAML anchors) - don't include in result
                    continue  
            
            # Validate upstream key naming pattern
            if not re.match(r'^[a-z][a-z0-9_-]*$', key):
                raise ValueError(
                    f"Invalid upstream key '{key}': must be lowercase alphanumeric "
                    f"with hyphens/underscores (pattern: ^[a-z][a-z0-9_-]*$)"
                )
            
            # Validate that key doesn't contain double underscores (reserved for namespace delimiter)
            if "__" in key:
                raise ValueError(
                    f"Invalid upstream key '{key}': cannot contain '__' (reserved for namespace delimiter)"
                )
            
            validated_dict[key] = policies
            
            # Note: Upstream existence validation happens at ProxyConfigSchema level
            # where we have access to the full upstreams configuration
        
        return validated_dict


# Dataclasses for internal representation (ADR-005)
@dataclass
class LoggingConfig:
    """Internal representation of logging configuration."""
    level: str = "INFO"
    handlers: List[str] = field(default_factory=lambda: ["stderr"])
    file_path: Optional[Path] = None
    max_file_size_mb: float = 10  # Size limit before rotating to a new log file
    backup_count: int = 5  # Number of rotated log files to keep (log.1, log.2, etc.)
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"  # Standard format, timezone handled by logging configuration
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}. Must be one of {valid_levels}")
        
        # Normalize level to uppercase
        self.level = self.level.upper()
        
        valid_handlers = {"stderr", "file"}
        for handler in self.handlers:
            if handler not in valid_handlers:
                raise ValueError(f"Invalid handler: {handler}. Must be one of {valid_handlers}")
        
        if "file" in self.handlers and self.file_path is None:
            raise ValueError("file_path is required when using file handler")
        
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
        
        if self.backup_count < 0:
            raise ValueError("backup_count must be non-negative")
    
    @classmethod
    def from_schema(cls, schema: LoggingConfigSchema, config_directory: Optional[Path] = None) -> 'LoggingConfig':
        """Create from validated Pydantic schema.
        
        Args:
            schema: Validated logging configuration schema
            config_directory: Directory containing the configuration file (for path resolution)
        """
        # Resolve file_path relative to config directory if provided
        file_path = None
        if schema.file_path:
            if config_directory is not None:
                file_path = resolve_config_path(schema.file_path, config_directory)
            else:
                file_path = Path(schema.file_path)
                
        return cls(
            level=schema.level,
            handlers=schema.handlers,
            file_path=file_path,
            max_file_size_mb=schema.max_file_size_mb,
            backup_count=schema.backup_count,
            format=schema.format,
            date_format=schema.date_format
        )


@dataclass
class PluginConfig:
    """Internal representation of plugin configuration."""
    policy: str  # Changed from 'path' to 'policy' for policy-based system
    enabled: bool = True
    priority: int = 50  # Plugin execution priority (0-100, lower = higher priority)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not (0 <= self.priority <= 100):
            raise ValueError(f"Plugin priority must be between 0 and 100, got {self.priority}")
    
    @classmethod
    def from_schema(cls, schema: PluginConfigSchema) -> 'PluginConfig':
        """Create from validated Pydantic schema."""
        return cls(
            policy=schema.policy,
            enabled=schema.enabled,
            priority=schema.priority,
            config=schema.config
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'policy': self.policy,
            'enabled': self.enabled,
            'priority': self.priority,
            'config': self.config
        }


@dataclass
class PluginsConfig:
    """Internal representation of upstream-scoped plugin configurations."""
    security: Dict[str, List[PluginConfig]] = field(default_factory=dict)
    auditing: Dict[str, List[PluginConfig]] = field(default_factory=dict)
    
    @classmethod
    def from_schema(cls, schema: PluginsConfigSchema) -> 'PluginsConfig':
        """Create from validated Pydantic schema."""
        # Convert dictionary of upstream -> plugin lists to internal format
        security_dict = {}
        for upstream, plugins in (schema.security or {}).items():
            security_dict[upstream] = [PluginConfig.from_schema(p) for p in plugins]
            
        auditing_dict = {}
        for upstream, plugins in (schema.auditing or {}).items():
            auditing_dict[upstream] = [PluginConfig.from_schema(p) for p in plugins]
            
        return cls(
            security=security_dict,
            auditing=auditing_dict
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        security_dict = {}
        for upstream, plugins in self.security.items():
            security_dict[upstream] = [plugin.to_dict() for plugin in plugins]
            
        auditing_dict = {}
        for upstream, plugins in self.auditing.items():
            auditing_dict[upstream] = [plugin.to_dict() for plugin in plugins]
            
        return {
            'security': security_dict,
            'auditing': auditing_dict
        }


class UpstreamConfigSchema(BaseModel):
    """Schema for validating upstream MCP server configuration."""
    name: str  # Mandatory server name for consistent behavior
    transport: Literal["stdio", "http"] = "stdio"
    command: Optional[Union[str, List[str]]] = None  # For stdio transport - can be string or list
    url: Optional[HttpUrl] = None  # For http transport
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    
    @model_validator(mode='after')
    def validate_and_normalize_command(self) -> 'UpstreamConfigSchema':
        if self.transport == "stdio" and not self.command:
            raise ValueError("stdio transport requires 'command'")
        if self.transport == "http" and not self.url:
            raise ValueError("http transport requires 'url'")
        
        # Normalize string commands to list format
        if self.command and isinstance(self.command, str):
            import shlex
            try:
                self.command = shlex.split(self.command)
            except ValueError as e:
                raise ValueError(f"Invalid command string format: {e}")
        
        return self

@dataclass
class UpstreamConfig:
    """Configuration for upstream MCP server.
    
    Attributes:
        name: Mandatory server name for consistent behavior
        transport: Transport type ("stdio" or "http")
        command: List of command line arguments to start the MCP server
        url: URL for HTTP transport
        restart_on_failure: Whether to restart the server if it fails
        max_restart_attempts: Maximum number of restart attempts
    """
    name: str
    transport: str = "stdio"
    command: Optional[List[str]] = None
    url: Optional[str] = None
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.transport == "stdio" and not self.command:
            raise ValueError("stdio transport requires 'command'")
        if self.transport == "http" and not self.url:
            raise ValueError("http transport requires 'url'")
    
    @classmethod
    def from_schema(cls, schema: UpstreamConfigSchema) -> 'UpstreamConfig':
        """Create from validated Pydantic schema."""
        return cls(
            name=schema.name,
            transport=schema.transport,
            command=schema.command,
            url=str(schema.url) if schema.url else None,
            restart_on_failure=schema.restart_on_failure,
            max_restart_attempts=schema.max_restart_attempts
        )


@dataclass
class TimeoutConfig:
    """Timeout configuration for connections and requests.
    
    Attributes:
        connection_timeout: Timeout for establishing connections (seconds)
        request_timeout: Timeout for individual requests (seconds)
    """
    connection_timeout: int = 60
    request_timeout: int = 60
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.connection_timeout <= 0 or self.request_timeout <= 0:
            raise ValueError("Timeout values must be positive")


@dataclass
class HttpConfig:
    """HTTP transport configuration.
    
    Attributes:
        host: Host address to bind the HTTP server to
        port: Port number to bind the HTTP server to
    """
    host: str = "127.0.0.1"
    port: int = 8080
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not (1 <= self.port <= 65535):
            raise ValueError("Port must be between 1 and 65535")


class ProxyConfigSchema(BaseModel):
    """Schema for validating main proxy configuration."""
    transport: Literal["stdio", "http"]
    upstreams: Optional[Union[UpstreamConfigSchema, List[UpstreamConfigSchema]]] = None
    timeouts: Optional[Dict[str, Any]] = None
    http: Optional[Dict[str, Any]] = None
    plugins: Optional[PluginsConfigSchema] = None
    logging: Optional[LoggingConfigSchema] = None
    
    @model_validator(mode='after')
    def validate_upstreams_and_plugins(self) -> 'ProxyConfigSchema':
        if not self.upstreams:
            raise ValueError("At least one upstream server must be configured")
        
        # Normalize single upstream to list
        if not isinstance(self.upstreams, list):
            self.upstreams = [self.upstreams]
        
        # All servers must have names
        for i, upstream in enumerate(self.upstreams):
            if not upstream.name:
                raise ValueError(f"All upstream servers must have a 'name'. Server at index {i} is missing a name.")
        
        # Names must be unique
        names = [u.name for u in self.upstreams]
        if len(names) != len(set(names)):
            raise ValueError("Upstream server names must be unique")
        
        # Validate server names - check for __ separator (namespace delimiter)
        for upstream in self.upstreams:
            if "__" in upstream.name:
                raise ValueError(f"Server name '{upstream.name}' cannot contain '__'")
        
        # Validate plugin configurations
        if self.plugins:
            server_names = set(u.name for u in self.upstreams)
            self._validate_plugin_server_references(self.plugins, server_names)
        
        return self
    
    def _validate_plugin_server_references(self, plugins: 'PluginsConfigSchema', server_names: set) -> None:
        """Validate that plugin configurations reference valid server names."""
        # Handle new dictionary-based structure
        all_plugin_sections = []
        if plugins.security:
            all_plugin_sections.append(plugins.security)
        if plugins.auditing:
            all_plugin_sections.append(plugins.auditing)
        
        for plugin_section in all_plugin_sections:
            # Validate upstream keys (except _global and ignored _* keys)
            for upstream_key in plugin_section.keys():
                if upstream_key.startswith('_'):
                    if upstream_key == '_global':
                        continue  # _global is special and doesn't need to exist in upstreams
                    else:
                        continue  # Other _* keys are ignored
                
                # Check if upstream exists in configuration
                if upstream_key not in server_names:
                    available = ", ".join(sorted(server_names))
                    raise ValueError(
                        f"Plugin configuration references unknown upstream '{upstream_key}'. "
                        f"Available upstreams: {available}"
                    )
            
            # Validate individual plugin configurations within each upstream
            for upstream_key, plugin_list in plugin_section.items():
                for plugin in plugin_list:
                    config = plugin.config or {}
                    
                    # Check tool access control plugins for configuration
                    if plugin.policy == "tool_allowlist" and "tools" in config:
                        tools_config = config["tools"]
                        
                        # Validate format (tools should be a dict)
                        if isinstance(tools_config, dict):
                            for server_name in tools_config.keys():
                                if server_name not in server_names:
                                    available = ", ".join(sorted(server_names))
                                    raise ValueError(
                                        f"Tool access control plugin references unknown server '{server_name}'. "
                                        f"Available servers: {available}"
                                    )
                    
                    # Check other plugins for exemptions
                    elif "exemptions" in config and isinstance(config["exemptions"], dict):
                        exemptions = config["exemptions"]
                        if "tools" in exemptions and isinstance(exemptions["tools"], dict):
                            for server_name in exemptions["tools"].keys():
                                if server_name not in server_names:
                                    available = ", ".join(sorted(server_names))
                                    raise ValueError(
                                        f"Plugin '{plugin.policy}' references unknown server '{server_name}' in exemptions. "
                                        f"Available servers: {available}"
                                    )

@dataclass
class ProxyConfig:
    """Main proxy configuration.
    
    Attributes:
        transport: Transport type ("stdio" or "http")
        upstreams: List of upstream server configurations
        timeouts: Timeout configuration
        http: Optional HTTP transport configuration
        plugins: Optional plugin configuration
        logging: Optional logging configuration
    """
    transport: str
    upstreams: List[UpstreamConfig]
    timeouts: TimeoutConfig
    http: Optional[HttpConfig] = None
    plugins: Optional[PluginsConfig] = None
    logging: Optional[LoggingConfig] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.transport not in ("stdio", "http"):
            raise ValueError("Transport must be 'stdio' or 'http'")
        
        if self.transport == "http" and self.http is None:
            raise ValueError("HTTP transport requires http configuration")
        
        if not self.upstreams:
            raise ValueError("At least one upstream server must be configured")
        
        # All server names must be unique
        names = [u.name for u in self.upstreams]
        if len(names) != len(set(names)):
            raise ValueError("Upstream server names must be unique")
        
        # Validate server names - check for __ separator (namespace delimiter)
        for upstream in self.upstreams:
            if "__" in upstream.name:
                raise ValueError(f"Server name '{upstream.name}' cannot contain '__'")
    
    
    @classmethod
    def from_schema(cls, schema: ProxyConfigSchema, config_directory: Optional[Path] = None) -> 'ProxyConfig':
        """Create from validated Pydantic schema."""
        # Convert upstreams
        upstreams = [UpstreamConfig.from_schema(u) for u in schema.upstreams or []]
        
        # Create timeouts config
        timeouts = TimeoutConfig()
        if schema.timeouts:
            timeouts = TimeoutConfig(**schema.timeouts)
        
        # Create HTTP config
        http = None
        if schema.http:
            http = HttpConfig(**schema.http)
        
        # Create plugins config
        plugins = None
        if schema.plugins:
            plugins = PluginsConfig.from_schema(schema.plugins)
        
        # Create logging config
        logging = None
        if schema.logging:
            logging = LoggingConfig.from_schema(schema.logging, config_directory)
        
        return cls(
            transport=schema.transport,
            upstreams=upstreams,
            timeouts=timeouts,
            http=http,
            plugins=plugins,
            logging=logging
        )
