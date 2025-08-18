# Plugin UI Implementation Guide

**Decision**: Plugins provide their own Textual widgets directly for TUI configuration. No schema layers, no abstraction - maximum freedom for plugin authors.

## Philosophy

We refuse to be a middleman between plugin authors and the UI they want. If a plugin wants to appear in the TUI, they provide a Textual widget. If they don't, they don't appear. Simple.

Benefits:
- **Zero abstraction** - Plugin authors use Textual directly
- **Maximum flexibility** - Any Textual widget or custom composition
- **Single file approach** - UI code lives with plugin logic
- **No special treatment** - Built-in plugins follow same rules as user plugins
- **Minimal maintenance** - We just mount their widget

## The Contract

Plugins that want TUI support must implement one method:

```python
@classmethod
def get_config_widget(cls, current_config: dict, context: dict = None):
    """Return a Textual widget for configuration.
    
    Args:
        current_config: Current configuration dict for this plugin
        context: Optional context (server_name, available_tools, etc.)
        
    Returns:
        A Textual widget that implements get_config() method
        Or None if plugin doesn't support TUI configuration
    """
```

The returned widget MUST implement:
```python
def get_config(self) -> dict:
    """Extract configuration from widget state."""
```

That's it. No schemas, no field definitions, no validation rules. The plugin handles everything.

## Implementation Pattern

All plugins follow this pattern - UI code embedded directly in the plugin file:

```python
# Import Textual only when needed
try:
    from textual.app import ComposeResult
    from textual.containers import Container, Vertical, Horizontal
    from textual.widgets import Static, RadioSet, Checkbox
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

class MyPlugin(SecurityPlugin):
    """Main plugin implementation with all security logic."""
    
    def __init__(self, config):
        # ... existing plugin logic ...
    
    async def check_request(self, request, server_name):
        # ... existing security logic ...
    
    # ========== TUI Configuration Support ==========
    
    @classmethod
    def get_config_widget(cls, current_config: dict, context: dict = None):
        """Return widget for TUI configuration."""
        if not HAS_TEXTUAL:
            return None
        return cls.MyConfigWidget(current_config, context)
    
    # Define widget as inner class
    if HAS_TEXTUAL:
        class MyConfigWidget(Container):
            """TUI configuration widget."""
            
            def __init__(self, config: dict, context: dict = None):
                super().__init__()
                self.config = config or {}
                self.context = context or {}
            
            def compose(self) -> ComposeResult:
                """Plugin authors have complete control over layout."""
                # Use any Textual widgets, custom layouts, styling, etc.
                pass
            
            def get_config(self) -> dict:
                """Extract config from widget state."""
                # Plugin handles their own config extraction
                return {}
```

## Complete Examples

### Security Plugin: PII Filter

```python
# watchgate/plugins/security/pii.py
"""Basic PII Filter security plugin implementation."""

import logging
import re
from typing import Dict, Any
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Static, RadioSet, Checkbox, Collapsible
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

logger = logging.getLogger(__name__)

class BasicPIIFilterPlugin(SecurityPlugin):
    """Security plugin for PII content filtering."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration validation."""
        super().__init__(config)
        self.action = config["action"]
        self.pii_types = config.get("pii_types", {})
        # ... rest of existing implementation
    
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        """Check request for PII violations."""
        # ... existing security logic unchanged
        pass
    
    # ========== TUI Configuration Support ==========
    
    @classmethod
    def get_config_widget(cls, current_config: dict, context: dict = None):
        """Return Textual widget for TUI configuration."""
        if not HAS_TEXTUAL:
            return None
        return cls.PIIConfigWidget(current_config)
    
    if HAS_TEXTUAL:
        class PIIConfigWidget(Container):
            """TUI configuration widget for PII Filter."""
            
            def __init__(self, config: dict):
                super().__init__()
                self.config = config or {}
            
            def compose(self) -> ComposeResult:
                """Compose the widget UI - plugin authors control everything."""
                
                # Detection Action Section
                yield Static("Detection Action:", classes="section-label")
                yield RadioSet(
                    ("redact", "Redact - Replace detected PII with [REDACTED]"),
                    ("block", "Block - Reject requests containing PII"),
                    ("audit_only", "Audit Only - Log detections but don't modify"),
                    value=self.config.get("action", "redact"),
                    id="action_selector"
                )
                
                # PII Types Section - Organized in groups
                yield Static("PII Types to Detect:", classes="section-header")
                
                with Horizontal(classes="pii-type-groups"):
                    # Personal Information Column
                    with Vertical(classes="pii-group"):
                        yield Static("Personal Information", classes="group-header")
                        
                        pii_types = self.config.get("pii_types", {})
                        
                        yield Checkbox(
                            "Email Addresses",
                            value=pii_types.get("email", {}).get("enabled", True),
                            id="pii_email"
                        )
                        yield Checkbox(
                            "Phone Numbers", 
                            value=pii_types.get("phone", {}).get("enabled", True),
                            id="pii_phone"
                        )
                        yield Checkbox(
                            "Social Security Numbers",
                            value=pii_types.get("ssn", {}).get("enabled", True),
                            id="pii_ssn"
                        )
                        yield Checkbox(
                            "Passport Numbers",
                            value=pii_types.get("passport", {}).get("enabled", False),
                            id="pii_passport"
                        )
                    
                    # Financial Column
                    with Vertical(classes="pii-group"):
                        yield Static("Financial", classes="group-header")
                        
                        yield Checkbox(
                            "Credit Card Numbers",
                            value=pii_types.get("credit_card", {}).get("enabled", False),
                            id="pii_credit_card"
                        )
                        yield Checkbox(
                            "Bank Account Numbers",
                            value=pii_types.get("bank_account", {}).get("enabled", False),
                            id="pii_bank_account"
                        )
                        yield Checkbox(
                            "Routing Numbers",
                            value=pii_types.get("routing", {}).get("enabled", False),
                            id="pii_routing"
                        )
                        yield Checkbox(
                            "IBAN",
                            value=pii_types.get("iban", {}).get("enabled", False),
                            id="pii_iban"
                        )
                    
                    # Network & Technical Column
                    with Vertical(classes="pii-group"):
                        yield Static("Network & Technical", classes="group-header")
                        
                        yield Checkbox(
                            "IP Addresses (IPv4/IPv6)",
                            value=pii_types.get("ip_address", {}).get("enabled", False),
                            id="pii_ip_address"
                        )
                        yield Checkbox(
                            "MAC Addresses",
                            value=pii_types.get("mac_address", {}).get("enabled", False),
                            id="pii_mac_address"
                        )
                        yield Checkbox(
                            "URLs",
                            value=pii_types.get("urls", {}).get("enabled", False),
                            id="pii_urls"
                        )
                        yield Checkbox(
                            "Bitcoin Addresses",
                            value=pii_types.get("bitcoin", {}).get("enabled", False),
                            id="pii_bitcoin"
                        )
                
                # Regional Formats Section
                yield Static("Regional Formats:", classes="section-header")
                with Horizontal():
                    yield Checkbox(
                        "US Formats (SSN, Phone)",
                        value=True,  # Could be from config
                        id="format_us"
                    )
                    yield Checkbox(
                        "EU Formats (VAT, Phone)",
                        value=True,
                        id="format_eu"
                    )
                    yield Checkbox(
                        "UK Formats (NI, Postcode)",
                        value=False,
                        id="format_uk"
                    )
                
                # Advanced Options - Collapsible
                with Collapsible(title="Advanced Options", collapsed=True):
                    yield Checkbox(
                        "Scan Base64 Encoded Content",
                        value=self.config.get("scan_base64", False),
                        id="scan_base64"
                    )
                    yield Static("⚠️ May impact performance", classes="warning")
                    
                    yield Checkbox(
                        "Case Sensitive Matching",
                        value=self.config.get("case_sensitive", False),
                        id="case_sensitive"
                    )
                
                # Statistics Display (read-only)
                yield Static("Statistics: Redacted today: 156 items | Last triggered: 2 minutes ago", 
                           classes="stats")
            
            def get_config(self) -> dict:
                """Extract configuration from widget state."""
                # Get action
                action_widget = self.query_one("#action_selector", RadioSet)
                action = action_widget.pressed_button.value if action_widget.pressed_button else "redact"
                
                # Get PII type selections
                pii_types = {}
                pii_checkboxes = [
                    ("email", "#pii_email"),
                    ("phone", "#pii_phone"), 
                    ("ssn", "#pii_ssn"),
                    ("passport", "#pii_passport"),
                    ("credit_card", "#pii_credit_card"),
                    ("bank_account", "#pii_bank_account"),
                    ("routing", "#pii_routing"),
                    ("iban", "#pii_iban"),
                    ("ip_address", "#pii_ip_address"),
                    ("mac_address", "#pii_mac_address"),
                    ("urls", "#pii_urls"),
                    ("bitcoin", "#pii_bitcoin")
                ]
                
                for pii_type, selector in pii_checkboxes:
                    checkbox = self.query_one(selector, Checkbox)
                    pii_types[pii_type] = {"enabled": checkbox.value}
                
                # Get advanced options
                scan_base64 = self.query_one("#scan_base64", Checkbox).value
                case_sensitive = self.query_one("#case_sensitive", Checkbox).value
                
                return {
                    "action": action,
                    "pii_types": pii_types,
                    "scan_base64": scan_base64,
                    "case_sensitive": case_sensitive
                }

# Policy manifest unchanged
POLICIES = {
    "pii": BasicPIIFilterPlugin
}
```

### Server-Specific Plugin: Tool Allowlist

```python
# watchgate/plugins/security/tool_allowlist.py
"""Tool allowlist security plugin implementation."""

import logging
from typing import Dict, Any
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Vertical, ScrollableContainer
    from textual.widgets import Static, RadioSet, Checkbox, Collapsible
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

logger = logging.getLogger(__name__)

class ToolAllowlistPlugin(SecurityPlugin):
    """Security plugin that implements tool allowlist/blocklist functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration."""
        super().__init__(config)
        self.mode = config["mode"]
        self.tools_config = config.get("tools", {})
    
    async def check_request(self, request, server_name: str) -> PolicyDecision:
        """Check if tool request should be allowed."""
        # ... existing security logic unchanged
        pass
    
    # ========== TUI Configuration Support ==========
    
    @classmethod
    def get_config_widget(cls, current_config: dict, context: dict = None):
        """Return widget for TUI configuration."""
        if not HAS_TEXTUAL:
            return None
        
        # Extract context for server-specific configuration
        server_name = context.get("server_name", "unknown") if context else "unknown"
        available_tools = context.get("available_tools", []) if context else []
        
        return cls.ToolAllowlistWidget(current_config, server_name, available_tools)
    
    if HAS_TEXTUAL:
        class ToolAllowlistWidget(Container):
            """TUI configuration widget for Tool Allowlist."""
            
            # Define patterns for dangerous tools
            DANGEROUS_PATTERNS = [
                "delete", "remove", "execute", "exec", "run", "command", 
                "set_permission", "chmod", "kill", "terminate", "destroy"
            ]
            
            def __init__(self, config: dict, server_name: str, available_tools: list):
                super().__init__()
                self.config = config or {}
                self.server_name = server_name
                self.available_tools = available_tools
                
                # Dynamically group tools by category
                self.tool_groups = self._group_tools_by_category()
            
            def _group_tools_by_category(self) -> dict:
                """Dynamically group tools by their function."""
                groups = {
                    "File Operations": [],
                    "Directory Operations": [],
                    "System Operations": [],
                    "Information": [],
                    "Other": []
                }
                
                for tool in self.available_tools:
                    tool_lower = tool.lower()
                    
                    # Categorize by name patterns
                    if any(word in tool_lower for word in ["file", "read", "write", "content"]):
                        groups["File Operations"].append(tool)
                    elif any(word in tool_lower for word in ["dir", "directory", "folder", "list"]):
                        groups["Directory Operations"].append(tool)
                    elif any(word in tool_lower for word in ["exec", "command", "run", "system", "permission"]):
                        groups["System Operations"].append(tool)
                    elif any(word in tool_lower for word in ["get", "info", "stat", "check", "show"]):
                        groups["Information"].append(tool)
                    else:
                        groups["Other"].append(tool)
                
                # Remove empty groups
                return {name: tools for name, tools in groups.items() if tools}
            
            def _is_dangerous_tool(self, tool: str) -> bool:
                """Check if a tool is potentially dangerous."""
                tool_lower = tool.lower()
                return any(pattern in tool_lower for pattern in self.DANGEROUS_PATTERNS)
            
            def compose(self) -> ComposeResult:
                """Compose the widget UI."""
                
                yield Static(f"Tool Allowlist Configuration", classes="header")
                yield Static(f"Server: {self.server_name}", classes="server-info")
                
                # Access Control Mode
                yield Static("Access Control Mode:", classes="section-label")
                current_mode = self.config.get("mode", "allowlist")
                yield RadioSet(
                    ("allow_all", "Allow All - No restrictions"),
                    ("allowlist", "Allowlist - Only allow selected tools"),
                    ("blocklist", "Blocklist - Block selected tools"),
                    value=current_mode,
                    id="access_mode"
                )
                
                # Tool Selection - Only show if not allow_all
                if current_mode != "allow_all":
                    yield Static("Available Tools:", classes="section-header")
                    
                    # Get currently selected tools for this server
                    current_tools = self.config.get("tools", {}).get(self.server_name, [])
                    
                    with ScrollableContainer():
                        for group_name, tools in self.tool_groups.items():
                            # Count selected vs total in group
                            selected_count = sum(1 for tool in tools if tool in current_tools)
                            
                            with Collapsible(
                                title=f"{group_name} ({selected_count}/{len(tools)} selected)",
                                collapsed=False
                            ):
                                for tool in sorted(tools):
                                    # Create label with danger indicator
                                    label = tool
                                    classes = ""
                                    if self._is_dangerous_tool(tool):
                                        label = f"⚠️ {tool}"
                                        classes = "dangerous-tool"
                                    
                                    yield Checkbox(
                                        label,
                                        value=tool in current_tools,
                                        id=f"tool_{tool}",
                                        classes=classes
                                    )
                    
                    # Quick action buttons could be added here
                    yield Static(f"Summary: {len(current_tools)} of {len(self.available_tools)} tools selected")
                
                # Custom block message
                yield Static("Custom Block Message:", classes="section-label")
                current_message = self.config.get("block_message", "Tool access denied by security policy")
                # Note: TextArea would be better here but keeping it simple
                yield Static(f"Message: {current_message}", classes="config-display")
            
            def get_config(self) -> dict:
                """Extract configuration from widget state."""
                # Get access mode
                mode_widget = self.query_one("#access_mode", RadioSet)
                mode = mode_widget.pressed_button.value if mode_widget.pressed_button else "allowlist"
                
                config = {"mode": mode}
                
                # If not allow_all, collect selected tools
                if mode != "allow_all":
                    selected_tools = []
                    
                    # Find all tool checkboxes and collect selected ones
                    for checkbox in self.query("Checkbox").results():
                        if checkbox.id and checkbox.id.startswith("tool_") and checkbox.value:
                            # Extract tool name (remove warning emoji if present)
                            tool_name = checkbox.label.replace("⚠️ ", "")
                            selected_tools.append(tool_name)
                    
                    config["tools"] = {self.server_name: selected_tools}
                
                # Include block message (would be editable in real implementation)
                config["block_message"] = "Tool access denied by security policy"
                
                return config

POLICIES = {
    "tool_allowlist": ToolAllowlistPlugin
}
```

### Audit Plugin: JSON Logger

```python
# watchgate/plugins/auditing/json_lines.py
"""JSON auditing plugin for Watchgate MCP gateway."""

import json
from typing import Dict, Any
from watchgate.plugins.auditing.base import BaseAuditingPlugin

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Static, Checkbox, Button
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

class JsonAuditingPlugin(BaseAuditingPlugin):
    """JSON auditing plugin for GRC platform integration."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize JSON auditing plugin."""
        super().__init__(config)
        self.include_request_body = config.get("include_request_body", False)
        self.pretty_print = config.get("pretty_print", False)
        # ... rest of existing implementation
    
    async def log_request(self, request, decision, server_name: str) -> None:
        """Log request in JSON format."""
        # ... existing audit logic unchanged
        pass
    
    # ========== TUI Configuration Support ==========
    
    @classmethod
    def get_config_widget(cls, current_config: dict, context: dict = None):
        """Return widget for TUI configuration."""
        if not HAS_TEXTUAL:
            return None
        return cls.JSONAuditConfigWidget(current_config)
    
    if HAS_TEXTUAL:
        class JSONAuditConfigWidget(Container):
            """TUI configuration widget for JSON Audit Logger."""
            
            def __init__(self, config: dict):
                super().__init__()
                self.config = config or {}
            
            def compose(self) -> ComposeResult:
                """Compose the widget UI."""
                
                # Status display
                output_file = self.config.get("output_file", "logs/audit.json")
                yield Static(f"JSON Audit Logger", classes="header")
                yield Static(f"Output: {output_file}", classes="file-info")
                yield Static("Size: 2.3 MB today, 45 MB total", classes="stats")
                
                # Configuration options
                yield Static("Logging Options:", classes="section-header")
                
                yield Checkbox(
                    "Include Request Body",
                    value=self.config.get("include_request_body", False),
                    id="include_request_body"
                )
                yield Static("Include full request parameters in logs", classes="help-text")
                
                yield Checkbox(
                    "Pretty Print JSON", 
                    value=self.config.get("pretty_print", False),
                    id="pretty_print"
                )
                yield Static("Format JSON with indentation (larger files)", classes="help-text")
                
                yield Checkbox(
                    "Include Risk Metadata",
                    value=self.config.get("include_risk_metadata", True),
                    id="include_risk_metadata" 
                )
                
                yield Checkbox(
                    "API Compatible Format",
                    value=self.config.get("api_compatible", True),
                    id="api_compatible"
                )
                
                # File management
                yield Static("File Management:", classes="section-header")
                max_size = self.config.get("max_file_size_mb", 10)
                backup_count = self.config.get("backup_count", 5)
                
                yield Static(f"Max file size: {max_size} MB", classes="config-display")
                yield Static(f"Backup files: {backup_count}", classes="config-display") 
                yield Static(f"Critical: {'Yes' if self.config.get('critical', True) else 'No'}", 
                           classes="config-display")
                
                # Action buttons
                with Horizontal():
                    yield Button("View Logs", id="view_logs")
                    yield Button("Rotate Log", id="rotate_log")
            
            def get_config(self) -> dict:
                """Extract configuration from widget state."""
                return {
                    "output_file": self.config.get("output_file", "logs/audit.json"),
                    "include_request_body": self.query_one("#include_request_body", Checkbox).value,
                    "pretty_print": self.query_one("#pretty_print", Checkbox).value,
                    "include_risk_metadata": self.query_one("#include_risk_metadata", Checkbox).value,
                    "api_compatible": self.query_one("#api_compatible", Checkbox).value,
                    "max_file_size_mb": self.config.get("max_file_size_mb", 10),
                    "backup_count": self.config.get("backup_count", 5),
                    "critical": self.config.get("critical", True)
                }

POLICIES = {
    "json_auditing": JsonAuditingPlugin
}
```

## TUI Integration

The TUI implementation is minimal - just mount the plugin's widget:

```python
# In the TUI application
class PluginConfigurationPanel(Container):
    """Panel for configuring individual plugins."""
    
    def show_plugin_config(self, plugin_class, current_config: dict, context: dict = None):
        """Display configuration UI for a plugin."""
        
        # Clear current content
        self.query("*").remove()
        
        # Check if plugin supports TUI configuration
        if hasattr(plugin_class, 'get_config_widget'):
            widget = plugin_class.get_config_widget(current_config, context)
            if widget:
                # Mount the plugin's widget directly
                self.mount(widget)
                return
        
        # Plugin doesn't support TUI configuration
        self.mount(Static(
            f"Plugin '{plugin_class.__name__}' doesn't provide TUI configuration.\n"
            "Configure via YAML file instead.",
            classes="no-ui-message"
        ))
    
    def save_plugin_config(self) -> dict:
        """Extract configuration from the current plugin widget."""
        widget = self.query_one()
        if hasattr(widget, 'get_config'):
            return widget.get_config()
        return None
```

## Benefits of This Approach

1. **Complete Freedom**: Plugin authors use Textual however they want
2. **Single File**: All code (logic + UI) in one place
3. **No Abstraction**: We don't interpret or generate anything
4. **Easy Distribution**: Users drop in one Python file
5. **Future Proof**: As Textual evolves, plugins can use new features immediately
6. **Equal Treatment**: Built-in plugins follow same rules as user plugins
7. **Graceful Fallback**: Works without Textual installed

## Migration Guide

To add TUI support to an existing plugin:

1. **Add Textual imports** (with try/catch for optional dependency)
2. **Add the `get_config_widget` classmethod**
3. **Create widget as inner class** (if HAS_TEXTUAL)
4. **Implement `compose()` method** with your UI
5. **Implement `get_config()` method** to extract configuration

The plugin continues to work exactly the same for non-TUI usage.

## No Fallbacks

If a plugin doesn't implement `get_config_widget()` or returns `None`, it simply doesn't appear in the TUI configuration options. Users configure it via YAML instead.

This forces plugin authors to make a conscious choice: support TUI or don't. No half-measures, no generic editors, no schema guessing.