# ADR-018: Plugin UI Widget Architecture

**Status:** Accepted 
**Deciders:** Development Team  

## Context

Watchgate's TUI needs a mechanism for plugins to provide their own configuration interfaces. Plugin configuration can be highly varied:

- **Security plugins** need complex UIs (PII types, detection actions, exemptions)
- **Auditing plugins** need file management, formatting options, connection settings
- **Server-specific plugins** need context about available tools and server capabilities
- **Different plugin types** have fundamentally different configuration needs

We need a solution that:
- Gives plugin authors maximum flexibility for their UI
- Avoids forcing all plugins into a generic configuration schema
- Allows plugins to leverage the full power of Textual widgets
- Maintains consistency with Watchgate's TUI experience
- Works with optional Textual dependency (graceful fallback)

## Decision

**Plugins provide their own Textual widgets directly for TUI configuration.**

### Plugin Contract

Plugins that want TUI support must implement:

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

### Implementation Pattern

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

### TUI Integration

The TUI implementation is minimal - just mount the plugin's widget:

```python
# Check if plugin supports TUI configuration
if hasattr(plugin_class, 'get_config_widget'):
    widget = plugin_class.get_config_widget(current_config, context)
    if widget:
        # Mount the plugin's widget directly
        self.mount(widget)
        return

# Plugin doesn't support TUI configuration
self.mount(Static("Plugin doesn't provide TUI configuration"))
```

## Alternatives Considered

### 1. Schema-Based Configuration
**Approach:** Plugins declare configuration schemas, TUI generates forms automatically.

**Rejected because:**
- Forces all plugins into generic form patterns
- Cannot handle complex UI needs (grouped checkboxes, dynamic layouts)
- Requires maintaining schema language and form generator
- Plugin authors lose control over user experience

### 2. Abstraction Layer
**Approach:** Create intermediate widgets (ConfigSection, ConfigGroup) that plugins compose.

**Rejected because:**
- Adds unnecessary complexity and learning curve
- Limits plugin authors to our predefined widget types
- Still requires maintaining abstraction layer code
- Textual already provides excellent primitive widgets

### 3. External Configuration Tools
**Approach:** Launch external editors or web interfaces for plugin configuration.

**Rejected because:**
- Breaks unified TUI experience
- Adds complexity for deployment and dependencies
- Poor user experience (context switching)
- Difficult to integrate with live configuration updates

### 4. YAML-Only Configuration
**Approach:** Require all plugin configuration via YAML files.

**Rejected because:**
- Poor user experience for complex configurations
- No validation feedback or guided setup
- Difficult to discover available options
- No integration with server context (available tools, etc.)

## Consequences

### Positive
- **Maximum flexibility** - Plugin authors use Textual however they want
- **Single file approach** - All code (logic + UI) in one place
- **No abstraction overhead** - Direct use of Textual widgets
- **Future-proof** - As Textual evolves, plugins can use new features immediately
- **Equal treatment** - Built-in plugins follow same rules as user plugins
- **Graceful fallback** - Works without Textual installed
- **Context-aware** - Plugins receive server context for intelligent UIs

### Negative
- **Learning curve** - Plugin authors must learn Textual
- **Code duplication** - Similar UI patterns may be repeated across plugins
- **Testing complexity** - Plugin authors must test their UI components
- **Textual dependency** - Optional but required for TUI features

### Mitigations
- Provide comprehensive examples and documentation
- Include common UI patterns in documentation
- Make Textual dependency optional with clear fallback behavior
- Ensure core plugin functionality works without UI components

## Implementation Notes

### Context Parameter
The `context` parameter allows plugins to receive relevant information:
- `server_name`: For server-specific plugins
- `available_tools`: For tool-related security plugins  
- `upstream_config`: Server configuration details
- `capabilities`: Server capabilities from MCP discovery

### Error Handling
- If `get_config_widget()` raises an exception, treat as "no TUI support"
- If returned widget doesn't implement `get_config()`, show error message
- Invalid configuration from `get_config()` should be handled gracefully

### Testing Strategy
- Plugin UI components should be unit tested independently
- TUI integration tests verify widget mounting and config extraction
- Manual testing for complex UI interactions

## References
- Plugin UI Implementation Guide: `docs/todos/visual-configuration-interface/plugin-ui-implementation.md`
- Textual Documentation: https://textual.textualize.io/
- Plugin Interface Definition: `watchgate/plugins/interfaces.py`