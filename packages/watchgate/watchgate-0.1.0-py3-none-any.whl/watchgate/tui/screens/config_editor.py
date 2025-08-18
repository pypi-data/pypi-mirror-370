"""Configuration editor screen for Watchgate TUI."""

from typing import Optional, Dict, List, Any
from pathlib import Path

from watchgate.config.models import ProxyConfig
from watchgate.plugins.manager import PluginManager

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Footer, Static, ListView, ListItem, Label


class ClickablePluginItem(Static, can_focus=True):
    """A clickable plugin item for global plugins section."""
    
    class GlobalPluginSelected(Message):
        """Message posted when a global plugin is selected."""
        
        def __init__(self, policy_name: str, plugin_type: str):
            self.policy_name = policy_name
            self.plugin_type = plugin_type
            super().__init__()
    
    def __init__(self, content: str, policy_name: str, plugin_type: str, **kwargs):
        super().__init__(content, **kwargs)
        self.policy_name = policy_name
        self.plugin_type = plugin_type
    
    def on_click(self) -> None:
        """Handle click events."""
        self.post_message(self.GlobalPluginSelected(self.policy_name, self.plugin_type))


class ConfigEditorScreen(Screen):
    """Main configuration editor screen with horizontal split layout."""
    
    CSS = """
    ConfigEditorScreen {
        background: $surface;
    }
    
    .header {
        height: 3;
        content-align: center middle;
        margin-bottom: 1;
    }
    
    .global-plugins-section {
        height: 12;
        margin-bottom: 1;
        border: solid $primary;
    }
    
    .global-section-title {
        height: 1;
        background: $primary;
        color: $background;
        content-align: center middle;
        text-style: bold;
    }
    
    .global-plugins-container {
        height: 1fr;
        padding: 1;
    }
    
    .server-management-section {
        height: 1fr;
        border: solid $primary;
    }
    
    .server-panes-container {
        height: 1fr;
    }
    
    .server-list-pane {
        width: 1fr;
        border-right: solid $secondary;
    }
    
    .server-plugins-pane {
        width: 1fr;
        border-right: solid $secondary;
    }
    
    .server-details-pane {
        width: 2fr;
    }
    
    .pane-title {
        height: 1;
        background: $secondary;
        color: $text;
        content-align: center middle;
        text-style: bold;
    }
    
    .pane-content {
        height: 1fr;
        padding: 1;
    }
    
    .plugin-item {
        height: 1;
        margin-bottom: 1;
        padding: 0 1;
    }
    
    .plugin-item:hover {
        background: $secondary;
        color: $text;
    }
    
    .plugin-item:focus {
        background: $primary;
        color: $background;
    }
    
    .plugin-status-active {
        color: $success;
        text-style: bold;
    }
    
    .plugin-status-disabled {
        color: $error;
    }
    
    .plugin-status-available {
        color: $text-muted;
    }
    
    .plugin-section-header {
        height: 1;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        padding: 0 1;
    }
    
    .button-row {
        height: 3;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("s", "save_config", "Save", priority=True),
        Binding("r", "reload_config", "Reload", priority=True),
        Binding("escape", "back_to_selector", "Back", priority=True),
        Binding("q", "quit", "Quit", priority=True),
    ]
    
    def __init__(self, config_file_path: Path, loaded_config: ProxyConfig):
        """Initialize the configuration editor.
        
        Args:
            config_file_path: Path to the configuration file
            loaded_config: Loaded and validated configuration
        """
        super().__init__()
        self.config_file_path = config_file_path
        self.config = loaded_config
        self.plugin_manager = None
        self.available_policies = {}
        self.selected_server = None
        self.selected_plugin = None
        
    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Static(f"Configuration Editor - {self.config_file_path.name}", classes="header")
        
        # Global plugins section (top)
        with Container(classes="global-plugins-section"):
            yield Static("Global Security & Auditing Plugins", classes="global-section-title")
            with Container(classes="global-plugins-container"):
                yield Container(id="global_security_plugins")
                yield Container(id="global_auditing_plugins")
        
        # Server management section (bottom) 
        with Container(classes="server-management-section"):
            with Horizontal(classes="server-panes-container"):
                # Left pane: MCP Servers list
                with Vertical(classes="server-list-pane"):
                    yield Static("MCP Servers", classes="pane-title")
                    with Container(classes="pane-content"):
                        yield ListView(id="servers_list")
                
                # Middle pane: Server plugins list
                with Vertical(classes="server-plugins-pane"):
                    yield Static("Server Plugins", classes="pane-title")
                    with Container(classes="pane-content"):
                        yield ListView(id="server_plugins_list")
                
                # Right pane: Configuration details
                with Vertical(classes="server-details-pane"):
                    yield Static("Configuration Details", classes="pane-title")
                    with Container(classes="pane-content"):
                        yield Container(id="config_details")
        
        # Action buttons
        with Horizontal(classes="button-row"):
            yield Button("Save Configuration", id="save_btn", variant="primary")
            yield Button("Reload from File", id="reload_btn")
            yield Button("Back to Selector", id="back_btn")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        await self._initialize_plugin_system()
        await self._populate_global_plugins()
        await self._populate_servers_list()
        
    async def _initialize_plugin_system(self) -> None:
        """Initialize plugin manager and discover available policies."""
        try:
            # Create a plugin manager to discover available policies
            plugins_config = {}
            if self.config.plugins:
                plugins_config = self.config.plugins.to_dict()
            
            self.plugin_manager = PluginManager(
                plugins_config, 
                config_directory=self.config_file_path.parent
            )
            
            # Discover available policies
            self.available_policies = {
                "security": self.plugin_manager._discover_policies("security"),
                "auditing": self.plugin_manager._discover_policies("auditing")
            }
            
        except Exception as e:
            # Handle plugin system initialization errors gracefully
            self.available_policies = {"security": {}, "auditing": {}}
    
    async def _populate_global_plugins(self) -> None:
        """Populate the global plugins section."""
        security_container = self.query_one("#global_security_plugins", Container)
        auditing_container = self.query_one("#global_auditing_plugins", Container)
        
        # Clear existing content
        security_container.remove_children()
        auditing_container.remove_children()
        
        # Add security section title and plugins
        security_container.mount(Static("GLOBAL SECURITY", classes="plugin-section-header"))
        await self._add_global_plugin_items(security_container, "security")
        
        # Add auditing section title and plugins  
        auditing_container.mount(Static("GLOBAL AUDITING", classes="plugin-section-header"))
        await self._add_global_plugin_items(auditing_container, "auditing")
    
    async def _add_global_plugin_items(self, container: Container, plugin_type: str) -> None:
        """Add global plugin items to a container.
        
        Args:
            container: Container to add plugins to
            plugin_type: Type of plugins ("security" or "auditing")
        """
        available_policies = self.available_policies.get(plugin_type, {})
        
        # Get configured global plugins for this type
        configured_plugins = {}
        if self.config.plugins:
            plugins_dict = getattr(self.config.plugins, plugin_type, {})
            global_plugins = plugins_dict.get("_global", [])
            for plugin_config in global_plugins:
                configured_plugins[plugin_config.policy] = plugin_config
        
        # Display all available policies with their status
        for policy_name, policy_class in available_policies.items():
            description = self._get_plugin_description(policy_name, plugin_type)
            
            if policy_name in configured_plugins:
                plugin_config = configured_plugins[policy_name]
                if plugin_config.enabled:
                    status = "✅ Active"
                    status_class = "plugin-status-active"
                    action = "Configure"
                else:
                    status = "❌ Disabled"
                    status_class = "plugin-status-disabled"
                    action = "Enable"
            else:
                status = "○ Available"
                status_class = "plugin-status-available" 
                action = "Setup"
            
            # Create plugin display item with description
            display_text = f"{self._format_policy_name(policy_name)} [{status}] {description}"
            plugin_display = ClickablePluginItem(
                display_text, 
                policy_name, 
                plugin_type, 
                classes=f"plugin-item {status_class}"
            )
            container.mount(plugin_display)
    
    def _format_policy_name(self, policy_name: str) -> str:
        """Format policy name for display."""
        # Convert actual policy names from POLICIES manifests to display names
        name_mapping = {
            # Security plugins
            "pii": "PII Filter",
            "secrets": "Secrets Filter", 
            "prompt_injection": "Prompt Defense",
            "tool_allowlist": "Tool Allowlist", 
            "filesystem_server": "Path Security",
            # Auditing plugins
            "json_auditing": "JSON Logger",
            "csv_auditing": "CSV Export", 
            "syslog_auditing": "Syslog Forward",
            "line_auditing": "Human Readable",
            "debug_auditing": "Debug Logger",
            "cef_auditing": "CEF Logger",
            "otel_auditing": "OpenTelemetry"
        }
        return name_mapping.get(policy_name, policy_name.replace("_", " ").title())
    
    def _get_plugin_description(self, policy_name: str, plugin_type: str) -> str:
        """Get description for a plugin based on its configuration and status."""
        descriptions = {
            # Security plugins
            "pii": "Redacting: Email, Phone, SSN",
            "secrets": "Blocking: API Keys, Tokens, Passwords", 
            "prompt_injection": "Click to enable injection protection",
            "tool_allowlist": "Control which tools are accessible",
            "filesystem_server": "Restrict file system access paths",
            # Auditing plugins
            "json_auditing": "logs/audit.json (audit trail in JSON format)",
            "csv_auditing": "Export audit logs to CSV format",
            "syslog_auditing": "Send logs to remote syslog server",
            "line_auditing": "Human readable audit log format",
            "debug_auditing": "Detailed debug information logging",
            "cef_auditing": "Common Event Format logging",
            "otel_auditing": "OpenTelemetry distributed tracing"
        }
        return descriptions.get(policy_name, "Plugin configuration")
    
    async def _populate_servers_list(self) -> None:
        """Populate the MCP servers list."""
        servers_list = self.query_one("#servers_list", ListView)
        servers_list.clear()
        
        for upstream in self.config.upstreams:
            # Create server list item with status
            status_indicator = "●" if self._is_server_connected(upstream.name) else "○"
            status_text = "Connected" if self._is_server_connected(upstream.name) else "Not connected"
            
            # Count tools (placeholder for now)
            tool_count = "? tools"  # TODO: Get actual tool count from server
            
            # Show command or URL info
            transport_info = ""
            if upstream.transport == "stdio" and upstream.command:
                cmd_text = " ".join(upstream.command)
                if len(cmd_text) > 30:
                    cmd_text = cmd_text[:27] + "..."
                transport_info = cmd_text
            elif upstream.transport == "http" and upstream.url:
                transport_info = upstream.url
            
            server_item = ListItem(
                Label(f"{status_indicator} {upstream.name}"),
                Label(f"  {status_text}"),
                Label(f"  {tool_count}"),
                Label(f"  {transport_info}")
            )
            server_item.data_server_name = upstream.name
            servers_list.append(server_item)
    
    def _is_server_connected(self, server_name: str) -> bool:
        """Check if a server is currently connected."""
        # TODO: Implement actual connection status check
        return False  # Placeholder
    
    @on(ListView.Selected, "#servers_list")
    async def on_server_selected(self, event: ListView.Selected) -> None:
        """Handle server selection."""
        if event.item and hasattr(event.item, 'data_server_name'):
            self.selected_server = event.item.data_server_name
            await self._populate_server_plugins()
            await self._update_server_details()
    
    async def _populate_server_plugins(self) -> None:
        """Populate plugins list for the selected server."""
        if not self.selected_server:
            return
            
        plugins_list = self.query_one("#server_plugins_list", ListView)
        plugins_list.clear()
        
        # Get configured plugins for this server
        server_plugins = {"security": [], "auditing": []}
        if self.config.plugins:
            # Get security plugins
            security_plugins = self.config.plugins.security.get(self.selected_server, [])
            server_plugins["security"] = security_plugins
            
            # Get auditing plugins
            auditing_plugins = self.config.plugins.auditing.get(self.selected_server, [])
            server_plugins["auditing"] = auditing_plugins
        
        # Display configured plugins with status
        for plugin_type, plugins in server_plugins.items():
            for plugin_config in plugins:
                status = "✅" if plugin_config.enabled else "❌"
                plugin_item = ListItem(
                    Label(f"• {self._format_policy_name(plugin_config.policy)} {status}"),
                    Label(f"  {plugin_type.capitalize()} plugin")
                )
                plugin_item.data_policy = plugin_config.policy
                plugin_item.data_type = plugin_type
                plugins_list.append(plugin_item)
        
        # Show available plugins that aren't configured
        for plugin_type, available_policies in self.available_policies.items():
            configured_names = {p.policy for p in server_plugins[plugin_type]}
            for policy_name in available_policies:
                if policy_name not in configured_names:
                    plugin_item = ListItem(
                        Label(f"○ {self._format_policy_name(policy_name)}"),
                        Label(f"  Available {plugin_type} plugin")
                    )
                    plugin_item.data_policy = policy_name
                    plugin_item.data_type = plugin_type
                    plugins_list.append(plugin_item)
    
    async def _update_server_details(self) -> None:
        """Update the server details pane."""
        if not self.selected_server:
            return
            
        details_container = self.query_one("#config_details", Container)
        details_container.remove_children()
        
        # Find the upstream config
        upstream_config = None
        for upstream in self.config.upstreams:
            if upstream.name == self.selected_server:
                upstream_config = upstream
                break
        
        if upstream_config:
            details_container.mount(Static(f"Server: {upstream_config.name}", classes="server-detail-title"))
            details_container.mount(Static("─" * 30))
            details_container.mount(Static(f"Status: {'● Connected' if self._is_server_connected(upstream_config.name) else '○ Not connected'}"))
            details_container.mount(Static(f"Transport: {upstream_config.transport}"))
            
            if upstream_config.command:
                command_text = " ".join(upstream_config.command)
                if len(command_text) > 50:
                    command_text = command_text[:47] + "..."
                details_container.mount(Static(f"Command: {command_text}"))
            
            if upstream_config.url:
                details_container.mount(Static(f"URL: {upstream_config.url}"))
                
            details_container.mount(Static(""))
            details_container.mount(Static("Available Tools: TODO"))  # TODO: Show actual tools
    
    @on(ClickablePluginItem.GlobalPluginSelected)
    async def on_global_plugin_selected(self, event: ClickablePluginItem.GlobalPluginSelected) -> None:
        """Handle global plugin selection."""
        self.selected_plugin = {
            "policy": event.policy_name,
            "type": event.plugin_type,
            "server": "_global"  # Global plugins use _global scope
        }
        self.selected_server = None  # Clear server selection
        await self._show_plugin_configuration()

    @on(ListView.Selected, "#server_plugins_list")
    async def on_server_plugin_selected(self, event: ListView.Selected) -> None:
        """Handle server plugin selection."""
        if event.item and hasattr(event.item, 'data_policy'):
            self.selected_plugin = {
                "policy": event.item.data_policy,
                "type": event.item.data_type,
                "server": self.selected_server
            }
            await self._show_plugin_configuration()
    
    async def _show_plugin_configuration(self) -> None:
        """Show configuration for the selected plugin."""
        if not self.selected_plugin:
            return
            
        details_container = self.query_one("#config_details", Container)
        details_container.remove_children()
        
        policy_name = self.selected_plugin["policy"]
        plugin_type = self.selected_plugin["type"]
        scope = self.selected_plugin["server"]
        
        scope_text = "Global" if scope == "_global" else f"Server: {scope}"
        title = f"{self._format_policy_name(policy_name)} Configuration ({scope_text})"
        
        details_container.mount(Static(title, classes="plugin-config-title"))
        details_container.mount(Static("─" * 50))
        
        # Check if plugin supports TUI configuration
        policy_class = self.available_policies[plugin_type].get(policy_name)
        if policy_class and hasattr(policy_class, 'get_config_widget'):
            try:
                # Get current configuration
                current_config = self._get_current_plugin_config(policy_name, plugin_type, scope)
                
                # Create context for plugin
                context = {
                    "server_name": scope if scope != "_global" else None,
                    "available_tools": []  # TODO: Get actual tools from server
                }
                
                # Get plugin configuration widget
                config_widget = policy_class.get_config_widget(current_config, context)
                if config_widget:
                    details_container.mount(config_widget)
                else:
                    details_container.mount(Static("Plugin doesn't support TUI configuration"))
                    details_container.mount(Static("Please edit YAML file manually"))
            except Exception as e:
                details_container.mount(Static(f"Error loading plugin configuration: {e}"))
        else:
            details_container.mount(Static("Plugin doesn't support TUI configuration"))
            details_container.mount(Static("Please edit YAML file manually"))
    
    def _get_current_plugin_config(self, policy_name: str, plugin_type: str, scope: str = None) -> Dict[str, Any]:
        """Get current configuration for a plugin."""
        if not self.config.plugins:
            return {}
            
        plugins_dict = getattr(self.config.plugins, plugin_type, {})
        
        # If scope is specified, look in that scope first
        if scope:
            scope_plugins = plugins_dict.get(scope, [])
            for plugin_config in scope_plugins:
                if plugin_config.policy == policy_name:
                    return plugin_config.config
        
        # Fall back to global configuration if not found in scope
        if scope != "_global":
            global_plugins = plugins_dict.get("_global", [])
            for plugin_config in global_plugins:
                if plugin_config.policy == policy_name:
                    return plugin_config.config
        
        return {}
    
    @on(Button.Pressed, "#save_btn")
    def on_save_button(self) -> None:
        """Handle save button press."""
        self.action_save_config()
    
    @on(Button.Pressed, "#reload_btn")  
    def on_reload_button(self) -> None:
        """Handle reload button press."""
        self.action_reload_config()
    
    @on(Button.Pressed, "#back_btn")
    def on_back_button(self) -> None:
        """Handle back button press."""
        self.action_back_to_selector()
    
    def action_save_config(self) -> None:
        """Save current configuration to file."""
        # TODO: Implement configuration saving
        self.app.bell()  # Placeholder
    
    def action_reload_config(self) -> None:
        """Reload configuration from file."""
        # TODO: Implement configuration reloading
        self.app.bell()  # Placeholder
    
    def action_back_to_selector(self) -> None:
        """Return to configuration selector."""
        self.dismiss()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()