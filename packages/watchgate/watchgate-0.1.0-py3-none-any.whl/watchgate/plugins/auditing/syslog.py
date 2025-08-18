"""Syslog auditing plugin for Watchgate MCP gateway.

This module provides the SyslogAuditingPlugin class that logs MCP requests and responses
in RFC 5424 or RFC 3164 syslog format with support for multiple transport methods
including TLS for secure network delivery and real-time compliance monitoring.
"""

import asyncio
import os
import socket
import ssl
from typing import Dict, Any, Union, Optional
from datetime import datetime, timezone
import re
from watchgate.plugins.auditing.base import BaseAuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision

# Precompiled regex patterns for performance
CONTROL_CHARS = re.compile(r'[\x00-\x1F\x7F]')
MULTIPLE_SPACES = re.compile(r' +')


class SyslogAuditingPlugin(BaseAuditingPlugin):
    """Syslog auditing plugin with TLS transport support.
    
    Logs MCP requests and responses in syslog format for centralized logging
    and SIEM integration. Supports both file-based logging and network transport
    with TLS encryption for secure real-time monitoring.
    
    Features:
    - RFC 5424 and RFC 3164 syslog format support
    - Multiple transport methods: file, UDP, TCP, TLS
    - TLS encryption with certificate verification
    - Real-time monitoring capabilities
    - Centralized logging system integration
    - Configurable facility and severity levels
    """
    
    # Type annotations for class attributes
    rfc_format: str
    facility: int
    hostname: str
    app_name: str
    process_id: str
    transport: str
    remote_host: Optional[str]
    remote_port: int
    tls_verify: bool
    tls_cert_file: Optional[str]
    tls_key_file: Optional[str]
    tls_ca_file: Optional[str]
    sd_field_max_length: int
    msg_max_length: int
    truncation_marker: str
    _ssl_context: Optional[ssl.SSLContext]
    _tls_warning_logged: bool
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Syslog auditing plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary with syslog-specific options:
                   - syslog_config: Dictionary containing:
                     - rfc_format: "5424" or "3164" (default: "5424")
                     - facility: Syslog facility code (default: 16 = local0)
                     - transport: "file", "udp", "tcp", "tls" (default: "file")
                       Note: Network transports (especially TLS) are experimental in v0.1.0
                     - remote_host: Remote syslog server hostname (required for network transports)
                     - remote_port: Remote syslog server port (default: 514 for UDP/TCP, 6514 for TLS)
                     - tls_verify: Verify TLS certificates (default: True)
                     - tls_cert_file: Path to client certificate file
                     - tls_key_file: Path to client key file
                     - tls_ca_file: Path to CA certificate file
                   Plus all BaseAuditingPlugin options (output_file, etc.)
                   
        Raises:
            ValueError: If configuration is invalid
            TypeError: If configuration has wrong types
        """
        # Initialize base class first
        super().__init__(config)
        
        # Syslog-specific configuration
        syslog_config = config.get("syslog_config", {})
        self.rfc_format = syslog_config.get("rfc_format", "5424")
        self.facility = syslog_config.get("facility", 16)  # local0
        self.hostname = socket.gethostname()
        self.app_name = "watchgate"
        self.process_id = str(os.getpid())
        
        # Transport configuration
        self.transport = syslog_config.get("transport", "file")
        self.remote_host = syslog_config.get("remote_host")
        self.remote_port = syslog_config.get("remote_port")
        
        # Set default port based on transport if not specified
        if self.remote_port is None:
            if self.transport == "tls":
                self.remote_port = 6514  # Standard TLS syslog port
            else:
                self.remote_port = 514   # Standard UDP/TCP syslog port
        
        # TLS configuration
        self.tls_verify = syslog_config.get("tls_verify", True)
        self.tls_cert_file = syslog_config.get("tls_cert_file")
        self.tls_key_file = syslog_config.get("tls_key_file")
        self.tls_ca_file = syslog_config.get("tls_ca_file")
        
        # Configurable length limits and truncation
        self.sd_field_max_length = syslog_config.get("sd_field_max_length", 256)
        self.msg_max_length = syslog_config.get("msg_max_length", 2048)
        self.truncation_marker = syslog_config.get("truncation_marker", "...")
        
        # Validate configuration
        self._validate_config()
        
        # Cache computed constants for performance
        self._cached_hostname = self.hostname
        self._cached_process_id = self.process_id
        
        # Initialize SSL context and warning tracking
        self._ssl_context = None
        self._tls_warning_logged = False
        if self.transport in ["udp", "tcp", "tls"]:
            self._setup_network_transport()
    
    def _validate_config(self):
        """Validate syslog configuration."""
        if self.rfc_format not in ["5424", "3164"]:
            raise ValueError(f"Invalid rfc_format '{self.rfc_format}'. Must be '5424' or '3164'")
        
        if not isinstance(self.facility, int) or self.facility < 0 or self.facility > 23:
            raise ValueError(f"Invalid facility {self.facility}. Must be between 0 and 23")
        
        if self.transport not in ["file", "udp", "tcp", "tls"]:
            raise ValueError(f"Invalid transport '{self.transport}'. Must be one of: file, udp, tcp, tls")
        
        if self.transport in ["udp", "tcp", "tls"] and not self.remote_host:
            raise ValueError(f"remote_host is required for transport '{self.transport}'")
        
        if not isinstance(self.remote_port, int) or self.remote_port <= 0 or self.remote_port > 65535:
            raise ValueError(f"Invalid remote_port {self.remote_port}. Must be between 1 and 65535")
        
        # Validate length limits with dynamic marker computation
        if not isinstance(self.sd_field_max_length, int) or self.sd_field_max_length <= len(self.truncation_marker):
            raise ValueError(f"sd_field_max_length must be integer > {len(self.truncation_marker)}")
        
        msg_marker_len = len(f" ({self.truncation_marker})")  # Match runtime marker format
        if not isinstance(self.msg_max_length, int) or self.msg_max_length <= msg_marker_len:
            raise ValueError(f"msg_max_length must be integer > {msg_marker_len}")
        
        # Validate TLS configuration
        if self.transport == "tls":
            if self.tls_cert_file and not isinstance(self.tls_cert_file, str):
                raise ValueError("tls_cert_file must be a string path")
            if self.tls_key_file and not isinstance(self.tls_key_file, str):
                raise ValueError("tls_key_file must be a string path")
            if self.tls_ca_file and not isinstance(self.tls_ca_file, str):
                raise ValueError("tls_ca_file must be a string path")
    
    def _setup_network_transport(self):
        """Set up network transport for syslog delivery.
        
        Note: Network transports (especially TLS) are experimental in v0.1.0
        and may have issues with connection pooling and retry logic.
        """
        if self.transport == "tls":
            # Set up SSL context for TLS transport
            self._ssl_context = ssl.create_default_context()
            
            if not self.tls_verify:
                # One-time warning to avoid log spam on frequent instantiation
                if not self._tls_warning_logged:
                    import logging
                    logger = logging.getLogger(f"watchgate.audit.{id(self)}")
                    logger.warning("TLS certificate verification is DISABLED for syslog transport - this reduces security")
                    self._tls_warning_logged = True
                self._ssl_context.check_hostname = False
                self._ssl_context.verify_mode = ssl.CERT_NONE
            
            if self.tls_cert_file and self.tls_key_file:
                self._ssl_context.load_cert_chain(self.tls_cert_file, self.tls_key_file)
            
            if self.tls_ca_file:
                self._ssl_context.load_verify_locations(self.tls_ca_file)
    
    async def _send_via_network(self, message: str):
        """Send syslog message via network transport.
        
        Args:
            message: Formatted syslog message to send
        """
        try:
            if self.transport == "udp":
                await self._send_udp(message)
            elif self.transport == "tcp":
                await self._send_tcp(message)
            elif self.transport == "tls":
                await self._send_tls(message)
        except Exception as e:
            # If network sending fails, fall back to base class file logging
            import logging
            logger = logging.getLogger(f"watchgate.audit.{id(self)}")
            logger.error(f"Failed to send syslog message via {self.transport}: {e}")
            
            if self.critical:
                raise RuntimeError(f"Critical syslog auditing plugin failed to send message: {e}")
            # For non-critical plugins, the message is already written to file by base class
    
    async def _send_udp(self, message: str):
        """Send syslog message via UDP."""
        # Create UDP socket and send asynchronously
        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setblocking(False)
            await loop.sock_sendto(sock, message.encode('utf-8'), (self.remote_host, self.remote_port))
        finally:
            sock.close()
    
    async def _send_tcp(self, message: str):
        """Send syslog message via TCP."""
        reader, writer = await asyncio.open_connection(self.remote_host, self.remote_port)
        try:
            # RFC 6587 - TCP transport with octet counting
            message_bytes = message.encode('utf-8')
            framed_message = f"{len(message_bytes)} ".encode('utf-8') + message_bytes
            writer.write(framed_message)
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _send_tls(self, message: str):
        """Send syslog message via TLS."""
        reader, writer = await asyncio.open_connection(
            self.remote_host, 
            self.remote_port, 
            ssl=self._ssl_context
        )
        try:
            # RFC 5425 - TLS transport with octet counting
            message_bytes = message.encode('utf-8')
            framed_message = f"{len(message_bytes)} ".encode('utf-8') + message_bytes
            writer.write(framed_message)
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()
    
    def _format_request_log(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> str:
        """Format a request log message in syslog format.
        
        Args:
            request: The MCP request
            decision: Policy decision
            server_name: Name of the target server
            
        Returns:
            str: Syslog-formatted log message
        """
        # Determine event type and severity
        if not decision.allowed:
            severity = 4  # Warning
            event_type = "SECURITY_BLOCK"
        elif decision.metadata.get("filtered_count", 0) > 0:
            severity = 5  # Notice
            event_type = "TOOLS_FILTERED"
        else:
            severity = 6  # Informational
            event_type = "REQUEST"
        
        # Build structured data
        structured_data = self._build_structured_data(request, decision, event_type, server_name)
        
        # Create message content
        message_content = f"Watchgate MCP {event_type}: {request.method}"
        if request.method == "tools/call" and request.params and "name" in request.params:
            message_content += f" - {request.params['name']}"
        
        if not decision.allowed:
            message_content += f" - BLOCKED: {decision.reason}"
        elif decision.reason:
            message_content += f" - {decision.reason}"
        
        # Sanitize message content
        message_content = self._sanitize_message_content(message_content)
        return self._format_syslog_message(severity, structured_data, message_content, event_type)
    
    def _format_response_log(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> str:
        """Format a response log message in syslog format.
        
        Args:
            request: The original MCP request
            response: The MCP response
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Syslog-formatted log message
        """
        # Determine event type and severity
        if not decision.allowed:
            severity = 4  # Warning
            event_type = "SECURITY_BLOCK"
        elif hasattr(response, 'error') and response.error:
            severity = 3  # Error
            # JSON-RPC reserved error range is -32000 to -32099
            error_code = response.error.get('code', 0)
            event_type = "UPSTREAM_ERROR" if -32099 <= error_code <= -32000 else "ERROR"
        elif decision.modified_content is not None:
            severity = 5  # Notice
            event_type = "REDACTION"
        else:
            severity = 6  # Informational
            event_type = "RESPONSE"
        
        # Build structured data
        structured_data = self._build_structured_data(response, decision, event_type, server_name)
        
        # Create message content
        message_content = f"Watchgate MCP {event_type}: response"
        if hasattr(response, 'error') and response.error:
            message_content += f" - ERROR: {response.error.get('message', 'Unknown error')}"
        elif decision.reason:
            message_content += f" - {decision.reason}"
        
        # Add duration if available
        if decision.metadata and "duration_ms" in decision.metadata:
            duration_s = decision.metadata["duration_ms"] / 1000
            message_content += f" (duration: {duration_s:.3f}s)"
        
        # Sanitize message content
        message_content = self._sanitize_message_content(message_content)
        return self._format_syslog_message(severity, structured_data, message_content, event_type)
    
    def _format_notification_log(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> str:
        """Format a notification log message in syslog format.
        
        Args:
            notification: The MCP notification
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Syslog-formatted log message
        """
        severity = 6  # Informational
        event_type = "NOTIFICATION"
        
        # Build structured data
        structured_data = self._build_structured_data(notification, decision, event_type, server_name)
        
        # Create message content
        message_content = f"Watchgate MCP {event_type}: {notification.method}"
        if decision.reason:
            message_content += f" - {decision.reason}"
        
        # Sanitize message content
        message_content = self._sanitize_message_content(message_content)
        return self._format_syslog_message(severity, structured_data, message_content, event_type)
    
    def _build_structured_data(self, message: Union[MCPRequest, MCPResponse, MCPNotification], 
                              decision: PolicyDecision, event_type: str, server_name: str) -> str:
        """Build RFC 5424 structured data section.
        
        Args:
            message: MCP message
            decision: Policy decision
            event_type: Type of event
            server_name: Name of the server
            
        Returns:
            str: Structured data section
        """
        if self.rfc_format != "5424":
            return ""  # RFC 3164 doesn't support structured data
        
        # Build structured data elements
        sd_elements = []
        
        # Watchgate enterprise ID and basic event data
        watchgate_data = [
            f'event_type="{self._escape_structured_data(event_type)}"',
            f'status="{self._escape_structured_data("ALLOWED" if decision.allowed else "BLOCKED")}"'
        ]
        
        if hasattr(message, 'method'):
            watchgate_data.append(f'method="{self._escape_structured_data(message.method)}"')
        
        if hasattr(message, 'id') and message.id:
            watchgate_data.append(f'request_id="{self._escape_structured_data(str(message.id))}"')
        
        if isinstance(message, MCPRequest) and message.method == "tools/call" and message.params and "name" in message.params:
            watchgate_data.append(f'tool="{self._escape_structured_data(message.params["name"])}"')
        
        if decision.reason:
            watchgate_data.append(f'reason="{self._escape_structured_data(decision.reason)}"')
        
        plugin_info = self._extract_plugin_info(decision)
        if plugin_info != "unknown":
            watchgate_data.append(f'plugin="{self._escape_structured_data(plugin_info)}"')
        
        watchgate_data.append(f'server="{self._escape_structured_data(server_name)}"')
        
        if decision.metadata and "duration_ms" in decision.metadata:
            watchgate_data.append(f'duration_ms="{decision.metadata["duration_ms"]}"')
        
        sd_elements.append(f"[watchgate@32473 {' '.join(watchgate_data)}]")
        
        return ''.join(sd_elements)
    
    def _escape_structured_data(self, value: str) -> str:
        """Escape structured data values according to RFC 5424 and sanitize control chars.
        
        Truncates individual structured data fields with plain marker (e.g., "...") 
        to maintain clean key=value format in structured data elements.
        
        Args:
            value: Value to escape
            
        Returns:
            str: Escaped and sanitized value
        """
        # First sanitize control characters, then escape RFC 5424 special chars
        sanitized = CONTROL_CHARS.sub(' ', value)
        # Collapse multiple spaces
        sanitized = MULTIPLE_SPACES.sub(' ', sanitized).strip()
        
        # Truncate individual field if too long
        if len(sanitized) > self.sd_field_max_length:
            truncate_at = self.sd_field_max_length - len(self.truncation_marker)
            if truncate_at > 0:  # Guard against negative truncation
                sanitized = sanitized[:truncate_at] + self.truncation_marker
            else:
                sanitized = self.truncation_marker[:self.sd_field_max_length]
        
        return sanitized.replace('\\', '\\\\').replace('"', '\\"').replace(']', '\\]')
    
    def _sanitize_message_content(self, content: str) -> str:
        """Sanitize message content by replacing control characters and enforcing size limits.
        
        Truncates message content with parenthetical marker (e.g., " (...)") 
        to clearly indicate truncation in the human-readable message portion.
        
        Args:
            content: Message content to sanitize
            
        Returns:
            str: Sanitized content with control characters replaced by spaces and size limited
        """
        # Replace newlines, tabs, and other control characters with spaces
        sanitized = CONTROL_CHARS.sub(' ', content)
        # Collapse multiple spaces
        sanitized = MULTIPLE_SPACES.sub(' ', sanitized).strip()
        
        # Truncate if too long, using harmonized truncation marker
        if len(sanitized) > self.msg_max_length:
            full_marker = f" ({self.truncation_marker})"
            truncate_at = self.msg_max_length - len(full_marker)
            if truncate_at > 0:  # Guard against negative truncation
                sanitized = sanitized[:truncate_at] + full_marker
            else:
                sanitized = full_marker[:self.msg_max_length]
            
        return sanitized
    
    def _format_syslog_message(self, severity: int, structured_data: str, message: str, event_type: str = None, timestamp: datetime = None) -> str:
        """Format complete syslog message.
        
        Args:
            severity: Syslog severity level (0-7)
            structured_data: RFC 5424 structured data (empty for RFC 3164)
            message: Log message content
            event_type: Event type for MSGID (RFC 5424 only)
            timestamp: Optional timestamp (computed if not provided)
            
        Returns:
            str: Complete syslog message
        """
        priority = self.facility * 8 + severity
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        if self.rfc_format == "5424":
            # RFC 5424 format - fix millisecond precision
            timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            # Use NIL value (-) when structured data is empty, use event_type as MSGID
            sd_part = structured_data if structured_data else "-"
            msgid = event_type if event_type else "-"  # Use event_type for MSGID when available
            header = f"<{priority}>1 {timestamp_str} {self._cached_hostname} {self.app_name} {self._cached_process_id} {msgid} {sd_part}"
            return f"{header} {message}"
        else:
            # RFC 3164 format (ensure day is space-padded, not zero-padded)
            timestamp_str = timestamp.strftime("%b %e %H:%M:%S").replace('  ', ' ')
            header = f"<{priority}>{timestamp_str} {self._cached_hostname} {self.app_name}[{self._cached_process_id}]:"
            return f"{header} {message}"
    
    # The following are stubs for a future network transport implementation
    # async def _safe_log_with_network(self, message: str):
    #     """Safely log message with network transport if configured."""
    #     # Always write to file first (via base class)
    #     self._safe_log(message)
        
    #     # Then send via network if configured
    #     if self.transport in ["udp", "tcp", "tls"]:
    #         try:
    #             await self._send_via_network(message)
    #         except Exception as e:
    #             # Network failure handled in _send_via_network
    #             pass
    
    # async def log_request(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> None:
    #     """Log an incoming request and its security decision."""
    #     # Store timestamp for duration calculation
    #     self._store_request_timestamp(request)
        
    #     # Format and log the request
    #     log_message = self._format_request_log(request, decision, server_name)
    #     await self._safe_log_with_network(log_message)
    
    # async def log_response(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> None:
    #     """Log a response to a request with the security decision."""
    #     # Calculate duration and add to metadata
    #     duration_ms = self._calculate_duration(request.id)
    #     enhanced_decision = self._enhance_decision_with_duration(decision, duration_ms)
        
    #     # Format and log the response
    #     log_message = self._format_response_log(request, response, enhanced_decision, server_name)
    #     await self._safe_log_with_network(log_message)
    
    # async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> None:
    #     """Log a notification message."""
    #     # Format and log the notification
    #     log_message = self._format_notification_log(notification, decision, server_name)
    #     await self._safe_log_with_network(log_message)




# Policy manifest for policy-based plugin discovery
POLICIES = {
    "syslog_auditing": SyslogAuditingPlugin
}