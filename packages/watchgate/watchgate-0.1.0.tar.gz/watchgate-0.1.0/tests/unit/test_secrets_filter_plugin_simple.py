"""Tests for the BasicSecretsFilterPlugin security plugin."""

import pytest
from watchgate.plugins.security.secrets import BasicSecretsFilterPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestBasicSecretsFilterPluginConfiguration:
    """Test configuration validation for BasicSecretsFilterPlugin."""
    
    def test_valid_configuration_parsing(self):
        """Test valid secrets detection configuration loading with all supported types."""
        config = {
            "action": "block",
            "secret_types": {
                "aws_access_keys": {"enabled": True},
                "github_tokens": {"enabled": True},
                "google_api_keys": {"enabled": True},
                "jwt_tokens": {"enabled": True},
                "ssh_private_keys": {"enabled": True},
                "aws_secret_keys": {"enabled": False}
            },
            "entropy_detection": {
                "enabled": True,
                "min_entropy": 5.5,
                "min_length": 32,
                "max_length": 200
            },
            "custom_patterns": [
                {"name": "company_api_key", "pattern": "COMP-[A-Za-z0-9]{32}", "enabled": True}
            ],
            "allowlist": {
                "patterns": ["test_key_*", "demo_token_*"]
            },
            "exemptions": {
                "tools": ["development_tool"],
                "paths": ["test/*", "examples/*"]
            }
        }
        
        plugin = BasicSecretsFilterPlugin(config)
        assert plugin.action == "block"
        assert plugin.secret_types["aws_access_keys"]["enabled"] is True
        assert plugin.secret_types["aws_secret_keys"]["enabled"] is False
        assert plugin.entropy_detection["enabled"] is True
        assert plugin.entropy_detection["min_entropy"] == 5.5
        assert len(plugin.custom_patterns) == 1
        assert plugin.custom_patterns[0]["name"] == "company_api_key"

    def test_invalid_configuration_handling(self):
        """Test error handling for invalid configurations and malformed patterns."""
        # Test that empty config uses defaults
        plugin = BasicSecretsFilterPlugin({})
        assert plugin.action == "block"  # Default action
        
        # Test invalid action
        with pytest.raises(ValueError, match="Invalid action"):
            BasicSecretsFilterPlugin({"action": "invalid_action"})
    
    def test_secret_type_specific_configuration(self):
        """Test enabling/disabling specific secret types individually."""
        config = {
            "action": "block",
            "secret_types": {
                "aws_access_keys": {"enabled": True},
                "github_tokens": {"enabled": False}
            }
        }
        
        plugin = BasicSecretsFilterPlugin(config)
        assert plugin.secret_types["aws_access_keys"]["enabled"] is True
        assert plugin.secret_types["github_tokens"]["enabled"] is False


class TestBasicSecretsFilterPluginDetection:
    """Test secret detection functionality."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance for testing."""
        config = {
            "action": "block",
            "secret_types": {
                "aws_access_keys": {"enabled": True},
                "github_tokens": {"enabled": True},
                "google_api_keys": {"enabled": True},
                "jwt_tokens": {"enabled": True},
                "ssh_private_keys": {"enabled": True}
            },
            "entropy_detection": {
                "enabled": True,
                "min_entropy": 5.5,
                "min_length": 32,
                "max_length": 200
            }
        }
        return BasicSecretsFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_aws_access_key_detection(self, plugin):
        """Test AWS Access Key ID detection (AKIA pattern) - high confidence."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file", "arguments": {"content": "AKIAIOSFODNN7EXAMPLE"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert "Secret detected" in decision.reason
        assert decision.metadata["secret_detected"] is True
        assert decision.metadata["detections"][0]["type"] == "aws_access_keys"
    
    @pytest.mark.asyncio
    async def test_github_personal_access_token_detection(self, plugin):
        """Test GitHub Personal Access Token detection (ghp_ prefix) - high confidence."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call", 
            id="test-2",
            params={"name": "write_file", "arguments": {"content": "ghp_1234567890abcdef1234567890abcdef12345678"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert "Secret detected" in decision.reason
        assert decision.metadata["secret_detected"] is True
        assert decision.metadata["detections"][0]["type"] == "github_tokens"
    
    @pytest.mark.asyncio
    async def test_no_secrets_detected(self, plugin):
        """Test that normal content is allowed through."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-3",
            params={"name": "read_file", "arguments": {"content": "This is normal text with no secrets"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert "No secrets detected" in decision.reason


class TestBasicSecretsFilterPluginModes:
    """Test different plugin modes (block, redact, audit_only)."""
    
    @pytest.mark.asyncio
    async def test_block_mode_prevents_transmission(self):
        """Test block mode prevents message transmission when secrets detected."""
        config = {"action": "block", "secret_types": {"aws_access_keys": {"enabled": True}}}
        plugin = BasicSecretsFilterPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file", "arguments": {"content": "AKIAIOSFODNN7EXAMPLE"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.modified_content is None
    
    @pytest.mark.asyncio 
    async def test_redact_mode_replaces_secrets(self):
        """Test redact mode replaces secrets with standard placeholder."""
        config = {"action": "redact", "secret_types": {"aws_access_keys": {"enabled": True}}}
        plugin = BasicSecretsFilterPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1", 
            params={"name": "read_file", "arguments": {"content": "AKIAIOSFODNN7EXAMPLE"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert "Secret redacted" in decision.reason
        # Note: For requests, we'd need to test response redaction
    
    @pytest.mark.asyncio
    async def test_audit_only_mode_logs_without_blocking(self):
        """Test audit-only mode logs detections without blocking transmission."""
        config = {"action": "audit_only", "secret_types": {"aws_access_keys": {"enabled": True}}}
        plugin = BasicSecretsFilterPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "read_file", "arguments": {"content": "AKIAIOSFODNN7EXAMPLE"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert "Secret logged" in decision.reason
        assert decision.metadata["secret_detected"] is True
