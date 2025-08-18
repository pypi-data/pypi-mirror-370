"""Validation tests for CEF formatter using external tools.

These tests use optional dependencies that are only available in test environments.
They validate CEF format compliance with external tools like pycef and jc.
"""

import pytest
import subprocess
import shutil
import tempfile
from watchgate.plugins.auditing.common_event_format import CefAuditingPlugin, CEF_EVENT_MAPPINGS
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestCEFValidationWithPyCEF:
    """Test CEF format validation with pycef library."""

    @pytest.fixture
    def cef_plugin(self):
        """Create a CefAuditingPlugin with CEF format for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'format': 'cef',
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            yield CefAuditingPlugin(config)

    @pytest.fixture
    def sample_events(self):
        """Create sample events for testing."""
        return [
            {
                'event_type': 'REQUEST',
                'method': 'tools/call',
                'tool': 'read_file',
                'status': 'ALLOWED',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '123',
                'plugin': 'test_plugin',
                'reason': 'Request approved'
            },
            {
                'event_type': 'SECURITY_BLOCK',
                'method': 'tools/call',
                'tool': 'delete_file',
                'status': 'BLOCKED',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '456',
                'plugin': 'tool_allowlist',
                'reason': 'Tool not in allowlist'
            },
            {
                'event_type': 'RESPONSE',
                'method': 'tools/call',
                'tool': 'read_file',
                'status': 'SUCCESS',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '789',
                'duration_ms': 150
            },
            {
                'event_type': 'ERROR',
                'method': 'tools/call',
                'tool': 'read_file',
                'status': 'ERROR',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '999',
                'reason': 'File not found'
            }
        ]

    def test_cef_with_pycef_library(self, cef_plugin, sample_events):
        """Test CEF format with pycef library validation."""
        pycef = pytest.importorskip("pycef")
        
        for event in sample_events:
            cef_message = cef_plugin._format_cef_message(event)
            
            # Parse with pycef library
            try:
                parsed = pycef.parse(cef_message)
                assert parsed is not None
                assert parsed.get('DeviceVendor') == 'Watchgate'
                assert parsed.get('DeviceProduct') == 'MCP Gateway'
                assert parsed.get('DeviceVersion') == '1.0.0'
                assert parsed.get('CEFVersion') == '0'
                
                # Check that the event was parsed correctly
                assert 'DeviceEventClassID' in parsed
                assert 'Name' in parsed
                assert 'Severity' in parsed
                
                # Check some extension fields
                if 'request_id' in event:
                    assert parsed.get('requestId') == event['request_id']
                    
                if 'plugin' in event:
                    # pycef maps labels to values, so cs1Label=Plugin becomes Plugin=<value>
                    assert parsed.get('Plugin') == event['plugin']
                    
                print(f"✓ CEF message parsed successfully: {event['event_type']}")
                
            except Exception as e:
                pytest.fail(f"CEF parsing failed for event {event['event_type']}: {e}\nCEF message: {cef_message}")

    def test_cef_with_pycef_complex_data(self, cef_plugin):
        """Test CEF format with complex data structures using pycef."""
        pycef = pytest.importorskip("pycef")
        
        # Create event with complex data and special characters
        event = {
            'event_type': 'SECURITY_BLOCK',
            'method': 'tools/call',
            'tool': 'complex=tool',
            'status': 'BLOCKED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123\\test',
            'plugin': 'test|plugin',
            'reason': 'Contains "quotes", newlines\nand pipes|, equals=signs'
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Parse with pycef
        parsed = pycef.parse(cef_message)
        
        # Verify basic structure
        assert parsed.get('DeviceVendor') == 'Watchgate'
        assert parsed.get('DeviceProduct') == 'MCP Gateway'
        assert parsed.get('DeviceEventClassID') == '200'  # SECURITY_BLOCK
        assert parsed.get('Name') == 'Security Block'
        assert parsed.get('Severity') == '8'
        
        # Verify escaped characters are handled properly
        assert parsed.get('requestId') == '123\\\\test'  # Double-escaped in CEF
        assert parsed.get('Plugin') == 'test\\|plugin'
        assert 'quotes' in parsed.get('reason', '')
        assert 'newlines' in parsed.get('reason', '')

    def test_cef_with_pycef_all_event_types(self, cef_plugin):
        """Test CEF format compliance for all event types using pycef."""
        pycef = pytest.importorskip("pycef")
        
        base_event = {
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123',
            'method': 'tools/call',
            'tool': 'test_tool',
            'status': 'ALLOWED'
        }
        
        for event_type, mapping in CEF_EVENT_MAPPINGS.items():
            event = base_event.copy()
            event['event_type'] = event_type
            
            cef_message = cef_plugin._format_cef_message(event)
            
            # Parse with pycef
            parsed = pycef.parse(cef_message)
            
            # Verify event type mapping
            assert parsed.get('DeviceEventClassID') == mapping['event_id']
            assert parsed.get('Name') == mapping['name']
            assert parsed.get('Severity') == str(mapping['severity'])
            
            # Verify basic structure
            assert parsed.get('DeviceVendor') == 'Watchgate'
            assert parsed.get('DeviceProduct') == 'MCP Gateway'
            assert parsed.get('CEFVersion') == '0'
            
            print(f"✓ pycef validated event type: {event_type}")


class TestCEFValidationWithJC:
    """Test CEF format validation with jc command-line tool."""

    @pytest.fixture
    def cef_plugin(self):
        """Create a CefAuditingPlugin with CEF format for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'format': 'cef',
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            yield CefAuditingPlugin(config)

    @pytest.fixture
    def sample_events(self):
        """Create sample events for testing."""
        return [
            {
                'event_type': 'REQUEST',
                'method': 'tools/call',
                'tool': 'read_file',
                'status': 'ALLOWED',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '123',
                'plugin': 'test_plugin',
                'reason': 'Request approved'
            },
            {
                'event_type': 'SECURITY_BLOCK',
                'method': 'tools/call',
                'tool': 'delete_file',
                'status': 'BLOCKED',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '456',
                'plugin': 'tool_allowlist',
                'reason': 'Tool not in allowlist'
            },
            {
                'event_type': 'RESPONSE',
                'method': 'tools/call',
                'tool': 'read_file',
                'status': 'SUCCESS',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '789',
                'duration_ms': 150
            },
            {
                'event_type': 'ERROR',
                'method': 'tools/call',
                'tool': 'read_file',
                'status': 'ERROR',
                'timestamp': '2023-12-01T14:30:25.123456Z',
                'request_id': '999',
                'reason': 'File not found'
            }
        ]

    def test_cef_with_jc_validator(self, cef_plugin, sample_events):
        """Test CEF format with jc command-line validator."""
        if not shutil.which('jc'):
            pytest.skip("jc command not available")
        
        for event in sample_events:
            cef_message = cef_plugin._format_cef_message(event)
            
            # Validate with jc
            try:
                result = subprocess.run(
                    ['jc', '--cef'],
                    input=cef_message,
                    text=True,
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    pytest.fail(f"jc validation failed for event {event['event_type']}: {result.stderr}\nCEF message: {cef_message}")
                
                # If jc succeeded, the CEF message is valid
                print(f"✓ CEF message validated with jc: {event['event_type']}")
                
            except subprocess.TimeoutExpired:
                pytest.fail(f"jc validation timed out for event {event['event_type']}")
            except Exception as e:
                pytest.fail(f"jc validation error for event {event['event_type']}: {e}")

    def test_cef_with_jc_complex_data(self, cef_plugin):
        """Test CEF format with complex data using jc validator."""
        if not shutil.which('jc'):
            pytest.skip("jc command not available")
        
        # Create event with special characters that need escaping
        event = {
            'event_type': 'REQUEST',
            'method': 'tools|call',  # Pipe character
            'tool': 'test=tool',     # Equals character
            'status': 'ALLOWED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123\\test',  # Backslash character
            'reason': 'Test\nwith\nnewlines'  # Newline characters
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Validate with jc
        result = subprocess.run(
            ['jc', '--cef'],
            input=cef_message,
            text=True,
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            pytest.fail(f"jc validation failed for complex data: {result.stderr}\nCEF message: {cef_message}")
        
        print("✓ CEF message with complex data validated with jc")

    def test_cef_with_jc_all_event_types(self, cef_plugin):
        """Test all CEF event types with jc validator."""
        if not shutil.which('jc'):
            pytest.skip("jc command not available")
        
        base_event = {
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123',
            'method': 'tools/call',
            'tool': 'test_tool',
            'status': 'ALLOWED'
        }
        
        for event_type in CEF_EVENT_MAPPINGS.keys():
            event = base_event.copy()
            event['event_type'] = event_type
            
            cef_message = cef_plugin._format_cef_message(event)
            
            # Validate with jc
            result = subprocess.run(
                ['jc', '--cef'],
                input=cef_message,
                text=True,
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                pytest.fail(f"jc validation failed for event type {event_type}: {result.stderr}\nCEF message: {cef_message}")
            
            print(f"✓ jc validated event type: {event_type}")


class TestCEFValidationIntegration:
    """Integration tests for CEF validation with real MCP message flows."""

    @pytest.fixture
    def cef_plugin(self):
        """Create a CefAuditingPlugin with CEF format for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'format': 'cef',
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            yield CefAuditingPlugin(config)

    @pytest.mark.asyncio
    async def test_cef_validation_with_real_mcp_flow(self, cef_plugin):
        """Test CEF validation with real MCP request/response flow."""
        pycef = pytest.importorskip("pycef")
        
        # Create real MCP request
        request = MCPRequest(
            jsonrpc="2.0",
            method='tools/call',
            params={'name': 'read_file', 'arguments': {'path': '/test.txt'}},
            id='test-123'
        )
        
        # Create real MCP response
        response = MCPResponse(
            jsonrpc="2.0",
            result={'content': 'file content'},
            id='test-123'
        )
        
        # Create policy decisions
        request_decision = PolicyDecision(
            allowed=True,
            reason='Request approved',
            metadata={'plugin': 'test_plugin'}
        )
        
        response_decision = PolicyDecision(
            allowed=True,
            reason='Response approved',
            metadata={'duration_ms': 150}
        )
        
        # Log request and response
        await cef_plugin.log_request(request, request_decision, "test-server")
        await cef_plugin.log_response(request, response, response_decision, "test-server")
        
        # Read the log file and validate each CEF message
        with open(cef_plugin.output_file, 'r') as f:
            log_content = f.read()
        
        cef_messages = [line for line in log_content.split('\n') if line.startswith('CEF:')]
        assert len(cef_messages) >= 2  # At least request and response
        
        for cef_message in cef_messages:
            # Validate with pycef
            parsed = pycef.parse(cef_message)
            
            # Verify basic structure
            assert parsed.get('DeviceVendor') == 'Watchgate'
            assert parsed.get('DeviceProduct') == 'MCP Gateway'
            assert parsed.get('DeviceVersion') == '1.0.0'
            assert parsed.get('CEFVersion') == '0'
            
            # Should have event class ID and name
            assert 'DeviceEventClassID' in parsed
            assert 'Name' in parsed
            assert 'Severity' in parsed
            
            print(f"✓ Real MCP flow CEF message validated: {parsed.get('Name')}")

    @pytest.mark.asyncio
    async def test_cef_validation_with_notification(self, cef_plugin):
        """Test CEF validation with MCP notification."""
        pycef = pytest.importorskip("pycef")
        
        # Create real MCP notification
        notification = MCPNotification(
            jsonrpc="2.0",
            method='notifications/initialized',
            params={'version': '1.0.0'}
        )
        
        decision = PolicyDecision(
            allowed=True,
            reason='Notification processed'
        )
        
        # Log notification
        await cef_plugin.log_notification(notification, decision, "test-server")
        
        # Read and validate
        with open(cef_plugin.output_file, 'r') as f:
            log_content = f.read()
        
        cef_messages = [line for line in log_content.split('\n') if line.startswith('CEF:')]
        assert len(cef_messages) >= 1
        
        for cef_message in cef_messages:
            parsed = pycef.parse(cef_message)
            
            # Verify notification-specific fields
            assert parsed.get('DeviceEventClassID') == '102'  # NOTIFICATION
            assert parsed.get('Name') == 'MCP Notification'
            assert parsed.get('Severity') == '4'
            
            print("✓ MCP notification CEF message validated")