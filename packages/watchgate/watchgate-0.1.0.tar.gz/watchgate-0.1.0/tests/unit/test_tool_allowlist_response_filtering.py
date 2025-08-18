"""Tests for tool allowlist response filtering functionality.

This module tests the filtering of tools/list responses by the ToolAllowlistPlugin.
Following TDD principles - these are the RED phase tests that should fail initially.
"""

import pytest
from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse


class TestToolsListResponseFiltering:
    """Test filtering of tools/list responses by ToolAllowlistPlugin."""

    @pytest.fixture
    def allowlist_plugin(self):
        """Create plugin in allowlist mode."""
        config = {
            "mode": "allowlist",
            "tools": {"filesystem": ["read_file", "write_file", "create_directory"]}
        }
        return ToolAllowlistPlugin(config)

    @pytest.fixture
    def blocklist_plugin(self):
        """Create plugin in blocklist mode."""
        config = {
            "mode": "blocklist", 
            "tools": {"filesystem": ["dangerous_tool", "delete_everything"]}
        }
        return ToolAllowlistPlugin(config)

    @pytest.fixture
    def allow_all_plugin(self):
        """Create plugin in allow_all mode."""
        config = {"mode": "allow_all"}
        return ToolAllowlistPlugin(config)

    @pytest.fixture
    def tools_list_request(self):
        """Create a tools/list request."""
        return MCPRequest(
            jsonrpc="2.0",
            method="tools/list",
            id="test-tools-list-1",
            params={}
        )

    @pytest.fixture
    def tools_list_response_multiple_tools(self):
        """Create a tools/list response with multiple tools."""
        return MCPResponse(
            jsonrpc="2.0",
            id="test-tools-list-1",
            result={
                "tools": [
                    {"name": "read_file", "description": "Read a file"},
                    {"name": "write_file", "description": "Write a file"},
                    {"name": "dangerous_tool", "description": "Dangerous operation"},
                    {"name": "create_directory", "description": "Create directory"},
                    {"name": "delete_everything", "description": "Delete all files"}
                ]
            }
        )

    @pytest.mark.asyncio
    async def test_tools_list_response_filtering_allowlist_mode(self, allowlist_plugin, tools_list_request, tools_list_response_multiple_tools):
        """Test that tools/list response is filtered in allowlist mode."""
        decision = await allowlist_plugin.check_response(tools_list_request, tools_list_response_multiple_tools, server_name="filesystem")
        
        # Should allow the response but modify it
        assert decision.allowed is True
        assert decision.modified_content is not None
        
        # Check filtered tools
        filtered_tools = decision.modified_content.result["tools"]
        tool_names = [tool["name"] for tool in filtered_tools]
        
        # Should only contain allowed tools
        assert set(tool_names) == {"read_file", "write_file", "create_directory"}
        assert "dangerous_tool" not in tool_names
        assert "delete_everything" not in tool_names
        
        # Check metadata
        assert decision.metadata["original_count"] == 5
        assert decision.metadata["filtered_count"] == 3
        assert set(decision.metadata["filtered_tools"]) == {"dangerous_tool", "delete_everything"}
        assert set(decision.metadata["allowed_tools"]) == {"read_file", "write_file", "create_directory"}
        assert decision.metadata["mode"] == "allowlist"

    @pytest.mark.asyncio
    async def test_tools_list_response_filtering_blocklist_mode(self, blocklist_plugin, tools_list_request, tools_list_response_multiple_tools):
        """Test that tools/list response is filtered in blocklist mode."""
        decision = await blocklist_plugin.check_response(tools_list_request, tools_list_response_multiple_tools, server_name="filesystem")
        
        # Should allow the response but modify it
        assert decision.allowed is True
        assert decision.modified_content is not None
        
        # Check filtered tools
        filtered_tools = decision.modified_content.result["tools"]
        tool_names = [tool["name"] for tool in filtered_tools]
        
        # Should contain all tools except blocked ones
        assert set(tool_names) == {"read_file", "write_file", "create_directory"}
        assert "dangerous_tool" not in tool_names
        assert "delete_everything" not in tool_names
        
        # Check metadata
        assert decision.metadata["original_count"] == 5
        assert decision.metadata["filtered_count"] == 3
        assert set(decision.metadata["filtered_tools"]) == {"dangerous_tool", "delete_everything"}
        assert set(decision.metadata["allowed_tools"]) == {"read_file", "write_file", "create_directory"}
        assert decision.metadata["mode"] == "blocklist"

    @pytest.mark.asyncio
    async def test_tools_list_response_filtering_allow_all_mode(self, allow_all_plugin, tools_list_request, tools_list_response_multiple_tools):
        """Test that tools/list response is unchanged in allow_all mode."""
        decision = await allow_all_plugin.check_response(tools_list_request, tools_list_response_multiple_tools, server_name="filesystem")
        
        # Should allow without modification
        assert decision.allowed is True
        assert decision.modified_content is None
        
        # Check metadata indicates no filtering
        assert decision.metadata["mode"] == "allow_all"
        assert "original_count" not in decision.metadata

    @pytest.mark.asyncio
    async def test_non_tools_list_responses_unchanged(self, allowlist_plugin):
        """Test that non-tools/list responses are not filtered."""
        # Test tools/call response
        tools_call_request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file"}
        )
        
        tools_call_response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"content": "file content"}
        )
        
        decision = await allowlist_plugin.check_response(tools_call_request, tools_call_response, server_name="filesystem")
        assert decision.allowed is True
        assert decision.modified_content is None
        
        # Test resources/list response
        resources_list_request = MCPRequest(
            jsonrpc="2.0",
            method="resources/list",
            id="test-2",
            params={}
        )
        
        resources_list_response = MCPResponse(
            jsonrpc="2.0",
            id="test-2",
            result={"resources": [{"uri": "file://test.txt"}]}
        )
        
        decision = await allowlist_plugin.check_response(resources_list_request, resources_list_response, server_name="filesystem")
        assert decision.allowed is True
        assert decision.modified_content is None

    @pytest.mark.asyncio
    async def test_malformed_tools_list_response_handling(self, allowlist_plugin, tools_list_request):
        """Test handling of malformed tools/list responses."""
        # Missing tools field
        malformed_response_no_tools = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={}
        )
        
        decision = await allowlist_plugin.check_response(tools_list_request, malformed_response_no_tools, server_name="filesystem")
        assert decision.allowed is False
        assert "Malformed tools/list response" in decision.reason
        
        # Tools field that's not an array
        malformed_response_invalid_tools = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"tools": "not_an_array"}
        )
        
        decision = await allowlist_plugin.check_response(tools_list_request, malformed_response_invalid_tools, server_name="filesystem")
        assert decision.allowed is False
        assert "Malformed tools/list response" in decision.reason

    @pytest.mark.asyncio
    async def test_tool_objects_missing_name_field(self, allowlist_plugin, tools_list_request):
        """Test handling of tool objects missing name field."""
        response_with_invalid_tools = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={
                "tools": [
                    {"name": "read_file", "description": "Read a file"},
                    {"description": "Tool without name"},  # Missing name field
                    {"name": "write_file", "description": "Write a file"},
                    {"name": "", "description": "Tool with empty name"},  # Empty name
                ]
            }
        )
        
        decision = await allowlist_plugin.check_response(tools_list_request, response_with_invalid_tools, server_name="filesystem")
        assert decision.allowed is True
        assert decision.modified_content is not None
        
        # Should filter out tools with missing/invalid names
        filtered_tools = decision.modified_content.result["tools"]
        tool_names = [tool["name"] for tool in filtered_tools]
        
        # Should only contain valid tools with proper names
        assert set(tool_names) == {"read_file", "write_file"}
        
        # Check metadata reflects the filtering
        assert decision.metadata["original_count"] == 4
        assert decision.metadata["filtered_count"] == 2

    @pytest.mark.asyncio
    async def test_empty_tools_list_response(self, allowlist_plugin, tools_list_request):
        """Test handling of empty tools list."""
        empty_response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"tools": []}
        )
        
        decision = await allowlist_plugin.check_response(tools_list_request, empty_response, server_name="filesystem")
        assert decision.allowed is True
        assert decision.modified_content is None  # No modification needed for empty list
        
        # Check metadata
        assert decision.metadata["original_count"] == 0
        assert decision.metadata["filtered_count"] == 0

    @pytest.mark.asyncio
    async def test_all_tools_filtered_out(self, allowlist_plugin, tools_list_request):
        """Test when all tools are filtered out."""
        response_with_blocked_tools = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={
                "tools": [
                    {"name": "dangerous_tool", "description": "Dangerous operation"},
                    {"name": "another_blocked_tool", "description": "Also blocked"},
                ]
            }
        )
        
        decision = await allowlist_plugin.check_response(tools_list_request, response_with_blocked_tools, server_name="filesystem")
        assert decision.allowed is True
        assert decision.modified_content is not None
        
        # Should have empty tools list
        filtered_tools = decision.modified_content.result["tools"]
        assert len(filtered_tools) == 0
        
        # Check metadata
        assert decision.metadata["original_count"] == 2
        assert decision.metadata["filtered_count"] == 0
        assert set(decision.metadata["filtered_tools"]) == {"dangerous_tool", "another_blocked_tool"}
        assert decision.metadata["allowed_tools"] == []

    @pytest.mark.asyncio
    async def test_filtering_preserves_tool_attributes(self, allowlist_plugin, tools_list_request):
        """Test that filtering preserves all tool attributes except name."""
        response_with_rich_tools = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={
                "tools": [
                    {
                        "name": "read_file",
                        "description": "Read a file from disk",
                        "inputSchema": {"type": "object"},
                        "custom_field": "custom_value"
                    },
                    {
                        "name": "blocked_tool", 
                        "description": "This should be filtered out"
                    }
                ]
            }
        )
        
        decision = await allowlist_plugin.check_response(tools_list_request, response_with_rich_tools, server_name="filesystem")
        assert decision.allowed is True
        assert decision.modified_content is not None
        
        # Should preserve all attributes of allowed tools
        filtered_tools = decision.modified_content.result["tools"]
        assert len(filtered_tools) == 1
        
        allowed_tool = filtered_tools[0]
        assert allowed_tool["name"] == "read_file"
        assert allowed_tool["description"] == "Read a file from disk"
        assert allowed_tool["inputSchema"] == {"type": "object"}
        assert allowed_tool["custom_field"] == "custom_value"
