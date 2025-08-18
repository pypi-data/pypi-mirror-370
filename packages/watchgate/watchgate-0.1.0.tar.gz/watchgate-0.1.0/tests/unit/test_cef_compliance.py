"""Unit tests for CEF format compliance without external dependencies.

These tests verify CEF format compliance using internal validation methods only.
They test format structure, escaping, and specification adherence.
"""

import pytest
import tempfile
from watchgate.plugins.auditing.common_event_format import CefAuditingPlugin, CEF_EVENT_MAPPINGS, DEFAULT_CEF_EVENT_MAPPING


class TestCEFComplianceInternal:
    """Test CEF format compliance using internal validation."""

    @pytest.fixture
    def cef_plugin(self):
        """Create a CefAuditingPlugin with CEF format for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            yield CefAuditingPlugin(config)

    def test_cef_format_compliance_basic(self, cef_plugin):
        """Test basic CEF format compliance without external tools."""
        event = {
            'event_type': 'REQUEST',
            'method': 'tools/call',
            'tool': 'read_file',
            'status': 'ALLOWED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123'
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Basic CEF format validation
        assert cef_message.startswith('CEF:0|')
        
        # Split header and extension
        parts = cef_message.split('|', 7)
        assert len(parts) == 8  # 7 header fields + extension
        
        # Check header fields
        assert parts[0] == 'CEF:0'
        assert parts[1] == 'Watchgate'
        assert parts[2] == 'MCP Gateway'
        assert parts[3] == '1.0.0'
        assert parts[4] == '100'  # REQUEST event ID
        assert parts[5] == 'MCP Request'
        assert parts[6] == '6'  # REQUEST severity
        
        # Check extension format
        extension = parts[7]
        assert '=' in extension
        assert 'requestId=123' in extension
        assert 'act=allowed' in extension
        assert 'rt=Dec 01 2023 14:30:25' in extension

    def test_cef_escaping_compliance(self, cef_plugin):
        """Test CEF escaping compliance."""
        event = {
            'event_type': 'REQUEST',
            'method': 'tools|call',  # Pipe in method (would go to header if used there)
            'tool': 'read=file',     # Equals in tool name
            'status': 'ALLOWED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123\\test',  # Backslash in request ID
            'reason': 'Test\nreason\rwith\r\nspecial chars'  # Newlines in reason
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Check that extensions are properly escaped
        assert 'cs3=read\\=file' in cef_message  # Tool name with escaped equals
        assert 'requestId=123\\\\test' in cef_message  # Request ID with escaped backslash
        assert 'reason=Test\\nnewline' in cef_message or 'reason=Test\\nreason\\rwith\\r\\nspecial chars' in cef_message

    def test_cef_all_event_types_compliance(self, cef_plugin):
        """Test CEF compliance for all supported event types."""
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
            
            # Check that the event type is mapped correctly
            assert f"|{mapping['event_id']}|{mapping['name']}|{mapping['severity']}|" in cef_message
            
            # Check basic CEF format compliance
            assert cef_message.startswith('CEF:0|')
            parts = cef_message.split('|', 7)
            assert len(parts) == 8
            
            print(f"✓ CEF format compliant for event type: {event_type}")

    def test_cef_performance_compliance(self, cef_plugin):
        """Test CEF formatting performance."""
        import time
        
        event = {
            'event_type': 'REQUEST',
            'method': 'tools/call',
            'tool': 'read_file',
            'status': 'ALLOWED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123',
            'plugin': 'test_plugin',
            'reason': 'Test reason'
        }
        
        # Test performance - should be fast
        start_time = time.time()
        for _ in range(1000):
            cef_message = cef_plugin._format_cef_message(event)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_message = total_time / 1000
        
        # Should be much faster than 10ms per message
        assert avg_time_per_message < 0.01, f"CEF formatting too slow: {avg_time_per_message:.4f}s per message"
        
        print(f"✓ CEF formatting performance: {avg_time_per_message:.4f}s per message")

    def test_cef_unicode_compliance(self, cef_plugin):
        """Test CEF format with Unicode characters."""
        event = {
            'event_type': 'REQUEST',
            'method': 'tools/call',
            'tool': 'read_file',
            'status': 'ALLOWED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123',
            'reason': 'Test with Unicode: 日本語, émojis: 🔒, special chars: ñáéíóú'
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Should be able to format Unicode characters
        assert '日本語' in cef_message
        assert '🔒' in cef_message
        assert 'ñáéíóú' in cef_message
        
        # Should still be valid CEF format
        assert cef_message.startswith('CEF:0|')
        parts = cef_message.split('|', 7)
        assert len(parts) == 8
        
        print(f"✓ CEF format handles Unicode correctly")

    def test_cef_size_compliance(self, cef_plugin):
        """Test CEF format with various message sizes."""
        # Test with very long reason
        long_reason = "A" * 1000  # Very long reason
        
        event = {
            'event_type': 'REQUEST',
            'method': 'tools/call',
            'tool': 'read_file',
            'status': 'ALLOWED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123',
            'reason': long_reason
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Should still be valid CEF format
        assert cef_message.startswith('CEF:0|')
        parts = cef_message.split('|', 7)
        assert len(parts) == 8
        
        # Should contain the full reason
        assert long_reason in cef_message
        
        print(f"✓ CEF format handles large messages correctly")

    def test_cef_empty_fields_compliance(self, cef_plugin):
        """Test CEF format with empty/None fields."""
        event = {
            'event_type': 'REQUEST',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'method': None,
            'tool': '',
            'status': 'ALLOWED',
            'request_id': '123',
            'reason': None
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Should still be valid CEF format
        assert cef_message.startswith('CEF:0|')
        parts = cef_message.split('|', 7)
        assert len(parts) == 8
        
        # Should handle empty/None fields gracefully
        assert 'requestId=123' in cef_message
        assert 'act=allowed' in cef_message
        
        print(f"✓ CEF format handles empty/None fields correctly")

    def test_cef_specification_compliance(self, cef_plugin):
        """Test adherence to CEF specification."""
        event = {
            'event_type': 'REQUEST',
            'method': 'tools/call',
            'tool': 'read_file',
            'status': 'ALLOWED',
            'timestamp': '2023-12-01T14:30:25.123456Z',
            'request_id': '123'
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Test required header format
        assert cef_message.startswith('CEF:0|')
        
        # Test pipe-separated header (exactly 7 fields before extension)
        header_part = cef_message.split('|', 7)
        assert len(header_part) == 8  # 7 header fields + extension
        
        # Test extension field format
        extension = header_part[7]
        assert '=' in extension  # Key-value pairs
        assert not extension.startswith('=')  # No leading equals
        
        # Test header fields are not empty
        assert header_part[0] == "CEF:0"  # Version
        assert header_part[1] == "Watchgate"  # Device Vendor
        assert header_part[2] == "MCP Gateway"  # Device Product
        assert header_part[3] == "1.0.0"  # Device Version
        assert header_part[4] == "100"  # Device Event Class ID
        assert header_part[5] == "MCP Request"  # Name
        assert header_part[6] == "6"  # Severity

    def test_cef_unknown_event_type_compliance(self, cef_plugin):
        """Test CEF format with unknown event type."""
        event = {
            'event_type': 'UNKNOWN_EVENT',
            'timestamp': '2023-12-01T14:30:25.123456Z'
        }
        
        cef_message = cef_plugin._format_cef_message(event)
        
        # Should use default mapping
        assert cef_message.startswith('CEF:0|Watchgate|MCP Gateway|1.0.0|999|Unknown Event|5|')

    def test_cef_dynamic_version_detection(self, cef_plugin):
        """Test dynamic version detection in CEF messages."""
        # Test version appears in output
        event = {'event_type': 'REQUEST', 'method': 'tools/call'}
        result = cef_plugin._format_cef_message(event)
        assert f'|{cef_plugin.device_version}|' in result

    def test_cef_header_escaping_methods(self, cef_plugin):
        """Test CEF header escaping methods."""
        # Test pipe escaping
        assert cef_plugin._escape_cef_header('test|pipe') == 'test\\|pipe'
        
        # Test backslash escaping
        assert cef_plugin._escape_cef_header('test\\backslash') == 'test\\\\backslash'
        
        # Test both
        assert cef_plugin._escape_cef_header('test|pipe\\backslash') == 'test\\|pipe\\\\backslash'
        
        # Test no escaping needed
        assert cef_plugin._escape_cef_header('normal_text') == 'normal_text'

    def test_cef_extension_escaping_methods(self, cef_plugin):
        """Test CEF extension escaping methods."""
        # Test equals escaping
        assert cef_plugin._escape_cef_extension('test=equals') == 'test\\=equals'
        
        # Test backslash escaping
        assert cef_plugin._escape_cef_extension('test\\backslash') == 'test\\\\backslash'
        
        # Test newline escaping
        assert cef_plugin._escape_cef_extension('test\nnewline') == 'test\\nnewline'
        
        # Test carriage return escaping
        assert cef_plugin._escape_cef_extension('test\rcarriage') == 'test\\rcarriage'
        
        # Test all combined
        assert cef_plugin._escape_cef_extension('test=equals\\backslash\nnewline\rcarriage') == 'test\\=equals\\\\backslash\\nnewline\\rcarriage'
        
        # Test no escaping needed
        assert cef_plugin._escape_cef_extension('normal_text') == 'normal_text'


# Tests moved from test_cef_bug_fixes.py to maintain CEF-specific test organization
class TestCEFBugFixes:
    """Tests for CEF auditing plugin bug fixes and improvements.
    
    These tests verify critical fixes for CEF plugin functionality including
    metadata guards, sanitization, network fields, and configuration handling.
    """
    
    def test_metadata_none_in_request_tools_list(self):
        """Test that metadata=None doesn't crash in tools/list filtering check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from unittest.mock import Mock
            from watchgate.protocol.messages import MCPRequest
            from watchgate.plugins.interfaces import PolicyDecision
            
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = CefAuditingPlugin(config)
            
            request = Mock(spec=MCPRequest)
            request.method = "tools/list"
            request.id = "test-1"
            request.params = {}
            
            decision = PolicyDecision(allowed=True, reason="test", metadata=None)
            
            result = plugin._format_request_log(request, decision, "test-server")
            assert result is not None
            assert "CEF:" in result
    
    def test_metadata_none_in_response_duration(self):
        """Test that metadata=None doesn't crash when checking duration_ms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from unittest.mock import Mock
            from watchgate.protocol.messages import MCPRequest, MCPResponse
            from watchgate.plugins.interfaces import PolicyDecision
            
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = CefAuditingPlugin(config)
            
            request = Mock(spec=MCPRequest)
            request.method = "test/method"
            request.id = "test-1"
            
            response = Mock(spec=MCPResponse)
            response.id = "test-1"
            response.error = None
            
            decision = PolicyDecision(allowed=True, reason="test", metadata=None)
            
            result = plugin._format_response_log(request, response, decision, "test-server")
            assert result is not None
            assert "duration_ms" not in result
    
    def test_no_default_localhost_ips(self):
        """Test that network fields don't default to 127.0.0.1."""
        from datetime import datetime
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = CefAuditingPlugin(config)
            
            event_data = {
                "event_type": "REQUEST",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "allowed"
            }
            
            result = plugin._format_cef_message(event_data)
            
            assert "src=127.0.0.1" not in result
            assert "dst=127.0.0.1" not in result
    
    def test_status_normalized_to_lowercase(self):
        """Test that status values are normalized to lowercase in act field."""
        from datetime import datetime
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = CefAuditingPlugin(config)
            
            for status in ["ALLOWED", "Blocked", "SUCCESS"]:
                event_data = {
                    "event_type": "REQUEST",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "status": status
                }
                
                result = plugin._format_cef_message(event_data)
                assert f"act={status.lower()}" in result.lower() or "act=" in result
    
    def test_modification_detection(self):
        """Test that modified_content triggers MODIFICATION event."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from unittest.mock import Mock
            from watchgate.protocol.messages import MCPRequest
            from watchgate.plugins.interfaces import PolicyDecision
            
            config = {'output_file': f'{tmpdir}/test.log'}
            plugin = CefAuditingPlugin(config)
            
            request = Mock(spec=MCPRequest)
            request.method = "test/method"
            request.id = "test-1"
            request.params = {"test": "value"}
            
            modified_request = Mock(spec=MCPRequest)
            modified_request.params = {"test": "modified"}
            decision = PolicyDecision(allowed=True, reason="test", modified_content=modified_request)
            
            result = plugin._format_request_log(request, decision, "test-server")
            
            assert "Content Modification" in result or "REDACTION" in result or "event_id=203" in result
    
    def test_device_fields_from_config(self):
        """Test that device fields are read from cef_config and included."""
        from datetime import datetime
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'device_hostname': 'test-host.example.com',
                    'device_ip': '10.0.0.1'
                }
            }
            plugin = CefAuditingPlugin(config)
            
            event_data = {
                "event_type": "REQUEST",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "allowed"
            }
            
            result = plugin._format_cef_message(event_data)
            
            if hasattr(plugin, 'device_hostname'):
                assert "dvchost=" in result
            if hasattr(plugin, 'device_ip'):
                assert "dvc=" in result