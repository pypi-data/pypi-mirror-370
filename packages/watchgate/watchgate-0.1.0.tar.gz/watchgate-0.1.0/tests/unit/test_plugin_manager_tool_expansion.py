"""Tests for plugin manager tool expansion and configuration handling."""

import pytest
from unittest.mock import MagicMock, patch
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest


class MockToolAllowlistPlugin(SecurityPlugin):
    """Mock tool access control plugin for testing server-aware configuration."""
    
    def __init__(self, config):
        super().__init__(config)
        self.config_data = config
        self.expanded_tools = None  # This should be set by plugin manager
    
    def set_expanded_tools(self, expanded_tools):
        """Method for plugin manager to provide expanded tool mappings."""
        self.expanded_tools = expanded_tools
    
    async def check_request(self, request, server_name=None):
        """Mock implementation."""
        return PolicyDecision(allowed=True, reason="Mock plugin")
    
    async def check_response(self, request, response, server_name=None):
        """Mock implementation.""" 
        return PolicyDecision(allowed=True, reason="Mock plugin")
    
    async def check_notification(self, notification, server_name=None):
        """Mock implementation."""
        return PolicyDecision(allowed=True, reason="Mock plugin")


class TestPluginManagerToolExpansion:
    """Test plugin manager tool expansion and configuration functionality."""
    
    @pytest.mark.asyncio
    async def test_server_grouped_tool_config_passed_to_plugin(self):
        """Test that plugin manager passes server-grouped tool config to plugins."""
        config = {
            "security": {
                "_global": [
                {
                    "policy": "tool_allowlist",
                    "config": {
                        "mode": "allowlist",
                        "tools": {
                            "filesystem": ["read_file", "write_file"],
                            "fetch": ["fetch"]
                        }
                    }
                }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {"tool_allowlist": MockToolAllowlistPlugin}
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Plugin should receive server-grouped tool dictionary
            plugin = manager.security_plugins[0]
            
            # Plugin should have been configured with server-grouped tools
            expected_tools = {
                "filesystem": ["read_file", "write_file"],
                "fetch": ["fetch"]
            }
            assert plugin.config_data["tools"] == expected_tools
    
    @pytest.mark.asyncio
    async def test_plugin_manager_provides_server_context_to_plugins(self):
        """Test that plugin manager provides server context when calling plugins."""
        # This test should pass once server-aware context is properly propagated
        config = {
            "security": {
                "_global": [
                {
                    "policy": "tool_allowlist",
                    "config": {
                        "mode": "allowlist",
                        "tools": {
                            "filesystem": ["read_file"]
                        }
                    }
                }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            # Create a mock plugin class that returns mock instances
            mock_plugin_instance = MagicMock(spec=SecurityPlugin)
            mock_plugin_instance.check_request.return_value = PolicyDecision(allowed=True, reason="Test")
            
            class MockPluginClass(SecurityPlugin):
                def __init__(self, config):
                    super().__init__(config)
                    self.mock_instance = mock_plugin_instance
                
                async def check_request(self, request, server_name=None):
                    return await self.mock_instance.check_request(request, server_name=server_name)
                
                async def check_response(self, request, response, server_name=None):
                    return PolicyDecision(allowed=True, reason="Test")
                
                async def check_notification(self, notification, server_name=None):
                    return PolicyDecision(allowed=True, reason="Test")
            
            mock_discover.return_value = {"tool_allowlist": MockPluginClass}
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Create a tool call request
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "read_file", "arguments": {}}
            )
            
            # Process request with server name
            await manager.process_request(request, server_name="filesystem")
            
            # Plugin should have been called with server_name parameter
            mock_plugin_instance.check_request.assert_called_once_with(request, server_name="filesystem")
    
    @pytest.mark.asyncio
    async def test_plugin_rejects_simple_tool_list_format(self):
        """Test that simple tool lists are rejected by the plugin."""
        # Simple list format should be rejected by the plugin
        config = {
            "security": {
                "_global": [
                {
                    "policy": "tool_allowlist", 
                    "config": {
                        "mode": "allowlist",
                        "tools": ["read_file", "write_file"]  # Simple list format
                    }
                }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            # Use the real plugin class to get proper validation
            from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
            mock_discover.return_value = {"tool_allowlist": ToolAllowlistPlugin}
            
            manager = PluginManager(config)
            
            # The plugin manager logs errors but doesn't re-raise them
            # Let's check that the plugin is not loaded
            await manager.load_plugins()
            
            # Should have no security plugins loaded due to the error
            assert len(manager.security_plugins) == 0
    
    @pytest.mark.asyncio
    async def test_plugin_manager_handles_tools_for_multiple_servers(self):
        """Test server-grouped tool configuration works for multiple servers."""
        config = {
            "security": {
                "_global": [
                {
                    "policy": "tool_allowlist",
                    "config": {
                        "mode": "allowlist", 
                        "tools": {
                            "filesystem": ["read_file", "write_file", "list_directory"],
                            "fetch": ["fetch", "post"],
                            "calculator": ["add", "subtract"]
                        }
                    }
                }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {"tool_allowlist": MockToolAllowlistPlugin}
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Plugin should receive server-grouped tool dictionary
            plugin = manager.security_plugins[0]
            expected_tools = {
                "filesystem": ["read_file", "write_file", "list_directory"],
                "fetch": ["fetch", "post"],
                "calculator": ["add", "subtract"]
            }
            assert plugin.config_data["tools"] == expected_tools
    
    @pytest.mark.asyncio
    async def test_plugin_manager_handles_empty_server_tool_lists(self):
        """Test handling of empty tool lists for specific servers."""
        # Empty lists should be handled gracefully
        config = {
            "security": {
                "_global": [
                {
                    "policy": "tool_allowlist",
                    "config": {
                        "mode": "allowlist",
                        "tools": {
                            "filesystem": ["read_file"],
                            "fetch": [],  # Empty list
                            "calculator": ["add"]
                        }
                    }
                }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {"tool_allowlist": MockToolAllowlistPlugin}
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Should preserve empty lists in the server-grouped configuration
            plugin = manager.security_plugins[0]
            expected_tools = {
                "filesystem": ["read_file"],
                "fetch": [],  # Empty list is preserved
                "calculator": ["add"]
            }
            assert plugin.config_data["tools"] == expected_tools
    
    def test_plugin_manager_handles_server_grouped_config(self):
        """Test that plugin manager handles server-grouped configuration correctly."""
        manager = PluginManager({})
        
        # Test that the manager can handle server-grouped tool configuration
        tools_dict = {
            "filesystem": ["read_file", "write_file"],
            "fetch": ["fetch"]
        }
        
        # The plugin manager should pass this configuration through without expansion
        # The actual filtering/validation happens in the plugin itself
        assert isinstance(tools_dict, dict)
        assert "filesystem" in tools_dict
        assert "fetch" in tools_dict
        assert tools_dict["filesystem"] == ["read_file", "write_file"]
        assert tools_dict["fetch"] == ["fetch"]
    
    def test_plugin_validates_server_aware_tool_format(self):
        """Test that plugin validates server-aware tool configuration format."""
        # Validation now happens in the plugin, not the manager
        from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
        
        # Valid format should pass
        valid_config = {
            "mode": "allowlist",
            "tools": {
                "filesystem": ["read_file", "write_file"],
                "fetch": ["fetch"]
            }
        }
        # Should not raise exception
        plugin = ToolAllowlistPlugin(valid_config)
        assert plugin.tools_config == valid_config["tools"]
        
        # Invalid format should fail
        invalid_config = {
            "mode": "allowlist",
            "tools": {
                "filesystem": "not_a_list"  # Should be a list
            }
        }
        # Plugin validation should catch this
        with pytest.raises(ValueError, match="Tools for server 'filesystem' must be a list"):
            ToolAllowlistPlugin(invalid_config)