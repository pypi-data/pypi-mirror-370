"""Integration tests for plugin system with other components."""

from typing import Optional
import tempfile
import pytest
from pathlib import Path
import yaml

from watchgate.config import ConfigLoader
from watchgate.plugins import PluginManager, SecurityPlugin, AuditingPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse

# Import mock classes from conftest
from conftest import MockSecurityPlugin, MockAuditingPlugin


class TestPluginIntegration:
    """Test integration scenarios between plugin system and other components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
    
    @pytest.mark.asyncio
    async def test_plugin_manager_with_yaml_config(self, plugin_yaml_config):
        """Test loading plugins from YAML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(plugin_yaml_config)
            f.flush()
            
            try:
                # Load configuration
                self.config_loader.load_from_file(Path(f.name))
                
                # Parse YAML again to extract plugins section
                with open(f.name, 'r') as yaml_file:
                    full_config = yaml.safe_load(yaml_file)
                
                plugins_config = full_config.get('plugins', {})
                
                # Create plugin manager with plugins config
                plugin_manager = PluginManager(plugins_config)
                
                # Load the plugins
                await plugin_manager.load_plugins()
                
                # Verify plugins were loaded
                assert len(plugin_manager.security_plugins) == 1
                assert len(plugin_manager.auditing_plugins) == 1
                
                # Test the loaded security plugin
                security_plugin = plugin_manager.security_plugins[0]
                # ToolAllowlistPlugin should have mode attribute
                assert hasattr(security_plugin, 'mode')
                assert security_plugin.mode == "allow_all"
                
                # Test the loaded auditing plugin  
                auditing_plugin = plugin_manager.auditing_plugins[0]
                # FileAuditingPlugin should have output_file attribute
                assert hasattr(auditing_plugin, 'output_file')
                # Path should be resolved to canonical form (e.g., /tmp -> /private/tmp on macOS)
                expected_path = Path("/tmp/test_audit.log").resolve()
                assert Path(auditing_plugin.output_file) == expected_path
                
            finally:
                Path(f.name).unlink()
    
    @pytest.mark.asyncio
    async def test_end_to_end_request_processing(self):
        """Test complete request processing pipeline with plugins."""
        # Create specialized mock for this test that checks keywords
        class KeywordBlockingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                self.blocked_keywords = config.get("blocked_keywords", [])
            
            async def check_request(self, request, server_name: Optional[str] = None):
                content = str(request.params)
                for keyword in self.blocked_keywords:
                    if keyword in content:
                        return PolicyDecision(
                            allowed=False,
                            reason=f"Request blocked due to keyword: {keyword}"
                        )
                return PolicyDecision(allowed=True, reason="Request allowed")
            
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Response allowed")
            
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Notification allowed")
        
        # Create plugin manager with mock plugins for testing
        config = {"security": {"_global": []}, "auditing": {"_global": []}}
        plugin_manager = PluginManager(config)
        
        # Manually add mock plugins for this test
        security_plugin = KeywordBlockingSecurityPlugin({"blocked_keywords": ["malicious"]})
        auditing_plugin = MockAuditingPlugin({})
        
        plugin_manager.security_plugins = [security_plugin]
        plugin_manager.auditing_plugins = [auditing_plugin]
        plugin_manager._initialized = True
        
        # Create test requests
        allowed_request = MCPRequest(
            jsonrpc="2.0",
            method="test/allowed",
            id="req-1",
            params={"data": "safe content"}
        )
        
        blocked_request = MCPRequest(
            jsonrpc="2.0",
            method="test/blocked",
            id="req-2",
            params={"data": "malicious content"}
        )
        
        # Test allowed request
        decision = await plugin_manager.process_request(allowed_request)
        assert decision.allowed is True
        assert "allowed" in decision.reason.lower()
        
        # Log the request for auditing
        await plugin_manager.log_request(allowed_request, decision)
        
        # Verify auditing occurred
        auditing_plugin = plugin_manager.auditing_plugins[0]
        assert len(auditing_plugin.logged_requests) == 1
        assert auditing_plugin.logged_requests[0][0].method == "test/allowed"  # (request, decision) tuple
        
        # Test blocked request
        decision = await plugin_manager.process_request(blocked_request)
        assert decision.allowed is False
        assert "malicious" in decision.reason
        
        # Log the blocked request
        await plugin_manager.log_request(blocked_request, decision)
        
        # Verify both requests were logged
        assert len(auditing_plugin.logged_requests) == 2
    
    @pytest.mark.asyncio
    async def test_response_logging_integration(self):
        """Test response logging with real MCPResponse objects."""
        # Create plugin manager with mock auditing plugin
        config = {"security": {"_global": []}, "auditing": {"_global": []}}
        plugin_manager = PluginManager(config)
        
        # Manually add mock auditing plugin for this test
        auditing_plugin = MockAuditingPlugin({})
        plugin_manager.auditing_plugins = [auditing_plugin]
        plugin_manager._initialized = True
        
        # Create test request to associate with responses
        request1 = MCPRequest(
            jsonrpc="2.0",
            method="test/request1",
            id="resp-1",
            params={}
        )
        
        # Test successful response
        success_response = MCPResponse(
            jsonrpc="2.0",
            id="resp-1",
            result={"status": "success", "data": "test"}
        )
        
        response_decision = PolicyDecision(allowed=True, reason="Response approved")
        await plugin_manager.log_response(request1, success_response, response_decision)
        
        # Create second test request
        request2 = MCPRequest(
            jsonrpc="2.0",
            method="test/request2",
            id="resp-2",
            params={}
        )
        
        # Test error response
        error_response = MCPResponse(
            jsonrpc="2.0",
            id="resp-2",
            error={"code": -1, "message": "Test error"}
        )
        
        error_response_decision = PolicyDecision(allowed=True, reason="Error response logged")
        await plugin_manager.log_response(request2, error_response, error_response_decision)
        
        # Verify both responses were logged
        auditing_plugin = plugin_manager.auditing_plugins[0]
        assert len(auditing_plugin.logged_responses) == 2
        
        # Check logged responses (stored as tuples: (request, response, decision))
        success_log = auditing_plugin.logged_responses[0]
        assert success_log[0].id == "resp-1"  # request
        assert success_log[1].id == "resp-1"  # response
        assert success_log[2].allowed is True  # decision
        assert hasattr(success_log[1], 'result')
        
        # Check error response logging
        error_log = auditing_plugin.logged_responses[1]
        assert error_log[0].id == "resp-2"  # request
        assert error_log[1].id == "resp-2"  # response
        assert error_log[2].allowed is True  # decision
        assert hasattr(error_log[1], 'error')
    
    @pytest.mark.asyncio
    async def test_basic_plugin_system_integration(self):
        """Test basic plugin system integration with minimal configuration.
        
        This test validates the fundamental integration scenario:
        - Plugin manager initialization with empty plugin lists
        - Real MCPRequest/MCPResponse object creation
        - End-to-end request processing and response logging
        - No mocks - pure integration validation
        """
        # Configuration with empty plugin lists (minimal case)
        config = {
            'security': [],
            'auditing': []
        }
        
        # Initialize plugin manager
        plugin_manager = PluginManager(config)
        assert plugin_manager is not None
        assert len(plugin_manager.security_plugins) == 0
        assert len(plugin_manager.auditing_plugins) == 0
        
        # Create real MCP request object
        request = MCPRequest(
            jsonrpc="2.0",
            method='tools/list',
            id='test-123',
            params={}
        )
        
        # Test request processing (should allow with no plugins)
        decision = await plugin_manager.process_request(request)
        assert decision is not None
        assert decision.allowed is True
        assert "no security plugins" in decision.reason.lower()
        
        # Create real MCP response object  
        response = MCPResponse(
            jsonrpc="2.0",
            id='test-123',
            result={'tools': []}
        )
        
        # Test response logging (should work with no plugins)
        # This should not raise any exceptions
        response_decision = PolicyDecision(allowed=True, reason="No plugins configured")
        await plugin_manager.log_response(request, response, response_decision)
        
        # Test request logging as well
        await plugin_manager.log_request(request, decision)
        
        # Verify the plugin manager remains in a valid state
        assert plugin_manager.security_plugins == []
        assert plugin_manager.auditing_plugins == []
