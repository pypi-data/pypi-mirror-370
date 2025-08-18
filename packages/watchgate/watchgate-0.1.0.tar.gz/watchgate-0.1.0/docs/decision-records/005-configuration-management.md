# ADR-005: Configuration Management Design

**Status**: Accepted

## Context

Watchgate requires flexible configuration management to support:

1. **Security Policies**: Configurable filtering rules and security parameters
2. **Server Connections**: Dynamic configuration of upstream MCP servers
3. **Transport Settings**: Different transport types with specific parameters
4. **Environment Adaptation**: Different settings for dev/staging/production
5. **Runtime Updates**: Some configurations may need dynamic updates
6. **Type Safety**: Prevent configuration errors that could impact security
7. **Plugin Extensibility**: Support for varied plugin configurations with proper validation

The configuration system must balance flexibility, type safety, ease of use, and extensibility.

## Decision

We will implement a **hybrid configuration system** that combines the strengths of Python dataclasses and Pydantic models:

### 1. Pydantic Models for Configuration Input/Validation

Pydantic models will handle the initial loading and validation of configuration from YAML files. This provides:

- Strong validation of user input with clear error messages
- Schema validation for complex, nested structures
- Type coercion for configuration values
- Support for default values and complex constraints

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Pydantic schemas for YAML validation
class ServerConfigSchema(BaseModel):
    """Schema for validating server configuration."""
    name: str
    command: List[str]
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    timeout: int = 30
    max_retries: int = 3

class PluginConfigSchema(BaseModel):
    """Schema for validating plugin configuration."""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    
class PluginsConfigSchema(BaseModel):
    """Schema for validating all plugin configurations."""
    security: List[PluginConfigSchema] = Field(default_factory=list)
    auditing: List[PluginConfigSchema] = Field(default_factory=list)
```

### 2. Dataclasses for Internal Representation

After validation, configurations are converted to immutable dataclasses for internal use:

- Lightweight representation with no runtime dependencies
- Consistent with Python standard library
- Clear type hints for IDE support and static analysis
- Immutability to prevent accidental modification

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ServerConfig:
    """Internal representation of server configuration."""
    name: str
    command: List[str]
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_schema(cls, schema: ServerConfigSchema) -> 'ServerConfig':
        """Create from validated schema."""
        return cls(
            name=schema.name,
            command=schema.command,
            args=schema.args,
            env=schema.env,
            timeout=schema.timeout,
            max_retries=schema.max_retries
        )

@dataclass
class PluginConfig:
    """Internal representation of plugin configuration."""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_schema(cls, schema: PluginConfigSchema) -> 'PluginConfig':
        """Create from validated schema."""
        return cls(
            name=schema.name,
            enabled=schema.enabled,
            config=schema.config
        )
```

### 3. Configuration Loading Pipeline

The configuration pipeline follows these steps:

1. Load YAML from file
2. Parse into Pydantic schema objects for validation
3. Convert validated schemas to internal dataclasses 
4. Use dataclass instances throughout the application

```python
# Example configuration loading pipeline
def load_config(path: Path) -> ProxyConfig:
    """Load configuration from YAML file."""
    # 1. Load and parse YAML
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    # 2. Validate with Pydantic schema
    config_schema = ProxyConfigSchema(**data)
    
    # 3. Convert to dataclass for internal use
    return ProxyConfig.from_schema(config_schema)
```

## Alternatives Considered

### Alternative 1: Pure Dataclasses Approach
```python
@dataclass
class ServerConfig:
    """Configuration for an upstream MCP server."""
    name: str
    command: List[str]
    timeout: int = 30
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.command:
            raise ValueError("Server command cannot be empty")
```
- **Pros**: Standard library only, no dependencies, lightweight
- **Cons**: Manual validation in `__post_init__`, limited validation features, error messages not as user-friendly

### Alternative 2: Pure Pydantic Approach
```python
from pydantic import BaseModel, Field, validator

class ServerConfig(BaseModel):
    name: str
    command: List[str]
    timeout: int = Field(default=30, gt=0)
    
    @validator('command')
    def command_not_empty(cls, v):
        if not v:
            raise ValueError("Server command cannot be empty")
        return v
```
- **Pros**: Rich validation, excellent error messages, JSON schema support
- **Cons**: Additional dependency for the entire application, performance overhead

### Alternative 3: Dictionary-Based Configuration
```python
# Simple dictionary approach
config = {
    "servers": [
        {"name": "server1", "command": ["python", "server.py"]},
        {"name": "server2", "command": ["node", "server.js"]}
    ],
    "security": {
        "allowed_methods": ["ping", "tools/list"],
        "rate_limit": 100
    }
}
```
- **Pros**: Simple, flexible, familiar
- **Cons**: No type safety, runtime errors, hard to validate

### Alternative 4: Configuration Classes with Properties
```python
class Config:
    def __init__(self, config_dict):
        self._config = config_dict
    
    @property
    def servers(self):
        return self._config.get('servers', [])
```
- **Pros**: Encapsulation, lazy loading
- **Cons**: No type hints, manual property implementation

### Alternative 5: Environment Variables Only
```python
import os

ALLOWED_METHODS = os.getenv('WATCHGATE_ALLOWED_METHODS', '').split(',')
RATE_LIMIT = int(os.getenv('WATCHGATE_RATE_LIMIT', '100'))
```
- **Pros**: 12-factor app compliance, simple deployment
- **Cons**: Limited structure, difficult complex configurations

## Consequences

### Positive
- **Strong Input Validation**: Pydantic provides robust validation with clear error messages
- **Type Safety**: Compile-time checking prevents configuration errors through the system
- **IDE Support**: Auto-completion and type hints in both validation and internal models
- **Separation of Concerns**: Clear distinction between external validation and internal representation
- **Extensibility**: Pydantic's validation capabilities support complex plugin configuration needs
- **Testability**: Easy to create and validate test configurations
- **Immutability**: Internal dataclass models prevent accidental configuration changes

### Negative
- **Additional Dependency**: Introduces Pydantic as a project dependency
- **Conversion Overhead**: Small performance cost to convert between validation and internal models
- **Two Systems to Maintain**: Need to keep Pydantic schemas and dataclasses in sync
- **Learning Curve**: Team must understand both Pydantic and dataclass patterns
- **Schema Evolution**: Requires careful handling of breaking changes in both systems

## Implementation Examples

### Configuration Loading Pipeline

```python
class ConfigLoader:
    """YAML configuration file loader with hybrid validation approach."""
    
    def load_from_file(self, path: Path) -> ProxyConfig:
        """Load configuration from YAML file."""
        try:
            # 1. Load YAML content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # 2. Parse YAML into dictionary
            if not content:
                raise ValueError("Configuration file is empty")
                
            config_dict = yaml.safe_load(content)
            
            if config_dict is None:
                raise ValueError("Configuration file contains only comments or is empty")
                
            # 3. Validate with Pydantic schema
            proxy_schema = ProxyConfigSchema(**config_dict)
            
            # 4. Convert to dataclass for internal use
            return ProxyConfig.from_schema(proxy_schema)
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
```

### Plugin Configuration Example

```python
# 1. Pydantic schema for plugin configuration validation
class PluginConfigSchema(BaseModel):
    """Schema for validating plugin configuration."""
    path: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    
class PluginsConfigSchema(BaseModel):
    """Schema for validating all plugin configurations."""
    security: List[PluginConfigSchema] = Field(default_factory=list)
    auditing: List[PluginConfigSchema] = Field(default_factory=list)

# 2. Dataclass for internal representation
@dataclass
class PluginConfig:
    """Internal dataclass representation of plugin configuration."""
    path: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_schema(cls, schema: PluginConfigSchema) -> 'PluginConfig':
        return cls(
            path=schema.path,
            enabled=schema.enabled,
            config=schema.config
        )

# 3. Usage example in PluginManager
class PluginManager:
    def __init__(self, plugins_config: Dict[str, Any]):
        # Convert from dictionary to Pydantic model for validation
        plugins_schema = PluginsConfigSchema(**plugins_config)
        
        # Convert validated schemas to internal dataclasses
        self.security_plugins_config = [
            PluginConfig.from_schema(schema) 
            for schema in plugins_schema.security
        ]
        self.auditing_plugins_config = [
            PluginConfig.from_schema(schema)
            for schema in plugins_schema.auditing
        ]
```

### Complete Configuration Example (YAML)

```yaml
# watchgate.yaml example with all sections
proxy:
  transport: "stdio"  # "stdio" or "http"
  
  # Upstream server settings
  upstream:
    command: ["python", "-m", "mcp_server"]
    restart_on_failure: true
    max_restart_attempts: 3
  
  # Connection timeouts
  timeouts:
    connection_timeout: 30
    request_timeout: 60
  
  # HTTP transport settings (when transport is "http")
  http:
    host: "127.0.0.1"
    port: 8080
  
  # Plugin configuration section
  plugins:
    # Security plugins
    security:
      - policy: "tool_allowlist"
        enabled: true
        config:
          mode: "allowlist"  # allowlist, blocklist, allow_all
          tools:
            - "read_file"
            - "list_directory"
            - "semantic_search"
      
      - policy: "rate_limiter"
        enabled: true
        config:
          requests_per_minute: 60
          burst_limit: 10
    
    # Auditing plugins
    auditing:
      - policy: "file_auditing"
        enabled: true
        config:
          file: "watchgate.log"
          max_size_mb: 10
          format: "json"  # json or text
      
      - policy: "database_logger"
        enabled: false
        config:
          connection_string: "sqlite:///audit.db"
          batch_size: 100
```

### Environment Variables Integration

Our hybrid approach also supports environment variable overrides, providing flexibility for different deployment environments:

```python
# Support environment variable overrides with clear naming patterns
# AG_PROXY_TIMEOUTS_CONNECTION_TIMEOUT=60 overrides connection timeout
# AG_PROXY_PLUGINS_SECURITY_0_ENABLED=false disables first security plugin

def _apply_env_overrides(config_dict: dict) -> dict:
    """Apply environment variable overrides to configuration."""
    for key, value in os.environ.items():
        if key.startswith('AG_'):
            path = key[3:].lower().split('_')  # Remove AG_ prefix
            
            # Handle array indexing in path (e.g., SECURITY_0_ENABLED)
            processed_path = []
            for segment in path:
                if segment.isdigit():
                    # Convert digit segments to integer indexes
                    processed_path.append(int(segment))
                else:
                    processed_path.append(segment)
            
            # Set the value in the nested dictionary
            _set_nested_value(config_dict, processed_path, _convert_value_type(value))
            
    return config_dict

def _convert_value_type(value: str) -> Any:
    """Convert string value to appropriate type."""
    if value.lower() in ('true', 'yes'):
        return True
    if value.lower() in ('false', 'no'):
        return False
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value  # Keep as string if not a special value
```

### Schema Evolution Strategy

Our hybrid approach facilitates configuration schema evolution through version tracking and migration functions:

```python
class ProxyConfigSchema(BaseModel):
    """Schema for proxy configuration with version support."""
    version: str = "1.0"
    transport: str
    upstream: UpstreamConfigSchema
    timeouts: TimeoutConfigSchema
    http: Optional[HttpConfigSchema] = None
    plugins: Optional[PluginsConfigSchema] = None
    
    @validator('version')
    def validate_version(cls, v):
        """Validate configuration version."""
        if v not in ["0.9", "1.0"]:
            raise ValueError(f"Unsupported configuration version: {v}")
        return v
    
    def apply_migrations(self):
        """Apply migrations based on configuration version."""
        if self.version == "0.9":
            # Convert v0.9 to v1.0 format
            if not hasattr(self, 'plugins'):
                self.plugins = PluginsConfigSchema()
            # Other migration logic...
            self.version = "1.0"
        return self
```

## Testing Strategy

The hybrid configuration system can be thoroughly tested at multiple levels:

```python
# Unit testing the validation layer
def test_plugin_config_schema_validation():
    """Test Pydantic validation for plugin configuration."""
    # Valid configuration
    valid_config = {"name": "test_plugin", "enabled": True, "config": {"key": "value"}}
    schema = PluginConfigSchema(**valid_config)
    assert schema.name == "test_plugin"
    assert schema.enabled is True
    
    # Invalid configuration (missing required field)
    invalid_config = {"enabled": True}
    with pytest.raises(ValidationError):
        PluginConfigSchema(**invalid_config)

# Testing the conversion to internal dataclasses
def test_plugin_config_conversion():
    """Test conversion from schema to dataclass."""
    schema = PluginConfigSchema(name="test_plugin", enabled=False, config={"setting": 123})
    dataclass_config = PluginConfig.from_schema(schema)
    
    assert isinstance(dataclass_config, PluginConfig)
    assert dataclass_config.name == "test_plugin"
    assert dataclass_config.enabled is False
    assert dataclass_config.config == {"setting": 123}

# Integration testing with YAML files
def test_config_loading_from_yaml(tmp_path):
    """Test loading configuration from YAML file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
    proxy:
      transport: stdio
      upstream:
        command: ["python", "-m", "server"]
      timeouts:
        connection_timeout: 30
        request_timeout: 60
      plugins:
        security:
          - name: test_plugin
            enabled: true
            config:
              mode: test
    """)
    
    config = ConfigLoader().load_from_file(config_file)
    assert config.transport == "stdio"
    assert len(config.plugins.security) == 1
    assert config.plugins.security[0].name == "test_plugin"
```

## Review and Evolution

This hybrid configuration management approach addresses the needs of both stability (through dataclasses) and flexibility (through Pydantic schemas). It provides a solid foundation for Watchgate's configuration requirements while enabling the extensibility needed for plugins.

### Key Benefits Realized
- **Type Safety** throughout the configuration pipeline
- **Clear Error Messages** for configuration issues
- **Extensibility** for plugin configuration
- **Separation of Concerns** between validation and internal representation

### Additional Considerations
- Configuration update API for runtime changes
- Schema versioning for backward compatibility as the system evolves
- Generating JSON schema from Pydantic models for configuration documentation
- Performance impact of the validation and conversion process

This approach may need adjustment when:
- Configuration schema complexity increases significantly
- New validation requirements emerge that are challenging to implement
- Performance profiling indicates overhead concerns
- Additional configuration sources beyond YAML files are needed
