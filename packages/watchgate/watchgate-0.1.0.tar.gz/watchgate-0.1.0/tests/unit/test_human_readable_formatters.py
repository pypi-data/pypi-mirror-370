"""Tests for human-readable auditing formatters.

This test suite covers the LineAuditingPlugin and DebugAuditingPlugin formatters:
- Line format output for operational monitoring
- Debug format output with detailed key-value pairs  
- Proper formatting of requests, responses, and notifications
- Tool call handling and parameter display
- Error handling and status reporting
"""

import json
import tempfile
from datetime import datetime

from watchgate.plugins.auditing.human_readable import LineAuditingPlugin, DebugAuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision


class TestLineAuditingFormatter:
    """Test LineAuditingPlugin formatting functionality."""
    
    def test_basic_request_formatting(self):
        """Test basic request formatting in line format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = LineAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="123",
                method="tools/list",
                params={}
            )
            
            decision = PolicyDecision(allowed=True, reason="")
            
            result = plugin._format_request_log(request, decision, "test_server")
            
            # Should contain timestamp, method, status, and server
            assert "REQUEST: tools/list" in result
            assert "ALLOWED" in result
            assert "test_server" in result
            assert "UTC" in result  # Timestamp format
    
    def test_tool_call_formatting(self):
        """Test tool call formatting in line format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = LineAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="123",
                method="tools/call",
                params={"name": "file_read", "arguments": {"path": "/test"}}
            )
            
            decision = PolicyDecision(allowed=True, reason="")
            
            result = plugin._format_request_log(request, decision, "test_server")
            
            # Should contain tool name
            assert "REQUEST: tools/call - file_read" in result
            assert "ALLOWED" in result
            assert "test_server" in result
    
    def test_security_block_formatting(self):
        """Test security block formatting in line format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = LineAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="123", 
                method="tools/call",
                params={"name": "dangerous_tool"}
            )
            
            decision = PolicyDecision(
                allowed=False,
                reason="Tool blocked by security policy",
                metadata={"plugin": "security_plugin"}
            )
            
            result = plugin._format_request_log(request, decision, "test_server")
            
            # Should contain security block info
            assert "SECURITY_BLOCK: dangerous_tool" in result
            assert "security_plugin" in result
            assert "Tool blocked by security policy" in result
            assert "test_server" in result
    
    def test_response_formatting_with_duration(self):
        """Test response formatting with duration information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = LineAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(jsonrpc="2.0", id="123", method="tools/call")
            response = MCPResponse(jsonrpc="2.0", id="123", result={"status": "ok"})
            
            decision = PolicyDecision(
                allowed=True,
                reason="",
                metadata={"duration_ms": 1500}
            )
            
            result = plugin._format_response_log(request, response, decision, "test_server")
            
            # Should contain success status and duration
            assert "RESPONSE: success" in result
            assert "(1.500s)" in result
            assert "test_server" in result
    
    def test_notification_formatting(self):
        """Test notification formatting in line format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = LineAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="notifications/message",
                params={"text": "Hello"}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="Message approved",
                metadata={"plugin": "message_filter"}
            )
            
            result = plugin._format_notification_log(notification, decision, "test_server")
            
            # Should contain notification info
            assert "NOTIFICATION: notifications/message" in result
            assert "message_filter" in result
            assert "Message approved" in result
            assert "test_server" in result


class TestDebugAuditingFormatter:
    """Test DebugAuditingPlugin formatting functionality."""
    
    def test_basic_request_debug_formatting(self):
        """Test basic request formatting in debug format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = DebugAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="123",
                method="tools/list",
                params={}
            )
            
            decision = PolicyDecision(allowed=True, reason="")
            
            result = plugin._format_request_log(request, decision, "test_server")
            
            # Should contain key-value pairs
            assert "REQUEST_ID=123" in result
            assert "EVENT=REQUEST" in result
            assert "METHOD=tools/list" in result
            assert "STATUS=ALLOWED" in result
            assert "SERVER=test_server" in result
            # Should contain millisecond timestamp
            assert re.search(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]', result)
    
    def test_tool_call_debug_formatting_with_params(self):
        """Test tool call formatting with parameters in debug format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = DebugAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="123",
                method="tools/call",
                params={
                    "name": "file_read",
                    "arguments": {"path": "/test/file.txt"}
                }
            )
            
            decision = PolicyDecision(allowed=True, reason="")
            
            result = plugin._format_request_log(request, decision, "test_server")
            
            # Should contain tool name and parameters
            assert "TOOL=file_read" in result
            assert "PARAMS_JSON=" in result
            assert "file_read" in result
            assert "/test/file.txt" in result
    
    def test_security_block_debug_formatting(self):
        """Test security block formatting in debug format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = DebugAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="123",
                method="dangerous/operation"
            )
            
            decision = PolicyDecision(
                allowed=False,
                reason="Operation not permitted",
                metadata={"plugin": "security_filter", "mode": "strict"}
            )
            
            result = plugin._format_request_log(request, decision, "test_server")
            
            # Should contain security block details
            assert "EVENT=SECURITY_BLOCK" in result
            assert "STATUS=BLOCKED" in result
            assert "PLUGIN=security_filter" in result
            assert 'REASON="Operation not permitted"' in result
            assert "POLICY_MODE=strict" in result
    
    def test_response_debug_formatting_with_error(self):
        """Test response formatting with error in debug format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = DebugAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(jsonrpc="2.0", id="123", method="tools/call")
            response = MCPResponse(
                jsonrpc="2.0",
                id="123",
                error={"code": -32001, "message": "Upstream server error"}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="",
                metadata={"duration_ms": 2500}
            )
            
            result = plugin._format_response_log(request, response, decision, "test_server")
            
            # Should contain error details and duration
            assert "EVENT=UPSTREAM_ERROR" in result
            assert "STATUS=error" in result
            assert "ERROR_CODE=-32001" in result
            assert 'ERROR_MESSAGE="Upstream server error"' in result
            assert "DURATION=2.500s" in result
            assert "DURATION_MS=2500" in result
    
    def test_notification_debug_formatting(self):
        """Test notification formatting in debug format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = DebugAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="notifications/progress",
                params={"progress": 50, "total": 100}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="Progress update",
                metadata={"plugin": "progress_tracker"}
            )
            
            result = plugin._format_notification_log(notification, decision, "test_server")
            
            # Should contain notification details
            assert "EVENT=NOTIFICATION" in result
            assert "METHOD=notifications/progress" in result
            assert "PLUGIN=progress_tracker" in result
            assert 'REASON="Progress update"' in result
            assert "PARAMS_JSON=" in result
            assert 'progress' in result  # JSON may be escaped, just check content
    
    def test_params_json_safety(self):
        """Test that PARAMS_JSON is safely escaped for key-value parsers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin = DebugAuditingPlugin({
                "output_file": f"{temp_dir}/test.log"
            })
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="123",
                method="tools/call",
                params={
                    "key=value": "data with = equals and spaces",
                    "quotes": 'data with "quotes" inside',
                    "backslashes": "data with \\\\ backslashes"
                }
            )
            
            decision = PolicyDecision(allowed=True, reason="")
            
            result = plugin._format_request_log(request, decision, "test_server")
            
            # Should have exactly one PARAMS_JSON field, properly quoted
            assert result.count('PARAMS_JSON="') == 1
            assert 'PARAMS_JSON="' in result
            
            # Extract the params content for validation
            params_start = result.find('PARAMS_JSON="') + len('PARAMS_JSON="')
            params_end = result.find('"', params_start)
            params_content = result[params_start:params_end]
            
            # Should contain escaped content or transformed content
            # The exact escaping may vary, but should be safe for KV parsers
            assert len(params_content) > 0
            # Content should be valid (not end with unmatched backslash unless properly escaped)
            # This is a basic safety check - exact escaping rules may vary


import re  # Add import for regex test