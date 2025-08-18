"""Basic Secrets Filter security plugin implementation.

⚠️  WARNING: This plugin provides only basic secrets protection and is NOT suitable 
for production use. It uses simple regex patterns and entropy analysis which can be 
bypassed. For production environments, implement enterprise-grade secret detection solutions.

This module provides a security plugin that detects and filters well-known 
secrets, tokens, and credentials across all MCP communications using 
high-confidence regex patterns and conservative entropy analysis.

The plugin supports:
- AWS Access Keys (AKIA-prefixed patterns)
- GitHub Tokens (ghp_, gho_, ghu_, ghs_, ghr_ prefixes)
- Google API Keys (AIza-prefixed patterns)
- JWT Tokens (three-part base64url structure)
- SSH Private Keys (PEM format headers)
- Base64-encoded secrets (12+ characters, with DoS protection)
- Conservative Shannon entropy detection
- Custom organization patterns
- Tool and path-based exemptions

NOTE: This plugin uses regex patterns, entropy analysis, and base64 decoding for secret detection.
Base64 decoding includes safeguards: candidate limits (50 max), size limits (100KB total decoded),
and skips data URLs to avoid false positives on legitimate file content.

While effective for well-known secret formats, it may not catch:
- Secrets in novel or proprietary formats
- Non-base64 encoded or obfuscated secrets (ROT13, custom encoding, etc.)
- Secrets split across multiple fields
- Context-dependent credentials

The entropy detection is conservative to minimize false positives. Consider
adjusting entropy thresholds based on your security requirements.
"""

import logging
import re
import json
import math
import copy
import base64
from typing import Dict, Any, List, Union, Tuple
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.utils.encoding import is_data_url

logger = logging.getLogger(__name__)


class BasicSecretsFilterPlugin(SecurityPlugin):
    """Security plugin that detects and filters secrets using high-confidence patterns and entropy analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration."""
        # Validate configuration type first
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Initialize base class to set priority
        super().__init__(config)
        
        # Validate action parameter
        action = config.get("action", "block")
        if action not in ["block", "redact", "audit_only"]:
            raise ValueError(f"Invalid action '{action}'. Must be one of: block, redact, audit_only")
        
        self.action = action
        
        # Initialize secret types with defaults
        default_secret_types = {
            "aws_access_keys": {"enabled": True},
            "github_tokens": {"enabled": True},
            "google_api_keys": {"enabled": True},
            "jwt_tokens": {"enabled": True},
            "ssh_private_keys": {"enabled": True},
            "aws_secret_keys": {"enabled": False}  # Higher false positive risk
        }
        
        # Support both "secret_types" and "detection_types" for backward compatibility
        self.secret_types = config.get("secret_types", config.get("detection_types", {}))
        # Merge with defaults
        for secret_type, default_config in default_secret_types.items():
            if secret_type not in self.secret_types:
                self.secret_types[secret_type] = default_config
        
        # Initialize entropy detection with conservative defaults
        default_entropy = {
            "enabled": True,
            "min_entropy": 6.0,  # Higher threshold to minimize false positives on code
            "min_length": 8
        }
        
        self.entropy_detection = config.get("entropy_detection", default_entropy)
        # Merge with defaults
        for key, default_value in default_entropy.items():
            if key not in self.entropy_detection:
                self.entropy_detection[key] = default_value
        
        # Initialize custom patterns
        self.custom_patterns = config.get("custom_patterns", [])
        
        # Initialize allowlist
        self.allowlist = config.get("allowlist", {"patterns": []})
        if "patterns" not in self.allowlist:
            self.allowlist["patterns"] = []
        
        # Initialize exemptions
        self.exemptions = config.get("exemptions", {"tools": [], "paths": []})
        if "tools" not in self.exemptions:
            self.exemptions["tools"] = []
        if "paths" not in self.exemptions:
            self.exemptions["paths"] = []
        
        # Note: base64_detection configuration option has been removed.
        # The plugin now automatically detects and decodes base64-encoded secrets
        # with built-in DoS protection (candidate/size limits, data URL skipping).
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        self.compiled_patterns = {}
        
        # High-confidence secret patterns
        secret_patterns = {
            "aws_access_keys": r"AKIA[0-9A-Z]{16}",
            "github_tokens": r"gh[pousrp]_[0-9a-zA-Z]{36}",
            "google_api_keys": r"AIza[0-9A-Za-z\-_]{35}",
            "jwt_tokens": r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
            "ssh_private_keys": r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"
        }
        
        for secret_type, pattern in secret_patterns.items():
            if self.secret_types.get(secret_type, {}).get("enabled", False):
                try:
                    self.compiled_patterns[secret_type] = re.compile(pattern)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern for {secret_type}: {e}")
        
        # Compile custom patterns
        for custom_pattern in self.custom_patterns:
            if custom_pattern.get("enabled", False):
                try:
                    name = custom_pattern["name"]
                    pattern = custom_pattern["pattern"]
                    self.compiled_patterns[f"custom_{name}"] = re.compile(pattern)
                except (KeyError, re.error) as e:
                    logger.warning(f"Invalid custom pattern: {e}")
        
        # Compile allowlist patterns
        self.compiled_allowlist = []
        for pattern in self.allowlist["patterns"]:
            try:
                # Convert shell-style wildcards to regex
                regex_pattern = pattern.replace("*", ".*").replace("?", ".")
                self.compiled_allowlist.append(re.compile(regex_pattern))
            except re.error as e:
                logger.warning(f"Invalid allowlist pattern '{pattern}': {e}")
    
    def _calculate_entropy(self, data: str) -> float:
        """Calculate Shannon entropy for potential secret detection."""
        if len(data) < self.entropy_detection["min_length"]:
            return 0.0
        
        entropy = 0.0
        data_len = len(data)
        
        # Count frequency of each character
        char_counts = {}
        for char in data:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        for count in char_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy += -probability * math.log2(probability)
        
        return entropy
    
    def _is_likely_base64_data(self, text: str) -> bool:
        """Heuristic to identify base64 encoded data that is likely file content, not secrets.
        
        This method is used to skip entropy detection on legitimate base64 file data
        to reduce false positives. The plugin separately handles base64 secret detection
        via the _detect_base64_encoded_secrets() method.
        
        Note: This heuristic is for entropy detection only. Base64 secret detection
        is handled separately with proper decoding and pattern matching.
        """
        # Check if it's a data URL (files embedded in responses)
        if is_data_url(text):
            return True
        
        # Skip short strings - they're more likely to be actual tokens
        if len(text) <= 100:
            return False
        
        # If it looks like base64 and is very long, it's probably file data
        if re.match(r'^[A-Za-z0-9+/]*={0,2}$', text) and len(text) % 4 == 0 and len(text) > 500:
            return True
        
        return False
    
    def _is_potential_secret_by_entropy(self, text: str) -> bool:
        """Determine if text might be a secret based on conservative entropy thresholds."""
        if not self.entropy_detection["enabled"]:
            return False
        
        min_length = self.entropy_detection["min_length"]
        min_entropy = self.entropy_detection["min_entropy"]
        
        # Check minimum length constraint (keep reasonable minimum to avoid false positives)
        # No maximum length limit - analyze all content regardless of size
        if len(text) < min_length:
            return False
        
        # Additional heuristics to reduce false positives
        if self._is_likely_base64_data(text):
            return False
        
        # Calculate entropy
        entropy = self._calculate_entropy(text)
        return entropy >= min_entropy
    
    def _matches_allowlist(self, text: str) -> bool:
        """Check if text matches any allowlist pattern."""
        for pattern in self.compiled_allowlist:
            if pattern.search(text):
                return True
        return False
    
    def _is_tool_exempted(self, tool_name: str) -> bool:
        """Check if tool is exempted from secret detection."""
        return tool_name in self.exemptions["tools"]
    
    
    def _detect_secrets_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Detect secrets in a text string."""
        detections = []
        
        # Check allowlist first
        if self._matches_allowlist(text):
            return []
        
        # Handle data URLs specially: check the URL itself but skip encoded content
        if is_data_url(text):
            # Extract the data URL prefix (before the base64 content) for pattern matching
            parts = text.split(',', 1)
            if len(parts) >= 1:
                # Check the data URL schema/MIME type part for patterns
                url_prefix = parts[0]
                prefix_detections = self._detect_secrets_in_text_content(url_prefix)
                detections.extend(prefix_detections)
            
            # Skip the base64 content portion - it's likely legitimate file data
            return detections
        
        # For non-data URLs, do normal detection
        return self._detect_secrets_in_text_content(text)
    
    def _detect_secrets_in_text_content(self, text: str) -> List[Dict[str, Any]]:
        """Core secret detection logic for text content."""
        detections = []
        
        # Check high-confidence patterns
        for secret_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                detection = {
                    "type": secret_type.replace("custom_", ""),
                    "pattern": "standard" if not secret_type.startswith("custom_") else "custom",
                    "position": [match.start(), match.end()],
                    "action": self.action,
                    "confidence": "high"
                }
                detections.append(detection)
        
        # Check entropy-based detection for longer strings
        if self.entropy_detection["enabled"] and not detections:
            # Split text into potential secret-like tokens
            tokens = re.findall(r'[A-Za-z0-9+/=_-]{40,200}', text)  # Longer minimum to reduce FPs
            for token in tokens:
                if self._is_potential_secret_by_entropy(token):
                    start_pos = text.find(token)
                    detection = {
                        "type": "entropy_based",
                        "entropy_score": self._calculate_entropy(token),
                        "position": [start_pos, start_pos + len(token)],
                        "action": self.action,
                        "confidence": "medium"
                    }
                    detections.append(detection)
        
        # Check base64-encoded secrets (12+ characters as per requirements)
        if not detections:
            base64_detections = self._detect_base64_encoded_secrets(text)
            detections.extend(base64_detections)
        
        return detections
    
    def _detect_base64_encoded_secrets(self, text: str) -> List[Dict[str, Any]]:
        """Detect secrets in base64-encoded content (12+ characters as per requirements).
        
        This method finds potential base64 strings, decodes them safely, and scans
        the decoded content for secret patterns. Implements requirement for base64
        secrets detection with minimum 12 character length.
        
        DoS Protection: Limits the number of base64 candidates processed to prevent
        attacks using many base64-like strings that could cause excessive decode operations.
        """
        from watchgate.utils.encoding import safe_decode_base64
        
        detections = []
        total_decoded_bytes = 0
        candidates_processed = 0
        
        # DoS protection: Limit base64 candidates to prevent time/memory exhaustion
        MAX_BASE64_CANDIDATES = 50  # Reasonable limit for legitimate content
        MAX_TOTAL_DECODED_BYTES = 100 * 1024  # 100KB total across all candidates
        
        # Find base64-like strings that are 12+ characters long (including padding)
        # Use word boundaries but make sure padding characters are included
        # Note: Regex is non-overlapping by design, which is correct behavior
        base64_pattern = re.compile(r'\b[A-Za-z0-9+/]{12,}={0,2}(?=\s|$|[^A-Za-z0-9+/=])')
        
        for match in base64_pattern.finditer(text):
            base64_candidate = match.group()
            
            # DoS protection: Stop processing if we've hit limits
            if candidates_processed >= MAX_BASE64_CANDIDATES:
                logger.warning(f"Base64 candidate limit reached ({MAX_BASE64_CANDIDATES}), skipping remaining candidates")
                break
            
            if total_decoded_bytes >= MAX_TOTAL_DECODED_BYTES:
                logger.warning(f"Total decoded bytes limit reached ({MAX_TOTAL_DECODED_BYTES}), skipping remaining candidates")
                break
            
            candidates_processed += 1
            
            # Additional validation: must be proper base64 length (multiple of 4)
            if len(base64_candidate) % 4 != 0:
                continue
            
            # Skip if the full text is a data URL (handled separately by _detect_secrets_in_text)
            if is_data_url(text):
                continue
                
            # Skip if this base64 candidate appears to be part of a data URL
            # Look for "data:...;base64," pattern immediately before the candidate
            start_pos = match.start()
            prefix_start = max(0, start_pos - 100)  # Look back up to 100 chars
            prefix_text = text[prefix_start:start_pos]
            if re.search(r'data:[^;]*;base64,$', prefix_text):
                continue  # This is likely part of a data URL, skip it
            
            # Attempt safe base64 decoding
            decoded_content = safe_decode_base64(base64_candidate, max_decode_size=10240)
            
            if decoded_content and len(decoded_content) >= 5:  # Must decode to something meaningful
                # Track total decoded bytes for DoS protection
                total_decoded_bytes += len(decoded_content)
                
                # Scan decoded content for secrets using pattern detection only (no recursive base64)
                decoded_detections = self._detect_patterns_only(decoded_content)
                
                # Mark these detections as base64-encoded and adjust positions
                for detection in decoded_detections:
                    detection.update({
                        "encoding_type": "base64",
                        "base64_position": [match.start(), match.end()],
                        "original_base64": base64_candidate[:50] + "..." if len(base64_candidate) > 50 else base64_candidate,
                        "decoded_length": len(decoded_content)
                    })
                    detections.append(detection)
        
        return detections
    
    def _detect_patterns_only(self, text: str) -> List[Dict[str, Any]]:
        """Detect secrets using pattern matching only (no base64 decoding or entropy).
        
        This method is used when scanning already-decoded base64 content to avoid
        recursive decoding and to focus on high-confidence pattern matches.
        """
        detections = []
        
        # Check high-confidence patterns only
        for secret_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                detection = {
                    "type": secret_type.replace("custom_", ""),
                    "pattern": "standard" if not secret_type.startswith("custom_") else "custom",
                    "position": [match.start(), match.end()],
                    "action": self.action,
                    "confidence": "high"
                }
                detections.append(detection)
        
        return detections
    
    def _detect_secrets_in_request(self, request: MCPRequest) -> List[Dict[str, Any]]:
        """Detect secrets in an MCP request."""
        from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED
        
        detections = []
        
        # Convert request params to JSON string for text analysis
        try:
            if request.params:
                request_text = json.dumps(request.params, default=str)
                
                # CRITICAL: Use byte length, not character count
                text_size_bytes = len(request_text.encode('utf-8'))
                if text_size_bytes > MAX_CONTENT_SIZE:
                    # Return a special detection that indicates size exceeded
                    return [{
                        "type": "content_size_exceeded",
                        "size_bytes": text_size_bytes,
                        "max_size": MAX_CONTENT_SIZE,
                        "reason": f"Content exceeds maximum size limit ({MAX_CONTENT_SIZE} bytes)",
                        "reason_code": REASON_CONTENT_SIZE_EXCEEDED
                    }]
                
                detections.extend(self._detect_secrets_in_text(request_text))
        except Exception as e:
            logger.warning(f"Error analyzing request for secrets: {e}")
        
        return detections
    
    def _redact_secrets_in_request(self, request: MCPRequest, detections: List[Dict[str, Any]]) -> MCPRequest:
        """Create a redacted copy of the request."""
        redacted_request = copy.deepcopy(request)
        
        # Convert params to string, redact secrets, then parse back
        try:
            if redacted_request.params:
                request_text = json.dumps(redacted_request.params, default=str)
                
                # Sort detections by position (reverse order to maintain positions)
                sorted_detections = sorted(detections, key=lambda x: x["position"][0], reverse=True)
                
                for detection in sorted_detections:
                    start, end = detection["position"]
                    if 0 <= start < end <= len(request_text):
                        request_text = (
                            request_text[:start] + 
                            "[REDACTED BY WATCHGATE]" + 
                            request_text[end:]
                        )
                
                # Parse back to params object
                redacted_request.params = json.loads(request_text)
            
        except Exception as e:
            logger.warning(f"Error redacting secrets from request: {e}")
        
        return redacted_request
    
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        """Check if request should be allowed."""
        # Check tool exemptions
        if request.method == "tools/call" and request.params:
            tool_name = request.params.get("name")
            if tool_name and self._is_tool_exempted(tool_name):
                return PolicyDecision(
                    allowed=True,
                    reason="Tool exempted from secrets detection",
                    metadata={"exempted_tool": tool_name}
                )
        
        # Detect secrets
        detections = self._detect_secrets_in_request(request)
        
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
        
        if not detections:
            from watchgate.plugins.security import REASON_NONE
            return PolicyDecision(
                allowed=True,
                reason="No secrets detected",
                metadata={
                    "plugin": self.__class__.__name__,
                    "secret_detected": False,
                    "reason_code": REASON_NONE
                }
            )
        
        # Handle detections based on action mode
        from watchgate.plugins.security import REASON_SECRET_DETECTED
        metadata = {
            "plugin": self.__class__.__name__,
            "secret_detected": True,
            "detection_mode": self.action,
            "detections": detections,
            "reason_code": REASON_SECRET_DETECTED
        }
        
        if self.action == "block":
            return PolicyDecision(
                allowed=False,
                reason=f"Secret detected: {len(detections)} secret(s) found",
                metadata=metadata
            )
        elif self.action == "redact":
            redacted_request = self._redact_secrets_in_request(request, detections)
            return PolicyDecision(
                allowed=True,
                reason=f"Secret redacted: {len(detections)} secret(s) redacted",
                metadata=metadata,
                modified_content=redacted_request
            )
        elif self.action == "audit_only":
            return PolicyDecision(
                allowed=True,
                reason=f"Secret logged: {len(detections)} secret(s) detected and logged",
                metadata=metadata
            )
        
        # Fallback (should not reach here)
        return PolicyDecision(
            allowed=False,
            reason="Unknown action mode",
            metadata=metadata
        )
    
    async def check_response(self, request: MCPRequest, response: MCPResponse, server_name: str) -> PolicyDecision:
        """Check if response should be allowed."""
        from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED
        
        # Convert response to text for analysis
        try:
            if response.result:
                response_text = json.dumps(response.result, default=str)
                
                # Check content size
                text_size_bytes = len(response_text.encode('utf-8'))
                if text_size_bytes > MAX_CONTENT_SIZE:
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Response content exceeds maximum size limit ({MAX_CONTENT_SIZE} bytes)",
                        metadata={
                            "plugin": self.__class__.__name__,
                            "content_size_bytes": text_size_bytes,
                            "max_size": MAX_CONTENT_SIZE,
                            "reason_code": REASON_CONTENT_SIZE_EXCEEDED
                        }
                    )
                
                detections = self._detect_secrets_in_text(response_text)
            else:
                detections = []
        except Exception as e:
            logger.warning(f"Error analyzing response for secrets: {e}")
            detections = []
        
        if not detections:
            from watchgate.plugins.security import REASON_NONE
            return PolicyDecision(
                allowed=True,
                reason="No secrets detected in response",
                metadata={
                    "plugin": self.__class__.__name__,
                    "secret_detected": False,
                    "reason_code": REASON_NONE
                }
            )
        
        # Handle detections based on action mode
        from watchgate.plugins.security import REASON_SECRET_DETECTED
        metadata = {
            "plugin": self.__class__.__name__,
            "secret_detected": True,
            "detection_mode": self.action,
            "detections": detections,
            "reason_code": REASON_SECRET_DETECTED
        }
        
        if self.action == "block":
            return PolicyDecision(
                allowed=False,
                reason=f"Secret detected in response: {len(detections)} secret(s) found",
                metadata=metadata
            )
        elif self.action == "redact":
            # Create a redacted copy of the response
            try:
                response_text = json.dumps(response.result, default=str)
                
                # Sort detections by position (reverse order to maintain positions)
                sorted_detections = sorted(detections, key=lambda x: x["position"][0], reverse=True)
                
                for detection in sorted_detections:
                    start, end = detection["position"]
                    if 0 <= start < end <= len(response_text):
                        response_text = (
                            response_text[:start] + 
                            "[REDACTED BY WATCHGATE]" + 
                            response_text[end:]
                        )
                
                # Parse back to result object
                modified_result = json.loads(response_text)
                
                # Create modified response
                modified_response = MCPResponse(
                    jsonrpc=response.jsonrpc,
                    id=response.id,
                    result=modified_result,
                    error=response.error,
                    sender_context=response.sender_context
                )
                
                return PolicyDecision(
                    allowed=True,
                    reason=f"Secret redacted from response: {len(detections)} secret(s) redacted",
                    metadata=metadata,
                    modified_content=modified_response
                )
                
            except Exception as e:
                logger.warning(f"Error redacting secrets from response: {e}")
                # If redaction fails, fall back to blocking for security
                metadata["reason_code"] = REASON_SECRET_DETECTED
                return PolicyDecision(
                    allowed=False,
                    reason=f"Secret detected and redaction failed: {e}",
                    metadata=metadata
                )
                
        elif self.action == "audit_only":
            return PolicyDecision(
                allowed=True,
                reason=f"Secret logged: {len(detections)} secret(s) detected in response",
                metadata=metadata
            )
        
        # Fallback (should not reach here)
        return PolicyDecision(
            allowed=False,
            reason="Unknown action mode",
            metadata=metadata
        )
    
    async def check_notification(self, notification: MCPNotification, server_name: str) -> PolicyDecision:
        """Check if notification contains secrets and apply configured action.
        
        Notifications can contain secrets in parameters or method names and should
        be checked with the same rigor as requests and responses.
        """
        from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED
        
        detections = []
        
        # Check notification parameters for secrets
        try:
            if notification.params:
                notification_text = json.dumps(notification.params, default=str)
                
                # Check content size
                text_size_bytes = len(notification_text.encode('utf-8'))
                if text_size_bytes > MAX_CONTENT_SIZE:
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Notification content exceeds maximum size limit ({MAX_CONTENT_SIZE} bytes)",
                        metadata={
                            "plugin": self.__class__.__name__,
                            "content_size_bytes": text_size_bytes,
                            "max_size": MAX_CONTENT_SIZE,
                            "reason_code": REASON_CONTENT_SIZE_EXCEEDED
                        }
                    )
                
                detections.extend(self._detect_secrets_in_text(notification_text))
            
            # Also check method name for potential secrets (though less common)
            if notification.method:
                method_detections = self._detect_secrets_in_text(notification.method)
                # Adjust detections to indicate they came from the method field
                for detection in method_detections:
                    detection["field"] = "method"
                detections.extend(method_detections)
        except Exception as e:
            logger.warning(f"Error analyzing notification for secrets: {e}")
        
        # Generate decision based on action mode
        if not detections:
            from watchgate.plugins.security import REASON_NONE
            return PolicyDecision(
                allowed=True,
                reason="No secrets detected in notification",
                metadata={
                    "plugin": self.__class__.__name__,
                    "secret_detected": False,
                    "detection_mode": self.action,
                    "detections": [],
                    "reason_code": REASON_NONE
                }
            )
        
        # Prepare metadata
        metadata = {
            "plugin": self.__class__.__name__,
            "secret_detected": True,
            "detection_mode": self.action,
            "detections": detections,
            "notification_method": notification.method
        }
        
        # Decide based on action mode
        from watchgate.plugins.security import REASON_SECRET_DETECTED
        if self.action == "block":
            metadata["reason_code"] = REASON_SECRET_DETECTED
            return PolicyDecision(
                allowed=False,
                reason=f"Secrets detected in notification - blocking transmission",
                metadata=metadata
            )
        elif self.action == "redact":
            # Create a redacted copy of the notification
            try:
                notification_text = json.dumps(notification.params, default=str) if notification.params else ""
                
                # Sort detections by position (reverse order to maintain positions)
                sorted_detections = sorted(detections, key=lambda x: x["position"][0], reverse=True)
                
                for detection in sorted_detections:
                    start, end = detection["position"]
                    if 0 <= start < end <= len(notification_text):
                        notification_text = (
                            notification_text[:start] + 
                            "[REDACTED BY WATCHGATE]" + 
                            notification_text[end:]
                        )
                
                # Parse back to params object
                modified_params = json.loads(notification_text) if notification_text else None
                
                # Create modified notification
                modified_notification = MCPNotification(
                    jsonrpc=notification.jsonrpc,
                    method=notification.method,
                    params=modified_params
                )
                
                metadata["reason_code"] = REASON_SECRET_DETECTED
                return PolicyDecision(
                    allowed=True,
                    reason=f"Secrets redacted from notification: {len(detections)} secret(s) redacted",
                    metadata=metadata,
                    modified_content=modified_notification
                )
                
            except Exception as e:
                logger.warning(f"Error redacting secrets from notification: {e}")
                # If redaction fails, fall back to blocking for security
                metadata["reason_code"] = REASON_SECRET_DETECTED
                return PolicyDecision(
                    allowed=False,
                    reason=f"Secret detected and redaction failed: {e}",
                    metadata=metadata
                )
        elif self.action == "audit_only":
            metadata["reason_code"] = REASON_SECRET_DETECTED
            return PolicyDecision(
                allowed=True,
                reason=f"Secrets detected in notification - audit only",
                metadata=metadata
            )
        
        # Default to blocking for unknown action (fail closed)
        return PolicyDecision(
            allowed=False,
            reason="Unknown action mode",
            metadata=metadata
        )


# Policy manifest for plugin discovery
POLICIES = {
    "secrets": BasicSecretsFilterPlugin
}
