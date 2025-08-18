"""Tests for CEF formatter module."""

import pytest
from datetime import datetime
from unittest.mock import patch
from watchgate.plugins.auditing.common_event_format import CefAuditingPlugin, CEF_EVENT_MAPPINGS, DEFAULT_CEF_EVENT_MAPPING


class TestCEFFormatter:
    """Test the CEF formatter functionality in CefAuditingPlugin."""

    def test_cef_plugin_initialization(self):
        """Test CEF plugin initialization with default values."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            assert plugin.cef_version == "0"
            assert plugin.device_vendor == "Watchgate"
            assert plugin.device_product == "MCP Gateway"
            assert plugin.device_version != "unknown"  # Should get actual version

    def test_cef_plugin_initialization_with_custom_version(self):
        """Test CEF plugin initialization with custom version."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'device_version': '2.0.0'
                }
            }
            plugin = CefAuditingPlugin(config)
            assert plugin.device_version == "2.0.0"

    def test_cef_plugin_initialization_with_custom_vendor(self):
        """Test CEF plugin initialization with custom vendor."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'device_vendor': 'CustomVendor'
                }
            }
            plugin = CefAuditingPlugin(config)
            assert plugin.device_vendor == "CustomVendor"
            assert plugin.device_product == "MCP Gateway"  # Default

    def test_cef_plugin_initialization_with_custom_product(self):
        """Test CEF plugin initialization with custom product."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'device_product': 'CustomProduct'
                }
            }
            plugin = CefAuditingPlugin(config)
            assert plugin.device_vendor == "Watchgate"  # Default
            assert plugin.device_product == "CustomProduct"

    def test_cef_plugin_initialization_with_all_custom(self):
        """Test CEF plugin initialization with all custom parameters."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'device_version': '3.0.0',
                    'device_vendor': 'TestVendor',
                    'device_product': 'TestProduct'
                }
            }
            plugin = CefAuditingPlugin(config)
            assert plugin.device_version == "3.0.0"
            assert plugin.device_vendor == "TestVendor"
            assert plugin.device_product == "TestProduct"

    def test_cef_header_escaping(self):
        """Test header field escaping."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            # Test pipe escaping
            assert plugin._escape_cef_header('test|pipe') == 'test\\|pipe'
            
            # Test backslash escaping (always first)
            assert plugin._escape_cef_header('test\\back') == 'test\\\\back'
            
            # Test combined escaping (backslash must be escaped first)
            assert plugin._escape_cef_header('test\\|combo') == 'test\\\\\\|combo'
            
            # Test no escaping needed
            assert plugin._escape_cef_header('test_normal') == 'test_normal'

    def test_cef_extension_escaping(self):
        """Test extension field escaping."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            # Test backslash escaping (always first)
            assert plugin._escape_cef_extension('test\\back') == 'test\\\\back'
            
            # Test equals escaping
            assert plugin._escape_cef_extension('test=equals') == 'test\\=equals'
            
            # Test newline escaping
            assert plugin._escape_cef_extension('test\nnewline') == 'test\\nnewline'
            assert plugin._escape_cef_extension('test\r\nwindows') == 'test\\r\\nwindows'
            
            # Test combined escaping (backslash must be escaped first)
            assert plugin._escape_cef_extension('test\\=combo\n') == 'test\\\\\\=combo\\n'
            
            # Test no escaping needed
            assert plugin._escape_cef_extension('test_normal') == 'test_normal'

    def test_format_cef_message_basic(self):
        """Test basic CEF message formatting."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            event_data = {
                'event_type': 'REQUEST',
                'timestamp': '2024-01-15T10:30:45.123Z',
                'source_ip': '192.168.1.100',
                'request_id': 'req-123',
                'method': 'tools/call',
                'tool': 'read_file',
                'server_name': 'test_server'
            }
            
            cef_message = plugin._format_cef_message(event_data)
            
            # Check CEF format structure
            assert cef_message.startswith('CEF:')
            assert '|Watchgate|MCP Gateway|' in cef_message
            assert '|100|MCP Request|6|' in cef_message  # Event ID and severity for REQUEST
            
            # Check extensions
            assert 'src=192.168.1.100' in cef_message
            assert 'requestId=req-123' in cef_message
            assert 'requestMethod=tools/call' in cef_message

    def test_format_cef_message_with_escaping(self):
        """Test CEF message formatting with special characters."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            event_data = {
                'event_type': 'SECURITY_BLOCK',
                'timestamp': '2024-01-15T10:30:45.123Z',
                'plugin': 'test|plugin',
                'reason': 'Blocked due to = suspicious\nactivity',
                'request_id': 'req-456'
            }
            
            cef_message = plugin._format_cef_message(event_data)
            
            # Check escaping in message
            assert 'reason=Blocked due to \\= suspicious\\nactivity' in cef_message
            assert 'sourceUserName=test\\|plugin' in cef_message

    def test_format_cef_message_with_null_value(self):
        """Test CEF message formatting with null/None values."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'null_value': 'N/A'
                }
            }
            plugin = CefAuditingPlugin(config)
            
            event_data = {
                'event_type': 'REQUEST',
                'timestamp': '2024-01-15T10:30:45.123Z',
                'source_ip': None,
                'request_id': 'req-789',
                'method': 'initialize'
            }
            
            cef_message = plugin._format_cef_message(event_data)
            
            # Check null value handling - network fields should be omitted when None
            assert 'src=' not in cef_message  # Should not include src field at all when None

    def test_format_cef_message_unknown_event_type(self):
        """Test CEF message formatting with unknown event type."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            event_data = {
                'event_type': 'UNKNOWN_EVENT',
                'timestamp': '2024-01-15T10:30:45.123Z',
                'request_id': 'req-999'
            }
            
            cef_message = plugin._format_cef_message(event_data)
            
            # Should use default mapping
            assert '|999|Unknown Event|5|' in cef_message  # Default event ID and severity

    def test_format_cef_message_all_event_types(self):
        """Test CEF formatting for all known event types."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            for event_type, mapping in CEF_EVENT_MAPPINGS.items():
                event_data = {
                    'event_type': event_type,
                    'timestamp': '2024-01-15T10:30:45.123Z',
                    'request_id': f'req-{event_type}'
                }
                
                cef_message = plugin._format_cef_message(event_data)
                
                # Check event mapping is correct
                expected_str = f"|{mapping['event_id']}|{mapping['name']}|{mapping['severity']}|"
                assert expected_str in cef_message, f"Event type {event_type} not formatted correctly"

    def test_cef_extension_field_mappings(self):
        """Test CEF extension field mappings."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            event_data = {
                'event_type': 'REQUEST',
                'timestamp': '2024-01-15T10:30:45.123Z',
                'source_ip': '10.0.0.1',
                'destination_ip': '10.0.0.2',
                'plugin': 'security_plugin',
                'user': 'test_user',
                'request_id': 'req-ext',
                'method': 'tools/list',
                'server_name': 'upstream_server',
                'duration_ms': 150,
                'tool': 'write_file',
                'args': {'path': '/tmp/test.txt'}
            }
            
            cef_message = plugin._format_cef_message(event_data)
            
            # Check field mappings
            assert 'src=10.0.0.1' in cef_message
            assert 'dst=10.0.0.2' in cef_message
            assert 'sourceUserName=security_plugin' in cef_message
            assert 'duser=test_user' in cef_message
            assert 'requestId=req-ext' in cef_message
            assert 'requestMethod=tools/list' in cef_message
            assert 'destinationServiceName=upstream_server' in cef_message
            assert 'duration=150' in cef_message
            assert 'fileName=write_file' in cef_message
            assert 'msg=' in cef_message and '/tmp/test.txt' in cef_message

    def test_cef_timestamp_formatting(self):
        """Test different timestamp formats in CEF."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log'
            }
            plugin = CefAuditingPlugin(config)
            
            # Test ISO format
            event_data = {
                'event_type': 'REQUEST',
                'timestamp': '2024-01-15T10:30:45.123Z',
                'request_id': 'req-time'
            }
            
            cef_message = plugin._format_cef_message(event_data)
            assert 'rt=Jan 15 2024 10:30:45' in cef_message

    @patch('watchgate.plugins.auditing.common_event_format.get_watchgate_version')
    def test_cef_auto_version_detection(self, mock_get_version):
        """Test automatic version detection."""
        import tempfile
        mock_get_version.return_value = "1.2.3"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'cef_config': {
                    'device_version': 'auto'
                }
            }
            plugin = CefAuditingPlugin(config)
            assert plugin.device_version == "1.2.3"

    def test_cef_config_validation(self):
        """Test CEF configuration validation."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test empty vendor
            with pytest.raises(ValueError, match="device_vendor must be a non-empty string"):
                config = {
                    'output_file': f'{tmpdir}/test.log',
                    'format': 'cef',
                    'cef_config': {
                        'device_vendor': ''
                    }
                }
                CefAuditingPlugin(config)
            
            # Test empty product
            with pytest.raises(ValueError, match="device_product must be a non-empty string"):
                config = {
                    'output_file': f'{tmpdir}/test.log',
                    'format': 'cef',
                    'cef_config': {
                        'device_product': ''
                    }
                }
                CefAuditingPlugin(config)
            
            # Test invalid compliance_tags type
            with pytest.raises(ValueError, match="compliance_tags must be a list"):
                config = {
                    'output_file': f'{tmpdir}/test.log',
                    'format': 'cef',
                    'cef_config': {
                        'compliance_tags': 'not_a_list'
                    }
                }
                CefAuditingPlugin(config)