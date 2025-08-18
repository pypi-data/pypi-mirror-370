"""Tests for the ToolAllowlistPlugin security plugin."""

import pytest
import re
from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestToolAllowlistPluginConfiguration:
    """Test configuration validation for ToolAllowlistPlugin."""
    
    def test_valid_allow_all_config(self):
        """Test valid allow_all configuration."""
        config = {"mode": "allow_all"}
        plugin = ToolAllowlistPlugin(config)
        assert plugin.mode == "allow_all"
        assert plugin.tools_config == {}
    
    def test_valid_allowlist_config(self):
        """Test valid allowlist configuration."""
        config = {"mode": "allowlist", "tools": {"filesystem": ["read_file", "list_directory"]}}
        plugin = ToolAllowlistPlugin(config)
        assert plugin.mode == "allowlist"
        assert plugin.tools_config == {"filesystem": ["read_file", "list_directory"]}
    
    def test_valid_blocklist_config(self):
        """Test valid blocklist configuration."""
        config = {"mode": "blocklist", "tools": {"filesystem": ["dangerous_tool"]}}
        plugin = ToolAllowlistPlugin(config)
        assert plugin.mode == "blocklist"
        assert plugin.tools_config == {"filesystem": ["dangerous_tool"]}
    
    def test_invalid_config_not_dict(self):
        """Test configuration validation fails for non-dict."""
        with pytest.raises(ValueError, match="Configuration must be a dictionary"):
            ToolAllowlistPlugin("not_a_dict")
    
    def test_missing_mode(self):
        """Test configuration validation fails when mode is missing."""
        config = {"tools": {"filesystem": ["read_file"]}}
        with pytest.raises(ValueError, match="Configuration must include 'mode'"):
            ToolAllowlistPlugin(config)
    
    def test_invalid_mode(self):
        """Test configuration validation fails for invalid mode."""
        config = {"mode": "invalid_mode"}
        with pytest.raises(ValueError, match="Invalid mode 'invalid_mode'"):
            ToolAllowlistPlugin(config)
    
    def test_allowlist_mode_missing_tools(self):
        """Test allowlist mode fails without tools list."""
        config = {"mode": "allowlist"}
        with pytest.raises(ValueError, match="Configuration must include 'tools' for allowlist mode"):
            ToolAllowlistPlugin(config)
    
    def test_blocklist_mode_missing_tools(self):
        """Test blocklist mode fails without tools list."""
        config = {"mode": "blocklist"}
        with pytest.raises(ValueError, match="Configuration must include 'tools' for blocklist mode"):
            ToolAllowlistPlugin(config)
    
    def test_allowlist_mode_tools_not_dict(self):
        """Test allowlist mode fails when tools is not a dict."""
        config = {"mode": "allowlist", "tools": "not_a_dict"}
        with pytest.raises(ValueError, match="'tools' must be a dictionary mapping server names to tool lists"):
            ToolAllowlistPlugin(config)
    
    def test_allowlist_mode_empty_tools(self):
        """Test allowlist mode works with empty tools dict."""
        config = {"mode": "allowlist", "tools": {}}
        plugin = ToolAllowlistPlugin(config)
        assert plugin.mode == "allowlist"
        assert plugin.tools_config == {}
    
    def test_blocklist_mode_empty_tools(self):
        """Test blocklist mode works with empty tools dict."""
        config = {"mode": "blocklist", "tools": {}}
        plugin = ToolAllowlistPlugin(config)
        assert plugin.mode == "blocklist"
        assert plugin.tools_config == {}




class TestAllowAllMode:
    """Test allow_all mode behavior."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin in allow_all mode."""
        config = {"mode": "allow_all"}
        return ToolAllowlistPlugin(config)
    
    @pytest.mark.asyncio
    async def test_allows_any_tool(self, plugin):
        """Test allow_all mode permits any tool."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "any_tool", "arguments": {}}
        )
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert "Allow-all mode permits all tools" in decision.reason
    
    @pytest.mark.asyncio
    async def test_allows_non_tool_requests(self, plugin):
        """Test allow_all mode permits non-tool requests."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="resources/list",
            id="test-2",
            params={}
        )
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert "Non-tool request always allowed" in decision.reason


class TestAllowlistMode:
    """Test allowlist mode behavior."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin in allowlist mode."""
        config = {"mode": "allowlist", "tools": {"filesystem": ["read_file", "list_directory"]}}
        return ToolAllowlistPlugin(config)
    
    @pytest.mark.asyncio
    async def test_allows_listed_tool(self, plugin):
        """Test allowlist mode permits tools in the list."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-3",
            params={"name": "read_file", "arguments": {}}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is True
        assert "Tool 'read_file' is in allowlist for server 'filesystem'" in decision.reason
    
    @pytest.mark.asyncio
    async def test_denies_unlisted_tool(self, plugin):
        """Test allowlist mode denies tools not in the list."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-4",
            params={"name": "write_file", "arguments": {}}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is False
        assert "Tool 'write_file' is not in allowlist for server 'filesystem'" in decision.reason
    
    @pytest.mark.asyncio
    async def test_allows_non_tool_requests(self, plugin):
        """Test allowlist mode permits non-tool requests."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="resources/list",
            id="test-5",
            params={}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is True
        assert "Non-tool request always allowed" in decision.reason


class TestBlocklistMode:
    """Test blocklist mode behavior."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin in blocklist mode."""
        config = {"mode": "blocklist", "tools": {"filesystem": ["dangerous_tool", "risky_operation"]}}
        return ToolAllowlistPlugin(config)
    
    @pytest.mark.asyncio
    async def test_denies_blocked_tool(self, plugin):
        """Test blocklist mode denies tools in the block list."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-6",
            params={"name": "dangerous_tool", "arguments": {}}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is False
        assert "Tool 'dangerous_tool' is in blocklist for server 'filesystem'" in decision.reason
    
    @pytest.mark.asyncio
    async def test_allows_non_blocked_tool(self, plugin):
        """Test blocklist mode permits tools not in the block list."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-7",
            params={"name": "safe_tool", "arguments": {}}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is True
        assert "Tool 'safe_tool' is not in blocklist for server 'filesystem'" in decision.reason
    
    @pytest.mark.asyncio
    async def test_allows_non_tool_requests(self, plugin):
        """Test blocklist mode permits non-tool requests."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="resources/list",
            id="test-8",
            params={}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is True
        assert "Non-tool request always allowed" in decision.reason


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for testing."""
        config = {"mode": "allowlist", "tools": {"filesystem": ["test_tool"]}}
        return ToolAllowlistPlugin(config)
    
    @pytest.mark.asyncio
    async def test_missing_tool_name(self, plugin):
        """Test request without tool name is denied."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-9",
            params={}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is False
        assert "Tool call missing tool name" in decision.reason
    
    @pytest.mark.asyncio
    async def test_none_tool_name(self, plugin):
        """Test request with None tool name is denied."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-10",
            params={"name": None}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is False
        assert "Tool call missing tool name" in decision.reason
    
    @pytest.mark.asyncio
    async def test_empty_params(self, plugin):
        """Test request with empty params is denied."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-11",
            params=None
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        assert decision.allowed is False
        assert "Tool call missing tool name" in decision.reason


class TestPolicyDecisionFormat:
    """Test PolicyDecision return format."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for testing."""
        config = {"mode": "allowlist", "tools": {"filesystem": ["allowed_tool"]}}
        return ToolAllowlistPlugin(config)
    
    @pytest.mark.asyncio
    async def test_policy_decision_structure(self, plugin):
        """Test PolicyDecision has correct structure."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-12",
            params={"name": "allowed_tool", "arguments": {}}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        
        assert isinstance(decision, PolicyDecision)
        assert hasattr(decision, 'allowed')
        assert hasattr(decision, 'reason')
        assert hasattr(decision, 'metadata')
        assert isinstance(decision.allowed, bool)
        assert isinstance(decision.reason, str)
        assert isinstance(decision.metadata, dict)
    
    @pytest.mark.asyncio
    async def test_reason_is_descriptive(self, plugin):
        """Test PolicyDecision reason is descriptive."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-13",
            params={"name": "denied_tool", "arguments": {}}
        )
        decision = await plugin.check_request(request, server_name="filesystem")
        
        assert len(decision.reason) > 10  # Reasonable description length
        assert "denied_tool" in decision.reason  # Contains tool name


class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_tool_list_performance(self):
        """Test plugin handles large tool lists efficiently."""
        # Create large tool list
        large_tool_list = [f"tool_{i}" for i in range(1000)]
        config = {"mode": "allowlist", "tools": {"filesystem": large_tool_list}}
        
        # Should create plugin quickly
        plugin = ToolAllowlistPlugin(config)
        
        # Should store the tools config as-is
        assert plugin.tools_config == {"filesystem": large_tool_list}
        assert len(plugin.tools_config["filesystem"]) == 1000
        
        # Lookups should be efficient
        assert "tool_500" in plugin.tools_config["filesystem"]
        assert "tool_999" in plugin.tools_config["filesystem"]
        assert "nonexistent_tool" not in plugin.tools_config["filesystem"]


class TestResponseAndNotificationHandling:
    """Test handling of responses and notifications."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for testing."""
        config = {"mode": "allowlist", "tools": {"filesystem": ["allowed_tool"]}}
        return ToolAllowlistPlugin(config)
    
    @pytest.mark.asyncio
    async def test_check_response(self, plugin):
        """Test check_response method."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "allowed_tool", "arguments": {}}
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"value": "test result"}
        )
        
        # Tool access control plugin should allow non-tools/list responses
        decision = await plugin.check_response(request, response, server_name="filesystem")
        assert decision.allowed is True
        assert "Tool access control plugin doesn't restrict non-tools/list responses" in decision.reason
        assert decision.metadata["mode"] == plugin.mode
    
    @pytest.mark.asyncio
    async def test_check_notification(self, plugin):
        """Test check_notification method."""
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        # Tool access control plugin should always allow notifications
        decision = await plugin.check_notification(notification, server_name="filesystem")
        assert decision.allowed is True
        assert "Tool access control plugin doesn't restrict notifications" in decision.reason
        assert decision.metadata["mode"] == plugin.mode


# Test cases for server-specific tool access control
class TestServerSpecificToolControl:
    """Test server-specific tool access control."""
    
    def test_multiple_servers_allowlist(self):
        """Test plugin works with multiple servers in allowlist mode."""
        config = {
            "mode": "allowlist",
            "tools": {
                "filesystem": ["read_file", "write_file"],
                "fetch": ["fetch", "post"]
            }
        }
        plugin = ToolAllowlistPlugin(config)
        
        assert plugin.tools_config["filesystem"] == ["read_file", "write_file"]
        assert plugin.tools_config["fetch"] == ["fetch", "post"]
    
    @pytest.mark.asyncio
    async def test_server_specific_allowlist_control(self):
        """Test that tool access is controlled per server."""
        config = {
            "mode": "allowlist",
            "tools": {
                "filesystem": ["read_file"],
                "fetch": ["fetch"]
            }
        }
        plugin = ToolAllowlistPlugin(config)
        
        # Test allowed tool for filesystem server
        request1 = MCPRequest(
            jsonrpc="2.0", id="test1", method="tools/call",
            params={"name": "read_file", "arguments": {}}
        )
        decision1 = await plugin.check_request(request1, server_name="filesystem")
        assert decision1.allowed is True
        
        # Test disallowed tool for filesystem server
        request2 = MCPRequest(
            jsonrpc="2.0", id="test2", method="tools/call",
            params={"name": "fetch", "arguments": {}}
        )
        decision2 = await plugin.check_request(request2, server_name="filesystem")
        assert decision2.allowed is False
        
        # Test allowed tool for fetch server
        request3 = MCPRequest(
            jsonrpc="2.0", id="test3", method="tools/call",
            params={"name": "fetch", "arguments": {}}
        )
        decision3 = await plugin.check_request(request3, server_name="fetch")
        assert decision3.allowed is True
    
    @pytest.mark.asyncio
    async def test_unknown_server_denied(self):
        """Test that tools for unknown servers are denied."""
        config = {
            "mode": "allowlist",
            "tools": {
                "filesystem": ["read_file"]
            }
        }
        plugin = ToolAllowlistPlugin(config)
        
        # Test tool call for unknown server
        request = MCPRequest(
            jsonrpc="2.0", id="test", method="tools/call",
            params={"name": "read_file", "arguments": {}}
        )
        decision = await plugin.check_request(request, server_name="unknown_server")
        assert decision.allowed is False
        assert "unknown_server" in decision.reason