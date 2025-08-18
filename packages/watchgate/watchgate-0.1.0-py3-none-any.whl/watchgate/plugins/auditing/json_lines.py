"""JSON auditing plugin for Watchgate MCP gateway.

This module provides the JsonAuditingPlugin class that logs MCP requests and responses
in JSON format for GRC platform integration and compliance automation,
supporting modern API integration and automated compliance analysis.

For JSON Lines (JSONL) format, set pretty_print=False in configuration.
"""

import json
from typing import Dict, Any, Union
from datetime import datetime, timezone
from watchgate.plugins.auditing.base import BaseAuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision


# Constants for compliance metadata
API_VERSION = "1.0"
SCHEMA_VERSION = "2024.1"
REGULATORY_FRAMEWORKS = {
    "financial_services": ["SOX", "GDPR"],
    "standard": [],
    "grc_standard": ["INTERNAL_GRC"]
}


class JsonAuditingPlugin(BaseAuditingPlugin):
    """JSON auditing plugin for GRC platform integration.
    
    Logs MCP requests and responses in JSON format for modern GRC
    (Governance, Risk, Compliance) platform integration and compliance automation.
    Provides machine-readable format for automated compliance analysis.
    
    Features:
    - JSON format (use pretty_print=False for JSON Lines compatibility)
    - GRC platform integration ready
    - Compliance schema support
    - Risk metadata inclusion
    - API-compatible structured format
    - Cloud-native compliance tool integration
    """
    
    # Type annotations for class attributes
    include_request_body: bool
    pretty_print: bool
    compliance_schema: str
    include_risk_metadata: bool
    api_compatible: bool
    timestamp_format: str
    redact_request_fields: list
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize JSON auditing plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary with JSON-specific options:
                   - include_request_body: Include full request parameters (default: False)
                   - pretty_print: Format JSON with indentation (default: False)
                   - compliance_schema: "standard", "grc_standard", "financial_services" (default: "standard")
                   - include_risk_metadata: Include risk assessment metadata (default: True)
                   - api_compatible: Ensure API-compatible field names (default: True)
                   - timestamp_format: "iso8601", "unix_timestamp" (default: "iso8601")
                   - redact_request_fields: List of field names to redact from request_body (default: ["password", "token", "secret", "key", "auth"])
                   Plus all BaseAuditingPlugin options (output_file, etc.)
                   
        Raises:
            ValueError: If configuration is invalid
            TypeError: If configuration has wrong types
        """
        # Initialize base class first
        super().__init__(config)
        
        # Track configuration overrides for traceability
        self._config_overrides = {}
        
        # JSON-specific configuration
        self.include_request_body = config.get("include_request_body", False)
        self.pretty_print = config.get("pretty_print", False)
        
        # JSON Lines format requires single-line output
        # If output_format is explicitly set to 'jsonl', enforce single-line output
        if config.get('output_format') == 'jsonl':
            if self.pretty_print:
                # Track that we're overriding user configuration for traceability
                self._config_overrides['pretty_print_forced'] = True
            # Automatically disable pretty_print for JSON Lines format
            self.pretty_print = False
        
        # GRC Platform Integration
        self.compliance_schema = config.get("compliance_schema", "standard")
        self.include_risk_metadata = config.get("include_risk_metadata", True)
        self.api_compatible = config.get("api_compatible", True)
        self.timestamp_format = config.get("timestamp_format", "iso8601")
        
        # Security configuration for request body logging
        self.redact_request_fields = config.get("redact_request_fields", 
                                              ["password", "token", "secret", "key", "auth", "authorization"])
        
        # Precompute lowercase set for efficient case-insensitive lookup
        self._redact_field_set = {field.lower() for field in self.redact_request_fields}
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate JSON configuration."""
        if self.compliance_schema not in ["standard", "grc_standard", "financial_services"]:
            raise ValueError(f"Invalid compliance_schema '{self.compliance_schema}'. Must be one of: standard, grc_standard, financial_services")
        
        if self.timestamp_format not in ["iso8601", "unix_timestamp"]:
            raise ValueError(f"Invalid timestamp_format '{self.timestamp_format}'. Must be one of: iso8601, unix_timestamp")
        
        if not isinstance(self.include_request_body, bool):
            raise ValueError("include_request_body must be a boolean")
        
        if not isinstance(self.pretty_print, bool):
            raise ValueError("pretty_print must be a boolean")
        
        if not isinstance(self.include_risk_metadata, bool):
            raise ValueError("include_risk_metadata must be a boolean")
        
        if not isinstance(self.api_compatible, bool):
            raise ValueError("api_compatible must be a boolean")
        
        if not isinstance(self.redact_request_fields, list):
            raise ValueError("redact_request_fields must be a list")
    
    def _redact_sensitive_fields(self, data: Any) -> Any:
        """Recursively redact sensitive fields from data structures.
        
        Args:
            data: Data structure to redact (dict, list, or primitive)
            
        Returns:
            Redacted copy of the data structure
        """
        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if key.lower() in self._redact_field_set:
                    redacted[key] = "[REDACTED]"
                else:
                    redacted[key] = self._redact_sensitive_fields(value)
            return redacted
        elif isinstance(data, list):
            return [self._redact_sensitive_fields(item) for item in data]
        else:
            return data
    
    def _get_error_details(self, response: MCPResponse) -> tuple[str, int, str]:
        """Extract and normalize error details from response.
        
        Args:
            response: MCP response that may contain error
            
        Returns:
            Tuple of (event_type, error_code, error_message)
        """
        if not (hasattr(response, 'error') and response.error):
            return "RESPONSE", 0, ""
        
        # Handle both dict and object-style errors
        if isinstance(response.error, dict):
            error_code = response.error.get('code', 0)
            error_message = response.error.get('message', '')
        else:
            error_code = getattr(response.error, 'code', 0)
            error_message = getattr(response.error, 'message', '')
        
        # Ensure error_code is an integer, default to 0 if None or invalid type
        if not isinstance(error_code, int):
            error_code = 0
        
        # Classify error type based on JSON-RPC spec
        # Server errors: -32000 to -32099
        # Protocol/client errors: other negative codes
        if -32099 <= error_code <= -32000:
            event_type = "UPSTREAM_ERROR"
        else:
            event_type = "ERROR"
        
        return event_type, error_code, error_message
    
    def _format_request_log(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> str:
        """Format a request log message in JSON format.
        
        Args:
            request: The MCP request
            decision: Policy decision
            server_name: Name of the target server
            
        Returns:
            str: JSON-formatted log message
        """
        # Clear timestamp cache for this new log event
        self._clear_event_timestamp_cache()
        # Determine event type
        if not decision.allowed:
            event_type = "SECURITY_BLOCK"
        elif decision.metadata.get("filtered_count", 0) > 0:
            event_type = "TOOLS_FILTERED"
        else:
            event_type = "REQUEST"
        
        # Build base log data
        log_data = {
            "timestamp": self._format_timestamp(),
            "event_type": event_type,
            "method": request.method,
            "request_id": request.id,
            "status": "ALLOWED" if decision.allowed else "BLOCKED",  # Legacy field
            "decision_status": "allowed" if decision.allowed else "blocked"  # Normalized field
        }
        
        # Add tool name for tools/call requests
        if request.method == "tools/call":
            if request.params and "name" in request.params:
                log_data["tool"] = request.params["name"]
            elif event_type == "SECURITY_BLOCK":
                # For security blocks, always include a tool name (even if unknown)
                log_data["tool"] = "unknown"
        
        # Add plugin information
        plugin_info = self._extract_plugin_info(decision)
        if plugin_info != "unknown":
            log_data["plugin"] = plugin_info
        
        # Add decision reason
        if decision.reason:
            log_data["reason"] = decision.reason
        
        # Add server name
        log_data["server_name"] = server_name
        
        # Add request body if configured (with sensitive field redaction)
        if self.include_request_body and request.params:
            log_data["request_body"] = self._redact_sensitive_fields(request.params)
        
        # Add compliance metadata if enabled
        if self.include_risk_metadata:
            log_data["compliance_metadata"] = self._generate_compliance_metadata(request, decision, event_type)
        
        # Add metadata from decision (excluding plugin to avoid duplication)
        if decision.metadata:
            filtered_metadata = {k: v for k, v in decision.metadata.items() if k != "plugin"}
            if filtered_metadata:
                log_data["plugin_metadata"] = filtered_metadata
        
        # Add configuration override information for traceability
        if hasattr(self, '_config_overrides') and self._config_overrides:
            log_data["config_overrides"] = self._config_overrides
        
        return self._format_json_output(log_data)
    
    def _format_response_log(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> str:
        """Format a response log message in JSON format.
        
        Args:
            request: The original MCP request
            response: The MCP response
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: JSON-formatted log message
        """
        # Clear timestamp cache for this new log event
        self._clear_event_timestamp_cache()
        # Determine event type using unified error helper
        if not decision.allowed:
            event_type = "SECURITY_BLOCK"
            error_code, error_message = 0, ""
        elif getattr(decision, 'modified_content', None) is not None:
            event_type = "REDACTION"
            error_code, error_message = 0, ""
        else:
            # Use helper to extract and classify errors
            event_type, error_code, error_message = self._get_error_details(response)
        
        # Build base log data
        log_data = {
            "timestamp": self._format_timestamp(),
            "event_type": event_type,
            "request_id": response.id,
            "method": request.method  # Add method from original request for correlation
        }
        
        # Add tool name from original request if it was a tools/call
        if request.method == "tools/call" and request.params and "name" in request.params:
            log_data["tool"] = request.params["name"]
        
        # Set status based on event type
        if event_type == "RESPONSE":
            log_data["status"] = "success"  # Legacy field
            log_data["decision_status"] = "success"  # Normalized field
        elif "ERROR" in event_type:
            log_data["status"] = "error"  # Legacy field  
            log_data["decision_status"] = "error"  # Normalized field
        elif event_type == "SECURITY_BLOCK":
            log_data["status"] = "blocked"  # Legacy field
            log_data["decision_status"] = "blocked"  # Normalized field
        else:
            log_data["status"] = "modified"  # Legacy field
            log_data["decision_status"] = "modified"  # Normalized field
        
        # Add error details if present (from unified error helper)
        if error_code != 0:
            log_data["error_code"] = error_code
            log_data["error_message"] = error_message
        
        # Add plugin information
        plugin_info = self._extract_plugin_info(decision)
        if plugin_info != "unknown":
            log_data["plugin"] = plugin_info
        
        # Add decision reason
        if decision.reason:
            log_data["reason"] = decision.reason
        
        # Add server name
        log_data["server_name"] = server_name
        
        # Add duration if available
        if decision.metadata and "duration_ms" in decision.metadata:
            log_data["duration_ms"] = decision.metadata["duration_ms"]
        
        # Add compliance metadata if enabled
        if self.include_risk_metadata:
            log_data["compliance_metadata"] = self._generate_compliance_metadata(response, decision, event_type)
        
        # Add metadata from decision (excluding plugin and duration to avoid duplication)
        if decision.metadata:
            filtered_metadata = {k: v for k, v in decision.metadata.items() 
                               if k not in ["plugin", "duration_ms"]}
            if filtered_metadata:
                log_data["plugin_metadata"] = filtered_metadata
        
        return self._format_json_output(log_data)
    
    def _format_notification_log(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> str:
        """Format a notification log message in JSON format.
        
        Args:
            notification: The MCP notification
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: JSON-formatted log message
        """
        # Clear timestamp cache for this new log event
        self._clear_event_timestamp_cache()
        event_type = "NOTIFICATION"
        
        # Build base log data
        log_data = {
            "timestamp": self._format_timestamp(),
            "event_type": event_type,
            "method": notification.method,
            "status": "notification",  # Legacy field
            "decision_status": "notification"  # Normalized field
        }
        
        # Add plugin information
        plugin_info = self._extract_plugin_info(decision)
        if plugin_info != "unknown":
            log_data["plugin"] = plugin_info
        
        # Add decision reason
        if decision.reason:
            log_data["reason"] = decision.reason
        
        # Add server name
        log_data["server_name"] = server_name
        
        # Add compliance metadata if enabled
        if self.include_risk_metadata:
            log_data["compliance_metadata"] = self._generate_compliance_metadata(notification, decision, event_type)
        
        # Add metadata from decision (excluding plugin to avoid duplication)
        if decision.metadata:
            filtered_metadata = {k: v for k, v in decision.metadata.items() if k != "plugin"}
            if filtered_metadata:
                log_data["plugin_metadata"] = filtered_metadata
        
        # Add configuration override information for traceability
        if hasattr(self, '_config_overrides') and self._config_overrides:
            log_data["config_overrides"] = self._config_overrides
        
        return self._format_json_output(log_data)
    
    def _get_event_timestamp(self) -> Union[int, str]:
        """Get cached timestamp for this log event to ensure consistency.
        
        This prevents timestamp drift between multiple timestamp fields
        (e.g., timestamp and audit_timestamp) within the same log entry.
        """
        if not hasattr(self, '_current_event_timestamp'):
            now = datetime.now(timezone.utc)
            if self.timestamp_format == "unix_timestamp":
                self._current_event_timestamp = int(now.timestamp())
            else:
                self._current_event_timestamp = now.isoformat()
        return self._current_event_timestamp
    
    def _clear_event_timestamp_cache(self):
        """Clear cached timestamp (called at start of each log operation)."""
        if hasattr(self, '_current_event_timestamp'):
            delattr(self, '_current_event_timestamp')
    
    def _format_timestamp(self) -> Union[int, str]:
        """Format timestamp according to configuration (uses cached timestamp)."""
        return self._get_event_timestamp()
    
    def _generate_compliance_metadata(self, message: Any, decision: PolicyDecision, event_type: str) -> Dict[str, Any]:
        """Generate compliance metadata for the event.
        
        Args:
            message: MCP message
            decision: Policy decision
            event_type: Type of event
            
        Returns:
            Dict[str, Any]: Compliance metadata
        """
        # Use cached timestamp if available, otherwise generate new one
        if hasattr(self, '_current_event_timestamp'):
            audit_timestamp = self._current_event_timestamp
        else:
            # Fallback for cases where this is called outside log formatting
            if self.timestamp_format == "unix_timestamp":
                audit_timestamp = int(datetime.now(timezone.utc).timestamp())
            else:
                audit_timestamp = datetime.now(timezone.utc).isoformat()
        
        metadata = {
            "compliance_schema": self.compliance_schema,
            "audit_timestamp": audit_timestamp,
            "event_classification": self._classify_event(event_type),
            "risk_level": self._assess_risk_level(event_type),
        }
        
        if self.compliance_schema == "grc_standard":
            metadata.update({
                "governance_category": self._get_governance_category(message, event_type),
                "risk_category": self._get_risk_category(event_type),
                "compliance_framework": "INTERNAL_GRC"
            })
        
        elif self.compliance_schema == "financial_services":
            metadata.update({
                "sox_control_objective": self._get_sox_control_objective(event_type),
                "regulatory_framework": REGULATORY_FRAMEWORKS["financial_services"],
                "control_effectiveness": self._assess_control_effectiveness(decision),
                "audit_trail_id": self._generate_audit_trail_id(),
                "evidence_type": self._get_evidence_type(message, event_type)
            })
        
        # Add API-compatible fields if enabled
        if self.api_compatible:
            metadata["api_version"] = API_VERSION
            metadata["schema_version"] = SCHEMA_VERSION
            metadata["data_format"] = "json_lines" if not self.pretty_print else "json_pretty"
        
        return metadata
    
    def _classify_event(self, event_type: str) -> str:
        """Classify event for compliance purposes."""
        security_events = ["SECURITY_BLOCK", "REDACTION", "TOOLS_FILTERED"]
        error_events = ["ERROR", "UPSTREAM_ERROR"]
        
        if event_type in security_events:
            return "SECURITY_EVENT"
        elif event_type in error_events:
            return "ERROR_EVENT"
        else:
            return "OPERATIONAL_EVENT"
    
    def _assess_risk_level(self, event_type: str) -> str:
        """Assess risk level based on event type."""
        risk_levels = {
            "SECURITY_BLOCK": "HIGH",
            "REDACTION": "MEDIUM",
            "TOOLS_FILTERED": "LOW",
            "ERROR": "MEDIUM",
            "UPSTREAM_ERROR": "LOW",
            "REQUEST": "LOW",
            "RESPONSE": "LOW",
            "NOTIFICATION": "LOW"
        }
        return risk_levels.get(event_type, "LOW")
    
    def _get_governance_category(self, message: Any, event_type: str) -> str:
        """Get governance category for GRC systems."""
        if isinstance(message, MCPRequest) and message.method == "tools/call":
            return "TOOL_GOVERNANCE"
        elif event_type in ["SECURITY_BLOCK", "REDACTION"]:
            return "SECURITY_GOVERNANCE"
        else:
            return "OPERATIONAL_GOVERNANCE"
    
    def _get_risk_category(self, event_type: str) -> str:
        """Get risk category for GRC systems."""
        if event_type in ["SECURITY_BLOCK", "REDACTION"]:
            return "SECURITY_RISK"
        elif event_type in ["ERROR", "UPSTREAM_ERROR"]:
            return "OPERATIONAL_RISK"
        else:
            return "MINIMAL_RISK"
    
    def _get_sox_control_objective(self, event_type: str) -> str:
        """Get SOX control objective for financial services."""
        control_objectives = {
            "SECURITY_BLOCK": "AC-3.1 Access Enforcement",
            "REDACTION": "SC-4.1 Information in Shared Resources",
            "TOOLS_FILTERED": "AC-3.4 Discretionary Access Control",
            "ERROR": "SI-11.1 Error Handling",
            "REQUEST": "AU-12.1 Audit Generation",
            "RESPONSE": "AU-12.1 Audit Generation",
            "NOTIFICATION": "AU-12.1 Audit Generation"
        }
        return control_objectives.get(event_type, "AU-12.1 Audit Generation")
    
    def _assess_control_effectiveness(self, decision: PolicyDecision) -> str:
        """Assess control effectiveness based on decision."""
        if not decision.allowed:
            return "EFFECTIVE"  # Control blocked unwanted action
        elif getattr(decision, 'modified_content', None) is not None:
            return "PARTIALLY_EFFECTIVE"  # Control modified content
        else:
            return "NOT_APPLICABLE"  # No control action needed
    
    def _generate_audit_trail_id(self) -> str:
        """Generate unique audit trail ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[:-3]
        return f"AG-JSON-{timestamp}"
    
    def _get_evidence_type(self, message: Any, event_type: str) -> str:
        """Get evidence type for audit purposes."""
        if isinstance(message, MCPRequest):
            if message.method == "tools/call":
                return "TOOL_EXECUTION_EVIDENCE"
            else:
                return "API_REQUEST_EVIDENCE"
        elif isinstance(message, MCPResponse):
            return "API_RESPONSE_EVIDENCE"
        elif isinstance(message, MCPNotification):
            return "SYSTEM_NOTIFICATION_EVIDENCE"
        else:
            return "UNKNOWN_EVIDENCE"
    
    def _format_json_output(self, log_data: Dict[str, Any]) -> str:
        """Format log data as JSON output.
        
        Args:
            log_data: Log data dictionary
            
        Returns:
            str: JSON-formatted string
            
        Raises:
            TypeError: If the data cannot be serialized to JSON
        """
        try:
            result = json.dumps(
                log_data, 
                ensure_ascii=False,
                indent=2 if self.pretty_print else None,
                separators=(',', ': ') if self.pretty_print else (',', ':')
            )
            # Always add newline for proper log framing (both compact and pretty modes)
            result += '\n'
            return result
        except (TypeError, ValueError) as e:
            # If serialization fails, try to create a safe version
            safe_log_data = {
                "error": "JSON serialization failed",
                "error_details": str(e),
                "timestamp": self._get_event_timestamp(),
                "event_type": log_data.get("event_type", "UNKNOWN")
            }
            # Add safe fields that we know can be serialized
            for key in ["request_id", "method", "status", "decision_status", "server_name"]:
                if key in log_data and isinstance(log_data[key], (str, int, float, bool, type(None))):
                    safe_log_data[key] = log_data[key]
            
            result = json.dumps(
                safe_log_data,
                ensure_ascii=False,
                indent=2 if self.pretty_print else None,
                separators=(',', ': ') if self.pretty_print else (',', ':')
            )
            # Always add newline for proper log framing (both compact and pretty modes)
            result += '\n'
            return result


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "json_auditing": JsonAuditingPlugin
}