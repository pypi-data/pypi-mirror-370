"""Validation tests for OpenTelemetry format compliance."""

import json
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from watchgate.plugins.auditing.opentelemetry import OtelAuditingPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestOtelCompliance:
    """Test OpenTelemetry specification compliance."""

    def test_otel_specification_compliance(self):
        """Test adherence to OTEL logging specification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.otel')
            config = {
                'output_file': log_file,
                'service_name': 'test-service',
                'service_version': '1.0.0'
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Create comprehensive test event
            event_data = {
                'event_type': 'REQUEST',
                'method': 'tools/call',
                'tool': 'read_file',
                'status': 'ALLOWED',
                'request_id': 'test-123',
                'plugin': 'test_plugin',
                'reason': 'Test reason',
                'duration_ms': 150,
                'server_name': 'test-server'
            }
            
            otel_json = plugin._format_otel_record(event_data)
            log_record = json.loads(otel_json)
            
            # Test required fields  
            assert 'time_unix_nano' in log_record
            assert 'body' in log_record
            
            # Test severity number range (1-24)
            severity_num = log_record['severity_number']
            assert 1 <= severity_num <= 24
            
            # Test resource attributes
            resource = log_record['resource']
            assert 'service.name' in resource
            assert 'service.version' in resource
            
            # Test attribute naming (should use semantic conventions)
            attributes = log_record['attributes']
            for key in attributes:
                assert key.startswith('watchgate.')  # Namespaced attributes

    def test_otel_timestamp_formats(self):
        """Test different timestamp precision formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_cases = [
                ('nanoseconds', 9),
                ('microseconds', 6),
                ('milliseconds', 3)
            ]
            
            for precision, expected_digits in test_cases:
                config = {
                    'output_file': os.path.join(tmpdir, f'test_{precision}.otel'),
                    'timestamp_precision': precision
                }
                
                plugin = OtelAuditingPlugin(config)
                formatted = plugin._format_timestamp_nano_from_ns(1701435025123456789)
                
                # Should be nanoseconds since Unix epoch (integer)
                assert isinstance(formatted, int)
                assert formatted > 0
                
                # Check precision by examining trailing zeros
                if precision == 'microseconds':
                    assert formatted % 1000 == 0  # Should end in 000
                elif precision == 'milliseconds':
                    assert formatted % 1_000_000 == 0  # Should end in 000000

    def test_otel_all_severity_levels(self):
        """Test all severity levels are within OTEL spec."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test all event types
            event_types = [
                'REQUEST', 'RESPONSE', 'SECURITY_BLOCK',
                'REDACTION', 'MODIFICATION', 'ERROR', 'UPSTREAM_ERROR',
                'NOTIFICATION', 'TOOLS_FILTERED', 'UNKNOWN'
            ]
            
            for event_type in event_types:
                severity_num = plugin._map_severity_number(event_type)
                severity_text = plugin._map_severity_text(event_type)
                
                # OTEL severity number must be 1-24
                assert 1 <= severity_num <= 24
                
                # OTEL severity text must be valid
                valid_severities = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
                assert severity_text in valid_severities

    def test_otel_resource_semantic_conventions(self):
        """Test resource attributes follow OTEL semantic conventions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'service_name': 'test-service',
                'service_version': '2.0.0',
                'service_namespace': 'test-namespace',
                'deployment_environment': 'staging'
            }
            
            plugin = OtelAuditingPlugin(config)
            resource = plugin._resource_attrs
            
            # Required service attributes
            assert 'service.name' in resource
            assert 'service.version' in resource
            
            # Optional but recommended attributes
            assert 'host.name' in resource
            assert 'process.pid' in resource
            
            # Telemetry SDK attributes
            assert 'telemetry.sdk.name' in resource
            assert 'telemetry.sdk.version' in resource
            assert 'telemetry.sdk.language' in resource
            
            # Check values
            assert resource['service.name'] == 'test-service'
            assert resource['service.version'] == '2.0.0'
            assert resource['telemetry.sdk.language'] == 'python'

    def test_otel_json_structure(self):
        """Test OTEL JSON structure is valid and complete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            event_data = {
                'event_type': 'REQUEST',
                'method': 'tools/call',
                'status': 'ALLOWED'
            }
            
            otel_json = plugin._format_otel_record(event_data)
            
            # Should be valid JSON
            log_record = json.loads(otel_json)
            
            # Check all required OTEL fields exist
            required_fields = [
                'time_unix_nano', 'observed_time_unix_nano', 'severity_text',
                'severity_number', 'body', 'attributes', 'resource'
            ]
            
            for field in required_fields:
                assert field in log_record, f"Missing required field: {field}"
            
            # Check types
            assert isinstance(log_record['time_unix_nano'], int)
            assert isinstance(log_record['severity_number'], int)
            assert isinstance(log_record['attributes'], dict)
            assert isinstance(log_record['resource'], dict)

    @pytest.mark.asyncio
    async def test_otel_with_response_logging(self):
        """Test OTEL format with response logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.otel')
            config = {
                'output_file': log_file,
                'service_name': 'test-service'
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Create test request and response
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/list',
                params={},
                id='test-456'
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                result={'tools': [{'name': 'read_file'}]},
                id='test-456'
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Response approved',
                metadata={'duration_ms': 25}
            )
            
            # Log the response
            await plugin.log_response(request, response, decision, "test-server")
            
            # Verify log output
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
                
            log_record = json.loads(log_content)
            
            # Verify OTEL structure for response
            assert log_record['severity_text'] == 'INFO'
            assert log_record['attributes']['watchgate.event_type'] == 'RESPONSE'
            assert log_record['attributes']['watchgate.duration_ms'] == 25
            assert 'MCP tools/list response' in log_record['body']

    @pytest.mark.asyncio
    async def test_otel_with_notification_logging(self):
        """Test OTEL format with notification logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.otel')
            config = {
                'output_file': log_file,
                'include_trace_correlation': False  # Disable for simpler test
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Create test notification
            notification = MCPNotification(
                jsonrpc="2.0",
                method='notifications/progress',
                params={'progress': 0.5}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Notification allowed'
            )
            
            # Log the notification
            await plugin.log_notification(notification, decision, "test-server")
            
            # Verify log output
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
                
            log_record = json.loads(log_content)
            
            # Verify OTEL structure for notification
            assert log_record['severity_text'] == 'INFO'
            assert log_record['attributes']['watchgate.event_type'] == 'NOTIFICATION'
            assert log_record['attributes']['watchgate.method'] == 'notifications/progress'
            assert 'trace_id' not in log_record  # Should not have trace correlation

    def test_otel_trace_id_format(self):
        """Test trace ID format compliance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Generate multiple trace IDs
            for _ in range(10):
                trace_id = plugin._generate_trace_id()
                
                # Should be 32-character hex string (16 bytes)
                assert len(trace_id) == 32
                assert all(c in '0123456789abcdef' for c in trace_id.lower())
                
                # Should not be all zeros
                assert trace_id != '00000000000000000000000000000000'

    def test_otel_span_id_format(self):
        """Test span ID format compliance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Generate multiple span IDs
            for _ in range(10):
                span_id = plugin._generate_span_id()
                
                # Should be 16-character hex string (8 bytes)
                assert len(span_id) == 16
                assert all(c in '0123456789abcdef' for c in span_id.lower())
                
                # Should not be all zeros
                assert span_id != '0000000000000000'


class TestOtelIntegration:
    """Test OpenTelemetry plugin integration with Watchgate."""

    @pytest.mark.asyncio
    async def test_otel_plugin_lifecycle(self):
        """Test OTEL plugin full lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.otel')
            config = {
                'output_file': log_file,
                'service_name': 'integration-test',
                'service_version': '1.0.0',
                'include_trace_correlation': True
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test plugin initialization
            assert plugin.service_name == 'integration-test'
            assert plugin.service_version == '1.0.0'
            assert plugin.include_trace_correlation is True
            
            # Create test events
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={'name': 'test_tool', 'arguments': {}},
                id='integration-test-1'
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Integration test',
                metadata={
                    'plugin': 'integration_plugin',
                    'trace_context': {
                        'trace_id': '1234567890abcdef1234567890abcdef',
                        'span_id': '1234567890abcdef'
                    }
                }
            )
            
            # Log request
            await plugin.log_request(request, decision, "integration-server")
            
            # Verify the log was written
            assert os.path.exists(log_file)
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
            
            log_record = json.loads(log_content)
            
            # Verify integration-specific fields
            assert log_record['resource']['service.name'] == 'integration-test'
            assert log_record['attributes']['watchgate.plugin'] == 'integration_plugin'
            assert log_record['trace_id'] == '1234567890abcdef1234567890abcdef'
            assert log_record['span_id'] == '1234567890abcdef'

    def test_otel_configuration_edge_cases(self):
        """Test OTEL configuration edge cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with minimal config
            minimal_config = {
                'output_file': os.path.join(tmpdir, 'minimal.otel')
            }
            
            plugin = OtelAuditingPlugin(minimal_config)
            assert plugin.service_name == 'watchgate'  # Default
            assert plugin.timestamp_precision == 'nanoseconds'  # Default
            
            # Test with empty resource attributes
            empty_attrs_config = {
                'output_file': os.path.join(tmpdir, 'empty.otel'),
                'resource_attributes': {}
            }
            
            plugin = OtelAuditingPlugin(empty_attrs_config)
            resource = plugin._resource_attrs
            assert 'service.name' in resource  # Should still have defaults
            
            # Test with additional resource attributes
            extra_attrs_config = {
                'output_file': os.path.join(tmpdir, 'extra.otel'),
                'resource_attributes': {
                    'custom.attribute': 'test-value',
                    'deployment.region': 'us-west-2'
                }
            }
            
            plugin = OtelAuditingPlugin(extra_attrs_config)
            resource = plugin._resource_attrs
            assert resource['custom.attribute'] == 'test-value'
            assert resource['deployment.region'] == 'us-west-2'

    def test_otel_error_handling(self):
        """Test OTEL plugin error handling scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'error_test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test with malformed event data
            malformed_data = {
                'event_type': None,  # Invalid
                'method': 123,       # Wrong type
                'status': []         # Wrong type
            }
            
            # Should handle gracefully without crashing
            result = plugin._format_otel_record(malformed_data)
            log_record = json.loads(result)
            
            # Should have defaults or safe conversions
            assert 'time_unix_nano' in log_record
            assert 'body' in log_record
            assert log_record['severity_text'] == 'INFO'  # Default for None event_type