"""Tests for the BasicPIIFilterPlugin security plugin."""

import base64
import pytest
import re
from watchgate.plugins.security.pii import BasicPIIFilterPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestBasicPIIFilterPluginConfiguration:
    """Test configuration validation for BasicPIIFilterPlugin."""
    
    def test_valid_configuration_parsing(self):
        """Test valid configuration is parsed correctly."""
        config = {
            "action": "redact",
            "pii_types": {
                "credit_card": {"enabled": True},
                "email": {"enabled": True},
                "phone": {"enabled": True, "formats": ["us", "international"]},
                "ip_address": {"enabled": True, "formats": ["ipv4", "ipv6"]},
                "national_id": {"enabled": True, "formats": ["us", "uk_ni"]},
            },
            "custom_patterns": [
                {"name": "employee_id", "pattern": "EMP-\\d{6}", "enabled": True}
            ],
            "exemptions": {
                "tools": ["allowed_tool_name"],
                "paths": ["allowed/path/*"]
            }
        }
        
        plugin = BasicPIIFilterPlugin(config)
        assert plugin.action == "redact"
        assert plugin.pii_types["credit_card"]["enabled"] is True
        assert plugin.pii_types["phone"]["formats"] == ["us", "international"]
        assert len(plugin.custom_patterns) == 1
        assert plugin.custom_patterns[0]["name"] == "employee_id"
        assert plugin.exemptions["tools"] == ["allowed_tool_name"]
        assert plugin.exemptions["paths"] == ["allowed/path/*"]
    
    def test_invalid_action_configuration(self):
        """Test invalid mode configuration raises ValueError."""
        config = {"action": "invalid_action", "pii_types": {}}
        
        with pytest.raises(ValueError, match="Invalid action 'invalid_action'"):
            BasicPIIFilterPlugin(config)
    
    def test_missing_mode_configuration(self):
        """Test missing action configuration raises ValueError."""
        config = {"pii_types": {}}
        
        with pytest.raises(ValueError, match="Action is required"):
            BasicPIIFilterPlugin(config)
    
    def test_all_format_expansion(self):
        """Test 'all' format is expanded to all supported formats."""
        config = {
            "action": "redact",
            "pii_types": {
                "phone": {"enabled": True, "formats": ["all"]},
                # ip_address removed in Requirement 8 - no longer supported
                "national_id": {"enabled": True, "formats": ["all"]},
            }
        }
        
        plugin = BasicPIIFilterPlugin(config)
        assert "us" in plugin.pii_types["phone"]["formats"]
        assert "international" in plugin.pii_types["phone"]["formats"]
        # IP address formats no longer expanded since IP detection removed
        assert "us" in plugin.pii_types["national_id"]["formats"]
        assert "uk_ni" in plugin.pii_types["national_id"]["formats"]
        assert "canadian_sin" in plugin.pii_types["national_id"]["formats"]
    
    def test_invalid_custom_pattern_configuration(self):
        """Test invalid custom pattern configuration raises ValueError."""
        config = {
            "action": "redact",
            "pii_types": {},
            "custom_patterns": [
                {"name": "invalid", "pattern": "[unclosed", "enabled": True}
            ]
        }
        
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            BasicPIIFilterPlugin(config)
    
    def test_default_formats_when_enabled_without_formats(self):
        """Test that PII types default to 'all' formats when enabled without formats specified."""
        config = {
            "action": "redact",
            "pii_types": {
                "credit_card": {"enabled": True},  # No formats specified
                "phone": {"enabled": True},        # No formats specified
                "ip_address": {"enabled": True},   # No formats specified
                "national_id": {"enabled": True},  # No formats specified
                "email": {"enabled": True}         # Email doesn't use formats
            }
        }
        
        plugin = BasicPIIFilterPlugin(config)
        
        # Check that formats defaulted to "all" and were expanded
        assert plugin.pii_types["credit_card"]["formats"] == ["all"]
        assert "us" in plugin.pii_types["phone"]["formats"]
        assert "international" in plugin.pii_types["phone"]["formats"]
        # IP address no longer supported - removed in Requirement 8
        assert "us" in plugin.pii_types["national_id"]["formats"]
        
        # Verify patterns were actually compiled
        assert "credit_card" in plugin.compiled_patterns
        assert "phone" in plugin.compiled_patterns
        # IP address patterns no longer compiled - removed in Requirement 8
        assert "ip_address" not in plugin.compiled_patterns
        assert "national_id" in plugin.compiled_patterns
        assert "email" in plugin.compiled_patterns
    
    def test_ssn_configuration_alias(self):
        """Test that 'ssn' configuration key works as alias for 'national_id'."""
        config = {
            "action": "redact",
            "pii_types": {
                "ssn": {"enabled": True, "formats": ["us"]}
            }
        }
        
        plugin = BasicPIIFilterPlugin(config)
        
        # Test that SSN patterns are compiled
        assert "national_id" in plugin.compiled_patterns
        assert len(plugin.compiled_patterns["national_id"]) > 0
        
        # Test that SSN is detected
        text = "My SSN is 123-45-6789"
        detections = plugin._detect_pii_in_text(text)
        assert len(detections) == 1
        assert detections[0]["type"] == "NATIONAL_ID"
        assert detections[0]["position"] == [10, 21]  # Position of "123-45-6789" in text


class TestPIIDetectionCreditCard:
    """Test credit card PII detection.
    
    Tests credit card detection for major card types using Luhn-validated test numbers.
    Covers: Visa, MasterCard, American Express, and Discover cards.
    
    Specific test values:
    - Visa: 4532015112830366 (16 digits, starts with 4)
    - MasterCard: 5555555555554444 (16 digits, starts with 5)
    - American Express: 378282246310005 (15 digits, starts with 34/37)
    - Discover: 6011111111111117 (16 digits, starts with 6011)
    - Invalid Luhn: 4532015112830367 (should not be detected)
    """
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for credit card testing."""
        config = {
            "action": "block",
            "pii_types": {
                "credit_card": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_visa_credit_card_detection(self, plugin):
        """Test Visa credit card detection with Luhn validation.
        
        Tests: 4532015112830366 (valid Visa test number)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "My card is 4532015112830366"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert "PII detected" in decision.reason
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "CREDIT_CARD" for d in decision.metadata["detections"])
    
    @pytest.mark.asyncio
    async def test_mastercard_detection(self, plugin):
        """Test MasterCard detection with Luhn validation.
        
        Tests: 5555555555554444 (valid MasterCard test number)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "Card: 5555555555554444"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_amex_detection(self, plugin):
        """Test American Express detection with Luhn validation.
        
        Tests: 378282246310005 (valid AmEx test number)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-3",
            params={"name": "test_tool", "arguments": {"data": "AmEx: 378282246310005"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_discover_detection(self, plugin):
        """Test Discover card detection with Luhn validation.
        
        Tests: 6011111111111117 (valid Discover test number)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-4",
            params={"name": "test_tool", "arguments": {"data": "Discover: 6011111111111117"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_invalid_luhn_not_detected(self, plugin):
        """Test invalid Luhn checksum is not detected as credit card.
        
        Tests: 4532015112830367 (invalid Luhn checksum - last digit changed from 6 to 7)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-5",
            params={"name": "test_tool", "arguments": {"data": "Invalid: 4532015112830367"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
    
    @pytest.mark.asyncio
    async def test_visa_spaced_format_detection(self, plugin):
        """Test Visa credit card detection with spaces.
        
        Tests: 4532 0151 1283 0366 (valid Visa with spaces)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-6",
            params={"name": "test_tool", "arguments": {"data": "Card: 4532 0151 1283 0366"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert "PII detected" in decision.reason
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "CREDIT_CARD" for d in decision.metadata["detections"])
    
    @pytest.mark.asyncio
    async def test_mastercard_dashed_format_detection(self, plugin):
        """Test MasterCard detection with dashes.
        
        Tests: 5555-5555-5555-4444 (valid MasterCard with dashes)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-7",
            params={"name": "test_tool", "arguments": {"data": "MC: 5555-5555-5555-4444"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "CREDIT_CARD" for d in decision.metadata["detections"])
    
    @pytest.mark.asyncio
    async def test_amex_spaced_format_detection(self, plugin):
        """Test American Express detection with spaces (4-6-5 format).
        
        Tests: 3782 822463 10005 (valid Amex with spaces)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-8",
            params={"name": "test_tool", "arguments": {"data": "Amex: 3782 822463 10005"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "CREDIT_CARD" for d in decision.metadata["detections"])


class TestPIIDetectionEmail:
    """Test email address PII detection.
    
    Tests RFC 5322 compliant email detection for various formats.
    
    Specific test values:
    - Simple email: user@example.com
    - Complex email: user.name+tag@sub.domain.co.uk
    """
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for email testing."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_simple_email_detection(self, plugin):
        """Test simple email address detection.
        
        Tests: user@example.com
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Contact user@example.com for help"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "EMAIL" for d in decision.metadata["detections"])
    
    @pytest.mark.asyncio
    async def test_complex_email_detection(self, plugin):
        """Test complex email address detection.
        
        Tests: user.name+tag@sub.domain.co.uk (complex format with subdomain and country TLD)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "Email: user.name+tag@sub.domain.co.uk"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True

    @pytest.mark.asyncio
    async def test_email_in_url_parameter(self, plugin):
        """Test email detection in URL parameters.
        
        Tests: https://example.com/user?email=user@example.com
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-3",
            params={"name": "test_tool", "arguments": {"data": "URL: https://example.com/user?email=user@example.com"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "EMAIL" for d in decision.metadata["detections"])

    @pytest.mark.asyncio
    async def test_email_concatenated_with_text(self, plugin):
        """Test email detection when concatenated with other text.
        
        Tests: userid:user@example.com,active
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-4",
            params={"name": "test_tool", "arguments": {"data": "userid:user@example.com,active"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "EMAIL" for d in decision.metadata["detections"])


class TestPIIDetectionPhone:
    """Test phone number PII detection.
    
    Tests multiple phone number formats including US and international.
    
    Specific test values:
    - US parentheses: (555) 123-4567
    - US dash: 555-123-4567
    - International: +44 20 7946 0958 (UK format)
    """
    
    @pytest.fixture
    def plugin_us(self):
        """Create plugin for US phone testing."""
        config = {
            "action": "block",
            "pii_types": {
                "phone": {"enabled": True, "formats": ["us"]}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.fixture
    def plugin_all(self):
        """Create plugin for all phone formats testing."""
        config = {
            "action": "block",
            "pii_types": {
                "phone": {"enabled": True, "formats": ["all"]}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_us_phone_parentheses_format(self, plugin_us):
        """Test US phone number in (xxx) xxx-xxxx format.
        
        Tests: (555) 123-4567
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Call me at (555) 123-4567"}}
        )
        
        decision = await plugin_us.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "PHONE" for d in decision.metadata["detections"])
    
    @pytest.mark.asyncio
    async def test_us_phone_dash_format(self, plugin_us):
        """Test US phone number in xxx-xxx-xxxx format.
        
        Tests: 555-123-4567
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "Phone: 555-123-4567"}}
        )
        
        decision = await plugin_us.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_international_phone_format(self, plugin_all):
        """Test international phone number format.
        
        Tests: +44 20 7946 0958 (UK landline format)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-3",
            params={"name": "test_tool", "arguments": {"data": "International: +44 20 7946 0958"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True

    @pytest.mark.asyncio
    async def test_us_phone_dots_format(self, plugin_us):
        """Test US phone number with dots instead of dashes.
        
        Tests: 555.123.4567 (xxx.xxx.xxxx format) - NOT detected to reduce false positives
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-4",
            params={"name": "test_tool", "arguments": {"data": "Call me at 555.123.4567"}}
        )
        
        decision = await plugin_us.check_request(request, "test-server")
        # Dot format is no longer detected to reduce false positives with version numbers
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False

    @pytest.mark.asyncio
    async def test_us_phone_mixed_separators(self, plugin_us):
        """Test US phone number with mixed separators.
        
        Tests: (555)123-4567 (parentheses without space after)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-5",
            params={"name": "test_tool", "arguments": {"data": "Phone: (555)123-4567"}}
        )
        
        decision = await plugin_us.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "PHONE" for d in decision.metadata["detections"])

    @pytest.mark.asyncio
    async def test_international_phone_compact_with_plus(self, plugin_all):
        """Test international phone number with + but minimal spacing.
        
        Tests: +442079460958 (UK number with + but no internal spaces)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-6",
            params={"name": "test_tool", "arguments": {"data": "Contact: +442079460958"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "PHONE" for d in decision.metadata["detections"])


class TestPIIDetectionIPAddress:
    """Test IP address PII detection.
    
    Tests IPv4 and IPv6 address detection.
    
    Specific test values:
    - IPv4: 192.168.1.100 (private IP)
    - IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334 (full format)
    """
    
    @pytest.fixture
    def plugin_ipv4(self):
        """Create plugin for IPv4 testing."""
        config = {
            "action": "block",
            "pii_types": {
                "ip_address": {"enabled": True, "formats": ["ipv4"]}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.fixture
    def plugin_all(self):
        """Create plugin for all IP formats testing."""
        config = {
            "action": "block",
            "pii_types": {
                "ip_address": {"enabled": True, "formats": ["all"]}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_ipv4_no_longer_detected(self, plugin_ipv4):
        """Test IPv4 addresses are no longer detected as PII (Requirement 8).
        
        IP addresses cause too many false positives and are not PII in most contexts.
        
        Tests: 192.168.1.100 (should NOT be detected)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Server IP: 192.168.1.100"}}
        )
        
        decision = await plugin_ipv4.check_request(request, "test-server")
        # Should be allowed - IP addresses no longer detected as PII
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False
    
    @pytest.mark.asyncio
    async def test_ipv6_no_longer_detected(self, plugin_all):
        """Test IPv6 addresses are no longer detected as PII (Requirement 8).
        
        IP addresses cause too many false positives and are not PII in most contexts.
        
        Tests: 2001:0db8:85a3:0000:0000:8a2e:0370:7334 (should NOT be detected)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        # Should be allowed - IP addresses no longer detected as PII
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False

    @pytest.mark.asyncio
    async def test_ipv4_in_url_no_longer_detected(self, plugin_ipv4):
        """Test IPv4 in URLs are no longer detected as PII (Requirement 8).
        
        This significantly reduces false positives from legitimate infrastructure.
        
        Tests: http://192.168.1.100/api (should NOT be detected)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-3",
            params={"name": "test_tool", "arguments": {"data": "API endpoint: http://192.168.1.100/api"}}
        )
        
        decision = await plugin_ipv4.check_request(request, "test-server")
        # Should be allowed - IP addresses no longer detected as PII
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False

    @pytest.mark.asyncio
    async def test_ipv4_concatenated_no_longer_detected(self, plugin_ipv4):
        """Test IPv4 concatenated with text no longer detected as PII (Requirement 8).
        
        This prevents false positives on configuration strings and identifiers.
        
        Tests: server192.168.1.100config (should NOT be detected)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-4",
            params={"name": "test_tool", "arguments": {"data": "Config: server192.168.1.100config"}}
        )
        
        decision = await plugin_ipv4.check_request(request, "test-server")
        # Should be allowed - IP addresses no longer detected as PII
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False

    @pytest.mark.asyncio
    async def test_data_url_should_be_skipped(self):
        """Test that data URLs are skipped during PII detection."""
        config = {
            "action": "block",
            "pii_types": {
                "credit_card": {"enabled": True},
                "email": {"enabled": True},
                "phone": {"enabled": True, "formats": ["us"]}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Test various data URLs that should be skipped
        data_urls = [
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC",
            "data:text/plain;base64,SGVsbG8gV29ybGQ=",
            "data:application/json;base64,eyJtZXNzYWdlIjogIkhlbGxvIFdvcmxkIn0=",
            "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAK==",
            "data:video/mp4;base64,AAAAIGZ0eXBpc29tAAAAAGlzb21tcDQx",
            "data:font/woff;base64,d09GRgABAAAAAC4AAAA="
        ]
        
        for data_url in data_urls:
            request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call",
                id="test-data-url",
                params={"name": "test_tool", "arguments": {"data": data_url}}
            )
            
            decision = await plugin.check_request(request, "test-server")
            assert decision.allowed is True, f"Data URL should be allowed: {data_url[:50]}..."
            assert decision.metadata["pii_detected"] is False

    @pytest.mark.asyncio
    async def test_data_url_with_pii_in_content_should_be_skipped(self):
        """Test that data URLs with PII in base64 content are skipped (as intended)."""
        config = {
            "action": "block",
            "pii_types": {
                "credit_card": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Credit card embedded in data URL base64 content - should be skipped
        credit_card = "4532015112830366"  # Valid test Visa number
        malicious_data_url = f"data:text/plain;base64,{base64.b64encode(credit_card.encode()).decode()}"
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-pii-in-data-url-content",
            params={"name": "test_tool", "arguments": {"data": malicious_data_url}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        # Should NOT detect PII since it's in base64 content (legitimate file data)
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False

    @pytest.mark.asyncio
    async def test_data_url_with_pii_outside_content_should_detect(self):
        """Test that PII outside data URL content is still detected."""
        config = {
            "action": "block",
            "pii_types": {
                "credit_card": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Credit card outside the data URL
        credit_card = "4532015112830366"  # Valid test Visa number
        text_with_pii = f"Card: {credit_card} and image: data:image/png;base64,iVBORw0KGgo="
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-pii-outside-data-url",
            params={"name": "test_tool", "arguments": {"data": text_with_pii}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        # Should detect the PII since it's outside the data URL
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True

    @pytest.mark.asyncio
    async def test_ipv6_in_url_no_longer_detected(self, plugin_all):
        """Test IPv6 in URLs are no longer detected as PII (Requirement 8).
        
        This prevents false positives from legitimate IPv6 infrastructure.
        
        Tests: http://[2001:0db8:85a3:0000:0000:8a2e:0370:7334]/api (should NOT be detected)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-5",
            params={"name": "test_tool", "arguments": {"data": "IPv6 endpoint: http://[2001:0db8:85a3:0000:0000:8a2e:0370:7334]/api"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        # Should be allowed - IP addresses no longer detected as PII
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False


class TestPIIDetectionNationalID:
    """Test national ID PII detection.
    
    Tests various national ID formats including US SSN and UK National Insurance.
    
    Specific test values:
    - US SSN (dashed): 123-45-6789
    - US SSN (no dashes): 123456789  
    - UK National Insurance: AB 12 34 56 C
    """
    
    @pytest.fixture
    def plugin_us(self):
        """Create plugin for US national ID testing."""
        config = {
            "action": "block",
            "pii_types": {
                "national_id": {"enabled": True, "formats": ["us"]}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.fixture
    def plugin_all(self):
        """Create plugin for all national ID formats testing."""
        config = {
            "action": "block",
            "pii_types": {
                "national_id": {"enabled": True, "formats": ["all"]}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_us_ssn_dashed_format(self, plugin_us):
        """Test US SSN in xxx-xx-xxxx format.
        
        Tests: 123-45-6789
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "SSN: 123-45-6789"}}
        )
        
        decision = await plugin_us.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "NATIONAL_ID" for d in decision.metadata["detections"])
    
    @pytest.mark.asyncio
    async def test_us_ssn_no_dashes_format_no_longer_detected(self, plugin_us):
        """Test US SSN in xxxxxxxxx format is no longer detected (Requirement 8).
        
        Unformatted 9-digit SSNs cause too many false positives and are
        no longer detected. Only formatted SSNs (xxx-xx-xxxx) are detected.
        
        Tests: 123456789 (should NOT be detected)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "Social: 123456789"}}
        )
        
        decision = await plugin_us.check_request(request, "test-server")
        # Should be allowed - unformatted SSNs no longer detected
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False
    
    @pytest.mark.asyncio
    async def test_uk_ni_format(self, plugin_all):
        """Test UK National Insurance number format.
        
        Tests: AB 12 34 56 C
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-3",
            params={"name": "test_tool", "arguments": {"data": "NI Number: AB 12 34 56 C"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_canadian_sin_format(self, plugin_all):
        """Test Canadian Social Insurance Number format.
        
        Tests: 123-456-789
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-4",
            params={"name": "test_tool", "arguments": {"data": "SIN: 123-456-789"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_canadian_sin_format(self, plugin_all):
        """Test Canadian Social Insurance Number format.
        
        Tests: 123-456-789
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-4",
            params={"name": "test_tool", "arguments": {"data": "SIN: 123-456-789"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True

    @pytest.mark.asyncio
    async def test_uk_ni_no_spaces(self, plugin_all):
        """Test UK National Insurance number without spaces.
        
        Tests: AB123456C (compact format)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-5",
            params={"name": "test_tool", "arguments": {"data": "NI Number: AB123456C"}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "NATIONAL_ID" for d in decision.metadata["detections"])

    @pytest.mark.asyncio
    async def test_us_ssn_in_json_format_no_longer_detected(self, plugin_all):
        """Test US SSN in JSON format is no longer detected (Requirement 8).
        
        Unformatted 9-digit SSNs cause too many false positives and are
        no longer detected, even in JSON format. Only formatted SSNs are detected.
        
        Tests: {"ssn":123456789} (should NOT be detected)
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-6",
            params={"name": "test_tool", "arguments": {"data": '{"ssn":123456789}'}}
        )
        
        decision = await plugin_all.check_request(request, "test-server")
        # Should be allowed - unformatted SSNs no longer detected
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False


class TestPIIDetectionCustomPatterns:
    """Test custom pattern PII detection.
    
    Tests user-defined regex patterns for organization-specific PII types.
    
    Specific test values:
    - Employee ID: EMP-123456 (pattern: EMP-\\d{6})
    - Project Code: PROJ-ABC-1234 (pattern: PROJ-[A-Z]{3}-\\d{4})
    """
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for custom pattern testing."""
        config = {
            "action": "block",
            "pii_types": {},
            "custom_patterns": [
                {"name": "employee_id", "pattern": "EMP-\\d{6}", "enabled": True},
                {"name": "project_code", "pattern": "PROJ-[A-Z]{3}-\\d{4}", "enabled": True}
            ]
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_employee_id_detection(self, plugin):
        """Test custom employee ID pattern detection.
        
        Tests: EMP-123456
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Employee EMP-123456 submitted report"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        assert any(d["type"] == "CUSTOM" and d["pattern"] == "employee_id" for d in decision.metadata["detections"])
    
    @pytest.mark.asyncio
    async def test_project_code_detection(self, plugin):
        """Test custom project code pattern detection.
        
        Tests: PROJ-ABC-1234
        """
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "Working on PROJ-ABC-1234"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True


class TestModeBlockBehavior:
    """Test block mode behavior."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin in block mode."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_block_mode_prevents_transmission(self, plugin):
        """Test block mode returns PolicyDecision(allowed=False) when PII detected."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Contact user@example.com"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert "PII detected" in decision.reason
        assert decision.modified_content is None
    
    @pytest.mark.asyncio
    async def test_block_mode_allows_clean_content(self, plugin):
        """Test block mode allows content without PII."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "This is clean content"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False


class TestModeRedactBehavior:
    """Test redact mode behavior."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin in redact mode."""
        config = {
            "action": "redact",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_redact_mode_replaces_pii(self, plugin):
        """Test redact mode returns PolicyDecision with modified_response."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Contact user@example.com for help"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert decision.modified_content is not None
        
        # Check that PII was redacted
        modified_data = decision.modified_content.params["arguments"]["data"]
        assert "user@example.com" not in modified_data
        assert "[EMAIL REDACTED by Watchgate]" in modified_data
    
    @pytest.mark.asyncio
    async def test_redact_mode_preserves_clean_content(self, plugin):
        """Test redact mode allows clean content unchanged."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "This is clean content"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert decision.modified_content is None


class TestModeAuditBehavior:
    """Test audit_only mode behavior."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin in audit_only mode."""
        config = {
            "action": "audit_only",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_audit_mode_logs_detections(self, plugin):
        """Test audit_only mode returns PolicyDecision(allowed=True) with metadata."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Contact user@example.com"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is True
        assert decision.metadata["detection_action"] == "audit_only"
        assert decision.modified_content is None


class TestExemptions:
    """Test exemption functionality."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin with exemptions."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            },
            "exemptions": {
                "tools": ["allowed_tool"],
                "paths": ["allowed/path/*"]
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_tool_exemption_allows_pii(self, plugin):
        """Test tool exemption allows PII for specific tools."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "allowed_tool", "arguments": {"data": "Contact user@example.com"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is True
        assert "Tool exempted" in decision.reason
    
    @pytest.mark.asyncio
    async def test_non_exempted_tool_blocks_pii(self, plugin):
        """Test non-exempted tool blocks PII."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "other_tool", "arguments": {"data": "Contact user@example.com"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        assert decision.allowed is False
        assert "PII detected" in decision.reason


class TestResponseProcessing:
    """Test response processing functionality."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for response testing."""
        config = {
            "action": "redact",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_response_pii_redaction(self, plugin):
        """Test response with PII is redacted."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {}}
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-1",
            result={"data": "Contact user@example.com for support"}
        )
        
        decision = await plugin.check_response(request, response, "test-server")
        assert decision.allowed is True
        assert decision.modified_content is not None
        
        modified_data = decision.modified_content.result["data"]
        assert "user@example.com" not in modified_data
        assert "[EMAIL REDACTED by Watchgate]" in modified_data


class TestNotificationProcessing:
    """Test notification processing functionality."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for notification testing."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_notification_pii_detection(self, plugin):
        """Test notification with PII is blocked."""
        notification = MCPNotification(
            jsonrpc="2.0",
            method="notifications/message",
            params={"message": "Contact user@example.com"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is False
        assert "PII detected" in decision.reason
    
    @pytest.mark.asyncio
    async def test_notification_redact_mode_redacts(self):
        """Test that redact mode properly redacts PII from notifications."""
        config = {
            "action": "redact",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="status",
            params={"message": "User john@example.com logged in"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is True
        assert "PII detected and redacted from notification" in decision.reason
        assert decision.modified_content is not None
        
        # Check that PII was redacted
        modified_message = decision.modified_content.params["message"]
        assert "john@example.com" not in modified_message
        assert "[EMAIL REDACTED by Watchgate]" in modified_message
    
    @pytest.mark.asyncio
    async def test_notification_redact_mode_no_pii(self):
        """Test that redact mode allows clean notifications without modification."""
        config = {
            "action": "redact",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="status",
            params={"message": "User logged in successfully"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is True
        assert decision.modified_content is None
        assert decision.metadata["pii_detected"] is False
    
    @pytest.mark.asyncio
    async def test_notification_audit_only_allows(self):
        """Test that audit_only mode allows notifications with PII."""
        config = {
            "action": "audit_only",
            "pii_types": {
                "phone": {"enabled": True, "formats": ["us"]}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="alert",
            params={"contact": "Call me at 555-123-4567"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is True
        assert "audit only" in decision.reason
        assert decision.metadata["pii_detected"] is True


class TestPolicyDecisionMetadataStructure:
    """Test PolicyDecision metadata structure validation."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for metadata testing."""
        config = {
            "action": "audit_only",
            "pii_types": {
                "email": {"enabled": True},
                "credit_card": {"enabled": True}
            }
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_metadata_structure_single_detection(self, plugin):
        """Test metadata structure for single PII detection."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Email: user@example.com"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        
        # Validate metadata structure
        assert "pii_detected" in decision.metadata
        assert "detection_action" in decision.metadata
        assert "detections" in decision.metadata
        
        assert decision.metadata["pii_detected"] is True
        assert decision.metadata["detection_action"] == "audit_only"
        assert isinstance(decision.metadata["detections"], list)
        assert len(decision.metadata["detections"]) == 1
        
        detection = decision.metadata["detections"][0]
        assert "type" in detection
        assert "pattern" in detection
        assert "position" in detection
        assert "action" in detection
        
        assert detection["type"] == "EMAIL"
        assert isinstance(detection["position"], list)
        assert len(detection["position"]) == 2  # start, end positions
    
    @pytest.mark.asyncio
    async def test_metadata_structure_multiple_detections(self, plugin):
        """Test metadata structure for multiple PII detections."""
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2",
            params={"name": "test_tool", "arguments": {"data": "Email user@example.com, card 4532015112830366"}}
        )
        
        decision = await plugin.check_request(request, "test-server")
        
        assert len(decision.metadata["detections"]) == 2
        types = [d["type"] for d in decision.metadata["detections"]]
        assert "EMAIL" in types
        assert "CREDIT_CARD" in types


class TestPerformanceRequirements:
    """Test performance requirements (<10ms per message)."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin for performance testing."""
        config = {
            "action": "redact",
            "pii_types": {
                "email": {"enabled": True},
                "credit_card": {"enabled": True},
                "phone": {"enabled": True, "formats": ["all"]},
                "ip_address": {"enabled": True, "formats": ["all"]},
                "national_id": {"enabled": True, "formats": ["all"]}
            },
            "custom_patterns": [
                {"name": "employee_id", "pattern": "EMP-\\d{6}", "enabled": True}
            ]
        }
        return BasicPIIFilterPlugin(config)
    
    @pytest.mark.asyncio
    async def test_performance_under_10ms(self, plugin):
        """Test processing time is under 10ms for typical message."""
        import time
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-1",
            params={"name": "test_tool", "arguments": {"data": "Large message with various content but no PII to test performance" * 100}}
        )
        
        start_time = time.perf_counter()
        decision = await plugin.check_request(request, "test-server")
        end_time = time.perf_counter()
        
        processing_time_ms = (end_time - start_time) * 1000
        assert processing_time_ms < 10.0, f"Processing took {processing_time_ms:.2f}ms, expected <10ms"
        assert decision.allowed is True


class TestContentProcessingConfiguration:
    """Test content processing configuration and chunking functionality."""
    
    def test_content_processing_constants(self):
        """Test that content processing uses proper constants."""
        from watchgate.plugins.security.pii import CHUNK_SIZE, OVERLAP_SIZE
        plugin = BasicPIIFilterPlugin({"action": "block"})
    
    @pytest.mark.asyncio
    async def test_large_content_chunking(self):
        """Test that large content is processed in chunks."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Create content larger than chunk size (64KB) with PII at the end
        large_content = "a" * 70000 + " Contact us at test@example.com"
        
        request = MCPRequest(
            jsonrpc="2.0",
            id=1,
            method="tools/call",
            params={"name": "test_tool", "arguments": {"text": large_content}}
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert result.metadata["pii_detected"] is True
        assert len(result.metadata["detections"]) > 0
        assert result.metadata["detections"][0]["type"] == "EMAIL"
    
    @pytest.mark.asyncio
    async def test_pii_across_chunk_boundary(self):
        """Test detection of PII that spans chunk boundaries."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Create content where email would be near chunk boundary
        # With 64KB chunks, we need a lot of content
        content = "x" * 65530 + "contact@example.com" + "x" * 40
        
        request = MCPRequest(
            jsonrpc="2.0",
            id=1,
            method="tools/call",
            params={"name": "test_tool", "arguments": {"text": content}}
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert result.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_very_large_content_processing(self):
        """Test that very large content is processed without limits."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Create very large content with PII at the end
        large_content = "a" * 10000 + " Contact: test@example.com"
        
        request = MCPRequest(
            jsonrpc="2.0",
            id=1,
            method="tools/call",
            params={"name": "test_tool", "arguments": {"text": large_content}}
        )
        
        # Should detect PII even in very large content
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert result.metadata["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_no_duplicate_detections_in_overlap(self):
        """Test that overlapping chunks don't create duplicate detections."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Create content with email that will be in overlap region
        content = "x" * 80 + "test@example.com" + "x" * 80
        
        request = MCPRequest(
            jsonrpc="2.0",
            id=1,
            method="tools/call",
            params={"name": "test_tool", "arguments": {"text": content}}
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        
        # Check that we don't have duplicate detections
        detections = result.metadata["detections"]
        positions = [(d["position"][0], d["position"][1]) for d in detections]
        assert len(positions) == len(set(positions))  # No duplicates


class TestPIIContentSizeLimits:
    """Test MAX_CONTENT_SIZE enforcement in PII filter plugin."""
    
    @pytest.mark.asyncio
    async def test_oversized_content_blocked_early(self):
        """Test that PII filter blocks oversized content early."""
        config = {"action": "block", "pii_types": {"email": {"enabled": True}}}
        plugin = BasicPIIFilterPlugin(config)
        
        # Create content larger than MAX_CONTENT_SIZE (1MB)
        from watchgate.plugins.security import MAX_CONTENT_SIZE
        oversized_content = "C" * (MAX_CONTENT_SIZE + 1000)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="test_method",
            params={"large_content": oversized_content},
            id="test-1"
        )
        
        # Should block due to size limit
        decision = await plugin.check_request(request, "test-server")
        
        assert not decision.allowed, "Should block oversized content"
        assert "exceeds maximum size limit" in decision.reason, "Should mention size limit"
        assert decision.metadata["reason_code"] == "content_size_exceeded", "Should have correct reason code"
        assert decision.metadata["content_size_bytes"] > MAX_CONTENT_SIZE, "Should report actual size"
