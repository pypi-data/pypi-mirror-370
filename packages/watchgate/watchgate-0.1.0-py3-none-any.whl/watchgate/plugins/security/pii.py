"""Basic PII Filter security plugin implementation.

⚠️  WARNING: This plugin provides only basic PII protection and is NOT suitable for 
production use. It uses simple regex-based pattern matching which can be  
bypassed. For production environments, implement enterprise-grade PII detection solutions.

This module provides a security plugin that detects and filters personally 
identifiable information (PII) across all MCP communications using configurable 
pattern matching with three operation modes: block, redact, and audit_only.

The plugin supports:
- Credit card numbers with Luhn validation
- Email addresses (RFC 5322 compliant)
- Phone numbers (multiple international formats)
- IP addresses (IPv4 and IPv6)
- National ID numbers (US SSN, UK NI, Canadian SIN)
- Custom regex patterns
- Tool and path-based exemptions

NOTE: This plugin uses regex-based pattern matching for PII detection. While effective
for common PII formats, it may not catch:
- Context-dependent PII (names, addresses without clear patterns)
- Obfuscated or encoded PII
- Novel or region-specific PII formats
- PII split across multiple fields

For higher accuracy PII detection, consider integrating with ML-based solutions
like Microsoft Presidio or cloud-based PII detection services.
"""

import logging
import re
import json
import base64
from typing import Dict, Any, List, Union, Tuple
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.utils.encoding import is_data_url

logger = logging.getLogger(__name__)

# Content processing constants
CHUNK_SIZE = 65536  # 64KB - optimal for performance and memory usage
OVERLAP_SIZE = 1024  # 1KB overlap to catch patterns at chunk boundaries

# Redaction format: [PII_TYPE REDACTED by Watchgate]
def get_redaction_placeholder(pii_type: str) -> str:
    """Get redaction placeholder for a specific PII type."""
    return f"[{pii_type.upper()} REDACTED by Watchgate]"


class BasicPIIFilterPlugin(SecurityPlugin):
    """Security plugin for PII content filtering with configurable detection modes."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with comprehensive configuration validation."""
        # Initialize parent class first
        super().__init__(config)
        
        # Validate required action parameter
        if "action" not in config:
            raise ValueError("Action is required")
        
        action = config["action"]
        if action not in ["block", "redact", "audit_only"]:
            raise ValueError(f"Invalid action '{action}'. Must be one of: block, redact, audit_only")
        
        self.action = action
        
        
        # Initialize PII types configuration with format expansion
        self.pii_types = config.get("pii_types", {})
        self._expand_all_formats()
        
        # Initialize custom patterns
        self.custom_patterns = config.get("custom_patterns", [])
        self._validate_custom_patterns()
        
        # Initialize exemptions
        self.exemptions = config.get("exemptions", {"tools": [], "paths": []})
        
        # Initialize base64 scanning option (disabled by default for safety)
        self.scan_base64 = config.get("scan_base64", False)
        
        # Pre-compile regex patterns for performance
        self._compile_patterns()
    
    def _expand_all_formats(self):
        """Expand 'all' format to all supported formats for each PII type."""
        format_mappings = {
            "phone": ["us", "uk", "eu", "international"],
            # ip_address removed in Requirement 8 - not PII and causes false positives
            "national_id": ["us", "uk_ni", "canadian_sin"],
            "ssn": ["us"],  # SSN is US-specific, maps to national_id with US format
            "credit_card": ["all"],  # Credit cards don't use format-based patterns
        }
        
        for pii_type, config in self.pii_types.items():
            if isinstance(config, dict):
                # If enabled but no formats specified, default to "all"
                if config.get("enabled") and "formats" not in config and pii_type in format_mappings:
                    config["formats"] = ["all"]
                
                # Expand "all" to specific formats
                if "formats" in config and "all" in config["formats"]:
                    if pii_type in format_mappings:
                        config["formats"] = format_mappings[pii_type]
    
    def _validate_custom_patterns(self):
        """Validate custom regex patterns."""
        for pattern_config in self.custom_patterns:
            try:
                re.compile(pattern_config["pattern"])
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern_config['pattern']}': {e}")
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance.
        
        Compiles patterns into efficient regex objects that can be reused
        for multiple text processing operations.
        """
        self.compiled_patterns = {}
        
        try:
            # Compile credit card patterns with Luhn validation
            if self.pii_types.get("credit_card", {}).get("enabled"):
                self.compiled_patterns["credit_card"] = [
                    # Visa (16 digits starting with 4)
                    re.compile(r'\b4\d{15}\b'),  # Continuous
                    re.compile(r'\b4\d{3}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b'),  # Spaced/dashed (require separator)
                    
                    # MasterCard (16 digits, 51-55)
                    re.compile(r'\b5[1-5]\d{14}\b'),  # Continuous
                    re.compile(r'\b5[1-5]\d{2}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b'),  # Spaced/dashed (require separator)
                    
                    # American Express (15 digits, 34/37)
                    re.compile(r'\b3[47]\d{13}\b'),  # Continuous
                    re.compile(r'\b3[47]\d{2}[\s\-]\d{6}[\s\-]\d{5}\b'),  # Spaced/dashed (4-6-5 format, require separator)
                    
                    # Discover (16 digits, 6011)
                    re.compile(r'\b6011\d{12}\b'),  # Continuous
                    re.compile(r'\b6011[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b'),  # Spaced/dashed (require separator)
                ]
            
            # Compile email patterns (RFC 5322 compliant)
            if self.pii_types.get("email", {}).get("enabled"):
                self.compiled_patterns["email"] = [
                    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                ]
            
            # Compile phone patterns based on enabled formats
            if self.pii_types.get("phone", {}).get("enabled"):
                formats = self.pii_types["phone"].get("formats", [])
                phone_patterns = []
                
                if "us" in formats:
                    # Only include high-confidence US phone formats to minimize false positives
                    phone_patterns.extend([
                        re.compile(r'\(\d{3}\)\s?\d{3}-\d{4}'),  # (xxx) xxx-xxxx
                        re.compile(r'\d{3}-\d{3}-\d{4}'),  # xxx-xxx-xxxx
                        # Removed xxx.xxx.xxxx format - too many false positives with version numbers
                    ])
                
                if "uk" in formats:
                    phone_patterns.extend([
                        re.compile(r'\+44\s?\d{4}\s?\d{6}'),  # +44 xxxx xxxxxx
                        re.compile(r'0\d{4}\s?\d{6}'),  # 0xxxx xxxxxx
                    ])
                
                if "international" in formats:
                    # International pattern is very broad - only enable if explicitly needed
                    # Consider using custom patterns for specific countries instead
                    phone_patterns.append(
                        re.compile(r'\+\d{1,3}\s?\d{1,4}\s?\d{1,4}\s?\d{1,9}')
                    )
                
                if phone_patterns:
                    self.compiled_patterns["phone"] = phone_patterns
            
            # IP address detection removed in Requirement 8 - too many false positives
            # IP addresses are not considered PII in most contexts and create noise
            # Organizations that need IP detection should use custom patterns
            
            # Compile national ID patterns (also check for 'ssn' key for US users)
            national_id_config = (
                self.pii_types.get("national_id") or 
                self.pii_types.get("ssn") or 
                {}
            )
            if national_id_config.get("enabled"):
                formats = national_id_config.get("formats", [])
                national_id_patterns = []
                
                if "us" in formats:
                    # Only detect properly formatted SSNs (xxx-xx-xxxx) - Requirement 8
                    # Unformatted 9-digit numbers cause too many false positives
                    national_id_patterns.extend([
                        re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),  # SSN xxx-xx-xxxx (formatted only)
                    ])
                
                if "uk_ni" in formats:
                    national_id_patterns.append(
                        re.compile(r'\b[A-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-Z]\b')
                    )
                
                if "canadian_sin" in formats:
                    national_id_patterns.append(
                        re.compile(r'\b\d{3}-\d{3}-\d{3}\b')
                    )
                
                if national_id_patterns:
                    self.compiled_patterns["national_id"] = national_id_patterns
            
            # Compile custom patterns
            custom_patterns = []
            for pattern_config in self.custom_patterns:
                if pattern_config.get("enabled", True):
                    custom_patterns.append({
                        "name": pattern_config["name"],
                        "pattern": re.compile(pattern_config["pattern"])
                    })
            
            if custom_patterns:
                self.compiled_patterns["custom"] = custom_patterns
                
        except re.error as e:
            logger.error(f"Error compiling PII detection patterns: {e}")
            raise ValueError(f"Pattern compilation failed: {e}")
    
    def _luhn_validate(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        # Remove spaces and non-digits
        digits = [int(d) for d in card_number if d.isdigit()]
        
        # Apply Luhn algorithm
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        return sum(digits) % 10 == 0
    
    
    def _should_skip_base64_content(self, text: str) -> bool:
        """Check if text should be skipped due to base64 content and configuration."""
        if self.scan_base64:
            return False  # Don't skip, scan everything (existing behavior)
        
        # Don't skip data URLs - they get special handling
        if is_data_url(text):
            return False
        
        # Simple base64 detection - if it looks like base64 and scanning is disabled, skip it
        if len(text) > 20 and re.match(r'^[A-Za-z0-9+/]*={0,2}$', text) and len(text) % 4 == 0:
            return True
        
        return False
    
    def _detect_pii_in_chunk(self, text: str, offset: int = 0) -> List[Dict[str, Any]]:
        """Detect PII in a text chunk and return list of detections."""
        detections = []
        
        # Check credit cards with Luhn validation
        if "credit_card" in self.compiled_patterns:
            for pattern in self.compiled_patterns["credit_card"]:
                for match in pattern.finditer(text):
                    card_number = match.group()
                    if self._luhn_validate(card_number):
                        detections.append({
                            "type": "CREDIT_CARD",
                            "pattern": "luhn_validated",
                            "position": [match.start() + offset, match.end() + offset],
                            "action": "detected"
                        })
        
        # Check emails
        if "email" in self.compiled_patterns:
            for pattern in self.compiled_patterns["email"]:
                for match in pattern.finditer(text):
                    detections.append({
                        "type": "EMAIL",
                        "pattern": "rfc5322",
                        "position": [match.start() + offset, match.end() + offset],
                        "action": "detected"
                    })
        
        # Check phone numbers
        if "phone" in self.compiled_patterns:
            for pattern in self.compiled_patterns["phone"]:
                for match in pattern.finditer(text):
                    detections.append({
                        "type": "PHONE",
                        "pattern": "phone_format",
                        "position": [match.start() + offset, match.end() + offset],
                        "action": "detected"
                    })
        
        # IP address detection removed in Requirement 8
        # IP addresses are not PII and cause too many false positives
        
        # Check national IDs
        if "national_id" in self.compiled_patterns:
            for pattern in self.compiled_patterns["national_id"]:
                for match in pattern.finditer(text):
                    detections.append({
                        "type": "NATIONAL_ID",
                        "pattern": "national_id_format",
                        "position": [match.start() + offset, match.end() + offset],
                        "action": "detected"
                    })
        
        # Check custom patterns
        if "custom" in self.compiled_patterns:
            for custom_pattern in self.compiled_patterns["custom"]:
                for match in custom_pattern["pattern"].finditer(text):
                    detections.append({
                        "type": "CUSTOM",
                        "pattern": custom_pattern["name"],
                        "position": [match.start() + offset, match.end() + offset],
                        "action": "detected"
                    })
        
        return detections
    
    def _detect_pii_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII in text, processing large content in chunks."""
        # Handle data URLs specially: check the URL itself but skip encoded content
        if is_data_url(text):
            # Extract the data URL prefix (before the base64 content) for pattern matching
            parts = text.split(',', 1)
            if len(parts) >= 1:
                # Check the data URL schema/MIME type part for patterns
                url_prefix = parts[0]
                return self._detect_pii_in_text_content(url_prefix)
            
            # Skip the base64 content portion - it's likely legitimate file data
            return []
        
        # For non-data URLs, do normal detection
        return self._detect_pii_in_text_content(text)
    
    def _detect_pii_in_text_content(self, text: str) -> List[Dict[str, Any]]:
        """Core PII detection logic for text content."""
        detections = []
        
        # Process in chunks if text is large
        if len(text) > CHUNK_SIZE:
            # Process with overlapping chunks to catch PII at boundaries
            offset = 0
            while offset < len(text):
                # Calculate chunk boundaries with overlap
                chunk_end = min(offset + CHUNK_SIZE, len(text))
                chunk = text[offset:chunk_end]
                
                # Process this chunk
                chunk_detections = self._detect_pii_in_chunk(chunk, offset)
                
                # Add detections, avoiding duplicates from overlapping regions
                for detection in chunk_detections:
                    # Check if this detection overlaps with existing ones
                    is_duplicate = False
                    for existing in detections:
                        if (detection["type"] == existing["type"] and
                            detection["pattern"] == existing["pattern"] and
                            abs(detection["position"][0] - existing["position"][0]) < OVERLAP_SIZE):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        detections.append(detection)
                
                # Move to next chunk with overlap
                offset += CHUNK_SIZE - OVERLAP_SIZE
                if offset + OVERLAP_SIZE >= len(text):
                    break
        else:
            # Process small text directly
            detections = self._detect_pii_in_chunk(text, 0)
        
        return detections
    
    def _redact_pii_in_text(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """Redact PII in text based on detections."""
        if not detections:
            return text
        
        # Sort detections by position (reverse order to maintain positions)
        sorted_detections = sorted(detections, key=lambda x: x["position"][0], reverse=True)
        
        redacted_text = text
        for detection in sorted_detections:
            start, end = detection["position"]
            redacted_text = (
                redacted_text[:start] + 
                get_redaction_placeholder(detection["type"]) +
                redacted_text[end:]
            )
            detection["action"] = "redacted"
        
        return redacted_text
    
    def _extract_text_from_data(self, data: Any) -> str:
        """Extract text content from various data types.
        
        Args:
            data: The data to extract text from
            
        Returns:
            String representation of the data
            
        Note:
            All content is processed regardless of size
        """
        if isinstance(data, str):
            text = data
        elif isinstance(data, dict):
            text = json.dumps(data)
        elif isinstance(data, list):
            text = json.dumps(data)
        else:
            text = str(data)
        
        return text
    
    def _is_tool_exempted(self, tool_name: str) -> bool:
        """Check if tool is exempted from PII filtering."""
        return tool_name in self.exemptions.get("tools", [])
    
    def _process_message_content(self, content: Any) -> Tuple[List[Dict[str, Any]], Any]:
        """Process message content and return detections and potentially modified content."""
        from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED
        
        text = self._extract_text_from_data(content)
        
        # CRITICAL: Use byte length, not character count
        text_size_bytes = len(text.encode('utf-8'))
        if text_size_bytes > MAX_CONTENT_SIZE:
            # Return a special detection that indicates size exceeded
            return [{
                "type": "content_size_exceeded",
                "size_bytes": text_size_bytes,
                "max_size": MAX_CONTENT_SIZE,
                "reason": f"Content exceeds maximum size limit ({MAX_CONTENT_SIZE} bytes)",
                "reason_code": REASON_CONTENT_SIZE_EXCEEDED
            }], content
        
        # Skip base64 content if base64 scanning is disabled
        if self._should_skip_base64_content(text):
            return [], content
        
        detections = self._detect_pii_in_text(text)
        
        if self.action == "redact" and detections:
            redacted_text = self._redact_pii_in_text(text, detections)
            # Try to reconstruct the original structure
            if isinstance(content, str):
                return detections, redacted_text
            elif isinstance(content, dict):
                try:
                    return detections, json.loads(redacted_text)
                except json.JSONDecodeError:
                    return detections, {"data": redacted_text}
            else:
                return detections, redacted_text
        
        return detections, content
    
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        """Check request for PII and apply configured mode."""
        # Check for tool exemptions
        if (request.method == "tools/call" and 
            request.params and 
            "name" in request.params and 
            self._is_tool_exempted(request.params["name"])):
            return PolicyDecision(
                allowed=True,
                reason="Tool exempted from PII filtering",
                metadata={"plugin": self.__class__.__name__, "pii_detected": False, "detection_action": self.action, "exempted": True}
            )
        
        # Process request content
        if request.params:
            detections, modified_params = self._process_message_content(request.params)
        else:
            detections = []
            modified_params = request.params
        
        # Check for content size exceeded (special case)
        if detections and len(detections) == 1 and detections[0].get("type") == "content_size_exceeded":
            size_detection = detections[0]
            return PolicyDecision(
                allowed=False,
                reason=size_detection["reason"],
                metadata={
                    "plugin": self.__class__.__name__,
                    "content_size_bytes": size_detection["size_bytes"],
                    "max_size": size_detection["max_size"],
                    "reason_code": size_detection["reason_code"]
                }
            )
        
        # Generate decision based on mode
        if not detections:
            return PolicyDecision(
                allowed=True,
                reason="No PII detected",
                metadata={"plugin": self.__class__.__name__, "pii_detected": False, "detection_action": self.action, "detections": []}
            )
        
        from watchgate.plugins.security import REASON_PII_DETECTED
        if self.action == "block":
            return PolicyDecision(
                allowed=False,
                reason="PII detected - blocking transmission",
                metadata={
                    "plugin": self.__class__.__name__,
                    "pii_detected": True,
                    "detection_action": self.action,
                    "detections": detections,
                    "reason_code": REASON_PII_DETECTED
                }
            )
        elif self.action == "redact":
            if modified_params != request.params:
                # Create a new request with redacted content
                # Create a new request with redacted content
                # This is a limitation of the current PolicyDecision interface
                modified_request = MCPRequest(
                    jsonrpc=request.jsonrpc,
                    method=request.method,
                    id=request.id,
                    params=modified_params,
                    sender_context=request.sender_context
                )
                from watchgate.plugins.security import REASON_PII_DETECTED
                return PolicyDecision(
                    allowed=True,
                    reason=f"PII detected and redacted from request: {', '.join([d['type'] for d in detections])}",
                    metadata={
                        "plugin": self.__class__.__name__,
                        "pii_detected": True,
                        "detection_action": self.action,
                        "detections": detections,
                        "reason_code": REASON_PII_DETECTED
                    },
                    modified_content=modified_request  # Proper field for request modification
                )
            else:
                from watchgate.plugins.security import REASON_PII_DETECTED
                return PolicyDecision(
                    allowed=True,
                    reason="PII detected but no redaction needed",
                    metadata={
                        "plugin": self.__class__.__name__,
                        "pii_detected": True,
                        "detection_action": self.action,
                        "detections": detections,
                        "reason_code": REASON_PII_DETECTED
                    }
                )
        else:  # audit_only
            from watchgate.plugins.security import REASON_PII_DETECTED
            return PolicyDecision(
                allowed=True,
                reason="PII detected - audit only",
                metadata={
                    "plugin": self.__class__.__name__,
                    "pii_detected": True,
                    "detection_action": self.action,
                    "detections": detections,
                    "reason_code": REASON_PII_DETECTED
                }
            )
    
    async def check_response(self, request: MCPRequest, response: MCPResponse, server_name: str) -> PolicyDecision:
        """Check response for PII and apply configured mode."""
        # Process response content
        if response.result:
            detections, modified_result = self._process_message_content(response.result)
        else:
            detections = []
            modified_result = response.result
        
        # Generate decision based on mode
        if not detections:
            return PolicyDecision(
                allowed=True,
                reason="No PII detected in response",
                metadata={"plugin": self.__class__.__name__, "pii_detected": False, "detection_action": self.action, "detections": []}
            )
        
        from watchgate.plugins.security import REASON_PII_DETECTED
        if self.action == "block":
            return PolicyDecision(
                allowed=False,
                reason="PII detected in response - blocking transmission",
                metadata={
                    "plugin": self.__class__.__name__,
                    "pii_detected": True,
                    "detection_action": self.action,
                    "detections": detections,
                    "reason_code": REASON_PII_DETECTED
                }
            )
        elif self.action == "redact":
            if modified_result != response.result:
                modified_response = MCPResponse(
                    jsonrpc=response.jsonrpc,
                    id=response.id,
                    result=modified_result,
                    error=response.error,
                    sender_context=response.sender_context
                )
                from watchgate.plugins.security import REASON_PII_DETECTED
                return PolicyDecision(
                    allowed=True,
                    reason="PII detected in response and redacted",
                    metadata={
                        "plugin": self.__class__.__name__,
                        "pii_detected": True,
                        "detection_action": self.action,
                        "detections": detections,
                        "reason_code": REASON_PII_DETECTED
                    },
                    modified_content=modified_response
                )
            else:
                from watchgate.plugins.security import REASON_PII_DETECTED
                return PolicyDecision(
                    allowed=True,
                    reason="PII detected in response but no modification needed",
                    metadata={
                        "plugin": self.__class__.__name__,
                        "pii_detected": True,
                        "detection_action": self.action,
                        "detections": detections,
                        "reason_code": REASON_PII_DETECTED
                    }
                )
        else:  # audit_only
            from watchgate.plugins.security import REASON_PII_DETECTED
            return PolicyDecision(
                allowed=True,
                reason="PII detected in response - audit only",
                metadata={
                    "plugin": self.__class__.__name__,
                    "pii_detected": True,
                    "detection_action": self.action,
                    "detections": detections,
                    "reason_code": REASON_PII_DETECTED
                }
            )
    
    async def check_notification(self, notification: MCPNotification, server_name: str) -> PolicyDecision:
        """Check notification for PII and apply configured mode."""
        # Process notification content
        if notification.params:
            detections, modified_params = self._process_message_content(notification.params)
        else:
            detections = []
            modified_params = notification.params
        
        # Generate decision based on mode
        if not detections:
            return PolicyDecision(
                allowed=True,
                reason="No PII detected in notification",
                metadata={"plugin": self.__class__.__name__, "pii_detected": False, "detection_action": self.action, "detections": []}
            )
        
        from watchgate.plugins.security import REASON_PII_DETECTED
        if self.action == "block":
            return PolicyDecision(
                allowed=False,
                reason="PII detected in notification - blocking transmission",
                metadata={
                    "plugin": self.__class__.__name__,
                    "pii_detected": True,
                    "detection_action": self.action,
                    "detections": detections,
                    "reason_code": REASON_PII_DETECTED
                }
            )
        elif self.action == "redact":
            if modified_params != notification.params:
                # Create a new notification with redacted content
                modified_notification = MCPNotification(
                    jsonrpc=notification.jsonrpc,
                    method=notification.method,
                    params=modified_params
                )
                from watchgate.plugins.security import REASON_PII_DETECTED
                return PolicyDecision(
                    allowed=True,
                    reason=f"PII detected and redacted from notification: {', '.join([d['type'] for d in detections])}",
                    metadata={
                        "plugin": self.__class__.__name__,
                        "pii_detected": True,
                        "detection_action": self.action,
                        "detections": detections,
                        "reason_code": REASON_PII_DETECTED
                    },
                    modified_content=modified_notification
                )
            else:
                from watchgate.plugins.security import REASON_PII_DETECTED
                return PolicyDecision(
                    allowed=True,
                    reason="PII detected in notification but no redaction needed",
                    metadata={
                        "plugin": self.__class__.__name__,
                        "pii_detected": True,
                        "detection_action": self.action,
                        "detections": detections,
                        "reason_code": REASON_PII_DETECTED
                    }
                )
        else:  # audit_only
            from watchgate.plugins.security import REASON_PII_DETECTED
            return PolicyDecision(
                allowed=True,
                reason="PII detected in notification - audit only",
                metadata={
                    "plugin": self.__class__.__name__,
                    "pii_detected": True,
                    "detection_action": self.action,
                    "detections": detections,
                    "reason_code": REASON_PII_DETECTED
                }
            )


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "pii": BasicPIIFilterPlugin
}
