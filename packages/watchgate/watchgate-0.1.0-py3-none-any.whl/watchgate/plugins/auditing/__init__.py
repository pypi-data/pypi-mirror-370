"""Auditing plugins for Watchgate MCP gateway.

This package contains auditing plugins that log request and response
information for security monitoring, compliance, and debugging.

Format-specific plugins provide dedicated functionality for each log format:
- CefAuditingPlugin: CEF format for SIEM integration
- SyslogAuditingPlugin: Syslog with TLS transport for centralized logging
- CsvAuditingPlugin: CSV format for compliance reporting and analysis
- JsonAuditingPlugin: JSON format for modern platform integration
- LineAuditingPlugin: Human-readable format for operational monitoring
- DebugAuditingPlugin: Detailed format for troubleshooting
- OtelAuditingPlugin: OpenTelemetry format for observability correlation
"""

from .base import BaseAuditingPlugin
from .common_event_format import CefAuditingPlugin
from .syslog import SyslogAuditingPlugin
from .csv import CsvAuditingPlugin
from .json_lines import JsonAuditingPlugin
from .human_readable import LineAuditingPlugin, DebugAuditingPlugin
from .opentelemetry import OtelAuditingPlugin

__all__ = [
    'BaseAuditingPlugin',
    'CefAuditingPlugin',
    'SyslogAuditingPlugin', 
    'CsvAuditingPlugin',
    'JsonAuditingPlugin',
    'LineAuditingPlugin',
    'DebugAuditingPlugin',
    'OtelAuditingPlugin'
]
