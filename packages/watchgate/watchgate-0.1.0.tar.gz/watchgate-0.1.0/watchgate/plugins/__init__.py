"""Plugin system for Watchgate MCP gateway."""

from .interfaces import SecurityPlugin, AuditingPlugin, PluginInterface, PolicyDecision
from .manager import PluginManager

__all__ = ["SecurityPlugin", "AuditingPlugin", "PluginInterface", "PolicyDecision", "PluginManager"]
