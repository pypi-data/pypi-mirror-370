"""Tests for plugin interfaces and data structures."""

from typing import Optional
import pytest
from pathlib import Path
from watchgate.plugins.interfaces import (
    SecurityPlugin, 
    AuditingPlugin, 
    PluginInterface, 
    PolicyDecision,
    PathResolvablePlugin
)
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestPolicyDecision:
    """Test PolicyDecision data structure."""
    
    def test_policy_decision_creation(self):
        """Test PolicyDecision creation and defaults."""
        decision = PolicyDecision(allowed=True, reason="Test reason")
        
        assert decision.allowed is True
        assert decision.reason == "Test reason"
        assert decision.metadata == {}
    
    def test_policy_decision_with_metadata(self):
        """Test PolicyDecision creation with metadata."""
        metadata = {"tool": "read_file", "user": "test"}
        decision = PolicyDecision(
            allowed=False, 
            reason="Not allowed", 
            metadata=metadata
        )
        
        assert decision.allowed is False
        assert decision.reason == "Not allowed"
        assert decision.metadata == metadata
    
    def test_policy_decision_metadata_default(self):
        """Test metadata defaults to empty dict."""
        decision = PolicyDecision(allowed=True, reason="Test")
        assert decision.metadata == {}
        
        # Verify we can modify the metadata
        decision.metadata["key"] = "value"
        assert decision.metadata["key"] == "value"
    
    def test_policy_decision_none_metadata_initialization(self):
        """Test that None metadata is converted to empty dict."""
        decision = PolicyDecision(allowed=True, reason="Test", metadata=None)
        assert decision.metadata == {}


class TestSecurityPluginInterface:
    """Test SecurityPlugin abstract interface."""
    
    def test_interface_compliance(self):
        """Test SecurityPlugin interface requirements."""
        # Verify SecurityPlugin inherits from PluginInterface
        assert issubclass(SecurityPlugin, PluginInterface)
        
        # Verify it's abstract
        with pytest.raises(TypeError):
            SecurityPlugin({})
    
    def test_abstract_methods(self):
        """Test abstract methods are properly defined."""
        # Check that check_request is abstract
        assert hasattr(SecurityPlugin, 'check_request')
        assert getattr(SecurityPlugin.check_request, '__isabstractmethod__', False)

        # Check that check_response is abstract
        assert hasattr(SecurityPlugin, 'check_response')
        assert getattr(SecurityPlugin.check_response, '__isabstractmethod__', False)
        
        # Check that check_notification is abstract
        assert hasattr(SecurityPlugin, 'check_notification')
        assert getattr(SecurityPlugin.check_notification, '__isabstractmethod__', False)
        
        # Check that __init__ is concrete (implemented in PluginInterface for priority handling)
        assert hasattr(SecurityPlugin, '__init__')
        # PluginInterface.__init__ should NOT be abstract since it provides priority handling
        assert not getattr(PluginInterface.__init__, '__isabstractmethod__', False)
    
    def test_concrete_implementation_requirements(self):
        """Test concrete implementation must implement all abstract methods."""
        
        class IncompleteSecurityPlugin(SecurityPlugin):
            """Plugin missing required methods."""
            pass
        
        # Should not be able to instantiate without implementing abstract methods
        with pytest.raises(TypeError):
            IncompleteSecurityPlugin({})
    
    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""
        
        class CompleteSecurityPlugin(SecurityPlugin):
            """Complete plugin implementation."""
            
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test plugin")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test plugin")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test plugin")
        
        # Should be able to instantiate complete implementation
        plugin = CompleteSecurityPlugin({"test": "config"})
        assert plugin.is_critical() is True  # Default to critical


class TestAuditingPluginInterface:
    """Test AuditingPlugin abstract interface."""
    
    def test_interface_compliance(self):
        """Test AuditingPlugin interface requirements."""
        # Verify AuditingPlugin inherits from PluginInterface
        assert issubclass(AuditingPlugin, PluginInterface)
        
        # Verify it's abstract
        with pytest.raises(TypeError):
            AuditingPlugin({})
    
    def test_abstract_methods(self):
        """Test abstract methods are properly defined."""
        # Check that log_request is abstract
        assert hasattr(AuditingPlugin, 'log_request')
        assert getattr(AuditingPlugin.log_request, '__isabstractmethod__', False)
        
        # Check that log_response is abstract
        assert hasattr(AuditingPlugin, 'log_response')
        assert getattr(AuditingPlugin.log_response, '__isabstractmethod__', False)
        
        # Check that log_notification is abstract
        assert hasattr(AuditingPlugin, 'log_notification')
        assert getattr(AuditingPlugin.log_notification, '__isabstractmethod__', False)
        
        # Check that __init__ is concrete (implemented in PluginInterface for priority handling)
        assert hasattr(AuditingPlugin, '__init__')
        # PluginInterface.__init__ should NOT be abstract since it provides priority handling
        assert not getattr(PluginInterface.__init__, '__isabstractmethod__', False)
    
    def test_concrete_implementation_requirements(self):
        """Test concrete implementation must implement all abstract methods."""
        
        class IncompleteAuditingPlugin(AuditingPlugin):
            """Plugin missing required methods."""
            
            def __init__(self, config):
                pass
            
            # Missing log_request, log_response, and log_notification
        
        # Should not be able to instantiate without implementing abstract methods
        with pytest.raises(TypeError):
            IncompleteAuditingPlugin({})
    
    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""
        
        class CompleteAuditingPlugin(AuditingPlugin):
            """Complete plugin implementation."""
            
            def __init__(self, config):
                self.config = config
            
            async def log_request(self, request, decision, server_name: Optional[str] = None):
                pass
                
            async def log_response(self, request, response, decision, server_name: Optional[str] = None):
                pass
                
            async def log_notification(self, notification, decision, server_name: Optional[str] = None):
                pass
        
        # Should be able to instantiate complete implementation
        plugin = CompleteAuditingPlugin({"test": "config"})
        assert plugin.config == {"test": "config"}
    
    def test_log_response_signature_requires_policy_decision(self):
        """Test that log_response method signature includes PolicyDecision parameter."""
        # This test verifies the interface signature
        import inspect
        
        # Get the log_response method signature
        log_response_method = AuditingPlugin.log_response
        signature = inspect.signature(log_response_method)
        
        # Should have parameters: self, request, response, decision
        param_names = list(signature.parameters.keys())
        assert 'self' in param_names
        assert 'request' in param_names  
        assert 'response' in param_names
        assert 'decision' in param_names, "log_response should include PolicyDecision parameter"
        
        # Check parameter types if annotations exist
        params = signature.parameters
        if 'request' in params and params['request'].annotation != inspect.Parameter.empty:
            assert params['request'].annotation == MCPRequest
        if 'response' in params and params['response'].annotation != inspect.Parameter.empty:
            assert params['response'].annotation == MCPResponse
        if 'decision' in params and params['decision'].annotation != inspect.Parameter.empty:
            assert params['decision'].annotation == PolicyDecision


class TestPluginInterfaceIntegration:
    """Test plugin interface integration with MCP protocol."""
    
    @pytest.mark.asyncio
    async def test_security_plugin_with_mcp_request(self):
        """Test SecurityPlugin with actual MCP request."""
        
        class TestSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                # Simple test logic
                if request.method == "tools/call":
                    return PolicyDecision(allowed=False, reason="Tools blocked")
                return PolicyDecision(allowed=True, reason="Method allowed")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Response allowed")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Notification allowed")
        
        plugin = TestSecurityPlugin({})
        
        # Test with tool call request
        tool_request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file"}
        )
        
        decision = await plugin.check_request(tool_request)
        assert decision.allowed is False
        assert decision.reason == "Tools blocked"
        
        # Test with non-tool request
        other_request = MCPRequest(
            jsonrpc="2.0",
            method="initialize",
            id="test-2"
        )
        
        decision = await plugin.check_request(other_request)
        assert decision.allowed is True
        assert decision.reason == "Method allowed"
        
    @pytest.mark.asyncio
    async def test_security_plugin_with_mcp_response(self):
        """Test SecurityPlugin with actual MCP response."""
        
        class TestSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Request allowed")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                # Simple test logic
                if response.error:
                    return PolicyDecision(allowed=False, reason="Error response blocked")
                return PolicyDecision(allowed=True, reason="Success response allowed")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Notification allowed")
        
        plugin = TestSecurityPlugin({})
        
        # Create request and successful response
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file"}
        )
        
        success_response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"content": "test content"}
        )
        
        decision = await plugin.check_response(request, success_response)
        assert decision.allowed is True
        assert decision.reason == "Success response allowed"
        
        # Test with error response
        error_response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            error={"code": -32601, "message": "Method not found"}
        )
        
        decision = await plugin.check_response(request, error_response)
        assert decision.allowed is False
        assert decision.reason == "Error response blocked"
        
    @pytest.mark.asyncio
    async def test_security_plugin_with_mcp_notification(self):
        """Test SecurityPlugin with actual MCP notification."""
        
        class TestSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Request allowed")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Response allowed")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                # Simple test logic
                if notification.method == "progress":
                    return PolicyDecision(allowed=True, reason="Progress notification allowed")
                return PolicyDecision(allowed=False, reason="Other notifications blocked")
        
        plugin = TestSecurityPlugin({})
        
        # Test with progress notification
        progress_notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 50}
        )
        
        decision = await plugin.check_notification(progress_notification)
        assert decision.allowed is True
        assert decision.reason == "Progress notification allowed"
        
        # Test with other notification
        other_notification = MCPNotification(
            jsonrpc="2.0",
            method="other_event",
            params={"data": "test"}
        )
        
        decision = await plugin.check_notification(other_notification)
        assert decision.allowed is False
        assert decision.reason == "Other notifications blocked"
    
    @pytest.mark.asyncio
    async def test_auditing_plugin_with_mcp_messages(self):
        """Test AuditingPlugin with actual MCP messages."""
        
        class TestAuditingPlugin(AuditingPlugin):
            def __init__(self, config):
                self.config = config
                self.logged_requests = []
                self.logged_responses = []
                self.logged_notifications = []
            
            async def log_request(self, request, decision, server_name: Optional[str] = None):
                self.logged_requests.append((request, decision))
                
            async def log_response(self, request, response, decision, server_name: Optional[str] = None):
                self.logged_responses.append((request, response))
                
            async def log_notification(self, notification, decision, server_name: Optional[str] = None):
                self.logged_notifications.append(notification)
        
        plugin = TestAuditingPlugin({})
        
        # Test request logging
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1"
        )
        decision = PolicyDecision(allowed=True, reason="Test")
        
        await plugin.log_request(request, decision)
        assert len(plugin.logged_requests) == 1
        assert plugin.logged_requests[0] == (request, decision)
        
        # Test response logging
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"success": True}
        )
        
        await plugin.log_response(request, response, decision)
        assert len(plugin.logged_responses) == 1
        assert plugin.logged_responses[0] == (request, response)
        
        # Test notification logging
        notification = MCPNotification(
            jsonrpc="2.0",
            method="progress",
            params={"percent": 75}
        )
        
        await plugin.log_notification(notification, decision)
        assert len(plugin.logged_notifications) == 1
        assert plugin.logged_notifications[0] == notification


class TestPathResolvablePluginInterface:
    """Test PathResolvablePlugin interface for path resolution."""
    
    def test_interface_compliance(self):
        """Test PathResolvablePlugin interface requirements."""
        # Verify PathResolvablePlugin exists
        assert hasattr(PathResolvablePlugin, 'set_config_directory')
        assert hasattr(PathResolvablePlugin, 'validate_paths')
        
        # Verify it's abstract
        with pytest.raises(TypeError):
            PathResolvablePlugin({})
    
    def test_abstract_methods(self):
        """Test abstract methods are properly defined."""
        # Check that set_config_directory is abstract
        assert hasattr(PathResolvablePlugin, 'set_config_directory')
        assert getattr(PathResolvablePlugin.set_config_directory, '__isabstractmethod__', False)
        
        # Check that validate_paths is abstract  
        assert hasattr(PathResolvablePlugin, 'validate_paths')
        assert getattr(PathResolvablePlugin.validate_paths, '__isabstractmethod__', False)
    
    def test_concrete_implementation_requirements(self):
        """Test concrete implementation must implement all abstract methods."""
        
        class IncompletePathPlugin(PathResolvablePlugin):
            """Plugin missing required methods."""
            
            def __init__(self, config):
                pass
            
            # Missing set_config_directory and validate_paths
        
        # Should not be able to instantiate without implementing abstract methods
        with pytest.raises(TypeError):
            IncompletePathPlugin({})
    
    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""
        
        class CompletePathPlugin(PathResolvablePlugin):
            """Complete plugin implementation."""
            
            def __init__(self, config):
                self.config = config
                self.config_directory = None
                self.path_errors = []
            
            def set_config_directory(self, config_directory):
                self.config_directory = config_directory
                
            def validate_paths(self):
                self.path_errors = []
                # Simple validation logic for testing
                if self.config.get("invalid_path"):
                    self.path_errors.append("Test path error")
                return self.path_errors
        
        # Should be able to instantiate complete implementation
        plugin = CompletePathPlugin({"test": "config"})
        assert plugin.config == {"test": "config"}
        assert plugin.config_directory is None
        
        # Test set_config_directory method
        plugin.set_config_directory(Path("/test/config"))
        assert plugin.config_directory == Path("/test/config")
        
        # Test validate_paths method returns empty list for valid config
        errors = plugin.validate_paths()
        assert errors == []
        
        # Test validate_paths method returns errors for invalid config
        plugin.config["invalid_path"] = True
        errors = plugin.validate_paths()
        assert errors == ["Test path error"]
    
    def test_path_plugin_with_security_mixin(self):
        """Test PathResolvablePlugin can be mixed with SecurityPlugin."""
        
        class PathAwareSecurityPlugin(SecurityPlugin, PathResolvablePlugin):
            """Plugin that implements both security and path interfaces."""
            
            def __init__(self, config):
                super().__init__(config)
                self.config_directory = None
                self.paths_validated = False
            
            def set_config_directory(self, config_directory):
                self.config_directory = config_directory
                
            def validate_paths(self):
                self.paths_validated = True
                return []  # No path errors for this test
                
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test plugin")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test plugin")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test plugin")
        
        # Should be able to instantiate with both interfaces
        plugin = PathAwareSecurityPlugin({"priority": 10})
        assert plugin.priority == 10
        assert plugin.config_directory is None
        assert plugin.paths_validated is False
        
        # Test path interface methods
        plugin.set_config_directory(Path("/config"))
        assert plugin.config_directory == Path("/config")
        
        errors = plugin.validate_paths()
        assert errors == []
        assert plugin.paths_validated is True
    
    def test_path_plugin_with_auditing_mixin(self):
        """Test PathResolvablePlugin can be mixed with AuditingPlugin."""
        
        class PathAwareAuditingPlugin(AuditingPlugin, PathResolvablePlugin):
            """Plugin that implements both auditing and path interfaces."""
            
            def __init__(self, config):
                super().__init__(config)
                self.config = config
                self.config_directory = None
                self.log_path = None
            
            def set_config_directory(self, config_directory):
                self.config_directory = config_directory
                # Resolve log path relative to config directory
                if self.config_directory and "log_file" in self.config:
                    from watchgate.utils.paths import resolve_config_path
                    self.log_path = resolve_config_path(
                        self.config["log_file"], 
                        self.config_directory
                    )
                
            def validate_paths(self):
                errors = []
                if self.log_path and not self.log_path.parent.exists():
                    errors.append(f"Log directory does not exist: {self.log_path.parent}")
                return errors
                
            async def log_request(self, request, decision, server_name: Optional[str] = None):
                pass
                
            async def log_response(self, request, response, decision, server_name: Optional[str] = None):
                pass
                
            async def log_notification(self, notification, decision, server_name: Optional[str] = None):
                pass
        
        # Create plugin with log file config
        config = {"log_file": "audit.log", "priority": 20}
        plugin = PathAwareAuditingPlugin(config)
        assert plugin.priority == 20
        assert plugin.config_directory is None
        assert plugin.log_path is None
        
        # Test path resolution on set_config_directory
        config_dir = Path("/config/dir")
        plugin.set_config_directory(config_dir)
        assert plugin.config_directory == config_dir
        assert plugin.log_path == config_dir / "audit.log"
        
        # Test path validation
        errors = plugin.validate_paths()
        # Should have error since /config/dir doesn't exist
        assert len(errors) == 1
        assert "Log directory does not exist" in errors[0]
