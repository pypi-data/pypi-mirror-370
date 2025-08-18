# ADR-017: TUI Invocation Pattern

> **Note: This ADR has been superseded by [ADR-019: TUI Distribution and Licensing Model](./019-tui-distribution-and-licensing-model.md)**
> 
> ADR-019 updates the command structure from `watchgate proxy` to `watchgate-gateway`
> as part of a broader licensing and distribution strategy to eliminate terminology confusion.

## Status

Superseded

## Context

Watchgate serves two distinct use cases that require different invocation patterns:

1. **MCP Client Integration**: Automated systems (like Claude Desktop) invoke Watchgate to proxy MCP connections between clients and servers. This requires a stable, predictable command-line interface.

2. **Human Configuration**: Users need an intuitive way to configure Watchgate's security policies, audit settings, and server connections through a Terminal User Interface (TUI).

The challenge is providing both capabilities without creating confusion or breaking existing integrations.

### Initial Considerations

We initially considered several approaches:

1. **Auto-detection based on `isatty()`**: Automatically launch TUI when stdin is a terminal, proxy mode when piped. This was rejected as "too clever" and potentially confusing.

2. **Mode flags**: Using flags like `--tui` vs default proxy behavior. This requires users to remember flags and doesn't make the default use case obvious.

3. **Separate commands**: Creating `watchgate-config` alongside `watchgate`. This fragments the user experience and requires separate installation/distribution.

4. **Subcommands with serve**: Using `watchgate serve --config` vs `watchgate config`. The word "serve" was deemed inaccurate since Watchgate acts as a proxy, not a server.

## Decision

We will implement a **human-first default** with explicit subcommands:

- **`watchgate`** - Opens TUI configuration interface (default behavior)
- **`watchgate --config file`** - Opens TUI with specific configuration file loaded
- **`watchgate proxy --config file`** - Run as MCP proxy server (required for MCP clients)

## Rationale

### Human-First Default

Making TUI the default behavior optimizes for the most common human interaction: configuration. Users can simply type `watchgate` to manage their security policies and server configurations.

### Explicit Automation

MCP clients and automated systems must explicitly use `watchgate proxy --config file`. This:
- Makes the intent clear in configuration files
- Prevents accidental TUI launches in automated contexts  
- Provides stability for programmatic usage
- Uses accurate terminology ("proxy" matches Watchgate's technical role)

### Progressive Disclosure

New users encounter the friendly TUI by default, while advanced users and automated systems use explicit subcommands. This follows the principle of making simple things simple and complex things possible.

### Terminology Alignment

Using `proxy` as the subcommand aligns with Watchgate's technical architecture and clarifies its role for users, even though the product is marketed as a "gateway."

## Consequences

### Positive

- **Intuitive default**: Users get immediate value from typing `watchgate`
- **Clear separation**: Configuration vs operation modes are explicit
- **Future extensibility**: Easy to add more subcommands (`watchgate validate`, `watchgate status`, etc.)
- **Automation-friendly**: MCP clients have stable, explicit invocation

### Negative

- **Breaking change**: Existing MCP client configurations must be updated
- **Migration effort**: Users must update their `claude_desktop_config.json` files
- **Command complexity**: Slightly more verbose for MCP client configurations

### Migration Strategy

To minimize disruption during the transition:

1. **Backward compatibility detection**: If `--config` is used without a subcommand and stdin is not a TTY (indicating MCP client usage), show a deprecation warning and run in proxy mode.

2. **Clear migration guidance**: Provide documentation and examples for updating MCP client configurations.

3. **Graceful degradation**: If the Textual TUI library is not installed, provide a helpful error message directing users to install the `[tui]` extras.

## Implementation Details

### Command Structure

```bash
# TUI modes (human interaction)
watchgate                    # Open TUI with default/last config
watchgate --config file      # Open TUI with specific config

# Proxy mode (MCP client integration)  
watchgate proxy --config file   # Run as MCP proxy

# Future extensibility
watchgate validate --config file  # Validate configuration
watchgate status                   # Show running instances
```

### Backward Compatibility

During transition period:
```python
if args.config and not args.subcommand:
    if not sys.stdin.isatty():
        # MCP client calling - maintain compatibility
        logger.warning("DEPRECATION: Use 'watchgate proxy --config' for MCP server mode")
        run_proxy_mode(args.config)
    else:
        # Human at terminal - open TUI with config
        run_tui_mode(args.config)
```

### Dependencies

- TUI functionality requires `textual>=0.47.0` as an optional dependency
- Installation with TUI support: `pip install watchgate[tui]`
- Core functionality remains available without Textual

## Alternative Considered

**Option: `watchgate run --config`** was considered as a neutral alternative to avoid the gateway/proxy terminology tension. However, `proxy` was chosen for its technical accuracy and to help users understand Watchgate's architecture.

## Decision Date

January 2025

## Decision Makers

User preference after evaluating multiple approaches and considering both technical accuracy and user experience implications.