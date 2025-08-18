"""Tests for plugin manager sequential response processing functionality.

This module tests the sequential processing of response modifications by the PluginManager.
"""

from typing import Optional
import pytest
from unittest.mock import AsyncMock, Mock
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import PolicyDecision, SecurityPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse


class MockPlugin(SecurityPlugin):
    """Mock plugin for testing response modification."""
    
    def __init__(self, config, check_response_mock=None):
        self.config = config
        self.check_response_mock = check_response_mock or AsyncMock()
    
    async def check_request(self, request, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Mock allows requests")
    
    async def check_response(self, request, response, server_name: Optional[str] = None):
        return await self.check_response_mock(request, response)
    
    async def check_notification(self, notification, server_name: Optional[str] = None):
        return PolicyDecision(allowed=True, reason="Mock allows notifications")


class TestPluginManagerSequentialProcessing:
    """Test sequential processing of response modifications."""
    
    @pytest.fixture
    def plugin_manager(self):
        """Create a plugin manager."""
        return PluginManager({})
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample request."""
        return MCPRequest(
            jsonrpc="2.0",
            method="tools/list",
            id="test-1",
            params={}
        )
    
    @pytest.fixture
    def sample_response(self):
        """Create a sample response."""
        return MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"tools": [{"name": "tool1"}, {"name": "tool2"}]}
        )
    
    @pytest.mark.asyncio
    async def test_sequential_plugin_processing_with_modifications(self, plugin_manager, sample_request, sample_response):
        """Test that plugins process responses sequentially with modifications flowing between them."""
        
        # Create modified responses for each plugin
        modified_response_1 = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"tools": [{"name": "tool1", "modified_by": "plugin1"}]}
        )
        
        modified_response_2 = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"tools": [{"name": "tool1", "modified_by": "plugin1", "also_modified_by": "plugin2"}]}
        )
        
        # Create mock plugins
        plugin1_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True,
            reason="Plugin1 modified response",
            modified_content=modified_response_1
        ))
        
        plugin2_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True, 
            reason="Plugin2 also modified response",
            modified_content=modified_response_2
        ))
        
        plugin1 = MockPlugin({}, plugin1_mock)
        plugin2 = MockPlugin({}, plugin2_mock)
        
        # Manually set plugins (bypassing normal loading)
        plugin_manager.security_plugins = [plugin1, plugin2]
        plugin_manager._initialized = True
        
        # Process response
        decision = await plugin_manager.process_response(sample_request, sample_response)
        
        # Verify both plugins were called
        plugin1_mock.assert_called_once_with(sample_request, sample_response)
        plugin2_mock.assert_called_once_with(sample_request, modified_response_1)  # Plugin2 should receive plugin1's modification
        
        # Verify final decision includes the last modification
        assert decision.allowed is True
        assert decision.modified_content == modified_response_2
        
    @pytest.mark.asyncio
    async def test_sequential_processing_stops_on_denial(self, plugin_manager, sample_request, sample_response):
        """Test that processing stops when a plugin denies the response."""
        
        # Create mock plugins
        plugin1_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True,
            reason="Plugin1 allows",
            modified_content=None
        ))
        
        plugin2_mock = AsyncMock(return_value=PolicyDecision(
            allowed=False,
            reason="Plugin2 denies response"
        ))
        
        plugin3_mock = AsyncMock()  # Should not be called
        
        plugin1 = MockPlugin({}, plugin1_mock)
        plugin2 = MockPlugin({}, plugin2_mock) 
        plugin3 = MockPlugin({}, plugin3_mock)
        
        # Manually set plugins
        plugin_manager.security_plugins = [plugin1, plugin2, plugin3]
        plugin_manager._initialized = True
        
        # Process response
        decision = await plugin_manager.process_response(sample_request, sample_response)
        
        # Verify processing stopped at plugin2
        plugin1_mock.assert_called_once()
        plugin2_mock.assert_called_once()
        plugin3_mock.assert_not_called()
        
        # Verify denial was returned
        assert decision.allowed is False
        assert decision.reason == "Plugin2 denies response"
        
    @pytest.mark.asyncio
    async def test_no_modifications_needed(self, plugin_manager, sample_request, sample_response):
        """Test processing when no plugins modify the response."""
        
        # Create mock plugins that don't modify responses
        plugin1_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True,
            reason="Plugin1 allows unchanged"
        ))
        
        plugin2_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True,
            reason="Plugin2 allows unchanged"
        ))
        
        plugin1 = MockPlugin({}, plugin1_mock)
        plugin2 = MockPlugin({}, plugin2_mock)
        
        # Manually set plugins
        plugin_manager.security_plugins = [plugin1, plugin2]
        plugin_manager._initialized = True
        
        # Process response
        decision = await plugin_manager.process_response(sample_request, sample_response)
        
        # Verify both plugins were called with original response
        plugin1_mock.assert_called_once_with(sample_request, sample_response)
        plugin2_mock.assert_called_once_with(sample_request, sample_response)
        
        # Verify no modifications were made
        assert decision.allowed is True
        assert decision.modified_content is None
        
    @pytest.mark.asyncio
    async def test_mixed_modification_and_no_modification(self, plugin_manager, sample_request, sample_response):
        """Test processing with some plugins modifying and others not."""
        
        modified_response = MCPResponse(
            jsonrpc="2.0",
            id="test-1", 
            result={"tools": [{"name": "modified_tool"}]}
        )
        
        # Plugin1 modifies, Plugin2 doesn't, Plugin3 sees Plugin1's modification
        plugin1_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True,
            reason="Plugin1 modified",
            modified_content=modified_response
        ))
        
        plugin2_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True,
            reason="Plugin2 doesn't modify"
        ))
        
        plugin3_mock = AsyncMock(return_value=PolicyDecision(
            allowed=True,
            reason="Plugin3 doesn't modify"
        ))
        
        plugin1 = MockPlugin({}, plugin1_mock)
        plugin2 = MockPlugin({}, plugin2_mock)
        plugin3 = MockPlugin({}, plugin3_mock)
        
        # Manually set plugins
        plugin_manager.security_plugins = [plugin1, plugin2, plugin3]
        plugin_manager._initialized = True
        
        # Process response
        decision = await plugin_manager.process_response(sample_request, sample_response)
        
        # Verify call sequence
        plugin1_mock.assert_called_once_with(sample_request, sample_response)
        plugin2_mock.assert_called_once_with(sample_request, modified_response)  # Sees modification
        plugin3_mock.assert_called_once_with(sample_request, modified_response)  # Also sees modification
        
        # Verify final decision has Plugin1's modification
        assert decision.allowed is True
        assert decision.modified_content == modified_response
