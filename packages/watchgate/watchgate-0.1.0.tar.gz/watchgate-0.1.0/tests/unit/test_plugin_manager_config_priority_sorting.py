"""Tests for plugin manager configuration-based priority sorting."""

import pytest
from unittest.mock import Mock
from watchgate.plugins.manager import PluginManager


class TestConfigBasedPrioritySorting:
    """Test that plugins loaded from configuration are sorted by priority."""
    
    @pytest.mark.asyncio
    async def test_security_plugins_loaded_in_priority_order(self):
        """Test that security plugins from config are sorted by priority regardless of config order."""
        # Configuration with plugins in random priority order
        plugins_config = {
            "security": {
                "_global": [
                    {
                        "policy": "pii",
                        "enabled": True,
                        "config": {
                            "action": "audit_only",
                            "priority": 90,  # Low priority (higher number = lower priority)
                            "pii_types": {
                                "email": {"enabled": True}
                            }
                        }
                    },
                    {
                        "policy": "tool_allowlist", 
                        "enabled": True,
                        "config": {
                            "mode": "allow_all",
                            "priority": 10  # High priority (lower number = higher priority)
                        }
                    },
                    {
                        "policy": "secrets",
                        "enabled": True,
                        "config": {
                            "action": "audit_only",
                            "priority": 50,  # Medium priority
                            "secret_types": {
                                "api_key": {"enabled": True}
                            }
                        }
                    }
                ]
            }
        }
        
        # Create plugin manager and load plugins
        manager = PluginManager(plugins_config)
        await manager.load_plugins()
        
        # Verify plugins are sorted by priority
        assert len(manager.security_plugins) == 3
        
        priorities = [plugin.priority for plugin in manager.security_plugins]
        plugin_names = [plugin.__class__.__name__ for plugin in manager.security_plugins]
        
        # Should be sorted in ascending priority order (lower numbers first)
        expected_priorities = [10, 50, 90]
        expected_plugin_names = ["ToolAllowlistPlugin", "BasicSecretsFilterPlugin", "BasicPIIFilterPlugin"]
        
        assert priorities == expected_priorities, f"Expected {expected_priorities}, got {priorities}"
        assert plugin_names == expected_plugin_names, f"Expected {expected_plugin_names}, got {plugin_names}"
    
    @pytest.mark.asyncio
    async def test_auditing_plugins_loaded_in_priority_order(self):
        """Test that auditing plugins from config are sorted by priority regardless of config order."""
        # Configuration with auditing plugins in random priority order
        plugins_config = {
            "auditing": {
                "_global": [
                    {
                        "policy": "json_auditing",
                        "enabled": True,
                        "config": {
                            "file": "/tmp/test.log",
                            "priority": 80,  # Low priority
                            "critical": False
                        }
                    }
                ]
            }
        }
        
        # Create plugin manager and load plugins
        manager = PluginManager(plugins_config)
        await manager.load_plugins()
        
        # Verify plugins are sorted by priority
        assert len(manager.auditing_plugins) == 1
        assert manager.auditing_plugins[0].priority == 80
    
    @pytest.mark.asyncio
    async def test_mixed_plugins_maintain_priority_order(self):
        """Test that both security and auditing plugins maintain priority order."""
        plugins_config = {
            "security": {
                "_global": [
                    {
                        "policy": "tool_allowlist", 
                        "enabled": True,
                        "config": {
                            "mode": "allow_all",
                            "priority": 30
                        }
                    },
                    {
                        "policy": "pii",
                        "enabled": True,
                        "config": {
                            "action": "audit_only",
                            "priority": 10,  # Higher priority than tool_allowlist
                            "pii_types": {
                                "email": {"enabled": True}
                            }
                        }
                    }
                ]
            },
            "auditing": {
                "_global": [
                    {
                        "policy": "json_auditing",
                        "enabled": True,
                        "config": {
                            "file": "/tmp/test.log",
                            "priority": 90,
                            "critical": False
                        }
                    }
                ]
            }
        }
        
        # Create plugin manager and load plugins
        manager = PluginManager(plugins_config)
        await manager.load_plugins()
        
        # Verify security plugins are correctly sorted
        assert len(manager.security_plugins) == 2
        security_priorities = [plugin.priority for plugin in manager.security_plugins]
        security_names = [plugin.__class__.__name__ for plugin in manager.security_plugins]
        
        assert security_priorities == [10, 30], f"Security priorities: {security_priorities}"
        assert security_names == ["BasicPIIFilterPlugin", "ToolAllowlistPlugin"]
        
        # Verify auditing plugins are loaded
        assert len(manager.auditing_plugins) == 1
        assert manager.auditing_plugins[0].priority == 90
    
    @pytest.mark.asyncio
    async def test_plugins_with_default_priority(self):
        """Test that plugins without explicit priority use default value of 50."""
        plugins_config = {
            "security": {
                "_global": [
                    {
                        "policy": "tool_allowlist", 
                        "enabled": True,
                        "config": {
                            "mode": "allow_all"
                            # No priority specified - should default to 50
                        }
                    },
                    {
                        "policy": "pii",
                        "enabled": True,
                        "config": {
                            "action": "audit_only",
                            "priority": 25,  # Explicit priority - should be first
                            "pii_types": {
                                "email": {"enabled": True}
                            }
                        }
                    }
                ]
            }
        }
        
        # Create plugin manager and load plugins
        manager = PluginManager(plugins_config)
        await manager.load_plugins()
        
        # Verify plugins are correctly sorted
        assert len(manager.security_plugins) == 2
        priorities = [plugin.priority for plugin in manager.security_plugins]
        plugin_names = [plugin.__class__.__name__ for plugin in manager.security_plugins]
        
        # PII filter (priority 25) should come before tool access control (default priority 50)
        assert priorities == [25, 50], f"Priorities: {priorities}"
        assert plugin_names == ["BasicPIIFilterPlugin", "ToolAllowlistPlugin"]
    
    @pytest.mark.asyncio
    async def test_same_priority_plugins_maintain_config_order(self):
        """Test that plugins with same priority maintain their configuration order."""
        plugins_config = {
            "security": {
                "_global": [
                    {
                        "policy": "tool_allowlist", 
                        "enabled": True,
                        "config": {
                            "mode": "allow_all",
                            "priority": 50
                        }
                    },
                    {
                        "policy": "pii",
                        "enabled": True,
                        "config": {
                            "action": "audit_only",
                            "priority": 50,  # Same priority
                            "pii_types": {
                                "email": {"enabled": True}
                            }
                        }
                    }
                ]
            }
        }
        
        # Create plugin manager and load plugins
        manager = PluginManager(plugins_config)
        await manager.load_plugins()
        
        # Verify plugins are loaded and have same priority
        assert len(manager.security_plugins) == 2
        priorities = [plugin.priority for plugin in manager.security_plugins]
        assert priorities == [50, 50]
        
        # For same priority, stable sort should maintain config order
        plugin_names = [plugin.__class__.__name__ for plugin in manager.security_plugins]
        # Note: Python's sort is stable, so original order should be preserved for equal elements
        assert plugin_names == ["ToolAllowlistPlugin", "BasicPIIFilterPlugin"]