"""Operational auditing plugins for Watchgate MCP gateway.

This module provides operational auditing plugins for human-readable log formats
used by operations teams for monitoring and troubleshooting.
"""

import json
import re
from typing import Dict, Any, Optional, Union
from datetime import datetime
from watchgate.plugins.auditing.base import BaseAuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision


class LineAuditingPlugin(BaseAuditingPlugin):
    """Line format auditing plugin for operational monitoring.
    
    Logs MCP requests and responses in single-line human-readable format
    for operational monitoring and quick visual inspection by ops teams.
    
    Features:
    - Single line per event for easy scanning
    - Human-readable timestamps and status
    - Concise tool and method information
    - Quick visual identification of issues
    """
    
    # No additional attributes beyond base class
    
    def _format_request_log(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> str:
        """Format a request log message in line format.
        
        Args:
            request: The MCP request
            decision: Policy decision
            server_name: Name of the target server
            
        Returns:
            str: Line-formatted log message
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        plugin_info = self._sanitize_user_string(self._extract_plugin_info(decision))
        
        # Validate request has required attributes
        if not hasattr(request, 'method') or request.method is None:
            return f"{timestamp} - REQUEST: [invalid request - missing method] - {self._sanitize_user_string(server_name)}"
        
        if request.method == "tools/call" and request.params and "name" in request.params:
            tool_name = self._sanitize_user_string(request.params["name"])
            if not decision.allowed:
                return f"{timestamp} - SECURITY_BLOCK: {tool_name} - [{plugin_info}] {self._sanitize_reason(decision.reason)} - {self._sanitize_user_string(server_name)}"
            elif decision.modified_content is not None:
                modification_type = self._get_modification_type(decision)
                return f"{timestamp} - {modification_type}: {self._sanitize_user_string(request.method)} - {tool_name} - [{plugin_info}] {self._sanitize_reason(decision.reason)} - {self._sanitize_user_string(server_name)}"
            else:
                return f"{timestamp} - REQUEST: {self._sanitize_user_string(request.method)} - {tool_name} - ALLOWED - {self._sanitize_user_string(server_name)}"
        else:
            if not decision.allowed:
                return f"{timestamp} - SECURITY_BLOCK: {self._sanitize_user_string(request.method)} - [{plugin_info}] {self._sanitize_reason(decision.reason)} - {self._sanitize_user_string(server_name)}"
            elif decision.modified_content is not None:
                modification_type = self._get_modification_type(decision)
                return f"{timestamp} - {modification_type}: {self._sanitize_user_string(request.method)} - [{plugin_info}] {self._sanitize_reason(decision.reason)} - {self._sanitize_user_string(server_name)}"
            elif decision.metadata and decision.metadata.get("filtered_count", 0) > 0:
                filtered_count = decision.metadata.get("filtered_count", 0)
                return f"{timestamp} - TOOLS_FILTERED: tools/list ({filtered_count} filtered) - [{plugin_info}] {self._sanitize_reason(decision.reason)} - {self._sanitize_user_string(server_name)}"
            else:
                return f"{timestamp} - REQUEST: {self._sanitize_user_string(request.method)} - ALLOWED - {self._sanitize_user_string(server_name)}"
    
    def _format_response_log(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> str:
        """Format a response log message in line format.
        
        Args:
            request: The original MCP request
            response: The MCP response
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Line-formatted log message
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        plugin_info = self._sanitize_user_string(self._extract_plugin_info(decision))
        
        if not decision.allowed:
            return f"{timestamp} - SECURITY_BLOCK: response - [{plugin_info}] {self._sanitize_reason(decision.reason)} - {self._sanitize_user_string(server_name)}"
        elif decision.modified_content is not None:
            modification_type = self._get_modification_type(decision)
            return f"{timestamp} - {modification_type}: response - [{plugin_info}] {self._sanitize_reason(decision.reason)} - {self._sanitize_user_string(server_name)}"
        elif hasattr(response, 'error') and response.error:
            error_code = response.error.get('code', 'unknown')
            error_msg = self._sanitize_reason(response.error.get('message', 'unknown'))
            return f"{timestamp} - RESPONSE: error {error_code} - {error_msg} - {self._sanitize_user_string(server_name)}"
        else:
            duration_info = ""
            if decision.metadata and "duration_ms" in decision.metadata:
                duration_s = decision.metadata["duration_ms"] / 1000
                duration_info = f" ({duration_s:.3f}s)"
            return f"{timestamp} - RESPONSE: success{duration_info} - {self._sanitize_user_string(server_name)}"
    
    def _format_notification_log(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> str:
        """Format a notification log message in line format.
        
        Args:
            notification: The MCP notification
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Line-formatted log message
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        plugin_info = self._sanitize_user_string(self._extract_plugin_info(decision))
        sanitized_method = self._sanitize_user_string(notification.method)
        
        # Add plugin info and reason for parity with other log types
        base_msg = f"{timestamp} - NOTIFICATION: {sanitized_method}"
        if plugin_info != "unknown":
            base_msg += f" - [{plugin_info}]"  # plugin_info already sanitized above
        if decision.reason:
            base_msg += f" {self._sanitize_reason(decision.reason)}"
        base_msg += f" - {self._sanitize_user_string(server_name)}"
        return base_msg
    

class DebugAuditingPlugin(BaseAuditingPlugin):
    """Debug format auditing plugin for troubleshooting.
    
    Logs MCP requests and responses in detailed key-value format
    for troubleshooting and debugging purposes with maximum information.
    
    Features:
    - Detailed key-value pairs for all available data
    - Millisecond precision timestamps
    - Full parameter dumps for requests
    - Duration tracking with high precision
    - Plugin metadata inclusion
    """
    
    # No additional attributes beyond base class
    
    def _format_request_log(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> str:
        """Format a request log message in debug format.
        
        Args:
            request: The MCP request
            decision: Policy decision
            server_name: Name of the target server
            
        Returns:
            str: Debug-formatted log message
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds
        plugin_info = self._sanitize_user_string(self._extract_plugin_info(decision))
        
        # Determine event type
        if not decision.allowed:
            event_type = "SECURITY_BLOCK"
        elif decision.modified_content is not None:
            event_type = self._get_modification_type(decision)
        elif decision.metadata and decision.metadata.get("filtered_count", 0) > 0:
            event_type = "TOOLS_FILTERED"
        else:
            event_type = "REQUEST"
        
        parts = [f"[{timestamp}]"]
        
        # Validate request attributes
        if hasattr(request, 'id') and request.id is not None:
            parts.append(f"REQUEST_ID={request.id}")
        else:
            parts.append("REQUEST_ID=none")
        
        parts.append(f"EVENT={event_type}")
        
        if hasattr(request, 'method') and request.method is not None:
            parts.append(f"METHOD={self._sanitize_user_string(request.method)}")
        else:
            parts.append("METHOD=unknown")
        
        if request.method == "tools/call" and request.params and "name" in request.params:
            parts.append(f"TOOL={self._sanitize_user_string(request.params['name'])}")
        
        if hasattr(request, 'params') and request.params:
            try:
                sanitized_params = self._sanitize_params(request.params)
                params_json = json.dumps(sanitized_params, ensure_ascii=False)
                escaped_params = self._sanitize_reason_for_kv(params_json)
                parts.append(f'PARAMS_JSON="{escaped_params}"')
            except (TypeError, ValueError):
                parts.append('PARAMS_JSON="[non-serializable]"')
        
        status = "ALLOWED" if decision.allowed else "BLOCKED"
        parts.append(f"STATUS={status}")
        
        if plugin_info != "unknown":
            parts.append(f"PLUGIN={self._sanitize_user_string(plugin_info)}")
        
        if decision.reason:
            sanitized_reason = self._sanitize_reason_for_kv(decision.reason)
            parts.append(f'REASON="{sanitized_reason}"')
        
        parts.append(f"SERVER={self._sanitize_user_string(server_name)}")
        
        # Add relevant metadata
        if decision.metadata:
            for key, value in decision.metadata.items():
                if key not in ["plugin"]:
                    if key == "mode":
                        parts.append(f"POLICY_MODE={value}")
                    elif key == "filtered_count":
                        parts.append(f"FILTERED_TOOLS={value}")
                    else:
                        # Prevent collisions by prefixing with META_
                        parts.append(f"META_{key}={value}")
        
        return " ".join(parts)
    
    def _format_response_log(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> str:
        """Format a response log message in debug format.
        
        Args:
            request: The original MCP request
            response: The MCP response
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Debug-formatted log message
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds
        plugin_info = self._sanitize_user_string(self._extract_plugin_info(decision))
        
        # Determine event type
        if not decision.allowed:
            event_type = "SECURITY_BLOCK"
        elif hasattr(response, 'error') and response.error:
            # JSON-RPC spec: -32000 to -32099 are reserved for server/upstream errors
            # Other error codes are parse/method/param errors or implementation-defined
            error_code = response.error.get('code', 0)
            event_type = "UPSTREAM_ERROR" if -32099 <= error_code <= -32000 else "ERROR"
        elif decision.modified_content is not None:
            event_type = self._get_modification_type(decision)
        else:
            event_type = "RESPONSE"
        
        parts = [f"[{timestamp}]"]
        
        # Validate response attributes
        if hasattr(response, 'id') and response.id is not None:
            parts.append(f"REQUEST_ID={response.id}")
        else:
            parts.append("REQUEST_ID=none")
        
        parts.append(f"EVENT={event_type}")
        
        if event_type == "RESPONSE":
            parts.append("STATUS=success")
        elif "ERROR" in event_type:
            parts.append("STATUS=error")
            if hasattr(response, 'error') and response.error:
                error_code = response.error.get('code', 'unknown')
                error_msg = response.error.get('message', 'unknown')
                parts.append(f"ERROR_CODE={error_code}")
                sanitized_error_msg = self._sanitize_reason_for_kv(error_msg)
                parts.append(f'ERROR_MESSAGE="{sanitized_error_msg}"')
        elif event_type == "SECURITY_BLOCK":
            parts.append("STATUS=blocked")
        elif event_type in ("REDACTION", "MODIFICATION"):
            parts.append("STATUS=modified")
        
        # Add duration if available
        if decision.metadata and "duration_ms" in decision.metadata:
            duration_ms = decision.metadata["duration_ms"]
            parts.append(f"DURATION={duration_ms/1000:.3f}s")
            parts.append(f"DURATION_MS={duration_ms}")
        
        if plugin_info != "unknown":
            parts.append(f"PLUGIN={self._sanitize_user_string(plugin_info)}")
        
        if decision.reason:
            sanitized_reason = self._sanitize_reason_for_kv(decision.reason)
            parts.append(f'REASON="{sanitized_reason}"')
        
        parts.append(f"SERVER={self._sanitize_user_string(server_name)}")
        
        # Add relevant metadata (excluding already processed items)
        if decision.metadata:
            for key, value in decision.metadata.items():
                if key not in ["plugin", "duration_ms"]:
                    if key == "mode":
                        parts.append(f"POLICY_MODE={value}")
                    else:
                        # Prevent collisions by prefixing with META_
                        parts.append(f"META_{key}={value}")
        
        return " ".join(parts)
    
    def _format_notification_log(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> str:
        """Format a notification log message in debug format.
        
        Args:
            notification: The MCP notification
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Debug-formatted log message
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds
        plugin_info = self._sanitize_user_string(self._extract_plugin_info(decision))
        
        parts = [f"[{timestamp}]"]
        parts.append(f"EVENT=NOTIFICATION")
        parts.append(f"METHOD={self._sanitize_user_string(notification.method)}")
        
        if hasattr(notification, 'params') and notification.params:
            try:
                sanitized_params = self._sanitize_params(notification.params)
                params_json = json.dumps(sanitized_params, ensure_ascii=False)
                escaped_params = self._sanitize_reason_for_kv(params_json)
                parts.append(f'PARAMS_JSON="{escaped_params}"')
            except (TypeError, ValueError):
                parts.append('PARAMS_JSON="[non-serializable]"')
        
        if plugin_info != "unknown":
            parts.append(f"PLUGIN={self._sanitize_user_string(plugin_info)}")
        
        if decision.reason:
            sanitized_reason = self._sanitize_reason_for_kv(decision.reason)
            parts.append(f'REASON="{sanitized_reason}"')
        
        parts.append(f"SERVER={self._sanitize_user_string(server_name)}")
        
        # Add relevant metadata
        if decision.metadata:
            for key, value in decision.metadata.items():
                if key not in ["plugin"]:
                    # Prevent collisions by prefixing with META_
                    parts.append(f"META_{key}={value}")
        
        return " ".join(parts)


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "line_auditing": LineAuditingPlugin,
    "debug_auditing": DebugAuditingPlugin
}