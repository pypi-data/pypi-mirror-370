"""Unit tests for upstream-scoped plugin manager functionality (TDD - RED phase).

This test file contains failing tests that define the requirements for the new
upstream-scoped plugin resolution in the plugin manager.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, List

from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, AuditingPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class MockSecurityPlugin(SecurityPlugin):
    """Mock security plugin for testing."""
    
    def __init__(self, config: Dict[str, Any]):
        self._plugin_id = config.get('identifier', 'mock_security')
        self.priority = config.get('priority', 50)
        self.config = config
        
    @property
    def plugin_id(self) -> str:
        return self._plugin_id
        
    @plugin_id.setter
    def plugin_id(self, value: str):
        self._plugin_id = value
    
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        return PolicyDecision(allowed=True, reason=f"Mock plugin {self.plugin_id} allowed")
    
    async def check_response(self, request: MCPRequest, response, server_name: str) -> PolicyDecision:
        return PolicyDecision(allowed=True, reason=f"Mock plugin {self.plugin_id} allowed")
    
    async def check_notification(self, notification: MCPNotification, server_name: str) -> PolicyDecision:
        return PolicyDecision(allowed=True, reason=f"Mock plugin {self.plugin_id} allowed")


class MockAuditingPlugin(AuditingPlugin):
    """Mock auditing plugin for testing."""
    
    def __init__(self, config: Dict[str, Any]):
        self._plugin_id = config.get('identifier', 'mock_auditing')
        self.priority = config.get('priority', 50)
        self.config = config
        
    @property
    def plugin_id(self) -> str:
        return self._plugin_id
        
    @plugin_id.setter
    def plugin_id(self, value: str):
        self._plugin_id = value
    
    async def log_request(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> None:
        pass
    
    async def log_response(self, request: MCPRequest, response, decision: PolicyDecision, server_name: str) -> None:
        pass
    
    async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> None:
        pass


class TestUpstreamScopedPluginLoading:
    """Test upstream-scoped plugin loading and resolution.
    
    These tests define the new functionality for loading plugins based on
    upstream-scoped configuration with _global and upstream-specific sections.
    """
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_load_plugins_with_global_and_upstream_specific_config(self):
        """Test loading plugins with _global and upstream-specific configuration.
        
        This test should FAIL initially because the current PluginManager
        expects list-based configuration, not dictionary-based.
        """
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "tool_allowlist",
                        "enabled": True,
                        "priority": 10,
                        "config": {"mode": "allowlist", "tools": {}}
                    }
                ],
                "github": [
                    {
                        "policy": "secrets",
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ],
                "file-system": [
                    {
                        "policy": "filesystem_server", 
                        "enabled": True,
                        "priority": 30,
                        "config": {"allowed_paths": ["/safe"]}
                    }
                ]
            },
            "auditing": {
                "_global": [
                    {
                        "policy": "json_auditing",
                        "enabled": True,
                        "priority": 10,
                        "config": {"output_file": "/tmp/test.log"}
                    }
                ]
            }
        }
        
        # Should load plugins successfully with new dictionary format
        manager = PluginManager(config)
        # This will fail until we implement upstream-scoped loading
        await manager.load_plugins()
        
        # Should be able to get plugins for different upstreams
        assert hasattr(manager, 'get_plugins_for_upstream')
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_load_plugins_upstream_specific_only(self):
        """Test loading plugins with upstream-specific configuration only (no _global).
        
        This test should FAIL initially because the current PluginManager
        doesn't support upstream-only configuration.
        """
        config = {
            "security": {
                "github": [
                    {
                        "policy": "secrets",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    },
                    {
                        "policy": "tool_allowlist",
                        "enabled": True,
                        "priority": 20,
                        "config": {"mode": "allowlist", "tools": {}}
                    }
                ],
                "file-system": [
                    {
                        "policy": "filesystem_server",
                        "enabled": True,
                        "priority": 10,
                        "config": {"allowed_paths": ["/safe"]}
                    },
                    {
                        "policy": "pii",
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ]
            },
            "auditing": {
                "file-system": [
                    {
                        "policy": "json_auditing",
                        "enabled": True,
                        "priority": 10,
                        "config": {"output_file": "/tmp/test_file_access.log"}
                    }
                ]
            }
        }
        
        manager = PluginManager(config)
        await manager.load_plugins()
        
        # Should be able to get plugins for each upstream
        assert hasattr(manager, 'get_plugins_for_upstream')


class TestUpstreamPluginResolution:
    """Test plugin resolution for specific upstreams.
    
    These tests define the new plugin resolution functionality that applies
    the correct plugin set based on the target upstream.
    """
    
    @pytest.mark.asyncio
    async def test_get_plugins_for_upstream_with_global_fallback(self):
        """Test getting plugins for upstream with global fallback.
        
        This test should FAIL initially because get_plugins_for_upstream() doesn't exist.
        """
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "rate_limiting",
                        "enabled": True,
                        "priority": 10,
                        "config": {"max_requests": 100}
                    }
                ],
                "github": [
                    {
                        "policy": "git_token_validation",
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ]
            },
            "auditing": {
                "_global": [
                    {
                        "policy": "request_logging",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "rate_limiting": MockSecurityPlugin,
                "git_token_validation": MockSecurityPlugin,
                "request_logging": MockAuditingPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Test upstream with specific plugins + global
            plugins = manager.get_plugins_for_upstream("github")
            
            # Should have both global and github-specific plugins
            assert "security" in plugins
            assert "auditing" in plugins
            
            # Should have 2 security plugins (1 global + 1 github-specific)
            assert len(plugins["security"]) == 2
            
            # Should have 1 auditing plugin (1 global, no github-specific auditing)
            assert len(plugins["auditing"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_plugins_for_upstream_specific_only(self):
        """Test getting plugins for upstream with specific configuration only.
        
        This test should FAIL initially because get_plugins_for_upstream() doesn't exist.
        """
        config = {
            "security": {
                "github": [
                    {
                        "policy": "git_token_validation",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ],
                "file-system": [
                    {
                        "policy": "path_restrictions",
                        "enabled": True,
                        "priority": 10,
                        "config": {"allowed_paths": ["/safe"]}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "git_token_validation": MockSecurityPlugin,
                "path_restrictions": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Test github upstream
            github_plugins = manager.get_plugins_for_upstream("github")
            assert len(github_plugins["security"]) == 1
            assert len(github_plugins["auditing"]) == 0
            
            # Test file-system upstream
            fs_plugins = manager.get_plugins_for_upstream("file-system")
            assert len(fs_plugins["security"]) == 1
            assert len(fs_plugins["auditing"]) == 0
            
            # Test unknown upstream
            unknown_plugins = manager.get_plugins_for_upstream("unknown")
            assert len(unknown_plugins["security"]) == 0
            assert len(unknown_plugins["auditing"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_plugins_for_upstream_global_only(self):
        """Test getting plugins for upstream with global configuration only.
        
        This test should FAIL initially because get_plugins_for_upstream() doesn't exist.
        """
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "rate_limiting",
                        "enabled": True,
                        "priority": 10,
                        "config": {"max_requests": 100}
                    }
                ]
            },
            "auditing": {
                "_global": [
                    {
                        "policy": "request_logging",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "rate_limiting": MockSecurityPlugin,
                "request_logging": MockAuditingPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Any upstream should get global plugins
            for upstream in ["github", "file-system", "unknown"]:
                plugins = manager.get_plugins_for_upstream(upstream)
                assert len(plugins["security"]) == 1
                assert len(plugins["auditing"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_plugins_for_upstream_empty_config(self):
        """Test getting plugins for upstream with empty configuration.
        
        This test should FAIL initially because get_plugins_for_upstream() doesn't exist.
        """
        config = {
            "security": {},
            "auditing": {}
        }
        
        manager = PluginManager(config)
        await manager.load_plugins()
        
        # Should return empty plugin sets
        plugins = manager.get_plugins_for_upstream("github")
        assert len(plugins["security"]) == 0
        assert len(plugins["auditing"]) == 0


class TestPluginPolicyOverride:
    """Test policy override behavior in upstream-scoped configuration.
    
    These tests define how upstream-specific policies override global policies
    with the same name.
    """
    
    @pytest.mark.asyncio
    async def test_upstream_policy_overrides_global_policy(self):
        """Test that upstream-specific policies override global policies with same name.
        
        This test should FAIL initially because policy override logic doesn't exist.
        """
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "rate_limiting",
                        "enabled": True,
                        "priority": 10,
                        "config": {"max_requests": 100}
                    }
                ],
                "github": [
                    {
                        "policy": "rate_limiting",  # Same policy name, should override
                        "enabled": True,
                        "priority": 20,
                        "config": {"max_requests": 50}  # Different config
                    },
                    {
                        "policy": "git_token_validation",
                        "enabled": True,
                        "priority": 30,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "rate_limiting": MockSecurityPlugin,
                "git_token_validation": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            plugins = manager.get_plugins_for_upstream("github")
            
            # Should have 2 security plugins (global rate_limiting overridden by github rate_limiting + git_token_validation)
            assert len(plugins["security"]) == 2
            
            # Find the rate_limiting plugin and verify it uses github config
            rate_limiting_plugin = None
            for plugin in plugins["security"]:
                if getattr(plugin, 'policy', None) == "rate_limiting":
                    rate_limiting_plugin = plugin
                    break
            
            assert rate_limiting_plugin is not None
            # Should use github-specific config (max_requests: 50, not 100)
            assert rate_limiting_plugin.config["max_requests"] == 50
    
    @pytest.mark.asyncio
    async def test_no_override_when_different_policy_names(self):
        """Test that different policy names don't override each other.
        
        This test should FAIL initially because additive policy logic doesn't exist.
        """
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "rate_limiting",
                        "enabled": True,
                        "priority": 10,
                        "config": {"max_requests": 100}
                    }
                ],
                "github": [
                    {
                        "policy": "git_token_validation",  # Different policy name
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "rate_limiting": MockSecurityPlugin,
                "git_token_validation": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            plugins = manager.get_plugins_for_upstream("github")
            
            # Should have 2 security plugins (global rate_limiting + github git_token_validation)
            assert len(plugins["security"]) == 2
            
            # Should have both policies
            policy_names = [getattr(p, 'policy', None) for p in plugins["security"]]
            assert "rate_limiting" in policy_names
            assert "git_token_validation" in policy_names


class TestUpstreamScopedRequestProcessing:
    """Test request processing with upstream-scoped plugins.
    
    These tests define how the plugin manager should process requests
    using the appropriate plugin set for the target upstream.
    """
    
    @pytest.mark.asyncio
    async def test_process_request_with_upstream_specific_plugins(self):
        """Test request processing uses upstream-specific plugins.
        
        This test should FAIL initially because upstream-aware request processing doesn't exist.
        """
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "basic_security",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ],
                "github": [
                    {
                        "policy": "git_token_validation",
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ]
            }
        }
        
        # Mock the plugin loading
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "basic_security": MockSecurityPlugin,
                "git_token_validation": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            # Test request processing for github upstream
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "git_clone", "arguments": {}}
            )
            
            # Should use github-specific plugins (global + github-specific)
            decision = await manager.process_request(request, server_name="github")
            
            assert decision.allowed is True
            # Current implementation doesn't yet support upstream-scoped processing
            # So this will use all loaded plugins regardless of server_name
    
    @pytest.mark.asyncio
    async def test_process_request_with_global_plugins_only(self):
        """Test request processing uses global plugins when no upstream-specific config.
        
        This test should FAIL initially because upstream-aware request processing doesn't exist.
        """
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "basic_security",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "basic_security": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "read_file", "arguments": {}}
            )
            
            # Should use global plugins for any upstream
            decision = await manager.process_request(request, server_name="file-system")
            
            assert decision.allowed is True
            # Current implementation doesn't yet support upstream-scoped processing
    
    @pytest.mark.asyncio
    async def test_process_request_no_plugins_for_upstream(self):
        """Test request processing when no plugins configured for upstream.
        
        This test should FAIL initially because upstream-aware request processing doesn't exist.
        """
        config = {
            "security": {
                "github": [
                    {
                        "policy": "git_token_validation",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "git_token_validation": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "read_file", "arguments": {}}
            )
            
            # Should allow by default when no plugins for upstream
            decision = await manager.process_request(request, server_name="file-system")
            
            assert decision.allowed is True
            # Current implementation doesn't yet support upstream-scoped processing
            # So this will use all loaded plugins regardless of server_name


class TestUpstreamScopedAuditLogging:
    """Test audit logging with upstream-scoped plugins.
    
    These tests define how audit logging should work with upstream-scoped configuration.
    """
    
    @pytest.mark.asyncio
    async def test_audit_request_with_upstream_specific_plugins(self):
        """Test audit logging uses upstream-specific plugins.
        
        This test should FAIL initially because upstream-aware audit logging doesn't exist.
        """
        config = {
            "auditing": {
                "_global": [
                    {
                        "policy": "request_logging",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ],
                "github": [
                    {
                        "policy": "git_operation_audit",
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "request_logging": MockAuditingPlugin,
                "git_operation_audit": MockAuditingPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "git_clone", "arguments": {}}
            )
            
            decision = PolicyDecision(allowed=True, reason="Test decision")
            
            # Should use github-specific audit plugins
            await manager.audit_request(request, decision, "github")
            
            # Test should verify that both global and github-specific audit plugins were called
            # (Implementation details to be determined during GREEN phase)
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_audit_request_captures_upstream_context(self):
        """Test that audit logging captures upstream context.
        
        This test should FAIL initially because upstream context capture doesn't exist.
        """
        config = {
            "auditing": {
                "_global": [
                    {
                        "policy": "request_logging",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        # Mock audit plugin that captures logs
        audit_logs = []
        
        class TestAuditingPlugin(AuditingPlugin):
            def __init__(self, config: Dict[str, Any]):
                self._plugin_id = config.get('identifier', 'test_audit')
                self.priority = config.get('priority', 10)
                self.config = config
                
            @property
            def plugin_id(self) -> str:
                return self._plugin_id
                
            @plugin_id.setter
            def plugin_id(self, value: str):
                self._plugin_id = value
            
            async def log_request(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> None:
                audit_logs.append({
                    "request": request,
                    "decision": decision,
                    "upstream": getattr(decision, 'upstream', None)
                })
            
            async def log_response(self, request: MCPRequest, response, decision: PolicyDecision, server_name: str) -> None:
                pass
            
            async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> None:
                pass
        
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "request_logging": TestAuditingPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "read_file", "arguments": {}}
            )
            
            decision = PolicyDecision(allowed=True, reason="Test decision")
            
            await manager.audit_request(request, decision, "test-server")
            
            # Should have captured upstream context in audit log
            assert len(audit_logs) == 1
            # In current implementation, upstream is None since it's not passed yet
            assert audit_logs[0]["upstream"] is None


class TestBackwardCompatibility:
    """Test backward compatibility handling during transition.
    
    These tests define how the plugin manager should handle the transition
    from old list-based to new dictionary-based configuration.
    """
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_old_list_format_should_fail_gracefully(self):
        """Test that old list format configurations fail with clear error.
        
        This test should PASS initially and continue to pass because we're
        making a breaking change for v0.1.0.
        """
        # Old list-based format
        old_config = {
            "security": [
                {
                    "policy": "rate_limiting",
                    "enabled": True,
                    "config": {}
                }
            ],
            "auditing": [
                {
                    "policy": "request_logging",
                    "enabled": True,
                    "config": {}
                }
            ]
        }
        
        # Breaking change implemented - should fail with AttributeError
        with patch('watchgate.plugins.manager.PluginManager._discover_policies') as mock_discover:
            mock_discover.return_value = {
                "rate_limiting": MockSecurityPlugin,
                "request_logging": MockAuditingPlugin
            }
            
            manager = PluginManager(old_config)
            
            # Should fail because list format is no longer supported
            with pytest.raises(AttributeError) as exc_info:
                await manager.load_plugins()
            
            # Should get clear error about 'list' object not having 'items' method
            assert "'list' object has no attribute 'items'" in str(exc_info.value)


class TestUpstreamScopedResponseProcessing:
    """Test response processing with upstream-scoped plugins.
    
    These tests define how the plugin manager should process responses
    using the appropriate plugin set for the source upstream.
    """
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_process_response_with_upstream_specific_plugins(self):
        """Test response processing uses upstream-specific plugins."""
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "basic_security",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ],
                "github": [
                    {
                        "policy": "git_response_filter",
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "basic_security": MockSecurityPlugin,
                "git_response_filter": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "git_clone", "arguments": {}}
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                id="test",
                result={"success": True}
            )
            
            # Should use github-specific plugins (global + github-specific)
            decision = await manager.process_response(request, response, server_name="github")
            
            assert decision.allowed is True
            # Should have metadata indicating which plugins were used
            assert "upstream" in decision.metadata
            assert decision.metadata["upstream"] == "github"
            assert decision.metadata["plugin_count"] == 2  # global + github-specific
    
    @pytest.mark.asyncio
    async def test_process_response_with_global_plugins_only(self):
        """Test response processing uses global plugins when no upstream-specific config."""
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "basic_security",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "basic_security": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "read_file", "arguments": {}}
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                id="test",
                result={"content": "file data"}
            )
            
            # Should use global plugins for any upstream
            decision = await manager.process_response(request, response, server_name="file-system")
            
            assert decision.allowed is True
            assert decision.metadata["upstream"] == "file-system"
            assert decision.metadata["plugin_count"] == 1
    
    @pytest.mark.asyncio
    async def test_process_response_no_plugins_for_upstream(self):
        """Test response processing when no plugins configured for upstream."""
        config = {
            "security": {
                "github": [
                    {
                        "policy": "git_response_filter",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "git_response_filter": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test",
                method="tools/call",
                params={"name": "read_file", "arguments": {}}
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                id="test",
                result={"content": "file data"}
            )
            
            # Should allow by default when no plugins for upstream
            decision = await manager.process_response(request, response, server_name="file-system")
            
            assert decision.allowed is True
            assert "no security plugins" in decision.reason.lower()
            assert decision.metadata["upstream"] == "file-system"
            assert decision.metadata["plugin_count"] == 0


class TestUpstreamScopedNotificationProcessing:
    """Test notification processing with upstream-scoped plugins.
    
    These tests define how the plugin manager should process notifications
    using the appropriate plugin set for the source upstream.
    """
    
    @pytest.mark.asyncio
    async def test_process_notification_with_upstream_specific_plugins(self):
        """Test notification processing uses upstream-specific plugins."""
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "basic_security",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ],
                "github": [
                    {
                        "policy": "git_notification_filter",
                        "enabled": True,
                        "priority": 20,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "basic_security": MockSecurityPlugin,
                "git_notification_filter": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 50, "message": "Cloning repository..."}
            )
            
            # Should use github-specific plugins (global + github-specific)
            decision = await manager.process_notification(notification, server_name="github")
            
            assert decision.allowed is True
            # Should have metadata indicating which plugins were used
            assert "upstream" in decision.metadata
            assert decision.metadata["upstream"] == "github"
            assert decision.metadata["plugin_count"] == 2  # global + github-specific
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_process_notification_with_global_plugins_only(self):
        """Test notification processing uses global plugins when no upstream-specific config."""
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "basic_security",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "basic_security": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 75, "message": "Reading file..."}
            )
            
            # Should use global plugins for any upstream
            decision = await manager.process_notification(notification, server_name="file-system")
            
            assert decision.allowed is True
            assert decision.metadata["upstream"] == "file-system"
            assert decision.metadata["plugin_count"] == 1
    
    @pytest.mark.asyncio
    async def test_process_notification_no_plugins_for_upstream(self):
        """Test notification processing when no plugins configured for upstream."""
        config = {
            "security": {
                "github": [
                    {
                        "policy": "git_notification_filter",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "git_notification_filter": MockSecurityPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 100, "message": "Operation complete"}
            )
            
            # Should allow by default when no plugins for upstream
            decision = await manager.process_notification(notification, server_name="file-system")
            
            assert decision.allowed is True
            assert "no security plugins" in decision.reason.lower()
            assert decision.metadata["upstream"] == "file-system"
            assert decision.metadata["plugin_count"] == 0


class TestUpstreamScopedNotificationLogging:
    """Test notification logging with upstream-scoped plugins.
    
    These tests define how notification logging should work with upstream-scoped configuration.
    """
    
    @pytest.mark.asyncio
    async def test_log_notification_with_upstream_specific_plugins(self):
        """Test notification logging uses upstream-specific plugins."""
        # Track which plugins were called
        called_plugins = []
        
        class TestAuditingPlugin(AuditingPlugin):
            def __init__(self, config: Dict[str, Any]):
                self._plugin_id = config.get('identifier', 'test_audit')
                self.priority = config.get('priority', 50)
                self.config = config
                
            @property
            def plugin_id(self) -> str:
                return self._plugin_id
                
            @plugin_id.setter
            def plugin_id(self, value: str):
                self._plugin_id = value
            
            async def log_request(self, request: MCPRequest, decision: PolicyDecision, **kwargs) -> None:
                pass
            
            async def log_response(self, request: MCPRequest, response, decision: PolicyDecision, **kwargs) -> None:
                pass
            
            async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, **kwargs) -> None:
                called_plugins.append(self.plugin_id)
        
        config = {
            "auditing": {
                "_global": [
                    {
                        "policy": "request_logging",
                        "enabled": True,
                        "priority": 10,
                        "config": {"identifier": "request_logging"}
                    }
                ],
                "github": [
                    {
                        "policy": "git_notification_audit",
                        "enabled": True,
                        "priority": 20,
                        "config": {"identifier": "git_notification_audit"}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "request_logging": TestAuditingPlugin,
                "git_notification_audit": TestAuditingPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 50, "message": "Cloning repository..."}
            )
            
            decision = PolicyDecision(allowed=True, reason="Test decision")
            
            # Should use github-specific audit plugins
            await manager.log_notification(notification, decision, server_name="github")
            
            # Should have called both global and github-specific plugins
            assert len(called_plugins) == 2
            assert "request_logging" in called_plugins
            assert "git_notification_audit" in called_plugins
    
    @pytest.mark.asyncio
    async def test_log_notification_captures_upstream_context(self):
        """Test that notification logging captures upstream context."""
        # Track decision metadata
        captured_decisions = []
        
        class TestAuditingPlugin(AuditingPlugin):
            def __init__(self, config: Dict[str, Any]):
                self._plugin_id = config.get('identifier', 'test_audit')
                self.priority = config.get('priority', 10)
                self.config = config
                
            @property
            def plugin_id(self) -> str:
                return self._plugin_id
                
            @plugin_id.setter
            def plugin_id(self, value: str):
                self._plugin_id = value
            
            async def log_request(self, request: MCPRequest, decision: PolicyDecision, **kwargs) -> None:
                pass
            
            async def log_response(self, request: MCPRequest, response, decision: PolicyDecision, **kwargs) -> None:
                pass
            
            async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, **kwargs) -> None:
                captured_decisions.append(decision)
        
        config = {
            "auditing": {
                "_global": [
                    {
                        "policy": "request_logging",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "request_logging": TestAuditingPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 100, "message": "File operation complete"}
            )
            
            decision = PolicyDecision(allowed=True, reason="Test decision")
            
            await manager.log_notification(notification, decision, server_name="file-system")
            
            # Should have captured upstream context in decision metadata
            assert len(captured_decisions) == 1
            assert captured_decisions[0].metadata is not None
            assert captured_decisions[0].metadata["upstream"] == "file-system"
    
    @pytest.mark.asyncio
    async def test_log_notification_no_plugins_for_upstream(self):
        """Test notification logging when no plugins configured for upstream."""
        config = {
            "auditing": {
                "github": [
                    {
                        "policy": "git_notification_audit",
                        "enabled": True,
                        "priority": 10,
                        "config": {}
                    }
                ]
            }
        }
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "git_notification_audit": MockAuditingPlugin
            }
            
            manager = PluginManager(config)
            await manager.load_plugins()
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 100, "message": "Operation complete"}
            )
            
            decision = PolicyDecision(allowed=True, reason="Test decision")
            
            # Should not crash when no plugins for upstream
            await manager.log_notification(notification, decision, server_name="file-system")
            
            # Should complete without error (no plugins to call)