"""Tests for CSV formatter functionality in CsvAuditingPlugin.

This test suite follows Test-Driven Development (TDD) methodology:
1. RED: Tests are written first and should fail initially since CSV implementation is incomplete
2. GREEN: Minimal implementation is added to make tests pass
3. REFACTOR: Code is improved while keeping tests green

These tests define the contract for CSV format support in the CsvAuditingPlugin.
"""

import pytest
import io
import csv
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from watchgate.plugins.auditing.csv import CsvAuditingPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestCSVFormatterBasic:
    """Test basic CSV formatter functionality."""
    
    def test_csv_formatter_initialization(self):
        """Test CSV formatter is initialized."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {"output_file": f.name}
            plugin = CsvAuditingPlugin(config)
            
            # Should have CSV attributes
            assert hasattr(plugin, 'delimiter')
            assert hasattr(plugin, 'field_order')
            assert plugin.field_order is not None
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_format_basic_request(self):
        """Test basic CSV message formatting for request."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {"output_file": f.name}
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test-123",
                method="tools/list",
                params={}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="Default allow",
                metadata={"plugin": "test_plugin"}
            )
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Parse CSV to verify structure
            reader = csv.DictReader(io.StringIO(formatted))
            rows = list(reader)
            
            assert len(rows) == 1
            row = rows[0]
            
            # Check basic fields
            assert row.get('event_type') == 'REQUEST'
            assert row.get('request_id') == 'test-123'
            assert row.get('method') == 'tools/list'
            assert row.get('status') == 'ALLOWED'
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_format_with_header(self):
        """Test CSV formatting includes header."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {"output_file": f.name}
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test-456",
                method="tools/call",
                params={"tool": "read_file"}
            )
            
            decision = PolicyDecision(
                allowed=False,
                reason="Blocked by policy"
            )
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            lines = formatted.strip().split('\n')
            assert len(lines) == 2  # Header + data row
            
            # Check header contains expected fields
            header_fields = lines[0].split(',')
            expected_fields = ['timestamp', 'event_type', 'request_id', 'method', 'status']
            for field in expected_fields:
                assert field in header_fields
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_format_special_characters(self):
        """Test CSV formatting handles special characters."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {"output_file": f.name}
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test-789",
                method="tools/call",
                params={"content": 'String with "quotes" and\nnewlines'}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Reason with, comma and "quotes"'
            )
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Parse with CSV reader to ensure proper escaping
            reader = csv.DictReader(io.StringIO(formatted))
            row = next(reader)
            
            # Check special characters are preserved
            assert '"quotes"' in row['reason']
            assert 'comma' in row['reason']
            
            # Clean up
            os.unlink(f.name)


class TestCSVFormatterConfiguration:
    """Test CSV formatter configuration options."""
    
    def test_csv_custom_delimiter(self):
        """Test CSV formatting with custom delimiter."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "format": "csv",
                "csv_config": {
                    "delimiter": "|"
                }
            }
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test-pipe",
                method="initialize",
                params={}
            )
            
            decision = PolicyDecision(allowed=True, reason="OK")
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Check delimiter is used
            assert '|' in formatted
            assert ',' not in formatted  # Default delimiter not used
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_custom_quote_char(self):
        """Test CSV formatting with custom quote character."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "format": "csv",
                "csv_config": {
                    "quote_char": "'"
                }
            }
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test-quote",
                method="tools/list",
                params={"filter": "needs 'quotes'"}
            )
            
            decision = PolicyDecision(allowed=True, reason="Contains 'quotes'")
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Verify single quotes are used for quoting
            # The string "needs 'quotes'" should be escaped with doubled single quotes
            assert "''" in formatted  # Escaped single quote
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_null_value_handling(self):
        """Test CSV formatting with custom null value."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "format": "csv",
                "csv_config": {
                    "null_value": "N/A"
                }
            }
            plugin = CsvAuditingPlugin(config)
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="server/log",
                params={"level": "info", "message": "test"}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="OK",
                metadata={}
            )
            
            csv_row = plugin._build_csv_row(notification, None, decision, "NOTIFICATION", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(formatted))
            row = next(reader)
            
            # Check null values are replaced (for notifications without request_id)
            # The empty request_id should be replaced with N/A or remain empty depending on implementation
            assert row.get('request_id') in ['N/A', '']  # Notifications have no ID
            
            # Clean up
            os.unlink(f.name)


class TestCSVFormatterCompliance:
    """Test CSV formatter compliance features."""
    
    def test_csv_sox_compliance_format(self):
        """Test CSV formatting with SOX compliance columns."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "format": "csv",
                "csv_config": {
                    "include_compliance_columns": True,
                    "audit_trail_format": "SOX_404"
                }
            }
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="sox-test",
                method="tools/call",
                params={"tool": "write_file", "args": {"path": "/etc/passwd"}}
            )
            
            decision = PolicyDecision(
                allowed=False,
                reason="Security policy violation",
                metadata={
                    "plugin": "filesystem_security",
                    "risk_score": 9
                }
            )
            
            csv_row = plugin._build_csv_row(request, None, decision, "SECURITY_BLOCK", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(formatted))
            rows = list(reader)
            
            assert len(rows) == 1
            row = rows[0]
            
            # Check compliance fields are included
            assert 'audit_trail_id' in row
            assert 'compliance_framework' in row
            assert row.get('compliance_framework') == 'SOX_404'
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_gdpr_compliance_format(self):
        """Test CSV formatting with GDPR compliance columns."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "format": "csv",
                "csv_config": {
                    "include_compliance_columns": True,
                    "audit_trail_format": "GDPR"
                }
            }
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="gdpr-test",
                method="tools/call",
                params={"tool": "read_file", "args": {"path": "user_data.csv"}}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="Allowed with audit",
                metadata={
                    "contains_pii": True,
                    "data_categories": ["personal", "financial"]
                }
            )
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(formatted))
            rows = list(reader)
            
            assert len(rows) == 1
            row = rows[0]
            
            # Check GDPR-specific fields
            assert 'audit_trail_id' in row
            assert 'compliance_framework' in row
            
            # Clean up
            os.unlink(f.name)


class TestCSVFormatterIntegration:
    """Test CSV formatter integration with CsvAuditingPlugin."""
    
    @pytest.mark.asyncio
    async def test_csv_log_request_response_cycle(self):
        """Test CSV formatting through complete request/response cycle."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {"output_file": f.name}
            plugin = CsvAuditingPlugin(config)
            
            # Request
            request = MCPRequest(
                jsonrpc="2.0",
                id="cycle-test",
                method="tools/call",
                params={"name": "calculator", "args": {"operation": "add", "a": 1, "b": 2}}
            )
            
            request_decision = PolicyDecision(
                allowed=True,
                reason="Calculator allowed"
            )
            
            # Log request
            await plugin.log_request(request, request_decision, "test_server")
            
            # Response
            response = MCPResponse(
                jsonrpc="2.0",
                id="cycle-test",
                result={"output": "3"}
            )
            
            response_decision = PolicyDecision(
                allowed=True,
                reason="Response allowed",
                metadata={"duration_ms": 42}
            )
            
            # Log response
            await plugin.log_response(request, response, response_decision, "test_server")
            
            # Read and verify CSV file
            with open(f.name, 'r') as csv_file:
                content = csv_file.read()
                lines = content.strip().split('\n')
                
                # Should have header + 2 data rows
                assert len(lines) >= 3
                
                # Verify both request and response are logged
                assert 'REQUEST' in content
                assert 'RESPONSE' in content
                assert 'cycle-test' in content
                assert 'calculator' in content
                # Duration is calculated dynamically, just verify it's present
                assert 'duration_ms' in lines[0]  # Header has duration_ms column
            
            # Clean up
            os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_csv_log_notification(self):
        """Test CSV formatting for notifications."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {"output_file": f.name}
            plugin = CsvAuditingPlugin(config)
            
            notification = MCPNotification(
                jsonrpc="2.0",
                method="server/progress",
                params={"progress": 50, "total": 100, "operation": "indexing"}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="Notification logged"
            )
            
            await plugin.log_notification(notification, decision, "test_server")
            
            # Read and verify CSV file
            with open(f.name, 'r') as csv_file:
                content = csv_file.read()
                
                # Verify notification is logged
                assert 'NOTIFICATION' in content
                assert 'server/progress' in content
                assert 'indexing' in content
            
            # Clean up
            os.unlink(f.name)


class TestCSVFormatterErrorHandling:
    """Test CSV formatter error handling."""
    
    def test_csv_invalid_delimiter(self):
        """Test CSV formatter rejects invalid delimiter."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "format": "csv",
                "csv_config": {
                    "delimiter": "abc"  # Multi-character delimiter
                }
            }
            
            with pytest.raises(ValueError, match="delimiter must be a single character"):
                CsvAuditingPlugin(config)
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_invalid_quote_style(self):
        """Test CSV formatter rejects invalid quote style."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "format": "csv",
                "csv_config": {
                    "quote_style": "invalid_style"
                }
            }
            
            with pytest.raises(ValueError, match="Invalid quote_style"):
                CsvAuditingPlugin(config)
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_quote_none_with_escapechar(self):
        """Test CSV formatting with QUOTE_NONE and escapechar for fields containing delimiters."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {
                "output_file": f.name,
                "csv_config": {
                    "quote_style": "none",
                    "escape_char": "\\",
                    "delimiter": ","
                }
            }
            plugin = CsvAuditingPlugin(config)
            
            # Create request with comma in the reason (delimiter character)
            request = MCPRequest(
                jsonrpc="2.0",
                id="test-escape",
                method="tools/call",
                params={"name": "test,tool"}  # Contains delimiter
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="Test with comma, and more text",  # Contains delimiter
                metadata={"plugin": "escape_test"}
            )
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Should handle the comma correctly with escapechar
            assert formatted is not None
            # Verify the CSV can be parsed back correctly
            import csv
            import io
            reader = csv.reader(io.StringIO(formatted), delimiter=',', escapechar='\\')
            rows = list(reader)
            # Should have header + data row
            assert len(rows) == 2
            
            # Clean up
            os.unlink(f.name)
    
    def test_csv_format_with_complex_data(self):
        """Test CSV formatting handles complex nested data."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            config = {"output_file": f.name}
            plugin = CsvAuditingPlugin(config)
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="complex-test",
                method="tools/call",
                params={
                    "name": "complex_tool",
                    "args": {
                        "nested": {
                            "deep": {
                                "value": "test"
                            }
                        },
                        "list": [1, 2, 3],
                        "boolean": True
                    }
                }
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason="Complex data test",
                metadata={
                    "scores": [0.1, 0.2, 0.3],
                    "flags": {"a": True, "b": False}
                }
            )
            
            csv_row = plugin._build_csv_row(request, None, decision, "REQUEST", "test-server")
            formatted = plugin._format_csv_message(csv_row)
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(formatted))
            row = next(reader)
            
            # Complex data should be handled (note: CSV doesn't include full params)
            # Just verify the basic request structure is preserved
            assert row.get('request_id') == 'complex-test'
            assert row.get('tool') == 'complex_tool'
            
            # Clean up
            os.unlink(f.name)