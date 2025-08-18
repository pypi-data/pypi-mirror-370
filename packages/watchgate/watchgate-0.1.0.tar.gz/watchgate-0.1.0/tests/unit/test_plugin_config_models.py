"""Tests for plugin configuration models."""

import pytest
from pydantic import ValidationError
from typing import Dict, Any

from watchgate.config.models import (
    PluginConfigSchema, PluginsConfigSchema,
    PluginConfig, PluginsConfig, ProxyConfig, ProxyConfigSchema
)


class TestPluginConfigSchema:
    """Test PluginConfigSchema Pydantic validation."""
    
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_valid_plugin_config_schema(self):
        """Test valid plugin configuration schema validation."""
        data = {
            "policy": "tool_allowlist",
            "enabled": True,
            "config": {
                "mode": "allowlist",
                "tools": ["read_file", "list_directory"]
            }
        }
        
        schema = PluginConfigSchema(**data)
        
        assert schema.policy == "tool_allowlist"
        assert schema.enabled is True
        assert schema.config == {
            "mode": "allowlist",
            "tools": ["read_file", "list_directory"]
        }
    
    def test_plugin_config_schema_defaults(self):
        """Test default values for plugin configuration."""
        data = {"policy": "tool_allowlist"}
        
        schema = PluginConfigSchema(**data)
        
        assert schema.policy == "tool_allowlist"
        assert schema.enabled is True  # Default value
        assert schema.config == {}  # Default empty dict
    
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_plugin_config_schema_validation_errors(self):
        """Test validation errors for invalid plugin configuration."""
        # Missing required policy field
        with pytest.raises(ValidationError) as exc_info:
            PluginConfigSchema(enabled=True, config={})
        
        error = exc_info.value
        assert "policy" in str(error).lower()
        assert ("field required" in str(error).lower() or "either 'policy' or 'name' field must be provided" in str(error).lower())
        
        # Invalid enabled type
        with pytest.raises(ValidationError) as exc_info:
            PluginConfigSchema(policy="tool_allowlist", enabled="invalid")
        
        error = exc_info.value
        assert "enabled" in str(error)
        
        # Invalid config type
        with pytest.raises(ValidationError) as exc_info:
            PluginConfigSchema(policy="tool_allowlist", config="invalid")
        
        error = exc_info.value
        assert "config" in str(error)


class TestPluginsConfigSchema:
    """Test PluginsConfigSchema Pydantic validation."""
    
    def test_valid_plugins_config_schema(self):
        """Test valid plugins configuration schema validation."""
        data = {
            "security": {
                "_global": [
                    {
                        "policy": "tool_allowlist",
                        "enabled": True,
                        "config": {"mode": "allowlist"}
                    }
                ]
            },
            "auditing": {
                "_global": [
                    {
                        "policy": "json_auditing",
                        "enabled": True,
                        "config": {"file": "test.log"}
                    }
                ]
            }
        }
        
        schema = PluginsConfigSchema(**data)
        
        assert len(schema.security["_global"]) == 1
        assert len(schema.auditing["_global"]) == 1
        assert schema.security["_global"][0].policy == "tool_allowlist"
        assert schema.auditing["_global"][0].policy == "json_auditing"
    
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_plugins_config_schema_defaults(self):
        """Test default values for plugins configuration."""
        schema = PluginsConfigSchema()
        
        assert schema.security == {}  # Default empty dict
        assert schema.auditing == {}  # Default empty dict
    
    def test_plugins_config_schema_partial(self):
        """Test plugins configuration with only one plugin type."""
        data = {
            "security": {
                "_global": [
                    {"policy": "tool_allowlist"}
                ]
            }
        }
        
        schema = PluginsConfigSchema(**data)
        
        assert len(schema.security["_global"]) == 1
        assert len(schema.auditing) == 0  # Uses default


class TestPluginConfig:
    """Test PluginConfig dataclass."""
    
    def test_plugin_config_from_schema(self):
        """Test conversion from schema to dataclass."""
        schema = PluginConfigSchema(
            policy="tool_allowlist",
            enabled=True,
            config={"mode": "allowlist", "tools": ["read_file"]}
        )
        
        config = PluginConfig.from_schema(schema)
        
        assert config.policy == "tool_allowlist"
        assert config.enabled is True
        assert config.config == {"mode": "allowlist", "tools": ["read_file"]}
    
    def test_plugin_config_policy_field(self):
        """Test that plugin config uses 'policy' field (not 'path')."""
        config = PluginConfig(
            policy="tool_allowlist",
            enabled=True,
            config={}
        )
        
        assert hasattr(config, 'policy')
        assert not hasattr(config, 'path')
        assert config.policy == "tool_allowlist"
    
    def test_plugin_config_defaults(self):
        """Test default values for plugin configuration."""
        config = PluginConfig(policy="tool_allowlist")
        
        assert config.policy == "tool_allowlist"
        assert config.enabled is True
        assert config.config == {}


class TestPluginsConfig:
    """Test PluginsConfig dataclass."""
    
    def test_plugins_config_from_schema(self):
        """Test conversion of full plugins configuration."""
        schema = PluginsConfigSchema(
            security={
                "_global": [
                    PluginConfigSchema(
                        policy="tool_allowlist",
                        enabled=True,
                        config={"mode": "allowlist"}
                    )
                ]
            },
            auditing={
                "_global": [
                    PluginConfigSchema(
                        policy="json_auditing",
                        enabled=True,
                        config={"file": "test.log"}
                    )
                ]
            }
        )
        
        config = PluginsConfig.from_schema(schema)
        
        assert len(config.security["_global"]) == 1
        assert len(config.auditing["_global"]) == 1
        assert config.security["_global"][0].policy == "tool_allowlist"
        assert config.auditing["_global"][0].policy == "json_auditing"
    
    def test_empty_plugins_config(self):
        """Test empty plugin configuration (should use defaults)."""
        schema = PluginsConfigSchema()
        config = PluginsConfig.from_schema(schema)
        
        assert config.security == {}
        assert config.auditing == {}
    
    def test_plugins_config_defaults(self):
        """Test default values for plugins configuration."""
        config = PluginsConfig()
        
        assert config.security == {}
        assert config.auditing == {}


class TestProxyConfigWithPlugins:
    """Test ProxyConfig with plugin configuration support."""
    
    def test_proxy_config_with_plugins(self):
        """Test ProxyConfig with plugin configuration."""
        from watchgate.config.models import UpstreamConfig, TimeoutConfig
        
        upstream = UpstreamConfig(name="test", command=["python", "-m", "test"])
        timeouts = TimeoutConfig(connection_timeout=30, request_timeout=60)
        plugins = PluginsConfig(
            security={
                "_global": [
                    PluginConfig(
                        policy="tool_allowlist",
                        enabled=True,
                        config={"mode": "allowlist"}
                    )
                ]
            }
        )
        
        config = ProxyConfig(
            transport="stdio",
            upstreams=[upstream],
            timeouts=timeouts,
            plugins=plugins
        )
        
        assert config.transport == "stdio"
        assert config.upstreams[0] == upstream
        assert config.timeouts == timeouts
        assert config.plugins == plugins
        assert len(config.plugins.security["_global"]) == 1
    
    def test_proxy_config_without_plugins(self):
        """Test ProxyConfig without plugin configuration (backwards compatibility)."""
        from watchgate.config.models import UpstreamConfig, TimeoutConfig
        
        upstream = UpstreamConfig(name="test", command=["python", "-m", "test"])
        timeouts = TimeoutConfig(connection_timeout=30, request_timeout=60)
        
        config = ProxyConfig(
            transport="stdio",
            upstreams=[upstream],
            timeouts=timeouts
        )
        
        assert config.transport == "stdio"
        assert config.upstreams[0] == upstream
        assert config.timeouts == timeouts
        assert config.plugins is None  # Should be None when not provided


class TestServerAwareToolConfiguration:
    """Test new server-aware tool configuration format."""
    
    def test_tool_allowlist_server_aware_config_schema(self):
        """Test server-aware tool configuration schema validation (should fail initially)."""
        # This test should fail until we implement the new server-aware format
        server_aware_config = {
            "policy": "tool_allowlist",
            "config": {
                "mode": "allowlist",
                "tools": {
                    "filesystem": ["read_file", "write_file"],
                    "fetch": ["fetch"]
                }
            }
        }
        
        # This should pass when server-aware config is implemented
        schema = PluginConfigSchema(**server_aware_config)
        
        # Validate the nested structure
        assert schema.config["tools"]["filesystem"] == ["read_file", "write_file"]
        assert schema.config["tools"]["fetch"] == ["fetch"]
    
    def test_tool_allowlist_old_format_still_works(self):
        """Test that old list format still works for now (but server-aware is preferred)."""
        # Simple list format still works (no __ in tool names since we never shipped that)
        old_config = {
            "policy": "tool_allowlist", 
            "config": {
                "mode": "allowlist",
                "tools": ["read_file", "fetch"]  # Simple tool names
            }
        }
        
        # This should still work - simple validation
        schema = PluginConfigSchema(**old_config)
        assert schema.config["tools"] == ["read_file", "fetch"]
    
    def test_tool_allowlist_server_name_validation(self):
        """Test server name validation against upstream configs."""
        # This should validate server names exist in upstream configuration
        
        proxy_config = {
            "transport": "stdio",
            "upstreams": [
                {"name": "filesystem", "command": ["python", "-m", "filesystem"]},
                {"name": "fetch", "command": ["python", "-m", "fetch"]}
            ],
            "plugins": {
                "security": {
                    "nonexistent": [{  # This upstream doesn't exist
                        "policy": "tool_allowlist",
                        "config": {
                            "mode": "allowlist", 
                            "tools": ["some_tool"]
                        }
                    }]
                }
            }
        }
        
        # Should fail validation due to nonexistent upstream
        with pytest.raises(ValidationError) as exc_info:
            ProxyConfigSchema(**proxy_config)
        
        error = str(exc_info.value)
        assert "nonexistent" in error
    
    def test_single_server_requires_name(self):
        """Test that all servers require names."""
        # All servers should require names
        proxy_config = {
            "transport": "stdio", 
            "upstreams": [
                {"command": ["python", "-m", "filesystem"]}  # No name provided
            ],
            "plugins": {
                "security": {
                    "_global": [{
                        "policy": "tool_allowlist",
                        "config": {
                            "mode": "allowlist",
                            "tools": {
                                "filesystem": ["read_file"]  # Can't reference server without name
                            }
                        }
                    }]
                }
            }
        }
        
        # Should fail because upstream has no name but plugin references "filesystem"
        with pytest.raises(ValidationError) as exc_info:
            ProxyConfigSchema(**proxy_config)
        
        error = str(exc_info.value)
        assert "name" in error.lower()
    
    def test_pii_filter_server_aware_config(self):
        """Test server-aware configuration for PII filter plugin (should fail initially)."""
        # Test that other plugins support server-aware exemptions
        server_aware_pii_config = {
            "policy": "pii_filter",
            "config": {
                "action": "redact",
                "exemptions": {
                    "tools": {
                        "filesystem": ["read_file"],  # No PII filtering for filesystem reads
                        "fetch": []  # Apply PII filtering to all fetch tools
                    }
                }
            }
        }
        
        # This should work when server-aware config is implemented for all plugins
        schema = PluginConfigSchema(**server_aware_pii_config)
        assert "exemptions" in schema.config
        assert "tools" in schema.config["exemptions"]
