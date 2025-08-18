# ADR-009: Sequential Plugin Processing for Responses

**Status**: Accepted  

## Context

When implementing response modification capabilities (see ADR-008), we needed to determine how multiple plugins should interact when processing responses. The key question was whether plugins should process responses in parallel with conflict resolution, or sequentially with cumulative modifications.

This decision affects:
- **Deterministic behavior**: Whether plugin processing order matters
- **Plugin interaction**: How plugins compose their modifications
- **Performance**: Processing time and resource usage
- **Debugging**: Ability to trace plugin effects
- **Configuration complexity**: How users understand plugin behavior

### Use Case Driving the Decision

The tool allowlist plugin filters `tools/list` responses, potentially followed by other plugins that might:
- Add metadata to tool descriptions
- Reorder tools based on priority
- Transform tool schemas for compatibility
- Log or audit tool access patterns

## Decision

We will implement **sequential plugin processing** where plugins process responses one after another, with each plugin receiving the output of the previous plugin as input.

```python
async def process_response(self, response: MCPResponse) -> MCPResponse:
    """Process response through plugins sequentially."""
    current_response = response
    
    for plugin in self.response_plugins:
        decision = await plugin.check_response(current_response)
        
        if not decision.allowed:
            raise PluginBlockedError(decision.reason)
        
        if decision.modified_response is not None:
            current_response = decision.modified_response
            # Next plugin receives this modified response
    
    return current_response
```

### Processing Order

Plugin processing order is determined by priority values (0-100, with 50 as default):

```yaml
plugins:
  security:
    - policy: "tool_allowlist"     # Processes first (priority: 10)
      enabled: true
      config:
        priority: 10
    - policy: "content_filter"     # Processes second (priority: 20)
      enabled: true
      config:
        priority: 20
  auditing:
    - policy: "response_logger"    # Processes third (priority: 50, default)
      enabled: true
```

## Alternatives Considered

### Alternative 1: Parallel Processing with Conflict Resolution

```python
async def process_response(self, response: MCPResponse) -> MCPResponse:
    """Process response through all plugins in parallel."""
    decisions = await asyncio.gather(*[
        plugin.check_response(response) 
        for plugin in self.response_plugins
    ])
    
    # Resolve conflicts between different modifications
    return resolve_response_conflicts(response, decisions)
```

**Rejected because**:
- **Conflict resolution complexity**: No clear rules for merging conflicting modifications
- **Non-deterministic behavior**: Parallel execution order can vary
- **Plugin interaction unclear**: Plugins can't build on each other's work
- **Debugging difficulty**: Hard to trace which plugin caused what change

### Alternative 3: Plugin Priority System

```python
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 10  # Higher priority (lower number)
    - policy: "content_filter" 
      priority: 50  # Default priority
```

**Rejected because**:
- **Configuration complexity**: Users must understand and manage priority values
- **Maintenance burden**: Priorities need coordination across plugin ecosystem
- **Still requires conflict resolution**: Multiple plugins at same priority level
- **Harder migration**: Existing configurations would need priority assignment

Note: This alternative was later reconsidered and adopted in a subsequent decision.

### Alternative 4: Plugin Dependency Declaration

```python
class ContentFilterPlugin:
    depends_on = ["tool_allowlist"]  # Must run after allowlist
```

**Rejected because**:
- **Dependency complexity**: Creates plugin coupling and circular dependency risks
- **Configuration validation**: Need to verify dependency graphs are valid
- **Over-engineering**: Current use cases don't require complex dependencies
- **Plugin portability**: Plugins become less reusable across configurations

Note: This alternative was later reconsidered and rejected in favor of a simple priority system.

### Alternative 5: Response Accumulation with Original

```python
async def process_response(self, response: MCPResponse) -> MCPResponse:
    """Each plugin sees original response, accumulate changes."""
    modifications = []
    
    for plugin in self.response_plugins:
        decision = await plugin.check_response(response)  # Always original
        if decision.modified_response:
            modifications.append(decision.modified_response)
    
    return merge_modifications(response, modifications)
```

**Rejected because**:
- **Limited plugin capabilities**: Plugins can't see effects of previous plugins
- **Complex merging logic**: Need sophisticated merge strategies
- **Use case mismatch**: Some plugins need to see filtered/modified responses

## Consequences

### Positive

- **Deterministic Behavior**: Same input always produces same output
- **Simple Mental Model**: Easy to understand and predict plugin behavior
- **Plugin Composition**: Plugins can build on each other's modifications
- **Easy Debugging**: Clear trace of how response evolved through plugins
- **Configuration Simplicity**: Priority values determine processing order
- **Performance Predictability**: Linear processing time, no conflict resolution overhead

### Negative

- **Order Dependency**: Plugin priority values matter significantly
- **Potential Inefficiency**: Later plugins might undo work of earlier plugins
- **Plugin Coupling**: Plugins may need to be aware of other plugins' effects
- **Serial Bottleneck**: Can't parallelize plugin processing for performance

### Mitigation Strategies

1. **Clear Documentation**: Explain priority system and its implications
2. **Plugin Guidelines**: Best practices for plugin design and priority assignment
3. **Configuration Validation**: Warn about potentially problematic plugin priorities
4. **Audit Logging**: Log each plugin's decision for transparency

## Implementation Details

### Plugin Manager Sequential Processing

```python
class PluginManager:
    async def process_response(self, response: MCPResponse, request_id: str = None) -> MCPResponse:
        """Process response through all enabled plugins sequentially."""
        current_response = response
        plugin_trace = []
        
        # Process security plugins first, then auditing plugins
        for plugin in self._get_response_plugins():
            try:
                decision = await plugin.check_response(current_response)
                
                plugin_trace.append({
                    "plugin": plugin.__class__.__name__,
                    "allowed": decision.allowed,
                    "reason": decision.reason,
                    "modified": decision.modified_response is not None
                })
                
                if not decision.allowed:
                    self.logger.warning(
                        f"Plugin {plugin.__class__.__name__} blocked response: {decision.reason}",
                        extra={"request_id": request_id}
                    )
                    raise PluginBlockedError(
                        f"Response blocked by {plugin.__class__.__name__}: {decision.reason}"
                    )
                
                if decision.modified_response is not None:
                    self.logger.debug(
                        f"Plugin {plugin.__class__.__name__} modified response: {decision.reason}",
                        extra={"request_id": request_id}
                    )
                    current_response = decision.modified_response
                    
            except Exception as e:
                # Plugin-specific error handling
                self.logger.error(
                    f"Error in plugin {plugin.__class__.__name__}: {str(e)}",
                    extra={"request_id": request_id}
                )
                raise
        
        # Log final plugin processing trace for audit
        if plugin_trace:
            self.logger.debug(
                f"Response processed through {len(plugin_trace)} plugins",
                extra={"request_id": request_id, "plugin_trace": plugin_trace}
            )
        
        return current_response
```

### Plugin Ordering Strategy

```python
def _get_response_plugins(self) -> List[PluginInterface]:
    """Get plugins in processing order: sorted by priority (0-100, lower = higher priority)."""
    plugins = []
    
    # Collect all response-capable plugins
    plugins.extend(self.security_plugins)
    plugins.extend(self.auditing_plugins)
    
    # Sort by priority (ascending - lower numbers first)
    response_plugins = [p for p in plugins if hasattr(p, 'check_response')]
    return sorted(response_plugins, key=lambda p: getattr(p, 'priority', 50))
```

This sequential processing approach provides predictable, debuggable plugin behavior while enabling powerful plugin composition for response modification use cases.
