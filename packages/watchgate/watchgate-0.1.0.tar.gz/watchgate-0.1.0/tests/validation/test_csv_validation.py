"""Validation tests for CSV formatter using external tools.

These tests use optional dependencies that are only available in test environments.
They validate CSV format compliance with external tools like pandas.
"""

import pytest
import io
import tempfile
import os
from watchgate.plugins.auditing.csv import CsvAuditingPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestCSVValidationWithPandas:
    """Test CSV format validation with pandas DataFrame."""
    
    def test_csv_with_pandas_basic(self):
        """Test CSV format with pandas DataFrame parsing."""
        pd = pytest.importorskip("pandas")
        
        # Create CSV plugin
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.csv")
            config = {
                "output_file": log_file,
                "format": "csv",
                "critical": False
            }
            plugin = CsvAuditingPlugin(config)
            
            # Create sample events
            events = [
                (MCPRequest(jsonrpc="2.0", id="req-1", method="tools/call", params={"name": "read_file"}), 
                 PolicyDecision(allowed=True, reason="Allowed", metadata={"plugin": "test"})),
                (MCPRequest(jsonrpc="2.0", id="req-2", method="tools/call", params={"name": "write_file"}), 
                 PolicyDecision(allowed=False, reason="Blocked", metadata={"plugin": "test"})),
                (MCPRequest(jsonrpc="2.0", id="req-3", method="resources/list", params={}), 
                 PolicyDecision(allowed=True, reason="Allowed", metadata={"plugin": "test"}))
            ]
            
            # Log all events
            import asyncio
            async def log_events():
                for request, decision in events:
                    await plugin.log_request(request, decision, "test-server")
            
            asyncio.run(log_events())
            
            # Parse with pandas
            df = pd.read_csv(log_file)
            
            # Verify structure
            assert len(df) == 3
            expected_columns = [
                'timestamp', 'event_type', 'method', 'tool', 'status', 
                'request_id', 'plugin', 'reason', 'duration_ms', 'server_name',
                'compliance_framework', 'audit_trail_id'
            ]
            assert list(df.columns) == expected_columns
            
            # Verify data types and content
            assert df['event_type'].notna().all()
            assert df['timestamp'].notna().all()
            assert df['request_id'].notna().all()
            
            # Verify specific values
            assert df.iloc[0]['event_type'] == 'REQUEST'
            assert df.iloc[0]['method'] == 'tools/call'
            assert df.iloc[0]['tool'] == 'read_file'
            assert df.iloc[0]['status'] == 'ALLOWED'
            
            assert df.iloc[1]['event_type'] == 'SECURITY_BLOCK'
            assert df.iloc[1]['status'] == 'BLOCKED'
            
            assert df.iloc[2]['event_type'] == 'REQUEST'
            assert df.iloc[2]['method'] == 'resources/list'
            assert pd.isna(df.iloc[2]['tool'])  # Empty for non-tools/call (pandas reads as NaN)
    
    def test_csv_with_pandas_complex_data(self):
        """Test CSV format with complex data structures."""
        pd = pytest.importorskip("pandas")
        
        # Create CSV plugin
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.csv")
            config = {
                "output_file": log_file,
                "format": "csv",
                "critical": False
            }
            plugin = CsvAuditingPlugin(config)
            
            # Create request with complex data
            request = MCPRequest(
                jsonrpc="2.0",
                id="req-complex",
                method="tools/call",
                params={
                    "name": "complex_tool",
                    "arguments": {
                        "nested": {"key": "value"},
                        "list": [1, 2, 3],
                        "string": "test with, comma and \"quotes\""
                    }
                }
            )
            decision = PolicyDecision(
                allowed=True,
                reason="Request with complex data approved",
                metadata={"plugin": "complex_plugin", "mode": "test"}
            )
            
            # Log event
            import asyncio
            async def log_event():
                await plugin.log_request(request, decision, "test-server")
            
            asyncio.run(log_event())
            
            # Parse with pandas
            df = pd.read_csv(log_file)
            
            # Verify structure
            assert len(df) == 1
            
            # Verify complex data handling
            row = df.iloc[0]
            assert row['event_type'] == 'REQUEST'
            assert row['method'] == 'tools/call'
            assert row['tool'] == 'complex_tool'
            assert row['status'] == 'ALLOWED'
            assert row['reason'] == 'Request with complex data approved'
            assert row['plugin'] == 'complex_plugin'
    
    def test_csv_with_pandas_data_types(self):
        """Test CSV format data type handling with pandas."""
        pd = pytest.importorskip("pandas")
        
        # Create CSV plugin
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.csv")
            config = {
                "output_file": log_file,
                "format": "csv",
                "critical": False
            }
            plugin = CsvAuditingPlugin(config)
            
            # Create response with duration
            request = MCPRequest(jsonrpc="2.0", id="req-duration", method="tools/call")
            response = MCPResponse(jsonrpc="2.0", id="req-duration", result={"status": "ok"})
            decision = PolicyDecision(
                allowed=True,
                reason="Response approved",
                metadata={"plugin": "test_plugin", "duration_ms": 150}
            )
            
            # Log event
            import asyncio
            async def log_event():
                await plugin.log_response(request, response, decision, "test-server")
            
            asyncio.run(log_event())
            
            # Parse with pandas
            df = pd.read_csv(log_file)
            
            # Verify data types
            assert len(df) == 1
            row = df.iloc[0]
            
            # Duration should be readable as integer
            assert pd.notna(row['duration_ms'])
            assert row['duration_ms'] == 150  # pandas auto-converts to int64
            
            # Should be convertible to numeric
            df['duration_ms'] = pd.to_numeric(df['duration_ms'], errors='coerce')
            assert df.iloc[0]['duration_ms'] == 150
    
    def test_csv_with_pandas_special_characters(self):
        """Test CSV format with special characters using pandas."""
        pd = pytest.importorskip("pandas")
        
        # Create CSV plugin
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.csv")
            config = {
                "output_file": log_file,
                "format": "csv",
                "critical": False
            }
            plugin = CsvAuditingPlugin(config)
            
            # Create request with special characters
            special_reason = 'Contains "quotes", newlines\nand commas, and more'
            request = MCPRequest(
                jsonrpc="2.0",
                id="req-special",
                method="tools/call",
                params={"name": "special_tool"}
            )
            decision = PolicyDecision(
                allowed=False,
                reason=special_reason,
                metadata={"plugin": "special_plugin"}
            )
            
            # Log event
            import asyncio
            async def log_event():
                await plugin.log_request(request, decision, "test-server")
            
            asyncio.run(log_event())
            
            # Parse with pandas
            df = pd.read_csv(log_file)
            
            # Verify special characters are preserved
            assert len(df) == 1
            row = df.iloc[0]
            assert row['reason'] == special_reason
            assert row['event_type'] == 'SECURITY_BLOCK'
            assert row['tool'] == 'special_tool'


class TestCSVValidationWithBuiltinCSV:
    """Test CSV format validation with Python's built-in csv module."""
    
    def test_csv_with_builtin_csv_reader(self):
        """Test CSV format with Python's csv.reader."""
        import csv
        
        # Create CSV plugin
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.csv")
            config = {
                "output_file": log_file,
                "format": "csv",
                "critical": False
            }
            plugin = CsvAuditingPlugin(config)
            
            # Create and log events
            events = [
                (MCPRequest(jsonrpc="2.0", id="req-1", method="tools/call", params={"name": "read_file"}), 
                 PolicyDecision(allowed=True, reason="Allowed", metadata={"plugin": "test"})),
                (MCPRequest(jsonrpc="2.0", id="req-2", method="tools/call", params={"name": "write_file"}), 
                 PolicyDecision(allowed=False, reason="Blocked", metadata={"plugin": "test"}))
            ]
            
            import asyncio
            async def log_events():
                for request, decision in events:
                    await plugin.log_request(request, decision, "test-server")
            
            asyncio.run(log_events())
            
            # Parse with csv.reader
            with open(log_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Verify structure
            assert len(rows) == 3  # Header + 2 data rows
            
            # Verify header
            expected_header = [
                'timestamp', 'event_type', 'method', 'tool', 'status', 
                'request_id', 'plugin', 'reason', 'duration_ms', 'server_name',
                'compliance_framework', 'audit_trail_id'
            ]
            assert rows[0] == expected_header
            
            # Verify data rows
            assert rows[1][1] == 'REQUEST'  # event_type
            assert rows[1][2] == 'tools/call'  # method
            assert rows[1][3] == 'read_file'  # tool
            assert rows[1][4] == 'ALLOWED'  # status
            
            assert rows[2][1] == 'SECURITY_BLOCK'  # event_type
            assert rows[2][4] == 'BLOCKED'  # status
    
    def test_csv_with_builtin_csv_dictreader(self):
        """Test CSV format with Python's csv.DictReader."""
        import csv
        
        # Create CSV plugin
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.csv")
            config = {
                "output_file": log_file,
                "format": "csv",
                "critical": False
            }
            plugin = CsvAuditingPlugin(config)
            
            # Create and log a complex event
            request = MCPRequest(
                jsonrpc="2.0",
                id="req-dict-test",
                method="tools/call",
                params={"name": "test_tool"}
            )
            decision = PolicyDecision(
                allowed=True,
                reason="Test with special chars: \", \n, ,",
                metadata={"plugin": "dict_test_plugin", "mode": "test"}
            )
            
            import asyncio
            async def log_event():
                await plugin.log_request(request, decision, "test-server")
            
            asyncio.run(log_event())
            
            # Parse with csv.DictReader
            with open(log_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Verify structure
            assert len(rows) == 1
            row = rows[0]
            
            # Verify all expected fields are present
            expected_fields = [
                'timestamp', 'event_type', 'method', 'tool', 'status', 
                'request_id', 'plugin', 'reason', 'duration_ms', 'server_name'
            ]
            for field in expected_fields:
                assert field in row
            
            # Verify data
            assert row['event_type'] == 'REQUEST'
            assert row['method'] == 'tools/call'
            assert row['tool'] == 'test_tool'
            assert row['status'] == 'ALLOWED'
            assert row['request_id'] == 'req-dict-test'
            assert row['plugin'] == 'dict_test_plugin'
            assert row['reason'] == 'Test with special chars: ", \n, ,'
            assert row['duration_ms'] == '0'  # Zero for requests (not available)
            assert row['server_name'] == 'test-server'  # Populated with provided server name