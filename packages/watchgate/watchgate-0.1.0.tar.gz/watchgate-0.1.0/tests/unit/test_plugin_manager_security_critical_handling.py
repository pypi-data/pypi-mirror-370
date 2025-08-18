"""Tests for plugin manager security critical handling functionality."""

from typing import Optional
import pytest
from unittest.mock import MagicMock, AsyncMock
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestPluginManagerSecurityCriticalHandling:
    """Test PluginManager security critical handling functionality."""
    
    @pytest.mark.asyncio
    async def test_critical_security_plugin_failure_blocks_request(self):
        """Test that critical security plugin failures block requests."""
        
        class CriticalFailingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                raise Exception("Critical security plugin failure")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
        
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "critical_failing",
                        "enabled": True,
                        "config": {"critical": True}
                    }
                ]
            }
        }
        
        manager = PluginManager(config)
        
        # Mock the plugin loading to use our test plugin
        manager.security_plugins = [CriticalFailingSecurityPlugin({"critical": True})]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="1")
        
        decision = await manager.process_request(request)
        
        assert decision.allowed is False
        assert "failed" in decision.reason.lower()
        assert decision.metadata.get("plugin_failure") is True
    
    @pytest.mark.asyncio
    async def test_non_critical_security_plugin_failure_allows_request(self):
        """Test that non-critical security plugin failures allow requests to continue."""
        
        class NonCriticalFailingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                raise Exception("Non-critical security plugin failure")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
        
        class PassingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Request allowed by basic security")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
        
        config = {
            "security": [
                {
                    "policy": "non_critical_failing", 
                    "enabled": True,
                    "config": {"critical": False}
                },
                {
                    "policy": "passing",
                    "enabled": True,
                    "config": {"critical": True}
                }
            ]
        }
        
        manager = PluginManager(config)
        
        # Mock the plugin loading to use our test plugins
        manager.security_plugins = [
            NonCriticalFailingSecurityPlugin({"critical": False}),
            PassingSecurityPlugin({"critical": True})
        ]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="1")
        
        decision = await manager.process_request(request)
        
        # Request should be allowed despite non-critical plugin failure
        assert decision.allowed is True
        assert "basic security" in decision.reason.lower()
    
    @pytest.mark.asyncio
    async def test_mixed_critical_non_critical_plugin_failures(self):
        """Test behavior with mix of critical and non-critical plugin failures."""
        
        class NonCriticalFailingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                raise Exception("Non-critical security plugin failure")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
        
        class CriticalFailingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                raise Exception("Critical security plugin failure")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
        
        config = {
            "security": [
                {
                    "policy": "non_critical_failing",
                    "enabled": True,
                    "config": {"critical": False}
                },
                {
                    "policy": "critical_failing",
                    "enabled": True,
                    "config": {"critical": True}
                }
            ]
        }
        
        manager = PluginManager(config)
        
        # Mock the plugin loading to use our test plugins
        # Non-critical plugin has lower priority (executes first)
        non_critical_plugin = NonCriticalFailingSecurityPlugin({"critical": False})
        non_critical_plugin.priority = 10
        
        critical_plugin = CriticalFailingSecurityPlugin({"critical": True})
        critical_plugin.priority = 20
        
        manager.security_plugins = [non_critical_plugin, critical_plugin]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="1")
        
        decision = await manager.process_request(request)
        
        # Should be blocked by critical plugin failure, even though 
        # non-critical plugin failed first
        assert decision.allowed is False
        assert "critical" in decision.reason.lower()
    
    @pytest.mark.asyncio
    async def test_critical_security_plugin_failure_blocks_response(self):
        """Test that critical security plugin failures block responses."""
        
        class CriticalFailingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                raise Exception("Critical security plugin failure on response")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
        
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "critical_failing",
                        "enabled": True,
                        "config": {"critical": True}
                    }
                ]
            }
        }
        
        manager = PluginManager(config)
        
        # Mock the plugin loading to use our test plugin
        manager.security_plugins = [CriticalFailingSecurityPlugin({"critical": True})]
        manager._initialized = True
        
        request = MCPRequest(jsonrpc="2.0", method="test", id="1")
        response = MCPResponse(jsonrpc="2.0", result={"test": "data"}, id="1")
        
        decision = await manager.process_response(request, response)
        
        assert decision.allowed is False
        assert "failed" in decision.reason.lower()
        assert decision.metadata.get("plugin_failure") is True
    
    @pytest.mark.asyncio
    async def test_critical_security_plugin_failure_blocks_notification(self):
        """Test that critical security plugin failures block notifications."""
        
        class CriticalFailingSecurityPlugin(SecurityPlugin):
            def __init__(self, config):
                super().__init__(config)
            
            async def check_request(self, request, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_response(self, request, response, server_name: Optional[str] = None):
                return PolicyDecision(allowed=True, reason="Test")
                
            async def check_notification(self, notification, server_name: Optional[str] = None):
                raise Exception("Critical security plugin failure on notification")
        
        config = {
            "security": {
                "_global": [
                    {
                        "policy": "critical_failing",
                        "enabled": True,
                        "config": {"critical": True}
                    }
                ]
            }
        }
        
        manager = PluginManager(config)
        
        # Mock the plugin loading to use our test plugin
        manager.security_plugins = [CriticalFailingSecurityPlugin({"critical": True})]
        manager._initialized = True
        
        notification = MCPNotification(jsonrpc="2.0", method="test_notification")
        
        decision = await manager.process_notification(notification)
        
        assert decision.allowed is False
        assert "failed" in decision.reason.lower()
        assert decision.metadata.get("plugin_failure") is True
