"""Integration test for PII Content Filter Plugin with Plugin Manager."""

import pytest
from watchgate.plugins.manager import PluginManager
from watchgate.protocol.messages import MCPRequest, MCPResponse


class TestPIIContentFilterIntegration:
    """Test PII Content Filter plugin integration with plugin manager."""
    
    @pytest.mark.asyncio
    async def test_pii_plugin_integration_block_mode(self):
        """Test PII plugin integration in block mode."""
        config = {
            "security": {
            "_global": [
                {
                    "policy": "pii",
                    "enabled": True,
                    "config": {
                        "action": "block",
                        "pii_types": {
                            "email": {"enabled": True}
                        }
                    }
                }
            ]
        },
        "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        await manager.load_plugins()
        
        # Test request with PII - should be blocked
        request_with_pii = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Contact user@example.com"}}
        )
        
        decision = await manager.process_request(request_with_pii)
        assert decision.allowed is False
        assert "PII detected" in decision.reason
        
        # Test request without PII - should be allowed
        clean_request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "This is clean content"}}
        )
        
        decision = await manager.process_request(clean_request)
        assert decision.allowed is True
    
    @pytest.mark.asyncio
    async def test_pii_plugin_integration_audit_mode(self):
        """Test PII plugin integration in audit mode."""
        config = {
            "security": {
            "_global": [
                {
                    "policy": "pii",
                    "enabled": True,
                    "config": {
                        "action": "audit_only",
                        "pii_types": {
                            "email": {"enabled": True}
                        }
                    }
                }
            ]
        },
        "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        await manager.load_plugins()
        
        # Test request with PII - should be allowed but logged
        request_with_pii = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Contact user@example.com"}}
        )
        
        decision = await manager.process_request(request_with_pii)
        assert decision.allowed is True
        
        # Note: In audit_only mode, the plugin manager only preserves detailed metadata 
        # when plugins modify content. For pure audit scenarios (no content modification),
        # generic metadata is returned as the plugin doesn't alter the request flow.
        # This is by design - detailed forensic metadata is available via auditing plugins.
        assert decision.metadata["plugin_count"] == 1
    
    @pytest.mark.asyncio
    async def test_pii_plugin_integration_redact_mode(self):
        """Test PII plugin integration in redact mode - should work since it modifies messages."""
        config = {
            "security": {
            "_global": [
                {
                    "policy": "pii",
                    "enabled": True,
                    "config": {
                        "action": "redact",
                        "pii_types": {
                            "email": {"enabled": True}
                        }
                    }
                }
            ]
        },
        "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        await manager.load_plugins()
        
        # Test request with PII - should be allowed with content redacted
        request_with_pii = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Contact user@example.com"}}
        )
        
        decision = await manager.process_request(request_with_pii)
        assert decision.allowed is True
        
        # Note: Request modification is not currently supported by the plugin manager.
        # The PII plugin correctly generates a modified request in redact mode, but
        # Note: With the security fix, request modification is now properly supported.
        # The plugin manager's process_request method handles request modification correctly.
        assert decision.modified_content is not None  # Request modification now supported
        assert isinstance(decision.modified_content, MCPRequest)
        
        # Note: Metadata preservation in redact mode for requests follows the same pattern
        # as response modification - detailed metadata is returned when content is modified
        assert decision.metadata["pii_detected"] is True
        assert decision.metadata["detection_action"] == "redact"
        assert "detections" in decision.metadata
    
    @pytest.mark.asyncio 
    async def test_pii_plugin_comprehensive_metadata_verification(self):
        """Test comprehensive PII metadata structure when plugin detects and processes PII in response redaction."""
        config = {
            "security": {
            "_global": [
                {
                    "policy": "pii",
                    "enabled": True,
                    "config": {
                        "action": "redact",  # Use redact mode to ensure metadata preservation
                        "pii_types": {
                            "email": {"enabled": True},
                            "credit_card": {"enabled": True},
                            "phone": {"enabled": True, "formats": ["us"]}
                        }
                    }
                }
            ]
        },
        "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        await manager.load_plugins()
        
        # Test response processing (where metadata preservation is implemented)
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool"}
        )
        
        # Response with multiple PII types
        response_with_pii = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={
                "data": "Contact: user@example.com, Card: 4532015112830366, Phone: (555) 123-4567"
            }
        )
        
        decision = await manager.process_response(request, response_with_pii)
        
        # Verify the decision allows in redact mode
        assert decision.allowed is True
        assert "PII detected" in decision.reason and "redacted" in decision.reason
        
        # Verify comprehensive metadata structure is preserved (since plugin modified content)
        assert "pii_detected" in decision.metadata
        assert "detection_action" in decision.metadata
        assert "detections" in decision.metadata
        
        assert decision.metadata["pii_detected"] is True
        assert decision.metadata["detection_action"] == "redact"
        assert isinstance(decision.metadata["detections"], list)
        assert len(decision.metadata["detections"]) >= 2  # At least email and phone detected
        
        # Verify individual detection structure
        for detection in decision.metadata["detections"]:
            assert "type" in detection
            assert "pattern" in detection
            assert "position" in detection
            assert "action" in detection
            assert detection["action"] in ["detected", "redacted"]
            assert isinstance(detection["position"], list)
            assert len(detection["position"]) == 2  # start, end positions
            
        # Verify that the response was actually modified (redacted)
        assert decision.modified_content is not None
        assert isinstance(decision.modified_content, MCPResponse)
        # Check that PII was redacted in the response
        modified_data = decision.modified_content.result["data"]
        assert "[EMAIL REDACTED by Watchgate]" in modified_data
        assert "[CREDIT_CARD REDACTED by Watchgate]" in modified_data
        assert "[PHONE REDACTED by Watchgate]" in modified_data

    @pytest.mark.asyncio
    async def test_multiple_pii_plugins_metadata_aggregation(self):
        """Test that multiple PII plugins process sequentially with last modifying plugin's metadata preserved."""
        # Set up two PII plugins with different configurations
        config = {
            "security": {
            "_global": [
                {
                    "policy": "pii",
                    "enabled": True,
                    "priority": 10,  # First plugin
                    "config": {
                        "action": "redact",
                        "pii_types": {
                            "email": {"enabled": True}
                        }
                    }
                },
                {
                    "policy": "pii", 
                    "enabled": True,
                    "priority": 20,  # Second plugin (lower priority, runs later)
                    "config": {
                        "action": "redact",
                        "pii_types": {
                            "phone": {"enabled": True, "formats": ["us"]},
                            "credit_card": {"enabled": True}
                        }
                    }
                }
            ]
        },
        "auditing": {"_global": []}
        }
        
        manager = PluginManager(config)
        await manager.load_plugins()
        
        # Test response processing with both email and phone PII
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool"}
        )
        
        response_with_mixed_pii = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={
                "data": "Contact user@example.com or call (555) 123-4567, Card: 4532015112830366"
            }
        )
        
        decision = await manager.process_response(request, response_with_mixed_pii)
        
        # Verify response is allowed (both plugins in redact mode)
        assert decision.allowed is True
        assert "PII detected" in decision.reason and "redacted" in decision.reason
        
        # Verify that the LAST modifying plugin's metadata is preserved
        # Since both plugins run and both redact content, the second plugin (priority 20)
        # should be the one whose metadata is preserved
        assert "pii_detected" in decision.metadata
        assert "detection_action" in decision.metadata
        assert "detections" in decision.metadata
        
        # The final decision should reflect the last plugin's context
        assert decision.metadata["detection_action"] == "redact"
        assert decision.metadata["pii_detected"] is True
        
        # Verify the response was modified
        assert decision.modified_content is not None
        assert isinstance(decision.modified_content, MCPResponse)
        modified_data = decision.modified_content.result["data"]
        
        # Both plugins should have done their work:
        # - Email should be redacted (first plugin)
        # - Phone and credit card should be redacted (second plugin)
        assert "[EMAIL REDACTED by Watchgate]" in modified_data
        assert "[PHONE REDACTED by Watchgate]" in modified_data
        assert "[CREDIT_CARD REDACTED by Watchgate]" in modified_data
        
        # Verify detection metadata contains findings from the final plugin state
        # (exact content depends on how sequential processing works)
        assert isinstance(decision.metadata["detections"], list)
        assert len(decision.metadata["detections"]) > 0
