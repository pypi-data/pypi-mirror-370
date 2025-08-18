"""Test PII pattern simplification for Requirement 8.

This test verifies that:
1. IP address detection is completely removed
2. SSN patterns require proper formatting (123-45-6789)
3. Phone patterns require proper formatting (parentheses/dashes, not plain digits)
4. Existing functionality is preserved for other PII types
"""

import pytest
from watchgate.plugins.security.pii import BasicPIIFilterPlugin
from watchgate.protocol.messages import MCPRequest


class TestPIIPatternSimplificationReq8:
    """Test PII pattern simplification requirements."""
    
    def test_ip_address_detection_completely_removed(self):
        """Test that IP address detection is completely removed."""
        config = {
            "action": "block",
            "pii_types": {
                "ip_address": {"enabled": True, "formats": ["ipv4", "ipv6"]}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # These should NOT be detected as PII anymore
        ip_test_cases = [
            "192.168.1.1",
            "10.0.0.1", 
            "127.0.0.1",
            "255.255.255.255",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "::1",
            "fe80::1"
        ]
        
        for ip_address in ip_test_cases:
            detections = plugin._detect_pii_in_text(ip_address)
            assert len(detections) == 0, f"IP address '{ip_address}' should NOT be detected as PII"
    
    def test_ip_patterns_not_compiled(self):
        """Test that IP patterns are not even compiled anymore."""
        config = {
            "action": "block", 
            "pii_types": {
                "ip_address": {"enabled": True, "formats": ["ipv4", "ipv6"]}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # IP address patterns should not exist in compiled patterns
        assert "ip_address" not in plugin.compiled_patterns, "IP address patterns should not be compiled"
    
    def test_ssn_requires_proper_formatting(self):
        """Test that SSN detection requires proper formatting."""
        config = {
            "action": "block",
            "pii_types": {
                "national_id": {"enabled": True, "formats": ["us"]}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Properly formatted SSNs should be detected
        formatted_ssns = [
            "123-45-6789",
            "987-65-4321",
            "555-12-3456"
        ]
        
        for ssn in formatted_ssns:
            detections = plugin._detect_pii_in_text(ssn)
            assert len(detections) > 0, f"Formatted SSN '{ssn}' should be detected"
            assert detections[0]["type"] == "NATIONAL_ID"
        
        # Unformatted SSNs (plain 9 digits) should NOT be detected
        unformatted_ssns = [
            "123456789",
            "987654321",
            "555123456"
        ]
        
        for ssn in unformatted_ssns:
            detections = plugin._detect_pii_in_text(ssn)
            assert len(detections) == 0, f"Unformatted SSN '{ssn}' should NOT be detected"
    
    def test_phone_requires_proper_formatting(self):
        """Test that phone detection requires proper formatting."""
        config = {
            "action": "block",
            "pii_types": {
                "phone": {"enabled": True, "formats": ["us"]}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Properly formatted phone numbers should be detected
        formatted_phones = [
            "(555) 123-4567",
            "555-123-4567",
            # "555.123.4567",  # Dot format removed to reduce false positives
            "(123) 456-7890"
        ]
        
        for phone in formatted_phones:
            detections = plugin._detect_pii_in_text(phone)
            assert len(detections) > 0, f"Formatted phone '{phone}' should be detected"
            assert detections[0]["type"] == "PHONE"
        
        # Dot format should NOT be detected anymore (false positive reduction)
        dot_phones = ["555.123.4567"]
        for phone in dot_phones:
            detections = plugin._detect_pii_in_text(phone)
            assert len(detections) == 0, f"Dot-formatted phone '{phone}' should NOT be detected"
        
        # Unformatted phones (plain 10 digits) should NOT be detected
        unformatted_phones = [
            "5551234567",
            "1234567890",
            "9876543210"
        ]
        
        for phone in unformatted_phones:
            detections = plugin._detect_pii_in_text(phone)
            assert len(detections) == 0, f"Unformatted phone '{phone}' should NOT be detected"
    
    def test_other_pii_types_still_work(self):
        """Test that other PII types still function correctly."""
        config = {
            "action": "block",
            "pii_types": {
                "email": {"enabled": True},
                "credit_card": {"enabled": True}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Email should still be detected
        email_detections = plugin._detect_pii_in_text("test@example.com")
        assert len(email_detections) > 0
        assert email_detections[0]["type"] == "EMAIL"
        
        # Valid credit card should still be detected (Luhn validated)
        cc_detections = plugin._detect_pii_in_text("4111111111111111")  # Valid test Visa
        assert len(cc_detections) > 0
        assert cc_detections[0]["type"] == "CREDIT_CARD"
    
    @pytest.mark.asyncio
    async def test_integration_with_policy_decision(self):
        """Test integration with PolicyDecision for simplified patterns."""
        config = {
            "action": "block",
            "pii_types": {
                "national_id": {"enabled": True, "formats": ["us"]},
                "phone": {"enabled": True, "formats": ["us"]},
                "ip_address": {"enabled": True, "formats": ["ipv4"]}  # Should be ignored
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # Test with content that has formatted SSN (should be blocked)
        request_with_formatted_ssn = MCPRequest(
            jsonrpc="2.0",
            method="tools/call", 
            id="test-1",
            params={"name": "read_file", "arguments": {"content": "My SSN is 123-45-6789"}}
        )
        
        decision = await plugin.check_request(request_with_formatted_ssn, "test-server")
        assert decision.allowed is False
        assert decision.metadata["pii_detected"] is True
        
        # Test with content that has unformatted SSN and IP (should be allowed)
        request_with_unformatted = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            id="test-2", 
            params={"name": "read_file", "arguments": {"content": "Data: 123456789 from 192.168.1.1"}}
        )
        
        decision = await plugin.check_request(request_with_unformatted, "test-server")
        assert decision.allowed is True
        assert decision.metadata["pii_detected"] is False
    
    def test_false_positive_reduction_with_simplified_patterns(self):
        """Test that simplified patterns reduce false positives."""
        config = {
            "action": "block",
            "pii_types": {
                "national_id": {"enabled": True, "formats": ["us"]},
                "phone": {"enabled": True, "formats": ["us"]},
                "ip_address": {"enabled": True, "formats": ["ipv4"]}  # Should be ignored
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # These should NOT trigger false positives anymore
        false_positive_cases = [
            "Server error code: 192168001",  # Looks like IP but isn't
            "Port 8080 on 127.0.0.1",       # Real IP but won't be detected
            "ID number: 123456789",         # Unformatted SSN
            "Call 5551234567 for support",  # Unformatted phone
            "Version 10.0.0.1 released",    # IP in version number
            "Process ID 987654321"          # 9-digit number
        ]
        
        for text in false_positive_cases:
            detections = plugin._detect_pii_in_text(text)
            assert len(detections) == 0, f"Should not detect PII in: '{text}'"
    
    def test_legitimate_formatted_patterns_still_detected(self):
        """Test that legitimate formatted patterns are still properly detected."""
        config = {
            "action": "block",
            "pii_types": {
                "national_id": {"enabled": True, "formats": ["us"]},
                "phone": {"enabled": True, "formats": ["us"]}
            }
        }
        plugin = BasicPIIFilterPlugin(config)
        
        # These legitimate formatted patterns should still be detected
        legitimate_cases = [
            ("SSN: 123-45-6789", "NATIONAL_ID"),
            ("Call (555) 123-4567", "PHONE"),
            ("Phone: 555-123-4567", "PHONE"), 
            ("Social Security Number 987-65-4321", "NATIONAL_ID"),
            # ("Contact at 555.123.4567", "PHONE")  # Dot format removed
        ]
        
        for text, expected_type in legitimate_cases:
            detections = plugin._detect_pii_in_text(text)
            assert len(detections) > 0, f"Should detect PII in: '{text}'"
            assert detections[0]["type"] == expected_type, f"Wrong PII type for: '{text}'"