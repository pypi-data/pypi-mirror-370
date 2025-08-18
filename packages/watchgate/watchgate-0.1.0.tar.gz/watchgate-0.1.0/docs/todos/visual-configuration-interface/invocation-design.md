# TUI Invocation Design

## Overview

This document details the command-line invocation patterns for Watchgate's dual-mode operation: Terminal User Interface (TUI) for human configuration and proxy mode for MCP client integration.

## Command Structure

### Human Configuration (TUI Mode)

**Primary usage**: Users configuring and managing Watchgate

```bash
# Launch TUI with default/discovered configuration
watchgate

# Launch TUI with specific configuration file
watchgate --config /path/to/config.yaml
watchgate -c ~/watchgate/production.yaml
```

### MCP Client Integration (Proxy Mode)

**Primary usage**: MCP clients like Claude Desktop invoking Watchgate as a proxy

```bash
# Run as MCP proxy with configuration
watchgate proxy --config /path/to/config.yaml
watchgate proxy -c ~/.watchgate/config.yaml
```

## User Workflows

### First-Time Setup

1. **User runs `watchgate`**
2. **TUI detects no configuration exists**
3. **TUI offers to create new configuration:**
   - Guided setup wizard
   - Template selection (minimal, development, production)
   - Server discovery and connection testing
4. **Configuration is saved and immediately usable**

### Daily Configuration Management

1. **User runs `watchgate`** (loads last used configuration)
2. **TUI shows current configuration state:**
   - Running servers and connection status
   - Active security plugins
   - Recent audit log entries
3. **User can modify settings and see changes hot-reloaded**

### Environment-Specific Configuration

1. **User runs `watchgate --config production.yaml`**
2. **TUI loads and displays production configuration**
3. **User can safely modify without affecting other environments**
4. **Changes are saved to the specified file**

### MCP Client Integration

1. **Claude Desktop starts with configuration:**
   ```json
   "mcpServers": {
     "watchgate": {
       "command": "watchgate",
       "args": ["proxy", "--config", "/path/to/config.yaml"]
     }
   }
   ```
2. **Watchgate runs in proxy mode (no TUI)**
3. **All MCP communication is monitored and secured**

## Integration with Hot-Swap Architecture

### TUI Configuration Changes

When users modify settings in the TUI:

1. **TUI writes changes to active configuration file**
2. **File watcher in proxy instances detects changes**
3. **Hot-reload triggers automatic configuration update**
4. **User sees real-time effects without proxy restart**

### Multi-Instance Management

The TUI can discover and manage multiple running Watchgate instances:

```bash
# TUI discovers these running instances
watchgate proxy --config ~/dev/config.yaml     # PID 1234
watchgate proxy --config ~/prod/config.yaml    # PID 5678
```

The TUI shows both instances and allows:
- **Instance selection**: Choose which instance to configure
- **Configuration comparison**: See differences between environments
- **Synchronized updates**: Apply changes to multiple instances

### Configuration Editing

Users can create and modify configuration files:

1. **TUI shows available configuration files**
2. **User selects or creates configuration**
3. **TUI applies changes to active proxy instance**
4. **Changes take effect immediately via hot-reload**

## Command Line Options

### Global Options

- `--config, -c FILE`: Specify configuration file path
- `--verbose, -v`: Enable verbose output (for proxy mode)
- `--help, -h`: Show help message

### TUI Mode (default)

```bash
watchgate [--config FILE]
```

**Behavior:**
- No configuration file: TUI offers to create one or discovers existing
- With configuration file: TUI loads and displays the specified config
- File watching: TUI can optionally watch for external changes
- Instance discovery: TUI discovers running proxy instances

### Proxy Mode

```bash
watchgate proxy --config FILE [--verbose]
```

**Behavior:**
- Configuration file required
- Runs as MCP proxy server
- Enables hot-reload via file watching
- Logs to configured destinations

### Future Subcommands

Extensibility for additional operations:

```bash
watchgate validate --config FILE    # Validate configuration
watchgate status                     # Show running instances  
watchgate logs                       # View audit logs
watchgate test --config FILE        # Test MCP server connections
```

## Error Handling

### Missing Textual Dependency

```bash
$ watchgate
Error: TUI functionality requires the Textual library.
Install with: pip install 'watchgate[tui]'
Or run in proxy mode: watchgate proxy --config FILE
```

### Configuration Errors

**TUI Mode:**
- Shows friendly error dialog
- Offers to create new configuration
- Provides validation feedback

**Proxy Mode:**
- Logs detailed error information
- Exits with non-zero status
- Compatible with MCP client error handling

### File Permission Issues

**TUI Mode:**
- Shows user-friendly error message
- Suggests permission fixes
- Offers alternative file locations

**Proxy Mode:**
- Logs technical details
- Fails fast for automated systems

## Migration Guide

### For MCP Client Configurations

**Before (v0.1.0):**
```json
"mcpServers": {
  "watchgate": {
    "command": "watchgate", 
    "args": ["--config", "/path/to/config.yaml"]
  }
}
```

**After (v0.2.0):**
```json
"mcpServers": {
  "watchgate": {
    "command": "watchgate",
    "args": ["proxy", "--config", "/path/to/config.yaml"] 
  }
}
```

### Backward Compatibility

During the transition period:
- Old format shows deprecation warning
- Continues to work if stdin is not a TTY (MCP client context)
- Humans using old format get TUI with their config loaded

### Migration Steps

1. **Update MCP client configurations** to use `proxy` subcommand
2. **Test new configurations** with MCP clients
3. **Users can immediately benefit** from TUI without changing proxy configs
4. **Gradual adoption** of new patterns

## Development and Testing

### Local Development

```bash
# Develop TUI features
watchgate

# Test proxy functionality  
watchgate proxy --config test-config.yaml

# Test with real MCP client
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \
  watchgate proxy --config test-config.yaml
```

### Automated Testing

```bash
# Test TUI launch (with mocked Textual)
python -m pytest tests/tui/

# Test proxy mode
python -m pytest tests/integration/test_proxy_invocation.py

# Test backward compatibility
python -m pytest tests/integration/test_migration.py
```

## Security Considerations

### TUI Mode
- Runs with user permissions
- Reads/writes configuration files in user space
- No network listening (safe for desktop use)

### Proxy Mode
- Handles MCP client connections
- May have elevated permissions for system integration
- Network communication with upstream servers

### File Access
- Configuration files contain sensitive policy settings
- TUI respects file permissions
- Proxy mode validates configuration file ownership

## Platform Considerations

### Cross-Platform Paths
- Uses `pathlib.Path` for consistent path handling
- Supports `~` expansion for home directories
- Handles Windows/macOS/Linux path differences

### Terminal Compatibility
- TUI requires modern terminal with color support
- Graceful degradation for limited terminals
- Proxy mode works in any shell environment

## Future Enhancements

### Enhanced TUI Features
- **Configuration wizard**: Step-by-step setup for new users
- **Real-time monitoring**: Live view of MCP traffic and security events
- **Plugin marketplace**: Discover and install security plugins
- **Configuration sharing**: Export/import security configurations

### Advanced CLI Features
- **Configuration validation**: `watchgate validate --config FILE`
- **Health checks**: `watchgate status --all-instances`
- **Log analysis**: `watchgate analyze --logs /path/to/logs`
- **Performance monitoring**: `watchgate monitor --duration 60s`

This invocation design provides clear separation between human and automated usage while maintaining flexibility for future enhancements.