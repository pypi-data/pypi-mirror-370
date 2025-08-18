"""Integration tests for OpenTelemetry auditing plugin."""

import pytest
import json
import tempfile
import os
from pathlib import Path

from watchgate.plugins.auditing.opentelemetry import OtelAuditingPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse


class TestOtelIntegration:
    """Test OpenTelemetry auditing plugin integration."""

    @pytest.mark.asyncio
    async def test_otel_end_to_end_logging(self):
        """Test end-to-end OTEL logging workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'integration.otel')
            config = {
                'output_file': log_file,
                'service_name': 'watchgate-integration',
                'service_version': '1.0.0',
                'service_namespace': 'testing',
                'deployment_environment': 'integration',
                'include_trace_correlation': True,
                'timestamp_precision': 'nanoseconds',
                'resource_attributes': {
                    'test.suite': 'integration',
                    'test.case': 'end_to_end'
                }
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Simulate a complete request-response cycle
            
            # 1. Log a request
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={
                    'name': 'integration_tool',
                    'arguments': {'input': 'test_data'}
                },
                id='integration-123'
            )
            
            request_decision = PolicyDecision(
                allowed=True,
                reason='Integration test request approved',
                metadata={
                    'plugin': 'integration_security_plugin',
                    'trace_context': {
                        'trace_id': 'abcdef1234567890abcdef1234567890',
                        'span_id': 'abcdef1234567890'
                    }
                }
            )
            
            await plugin.log_request(request, request_decision, "integration-server")
            
            # 2. Log a successful response
            response = MCPResponse(
                jsonrpc="2.0",
                result={'output': 'integration_result', 'status': 'success'},
                id='integration-123'
            )
            
            response_decision = PolicyDecision(
                allowed=True,
                reason='Integration test response approved',
                metadata={
                    'duration_ms': 150,
                    'plugin': 'integration_response_plugin'
                }
            )
            
            await plugin.log_response(request, response, response_decision, "integration-server")
            
            # Verify both log entries were written
            assert os.path.exists(log_file)
            
            with open(log_file, 'r') as f:
                log_lines = [line.strip() for line in f.readlines() if line.strip()]
            
            assert len(log_lines) == 2  # Request + Response
            
            # Parse and verify request log
            request_log = json.loads(log_lines[0])
            
            assert request_log['severity_text'] == 'INFO'
            assert request_log['attributes']['watchgate.event_type'] == 'REQUEST'
            assert request_log['attributes']['watchgate.method'] == 'tools/call'
            assert request_log['attributes']['watchgate.tool'] == 'integration_tool'
            assert request_log['attributes']['watchgate.status'] == 'ALLOWED'
            assert request_log['attributes']['watchgate.request_id'] == 'integration-123'
            assert request_log['resource']['service.name'] == 'watchgate-integration'
            assert request_log['resource']['service.namespace'] == 'testing'
            assert request_log['resource']['test.suite'] == 'integration'
            assert request_log['trace_id'] == 'abcdef1234567890abcdef1234567890'
            assert request_log['span_id'] == 'abcdef1234567890'
            
            # Parse and verify response log
            response_log = json.loads(log_lines[1])
            
            assert response_log['severity_text'] == 'INFO'
            assert response_log['attributes']['watchgate.event_type'] == 'RESPONSE'
            assert response_log['attributes']['watchgate.method'] == 'tools/call'
            assert response_log['attributes']['watchgate.status'] == 'SUCCESS'
            assert response_log['attributes']['watchgate.duration_ms'] == 150
            assert response_log['resource']['service.name'] == 'watchgate-integration'
            
    @pytest.mark.asyncio
    async def test_otel_security_event_logging(self):
        """Test OTEL logging of security events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'security.otel')
            config = {
                'output_file': log_file,
                'service_name': 'watchgate-security',
                'include_trace_correlation': False
            }
            
            plugin = OtelAuditingPlugin(config)
            
            # Simulate a blocked request
            blocked_request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={
                    'name': 'dangerous_tool',
                    'arguments': {'action': 'delete_all'}
                },
                id='security-456'
            )
            
            block_decision = PolicyDecision(
                allowed=False,
                reason='Tool access denied due to security policy',
                metadata={
                    'plugin': 'security_policy_plugin',
                    'policy_violated': 'dangerous_tools_blocked',
                    'risk_level': 'high'
                }
            )
            
            await plugin.log_request(blocked_request, block_decision, "production-server")
            
            # Verify security event log
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
            
            security_log = json.loads(log_content)
            
            # Verify security event characteristics
            assert security_log['severity_text'] == 'WARN'
            assert security_log['severity_number'] == 13
            assert security_log['attributes']['watchgate.event_type'] == 'SECURITY_BLOCK'
            assert security_log['attributes']['watchgate.status'] == 'BLOCKED'
            assert security_log['attributes']['watchgate.tool'] == 'dangerous_tool'
            assert security_log['attributes']['watchgate.reason'] == 'Tool access denied due to security policy'
            assert 'Security block:' in security_log['body']
            
            # Verify trace correlation is disabled
            assert 'trace_id' not in security_log
            assert 'span_id' not in security_log

    def test_otel_plugin_discovery(self):
        """Test that OTEL plugin is properly discoverable."""
        from watchgate.plugins.auditing.opentelemetry import POLICIES
        
        assert 'otel_auditing' in POLICIES
        assert POLICIES['otel_auditing'] == OtelAuditingPlugin
        
        # Test plugin can be instantiated via policy discovery
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'discovery.otel')
            }
            
            plugin_class = POLICIES['otel_auditing']
            plugin = plugin_class(config)
            
            assert isinstance(plugin, OtelAuditingPlugin)
            assert plugin.service_name == 'watchgate'

    def test_otel_import_integration(self):
        """Test that OTEL plugin can be imported from main package."""
        from watchgate.plugins.auditing import OtelAuditingPlugin as ImportedPlugin
        from watchgate.plugins.auditing.opentelemetry import OtelAuditingPlugin as DirectPlugin
        
        assert ImportedPlugin == DirectPlugin
        
        # Verify it's in __all__
        from watchgate.plugins.auditing import __all__
        assert 'OtelAuditingPlugin' in __all__