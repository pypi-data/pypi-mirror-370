"""Integration tests for CEF format with file auditing plugin."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from watchgate.plugins.auditing.common_event_format import CefAuditingPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestCEFIntegration:
    """Test CEF format integration with file auditing plugin."""

    def test_cef_plugin_initialization(self):
        """Test CEF format plugin initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.log'),
                'cef_config': {
                    'device_vendor': 'TestVendor',
                    'device_version': '2.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            assert plugin.device_vendor == 'TestVendor'
            assert plugin.device_version == '2.0.0'

    def test_cef_plugin_initialization_with_auto_version(self):
        """Test CEF format plugin initialization with auto version detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.log'),
                'cef_config': {
                    'device_version': 'auto'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            assert plugin.device_version != 'auto'
            assert plugin.device_version != 'unknown'

    def test_cef_plugin_initialization_default_config(self):
        """Test CEF format plugin initialization with default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': os.path.join(tmpdir, 'test.log')
            }
            
            plugin = CefAuditingPlugin(config)
            assert plugin.device_vendor == 'Watchgate'
            assert plugin.device_product == 'MCP Gateway'

    @pytest.mark.asyncio
    async def test_cef_log_request_allowed(self):
        """Test CEF logging for allowed request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            config = {
                'output_file': log_file,
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            
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
                log_content = f.read()
                
            assert 'CEF:0|Watchgate|MCP Gateway|1.0.0|100|MCP Request|6|' in log_content
            assert 'requestId=test-123' in log_content
            assert 'act=allowed' in log_content
            assert 'cs1=test_plugin' in log_content
            assert 'cs1Label=Plugin' in log_content
            assert 'cs2=tools/call' in log_content
            assert 'cs2Label=Method' in log_content
            assert 'cs3=read_file' in log_content
            assert 'cs3Label=Tool' in log_content

    @pytest.mark.asyncio
    async def test_cef_log_request_blocked(self):
        """Test CEF logging for blocked request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            config = {
                'output_file': log_file,
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            
            # Create test request
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={'name': 'delete_file', 'arguments': {'path': '/test.txt'}},
                id='test-456'
            )
            
            decision = PolicyDecision(
                allowed=False,
                reason='Tool not in allowlist',
                metadata={'plugin': 'tool_allowlist'}
            )
            
            # Log the request
            await plugin.log_request(request, decision, "test-server")
            
            # Verify log output
            with open(log_file, 'r') as f:
                log_content = f.read()
                
            assert 'CEF:0|Watchgate|MCP Gateway|1.0.0|200|Security Block|8|' in log_content
            assert 'requestId=test-456' in log_content
            assert 'act=blocked' in log_content
            assert 'reason=Tool not in allowlist' in log_content
            assert 'cs1=tool_allowlist' in log_content
            assert 'cs1Label=Plugin' in log_content

    @pytest.mark.asyncio
    async def test_cef_log_response_success(self):
        """Test CEF logging for successful response."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            config = {
                'output_file': log_file,
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            
            # Create test request and response
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={'name': 'read_file', 'arguments': {'path': '/test.txt'}},
                id='test-789'
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                result={'content': 'file content'},
                id='test-789'
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Response approved',
                metadata={'duration_ms': 150}
            )
            
            # Log the response
            await plugin.log_response(request, response, decision, "test-server")
            
            # Verify log output
            with open(log_file, 'r') as f:
                log_content = f.read()
                
            assert 'CEF:0|Watchgate|MCP Gateway|1.0.0|101|MCP Response|6|' in log_content
            assert 'requestId=test-789' in log_content
            assert 'act=success' in log_content
            assert 'cs4=150' in log_content
            assert 'cs4Label=Duration' in log_content

    @pytest.mark.asyncio
    async def test_cef_log_response_error(self):
        """Test CEF logging for error response."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            config = {
                'output_file': log_file,
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            
            # Create test request and error response
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={'name': 'read_file', 'arguments': {'path': '/nonexistent.txt'}},
                id='test-error'
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                error={'code': -1, 'message': 'File not found'},
                id='test-error'
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Error response',
                metadata={'duration_ms': 50}
            )
            
            # Log the response
            await plugin.log_response(request, response, decision, "test-server")
            
            # Verify log output
            with open(log_file, 'r') as f:
                log_content = f.read()
                
            assert 'CEF:0|Watchgate|MCP Gateway|1.0.0|400|System Error|9|' in log_content
            assert 'requestId=test-error' in log_content
            assert 'act=error' in log_content

    @pytest.mark.asyncio
    async def test_cef_log_notification(self):
        """Test CEF logging for notification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            config = {
                'output_file': log_file,
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            
            # Create test notification
            notification = MCPNotification(
                jsonrpc="2.0",
                method='notifications/initialized',
                params={'version': '1.0.0'}
            )
            
            decision = PolicyDecision(
                allowed=True,
                reason='Notification processed'
            )
            
            # Log the notification
            await plugin.log_notification(notification, decision, "test-server")
            
            # Verify log output
            with open(log_file, 'r') as f:
                log_content = f.read()
                
            assert 'CEF:0|Watchgate|MCP Gateway|1.0.0|102|MCP Notification|4|' in log_content
            assert 'cs2=notifications/initialized' in log_content
            assert 'cs2Label=Method' in log_content
            assert 'act=notification' in log_content

    @pytest.mark.asyncio
    async def test_cef_character_escaping(self):
        """Test CEF character escaping in real log output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            config = {
                'output_file': log_file,
                'cef_config': {
                    'device_version': '1.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(config)
            
            # Create test request with characters that need escaping
            request = MCPRequest(
                jsonrpc="2.0",
                method='tools/call',
                params={'name': 'test=tool', 'arguments': {'path': '/test\nfile.txt'}},
                id='test-escape'
            )
            
            decision = PolicyDecision(
                allowed=False,
                reason='Tool contains=equals and\nnewline',
                metadata={'plugin': 'test|plugin'}
            )
            
            # Log the request
            await plugin.log_request(request, decision, "test-server")
            
            # Verify log output has proper escaping
            with open(log_file, 'r') as f:
                log_content = f.read()
                
            # Check that equals signs are escaped in extensions
            # Note: newlines get double-escaped (sanitize then CEF escape)
            assert 'reason=Tool contains\\=equals and\\\\nnewline' in log_content
            # Check that tool name is escaped
            assert 'cs3=test\\=tool' in log_content
            # Check that plugin name is escaped (pipe is escaped in extensions too)
            assert 'cs1=test\\|plugin' in log_content


    def test_cef_configuration_validation(self):
        """Test CEF configuration validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test valid configuration
            valid_config = {
                'output_file': os.path.join(tmpdir, 'test.log'),
                'cef_config': {
                    'device_vendor': 'CustomVendor',
                    'device_product': 'CustomProduct',
                    'device_version': '3.0.0'
                }
            }
            
            plugin = CefAuditingPlugin(valid_config)
            assert plugin.device_vendor == 'CustomVendor'
            assert plugin.device_product == 'CustomProduct'
            assert plugin.device_version == '3.0.0'