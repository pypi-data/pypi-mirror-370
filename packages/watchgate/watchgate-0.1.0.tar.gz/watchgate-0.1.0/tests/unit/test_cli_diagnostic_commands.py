"""Tests for Watchgate CLI diagnostic commands."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, AsyncMock
from io import StringIO

from watchgate.main import debug_show_plugin_order, debug_validate_priorities


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
def invalid_config_file():
    """Create a config file with invalid priorities for testing."""
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
        priority: 150  # Invalid - outside 0-100 range
        config:
          mode: "allowlist"
          tools: 
            test_server: ["read_file"]
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield Path(f.name)
    
    # Cleanup
    os.unlink(f.name)


@pytest.mark.asyncio
async def test_debug_show_plugin_order(sample_config_file, capsys):
    """Test the debug show plugin order command."""
    await debug_show_plugin_order(sample_config_file)
    
    captured = capsys.readouterr()
    
    # Check that output contains expected information
    assert "Plugin Execution Order:" in captured.out
    assert "Security Plugins" in captured.out
    assert "Auditing Plugins" in captured.out
    assert "ToolAllowlistPlugin" in captured.out
    assert "JsonAuditingPlugin" in captured.out
    assert "priority: 10" in captured.out
    assert "priority: 50" in captured.out
    assert "Total plugins loaded: 2" in captured.out


@pytest.mark.asyncio
async def test_debug_show_plugin_order_no_plugins(capsys):
    """Test the debug show plugin order command with no plugins configured."""
    config_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "echo test"
  timeouts:
    connection_timeout: 30
    request_timeout: 60
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        config_path = Path(f.name)
    
    try:
        await debug_show_plugin_order(config_path)
        
        captured = capsys.readouterr()
        
        # Check that output handles no plugins gracefully
        assert "Plugin Execution Order:" in captured.out
        assert "Security Plugins: None configured" in captured.out
        assert "Auditing Plugins: None configured" in captured.out
        assert "Total plugins loaded: 0" in captured.out
        
    finally:
        os.unlink(config_path)


@pytest.mark.asyncio
async def test_debug_validate_priorities_valid(sample_config_file, capsys):
    """Test the debug validate priorities command with valid priorities."""
    await debug_validate_priorities(sample_config_file)
    
    captured = capsys.readouterr()
    
    # Check that validation passes
    assert "Plugin Priority Validation:" in captured.out
    assert "✅ All plugin priorities are valid (0-100 range)" in captured.out


@pytest.mark.asyncio  
async def test_debug_validate_priorities_same_priority_warning(capsys):
    """Test the debug validate priorities command warns about same priorities."""
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
        config:
          mode: "allowlist"
          tools: 
            test_server: ["read_file"]
          priority: 50
  
  auditing:
    _global:
      - policy: "json_auditing"
        enabled: true
        config:
          file: "test.log"
          priority: 50  # Same as security plugin
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        config_path = Path(f.name)
    
    try:
        await debug_validate_priorities(config_path)
        
        captured = capsys.readouterr()
        
        # Check that same priority warning is shown
        assert "⚠️  Plugins with same priority" in captured.out
        assert "Priority 50: ToolAllowlistPlugin, JsonAuditingPlugin" in captured.out
        assert "potential issue(s) found, but priorities are valid" in captured.out
        
    finally:
        os.unlink(config_path)


@pytest.mark.asyncio
async def test_debug_validate_priorities_invalid(invalid_config_file, capsys):
    """Test the debug validate priorities command with invalid priorities."""
    with pytest.raises(SystemExit) as exc_info:
        await debug_validate_priorities(invalid_config_file)
    
    # Should exit with code 1 for validation failure
    assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    
    # Check that validation failure is reported
    assert "Plugin Priority Validation:" in captured.out
    assert "❌ Configuration validation failed:" in captured.out
    assert "Input should be less than or equal to 100" in captured.out


@pytest.mark.asyncio
async def test_debug_show_plugin_order_file_not_found(capsys):
    """Test debug show plugin order with non-existent config file."""
    non_existent_path = Path("/non/existent/config.yaml")
    
    with pytest.raises(SystemExit) as exc_info:
        await debug_show_plugin_order(non_existent_path)
    
    # Should exit with code 1 for file not found
    assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_debug_validate_priorities_file_not_found(capsys):
    """Test debug validate priorities with non-existent config file."""
    non_existent_path = Path("/non/existent/config.yaml")
    
    with pytest.raises(SystemExit) as exc_info:
        await debug_validate_priorities(non_existent_path)
    
    # Should exit with code 1 for file not found
    assert exc_info.value.code == 1


