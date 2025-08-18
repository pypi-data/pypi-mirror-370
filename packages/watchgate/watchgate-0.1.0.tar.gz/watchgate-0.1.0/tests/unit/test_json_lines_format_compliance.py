"""Tests for JSON Lines auditing plugin format compliance and error handling.

This test suite verifies:
- JSON-RPC error code classification
- JSON Lines (JSONL) format enforcement
- Timezone-aware timestamp generation
- Response log field completeness for correlation
- Safe attribute access for optional fields
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import pytest

from watchgate.plugins.auditing.json_lines import JsonAuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision


class TestJsonRpcErrorClassification:
    """Test correct classification of JSON-RPC error codes."""
    
    def test_upstream_server_error_classification(self):
        """Test that JSON-RPC server errors (-32000 to -32099) are classified as UPSTREAM_ERROR."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Test various server error codes
            for error_code in [-32000, -32050, -32099]:
                error_response = MCPResponse(jsonrpc="2.0", id="test")
                error_response.error = {"code": error_code, "message": "Server error"}
                
                log_output = plugin._format_response_log(
                    MCPRequest(jsonrpc="2.0", method="test", id="test"),
                    error_response,
                    PolicyDecision(allowed=True, reason="test"),
                    "test_server"
                )
                
                log_data = json.loads(log_output.strip())
                assert log_data["event_type"] == "UPSTREAM_ERROR", \
                    f"Error code {error_code} should be UPSTREAM_ERROR"
    
    def test_protocol_error_classification(self):
        """Test that protocol/client errors are classified as ERROR."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Test various protocol error codes
            protocol_errors = [
                (-32700, "Parse error"),
                (-32600, "Invalid Request"),
                (-32601, "Method not found"),
                (-32602, "Invalid params"),
                (-32603, "Internal error"),
            ]
            
            for error_code, message in protocol_errors:
                error_response = MCPResponse(jsonrpc="2.0", id="test")
                error_response.error = {"code": error_code, "message": message}
                
                log_output = plugin._format_response_log(
                    MCPRequest(jsonrpc="2.0", method="test", id="test"),
                    error_response,
                    PolicyDecision(allowed=True, reason="test"),
                    "test_server"
                )
                
                log_data = json.loads(log_output.strip())
                assert log_data["event_type"] == "ERROR", \
                    f"Error code {error_code} should be ERROR, not {log_data['event_type']}"
    
    def test_error_object_attribute_access(self):
        """Test safe access to error as object attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Create response with error as object with attributes
            error_response = MCPResponse(jsonrpc="2.0", id="test")
            
            class ErrorObject:
                code = -32050
                message = "Server error"
            
            error_response.error = ErrorObject()
            
            # Should not crash and should classify correctly
            log_output = plugin._format_response_log(
                MCPRequest(jsonrpc="2.0", method="test", id="test"),
                error_response,
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert log_data["event_type"] == "UPSTREAM_ERROR"
            assert log_data["error_code"] == -32050
            assert log_data["error_message"] == "Server error"


class TestJsonLinesFormatEnforcement:
    """Test JSON Lines (JSONL) format requirements."""
    
    def test_jsonl_format_disables_pretty_print(self):
        """Test that output_format='jsonl' automatically disables pretty_print."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'output_format': 'jsonl',
                'pretty_print': True  # Should be auto-disabled
            }
            
            plugin = JsonAuditingPlugin(config)
            assert plugin.pretty_print is False, \
                "pretty_print should be automatically disabled for JSONL format"
    
    def test_jsonl_output_includes_newline(self):
        """Test that JSON Lines output includes trailing newline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'pretty_print': False  # JSON Lines mode
            }
            plugin = JsonAuditingPlugin(config)
            
            # Test request log
            request_log = plugin._format_request_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            assert request_log.endswith('\n'), "JSONL output must end with newline"
            
            # Verify it's valid single-line JSON
            json_part = request_log.rstrip('\n')
            assert '\n' not in json_part, "JSONL must be single-line JSON"
            json.loads(json_part)  # Should parse successfully
            
            # Test response log
            response_log = plugin._format_response_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                MCPResponse(jsonrpc="2.0", id="123", result={}),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            assert response_log.endswith('\n'), "JSONL output must end with newline"
    
    def test_pretty_print_produces_multiline_json(self):
        """Test that pretty_print=True produces multi-line formatted JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'pretty_print': True
            }
            plugin = JsonAuditingPlugin(config)
            
            request_log = plugin._format_request_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            # Pretty printed JSON should have multiple lines (including final newline)
            lines = request_log.split('\n')
            assert len(lines) > 2, "Pretty print should produce multi-line JSON with final newline"
            
            # Remove final newline and parse as JSON  
            json_content = request_log.rstrip('\n')
            json.loads(json_content)  # Should still be valid JSON


class TestTimezoneAwareTimestamps:
    """Test timezone-aware timestamp generation."""
    
    def test_iso8601_timestamp_includes_timezone(self):
        """Test that ISO8601 timestamps include timezone information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'timestamp_format': 'iso8601'
            }
            plugin = JsonAuditingPlugin(config)
            
            timestamp = plugin._format_timestamp()
            
            # Should be a string in ISO format
            assert isinstance(timestamp, str)
            
            # Should parse as a timezone-aware datetime
            dt = datetime.fromisoformat(timestamp)
            assert dt.tzinfo is not None, "Timestamp should include timezone"
            
            # Should include timezone indicator (+ or - or Z)
            assert any(char in timestamp for char in ['+', '-', 'Z']), \
                "ISO8601 timestamp should include timezone offset"
    
    def test_unix_timestamp_format(self):
        """Test that unix_timestamp format works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'timestamp_format': 'unix_timestamp'
            }
            plugin = JsonAuditingPlugin(config)
            
            timestamp = plugin._format_timestamp()
            
            # Should be an integer
            assert isinstance(timestamp, int)
            
            # Should be a reasonable Unix timestamp (after year 2020)
            assert timestamp > 1577836800, "Timestamp should be after 2020"


class TestResponseLogCorrelation:
    """Test that response logs include fields for correlation with requests."""
    
    def test_response_log_includes_method(self):
        """Test that response logs include the method from the original request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            request = MCPRequest(jsonrpc="2.0", method="tools/list", id="123")
            response = MCPResponse(jsonrpc="2.0", id="123", result=[])
            
            log_output = plugin._format_response_log(
                request,
                response,
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert "method" in log_data, "Response log should include method field"
            assert log_data["method"] == "tools/list", \
                f"Method should be 'tools/list', got {log_data['method']}"
    
    def test_response_log_includes_tool_name_for_tools_call(self):
        """Test that response logs include tool name for tools/call requests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call",
                id="123",
                params={"name": "read_file", "arguments": {"path": "/test"}}
            )
            response = MCPResponse(jsonrpc="2.0", id="123", result={"content": "test"})
            
            log_output = plugin._format_response_log(
                request,
                response,
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert "tool" in log_data, "Response log should include tool field for tools/call"
            assert log_data["tool"] == "read_file", \
                f"Tool should be 'read_file', got {log_data['tool']}"
    
    def test_response_log_no_tool_field_for_non_tools_call(self):
        """Test that non-tools/call responses don't include tool field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            request = MCPRequest(jsonrpc="2.0", method="resources/list", id="123")
            response = MCPResponse(jsonrpc="2.0", id="123", result=[])
            
            log_output = plugin._format_response_log(
                request,
                response,
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert "tool" not in log_data, \
                "Response log should not include tool field for non-tools/call"


class TestSafeAttributeAccess:
    """Test safe access to optional decision attributes."""
    
    def test_safe_modified_content_access(self):
        """Test that accessing decision.modified_content doesn't crash when absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Test with decision lacking modified_content attribute
            decision = PolicyDecision(allowed=True, reason="test")
            
            log_output = plugin._format_response_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                MCPResponse(jsonrpc="2.0", id="123", result={}),
                decision,
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert log_data["event_type"] == "RESPONSE", \
                "Should be RESPONSE when no modification"
    
    def test_redaction_detected_when_modified_content_present(self):
        """Test that redaction is detected when modified_content is present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Create decision with modified_content
            decision = PolicyDecision(allowed=True, reason="PII redacted")
            decision.modified_content = {"result": "REDACTED"}
            
            log_output = plugin._format_response_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                MCPResponse(jsonrpc="2.0", id="123", result={"result": "SSN: 123-45-6789"}),
                decision,
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert log_data["event_type"] == "REDACTION", \
                "Should be REDACTION when modified_content is present"


class TestSensitiveDataRedaction:
    """Test redaction of sensitive fields in request bodies."""
    
    def test_redact_sensitive_fields_in_request_body(self):
        """Test that sensitive fields are redacted when logging request bodies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'include_request_body': True
            }
            plugin = JsonAuditingPlugin(config)
            
            # Create request with sensitive data
            request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call",
                id="123",
                params={
                    "name": "authenticate",
                    "arguments": {
                        "username": "user123",
                        "password": "secret123",  # Should be redacted
                        "token": "abc123",        # Should be redacted
                        "normal_field": "visible_data"  # Should remain
                    }
                }
            )
            
            log_output = plugin._format_request_log(
                request,
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            
            # Check that sensitive fields are redacted
            assert "request_body" in log_data
            params = log_data["request_body"]
            assert params["arguments"]["password"] == "[REDACTED]"
            assert params["arguments"]["token"] == "[REDACTED]"
            
            # Check that non-sensitive fields remain
            assert params["arguments"]["username"] == "user123"
            assert params["arguments"]["normal_field"] == "visible_data"
            assert params["name"] == "authenticate"
    
    def test_custom_redaction_fields(self):
        """Test that custom redaction field lists work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'include_request_body': True,
                'redact_request_fields': ['custom_secret', 'api_key']
            }
            plugin = JsonAuditingPlugin(config)
            
            # Create request with custom sensitive fields
            request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call", 
                id="123",
                params={
                    "password": "should_not_be_redacted",  # Not in custom list
                    "custom_secret": "should_be_redacted",
                    "api_key": "should_be_redacted",
                    "normal_field": "visible"
                }
            )
            
            log_output = plugin._format_request_log(
                request,
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            params = log_data["request_body"]
            
            # Custom fields should be redacted
            assert params["custom_secret"] == "[REDACTED]"
            assert params["api_key"] == "[REDACTED]"
            
            # Default sensitive field not in list should remain
            assert params["password"] == "should_not_be_redacted"
            assert params["normal_field"] == "visible"
    
    def test_redaction_performance_optimization(self):
        """Test that redaction uses precomputed set for performance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'include_request_body': True,
                'redact_request_fields': ['SECRET', 'Token', 'API_Key']  # Mixed case
            }
            plugin = JsonAuditingPlugin(config)
            
            # Verify precomputed set exists and is lowercase
            assert hasattr(plugin, '_redact_field_set')
            assert plugin._redact_field_set == {'secret', 'token', 'api_key'}
            
            # Test case-insensitive matching
            request = MCPRequest(
                jsonrpc="2.0",
                method="test",
                id="123",
                params={
                    "secret": "should_be_redacted",      # lowercase match
                    "SECRET": "should_be_redacted",      # uppercase match  
                    "Token": "should_be_redacted",       # mixed case match
                    "api_key": "should_be_redacted",     # lowercase match
                    "normal_field": "visible"
                }
            )
            
            log_output = plugin._format_request_log(
                request,
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            params = log_data["request_body"]
            
            # All variations should be redacted
            assert params["secret"] == "[REDACTED]"
            assert params["SECRET"] == "[REDACTED]"
            assert params["Token"] == "[REDACTED]"
            assert params["api_key"] == "[REDACTED]"
            
            # Normal field should remain
            assert params["normal_field"] == "visible"


class TestStatusVocabularyNormalization:
    """Test normalized decision_status field."""
    
    def test_normalized_decision_status_in_request_logs(self):
        """Test that request logs include normalized decision_status field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Test allowed request
            log_output = plugin._format_request_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert log_data["status"] == "ALLOWED"  # Legacy field
            assert log_data["decision_status"] == "allowed"  # Normalized field
            
            # Test blocked request
            log_output = plugin._format_request_log(
                MCPRequest(jsonrpc="2.0", method="test", id="124"),
                PolicyDecision(allowed=False, reason="blocked"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert log_data["status"] == "BLOCKED"  # Legacy field
            assert log_data["decision_status"] == "blocked"  # Normalized field
    
    def test_normalized_decision_status_in_response_logs(self):
        """Test that response logs include normalized decision_status field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Test successful response
            log_output = plugin._format_response_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                MCPResponse(jsonrpc="2.0", id="123", result={}),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            assert log_data["status"] == "success"  # Legacy field
            assert log_data["decision_status"] == "success"  # Normalized field


class TestTimestampConsistency:
    """Test timestamp consistency optimization."""
    
    def test_timestamp_consistency_within_single_log_entry(self):
        """Test that timestamp and audit_timestamp are identical within same log entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'include_risk_metadata': True  # Enable compliance metadata with audit_timestamp
            }
            plugin = JsonAuditingPlugin(config)
            
            # Generate a request log with compliance metadata
            log_output = plugin._format_request_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            log_data = json.loads(log_output.strip())
            
            # Extract timestamps
            main_timestamp = log_data["timestamp"]
            compliance_metadata = log_data.get("compliance_metadata", {})
            audit_timestamp = compliance_metadata.get("audit_timestamp")
            
            # Both timestamps should be identical (no drift)
            assert main_timestamp == audit_timestamp, \
                f"Timestamps should be identical: {main_timestamp} != {audit_timestamp}"
    
    def test_timestamp_changes_between_separate_log_entries(self):
        """Test that timestamp cache is cleared between separate log entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Generate first log entry
            log1 = plugin._format_request_log(
                MCPRequest(jsonrpc="2.0", method="test", id="123"),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            # Small delay to ensure timestamp would be different
            import time
            time.sleep(0.001)
            
            # Generate second log entry  
            log2 = plugin._format_request_log(
                MCPRequest(jsonrpc="2.0", method="test", id="124"),
                PolicyDecision(allowed=True, reason="test"),
                "test_server"
            )
            
            data1 = json.loads(log1.strip())
            data2 = json.loads(log2.strip())
            
            # Timestamps should be different between separate entries
            assert data1["timestamp"] != data2["timestamp"], \
                "Timestamps should be different between separate log entries"


class TestJsonSerializationRobustness:
    """Test JSON serialization error handling."""
    
    def test_serialization_fallback_on_error(self):
        """Test that serialization errors are handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = JsonAuditingPlugin(config)
            
            # Create a log_data dict with non-serializable content
            # We'll mock this by calling _format_json_output directly
            class NonSerializable:
                def __str__(self):
                    return "NonSerializable"
            
            log_data = {
                "timestamp": plugin._format_timestamp(),
                "event_type": "TEST",
                "non_serializable": NonSerializable()  # This will cause TypeError
            }
            
            # Should handle the error and return safe JSON
            result = plugin._format_json_output(log_data)
            
            # Should be valid JSON
            parsed = json.loads(result.strip())
            
            # Should contain error information
            assert "error" in parsed
            assert parsed["error"] == "JSON serialization failed"
            assert "error_details" in parsed
            assert parsed["event_type"] == "TEST"  # Should preserve safe fields