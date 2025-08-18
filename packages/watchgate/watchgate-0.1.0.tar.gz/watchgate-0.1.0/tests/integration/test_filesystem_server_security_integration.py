"""Integration test for FilesystemServerSecurityPlugin to verify plugin loading and basic functionality."""

import pytest
import asyncio
from watchgate.plugins.manager import PluginManager
from watchgate.protocol.messages import MCPRequest


@pytest.mark.asyncio
async def test_plugin_discovery_and_loading():
    """Test that the filesystem server security plugin can be discovered and loaded."""
    config = {
        "security": {
            "_global": [
                {
                    "policy": "filesystem_server",
                    "enabled": True,
                    "config": {
                        "read": ["docs/*", "public/**/*.txt"],
                        "write": ["uploads/*", "admin/**/*"]
                    }
                }
            ]
        },
        "auditing": {"_global": []}
    }
    
    plugin_manager = PluginManager(config)
    await plugin_manager.load_plugins()
    
    # Verify plugin was loaded
    assert len(plugin_manager.security_plugins) == 1
    assert plugin_manager.security_plugins[0].__class__.__name__ == "FilesystemServerSecurityPlugin"


@pytest.mark.asyncio
async def test_end_to_end_request_processing():
    """Test end-to-end request processing through the plugin manager."""
    config = {
        "security": {
            "_global": [
                {
                    "policy": "filesystem_server",
                    "enabled": True,
                    "config": {
                        "read": ["docs/*"],
                        "write": ["uploads/*"]
                    }
                }
            ]
        },
        "auditing": {"_global": []}
    }
    
    plugin_manager = PluginManager(config)
    await plugin_manager.load_plugins()
    
    # Test allowed read request
    allowed_request = MCPRequest(
        jsonrpc="2.0",
        method="tools/call",
        params={
            "name": "read_file", 
            "arguments": {"path": "docs/readme.md"}
        },
        id="test-1"
    )
    
    decision = await plugin_manager.process_request(allowed_request)
    assert decision.allowed is True
    
    # Test denied read request
    denied_request = MCPRequest(
        jsonrpc="2.0",
        method="tools/call",
        params={
            "name": "read_file",
            "arguments": {"path": "secret/config.txt"}
        },
        id="test-2"
    )
    
    decision = await plugin_manager.process_request(denied_request)
    assert decision.allowed is False
    assert "access denied" in decision.reason.lower()


@pytest.mark.asyncio
async def test_plugin_with_empty_config():
    """Test plugin behavior with empty configuration (should deny all)."""
    config = {
        "security": {
            "_global": [
                {
                    "policy": "filesystem_server",
                    "enabled": True,
                    "config": {}
                }
            ]
        },
        "auditing": {"_global": []}
    }
    
    plugin_manager = PluginManager(config)
    await plugin_manager.load_plugins()
    
    # Test that empty config denies filesystem requests
    request = MCPRequest(
        jsonrpc="2.0",
        method="tools/call",
        params={
            "name": "read_file",
            "arguments": {"path": "any/file.txt"}
        },
        id="test-3"
    )
    
    decision = await plugin_manager.process_request(request)
    assert decision.allowed is False
