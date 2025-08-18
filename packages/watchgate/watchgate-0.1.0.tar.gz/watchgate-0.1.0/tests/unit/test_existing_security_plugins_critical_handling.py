"""Tests for updating existing security plugins with critical handling."""

import pytest
from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
from watchgate.plugins.security.secrets import BasicSecretsFilterPlugin
from watchgate.plugins.security.pii import BasicPIIFilterPlugin
from watchgate.plugins.security.prompt_injection import BasicPromptInjectionDefensePlugin
from watchgate.plugins.security.filesystem_server import FilesystemServerSecurityPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest


class TestExistingSecurityPluginsCriticalHandling:
    """Test that existing security plugins support critical handling."""
    
    def test_tool_allowlist_plugin_supports_critical_handling(self):
        """Test that ToolAllowlistPlugin supports critical configuration."""
        
        # Test default critical behavior
        plugin = ToolAllowlistPlugin({"mode": "allow_all"})
        assert plugin.is_critical() is True
        
        # Test explicit critical configuration
        plugin_critical = ToolAllowlistPlugin({"mode": "allow_all", "critical": True})
        assert plugin_critical.is_critical() is True
        
        # Test non-critical configuration
        plugin_non_critical = ToolAllowlistPlugin({"mode": "allow_all", "critical": False})
        assert plugin_non_critical.is_critical() is False
    
    def test_secrets_filter_plugin_supports_critical_handling(self):
        """Test that BasicSecretsFilterPlugin supports critical configuration."""
        
        # Test default critical behavior
        plugin = BasicSecretsFilterPlugin({"action": "block"})
        assert plugin.is_critical() is True
        
        # Test explicit critical configuration
        plugin_critical = BasicSecretsFilterPlugin({"action": "block", "critical": True})
        assert plugin_critical.is_critical() is True
        
        # Test non-critical configuration
        plugin_non_critical = BasicSecretsFilterPlugin({"action": "audit_only", "critical": False})
        assert plugin_non_critical.is_critical() is False
    
    def test_pii_filter_plugin_supports_critical_handling(self):
        """Test that BasicPIIFilterPlugin supports critical configuration."""
        
        # Test default critical behavior
        plugin = BasicPIIFilterPlugin({"action": "block"})
        assert plugin.is_critical() is True
        
        # Test explicit critical configuration
        plugin_critical = BasicPIIFilterPlugin({"action": "block", "critical": True})
        assert plugin_critical.is_critical() is True
        
        # Test non-critical configuration
        plugin_non_critical = BasicPIIFilterPlugin({"action": "audit_only", "critical": False})
        assert plugin_non_critical.is_critical() is False
    
    @pytest.mark.asyncio
    async def test_critical_configuration_affects_plugin_behavior(self):
        """Test that critical configuration doesn't change plugin behavior - only failure handling."""
        
        # Create two identical plugins with different critical settings
        plugin_critical = ToolAllowlistPlugin({
            "mode": "allowlist", 
            "tools": {"test_server": ["read_file"]},
            "critical": True
        })
        
        plugin_non_critical = ToolAllowlistPlugin({
            "mode": "allowlist", 
            "tools": {"test_server": ["read_file"]},
            "critical": False
        })
        
        # Both should behave identically for normal operations
        request_allowed = MCPRequest(jsonrpc="2.0", method="tools/call", id="1", params={"name": "read_file"})
        request_blocked = MCPRequest(jsonrpc="2.0", method="tools/call", id="2", params={"name": "write_file"})
        
        # Test allowed request
        decision_critical = await plugin_critical.check_request(request_allowed, server_name="test_server")
        decision_non_critical = await plugin_non_critical.check_request(request_allowed, server_name="test_server")
        
        assert decision_critical.allowed == decision_non_critical.allowed
        assert decision_critical.allowed is True
        
        # Test blocked request
        decision_critical = await plugin_critical.check_request(request_blocked, server_name="test_server")
        decision_non_critical = await plugin_non_critical.check_request(request_blocked, server_name="test_server")
        
        assert decision_critical.allowed == decision_non_critical.allowed
        assert decision_critical.allowed is False
    
    def test_prompt_injection_defense_plugin_supports_critical_handling(self):
        """Test that BasicPromptInjectionDefensePlugin supports critical configuration."""
        
        # Test default critical behavior
        plugin = BasicPromptInjectionDefensePlugin({"action": "block"})
        assert plugin.is_critical() is True
        
        # Test explicit critical configuration
        plugin_critical = BasicPromptInjectionDefensePlugin({"action": "block", "critical": True})
        assert plugin_critical.is_critical() is True
        
        # Test non-critical configuration
        plugin_non_critical = BasicPromptInjectionDefensePlugin({"action": "audit_only", "critical": False})
        assert plugin_non_critical.is_critical() is False
    
    def test_filesystem_server_security_plugin_supports_critical_handling(self):
        """Test that FilesystemServerSecurityPlugin supports critical configuration."""
        
        # Test default critical behavior
        plugin = FilesystemServerSecurityPlugin({"permissions": {"read": ["*.txt"], "write": []}})
        assert plugin.is_critical() is True
        
        # Test explicit critical configuration
        plugin_critical = FilesystemServerSecurityPlugin({
            "permissions": {"read": ["*.txt"], "write": []}, 
            "critical": True
        })
        assert plugin_critical.is_critical() is True
        
        # Test non-critical configuration
        plugin_non_critical = FilesystemServerSecurityPlugin({
            "permissions": {"read": ["*.txt"], "write": []}, 
            "critical": False
        })
        assert plugin_non_critical.is_critical() is False
    
    def test_all_security_plugins_support_critical_handling(self):
        """Integration test to verify ALL security plugins support critical handling."""
        
        # List of all security plugin classes and their minimum required config
        security_plugins = [
            (ToolAllowlistPlugin, {"mode": "allow_all"}),
            (BasicSecretsFilterPlugin, {"action": "audit_only"}),
            (BasicPIIFilterPlugin, {"action": "audit_only"}),
            (BasicPromptInjectionDefensePlugin, {"action": "audit_only"}),
            (FilesystemServerSecurityPlugin, {"permissions": {"read": ["*"], "write": []}})
        ]
        
        for plugin_class, min_config in security_plugins:
            # Test default behavior (should be critical)
            plugin_default = plugin_class(min_config)
            assert hasattr(plugin_default, 'is_critical'), f"{plugin_class.__name__} missing is_critical method"
            assert plugin_default.is_critical() is True, f"{plugin_class.__name__} should default to critical"
            
            # Test explicit critical configuration
            critical_config = {**min_config, "critical": True}
            plugin_critical = plugin_class(critical_config)
            assert plugin_critical.is_critical() is True, f"{plugin_class.__name__} critical config failed"
            
            # Test non-critical configuration
            non_critical_config = {**min_config, "critical": False}
            plugin_non_critical = plugin_class(non_critical_config)
            assert plugin_non_critical.is_critical() is False, f"{plugin_class.__name__} non-critical config failed"
