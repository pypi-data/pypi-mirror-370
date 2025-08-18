"""Tests for plugin manager metadata preservation functionality."""

from typing import Optional
import pytest
from unittest.mock import AsyncMock, MagicMock
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse


class MockModifyingPlugin(SecurityPlugin):
    """Mock plugin that modifies responses with specific reason/metadata"""
    def __init__(self, config=None):
        if config is None:
            config = {}
        super().__init__(config)
    
    async def check_request(self, request, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Request allowed")
    
    async def check_response(self, request, response, server_name: Optional[str] = None):
        # Simulate response modification with specific context
        modified_response = MCPResponse(
            jsonrpc="2.0",
            id=response.id,
            result={"modified": True, "original": response.result}
        )
        return PolicyDecision(
            allowed=True,
            reason="Content filtered by mock plugin",
            metadata={"items_filtered": 3},
            modified_content=modified_response
        )
    
    async def check_notification(self, notification, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Notification allowed")


class MockNonModifyingPlugin(SecurityPlugin):
    """Mock plugin that allows without modification"""
    def __init__(self, config=None):
        if config is None:
            config = {}
        super().__init__(config)
    
    async def check_request(self, request, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Request allowed")
    
    async def check_response(self, request, response, server_name: Optional[str] = None):
        return PolicyDecision(
            allowed=True,
            reason="Content reviewed and approved",
            metadata={"review_passed": True}
        )
    
    async def check_notification(self, notification, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Notification allowed")


@pytest.mark.asyncio
class TestPluginManagerMetadataPreservation:
    
    async def test_plugin_manager_metadata_preservation(self):
        """Test plugin manager preserves plugin reason and metadata when response is modified"""
        # RED: Write test first - expect it to fail with current implementation
        manager = PluginManager({})
        manager.security_plugins = [MockModifyingPlugin()]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id=1)
        response = MCPResponse(jsonrpc="2.0", id=1, result={"data": "test"})
        
        result = await manager.process_response(request, response)
        
        # Should preserve plugin's specific context, not use generic
        assert result.allowed is True
        assert result.reason == "Content filtered by mock plugin"  # NOT generic
        # Should include plugin metadata plus plugin_count
        assert result.metadata == {"items_filtered": 3, "plugin": "MockModifyingPlugin", "plugin_count": 1, "upstream": None}
        assert result.modified_content is not None
    
    async def test_plugin_manager_generic_metadata_when_no_modification(self):
        """Test plugin manager uses generic reason/metadata when plugins allow without modification"""
        manager = PluginManager({})
        manager.security_plugins = [MockNonModifyingPlugin()]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id=1)
        response = MCPResponse(jsonrpc="2.0", id=1, result={"data": "test"})
        
        result = await manager.process_response(request, response)
        
        # Should use generic context since no modification occurred
        assert result.allowed is True
        assert result.reason == "Response allowed by all security plugins for upstream 'unknown'"  # Generic
        assert result.metadata == {"plugin_count": 1, "upstream": None, "plugins_applied": ["MockNonModifyingPlugin"]}  # Generic
        assert result.modified_content is None
    
    async def test_plugin_manager_last_modifying_plugin_wins(self):
        """Test that when multiple plugins modify responses, last plugin's metadata is preserved"""
        plugin1 = MockModifyingPlugin({"priority": 10})
        
        plugin2 = MockModifyingPlugin({"priority": 20})
        
        # Override second plugin to return different context
        async def second_plugin_response(request, response, server_name: Optional[str] = None):
            modified_response = MCPResponse(
                jsonrpc="2.0",
                id=response.id,
                result={"final_modification": True}
            )
            return PolicyDecision(
                allowed=True,
                reason="Final processing by second plugin",
                metadata={"final_step": True},
                modified_content=modified_response
            )
        plugin2.check_response = second_plugin_response
        
        manager = PluginManager({})
        manager.security_plugins = [plugin1, plugin2]  # Sorted by priority
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id=1)
        response = MCPResponse(jsonrpc="2.0", id=1, result={"data": "test"})
        
        result = await manager.process_response(request, response)
        
        # Should preserve LAST modifying plugin's context
        assert result.allowed is True
        assert result.reason == "Final processing by second plugin"  # From plugin2
        # Should include last plugin metadata plus plugin_count
        assert result.metadata == {"final_step": True, "plugin": "MockModifyingPlugin", "plugin_count": 2, "upstream": None}  # From plugin2
        assert result.modified_content is not None
    
    async def test_plugin_manager_preserves_denial_metadata(self):
        """Test that plugin denials preserve specific context (existing behavior)"""
        # This test verifies current behavior is not broken
        plugin = MockModifyingPlugin()
        
        async def denying_response(request, response, server_name: Optional[str] = None):
            return PolicyDecision(
                allowed=False,
                reason="Content blocked by security policy",
                metadata={"violation": "sensitive_data", "confidence": 0.95}
            )
        plugin.check_response = denying_response
        
        manager = PluginManager({})
        manager.security_plugins = [plugin]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id=1)
        response = MCPResponse(jsonrpc="2.0", id=1, result={"data": "test"})
        
        result = await manager.process_response(request, response)
        
        # Should preserve denial context (existing behavior)
        assert result.allowed is False
        assert result.reason == "Content blocked by security policy"
        assert result.metadata == {"violation": "sensitive_data", "confidence": 0.95, "plugin": "MockModifyingPlugin"}
