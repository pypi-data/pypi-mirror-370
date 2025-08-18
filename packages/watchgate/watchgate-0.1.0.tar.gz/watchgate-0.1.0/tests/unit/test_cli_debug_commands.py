"""Tests for Watchgate CLI debug commands.

Tests for all debug subcommands following TDD methodology.
These tests are written in RED phase and should initially fail.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from io import StringIO

from watchgate.main import (
    debug_show_plugin_order, 
    debug_validate_priorities
)

from watchgate.main import (
    debug_validate_config,
    debug_list_available_plugins,
    debug_validate_plugin_config
)


@pytest.fixture
def sample_config_file():
    """Create a temporary config file for testing."""
    config_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "echo test"
  timeouts:
    connection_timeout: 30
    request_timeout: 60

plugins:
  security:
    _global:
      - policy: "tool_allowlist"
        enabled: true
        priority: 10
        config:
          mode: "allowlist"
          tools: 
            test_server: ["read_file", "write_file"]
  
  auditing:
    _global:
      - policy: "json_auditing" 
        enabled: true
        priority: 50
        config:
          output_file: "test.log"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield Path(f.name)
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def invalid_yaml_config_file():
    """Create a config file with invalid YAML syntax."""
    config_content = """
proxy:
  transport: stdio
  upstreams:
    - command: ["echo", "test"
  # Missing closing bracket - invalid YAML
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield Path(f.name)
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def missing_required_fields_config_file():
    """Create a config file missing required fields."""
    config_content = """
proxy:
  # Missing transport and upstream - required fields
  timeouts:
    connection_timeout: 30
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield Path(f.name)
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def type_validation_error_config_file():
    """Create a config file with type validation errors."""
    config_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "should be list not string"  # Type error
  timeouts:
    connection_timeout: "thirty"  # Should be int not string
    request_timeout: 60
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield Path(f.name)
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def invalid_plugin_config_file():
    """Create a config file with invalid plugin configuration."""
    config_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "echo test"

plugins:
  security:
    _global:
      - policy: "tool_allowlist"
        enabled: true
        priority: 10
        config:
          mode: "invalid_mode"  # Should be allowlist/denylist
          tools: "should_be_list_not_string"  # Type error
  
  auditing:
    _global:
      - policy: "json_auditing" 
        enabled: true
        priority: 50
        # Missing required config section
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield Path(f.name)
    
    # Cleanup
    os.unlink(f.name)


# Tests for debug config --validate command
class TestDebugConfigValidate:
    """Test cases for debug config --validate command."""
    
    @pytest.mark.asyncio
    async def test_debug_validate_config_valid_file(self, sample_config_file, capsys):
        """Test config validation with valid configuration file."""
        await debug_validate_config(sample_config_file)
        
        captured = capsys.readouterr()
        
        assert "Configuration Validation:" in captured.out
        assert "✅ Configuration is valid" in captured.out
        assert "All required fields present" in captured.out
        assert "All types valid" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_validate_config_invalid_yaml(self, invalid_yaml_config_file, capsys):
        """Test config validation with invalid YAML syntax."""
        with pytest.raises(SystemExit) as exc_info:
            await debug_validate_config(invalid_yaml_config_file)
        
        assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        
        assert "Configuration Validation:" in captured.out
        assert "❌ YAML syntax error:" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_validate_config_missing_required_fields(self, missing_required_fields_config_file, capsys):
        """Test config validation with missing required fields."""
        with pytest.raises(SystemExit) as exc_info:
            await debug_validate_config(missing_required_fields_config_file)
        
        assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        
        assert "Configuration Validation:" in captured.out
        assert "❌ Missing required field:" in captured.out
        assert "transport" in captured.out or "upstream" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_validate_config_type_validation_errors(self, type_validation_error_config_file, capsys):
        """Test config validation with type validation errors."""
        with pytest.raises(SystemExit) as exc_info:
            await debug_validate_config(type_validation_error_config_file)
        
        assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        
        assert "Configuration Validation:" in captured.out
        assert "❌ Configuration validation failed:" in captured.out
        assert "'<=' not supported between instances of 'str' and 'int'" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_validate_config_nonexistent_file(self, capsys):
        """Test config validation with non-existent config file."""
        non_existent_path = Path("/non/existent/config.yaml")
        
        with pytest.raises(SystemExit) as exc_info:
            await debug_validate_config(non_existent_path)
        
        assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        
        assert "Configuration Validation:" in captured.out
        assert "❌ Configuration file not found:" in captured.out


# Tests for debug plugins --list-available command
class TestDebugListAvailablePlugins:
    """Test cases for debug plugins --list-available command."""
    
    @pytest.mark.asyncio 
    async def test_debug_list_available_plugins_normal_operation(self, capsys):
        """Test listing all available plugins."""
        await debug_list_available_plugins()
        
        captured = capsys.readouterr()
        
        assert "Available Plugins:" in captured.out
        assert "Security Plugins:" in captured.out
        assert "Auditing Plugins:" in captured.out
        assert "tool_allowlist" in captured.out
        assert "json_auditing" in captured.out
        assert "pii" in captured.out
        assert "secrets" in captured.out
        assert "prompt_injection" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_list_available_plugins_with_descriptions(self, capsys):
        """Test listing plugins includes descriptions."""
        await debug_list_available_plugins()
        
        captured = capsys.readouterr()
        
        # Should include plugin descriptions
        assert "tool allowlist/blocklist functionality" in captured.out
        assert "JSON auditing plugin for GRC platform integration" in captured.out
        assert "PII content filtering" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_list_available_plugins_empty_directory(self, capsys):
        """Test listing plugins when plugin directory is empty."""
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {}
            
            await debug_list_available_plugins()
            
            captured = capsys.readouterr()
            
            assert "Available Plugins:" in captured.out
            assert "None found" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_list_available_plugins_discovery_errors(self, capsys):
        """Test listing plugins handles plugin discovery errors."""
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.side_effect = Exception("Plugin discovery failed")
            
            with pytest.raises(SystemExit) as exc_info:
                await debug_list_available_plugins()
            
            assert exc_info.value.code == 1
            
            captured = capsys.readouterr()
            
            assert "❌ Error discovering plugins:" in captured.out
            assert "Plugin discovery failed" in captured.out


# Tests for debug plugins --validate-config command
class TestDebugValidatePluginConfig:
    """Test cases for debug plugins --validate-config command."""
    
    @pytest.mark.asyncio
    async def test_debug_validate_plugin_config_valid(self, sample_config_file, capsys):
        """Test plugin config validation with valid configurations."""
        await debug_validate_plugin_config(sample_config_file)
        
        captured = capsys.readouterr()
        
        assert "Plugin Configuration Validation:" in captured.out
        assert "✅ All plugin configurations are valid" in captured.out
        assert "tool_allowlist: Valid" in captured.out
        assert "json_auditing: Valid" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_validate_plugin_config_invalid_schema(self, invalid_plugin_config_file, capsys):
        """Test plugin config validation with invalid plugin configuration schema."""
        with pytest.raises(SystemExit) as exc_info:
            await debug_validate_plugin_config(invalid_plugin_config_file)
        
        assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        
        assert "Plugin Configuration Validation:" in captured.out
        assert "❌ Plugin configuration errors found:" in captured.out
        assert "tool_allowlist" in captured.out
        assert "invalid_mode" in captured.out or "should_be_list_not_string" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_validate_plugin_config_missing_required_fields(self, capsys):
        """Test plugin config validation with missing required plugin config fields."""
        config_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "echo test"

plugins:
  security:
    _global:
      - policy: "tool_allowlist"
        enabled: true
        priority: 10
        # Missing required config section
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            config_path = Path(f.name)
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                await debug_validate_plugin_config(config_path)
            
            assert exc_info.value.code == 1
            
            captured = capsys.readouterr()
            
            assert "Plugin Configuration Validation:" in captured.out
            assert "❌ Plugin configuration errors found:" in captured.out  
            assert "must include 'mode'" in captured.out
            
        finally:
            os.unlink(config_path)
    
    @pytest.mark.asyncio
    async def test_debug_validate_plugin_config_no_plugins(self, capsys):
        """Test plugin config validation with no plugins configured."""
        config_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "echo test"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            config_path = Path(f.name)
        
        try:
            await debug_validate_plugin_config(config_path)
            
            captured = capsys.readouterr()
            
            assert "Plugin Configuration Validation:" in captured.out
            assert "No plugins configured" in captured.out
            
        finally:
            os.unlink(config_path)


# Tests for existing debug commands that should still work
class TestExistingDebugCommands:
    """Test cases for existing debug commands to ensure no regression."""
    
    @pytest.mark.asyncio
    async def test_debug_show_plugin_order(self, sample_config_file, capsys):
        """Test the debug show plugin order command works correctly."""
        await debug_show_plugin_order(sample_config_file)
        
        captured = capsys.readouterr()
        
        assert "Plugin Execution Order:" in captured.out
        assert "Security Plugins" in captured.out
        assert "Auditing Plugins" in captured.out
        assert "Total plugins loaded:" in captured.out
    
    @pytest.mark.asyncio
    async def test_debug_validate_priorities(self, sample_config_file, capsys):
        """Test the debug validate priorities command works correctly."""
        await debug_validate_priorities(sample_config_file)
        
        captured = capsys.readouterr()
        
        assert "Plugin Priority Validation:" in captured.out
        assert "✅ All plugin priorities are valid" in captured.out