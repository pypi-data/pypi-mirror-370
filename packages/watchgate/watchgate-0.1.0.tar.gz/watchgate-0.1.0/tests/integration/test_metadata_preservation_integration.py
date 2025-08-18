"""Integration tests for plugin manager metadata preservation functionality."""

import pytest
from typing import Optional
from unittest.mock import AsyncMock, MagicMock
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, AuditingPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse


class MockModifyingSecurityPlugin(SecurityPlugin):
    """Mock security plugin that modifies responses with detailed metadata"""
    def __init__(self, config=None):
        if config is None:
            config = {}
        super().__init__(config)
    
    async def check_request(self, request, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Request allowed")
    
    async def check_response(self, request, response, server_name: Optional[str] = None):
        # Simulate response modification with security context
        modified_response = MCPResponse(
            jsonrpc="2.0",
            id=response.id,
            result={"sanitized": True, "original": response.result}
        )
        return PolicyDecision(
            allowed=True,
            reason="Response sanitized by security filter",
            metadata={"items_sanitized": 2, "filter": "basic_pii_filter", "confidence": 0.95},
            modified_content=modified_response
        )
    
    async def check_notification(self, notification, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Notification allowed")


class MockAuditingPlugin(AuditingPlugin):
    """Mock auditing plugin that captures enhanced metadata"""
    def __init__(self, config=None):
        if config is None:
            config = {}
        super().__init__(config)
        self.logged_responses = []
    
    async def log_request(self, request, decision, server_name: Optional[str] = None):
        pass  # Not relevant for this test
    
    async def log_response(self, request, response, decision, server_name: Optional[str] = None):
        # Store the response for verification
        self.logged_responses.append(response)
    
    async def log_notification(self, notification, decision, server_name: Optional[str] = None):
        pass  # Not relevant for this test


@pytest.mark.asyncio
class TestMetadataPreservationIntegration:
    
    async def test_end_to_end_metadata_preservation_flow(self):
        """Test that enhanced metadata flows through entire request/response pipeline"""
        # Set up plugins
        security_plugin = MockModifyingSecurityPlugin()
        auditing_plugin = MockAuditingPlugin()
        
        manager = PluginManager({})
        manager.security_plugins = [security_plugin]
        manager.auditing_plugins = [auditing_plugin]
        manager._initialized = True
        
        # Original request/response
        request = MCPRequest(jsonrpc="2.0", method="get_user_data", id=1)
        response = MCPResponse(jsonrpc="2.0", id=1, result={"user": "john@example.com", "ssn": "123-45-6789"})
        
        # Process through security plugins
        security_decision = await manager.process_response(request, response)
        
        # Verify enhanced metadata is preserved from security plugin
        assert security_decision.allowed is True
        assert security_decision.reason == "Response sanitized by security filter"
        # Check that plugin metadata is preserved along with plugin_count, auto-injected plugin name, and upstream context
        expected_metadata = {"items_sanitized": 2, "filter": "basic_pii_filter", "confidence": 0.95, "plugin_count": 1, "plugin": "MockModifyingSecurityPlugin", "upstream": None}
        assert security_decision.metadata == expected_metadata
        assert security_decision.modified_content is not None
        assert isinstance(security_decision.modified_content, MCPResponse)
        assert security_decision.modified_content.result == {"sanitized": True, "original": {"user": "john@example.com", "ssn": "123-45-6789"}}
        
        # Log the response (this is what happens in the actual proxy flow)
        await manager.log_response(request, security_decision.modified_content, security_decision)
        
        # Verify auditing plugin received the modified response
        assert len(auditing_plugin.logged_responses) == 1
        logged_response = auditing_plugin.logged_responses[0]
        assert logged_response.result["sanitized"] is True
    
    async def test_user_error_messages_contain_specific_plugin_context(self):
        """Test that error messages to users contain specific plugin reasons, not generic ones"""
        # This simulates the scenario where a user would see the error message
        security_plugin = MockModifyingSecurityPlugin()
        
        # Override to return a denial with specific context
        async def denying_response(request, response, server_name: Optional[str] = None):
            return PolicyDecision(
                allowed=False,
                reason="Response blocked: contains sensitive PII data",
                metadata={"violation_type": "pii_detection", "confidence": 0.98, "items_found": ["ssn", "email"]}
            )
        security_plugin.check_response = denying_response
        
        manager = PluginManager({})
        manager.security_plugins = [security_plugin]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="get_user_data", id=1)
        response = MCPResponse(jsonrpc="2.0", id=1, result={"user": "john@example.com", "ssn": "123-45-6789"})
        
        result = await manager.process_response(request, response)
        
        # Verify specific error context is preserved (not generic)
        assert result.allowed is False
        assert result.reason == "Response blocked: contains sensitive PII data"
        assert result.metadata["violation_type"] == "pii_detection"
        assert result.metadata["confidence"] == 0.98
        assert result.metadata["items_found"] == ["ssn", "email"]
        
        # This specific reason would be shown to the user instead of generic message
        assert "generic" not in result.reason.lower()
        assert "PII data" in result.reason
    
    async def test_multiple_plugins_last_modification_wins(self):
        """Test integration with multiple security plugins where last modifier wins"""
        # First plugin - PII filter
        pii_plugin = MockModifyingSecurityPlugin()
        
        # Second plugin - Content filter (higher priority, runs later)
        content_plugin = MockModifyingSecurityPlugin({"priority": 60})
        
        async def content_filter_response(request, response, server_name: Optional[str] = None):
            modified_response = MCPResponse(
                jsonrpc="2.0",
                id=response.id,
                result={"content_filtered": True, "previous": response.result}
            )
            return PolicyDecision(
                allowed=True,
                reason="Content filtered for appropriate language",
                metadata={"filter_type": "content", "words_replaced": 1},
                modified_content=modified_response
            )
        content_plugin.check_response = content_filter_response
        
        manager = PluginManager({})
        manager.security_plugins = [pii_plugin, content_plugin]  # Content plugin runs last
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="get_content", id=1)
        response = MCPResponse(jsonrpc="2.0", id=1, result={"text": "Hello world, damn it!"})
        
        result = await manager.process_response(request, response)
        
        # Should preserve the LAST modifying plugin's context (content filter) plus plugin_count and auto-injected plugin name
        assert result.allowed is True
        assert result.reason == "Content filtered for appropriate language"
        assert result.metadata == {"filter_type": "content", "words_replaced": 1, "plugin_count": 2, "plugin": "MockModifyingSecurityPlugin", "upstream": None}
        
        # Response should reflect both modifications (nested structure)
        assert result.modified_content.result["content_filtered"] is True
        assert "previous" in result.modified_content.result
