"""Integration tests for upstream-scoped plugin configuration.

This module tests the complete upstream-scoped plugin configuration functionality
with real PluginManager instances (no mocking of core plugin resolution).
Tests verify end-to-end behavior including plugin loading, request processing,
and audit logging with upstream context.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List

from watchgate.config import ConfigLoader
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, AuditingPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
from watchgate.plugins.auditing.json_lines import JsonAuditingPlugin

# Import mock classes from conftest for specific test scenarios
from conftest import MockSecurityPlugin, MockAuditingPlugin


class MockUpstreamScopedSecurityPlugin(SecurityPlugin):
    """Test security plugin that tracks upstream context."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.config = config
        self._plugin_id = f"test_security_{config.get('identifier', 'default')}"
        self.priority = config.get('priority', 50)
        self.blocked_methods = config.get('blocked_methods', [])
        self.upstream_requests = []  # Track requests by upstream
        
    @property
    def plugin_id(self) -> str:
        """Unique identifier for this plugin."""
        return self._plugin_id
        
    async def check_request(self, request: MCPRequest, server_name: Optional[str] = None) -> PolicyDecision:
        # Track which upstream this request came from
        self.upstream_requests.append({
            'upstream': server_name,
            'method': request.method,
            'request_id': request.id
        })
        
        if request.method in self.blocked_methods:
            return PolicyDecision(
                allowed=False,
                reason=f"Method {request.method} blocked by {self._plugin_id} for upstream {server_name}",
                metadata={'upstream': server_name, 'plugin': self._plugin_id}
            )
        
        return PolicyDecision(
            allowed=True,
            reason=f"Method {request.method} allowed by {self._plugin_id} for upstream {server_name}",
            metadata={'upstream': server_name, 'plugin': self._plugin_id}
        )
    
    async def check_response(self, request: MCPRequest, response: MCPResponse, server_name: Optional[str] = None) -> PolicyDecision:
        return PolicyDecision(
            allowed=True,
            reason=f"Response allowed by {self._plugin_id} for upstream {server_name}",
            metadata={'upstream': server_name, 'plugin': self._plugin_id}
        )
    
    async def check_notification(self, notification, server_name: Optional[str] = None) -> PolicyDecision:
        return PolicyDecision(
            allowed=True,
            reason=f"Notification allowed by {self._plugin_id} for upstream {server_name}",
            metadata={'upstream': server_name, 'plugin': self._plugin_id}
        )


class MockUpstreamScopedAuditingPlugin(AuditingPlugin):
    """Test auditing plugin that tracks upstream context."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.config = config
        self._plugin_id = f"test_audit_{config.get('identifier', 'default')}"
        self.priority = config.get('priority', 50)
        self.logged_requests = []
        self.logged_responses = []
        self.logged_notifications = []
        
    @property
    def plugin_id(self) -> str:
        """Unique identifier for this plugin."""
        return self._plugin_id
        
    async def log_request(self, request: MCPRequest, decision: PolicyDecision, server_name: Optional[str] = None) -> None:
        self.logged_requests.append({
            'upstream': server_name,
            'method': request.method,
            'request_id': request.id,
            'decision': decision,
            'plugin': self._plugin_id
        })
    
    async def log_response(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: Optional[str] = None) -> None:
        self.logged_responses.append({
            'upstream': server_name,
            'request_id': request.id,
            'response_id': response.id,
            'decision': decision,
            'plugin': self._plugin_id
        })
    
    async def log_notification(self, notification, decision: PolicyDecision, server_name: Optional[str] = None) -> None:
        self.logged_notifications.append({
            'upstream': server_name,
            'decision': decision,
            'plugin': self._plugin_id
        })


class TestUpstreamScopedPluginIntegration:
    """Integration tests for upstream-scoped plugin configuration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
    
    @pytest.mark.asyncio
    async def test_global_plus_specific_policies_integration(self):
        """Test upstream with both global and specific policies - verify both sets apply correctly."""
        # Mock the plugin discovery to use our test plugins
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "global_security": MockUpstreamScopedSecurityPlugin,
                "github_security": MockUpstreamScopedSecurityPlugin,
                "global_audit": MockUpstreamScopedAuditingPlugin,
                "github_audit": MockUpstreamScopedAuditingPlugin
            }
            
            # Configuration with global + upstream-specific policies
            plugins_config = {
                "security": {
                    "_global": [
                        {
                            "policy": "global_security",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "global",
                                "blocked_methods": ["dangerous_global"]
                            }
                        }
                    ],
                    "github": [
                        {
                            "policy": "github_security",
                            "enabled": True,
                            "priority": 20,
                            "config": {
                                "identifier": "github",
                                "blocked_methods": ["git_forbidden"]
                            }
                        }
                    ]
                },
                "auditing": {
                    "_global": [
                        {
                            "policy": "global_audit",
                            "enabled": True,
                            "priority": 10,
                            "config": {"identifier": "global"}
                        }
                    ],
                    "github": [
                        {
                            "policy": "github_audit",
                            "enabled": True,
                            "priority": 20,
                            "config": {"identifier": "github"}
                        }
                    ]
                }
            }
            
            # Initialize plugin manager and load plugins
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Verify plugins loaded for github upstream
            github_plugins = plugin_manager.get_plugins_for_upstream("github")
            assert len(github_plugins["security"]) == 2  # global + github-specific
            assert len(github_plugins["auditing"]) == 2  # global + github-specific
            
            # Test request processing for github upstream
            request = MCPRequest(
                jsonrpc="2.0",
                method="git_clone",
                id="test-1",
                params={"repo": "example/repo"}
            )
            
            # Process request through upstream-specific plugins
            decision = await plugin_manager.process_request(request, server_name="github")
            assert decision.allowed is True
            assert decision.metadata["upstream"] == "github"
            
            # Log request through upstream-specific audit plugins
            await plugin_manager.log_request(request, decision, server_name="github")
            
            # Verify both audit plugins logged the request
            github_security_plugins = github_plugins["security"]
            github_audit_plugins = github_plugins["auditing"]
            
            # Check that both audit plugins have logged the request
            global_audit_plugin = next(p for p in github_audit_plugins if p.plugin_id == "test_audit_global")
            github_audit_plugin = next(p for p in github_audit_plugins if p.plugin_id == "test_audit_github")
            
            assert len(global_audit_plugin.logged_requests) == 1
            assert len(github_audit_plugin.logged_requests) == 1
            assert global_audit_plugin.logged_requests[0]["upstream"] == "github"
            assert github_audit_plugin.logged_requests[0]["upstream"] == "github"
    
    @pytest.mark.asyncio
    async def test_specific_only_policies_integration(self):
        """Test upstream with only specific policies - ensure no accidental global inheritance."""
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "github_security": MockUpstreamScopedSecurityPlugin,
                "filesystem_security": MockUpstreamScopedSecurityPlugin,
                "filesystem_audit": MockUpstreamScopedAuditingPlugin
            }
            
            # Configuration with only upstream-specific policies (no _global)
            plugins_config = {
                "security": {
                    "github": [
                        {
                            "policy": "github_security",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "github",
                                "blocked_methods": ["git_push"]
                            }
                        }
                    ],
                    "filesystem": [
                        {
                            "policy": "filesystem_security",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "filesystem",
                                "blocked_methods": ["rm_rf"]
                            }
                        }
                    ]
                },
                "auditing": {
                    "filesystem": [
                        {
                            "policy": "filesystem_audit",
                            "enabled": True,
                            "priority": 10,
                            "config": {"identifier": "filesystem"}
                        }
                    ]
                }
            }
            
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Test github upstream - should only have github-specific plugins
            github_plugins = plugin_manager.get_plugins_for_upstream("github")
            assert len(github_plugins["security"]) == 1
            assert len(github_plugins["auditing"]) == 0  # No auditing for github
            
            github_security = github_plugins["security"][0]
            assert github_security.plugin_id == "test_security_github"
            
            # Test filesystem upstream - should only have filesystem-specific plugins
            filesystem_plugins = plugin_manager.get_plugins_for_upstream("filesystem")
            assert len(filesystem_plugins["security"]) == 1
            assert len(filesystem_plugins["auditing"]) == 1
            
            filesystem_security = filesystem_plugins["security"][0]
            filesystem_audit = filesystem_plugins["auditing"][0]
            assert filesystem_security.plugin_id == "test_security_filesystem"
            assert filesystem_audit.plugin_id == "test_audit_filesystem"
            
            # Test unknown upstream - should have no plugins
            unknown_plugins = plugin_manager.get_plugins_for_upstream("unknown")
            assert len(unknown_plugins["security"]) == 0
            assert len(unknown_plugins["auditing"]) == 0
            
            # Test request processing for each upstream
            github_request = MCPRequest(jsonrpc="2.0", method="git_status", id="github-1", params={})
            filesystem_request = MCPRequest(jsonrpc="2.0", method="read_file", id="fs-1", params={})
            
            github_decision = await plugin_manager.process_request(github_request, server_name="github")
            filesystem_decision = await plugin_manager.process_request(filesystem_request, server_name="filesystem")
            
            # Both should be allowed
            assert github_decision.allowed is True
            assert filesystem_decision.allowed is True
            assert github_decision.metadata["upstream"] == "github"
            assert filesystem_decision.metadata["upstream"] == "filesystem"
    
    @pytest.mark.asyncio
    async def test_global_fallback_integration(self):
        """Test upstream without specific config - confirm it uses global policies."""
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "global_security": MockUpstreamScopedSecurityPlugin,
                "global_audit": MockUpstreamScopedAuditingPlugin
            }
            
            # Configuration with only global policies
            plugins_config = {
                "security": {
                    "_global": [
                        {
                            "policy": "global_security",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "global",
                                "blocked_methods": ["dangerous_method"]
                            }
                        }
                    ]
                },
                "auditing": {
                    "_global": [
                        {
                            "policy": "global_audit",
                            "enabled": True,
                            "priority": 10,
                            "config": {"identifier": "global"}
                        }
                    ]
                }
            }
            
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Test multiple upstreams - all should get global plugins
            for upstream in ["github", "filesystem", "unknown_server"]:
                plugins = plugin_manager.get_plugins_for_upstream(upstream)
                assert len(plugins["security"]) == 1
                assert len(plugins["auditing"]) == 1
                
                security_plugin = plugins["security"][0]
                audit_plugin = plugins["auditing"][0]
                assert security_plugin.plugin_id == "test_security_global"
                assert audit_plugin.plugin_id == "test_audit_global"
                
                # Test request processing
                request = MCPRequest(
                    jsonrpc="2.0",
                    method="test_method",
                    id=f"{upstream}-1",
                    params={}
                )
                
                decision = await plugin_manager.process_request(request, server_name=upstream)
                assert decision.allowed is True
                assert decision.metadata["upstream"] == upstream
                
                # Test auditing
                await plugin_manager.log_request(request, decision, server_name=upstream)
                
                # Verify audit plugin captured the upstream context
                assert len(audit_plugin.logged_requests) >= 1
                latest_log = audit_plugin.logged_requests[-1]
                assert latest_log["upstream"] == upstream
    
    @pytest.mark.asyncio
    async def test_policy_override_integration(self):
        """Test upstream-specific policy overrides global policy with same name."""
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "rate_limiting": MockUpstreamScopedSecurityPlugin,
                "access_control": MockUpstreamScopedSecurityPlugin
            }
            
            # Configuration where github overrides global rate_limiting policy
            plugins_config = {
                "security": {
                    "_global": [
                        {
                            "policy": "rate_limiting",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "global_rate",
                                "blocked_methods": ["global_blocked"]
                            }
                        },
                        {
                            "policy": "access_control",
                            "enabled": True,
                            "priority": 20,
                            "config": {
                                "identifier": "global_access",
                                "blocked_methods": []
                            }
                        }
                    ],
                    "github": [
                        {
                            "policy": "rate_limiting",  # Same policy name - should override
                            "enabled": True,
                            "priority": 15,
                            "config": {
                                "identifier": "github_rate",
                                "blocked_methods": ["github_blocked"]
                            }
                        }
                    ]
                },
                "auditing": {}
            }
            
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Test github upstream - should have github rate_limiting + global access_control
            github_plugins = plugin_manager.get_plugins_for_upstream("github")
            assert len(github_plugins["security"]) == 2  # access_control + rate_limiting (overridden)
            
            # Verify the rate_limiting plugin is the github version, not global
            rate_limiting_plugin = next(
                p for p in github_plugins["security"] 
                if p.plugin_id == "test_security_github_rate"
            )
            access_control_plugin = next(
                p for p in github_plugins["security"] 
                if p.plugin_id == "test_security_global_access"
            )
            
            assert rate_limiting_plugin is not None
            assert access_control_plugin is not None
            assert "github_blocked" in rate_limiting_plugin.blocked_methods
            assert "global_blocked" not in rate_limiting_plugin.blocked_methods
            
            # Test request that triggers github-specific rate limiting
            request = MCPRequest(
                jsonrpc="2.0",
                method="github_blocked",
                id="override-1",
                params={}
            )
            
            decision = await plugin_manager.process_request(request, server_name="github")
            assert decision.allowed is False
            assert "github_blocked" in decision.reason
            assert decision.metadata["upstream"] == "github"
            
            # Test other upstream - should use global policies only
            other_plugins = plugin_manager.get_plugins_for_upstream("other")
            assert len(other_plugins["security"]) == 2  # Both global policies
            
            global_rate_plugin = next(
                p for p in other_plugins["security"] 
                if p.plugin_id == "test_security_global_rate"
            )
            assert global_rate_plugin is not None
            assert "global_blocked" in global_rate_plugin.blocked_methods
    
    @pytest.mark.asyncio
    async def test_audit_logs_contain_upstream_context(self):
        """Test that audit logs contain correct upstream context in real scenarios."""
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "context_audit": MockUpstreamScopedAuditingPlugin,
                "context_security": MockUpstreamScopedSecurityPlugin
            }
            
            plugins_config = {
                "security": {
                    "_global": [
                        {
                            "policy": "context_security",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "global",
                                "blocked_methods": []
                            }
                        }
                    ]
                },
                "auditing": {
                    "_global": [
                        {
                            "policy": "context_audit",
                            "enabled": True,
                            "priority": 10,
                            "config": {"identifier": "global"}
                        }
                    ],
                    "github": [
                        {
                            "policy": "context_audit",
                            "enabled": True,
                            "priority": 20,
                            "config": {"identifier": "github"}
                        }
                    ]
                }
            }
            
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Test requests to different upstreams
            test_cases = [
                ("github", "git_clone"),
                ("filesystem", "read_file"),
                ("database", "query")
            ]
            
            for upstream, method in test_cases:
                request = MCPRequest(
                    jsonrpc="2.0",
                    method=method,
                    id=f"context-{upstream}",
                    params={}
                )
                
                # Process request and response
                decision = await plugin_manager.process_request(request, server_name=upstream)
                
                response = MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={"status": "success"}
                )
                
                response_decision = PolicyDecision(
                    allowed=True,
                    reason="Response allowed",
                    metadata={"upstream": upstream}
                )
                
                # Log both request and response
                await plugin_manager.log_request(request, decision, server_name=upstream)
                await plugin_manager.log_response(request, response, response_decision, server_name=upstream)
                
                # Verify audit logs contain correct upstream context
                upstream_plugins = plugin_manager.get_plugins_for_upstream(upstream)
                audit_plugins = upstream_plugins["auditing"]
                
                for audit_plugin in audit_plugins:
                    # Check request logs
                    request_logs = [log for log in audit_plugin.logged_requests if log["request_id"] == request.id]
                    assert len(request_logs) == 1
                    assert request_logs[0]["upstream"] == upstream
                    assert request_logs[0]["method"] == method
                    
                    # Check response logs
                    response_logs = [log for log in audit_plugin.logged_responses if log["request_id"] == request.id]
                    assert len(response_logs) == 1
                    assert response_logs[0]["upstream"] == upstream
    
    @pytest.mark.asyncio
    async def test_mixed_real_and_mock_plugins_integration(self):
        """Test integration with a mix of real and mock plugins to validate realistic scenarios."""
        # Create a configuration that uses both real Watchgate plugins and our test plugins
        plugins_config = {
            "security": {
                "_global": [
                    {
                        "policy": "tool_allowlist",
                        "enabled": True,
                        "priority": 10,
                        "config": {
                            "mode": "allowlist",
                            "tools": {
                                "github": ["git_clone", "git_status"],
                                "filesystem": ["read_file", "write_file"]
                            }
                        }
                    }
                ],
                "github": [
                    {
                        "policy": "tool_allowlist",
                        "enabled": True,
                        "priority": 20,
                        "config": {
                            "mode": "blocklist",
                            "tools": {
                                "github": ["git_push"]  # Override global with more restrictive
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
                        "priority": 10,
                        "config": {
                            "output_file": "/tmp/test_audit.log",
                            "format": "json"
                        }
                    }
                ]
            }
        }
        
        plugin_manager = PluginManager(plugins_config)
        await plugin_manager.load_plugins()
        
        # Test github upstream - should have overridden tool access control
        github_plugins = plugin_manager.get_plugins_for_upstream("github")
        assert len(github_plugins["security"]) == 1  # Overridden global policy
        assert len(github_plugins["auditing"]) == 1  # Global auditing policy
        
        # Test allowed git operation
        allowed_request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="mixed-1",
            params={"name": "git_status", "arguments": {}}
        )
        
        decision = await plugin_manager.process_request(allowed_request, server_name="github")
        assert decision.allowed is True
        
        # Test blocked git operation (blocked by github-specific override)
        blocked_request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="mixed-2",
            params={"name": "git_push", "arguments": {}}
        )
        
        decision = await plugin_manager.process_request(blocked_request, server_name="github")
        assert decision.allowed is False
        assert "git_push" in decision.reason
        
        # Test filesystem upstream - should use global allowlist
        filesystem_request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="mixed-3",
            params={"name": "read_file", "arguments": {}}
        )
        
        decision = await plugin_manager.process_request(filesystem_request, server_name="filesystem")
        assert decision.allowed is True
        
        # Verify auditing works across all upstreams
        for request, upstream in [(allowed_request, "github"), (blocked_request, "github"), (filesystem_request, "filesystem")]:
            test_decision = PolicyDecision(allowed=True, reason="Test", metadata={"upstream": upstream})
            await plugin_manager.log_request(request, test_decision, server_name=upstream)
            
            upstream_plugins = plugin_manager.get_plugins_for_upstream(upstream)
            audit_plugins = upstream_plugins["auditing"]
            assert len(audit_plugins) == 1  # Should have global file auditing plugin
    
    @pytest.mark.asyncio
    async def test_upstream_scoped_response_processing_integration(self):
        """Test response processing uses correct upstream-scoped plugins in real scenarios."""
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "response_filter": MockUpstreamScopedSecurityPlugin,
                "response_audit": MockUpstreamScopedAuditingPlugin
            }
            
            plugins_config = {
                "security": {
                    "_global": [
                        {
                            "policy": "response_filter",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "global_response",
                                "blocked_methods": []
                            }
                        }
                    ],
                    "github": [
                        {
                            "policy": "response_filter",
                            "enabled": True,
                            "priority": 20,
                            "config": {
                                "identifier": "github_response",
                                "blocked_methods": []
                            }
                        }
                    ]
                },
                "auditing": {
                    "_global": [
                        {
                            "policy": "response_audit",
                            "enabled": True,
                            "priority": 10,
                            "config": {"identifier": "global"}
                        }
                    ],
                    "github": [
                        {
                            "policy": "response_audit",
                            "enabled": True,
                            "priority": 20,
                            "config": {"identifier": "github"}
                        }
                    ]
                }
            }
            
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Test response processing for github upstream
            request = MCPRequest(
                jsonrpc="2.0",
                method="git_clone",
                id="response-test-1",
                params={"repo": "example/repo"}
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                id="response-test-1",
                result={"success": True, "output": "Repository cloned successfully"}
            )
            
            # Process response through upstream-scoped plugins
            decision = await plugin_manager.process_response(request, response, server_name="github")
            assert decision.allowed is True
            assert decision.metadata["upstream"] == "github"
            assert decision.metadata["plugin_count"] == 1  # github-specific overrides global
            
            # Log response through upstream-scoped audit plugins
            await plugin_manager.log_response(request, response, decision, server_name="github")
            
            # Verify audit plugin logged the response (github overrides global)
            github_plugins = plugin_manager.get_plugins_for_upstream("github")
            github_audit_plugins = github_plugins["auditing"]
            
            # Only github audit plugin should be present (overrides global)
            assert len(github_audit_plugins) == 1
            github_audit_plugin = github_audit_plugins[0]
            assert github_audit_plugin.plugin_id == "test_audit_github"
            
            assert len(github_audit_plugin.logged_responses) == 1
            assert github_audit_plugin.logged_responses[0]["upstream"] == "github"
            
            # Test filesystem upstream - should only use global plugins
            filesystem_response = MCPResponse(
                jsonrpc="2.0",
                id="response-test-2",
                result={"content": "file data"}
            )
            
            filesystem_request = MCPRequest(
                jsonrpc="2.0",
                method="read_file",
                id="response-test-2",
                params={"path": "/example.txt"}
            )
            
            filesystem_decision = await plugin_manager.process_response(
                filesystem_request, filesystem_response, server_name="filesystem"
            )
            assert filesystem_decision.allowed is True
            assert filesystem_decision.metadata["upstream"] == "filesystem"
            assert filesystem_decision.metadata["plugin_count"] == 1  # only global
    
    @pytest.mark.asyncio
    async def test_upstream_scoped_notification_processing_integration(self):
        """Test notification processing uses correct upstream-scoped plugins in real scenarios."""
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "notification_filter": MockUpstreamScopedSecurityPlugin,
                "notification_audit": MockUpstreamScopedAuditingPlugin
            }
            
            plugins_config = {
                "security": {
                    "_global": [
                        {
                            "policy": "notification_filter",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "global_notification",
                                "blocked_methods": []
                            }
                        }
                    ],
                    "github": [
                        {
                            "policy": "notification_filter",
                            "enabled": True,
                            "priority": 20,
                            "config": {
                                "identifier": "github_notification",
                                "blocked_methods": []
                            }
                        }
                    ]
                },
                "auditing": {
                    "_global": [
                        {
                            "policy": "notification_audit",
                            "enabled": True,
                            "priority": 10,
                            "config": {"identifier": "global"}
                        }
                    ],
                    "github": [
                        {
                            "policy": "notification_audit",
                            "enabled": True,
                            "priority": 20,
                            "config": {"identifier": "github"}
                        }
                    ]
                }
            }
            
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Test notification processing for github upstream
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 50, "message": "Cloning repository..."}
            )
            
            # Process notification through upstream-scoped plugins
            decision = await plugin_manager.process_notification(notification, server_name="github")
            assert decision.allowed is True
            assert decision.metadata["upstream"] == "github"
            assert decision.metadata["plugin_count"] == 1  # github-specific overrides global
            
            # Log notification through upstream-scoped audit plugins
            await plugin_manager.log_notification(notification, decision, server_name="github")
            
            # Verify audit plugin logged the notification (github overrides global)
            github_plugins = plugin_manager.get_plugins_for_upstream("github")
            github_audit_plugins = github_plugins["auditing"]
            
            # Only github audit plugin should be present (overrides global)
            assert len(github_audit_plugins) == 1
            github_audit_plugin = github_audit_plugins[0]
            assert github_audit_plugin.plugin_id == "test_audit_github"
            
            assert len(github_audit_plugin.logged_notifications) == 1
            assert github_audit_plugin.logged_notifications[0]["upstream"] == "github"
            
            # Test filesystem upstream - should only use global plugins
            filesystem_notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 100, "message": "File operation complete"}
            )
            
            filesystem_decision = await plugin_manager.process_notification(
                filesystem_notification, server_name="filesystem"
            )
            assert filesystem_decision.allowed is True
            assert filesystem_decision.metadata["upstream"] == "filesystem"
            assert filesystem_decision.metadata["plugin_count"] == 1  # only global
    
    @pytest.mark.asyncio
    async def test_complete_upstream_scoped_flow_integration(self):
        """Test complete flow: request, response, and notification processing with upstream-scoped plugins."""
        from unittest.mock import patch
        
        with patch.object(PluginManager, '_discover_policies') as mock_discover:
            mock_discover.return_value = {
                "flow_security": MockUpstreamScopedSecurityPlugin,
                "flow_audit": MockUpstreamScopedAuditingPlugin
            }
            
            plugins_config = {
                "security": {
                    "_global": [
                        {
                            "policy": "flow_security",
                            "enabled": True,
                            "priority": 10,
                            "config": {
                                "identifier": "global_flow",
                                "blocked_methods": []
                            }
                        }
                    ],
                    "github": [
                        {
                            "policy": "flow_security",
                            "enabled": True,
                            "priority": 20,
                            "config": {
                                "identifier": "github_flow",
                                "blocked_methods": []
                            }
                        }
                    ]
                },
                "auditing": {
                    "_global": [
                        {
                            "policy": "flow_audit",
                            "enabled": True,
                            "priority": 10,
                            "config": {"identifier": "global"}
                        }
                    ],
                    "github": [
                        {
                            "policy": "flow_audit",
                            "enabled": True,
                            "priority": 20,
                            "config": {"identifier": "github"}
                        }
                    ]
                }
            }
            
            plugin_manager = PluginManager(plugins_config)
            await plugin_manager.load_plugins()
            
            # Simulate complete MCP flow for github upstream
            request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call",
                id="flow-test-1",
                params={"name": "git_clone", "arguments": {"repo": "example/repo"}}
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                id="flow-test-1",
                result={"success": True, "output": "Repository cloned"}
            )
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="progress",
                params={"progress": 100, "message": "Clone complete"}
            )
            
            # Process request
            request_decision = await plugin_manager.process_request(request, server_name="github")
            assert request_decision.allowed is True
            assert request_decision.metadata["upstream"] == "github"
            
            # Log request
            await plugin_manager.log_request(request, request_decision, server_name="github")
            
            # Process response
            response_decision = await plugin_manager.process_response(request, response, server_name="github")
            assert response_decision.allowed is True
            assert response_decision.metadata["upstream"] == "github"
            
            # Log response
            await plugin_manager.log_response(request, response, response_decision, server_name="github")
            
            # Process notification
            notification_decision = await plugin_manager.process_notification(notification, server_name="github")
            assert notification_decision.allowed is True
            assert notification_decision.metadata["upstream"] == "github"
            
            # Log notification
            await plugin_manager.log_notification(notification, notification_decision, server_name="github")
            
            # Verify plugin was used consistently
            github_plugins = plugin_manager.get_plugins_for_upstream("github")
            audit_plugins = github_plugins["auditing"]
            
            # Should have 1 audit plugin (github-specific overrides global)
            assert len(audit_plugins) == 1
            audit_plugin = audit_plugins[0]
            assert audit_plugin.plugin_id == "test_audit_github"
            
            # Plugin should have logged all three types of events
            assert len(audit_plugin.logged_requests) == 1
            assert len(audit_plugin.logged_responses) == 1
            assert len(audit_plugin.logged_notifications) == 1
            
            # All logs should have correct upstream context
            assert audit_plugin.logged_requests[0]["upstream"] == "github"
            assert audit_plugin.logged_responses[0]["upstream"] == "github"
            assert audit_plugin.logged_notifications[0]["upstream"] == "github"