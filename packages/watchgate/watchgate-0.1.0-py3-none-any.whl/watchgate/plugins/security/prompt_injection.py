"""Basic Prompt Injection Defense Plugin implementation.

⚠️  WARNING: This plugin provides only basic prompt injection protection and is NOT 
suitable for production use. It uses simple regex patterns which can be bypassed. 
For production environments, implement enterprise-grade prompt injection detection solutions.

This plugin provides basic detection of obvious prompt injection patterns using simple
regex matching. It targets common low-sophistication attacks such as delimiter injection,
crude role manipulation, and basic context breaking attempts.

WARNING: This plugin provides only basic protection against unsophisticated attacks.
It will NOT detect:
- Semantic injections without obvious keywords
- Encoded attacks (Base64, ROT13, etc.)
- Synonym-based evasion techniques  
- Multi-turn conversation attacks
- Context-dependent manipulation
- Advanced jailbreaking techniques

For production environments with serious security requirements, implement additional
AI-based detection systems or human review processes.
"""

import re
import time
import logging
from typing import Dict, Any, List, Tuple
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.utils.encoding import is_data_url

logger = logging.getLogger(__name__)

# Content processing constants
CHUNK_SIZE = 65536  # 64KB - optimal for performance and memory usage
OVERLAP_SIZE = 1024  # 1KB overlap to catch patterns at chunk boundaries


class BasicPromptInjectionDefensePlugin(SecurityPlugin):
    """Security plugin that detects basic, obvious prompt injection patterns."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration."""
        # Validate configuration type first
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Initialize base class to set priority
        super().__init__(config)
        
        # Validate action parameter
        action = config.get("action", "block")
        if action not in ["block", "audit_only"]:
            raise ValueError(f"Invalid action '{action}'. Must be one of: block, audit_only")
        self.action = action
        
        # Validate sensitivity parameter
        sensitivity = config.get("sensitivity", "standard")
        if sensitivity not in ["standard", "strict"]:
            raise ValueError(f"Invalid sensitivity '{sensitivity}'. Must be one of: standard, strict")
        self.sensitivity = sensitivity
        
        
        # Initialize detection methods with defaults
        detection_methods = config.get("detection_methods", {})
        self.detection_methods = {
            "delimiter_injection": detection_methods.get("delimiter_injection", {"enabled": True}),
            "role_manipulation": detection_methods.get("role_manipulation", {"enabled": True}),
            "context_breaking": detection_methods.get("context_breaking", {"enabled": True})
        }
        
        # Initialize custom patterns
        custom_patterns = config.get("custom_patterns", [])
        self.custom_patterns = []
        for pattern_config in custom_patterns:
            try:
                # Validate and compile regex pattern
                compiled_pattern = re.compile(pattern_config["pattern"], re.IGNORECASE)
                self.custom_patterns.append({
                    "name": pattern_config["name"],
                    "pattern": pattern_config["pattern"],
                    "compiled": compiled_pattern,
                    "enabled": pattern_config.get("enabled", True)
                })
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern_config['pattern']}': {e}")
        
        # Initialize exemptions
        exemptions = config.get("exemptions", {})
        self.exemptions = {
            "tools": set(exemptions.get("tools", []))
        }
        
        # Compile detection patterns based on sensitivity
        self._compile_detection_patterns()
    
    def _compile_detection_patterns(self):
        """Compile regex patterns for injection detection based on sensitivity level."""
        self.compiled_patterns = {}
        
        # Delimiter injection patterns
        if self.detection_methods["delimiter_injection"]["enabled"]:
            delimiter_patterns = [
                r'["\']{3,}.*?(?:system|admin|override|ignore).*?["\']{3,}',  # Triple quotes with injection keywords
                r'```.*?(?:system|admin|override|ignore).*?```',  # Markdown code blocks
                r'~~~.*?(?:system|admin|override|ignore).*?~~~',  # Alternative code blocks
                r'<(?:system|admin|instruction|override)>.*?</(?:system|admin|instruction|override)>',  # XML/HTML tags
                r'\[(?:SYSTEM|ADMIN|USER|ASSISTANT)\].*?\[/(?:SYSTEM|ADMIN|USER|ASSISTANT)\]'  # Role delimiters
            ]
            
            if self.sensitivity == "strict":
                # More aggressive patterns for strict mode
                delimiter_patterns.extend([
                    r'["\']{{2,}}.*?(?:bypass|disable|cancel).*?["\']{{2,}}',
                    r'```[^`]*(?:bypass|disable|cancel)[^`]*```'
                ])
            
            self.compiled_patterns["delimiter_injection"] = [
                re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in delimiter_patterns
            ]
        
        # Role manipulation patterns - More specific to reduce false positives while maintaining security
        if self.detection_methods["role_manipulation"]["enabled"]:
            role_patterns = [
                # Original patterns but with DAN added and slight refinements
                r'(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be)\s+(?:an?\s+)?(?:admin|administrator|system|root|superuser|DAN)\b',
                r'(?:ignore|disregard)\s+(?:previous|earlier|original)\s+(?:role|instructions|commands)\b',
                r'(?:as\s+)?(?:admin|administrator|system)\s*[:,]?\s*(?:execute|run|bypass)\b',
                r'(?:with|using)\s+(?:elevated|admin|administrative|system)\s+(?:privileges|access|rights)\b',
                r'administrator\s+mode\s*:',
                r'you\s+are\s+now\s+operating\s+as\s+(?:root|admin|system)\b',
                r'act\s+as\s+if\s+you\s+are\s+(?:a|an)?\s*(?:security|admin|system)\s+(?:bypass|override)\b'
            ]
            
            if self.sensitivity == "strict":
                # More aggressive patterns for strict mode
                role_patterns.extend([
                    r'(?:you\s+are|act\s+as)\s+(?:an?\s+)?(?:admin|administrator)\b',
                    r'admin\s+(?:mode|access|override)\b'
                ])
            
            self.compiled_patterns["role_manipulation"] = [
                re.compile(pattern, re.IGNORECASE) for pattern in role_patterns
            ]
        
        # Context breaking patterns - More specific to reduce false positives on legitimate conversation starters 
        if self.detection_methods["context_breaking"]["enabled"]:
            context_patterns = [
                r'(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|earlier|original|everything)?\s*(?:instructions|commands|rules)\b',
                r'(?:forget|ignore)\s+(?:everything|all)\s+(?:you|that|previous|above)\b',
                r'(?:reset|clear)\s+(?:context|conversation|session|memory|all)\b',
                r'(?:start|begin)\s+(?:fresh|new)\s+(?:and|then)\s+(?:ignore|reset|forget)\b',  # Explicit reset + ignore combinations
                r'(?:new|fresh)\s+(?:conversation|session)\s*[:,]\s*(?:reset|ignore|forget)\b',  # "New conversation: reset..."
                r'(?:begin|start)\s+(?:new\s+session|fresh)\s+without\s+(?:restrictions|limitations|rules)\b',  # "Begin new session without restrictions"
                r'reset\s+(?:context|all\s+parameters)\s+and\s+start\s+over\b',  # "Reset context and start over"
                r'(?:override|bypass|disable)\s+(?:all|safety|security)\s*(?:instructions|protocols|rules)?\b',
                r'(?:override|bypass|disable)\s+(?:all|any)\s+(?:safety|security)\s+(?:instructions|protocols|rules)\b',
                # Remove the generic "start fresh/new" patterns that cause false positives
                # Keep only explicit injection-intent patterns
                r'(?:start|begin)\s+(?:fresh|new|over)\s+(?:by|with)\s+(?:ignoring|forgetting|disregarding)\s+(?:all|everything|previous|instructions)\b'
            ]
            
            if self.sensitivity == "strict":
                # More aggressive patterns for strict mode
                context_patterns.extend([
                    r'(?:ignore|forget)\s+(?:this|that|instructions)\b',
                    # Keep the generic new conversation pattern only in strict mode
                    r'(?:new|fresh)\s+(?:conversation|session)\b'
                ])
            
            self.compiled_patterns["context_breaking"] = [
                re.compile(pattern, re.IGNORECASE) for pattern in context_patterns
            ]
    
    def _extract_text_from_request(self, request: MCPRequest) -> List[str]:
        """Extract text content from MCP request for analysis."""
        text_content = []
        
        if request.params:
            # Recursively extract string values from params
            def extract_strings(obj):
                if isinstance(obj, str):
                    text_content.append(obj)
                elif isinstance(obj, dict):
                    for value in obj.values():
                        extract_strings(value)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_strings(item)
            
            extract_strings(request.params)
        
        return text_content
    
    def _decode_potential_encodings(self, text: str) -> List[Tuple[str, str]]:
        """Attempt to decode potentially encoded attack payloads.
        
        Returns list of (decoded_text, encoding_type) tuples.
        Only decodes strings that look like they might be encoded.
        Includes deduplication and validation.
        """
        from watchgate.utils.encoding import safe_decode_base64
        
        decoded_versions = []
        seen_texts = {text}  # Track to avoid duplicates
        
        # Skip data URLs entirely
        if is_data_url(text):
            return []
        
        # Check for base64 encoding (min 40 chars to minimize false positives)
        # Note: Higher threshold dramatically reduces false positives on legitimate data
        if len(text) >= 40 and re.match(r'^[A-Za-z0-9+/]*={0,2}$', text) and len(text) % 4 == 0:
            # Use shared safe_decode_base64 utility
            decoded = safe_decode_base64(text, max_decode_size=10240)
            if decoded and len(decoded) > 5 and decoded not in seen_texts:
                decoded_versions.append((decoded, 'base64'))
                seen_texts.add(decoded)
        
        # ROT13 detection removed - too many false positives for minimal benefit
        # Real-world prompt injection attacks rarely use ROT13 encoding
        
        return decoded_versions
    
    def _process_text_chunk(self, text: str, offset: int = 0) -> List[Dict[str, Any]]:
        """Process a single chunk of text for injection patterns."""
        detections = []
        
        # Check delimiter injection patterns
        if "delimiter_injection" in self.compiled_patterns:
            for i, pattern in enumerate(self.compiled_patterns["delimiter_injection"]):
                matches = pattern.finditer(text)
                for match in matches:
                    detections.append({
                        "category": "delimiter_injection",
                        "pattern": f"delimiter_pattern_{i}",
                        "matched_text": match.group()[:100],  # Truncate for logging
                        "position": [match.start() + offset, match.end() + offset],
                        "confidence": "high"
                    })
        
        # Check role manipulation patterns
        if "role_manipulation" in self.compiled_patterns:
            for i, pattern in enumerate(self.compiled_patterns["role_manipulation"]):
                matches = pattern.finditer(text)
                for match in matches:
                    detections.append({
                        "category": "role_manipulation",
                        "pattern": f"role_pattern_{i}",
                        "matched_text": match.group()[:100],
                        "position": [match.start() + offset, match.end() + offset],
                        "confidence": "high"
                    })
        
        # Check context breaking patterns
        if "context_breaking" in self.compiled_patterns:
            for i, pattern in enumerate(self.compiled_patterns["context_breaking"]):
                matches = pattern.finditer(text)
                for match in matches:
                    detections.append({
                        "category": "context_breaking",
                        "pattern": f"context_pattern_{i}",
                        "matched_text": match.group()[:100],
                        "position": [match.start() + offset, match.end() + offset],
                        "confidence": "high"
                    })
        
        # Check custom patterns
        for custom_pattern in self.custom_patterns:
            if custom_pattern["enabled"]:
                matches = custom_pattern["compiled"].finditer(text)
                for match in matches:
                    detections.append({
                        "category": "custom_pattern",
                        "pattern": custom_pattern["name"],
                        "matched_text": match.group()[:100],
                        "position": [match.start() + offset, match.end() + offset],
                        "confidence": "high"
                    })
        
        return detections

    def _detect_injections(self, text_content: List[str]) -> List[Dict[str, Any]]:
        """Detect injection patterns in text content, including encoded versions."""
        from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED, REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
        
        detections = []
        total_decoded_size = 0
        
        for text in text_content:
            if not text:
                continue
            
            # Size check is now done earlier in check_request - no need to duplicate here
            
            # Check original text
            original_detections = self._process_single_text(text, 'original')
            detections.extend(original_detections)
            
            # Also check decoded versions if they exist
            decoded_versions = self._decode_potential_encodings(text)
            for decoded_text, encoding_type in decoded_versions:
                # Limit total decoded content size to prevent DoS
                total_decoded_size += len(decoded_text.encode('utf-8'))
                if total_decoded_size > MAX_CONTENT_SIZE:
                    logger.warning("Decoded content size limit exceeded, skipping further decoding")
                    break
                
                # Process the decoded text
                decoded_detections = self._process_single_text(decoded_text, encoding_type)
                detections.extend(decoded_detections)
        
        return detections
    
    def _process_single_text(self, text: str, encoding_type: str) -> List[Dict[str, Any]]:
        """Process a single text string for injection patterns."""
        from watchgate.plugins.security import REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
        
        detections = []
        
        # Process in chunks if text is large  
        if len(text) > CHUNK_SIZE:
            # Process with overlapping chunks to catch patterns at boundaries
            offset = 0
            while offset < len(text):
                # Calculate chunk boundaries with overlap
                chunk_end = min(offset + CHUNK_SIZE, len(text))
                chunk = text[offset:chunk_end]
                
                # Process this chunk
                chunk_detections = self._process_text_chunk(chunk, offset)
                
                # Add encoding_type to detections and set reason codes
                for detection in chunk_detections:
                    detection["encoding_type"] = encoding_type
                    if encoding_type != 'original':
                        detection["reason_code"] = REASON_ENCODED_INJECTION_DETECTED
                    else:
                        detection["reason_code"] = REASON_INJECTION_DETECTED
                    
                    # Check if this detection overlaps with existing ones
                    is_duplicate = False
                    for existing in detections:
                        if (detection["category"] == existing["category"] and
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
            chunk_detections = self._process_text_chunk(text, 0)
            
            # Add encoding_type to detections
            for detection in chunk_detections:
                detection["encoding_type"] = encoding_type
                if encoding_type != 'original':
                    detection["reason_code"] = REASON_ENCODED_INJECTION_DETECTED
                else:
                    detection["reason_code"] = REASON_INJECTION_DETECTED
                detections.append(detection)
        
        return detections
    
    def _is_tool_exempt(self, request: MCPRequest) -> bool:
        """Check if the request is from an exempt tool."""
        if request.method == "tools/call" and request.params and "name" in request.params:
            tool_name = request.params["name"]
            return tool_name in self.exemptions["tools"]
        return False
    
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        """Check if request contains prompt injection attempts."""
        start_time = time.time()
        
        try:
            # Check tool exemptions first
            if self._is_tool_exempt(request):
                return PolicyDecision(
                    allowed=True,
                    reason="Tool is exempt from prompt injection defense",
                    metadata={
                        "plugin": "prompt_injection",
                        "injection_detected": False,
                        "exemption_applied": True,
                        "processing_time_ms": round((time.time() - start_time) * 1000, 2)
                    }
                )
            
            # Extract text content from request
            text_content = self._extract_text_from_request(request)
            
            # Check content size before processing (early DoS protection)
            from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED
            for text in text_content:
                if text:
                    text_size_bytes = len(text.encode('utf-8'))
                    if text_size_bytes > MAX_CONTENT_SIZE:
                        return PolicyDecision(
                            allowed=False,
                            reason=f"Content exceeds maximum size limit ({MAX_CONTENT_SIZE} bytes)",
                            metadata={
                                "plugin": self.__class__.__name__,
                                "content_size_bytes": text_size_bytes,
                                "max_size": MAX_CONTENT_SIZE,
                                "reason_code": REASON_CONTENT_SIZE_EXCEEDED,
                                "processing_time_ms": round((time.time() - start_time) * 1000, 2)
                            }
                        )
            
            # Detect injection patterns
            detections = self._detect_injections(text_content)
            
            processing_time_ms = round((time.time() - start_time) * 1000, 2)
            
            # Prepare metadata
            metadata = {
                "plugin": "prompt_injection",
                "injection_detected": len(detections) > 0,
                "detection_mode": self.action,
                "sensitivity_level": self.sensitivity,
                "detections": detections,
                "total_detections": len(detections),
                "exemption_applied": False,
                "processing_time_ms": processing_time_ms
            }
            
            # Return decision based on mode and detections
            if len(detections) == 0:
                return PolicyDecision(
                    allowed=True,
                    reason="No prompt injection detected",
                    metadata=metadata
                )
            
            
            # Injection detected - handle based on mode
            if self.action == "block":
                from watchgate.plugins.security import REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
                # Determine reason code based on detection types
                has_encoded = any(d.get("encoding_type") != 'original' for d in detections)
                reason_code = REASON_ENCODED_INJECTION_DETECTED if has_encoded else REASON_INJECTION_DETECTED
                metadata["reason_code"] = reason_code
                
                return PolicyDecision(
                    allowed=False,
                    reason=f"Prompt injection detected: {len(detections)} pattern(s) found",
                    metadata=metadata
                )
            elif self.action == "audit_only":
                from watchgate.plugins.security import REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
                # Determine reason code based on detection types
                has_encoded = any(d.get("encoding_type") != 'original' for d in detections)
                reason_code = REASON_ENCODED_INJECTION_DETECTED if has_encoded else REASON_INJECTION_DETECTED
                metadata["reason_code"] = reason_code
                
                return PolicyDecision(
                    allowed=True,
                    reason=f"Injection attempt logged: {len(detections)} pattern(s) found",
                    metadata=metadata
                )
            
        except Exception as e:
            # Fail closed on errors
            logger.error(f"Error in prompt injection detection: {e}")
            return PolicyDecision(
                allowed=False,
                reason=f"Error during injection detection: {str(e)}",
                metadata={
                    "plugin": "prompt_injection",
                    "error": str(e),
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2)
                }
            )
    
    async def check_response(self, request: MCPRequest, response: MCPResponse, server_name: str) -> PolicyDecision:
        """Check if response contains prompt injection attempts.
        
        This is critical for preventing injection attacks embedded in file contents,
        API responses, or other data sources that might be returned to the user.
        """
        start_time = time.time()
        
        try:
            # Check tool exemptions first
            if self._is_tool_exempt(request):
                return PolicyDecision(
                    allowed=True,
                    reason="Tool is exempt from prompt injection defense",
                    metadata={
                        "plugin": "prompt_injection",
                        "injection_detected": False,
                        "exemption_applied": True,
                        "processing_time_ms": round((time.time() - start_time) * 1000, 2)
                    }
                )
            
            # Extract text content from response
            text_content = []
            if response.result:
                def extract_strings(obj):
                    if isinstance(obj, str):
                        text_content.append(obj)
                    elif isinstance(obj, dict):
                        for value in obj.values():
                            extract_strings(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_strings(item)
                
                extract_strings(response.result)
            
            # Check content size before processing (early DoS protection)
            from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED
            for text in text_content:
                if text:
                    text_size_bytes = len(text.encode('utf-8'))
                    if text_size_bytes > MAX_CONTENT_SIZE:
                        return PolicyDecision(
                            allowed=False,
                            reason=f"Response content exceeds maximum size limit ({MAX_CONTENT_SIZE} bytes)",
                            metadata={
                                "plugin": self.__class__.__name__,
                                "content_size_bytes": text_size_bytes,
                                "max_size": MAX_CONTENT_SIZE,
                                "reason_code": REASON_CONTENT_SIZE_EXCEEDED,
                                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                                "check_type": "response"
                            }
                        )
            
            # Detect injection patterns in response content
            detections = self._detect_injections(text_content)
            
            processing_time_ms = round((time.time() - start_time) * 1000, 2)
            
            # Prepare metadata
            metadata = {
                "plugin": "prompt_injection",
                "injection_detected": len(detections) > 0,
                "detection_mode": self.action,
                "sensitivity_level": self.sensitivity,
                "detections": detections,
                "total_detections": len(detections),
                "exemption_applied": False,
                "processing_time_ms": processing_time_ms,
                "check_type": "response"
            }
            
            # Return decision based on mode and detections
            if len(detections) == 0:
                return PolicyDecision(
                    allowed=True,
                    reason="No prompt injection detected in response",
                    metadata=metadata
                )
            
            
            # Injection detected in response - handle based on mode
            if self.action == "block":
                from watchgate.plugins.security import REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
                # Determine reason code based on detection types
                has_encoded = any(d.get("encoding_type") != 'original' for d in detections)
                reason_code = REASON_ENCODED_INJECTION_DETECTED if has_encoded else REASON_INJECTION_DETECTED
                metadata["reason_code"] = reason_code
                
                return PolicyDecision(
                    allowed=False,
                    reason=f"Prompt injection detected in response: {len(detections)} pattern(s) found",
                    metadata=metadata
                )
            elif self.action == "audit_only":
                from watchgate.plugins.security import REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
                # Determine reason code based on detection types
                has_encoded = any(d.get("encoding_type") != 'original' for d in detections)
                reason_code = REASON_ENCODED_INJECTION_DETECTED if has_encoded else REASON_INJECTION_DETECTED
                metadata["reason_code"] = reason_code
                
                return PolicyDecision(
                    allowed=True,
                    reason=f"Injection attempt in response logged: {len(detections)} pattern(s) found",
                    metadata=metadata
                )
            
        except Exception as e:
            # Fail closed on errors
            logger.error(f"Error in prompt injection detection for response: {e}")
            return PolicyDecision(
                allowed=False,
                reason=f"Error during response injection detection: {str(e)}",
                metadata={
                    "plugin": "prompt_injection",
                    "error": str(e),
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2)
                }
            )
    
    async def check_notification(self, notification: MCPNotification, server_name: str) -> PolicyDecision:
        """Check if notification contains prompt injection attempts.
        
        Notifications can be another vector for injection attacks and should be
        checked with the same rigor as requests and responses.
        """
        start_time = time.time()
        
        try:
            # Extract text content from notification
            text_content = []
            if notification.params:
                def extract_strings(obj):
                    if isinstance(obj, str):
                        text_content.append(obj)
                    elif isinstance(obj, dict):
                        for value in obj.values():
                            extract_strings(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_strings(item)
                
                extract_strings(notification.params)
            
            # Also check the method name itself for injection patterns
            if notification.method:
                text_content.append(notification.method)
            
            # Check content size before processing (early DoS protection)
            from watchgate.plugins.security import MAX_CONTENT_SIZE, REASON_CONTENT_SIZE_EXCEEDED
            for text in text_content:
                if text:
                    text_size_bytes = len(text.encode('utf-8'))
                    if text_size_bytes > MAX_CONTENT_SIZE:
                        return PolicyDecision(
                            allowed=False,
                            reason=f"Notification content exceeds maximum size limit ({MAX_CONTENT_SIZE} bytes)",
                            metadata={
                                "plugin": self.__class__.__name__,
                                "content_size_bytes": text_size_bytes,
                                "max_size": MAX_CONTENT_SIZE,
                                "reason_code": REASON_CONTENT_SIZE_EXCEEDED,
                                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                                "check_type": "notification"
                            }
                        )
            
            # Detect injection patterns
            detections = self._detect_injections(text_content)
            
            processing_time_ms = round((time.time() - start_time) * 1000, 2)
            
            # Prepare metadata
            metadata = {
                "plugin": "prompt_injection",
                "injection_detected": len(detections) > 0,
                "detection_mode": self.action,
                "sensitivity_level": self.sensitivity,
                "detections": detections,
                "total_detections": len(detections),
                "processing_time_ms": processing_time_ms,
                "check_type": "notification"
            }
            
            # Return decision based on mode and detections
            if len(detections) == 0:
                return PolicyDecision(
                    allowed=True,
                    reason="No prompt injection detected in notification",
                    metadata=metadata
                )
            
            
            # Injection detected in notification - handle based on mode
            if self.action == "block":
                from watchgate.plugins.security import REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
                # Determine reason code based on detection types
                has_encoded = any(d.get("encoding_type") != 'original' for d in detections)
                reason_code = REASON_ENCODED_INJECTION_DETECTED if has_encoded else REASON_INJECTION_DETECTED
                metadata["reason_code"] = reason_code
                
                return PolicyDecision(
                    allowed=False,
                    reason=f"Prompt injection detected in notification: {len(detections)} pattern(s) found",
                    metadata=metadata
                )
            elif self.action == "audit_only":
                from watchgate.plugins.security import REASON_INJECTION_DETECTED, REASON_ENCODED_INJECTION_DETECTED
                # Determine reason code based on detection types
                has_encoded = any(d.get("encoding_type") != 'original' for d in detections)
                reason_code = REASON_ENCODED_INJECTION_DETECTED if has_encoded else REASON_INJECTION_DETECTED
                metadata["reason_code"] = reason_code
                
                return PolicyDecision(
                    allowed=True,
                    reason=f"Injection attempt in notification logged: {len(detections)} pattern(s) found",
                    metadata=metadata
                )
            
        except Exception as e:
            # Fail closed on errors
            logger.error(f"Error in prompt injection detection for notification: {e}")
            return PolicyDecision(
                allowed=False,
                reason=f"Error during notification injection detection: {str(e)}",
                metadata={
                    "plugin": "prompt_injection",
                    "error": str(e),
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2)
                }
            )


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "prompt_injection": BasicPromptInjectionDefensePlugin
}
