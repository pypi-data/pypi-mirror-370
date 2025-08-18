"""Tests for OpenTelemetry auditing plugin."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone

from watchgate.plugins.auditing.opentelemetry import OtelAuditingPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestOtelAuditingPlugin:
    """Test OpenTelemetry auditing plugin."""

    def test_otel_plugin_initialization(self):
        """Test OTEL auditing plugin initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'service_name': 'test-service',
                'service_version': '1.0.0'
            }
            
            plugin = OtelAuditingPlugin(config)
            assert plugin.service_name == 'test-service'
            assert plugin.service_version == '1.0.0'
            assert plugin.service_namespace == 'watchgate'  # default
            assert plugin.include_trace_correlation is True  # default

    def test_otel_plugin_initialization_defaults(self):
        """Test OTEL auditing plugin initialization with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            assert plugin.service_name == 'watchgate'
            assert plugin.service_version is not None  # Should auto-detect
            assert plugin.service_namespace == 'watchgate'
            assert plugin.deployment_environment == 'production'

    def test_otel_plugin_initialization_invalid_config(self):
        """Test OTEL auditing plugin initialization with invalid config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'timestamp_precision': 'invalid'
            }
            
            with pytest.raises(ValueError, match="timestamp_precision must be one of"):
                OtelAuditingPlugin(config)

    @pytest.mark.asyncio
    async def test_otel_log_request_basic(self):
        """Test basic OTEL request logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.otel')
            config = {
                'output_file': log_file,
                'service_name': 'test-service',
                'service_version': '1.0.0'
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Create test request
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={'name': 'read_file', 'arguments': {'path': '/test.txt'}},
                id='test-123'
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Request approved',
                metadata={'plugin': 'test_plugin'}
            )
            
            # Log the request
            await plugin.log_request(request, decision, "test-server")
            
            # Verify log output
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
                
            log_record = json.loads(log_content)
            
            # Verify OTEL structure
            assert 'time_unix_nano' in log_record
            assert 'observed_time_unix_nano' in log_record
            assert 'severity_text' in log_record
            assert 'severity_number' in log_record
            assert 'body' in log_record
            assert 'attributes' in log_record
            assert 'resource' in log_record
            
            # Verify content
            assert log_record['severity_text'] == 'INFO'
            assert log_record['severity_number'] == 9
            assert 'MCP tools/call request' in log_record['body']
            assert log_record['attributes']['watchgate.event_type'] == 'REQUEST'
            assert log_record['attributes']['watchgate.method'] == 'tools/call'
            assert log_record['attributes']['watchgate.tool'] == 'read_file'
            assert log_record['attributes']['watchgate.status'] == 'ALLOWED'
            assert log_record['attributes']['watchgate.request_id'] == 'test-123'
            assert log_record['resource']['service.name'] == 'test-service'
            assert log_record['resource']['service.version'] == '1.0.0'


class TestOtelFormatting:
    """Test OTEL formatting methods."""

    def test_timestamp_formatting_nanoseconds(self):
        """Test OTEL timestamp formatting with nanosecond precision."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'timestamp_precision': 'nanoseconds'
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test with timestamp in nanoseconds
            timestamp_ns = 1701435025123456789
            formatted = plugin._format_timestamp_nano_from_ns(timestamp_ns)
            
            # Should be nanoseconds since Unix epoch (integer)
            assert isinstance(formatted, int)
            # Should preserve nanosecond precision
            assert formatted == timestamp_ns

    def test_timestamp_formatting_microseconds(self):
        """Test OTEL timestamp formatting with microsecond precision."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'timestamp_precision': 'microseconds'
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test with timestamp in nanoseconds  
            timestamp_ns = 1701435025123456000  # Already at microsecond precision
            formatted = plugin._format_timestamp_nano_from_ns(timestamp_ns)
            
            # Should be nanoseconds since Unix epoch truncated to microsecond precision
            assert isinstance(formatted, int)
            # Should truncate to microsecond precision (last 3 digits should be 0)
            assert formatted % 1000 == 0

    def test_severity_mapping(self):
        """Test event type to OTEL severity mapping."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test different event types
            assert plugin._map_severity_text('REQUEST') == 'INFO'
            assert plugin._map_severity_number('REQUEST') == 9
            
            assert plugin._map_severity_text('RESPONSE') == 'INFO'
            assert plugin._map_severity_number('RESPONSE') == 9
            
            assert plugin._map_severity_text('SECURITY_BLOCK') == 'WARN'
            assert plugin._map_severity_number('SECURITY_BLOCK') == 13
            
            assert plugin._map_severity_text('REDACTION') == 'WARN'
            assert plugin._map_severity_number('REDACTION') == 13
            
            assert plugin._map_severity_text('ERROR') == 'ERROR'
            assert plugin._map_severity_number('ERROR') == 17
            
            assert plugin._map_severity_text('UPSTREAM_ERROR') == 'ERROR'
            assert plugin._map_severity_number('UPSTREAM_ERROR') == 17
            
            assert plugin._map_severity_text('NOTIFICATION') == 'INFO'
            assert plugin._map_severity_number('NOTIFICATION') == 9
            
            assert plugin._map_severity_text('TOOLS_FILTERED') == 'DEBUG'
            assert plugin._map_severity_number('TOOLS_FILTERED') == 5
            
            # Test unknown event type (should default to INFO)
            assert plugin._map_severity_text('UNKNOWN') == 'INFO'
            assert plugin._map_severity_number('UNKNOWN') == 9

    def test_body_formatting(self):
        """Test log message body formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test REQUEST
            body = plugin._format_body('REQUEST', 'tools/call', 'ALLOWED', 'Test reason')
            assert body == 'MCP tools/call request - ALLOWED'
            
            # Test RESPONSE
            body = plugin._format_body('RESPONSE', 'tools/list', 'SUCCESS', None)
            assert body == 'MCP tools/list response - SUCCESS'
            
            # Test SECURITY_BLOCK
            body = plugin._format_body('SECURITY_BLOCK', 'tools/call', 'BLOCKED', 'Unauthorized tool')
            assert body == 'Security block: Unauthorized tool'
            
            # Test unknown event type
            body = plugin._format_body('UNKNOWN', 'tools/call', 'ALLOWED', None)
            assert body == 'UNKNOWN: tools/call - ALLOWED'

    def test_attributes_formatting(self):
        """Test OTEL attributes formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
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
            
            attributes = plugin._format_attributes(event_data)
            
            expected_attributes = {
                'watchgate.event_type': 'REQUEST',
                'watchgate.method': 'tools/call',
                'watchgate.tool': 'read_file',
                'watchgate.status': 'ALLOWED',
                'watchgate.request_id': 'test-123',
                'watchgate.plugin': 'test_plugin',
                'watchgate.reason': 'Test reason',
                'watchgate.duration_ms': 150,
                'watchgate.server_name': 'test-server'
            }
            
            assert attributes == expected_attributes

    def test_resource_attributes(self):
        """Test OTEL resource attributes formatting."""
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
            
            # Verify required attributes
            assert resource['service.name'] == 'test-service'
            assert resource['service.version'] == '2.0.0'
            assert resource['service.namespace'] == 'test-namespace'
            assert resource['deployment.environment'] == 'staging'
            assert 'host.name' in resource
            assert 'process.pid' in resource
            assert resource['telemetry.sdk.name'] == 'watchgate'
            assert resource['telemetry.sdk.version'] == '2.0.0'
            assert resource['telemetry.sdk.language'] == 'python'

    def test_trace_correlation_enabled(self):
        """Test trace correlation when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'include_trace_correlation': True
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test with trace context in metadata
            metadata = {
                'trace_context': {
                    'trace_id': '5b8efff798038103d269b633813fc60c',
                    'span_id': 'eee19b7ec3c1b174'
                }
            }
            
            trace_context = plugin._get_trace_context(metadata)
            
            assert trace_context is not None
            assert trace_context['trace_id'] == '5b8efff798038103d269b633813fc60c'
            assert trace_context['span_id'] == 'eee19b7ec3c1b174'

    def test_trace_correlation_disabled(self):
        """Test trace correlation when disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'include_trace_correlation': False
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Test with trace context in metadata (should be ignored)
            metadata = {
                'trace_context': {
                    'trace_id': '5b8efff798038103d269b633813fc60c',
                    'span_id': 'eee19b7ec3c1b174'
                }
            }
            
            trace_context = plugin._get_trace_context(metadata)
            
            assert trace_context is None

    def test_trace_id_generation(self):
        """Test trace ID generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            trace_id = plugin._generate_trace_id()
            
            # Should be 32-character hex string (16 bytes)
            assert len(trace_id) == 32
            assert all(c in '0123456789abcdef' for c in trace_id.lower())

    def test_span_id_generation(self):
        """Test span ID generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel')
            }
            
            plugin = OtelAuditingPlugin(config)
            
            span_id = plugin._generate_span_id()
            
            # Should be 16-character hex string (8 bytes)
            assert len(span_id) == 16
            assert all(c in '0123456789abcdef' for c in span_id.lower())

    def test_response_modification_vs_redaction_classification(self):
        """Test response modification vs redaction event classification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': os.path.join(tmpdir, 'test.otel')}
            plugin = OtelAuditingPlugin(config)
            
            request = MCPRequest(jsonrpc="2.0", method='tools/call', params={'name': 'test'}, id='1')
            response = MCPResponse(jsonrpc="2.0", result={'data': 'modified'}, id='1')
            
            # Test MODIFICATION (no "redact" in reason)
            decision_mod = PolicyDecision(allowed=True, reason="Content sanitized for safety", modified_content=response)
            log_entry = plugin._format_response_log(request, response, decision_mod, "test-server")
            log_data = json.loads(log_entry)
            assert log_data['attributes']['watchgate.event_type'] == 'MODIFICATION'
            
            # Test REDACTION ("redact" in reason) 
            decision_red = PolicyDecision(allowed=True, reason="PII redacted from response", modified_content=response)
            log_entry = plugin._format_response_log(request, response, decision_red, "test-server")
            log_data = json.loads(log_entry)
            assert log_data['attributes']['watchgate.event_type'] == 'REDACTION'

    def test_auto_generated_trace_context(self):
        """Test automatic trace context generation when correlation enabled but not provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'include_trace_correlation': True
            }
            plugin = OtelAuditingPlugin(config)
            
            event_data = {'event_type': 'REQUEST', 'method': 'tools/call'}
            log_record_str = plugin._format_otel_record(event_data)
            log_record = json.loads(log_record_str)
            
            assert 'trace_id' in log_record, "Should have auto-generated trace_id"
            assert 'span_id' in log_record, "Should have auto-generated span_id"
            assert len(log_record['trace_id']) == 32, "Trace ID should be 32 hex chars"
            assert len(log_record['span_id']) == 16, "Span ID should be 16 hex chars"

    def test_tool_unknown_restricted_to_tools_call(self):
        """Test tool='unknown' logic is restricted to tools/call methods only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': os.path.join(tmpdir, 'test.otel')}
            plugin = OtelAuditingPlugin(config)
            
            decision_block = PolicyDecision(allowed=False, reason="Blocked")
            
            # Non-tools/call security block should not get tool="unknown"
            request_list = MCPRequest(jsonrpc="2.0", method='tools/list', params={}, id='2')
            log_entry = plugin._format_request_log(request_list, decision_block, "test-server")
            log_data = json.loads(log_entry)
            assert 'watchgate.tool' not in log_data['attributes'], "Non-tools/call should not get tool field"
            
            # tools/call security block should get tool="unknown" when no name param
            request_call = MCPRequest(jsonrpc="2.0", method='tools/call', params={}, id='3')
            log_entry = plugin._format_request_log(request_call, decision_block, "test-server")
            log_data = json.loads(log_entry)
            assert log_data['attributes']['watchgate.tool'] == 'unknown'

    def test_service_instance_id_in_resource(self):
        """Test service.instance.id is included in resource attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': os.path.join(tmpdir, 'test.otel')}
            plugin = OtelAuditingPlugin(config)
            
            resource = plugin._resource_attrs
            assert 'service.instance.id' in resource
            instance_id = resource['service.instance.id']
            assert '-' in instance_id, "Should be hostname-pid format"

    def test_json_serialization_error_handling(self):
        """Test fallback behavior when JSON serialization fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': os.path.join(tmpdir, 'test.otel')}
            plugin = OtelAuditingPlugin(config)
            
            # Force serialization error by patching json.dumps
            original_dumps = json.dumps
            def failing_dumps(*args, **kwargs):
                if 'watchgate.error' not in str(args):  # Allow fallback record
                    raise TypeError("Mock serialization error")
                return original_dumps(*args, **kwargs)
            
            json.dumps = failing_dumps
            try:
                fallback_record_str = plugin._format_otel_record({'event_type': 'TEST'})
                fallback_record = json.loads(fallback_record_str)
                assert fallback_record['attributes']['watchgate.error'] == 'serialization_failed'
                assert 'OTEL serialization error' in fallback_record['body']
                assert fallback_record['severity_text'] == 'ERROR'
            finally:
                json.dumps = original_dumps

    def test_metadata_sanitization_and_collision_protection(self):
        """Test metadata sanitization and core field collision protection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'max_string_length': 50
            }
            plugin = OtelAuditingPlugin(config)
            
            class NonSerializable:
                def __str__(self):
                    return "NonSerializableObject"
            
            request = MCPRequest(jsonrpc="2.0", method='tools/call', params={'name': 'test'}, id='1')
            decision = PolicyDecision(
                allowed=True,
                reason="Test reason",
                metadata={
                    "plugin": "should_be_filtered",  # Core field - should be filtered
                    "non_serializable": NonSerializable(),
                    "long_string": "x" * 100,  # Will be truncated
                    "normal_field": "normal_value"
                }
            )
            
            log_entry = plugin._format_request_log(request, decision, "test-server")
            log_data = json.loads(log_entry)
            attributes = log_data['attributes']
            
            # Core field protection - plugin metadata should be filtered out
            assert 'watchgate.metadata.plugin' not in attributes
            
            # Non-serializable handling
            assert 'watchgate.metadata.non_serializable' in attributes
            non_ser_val = attributes['watchgate.metadata.non_serializable']
            assert non_ser_val.startswith('[CONVERTED]')
            
            # String truncation
            assert 'watchgate.metadata.long_string' in attributes
            long_val = attributes['watchgate.metadata.long_string']
            assert long_val.endswith('...')
            assert len(long_val) <= 53  # 50 + '...'
            
            # Normal field preserved
            assert attributes['watchgate.metadata.normal_field'] == 'normal_value'

    def test_reason_processing_truncation_and_redaction(self):
        """Test reason text processing with truncation and redaction options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test truncation
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'max_reason_length': 20
            }
            plugin = OtelAuditingPlugin(config)
            
            long_reason = "This is a very long reason that should be truncated"
            processed = plugin._process_reason(long_reason)
            assert processed.endswith('...')
            assert len(processed) <= 23  # 20 + '...'
            
            # Test redaction
            config_redacted = config.copy()
            config_redacted['redact_reason'] = True
            plugin_redacted = OtelAuditingPlugin(config_redacted)
            
            redacted = plugin_redacted._process_reason("Secret information")
            # Redacted reasons now include hash for audit reconciliation
            assert redacted.startswith('[REDACTED:hash:')
            assert redacted.endswith(']')
            assert len(redacted) == 32  # [REDACTED:hash: + 16 hex chars + ]

    def test_configurable_redaction_keywords(self):
        """Test configurable redaction keywords for MODIFICATION vs REDACTION classification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'redaction_keywords': ['hide', 'mask', 'obfuscate']
            }
            plugin = OtelAuditingPlugin(config)
            
            request = MCPRequest(jsonrpc="2.0", method='tools/call', params={'name': 'test'}, id='1')
            
            # Test with configured redaction keyword
            decision_hide = PolicyDecision(allowed=True, reason="Data was masked for security", modified_content=request)
            log_entry = plugin._format_request_log(request, decision_hide, "test-server")
            log_data = json.loads(log_entry)
            assert log_data['attributes']['watchgate.event_type'] == 'REDACTION'
            
            # Test with non-redaction keyword
            decision_clean = PolicyDecision(allowed=True, reason="Content was sanitized", modified_content=request)
            log_entry = plugin._format_request_log(request, decision_clean, "test-server")
            log_data = json.loads(log_entry)
            assert log_data['attributes']['watchgate.event_type'] == 'MODIFICATION'

    def test_service_instance_uid_uniqueness(self):
        """Test service.instance.uid is unique per plugin instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': os.path.join(tmpdir, 'test.otel')}
            
            plugin1 = OtelAuditingPlugin(config)
            plugin2 = OtelAuditingPlugin(config)
            
            uid1 = plugin1._resource_attrs['service.instance.uid']
            uid2 = plugin2._resource_attrs['service.instance.uid']
            
            assert uid1 != uid2, "Each plugin instance should have unique UID"
            assert len(uid1) == 36, "Should be UUID format"
            assert len(uid2) == 36, "Should be UUID format"

    def test_attribute_enrichment_hook(self):
        """Test optional attribute enrichment hook for extensibility."""
        with tempfile.TemporaryDirectory() as tmpdir:
            def enrichment_hook(attributes, event_data):
                return {
                    'custom.field': 'enriched_value',
                    'custom.method': event_data.get('method', 'unknown')
                }
            
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'attribute_enrichment_hook': enrichment_hook
            }
            plugin = OtelAuditingPlugin(config)
            
            event_data = {'event_type': 'REQUEST', 'method': 'tools/call'}
            log_record_str = plugin._format_otel_record(event_data)
            log_record = json.loads(log_record_str)
            
            attributes = log_record['attributes']
            assert attributes['custom.field'] == 'enriched_value'
            assert attributes['custom.method'] == 'tools/call'

    def test_attribute_enrichment_hook_error_handling(self):
        """Test attribute enrichment hook error handling doesn't break audit pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            def failing_hook(attributes, event_data):
                raise Exception("Hook failure")
            
            config = {
                'output_file': os.path.join(tmpdir, 'test.otel'),
                'attribute_enrichment_hook': failing_hook
            }
            plugin = OtelAuditingPlugin(config)
            
            # Should not raise exception despite hook failure
            event_data = {'event_type': 'REQUEST', 'method': 'tools/call'}
            log_record_str = plugin._format_otel_record(event_data)
            log_record = json.loads(log_record_str)
            
            # Should still have basic attributes
            assert 'watchgate.event_type' in log_record['attributes']