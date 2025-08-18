"""CEF (Common Event Format) auditing plugin for Watchgate MCP gateway.

This module provides the CefAuditingPlugin class that logs MCP requests and responses
in CEF format for SIEM integration and compliance monitoring.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from watchgate.plugins.auditing.base import BaseAuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.utils.version import get_watchgate_version


# CEF Event Type Mappings
CEF_EVENT_MAPPINGS = {
    'REQUEST': {'event_id': '100', 'severity': 6, 'name': 'MCP Request'},
    'RESPONSE': {'event_id': '101', 'severity': 6, 'name': 'MCP Response'},
    'SECURITY_BLOCK': {'event_id': '200', 'severity': 8, 'name': 'Security Block'},
    'REDACTION': {'event_id': '201', 'severity': 7, 'name': 'Content Redaction'},
    'MODIFICATION': {'event_id': '203', 'severity': 7, 'name': 'Content Modification'},
    'ERROR': {'event_id': '400', 'severity': 9, 'name': 'System Error'},
    'UPSTREAM_ERROR': {'event_id': '401', 'severity': 8, 'name': 'Upstream Error'},
    'TOOLS_FILTERED': {'event_id': '202', 'severity': 7, 'name': 'Tools Filtered'},
    'NOTIFICATION': {'event_id': '102', 'severity': 4, 'name': 'MCP Notification'},
}

# Default mapping for unknown event types
DEFAULT_CEF_EVENT_MAPPING = {'event_id': '999', 'severity': 5, 'name': 'Unknown Event'}


class CefAuditingPlugin(BaseAuditingPlugin):
    """CEF (Common Event Format) auditing plugin.
    
    Logs MCP requests and responses in CEF format for SIEM integration.
    CEF is an industry-standard format widely accepted by security information
    and event management systems.
    
    Features:
    - Industry-standard CEF format for universal SIEM acceptance
    - Compliance-ready event structure
    - Security event classification and severity scoring
    - Configurable compliance tags and extensions
    - Risk scoring and regulatory field support
    """
    
    # Type annotations for class attributes
    device_vendor: str
    device_product: str
    device_version: str
    cef_version: str
    compliance_tags: List[str]
    risk_scoring: bool
    regulatory_fields: bool
    lean_mode: bool
    field_max_lengths: Dict[str, int]
    truncation_indicator: str
    drop_args: bool
    hash_large_fields: bool
    device_hostname: Optional[str]
    device_ip: Optional[str]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize CEF auditing plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary with CEF-specific options:
                   - device_vendor: Vendor name (default: "Watchgate")
                   - device_product: Product name (default: "MCP Gateway")
                   - device_version: Version string (default: auto-detected)
                   - compliance_tags: List of compliance frameworks
                   - risk_scoring: Enable risk scoring (default: True)
                   - regulatory_fields: Include regulatory fields (default: True)
                   Plus all BaseAuditingPlugin options (output_file, etc.)
                   
        Raises:
            ValueError: If configuration is invalid
            TypeError: If configuration has wrong types
        """
        # Initialize base class first
        super().__init__(config)
        
        # CEF-specific configuration - ALL from cef_config section
        cef_config = config.get("cef_config", {})
        
        # Device identification
        device_version = cef_config.get("device_version")
        if device_version == "auto":
            device_version = None  # Will use automatic detection
        
        self.device_vendor = cef_config.get("device_vendor", "Watchgate")
        self.device_product = cef_config.get("device_product", "MCP Gateway")
        self.device_version = device_version or get_watchgate_version()
        self.cef_version = "0"
        
        # Optional device fields for network correlation
        self.device_hostname = cef_config.get("device_hostname")
        self.device_ip = cef_config.get("device_ip")
        
        # Compliance Extensions
        self.compliance_tags = cef_config.get("compliance_tags", [])
        self.risk_scoring = cef_config.get("risk_scoring", True)
        self.regulatory_fields = cef_config.get("regulatory_fields", True)
        
        # Performance and privacy options
        self.lean_mode = cef_config.get("lean_mode", False)
        self.drop_args = cef_config.get("drop_args", False)
        self.hash_large_fields = cef_config.get("hash_large_fields", False)
        
        # Field length limits for sanitization
        self.field_max_lengths = cef_config.get("field_max_lengths", {
            'reason': 2000,
            'tool': 256,
            'method': 256,
            'plugin': 256,
            'server_name': 256,
            'device_hostname': 256,
            'device_ip': 50,
            'source_ip': 50,
            'destination_ip': 50,
            'args': 10000,
            'message': 10000,
            'default': 1000
        })
        self.truncation_indicator = cef_config.get("truncation_indicator", "...[truncated]")
        
        # Set high max_message_length to avoid double truncation
        self.max_message_length = cef_config.get("max_message_length", 50000)
        
        # Validate CEF configuration
        if not isinstance(self.device_vendor, str) or not self.device_vendor.strip():
            raise ValueError("device_vendor must be a non-empty string")
        
        if not isinstance(self.device_product, str) or not self.device_product.strip():
            raise ValueError("device_product must be a non-empty string")
        
        if not isinstance(self.device_version, str) or not self.device_version.strip():
            raise ValueError("device_version must be a non-empty string")
        
        if not isinstance(self.compliance_tags, list):
            raise ValueError("compliance_tags must be a list")
    
    def _sanitize_for_log(self, value: Optional[str], field_name: str = 'default') -> str:
        """Centralized sanitization - apply BEFORE CEF escaping.
        
        - Remove control characters
        - Apply configurable per-field length limits
        - Prevent log injection
        - Avoid double-escaping by sanitizing first
        """
        if value is None:
            return ""
        
        value = str(value)  # Ensure string type
        
        # Remove control characters except tab/newline
        sanitized = ''.join(char for char in value 
                          if char.isprintable() or char in '\t\n')
        
        # Replace newlines with escaped version
        sanitized = sanitized.replace('\n', '\\n').replace('\r', '\\r')
        
        # Apply field-specific length limit from config
        max_length = self.field_max_lengths.get(field_name, 
                                               self.field_max_lengths['default'])
        
        if len(sanitized) > max_length:
            # Use stored truncation_indicator
            sanitized = sanitized[:max_length-len(self.truncation_indicator)] + self.truncation_indicator
        
        return sanitized
    
    def _format_request_log(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> str:
        """Format a request log message in CEF format.
        
        Args:
            request: The MCP request
            decision: Policy decision
            server_name: Name of the target server
            
        Returns:
            str: CEF-formatted log message
        """
        # Determine event type based on security decision
        if not decision.allowed:
            # Use SECURITY_BLOCK for all blocked requests
            event_type = "SECURITY_BLOCK"
        else:
            # Check for special tool filtering events with metadata guard
            if (request.method == "tools/list" and 
                decision.metadata and  # Guard against None
                decision.metadata.get("filtered_count", 0) > 0):
                event_type = "TOOLS_FILTERED"
            else:
                event_type = "REQUEST"
        
        # Detect security modifications - ANY modified_content means modification
        if decision.modified_content is not None:
            event_type = "MODIFICATION"  # Default to modification
            
            # Check for redaction hint in reason
            if decision.reason and 'redact' in decision.reason.lower():
                event_type = "REDACTION"
        
        # Sanitize all user-controlled fields FIRST
        sanitized_reason = self._sanitize_for_log(decision.reason, 'reason')
        sanitized_method = self._sanitize_for_log(request.method, 'method')
        sanitized_tool = None
        if request.method == "tools/call" and request.params and "name" in request.params:
            sanitized_tool = self._sanitize_for_log(request.params["name"], 'tool')
        elif event_type == "SECURITY_BLOCK":
            sanitized_tool = "unknown"
        
        sanitized_server = self._sanitize_for_log(server_name, 'server_name')
        sanitized_plugin = self._sanitize_for_log(self._extract_plugin_info(decision), 'plugin')
        
        # Build event data with sanitized values
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "method": sanitized_method,
            "request_id": request.id,
            "status": "ALLOWED" if decision.allowed else "BLOCKED"
        }
        
        if sanitized_tool:
            event_data["tool"] = sanitized_tool
        
        if sanitized_plugin != "unknown":
            event_data["plugin"] = sanitized_plugin
        
        if sanitized_reason:
            event_data["reason"] = sanitized_reason
        
        # Add request arguments if not dropped
        if not self.drop_args and hasattr(request, 'params'):
            event_data["args"] = request.params
        
        event_data["server_name"] = sanitized_server
        
        return self._format_cef_message(event_data)
    
    def _format_response_log(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> str:
        """Format a response log message in CEF format.
        
        Args:
            request: The original MCP request
            response: The MCP response
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: CEF-formatted log message
        """
        # Determine response status and event type based on security decision first
        if not decision.allowed:
            # Security plugin blocked the response
            event_type = "SECURITY_BLOCK"
        elif decision.modified_content is not None:
            # Security plugin modified the response - default to MODIFICATION
            if isinstance(request, MCPRequest) and request.method == "tools/list":
                event_type = "TOOLS_FILTERED"
            elif decision.reason and 'redact' in decision.reason.lower():
                event_type = "REDACTION"
            else:
                event_type = "MODIFICATION"
        elif hasattr(response, 'error') and response.error:
            # Response has error - distinguish between upstream and Watchgate errors
            event_type = "UPSTREAM_ERROR" if response.error.get('code', 0) < -32000 else "ERROR"
        else:
            # Successful response
            event_type = "RESPONSE"
        
        # Sanitize all user-controlled fields FIRST
        sanitized_reason = self._sanitize_for_log(decision.reason, 'reason')
        sanitized_plugin = self._sanitize_for_log(self._extract_plugin_info(decision), 'plugin')
        sanitized_server = self._sanitize_for_log(server_name, 'server_name')
        
        # Build event data with sanitized values
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": response.id,
        }
        
        # Set status based on event type
        if event_type == "RESPONSE":
            event_data["status"] = "SUCCESS"
        elif "ERROR" in event_type:
            event_data["status"] = "ERROR"
        elif event_type == "SECURITY_BLOCK":
            event_data["status"] = "BLOCKED"
        else:
            event_data["status"] = "MODIFIED"
        
        if sanitized_plugin != "unknown":
            event_data["plugin"] = sanitized_plugin
        
        if sanitized_reason:
            event_data["reason"] = sanitized_reason
        
        # Add duration if available in metadata (with guard)
        if decision.metadata and "duration_ms" in decision.metadata:
            event_data["duration_ms"] = decision.metadata["duration_ms"]
        
        # Add response content if configured (could be result or error)
        if not self.drop_args:
            if hasattr(response, 'result'):
                event_data["args"] = response.result
            elif hasattr(response, 'error'):
                event_data["args"] = response.error
        
        event_data["server_name"] = sanitized_server
        
        return self._format_cef_message(event_data)
    
    def _format_notification_log(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> str:
        """Format a notification log message in CEF format.
        
        Args:
            notification: The MCP notification
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: CEF-formatted log message
        """
        # Sanitize all user-controlled fields FIRST
        sanitized_method = self._sanitize_for_log(notification.method, 'method')
        sanitized_reason = self._sanitize_for_log(decision.reason, 'reason')
        sanitized_plugin = self._sanitize_for_log(self._extract_plugin_info(decision), 'plugin')
        sanitized_server = self._sanitize_for_log(server_name, 'server_name')
        
        # Build event data with sanitized values
        event_data = {
            "event_type": "NOTIFICATION",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "method": sanitized_method,
            "status": "NOTIFICATION"
        }
        
        if sanitized_plugin != "unknown":
            event_data["plugin"] = sanitized_plugin
        
        if sanitized_reason:
            event_data["reason"] = sanitized_reason
        
        event_data["server_name"] = sanitized_server
        
        return self._format_cef_message(event_data)
    
    
    def _format_cef_message(self, event_data: Dict[str, Any]) -> str:
        """Format Watchgate event as CEF message.
        
        Args:
            event_data: Event data dictionary from Watchgate
            
        Returns:
            str: Formatted CEF message
        """
        # Get event mapping
        event_type = event_data.get('event_type', 'UNKNOWN')
        event_mapping = CEF_EVENT_MAPPINGS.get(event_type, DEFAULT_CEF_EVENT_MAPPING)
        
        # Build CEF header
        header_parts = [
            f"CEF:{self.cef_version}",
            self._escape_cef_header(self.device_vendor),
            self._escape_cef_header(self.device_product),
            self._escape_cef_header(self.device_version),
            self._escape_cef_header(event_mapping['event_id']),
            self._escape_cef_header(event_mapping['name']),
            self._escape_cef_header(str(event_mapping['severity']))
        ]
        
        # Build extension fields
        extensions = []
        
        # Required fields
        if 'timestamp' in event_data:
            cef_timestamp = self._convert_to_cef_timestamp(event_data['timestamp'])
            extensions.append(f"rt={self._escape_cef_extension(cef_timestamp)}")
        
        if 'request_id' in event_data:
            extensions.append(f"requestId={self._escape_cef_extension(str(event_data['request_id']))}")
        
        # Action based on status - ALWAYS normalize to lowercase
        status = event_data.get('status', '')
        if status:
            normalized_status = str(status).lower()
            extensions.append(f"act={self._escape_cef_extension(normalized_status)}")
        
        # Optional fields using CEF custom strings
        if 'reason' in event_data:
            extensions.append(f"reason={self._escape_cef_extension(event_data['reason'])}")
        
        if 'plugin' in event_data:
            extensions.append(f"cs1={self._escape_cef_extension(event_data['plugin'])}")
            extensions.append("cs1Label=Plugin")
            # Only add duplicate standard field if not in lean mode
            if not self.lean_mode:
                extensions.append(f"sourceUserName={self._escape_cef_extension(event_data['plugin'])}")
        
        if 'method' in event_data:
            extensions.append(f"cs2={self._escape_cef_extension(event_data['method'])}")
            extensions.append("cs2Label=Method")
            if not self.lean_mode:
                extensions.append(f"requestMethod={self._escape_cef_extension(event_data['method'])}")
        
        if 'tool' in event_data:
            extensions.append(f"cs3={self._escape_cef_extension(event_data['tool'])}")
            extensions.append("cs3Label=Tool")
            if not self.lean_mode:
                extensions.append(f"fileName={self._escape_cef_extension(event_data['tool'])}")
        
        if 'duration_ms' in event_data:
            extensions.append(f"cs4={self._escape_cef_extension(str(event_data['duration_ms']))}")
            extensions.append("cs4Label=Duration")
            if not self.lean_mode:
                extensions.append(f"duration={self._escape_cef_extension(str(event_data['duration_ms']))}")
        
        if 'server_name' in event_data:
            extensions.append(f"cs5={self._escape_cef_extension(event_data['server_name'])}")
            extensions.append("cs5Label=Server")
            if not self.lean_mode:
                extensions.append(f"destinationServiceName={self._escape_cef_extension(event_data['server_name'])}")
        
        # Additional standard CEF fields
        if 'user' in event_data:
            extensions.append(f"duser={self._escape_cef_extension(str(event_data['user']))}")
        
        if 'args' in event_data and not self.drop_args:
            args_str = str(event_data['args']) if event_data['args'] is not None else ''
            if self.hash_large_fields and len(args_str) > self.field_max_lengths.get('args', 10000):
                import hashlib
                hash_val = hashlib.sha256(args_str.encode()).hexdigest()[:16]
                extensions.append(f"msg=[SHA256:{hash_val}...{self.truncation_indicator}]")
            else:
                sanitized_args = self._sanitize_for_log(args_str, 'args')
                extensions.append(f"msg={self._escape_cef_extension(sanitized_args)}")
        
        # Compliance Extensions
        if self.compliance_tags:
            compliance_str = ",".join(self.compliance_tags)
            extensions.append(f"cs6={self._escape_cef_extension(compliance_str)}")
            extensions.append("cs6Label=Compliance")
        
        # Network fields - NO misleading defaults!
        source_ip = event_data.get('source_ip')
        destination_ip = event_data.get('destination_ip')
        
        # Only add if actually known (sanitize first!)
        if source_ip is not None:
            sanitized_src = self._sanitize_for_log(str(source_ip), 'source_ip')
            extensions.append(f"src={self._escape_cef_extension(sanitized_src)}")
        
        if destination_ip is not None:
            sanitized_dst = self._sanitize_for_log(str(destination_ip), 'destination_ip')
            extensions.append(f"dst={self._escape_cef_extension(sanitized_dst)}")
        
        # Add device fields only if configured (ALWAYS sanitize first!)
        if self.device_hostname:
            sanitized_hostname = self._sanitize_for_log(self.device_hostname, 'device_hostname')
            extensions.append(f"dvchost={self._escape_cef_extension(sanitized_hostname)}")
        
        if self.device_ip:
            sanitized_ip = self._sanitize_for_log(self.device_ip, 'device_ip')
            extensions.append(f"dvc={self._escape_cef_extension(sanitized_ip)}")
        # NEVER default to 127.0.0.1 or 'watchgate' - omit if unknown
        
        # Combine header and extensions
        header = '|'.join(header_parts)
        extension = ' '.join(extensions)
        
        return f"{header}|{extension}"
    
    def _escape_cef_header(self, value: str) -> str:
        """Escape header field values (pipe and backslash).
        
        Args:
            value: Value to escape
            
        Returns:
            str: Escaped value
        """
        return str(value).replace('\\', '\\\\').replace('|', '\\|')
    
    def _escape_cef_extension(self, value: str) -> str:
        """Escape extension field values (backslash, equals, newlines, pipes).
        
        Args:
            value: Value to escape
            
        Returns:
            str: Escaped value
        """
        return str(value).replace('\\', '\\\\').replace('=', '\\=').replace('\n', '\\n').replace('\r', '\\r').replace('|', '\\|')
    
    def _convert_to_cef_timestamp(self, timestamp: str) -> str:
        """Convert ISO timestamp to CEF format with UTC normalization.
        
        Args:
            timestamp: ISO timestamp string (any timezone)
            
        Returns:
            str: CEF timestamp in UTC (MMM dd yyyy HH:mm:ss)
        """
        try:
            from datetime import datetime, timezone
            
            # Parse ISO timestamp with timezone awareness
            if timestamp.endswith('Z'):
                dt = datetime.fromisoformat(timestamp[:-1]).replace(tzinfo=timezone.utc)
            elif '+' in timestamp or timestamp.count('-') > 2:
                # Has timezone offset
                dt = datetime.fromisoformat(timestamp)
            else:
                # No timezone, assume UTC
                dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
            
            # Normalize to UTC
            dt_utc = dt.astimezone(timezone.utc)
            
            # Format for CEF (human-readable UTC)
            # Document: All CEF timestamps are normalized to UTC
            return dt_utc.strftime("%b %d %Y %H:%M:%S")
            
        except Exception as e:
            # Log warning about timestamp parse failure (ensure logger exists)
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"Failed to parse timestamp {timestamp}: {e}")
            # Return original on failure
            return timestamp
    
    def _extract_plugin_info(self, decision: Optional[PolicyDecision]) -> str:
        """Robustly extract plugin information.
        
        Args:
            decision: The policy decision containing metadata
            
        Returns:
            str: Plugin name or 'unknown' if not found
        """
        try:
            if decision is None:
                return "unknown"
            
            if hasattr(decision, 'plugin_name') and decision.plugin_name:
                return str(decision.plugin_name)
            
            if hasattr(decision, 'metadata') and decision.metadata:
                if isinstance(decision.metadata, dict):
                    return decision.metadata.get('plugin', 'unknown')
            
            return "unknown"
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"Failed to extract plugin info: {e}")
            return "unknown"


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "cef_auditing": CefAuditingPlugin
}