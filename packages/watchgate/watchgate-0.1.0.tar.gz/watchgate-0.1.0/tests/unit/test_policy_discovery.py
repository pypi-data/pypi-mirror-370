"""Tests for policy discovery and loading functionality."""

import pytest
from typing import Optional
from unittest.mock import patch, MagicMock
from pathlib import Path
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, AuditingPlugin, PolicyDecision


class TestPolicyDiscovery:
    """Test policy discovery functionality."""

    def test_policy_discovery_scans_security_directory(self):
        """Test that policy discovery scans the security plugin directory."""
        config = {
            "security": {"_global": [{"policy": "tool_allowlist", "enabled": True, "config": {}}]},
            "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        
        # This should discover policies from watchgate/plugins/security/
        policies = manager._discover_policies("security")
        
        # Should find at least the tool_allowlist policy
        assert "tool_allowlist" in policies
        assert callable(policies["tool_allowlist"])
    
    def test_policy_discovery_scans_auditing_directory(self):
        """Test that policy discovery scans the auditing plugin directory."""
        config = {
            "security": {"_global": []},
            "auditing": {"_global": [{"policy": "json_auditing", "enabled": True, "config": {}}]}
        }
        
        manager = PluginManager(config)
        
        # This should discover policies from watchgate/plugins/auditing/
        policies = manager._discover_policies("auditing")
        
        # Should find at least the json_auditing policy
        assert "json_auditing" in policies
        assert callable(policies["json_auditing"])
        
    def test_policy_discovery_handles_missing_directory(self):
        """Test policy discovery handles missing plugin directories gracefully."""
        config = {"security": {"_global": []}, "auditing": {"_global": []}}
        manager = PluginManager(config)
        
        # Should return empty dict for non-existent category
        policies = manager._discover_policies("nonexistent")
        assert policies == {}
        
    def test_policy_discovery_ignores_files_without_policies_manifest(self):
        """Test that files without POLICIES manifest are ignored."""
        config = {"security": {"_global": []}, "auditing": {"_global": []}}
        manager = PluginManager(config)
        
        with patch('pathlib.Path.glob') as mock_glob:
            # Mock finding a Python file
            mock_file = MagicMock()
            mock_file.is_file.return_value = True
            mock_file.suffix = '.py'
            mock_file.__str__ = lambda: 'test_file.py'
            mock_glob.return_value = [mock_file]
            
            with patch('importlib.util.spec_from_file_location') as mock_spec:
                mock_module = MagicMock()
                # Module without POLICIES attribute
                del mock_module.POLICIES  # Ensure no POLICIES attribute
                mock_spec.return_value.loader.exec_module.return_value = None
                
                policies = manager._discover_policies("security")
                
                # Should be empty since no POLICIES manifest found
                assert policies == {}


class TestPolicyBasedLoading:
    """Test policy-based plugin loading."""
    
    @pytest.mark.asyncio
    async def test_load_plugin_by_policy_name(self):
        """Test loading a plugin by policy name."""
        config = {
            "security": {"_global": [{"policy": "tool_allowlist", "enabled": True, "config": {"mode": "allow_all"}}]},
            "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        
        # Create a proper mock plugin class that inherits from SecurityPlugin
        class MockSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                self.config = config
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test")
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test")
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test")
        
        # Mock policy discovery
        with patch.object(manager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {"tool_allowlist": MockSecurityPlugin}
            
            await manager.load_plugins()
            
            # Should have loaded one security plugin
            assert len(manager.security_plugins) == 1
            assert isinstance(manager.security_plugins[0], MockSecurityPlugin)
            assert manager.security_plugins[0].config == {"mode": "allow_all"}
    
    @pytest.mark.asyncio
    async def test_load_plugin_policy_not_found_error(self):
        """Test error when requested policy is not found."""
        config = {
            "security": {"_global": [{"policy": "nonexistent_policy", "enabled": True, "config": {}}]},
            "auditing": {}
        }
        
        manager = PluginManager(config)
        
        # Create a proper mock plugin class
        class MockSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                self.config = config
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test")
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test")
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test")
        
        # Mock policy discovery returning only tool_allowlist
        with patch.object(manager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {"tool_allowlist": MockSecurityPlugin}
            
            with pytest.raises(ValueError) as exc_info:
                await manager.load_plugins()
            
            error_msg = str(exc_info.value)
            assert "Policy 'nonexistent_policy' not found" in error_msg
            assert "Available policies: tool_allowlist" in error_msg
    
    @pytest.mark.asyncio
    async def test_load_multiple_policies_from_same_file(self):
        """Test loading multiple policies from the same plugin file."""
        config = {
            "security": {
                "_global": [
                    {"policy": "policy_one", "enabled": True, "config": {}},
                    {"policy": "policy_two", "enabled": True, "config": {}}
                ]
            },
            "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        
        # Create proper mock plugin classes
        class MockSecurityPlugin1(SecurityPlugin):
            def __init__(self, config):
                self.config = config
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test1")
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test1")
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test1")
                
        class MockSecurityPlugin2(SecurityPlugin):
            def __init__(self, config):
                self.config = config
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test2")
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test2")
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="test2")
        
        # Mock policy discovery with multiple policies
        with patch.object(manager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "policy_one": MockSecurityPlugin1,
                "policy_two": MockSecurityPlugin2
            }
            
            await manager.load_plugins()
            
            # Should have loaded two security plugins
            assert len(manager.security_plugins) == 2
            assert isinstance(manager.security_plugins[0], MockSecurityPlugin1)
            assert isinstance(manager.security_plugins[1], MockSecurityPlugin2)


class TestPolicyConfigurationValidation:
    """Test policy-based configuration validation."""
    
    def test_policy_field_required(self):
        """Test that policy field is required in plugin configuration."""
        from watchgate.config.models import PluginConfigSchema
        from pydantic import ValidationError
        
        # Should raise validation error for missing policy field
        with pytest.raises(ValidationError) as exc_info:
            PluginConfigSchema(enabled=True, config={})
        
        assert "policy" in str(exc_info.value)
    
    def test_policy_field_validation(self):
        """Test policy field validation."""
        from watchgate.config.models import PluginConfigSchema
        
        # Valid policy configuration
        config = PluginConfigSchema(
            policy="tool_allowlist", 
            enabled=True, 
            config={"mode": "allow_all"}
        )
        
        assert config.policy == "tool_allowlist"
        assert config.enabled is True
        assert config.config == {"mode": "allow_all"}
    
    def test_policy_config_backwards_compatibility_removed(self):
        """Test that path field is no longer supported."""
        from watchgate.config.models import PluginConfigSchema
        from pydantic import ValidationError
        
        # Should raise validation error for old path field
        with pytest.raises(ValidationError):
            PluginConfigSchema(
                path="./plugins/security/tool_allowlist.py",  # Old format
                enabled=True,
                config={}
            )
