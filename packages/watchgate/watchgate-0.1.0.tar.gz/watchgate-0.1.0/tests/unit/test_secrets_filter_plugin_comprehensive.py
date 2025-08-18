"""Comprehensive tests for BasicSecretsFilterPlugin to verify requirements."""

import pytest
import time
from watchgate.plugins.security.secrets import BasicSecretsFilterPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestSecretsFilterRequirements:
    """Test specific requirements from the implementation prompt."""
    
    def test_high_confidence_secret_patterns(self):
        """Test all high-confidence secret types from requirements."""
        config = {
            "action": "block",
            "secret_types": {
                "aws_access_keys": {"enabled": True},
                "github_tokens": {"enabled": True},
                "google_api_keys": {"enabled": True},
                "jwt_tokens": {"enabled": True},
                "ssh_private_keys": {"enabled": True}
            }
        }
        plugin = BasicSecretsFilterPlugin(config)
        
        # Test each secret type
        test_cases = [
            ("AKIAIOSFODNN7EXAMPLE", "aws_access_keys"),
            ("ghp_1234567890abcdef1234567890abcdef12345678", "github_tokens"),
            ("gho_1234567890abcdef1234567890abcdef12345678", "github_tokens"),
            ("ghu_1234567890abcdef1234567890abcdef12345678", "github_tokens"),
            ("ghs_1234567890abcdef1234567890abcdef12345678", "github_tokens"),
            ("ghr_1234567890abcdef1234567890abcdef12345678", "github_tokens"),
            ("AIza1234567890abcdef1234567890abcdef123456", "google_api_keys"),
            ("-----BEGIN RSA PRIVATE KEY-----", "ssh_private_keys"),
            ("-----BEGIN DSA PRIVATE KEY-----", "ssh_private_keys"),
            ("-----BEGIN EC PRIVATE KEY-----", "ssh_private_keys"),
            ("-----BEGIN OPENSSH PRIVATE KEY-----", "ssh_private_keys"),
        ]
        
        for secret_value, expected_type in test_cases:
            detections = plugin._detect_secrets_in_text(secret_value)
            assert len(detections) > 0, f"Should detect {expected_type} in '{secret_value}'"
            assert detections[0]["type"] == expected_type
            assert detections[0]["confidence"] == "high"
    
    def test_jwt_token_detection(self):
        """Test JWT token detection with proper three-part structure."""
        config = {"action": "block", "secret_types": {"jwt_tokens": {"enabled": True}}}
        plugin = BasicSecretsFilterPlugin(config)
        
        # Valid JWT structure (header.payload.signature)
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        detections = plugin._detect_secrets_in_text(jwt_token)
        assert len(detections) > 0
        assert detections[0]["type"] == "jwt_tokens"
    
    def test_entropy_detection_enabled_by_default(self):
        """Test that entropy detection is enabled by default with conservative thresholds."""
        config = {"action": "block"}
        plugin = BasicSecretsFilterPlugin(config)
        
        assert plugin.entropy_detection["enabled"] is True
        assert plugin.entropy_detection["min_entropy"] == 6.0  # Updated in Requirement 4 to reduce false positives
        assert plugin.entropy_detection["min_length"] == 8
        # No max_length - entropy detection should analyze all content regardless of size
        assert "max_length" not in plugin.entropy_detection or plugin.entropy_detection.get("max_length") is None
    
    def test_custom_patterns_support(self):
        """Test custom organization patterns support."""
        config = {
            "action": "block",
            "custom_patterns": [
                {"name": "company_api_key", "pattern": "COMP-[A-Za-z0-9]{32}", "enabled": True},
                {"name": "internal_token", "pattern": "INT_[A-Z0-9]{24}", "enabled": True}
            ]
        }
        plugin = BasicSecretsFilterPlugin(config)
        
        # Test custom pattern detection
        test_text = "COMP-abcd1234567890abcdef1234567890abcd"
        detections = plugin._detect_secrets_in_text(test_text)
        assert len(detections) > 0
        assert detections[0]["type"] == "company_api_key"  # Uses pattern name as type
        assert detections[0]["pattern"] == "custom"  # Indicates it's a custom pattern
    
    def test_allowlist_functionality(self):
        """Test allowlist patterns for testing scenarios."""
        config = {
            "action": "block",
            "secret_types": {"aws_access_keys": {"enabled": True}},
            "allowlist": {
                "patterns": ["test_key_*", "demo_token_*", "AKIATEST*"]
            }
        }
        plugin = BasicSecretsFilterPlugin(config)
        
        # Test that allowlisted pattern is not detected
        test_text = "AKIATESTKEY123456789"
        
        # Check if the text matches allowlist (should return True)
        matches_allowlist = plugin._matches_allowlist(test_text)
        assert matches_allowlist is True, "AKIATEST* pattern should match allowlist"
        
        # When allowlist matches, no detections should be returned by the main detection
        detections = plugin._detect_secrets_in_text(test_text)
        assert len(detections) == 0, "Allowlisted pattern should not generate detections"
    
    @pytest.mark.asyncio
    async def test_performance_requirement(self):
        """Test <10ms processing time requirement."""
        config = {
            "action": "block",
            "secret_types": {
                "aws_access_keys": {"enabled": True},
                "github_tokens": {"enabled": True},
                "google_api_keys": {"enabled": True},
                "jwt_tokens": {"enabled": True},
                "ssh_private_keys": {"enabled": True}
            },
            "entropy_detection": {"enabled": True}
        }
        plugin = BasicSecretsFilterPlugin(config)
        
        # Test with a reasonably sized message
        large_content = "Normal text content " * 100 + " AKIAIOSFODNN7EXAMPLE " + "More normal content " * 100
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file", "arguments": {"content": large_content}}
        )
        
        start_time = time.time()
        decision = await plugin.check_request(request, "test-server")
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        assert processing_time < 10, f"Processing took {processing_time:.2f}ms, should be <10ms"
        assert decision.allowed is False  # Should detect the AWS key
    
    def test_conservative_defaults(self):
        """Test that higher false positive risk patterns are disabled by default."""
        config = {"action": "block"}
        plugin = BasicSecretsFilterPlugin(config)
        
        # AWS secret keys should be disabled by default (higher false positive risk)
        assert plugin.secret_types["aws_secret_keys"]["enabled"] is False
        
        # High confidence patterns should be enabled by default
        assert plugin.secret_types["aws_access_keys"]["enabled"] is True
        assert plugin.secret_types["github_tokens"]["enabled"] is True
        assert plugin.secret_types["google_api_keys"]["enabled"] is True
        assert plugin.secret_types["jwt_tokens"]["enabled"] is True
        assert plugin.secret_types["ssh_private_keys"]["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_policy_decision_metadata_structure(self):
        """Test PolicyDecision metadata structure matches requirements."""
        config = {"action": "block", "secret_types": {"aws_access_keys": {"enabled": True}}}
        plugin = BasicSecretsFilterPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file", "arguments": {"content": "AKIAIOSFODNN7EXAMPLE"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        
        # Verify metadata structure
        assert decision.metadata["secret_detected"] is True
        assert decision.metadata["detection_mode"] == "block"
        assert "detections" in decision.metadata
        assert len(decision.metadata["detections"]) > 0
        
        detection = decision.metadata["detections"][0]
        assert "type" in detection
        assert "pattern" in detection
        assert "position" in detection
        assert "action" in detection
        assert "confidence" in detection
        
        assert detection["type"] == "aws_access_keys"
        assert detection["confidence"] == "high"
        assert detection["action"] == "block"  # Uses action value directly
    
    @pytest.mark.asyncio
    async def test_redact_mode_functionality(self):
        """Test redact mode replaces secrets with placeholder."""
        config = {"action": "redact", "secret_types": {"aws_access_keys": {"enabled": True}}}
        plugin = BasicSecretsFilterPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file", "arguments": {"content": "My secret: AKIAIOSFODNN7EXAMPLE"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        
        assert decision.allowed is True
        assert "Secret redacted" in decision.reason
        assert decision.metadata["secret_detected"] is True
        assert decision.metadata["detection_mode"] == "redact"
        # Note: Redaction happens on responses, not requests, so we just verify the decision
    
    def test_false_positive_prevention(self):
        """Test that common non-secret patterns are not flagged."""
        config = {
            "action": "block",
            "secret_types": {
                "aws_access_keys": {"enabled": True},
                "github_tokens": {"enabled": True},
                "google_api_keys": {"enabled": True}
            }
        }
        plugin = BasicSecretsFilterPlugin(config)
        
        # Common patterns that should NOT be detected as secrets
        false_positive_patterns = [
            "This is normal text",
            "example@email.com", 
            "https://github.com/user/repo",
            "console.log('Hello World')",
            "function myFunction() { return true; }",
            "EXAMPLE_CONSTANT_VALUE",
            "API_KEY_PLACEHOLDER",
            "var token = 'placeholder_token';"
        ]
        
        for text in false_positive_patterns:
            detections = plugin._detect_secrets_in_text(text)
            assert len(detections) == 0, f"Should not detect secrets in: '{text}'"


class TestSecretsFilterIntegration:
    """Test integration with plugin architecture."""
    
    def test_plugin_registration(self):
        """Test that plugin is properly registered in POLICIES."""
        from watchgate.plugins.security.secrets import POLICIES
        
        assert "secrets" in POLICIES
        assert POLICIES["secrets"] == BasicSecretsFilterPlugin
    
    @pytest.mark.asyncio
    async def test_notification_handling(self):
        """Test that notifications are handled properly."""
        config = {"action": "block"}
        plugin = BasicSecretsFilterPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="notifications/test",
            params={"message": "AKIAIOSFODNN7EXAMPLE"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        # Notifications with secrets should be blocked
        assert decision.allowed is False
        assert "secrets detected" in decision.reason.lower()
        assert decision.metadata["secret_detected"] is True
        assert len(decision.metadata["detections"]) > 0
        assert decision.metadata["detection_mode"] == "block"
