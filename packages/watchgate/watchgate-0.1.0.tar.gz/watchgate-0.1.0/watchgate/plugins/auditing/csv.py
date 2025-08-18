"""CSV auditing plugin for Watchgate MCP gateway.

This module provides the CsvAuditingPlugin class that logs MCP requests and responses
in CSV format for compliance reporting and regulatory analysis, supporting
bulk evidence collection and audit trail requirements.
"""

import csv
import io
import json
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from watchgate.plugins.auditing.base import BaseAuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision


class CsvAuditingPlugin(BaseAuditingPlugin):
    """CSV auditing plugin for compliance reporting.
    
    Logs MCP requests and responses in CSV format for compliance reporting
    and regulatory analysis. Provides Excel-compatible format for compliance
    teams and supports bulk evidence collection for audit purposes.
    
    Features:
    - Bulk evidence collection for compliance frameworks
    - Excel-compatible CSV format
    - Configurable delimiters and quote styles
    - Header management with compliance columns
    - Regulatory schema support
    - Audit trail formatting for external auditors
    """
    
    # Type annotations for class attributes
    delimiter: str
    quote_char: str
    quote_style: str
    escape_char: str
    null_value: str
    include_compliance_columns: bool
    audit_trail_format: str
    regulatory_schema: str
    header_written: bool
    csv_quote_style: int
    field_order: List[str]
    _header_lock: threading.Lock
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize CSV auditing plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary with CSV-specific options:
                   - csv_config: Dictionary containing:
                     - delimiter: CSV field delimiter (default: ",")
                     - quote_char: Quote character (default: '"')
                     - quote_style: "minimal", "all", "nonnumeric", "none" (default: "minimal")
                     - null_value: Value for null fields (default: "")
                     - include_compliance_columns: Include compliance metadata (default: True)
                     - audit_trail_format: "SOX_404", "GDPR", "standard" (default: "standard")
                     - regulatory_schema: "financial_services", "default" (default: "default")
                   Plus all BaseAuditingPlugin options (output_file, etc.)
                   
        Raises:
            ValueError: If configuration is invalid
            TypeError: If configuration has wrong types
        """
        # CSV format requires newlines for structure - preserve them during sanitization
        config = config.copy()
        config['preserve_formatting_newlines'] = True
        
        # Initialize base class first
        super().__init__(config)
        
        # CSV-specific configuration
        csv_config = config.get("csv_config", {})
        self.delimiter = csv_config.get("delimiter", ",")
        self.quote_char = csv_config.get("quote_char", '"')
        self.quote_style = csv_config.get("quote_style", "minimal")
        self.escape_char = csv_config.get("escape_char", "\\")
        self.null_value = csv_config.get("null_value", "")
        
        # Compliance Extensions
        self.include_compliance_columns = csv_config.get("include_compliance_columns", True)
        self.audit_trail_format = csv_config.get("audit_trail_format", "standard")
        self.regulatory_schema = csv_config.get("regulatory_schema", "default")
        
        # Header management
        self.header_written = False
        self._header_lock = threading.Lock()
        
        # Validate configuration
        self._validate_config()
        
        # Set up CSV configuration
        self.csv_quote_style = self._get_csv_quote_style()
        self.field_order = self._get_field_order()
    
    def _validate_config(self):
        """Validate CSV configuration."""
        if not isinstance(self.delimiter, str) or len(self.delimiter) != 1:
            raise ValueError("delimiter must be a single character")
        
        if not isinstance(self.quote_char, str) or len(self.quote_char) != 1:
            raise ValueError("quote_char must be a single character")
        
        if self.quote_style not in ["minimal", "all", "nonnumeric", "none"]:
            raise ValueError(f"Invalid quote_style '{self.quote_style}'. Must be one of: minimal, all, nonnumeric, none")
        
        if self.audit_trail_format not in ["SOX_404", "GDPR", "standard"]:
            raise ValueError(f"Invalid audit_trail_format '{self.audit_trail_format}'. Must be one of: SOX_404, GDPR, standard")
        
        if self.regulatory_schema not in ["financial_services", "default"]:
            raise ValueError(f"Invalid regulatory_schema '{self.regulatory_schema}'. Must be one of: financial_services, default")
    
    def _get_csv_quote_style(self) -> int:
        """Get CSV quote style constant from configuration."""
        quote_style_map = {
            'minimal': csv.QUOTE_MINIMAL,
            'all': csv.QUOTE_ALL,
            'nonnumeric': csv.QUOTE_NONNUMERIC,
            'none': csv.QUOTE_NONE
        }
        return quote_style_map[self.quote_style]
    
    def _get_field_order(self) -> List[str]:
        """Get field order based on regulatory schema."""
        base_fields = [
            'timestamp', 'event_type', 'method', 'tool', 'status',
            'request_id', 'plugin', 'reason', 'duration_ms', 'server_name'
        ]
        
        if self.include_compliance_columns:
            if self.regulatory_schema == "financial_services":
                # Financial services compliance fields
                compliance_fields = [
                    'compliance_framework', 'risk_score', 'control_objective',
                    'audit_trail_id', 'regulatory_status', 'evidence_type'
                ]
            else:
                # Default compliance fields
                compliance_fields = [
                    'compliance_framework', 'audit_trail_id'
                ]
            base_fields.extend(compliance_fields)
        
        return base_fields
    
    def _format_request_log(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> str:
        """Format a request log message in CSV format.
        
        Args:
            request: The MCP request
            decision: Policy decision
            server_name: Name of the target server
            
        Returns:
            str: CSV-formatted log message
        """
        # Determine event type
        if not decision.allowed:
            event_type = "SECURITY_BLOCK"
        elif decision.metadata and decision.metadata.get("filtered_count", 0) > 0:
            event_type = "TOOLS_FILTERED"
        elif decision.modified_content is not None:
            event_type = "REQUEST_MODIFIED"
        else:
            event_type = "REQUEST"
        
        # Build CSV row data
        csv_row = self._build_csv_row(request, None, decision, event_type, server_name)
        
        # Format CSV message with header if needed
        return self._format_csv_message(csv_row)
    
    def _format_response_log(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> str:
        """Format a response log message in CSV format.
        
        Args:
            request: The original MCP request
            response: The MCP response
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: CSV-formatted log message
        """
        # Determine event type
        if not decision.allowed:
            event_type = "SECURITY_BLOCK"
        elif hasattr(response, 'error') and response.error:
            event_type = "UPSTREAM_ERROR" if response.error.get('code', 0) < -32000 else "ERROR"
        elif decision.modified_content is not None:
            event_type = "REDACTION"
        else:
            event_type = "RESPONSE"
        
        # Build CSV row data - pass response as the main message for response logs
        csv_row = self._build_csv_row(response, request, decision, event_type, server_name)
        
        # Format CSV message
        return self._format_csv_message(csv_row)
    
    def _format_notification_log(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> str:
        """Format a notification log message in CSV format.
        
        Args:
            notification: The MCP notification
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: CSV-formatted log message
        """
        event_type = "NOTIFICATION"
        
        # Build CSV row data
        csv_row = self._build_csv_row(notification, None, decision, event_type, server_name)
        
        # Format CSV message
        return self._format_csv_message(csv_row)
    
    def _build_csv_row(self, message: any, context_message: Optional[Any], decision: PolicyDecision, 
                      event_type: str, server_name: str) -> Dict[str, str]:
        """Build CSV row data from message and decision.
        
        Args:
            message: MCP message (request, response, or notification)
            context_message: Optional context message (e.g., original request for responses)
            decision: Policy decision
            event_type: Type of event
            server_name: Name of the server
            
        Returns:
            Dict[str, str]: CSV row data
        """
        csv_row = {}
        
        # Common fields
        csv_row['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        csv_row['event_type'] = event_type
        csv_row['plugin'] = decision.metadata.get('plugin', '') if decision.metadata else ''
        csv_row['reason'] = self._format_csv_value(decision.reason)
        csv_row['server_name'] = server_name
        
        # Message-specific fields
        if isinstance(message, MCPRequest):
            csv_row['method'] = message.method
            csv_row['request_id'] = message.id or ''
            csv_row['tool'] = self._extract_tool_name(message)
            csv_row['status'] = self._get_request_status(decision)
            csv_row['duration_ms'] = '0'  # Not available for requests
            
        elif isinstance(message, MCPResponse):
            # Use context_message (original request) if available for better correlation
            if context_message and isinstance(context_message, MCPRequest):
                csv_row['method'] = context_message.method
                csv_row['tool'] = self._extract_tool_name(context_message)
            else:
                csv_row['method'] = ''  # Not available without context
                csv_row['tool'] = ''  # Not available without context
            csv_row['request_id'] = message.id or ''
            csv_row['status'] = self._get_response_status(event_type, message)
            csv_row['duration_ms'] = self._extract_duration(decision)
            
        elif isinstance(message, MCPNotification):
            csv_row['method'] = message.method
            csv_row['request_id'] = ''  # Notifications don't have request IDs
            csv_row['tool'] = ''  # Not applicable for notifications
            csv_row['status'] = 'ALLOWED' if decision.allowed else 'BLOCKED'
            csv_row['duration_ms'] = '0'  # Not applicable for notifications
            
            # Include key notification parameters in reason field for auditing
            if hasattr(message, 'params') and message.params:
                import json
                # Add notification params to reason for auditing purposes
                original_reason = csv_row.get('reason', decision.reason or '')
                params_str = json.dumps(message.params, separators=(',', ':'))
                if original_reason:
                    csv_row['reason'] = f"{original_reason} params={params_str}"
                else:
                    csv_row['reason'] = f"params={params_str}"
        
        # Add compliance fields if enabled
        if self.include_compliance_columns:
            csv_row.update(self._build_compliance_fields(message, decision, event_type))
        
        # Ensure all fields are present and formatted
        for field in self.field_order:
            if field not in csv_row:
                csv_row[field] = self.null_value
            else:
                csv_row[field] = self._format_csv_value(csv_row[field])
        
        return csv_row
    
    def _extract_tool_name(self, request: MCPRequest) -> str:
        """Extract tool name from MCP request."""
        if request.method == "tools/call" and request.params:
            # Get tool name from correct MCP spec field
            return request.params.get("name", "unknown")
        return ""
    
    def _get_request_status(self, decision: PolicyDecision) -> str:
        """Get request status from policy decision."""
        return "ALLOWED" if decision.allowed else "BLOCKED"
    
    def _get_response_status(self, event_type: str, response: MCPResponse) -> str:
        """Get response status from event type and response."""
        if "ERROR" in event_type:
            return "error"
        elif event_type == "RESPONSE":
            return "success"
        elif event_type == "SECURITY_BLOCK":
            return "blocked"
        elif event_type == "REDACTION":
            return "modified"
        else:
            return "unknown"
    
    def _extract_duration(self, decision: PolicyDecision) -> str:
        """Extract duration from policy decision metadata."""
        if decision.metadata and "duration_ms" in decision.metadata:
            return str(decision.metadata["duration_ms"])
        return "0"
    
    def _build_compliance_fields(self, message: any, decision: PolicyDecision, event_type: str) -> Dict[str, str]:
        """Build compliance-specific fields for the CSV row.
        
        Args:
            message: MCP message
            decision: Policy decision
            event_type: Type of event
            
        Returns:
            Dict[str, str]: Compliance fields
        """
        compliance_fields = {}
        
        # Base compliance fields
        compliance_fields['compliance_framework'] = self.audit_trail_format
        compliance_fields['audit_trail_id'] = self._generate_audit_trail_id()
        
        if self.regulatory_schema == "financial_services":
            # Financial services specific fields
            compliance_fields['risk_score'] = self._calculate_risk_score(event_type)
            compliance_fields['control_objective'] = self._get_control_objective(event_type)
            compliance_fields['regulatory_status'] = self._get_regulatory_status(decision)
            compliance_fields['evidence_type'] = self._get_evidence_type(message, event_type)
        
        return compliance_fields
    
    def _generate_audit_trail_id(self) -> str:
        """Generate unique audit trail ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:-3]
        return f"AG-{timestamp}"
    
    def _calculate_risk_score(self, event_type: str) -> str:
        """Calculate risk score based on event type."""
        risk_scores = {
            "SECURITY_BLOCK": "HIGH",
            "REDACTION": "MEDIUM",
            "REQUEST_MODIFIED": "MEDIUM",
            "TOOLS_FILTERED": "LOW",
            "ERROR": "MEDIUM",
            "UPSTREAM_ERROR": "LOW",
            "REQUEST": "LOW",
            "RESPONSE": "LOW",
            "NOTIFICATION": "LOW"
        }
        return risk_scores.get(event_type, "LOW")
    
    def _get_control_objective(self, event_type: str) -> str:
        """Get SOX control objective based on event type."""
        if self.audit_trail_format == "SOX_404":
            control_objectives = {
                "SECURITY_BLOCK": "AC-3.1 Access Enforcement",
                "REDACTION": "SC-4.1 Information in Shared Resources",
                "REQUEST_MODIFIED": "SC-4.1 Information in Shared Resources",
                "TOOLS_FILTERED": "AC-3.4 Discretionary Access Control",
                "ERROR": "SI-11.1 Error Handling",
                "REQUEST": "AU-12.1 Audit Generation",
                "RESPONSE": "AU-12.1 Audit Generation",
                "NOTIFICATION": "AU-12.1 Audit Generation"
            }
        else:
            control_objectives = {
                "SECURITY_BLOCK": "Access Control",
                "REDACTION": "Data Protection",
                "REQUEST_MODIFIED": "Data Protection",
                "TOOLS_FILTERED": "Authorization",
                "ERROR": "Error Handling",
                "REQUEST": "Audit Logging",
                "RESPONSE": "Audit Logging",
                "NOTIFICATION": "Audit Logging"
            }
        return control_objectives.get(event_type, "General")
    
    def _get_regulatory_status(self, decision: PolicyDecision) -> str:
        """Get regulatory compliance status."""
        if not decision.allowed:
            return "NON_COMPLIANT"
        elif decision.modified_content is not None:
            return "MODIFIED"
        else:
            return "COMPLIANT"
    
    def _get_evidence_type(self, message: any, event_type: str) -> str:
        """Get evidence type for audit purposes."""
        if isinstance(message, MCPRequest):
            if message.method == "tools/call":
                return "TOOL_EXECUTION"
            else:
                return "API_REQUEST"
        elif isinstance(message, MCPResponse):
            return "API_RESPONSE"
        elif isinstance(message, MCPNotification):
            return "SYSTEM_NOTIFICATION"
        else:
            return "UNKNOWN"
    
    def _format_csv_value(self, value: Any) -> str:
        """Format values for CSV output with injection protection.
        
        Args:
            value: Value to format
            
        Returns:
            str: Formatted value with CSV injection protection
        """
        if value is None:
            return self.null_value
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, dict):
            # Convert dict to JSON string for complex data
            json_str = json.dumps(value, separators=(',', ':'))
            # Truncate if too long for Excel (32767 char limit)
            if len(json_str) > 32000:
                json_str = json_str[:31997] + '...'
            return self._sanitize_csv_injection(json_str)
        elif isinstance(value, list):
            # Convert list to JSON string
            json_str = json.dumps(value, separators=(',', ':'))
            # Truncate if too long for Excel
            if len(json_str) > 32000:
                json_str = json_str[:31997] + '...'
            return self._sanitize_csv_injection(json_str)
        else:
            return self._sanitize_csv_injection(str(value))
    
    def _sanitize_csv_injection(self, value: str) -> str:
        """Sanitize values to prevent CSV injection attacks.
        
        Args:
            value: String value to sanitize
            
        Returns:
            str: Sanitized value safe from CSV injection
        """
        if not value:
            return value
        
        # Check if first character could trigger formula execution
        if value[0] in ('=', '+', '-', '@', '\t', '\r'):
            # Prefix with single quote to prevent formula execution
            return "'" + value
        
        return value
    
    def _check_header_needed(self) -> bool:
        """Check if header needs to be written (for file rotation support).
        
        Note: While thread-safe within a process, multiple processes writing
        to the same file may still experience header races. For multi-process
        deployments, consider using separate log files per process or a
        centralized logging service.
        
        Returns:
            bool: True if header should be written
        """
        # If we're writing to a file, check if it's empty or new
        if hasattr(self, 'output_file') and self.output_file:
            import os
            try:
                # Check if file exists and has content
                if os.path.exists(self.output_file):
                    file_size = os.path.getsize(self.output_file)
                    return file_size == 0
                else:
                    return True
            except:
                # If we can't check, assume header not needed
                return False
        
        # For non-file outputs, use the instance flag
        return not self.header_written
    
    def _format_csv_message(self, csv_row: Dict[str, str]) -> str:
        """Format CSV message with header if needed.
        
        Args:
            csv_row: CSV row data
            
        Returns:
            str: Formatted CSV message
        """
        output = io.StringIO()
        
        # Configure writer kwargs based on quote style
        writer_kwargs = {
            'fieldnames': self.field_order,
            'quoting': self.csv_quote_style,
            'delimiter': self.delimiter,
            'quotechar': self.quote_char,
            'lineterminator': '\n'
        }
        
        # Add escapechar if using QUOTE_NONE
        if self.csv_quote_style == csv.QUOTE_NONE:
            writer_kwargs['escapechar'] = self.escape_char
        
        writer = csv.DictWriter(output, **writer_kwargs)
        
        # Thread-safe header writing with file rotation support
        header_needed = False
        with self._header_lock:
            if self._check_header_needed():
                header_needed = True
                self.header_written = True
        
        # Write header if needed (outside lock to minimize critical section)
        if header_needed:
            writer.writeheader()
        
        # Write data row
        writer.writerow(csv_row)
        
        # Remove trailing newline since logging system will add it
        result = output.getvalue()
        if result.endswith('\n'):
            result = result[:-1]
        
        return result


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "csv_auditing": CsvAuditingPlugin
}