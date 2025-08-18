"""Tests for plugin manager functionality."""

import pytest
import tempfile
from unittest.mock import MagicMock, patch
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, AuditingPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification

# Import mock classes from conftest
from conftest import MockSecurityPlugin, MockAuditingPlugin, FailingSecurityPlugin, FailingAuditingPlugin


class TestPluginManager:
    """Test PluginManager functionality."""
    
    def test_initialization(self):
        """Test PluginManager initialization."""
        config = {
            "security": {"_global": [{"name": "test", "enabled": True}]},
            "auditing": {"_global": [{"name": "test", "enabled": True}]}
        }
        
        manager = PluginManager(config)
        
        assert manager.plugins_config == config
        assert manager.security_plugins == []
        assert manager.auditing_plugins == []
        assert manager._initialized is False
    
    def test_initialization_with_empty_config(self):
        """Test PluginManager initialization with empty configuration."""
        manager = PluginManager({})
        
        assert manager.plugins_config == {}
        assert manager.security_plugins == []
        assert manager.auditing_plugins == []
        assert manager._initialized is False
    
    @pytest.mark.asyncio
    async def test_load_plugins_empty_config(self):
        """Test loading with empty plugin configuration."""
        manager = PluginManager({})
        
        await manager.load_plugins()
        
        assert manager._initialized is True
        assert len(manager.security_plugins) == 0
        assert len(manager.auditing_plugins) == 0
    
    @pytest.mark.asyncio
    async def test_load_plugins_missing_sections(self):
        """Test loading with missing security/auditing sections."""
        config = {"other_section": []}
        manager = PluginManager(config)
        
        await manager.load_plugins()
        
        assert manager._initialized is True
        assert len(manager.security_plugins) == 0
        assert len(manager.auditing_plugins) == 0
    
    @pytest.mark.asyncio
    async def test_load_plugins_disabled_plugins(self):
        """Test loading with disabled plugins."""
        config = {
            "security": {
                "_global": [
                    {"name": "test", "enabled": False, "config": {}}
                ]
            },
            "auditing": {
                "_global": [
                    {"name": "test", "enabled": False, "config": {}}
                ]
            }
        }
        manager = PluginManager(config)
        
        await manager.load_plugins()
        
        assert manager._initialized is True
        assert len(manager.security_plugins) == 0
        assert len(manager.auditing_plugins) == 0
    
    @pytest.mark.asyncio
    async def test_load_plugins_prevents_double_initialization(self):
        """Test that load_plugins prevents double initialization."""
        manager = PluginManager({})
        
        # First load
        await manager.load_plugins()
        assert manager._initialized is True
        
        # Second load should be skipped
        with patch('watchgate.plugins.manager.logger') as mock_logger:
            await manager.load_plugins()
            mock_logger.warning.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('watchgate.plugins.manager.PluginManager._discover_policies')
    async def test_load_plugins_with_valid_plugins(self, mock_discover_policies):
        """Test loading with valid plugin configuration."""
        # Mock the policy discovery for each category
        def mock_discover_side_effect(category):
            if category == "security":
                return {
                    "mock_security": MockSecurityPlugin
                }
            elif category == "auditing":
                return {
                    "mock_auditing": MockAuditingPlugin
                }
            return {}
            
        mock_discover_policies.side_effect = mock_discover_side_effect
        
        config = {
            "security": {
                "_global": [
                    {"policy": "mock_security", "enabled": True, "config": {"test": "value"}}
                ]
            },
            "auditing": {
                "_global": [
                    {"policy": "mock_auditing", "enabled": True, "config": {"test": "value"}}
                ]
            }
        }
        manager = PluginManager(config)
        
        await manager.load_plugins()
        
        assert manager._initialized is True
        assert len(manager.upstream_security_plugins.get("_global", [])) == 1
        assert len(manager.upstream_auditing_plugins.get("_global", [])) == 1
        assert isinstance(manager.upstream_security_plugins["_global"][0], MockSecurityPlugin)
        assert isinstance(manager.upstream_auditing_plugins["_global"][0], MockAuditingPlugin)
    
    @pytest.mark.asyncio
    async def test_process_request_no_plugins(self):
        """Test request processing with no plugins loaded."""
        manager = PluginManager({})
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        decision = await manager.process_request(request)
        
        assert decision.allowed is True
        assert "No security plugins configured" in decision.reason
        assert decision.metadata["plugin_count"] == 0
    
    @pytest.mark.asyncio
    async def test_process_request_with_allowing_plugin(self):
        """Test request processing with plugin that allows request."""
        manager = PluginManager({})
        # Manually add a mock plugin that allows requests
        manager.security_plugins = [MockSecurityPlugin({"allowed": True, "reason": "Request allowed"})]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        decision = await manager.process_request(request)
        
        assert decision.allowed is True
        assert decision.reason == "Allowed by all security plugins for upstream 'unknown'"
        assert decision.metadata["plugin_count"] == 1
    
    @pytest.mark.asyncio
    async def test_process_request_with_denying_plugin(self):
        """Test request processing with plugin that denies request."""
        manager = PluginManager({})
        # Manually add a mock plugin that denies requests
        manager.security_plugins = [MockSecurityPlugin({
            "allowed": False,
            "reason": "Test denial"
        })]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        decision = await manager.process_request(request)
        
        assert decision.allowed is False
        assert decision.reason == "Test denial"
        assert decision.metadata["plugin"] == "MockSecurityPlugin"
    
    @pytest.mark.asyncio
    async def test_process_request_multiple_plugins_first_denies(self):
        """Test request processing with multiple plugins where first denies."""
        manager = PluginManager({})
        # Add plugins where first denies, second would allow
        manager.security_plugins = [
            MockSecurityPlugin({"allowed": False, "reason": "First denial"}),
            MockSecurityPlugin({"allowed": True, "reason": "Second would allow"})
        ]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        decision = await manager.process_request(request)
        
        # Should stop at first denial
        assert decision.allowed is False
        assert decision.reason == "First denial"
    
    @pytest.mark.asyncio
    async def test_process_request_multiple_plugins_all_allow(self):
        """Test request processing with multiple plugins that all allow."""
        manager = PluginManager({})
        # Add multiple plugins that all allow
        manager.security_plugins = [
            MockSecurityPlugin({"allowed": True, "reason": "Request allowed"}),
            MockSecurityPlugin({"allowed": True, "reason": "Request allowed"})
        ]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        decision = await manager.process_request(request)
        
        assert decision.allowed is True
        assert decision.reason == "Allowed by all security plugins for upstream 'unknown'"
        assert decision.metadata["plugin_count"] == 2
    
    @pytest.mark.asyncio
    async def test_plugin_loading_failure_handling(self):
        """Test graceful handling of plugin loading failures.
        
        This test now verifies that missing policies raise ValueError immediately,
        which is the expected behavior for configuration errors.
        """
        config = {
            "security": {"_global": [
                {"policy": "nonexistent_plugin", "enabled": True, "config": {}}
            ]}
        }
        manager = PluginManager(config)
        
        # Should raise ValueError for missing policy (configuration error)
        with pytest.raises(ValueError) as exc_info:
            await manager.load_plugins()
        
        assert "nonexistent_plugin" in str(exc_info.value)
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_plugin_runtime_failure_handling(self):
        """Test graceful handling of plugin runtime failures."""
        manager = PluginManager({})
        # Add a plugin that always fails
        manager.security_plugins = [FailingSecurityPlugin({})]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        decision = await manager.process_request(request)
        
        # Should default to denial on plugin failure
        assert decision.allowed is False
        assert "failed" in decision.reason
        assert decision.metadata["plugin_failure"] is True
    
    @pytest.mark.asyncio
    async def test_log_request_no_plugins(self):
        """Test request logging with no auditing plugins."""
        manager = PluginManager({})
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        decision = PolicyDecision(allowed=True, reason="Test")
        
        # Should not raise exception
        await manager.log_request(request, decision)
    
    @pytest.mark.asyncio
    async def test_log_request_with_plugins(self):
        """Test request logging with auditing plugins."""
        manager = PluginManager({})
        
        # Add mock auditing plugin
        mock_plugin = MockAuditingPlugin({})
        manager.auditing_plugins = [mock_plugin]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        decision = PolicyDecision(allowed=True, reason="Test")
        
        await manager.log_request(request, decision)
        
        assert len(mock_plugin.logged_requests) == 1
        assert mock_plugin.logged_requests[0] == (request, decision)
    
    @pytest.mark.asyncio
    async def test_log_response_no_plugins(self):
        """Test response logging with no auditing plugins."""
        manager = PluginManager({})
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        response = MCPResponse(jsonrpc="2.0", id="test-1", result={"success": True})
        decision = PolicyDecision(allowed=True, reason="Response approved")
        
        # Should not raise exception
        await manager.log_response(request, response, decision)
    
    @pytest.mark.asyncio
    async def test_log_response_with_plugins(self):
        """Test response logging with auditing plugins."""
        manager = PluginManager({})
        
        # Add mock auditing plugin
        mock_plugin = MockAuditingPlugin({})
        manager.auditing_plugins = [mock_plugin]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        response = MCPResponse(jsonrpc="2.0", id="test-1", result={"success": True})
        decision = PolicyDecision(allowed=True, reason="Response approved")
        
        await manager.log_response(request, response, decision)
        
        assert len(mock_plugin.logged_responses) == 1
        assert mock_plugin.logged_responses[0] == (request, response, decision)
    
    @pytest.mark.asyncio
    async def test_auditing_plugin_failure_handling(self):
        """Test graceful handling of auditing plugin failures."""
        manager = PluginManager({})
        
        # Add failing auditing plugin
        manager.auditing_plugins = [FailingAuditingPlugin({})]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        decision = PolicyDecision(allowed=True, reason="Test")
        response = MCPResponse(jsonrpc="2.0", id="test-1", result={})
        notification = MCPNotification(jsonrpc="2.0", method="progress", params={"percent": 50})
        
        # Should not raise exceptions even when plugins fail
        await manager.log_request(request, decision)
        await manager.log_response(request, response, decision)
        await manager.log_notification(notification, decision)
    
    @pytest.mark.asyncio
    async def test_auto_initialization_on_process_request(self):
        """Test automatic initialization when processing request."""
        manager = PluginManager({})
        assert manager._initialized is False
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        
        # Should auto-initialize
        await manager.process_request(request)
        
        assert manager._initialized is True
    
    @pytest.mark.asyncio
    async def test_auto_initialization_on_log_request(self):
        """Test automatic initialization when logging request."""
        manager = PluginManager({})
        assert manager._initialized is False
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        decision = PolicyDecision(allowed=True, reason="Test")
        
        # Should auto-initialize
        await manager.log_request(request, decision)
        
        assert manager._initialized is True
    
    @pytest.mark.asyncio
    async def test_auto_initialization_on_log_response(self):
        """Test automatic initialization when logging response."""
        manager = PluginManager({})
        assert manager._initialized is False
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        response = MCPResponse(jsonrpc="2.0", id="test-1", result={})
        decision = PolicyDecision(allowed=True, reason="Response approved")
        
        # Should auto-initialize
        await manager.log_response(request, response, decision)
        
        assert manager._initialized is True



class TestPluginManagerErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_mixed_plugin_success_and_failure(self):
        """Test handling mix of successful and failing plugins."""
        manager = PluginManager({})
        
        # Mix of working and failing security plugins
        manager.security_plugins = [
            MockSecurityPlugin({"allowed": True}),
            FailingSecurityPlugin({})  # This will fail
        ]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        
        # Should get past first plugin but fail on second
        decision = await manager.process_request(request)
        
        assert decision.allowed is False
        assert "failed" in decision.reason
    
    @pytest.mark.asyncio
    async def test_complex_plugin_workflow(self):
        """Test complete workflow with multiple security and auditing plugins."""
        manager = PluginManager({})
        
        # Setup multiple plugins
        security_plugin = MockSecurityPlugin({"allowed": True})
        auditing_plugin = MockAuditingPlugin({})
        
        manager.security_plugins = [security_plugin]
        manager.auditing_plugins = [auditing_plugin]
        manager._initialized = True
        
        # Process request
        request = MCPRequest(jsonrpc="2.0", method="test", id="test-1")
        decision = await manager.process_request(request)
        
        # Log request
        await manager.log_request(request, decision)
        
        # Log response
        response = MCPResponse(jsonrpc="2.0", id="test-1", result={"success": True})
        response_decision = PolicyDecision(allowed=True, reason="Response approved")
        await manager.log_response(request, response, response_decision)
        
        # Verify complete workflow
        assert decision.allowed is True
        assert len(auditing_plugin.logged_requests) == 1
        assert len(auditing_plugin.logged_responses) == 1
        assert auditing_plugin.logged_requests[0] == (request, decision)
        assert auditing_plugin.logged_responses[0] == (request, response, response_decision)
    
    @pytest.mark.asyncio
    async def test_process_response_no_plugins(self):
        """Test response processing with no plugins loaded."""
        manager = PluginManager({})
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"success": True}
        )
        
        decision = await manager.process_response(request, response)
        
        assert decision.allowed is True
        assert decision.reason == "No security plugins configured for upstream 'unknown'"
        assert decision.metadata["plugin_count"] == 0
    
    @pytest.mark.asyncio
    async def test_process_response_with_allowing_plugin(self):
        """Test response processing with plugin that allows response."""
        manager = PluginManager({})
        # Manually add a mock plugin that allows responses
        manager.security_plugins = [MockSecurityPlugin({"allowed": True})]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"success": True}
        )
        
        decision = await manager.process_response(request, response)
        
        assert decision.allowed is True
        # The plugin manager returns "Response allowed by all security plugins" instead of the plugin's specific reason
        assert "Response allowed by all security plugins" in decision.reason
    
    @pytest.mark.asyncio
    async def test_process_response_with_denying_plugin(self):
        """Test response processing with plugin that denies response."""
        manager = PluginManager({})
        # Manually add a mock plugin that denies responses
        manager.security_plugins = [MockSecurityPlugin({"allowed": False, "reason": "Denied for test"})]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"success": True}
        )
        
        decision = await manager.process_response(request, response)
        
        assert decision.allowed is False
        assert "Response Denied for test" in decision.reason
    
    @pytest.mark.asyncio
    async def test_process_response_with_failing_plugin(self):
        """Test response processing with plugin that throws exception."""
        manager = PluginManager({})
        # Manually add a mock plugin that fails
        manager.security_plugins = [FailingSecurityPlugin({})]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"success": True}
        )
        
        decision = await manager.process_response(request, response)
        
        assert decision.allowed is False
        assert "failed on response" in decision.reason
        assert decision.metadata["plugin_failure"] is True
    
    @pytest.mark.asyncio
    async def test_process_notification_no_plugins(self):
        """Test notification processing with no plugins loaded."""
        manager = PluginManager({})
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        decision = await manager.process_notification(notification)
        
        assert decision.allowed is True
        assert decision.reason == "No security plugins configured for upstream 'unknown'"
        assert decision.metadata["plugin_count"] == 0
    
    @pytest.mark.asyncio
    async def test_process_notification_with_allowing_plugin(self):
        """Test notification processing with plugin that allows notification."""
        manager = PluginManager({})
        # Manually add a mock plugin that allows notifications
        manager.security_plugins = [MockSecurityPlugin({"allowed": True})]
        manager._initialized = True
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        decision = await manager.process_notification(notification)
        
        assert decision.allowed is True
        # The plugin manager returns "Notification allowed by all security plugins" instead of the plugin's specific reason
        assert "Notification allowed by all security plugins" in decision.reason
    
    @pytest.mark.asyncio
    async def test_process_notification_with_denying_plugin(self):
        """Test notification processing with plugin that denies notification."""
        manager = PluginManager({})
        # Manually add a mock plugin that denies notifications
        manager.security_plugins = [MockSecurityPlugin({"allowed": False, "reason": "Denied for test"})]
        manager._initialized = True
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        decision = await manager.process_notification(notification)
        
        assert decision.allowed is False
        assert "Notification Denied for test" in decision.reason
    
    @pytest.mark.asyncio
    async def test_process_notification_with_failing_plugin(self):
        """Test notification processing with plugin that throws exception."""
        manager = PluginManager({})
        # Manually add a mock plugin that fails
        manager.security_plugins = [FailingSecurityPlugin({})]
        manager._initialized = True
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        decision = await manager.process_notification(notification)
        
        assert decision.allowed is False
        assert "failed on notification" in decision.reason
        assert decision.metadata["plugin_failure"] is True
    
    @pytest.mark.asyncio
    async def test_log_response_invokes_plugins(self):
        """Test that log_response calls all auditing plugins."""
        manager = PluginManager({})
        
        # Create mock plugins
        mock1 = MockAuditingPlugin({})
        mock2 = MockAuditingPlugin({})
        manager.auditing_plugins = [mock1, mock2]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"success": True}
        )
        
        decision = PolicyDecision(allowed=True, reason="Response approved")
        
        await manager.log_response(request, response, decision)
        
        assert len(mock1.logged_responses) == 1
        assert len(mock2.logged_responses) == 1
        assert mock1.logged_responses[0] == (request, response, decision)
        assert mock2.logged_responses[0] == (request, response, decision)
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_log_response_handles_plugin_failure(self):
        """Test that log_response handles plugin failures gracefully."""
        manager = PluginManager({})
        
        # Create one good and one failing plugin
        mock = MockAuditingPlugin({})
        failing = FailingAuditingPlugin({})
        manager.auditing_plugins = [mock, failing]
        manager._initialized = True
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test",
            id="test-1"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"success": True}
        )
        
        decision = PolicyDecision(allowed=True, reason="Response approved")
        
        # Should not raise exception even though failing plugin fails
        with patch('watchgate.plugins.manager.logger') as mock_logger:
            await manager.log_response(request, response, decision)
            mock_logger.error.assert_called_once()
        
        # Good plugin should still have been called
        assert len(mock.logged_responses) == 1
    
    @pytest.mark.asyncio
    async def test_log_response_passes_policy_decision(self):
        """Test that log_response passes the PolicyDecision from response processing."""
        manager = PluginManager({})
        
        # Add mock plugins
        mock_audit = MockAuditingPlugin({})
        manager.auditing_plugins = [mock_audit]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="tools/call", id="test-1", params={"name": "read_file"})
        response = MCPResponse(jsonrpc="2.0", id="test-1", result={"content": "file data"})
        
        # Mock response decision (this would come from security plugin processing)
        response_decision = PolicyDecision(
            allowed=True, 
            reason="Response approved by security plugins",
            metadata={"plugin": "tool_allowlist", "filtered": False}
        )
        
        # This should pass the decision - currently will fail because interface doesn't support it
        await manager.log_response(request, response, response_decision)
        
        # Verify the auditing plugin received the decision
        assert len(mock_audit.logged_responses) == 1
        # The mock plugin should have received the actual decision, not a mock one
        logged_request, logged_response, logged_decision = mock_audit.logged_responses[0]
        assert logged_decision.allowed is True
        assert logged_decision.reason == "Response approved by security plugins"
        assert logged_decision.metadata["plugin"] == "tool_allowlist"
    
    @pytest.mark.asyncio
    async def test_log_notification_invokes_plugins(self):
        """Test that log_notification calls all auditing plugins."""
        manager = PluginManager({})
        
        # Create mock plugins
        mock1 = MockAuditingPlugin({})
        mock2 = MockAuditingPlugin({})
        manager.auditing_plugins = [mock1, mock2]
        manager._initialized = True
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        decision = PolicyDecision(allowed=True, reason="Notification allowed")
        await manager.log_notification(notification, decision)
        
        assert len(mock1.logged_notifications) == 1
        assert len(mock2.logged_notifications) == 1
        assert mock1.logged_notifications[0][0] == notification
        assert mock1.logged_notifications[0][1] == decision
        assert mock2.logged_notifications[0][0] == notification
        assert mock2.logged_notifications[0][1] == decision
    
    @pytest.mark.asyncio
    async def test_log_notification_handles_plugin_failure(self):
        """Test that log_notification handles plugin failures gracefully."""
        manager = PluginManager({})
        
        # Create one good and one failing plugin
        mock = MockAuditingPlugin({})
        failing = FailingAuditingPlugin({})
        manager.auditing_plugins = [mock, failing]
        manager._initialized = True
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        decision = PolicyDecision(allowed=True, reason="Notification allowed")
        
        # Should not raise exception even though failing plugin fails
        with patch('watchgate.plugins.manager.logger') as mock_logger:
            await manager.log_notification(notification, decision)
            mock_logger.error.assert_called_once()
        
        # Good plugin should still have been called
        assert len(mock.logged_notifications) == 1
