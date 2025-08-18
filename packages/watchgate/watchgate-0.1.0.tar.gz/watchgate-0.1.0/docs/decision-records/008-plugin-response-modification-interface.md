# ADR-008: Plugin Content Modification Interface

**Status**: Accepted  
**Date**: v0.1.0 Development  

## Context

### Initial Requirement

Watchgate's original plugin architecture supported allow/block decisions for requests through the `PolicyDecision` class. However, implementing tools/list response filtering revealed a need for plugins to modify responses, not just allow or block them entirely.

The requirement emerged from the tool allowlist security plugin, which needed to filter `tools/list` responses to show only allowed tools while preserving the overall response structure and other fields.

### Original Plugin Interface Limitation

```python
@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    # No way to specify modified content
```

This interface only supported binary allow/block decisions, making content modification impossible without significant architectural changes.

## Decision

We will **extend the existing `PolicyDecision` interface** to support generic content modification through a `modified_content` field that can handle any MCP message type:

```python
@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    modified_content: Optional[Union[MCPRequest, MCPResponse, MCPNotification]] = None
```

### Design Principles

1. **Generic Content Modification**: Support modification of requests, responses, and notifications through a single field
2. **Type Safety**: Use Union types and runtime type checking to ensure proper handling
3. **Security First**: Plugin manager must respect content modifications for all message types
4. **Clear Intent**: Field name explicitly indicates it can contain any content type
5. **Backward Compatibility**: Existing plugins continue to work without changes (those not modifying content)

### Plugin Manager Processing

Each processing method will check for the appropriate content type:

```python
# Request processing
if decision.modified_content and isinstance(decision.modified_content, MCPRequest):
    current_request = decision.modified_content

# Response processing  
if decision.modified_content and isinstance(decision.modified_content, MCPResponse):
    current_response = decision.modified_content

# Notification processing
if decision.modified_content and isinstance(decision.modified_content, MCPNotification):
    current_notification = decision.modified_content
```

### Usage Pattern

```python
class BasicPiiFilterPlugin(SecurityPlugin):
    async def check_request(self, request: MCPRequest) -> PolicyDecision:
        if self.mode == "redact" and contains_pii(request):
            redacted_request = redact_pii(request)
            return PolicyDecision(
                allowed=True,
                reason="PII detected and redacted from request",
                metadata={"pii_redacted": True},
                modified_content=redacted_request  # Proper field for request modification
            )
        return PolicyDecision(allowed=True, reason="No PII detected")

    async def check_response(self, request: MCPRequest, response: MCPResponse) -> PolicyDecision:
        if self.mode == "redact" and contains_pii(response):
            redacted_response = redact_pii(response)
            return PolicyDecision(
                allowed=True,
                reason="PII detected and redacted from response", 
                metadata={"pii_redacted": True},
                modified_content=redacted_response  # Same field for response modification
            )
        return PolicyDecision(allowed=True, reason="No PII detected")
```
```

## Alternatives Considered

### Alternative 1: Response-Specific Field (Original Design - Rejected)

```python
@dataclass
class PolicyDecision:
    modified_response: Optional[MCPResponse] = None  # Response-only
```

**Rejected because**:
- Cannot handle request or notification modifications
- Forces inappropriate workarounds for request modification (security vulnerability)
- Inconsistent interface for different message types

### Alternative 2: Separate Fields for Each Type

```python
@dataclass
class PolicyDecision:
    modified_request: Optional[MCPRequest] = None
    modified_response: Optional[MCPResponse] = None  
    modified_notification: Optional[MCPNotification] = None
```

**Rejected because**:
- Interface bloat with multiple optional fields
- Plugins can only modify one type per decision anyway
- More complex validation logic required

### Alternative 3: Backward Compatibility with Deprecation

```python
@dataclass
class PolicyDecision:
    modified_content: Optional[Union[MCPRequest, MCPResponse, MCPNotification]] = None
    modified_response: Optional[MCPResponse] = None  # Deprecated
```

**Rejected because**:
- Added complexity for zero benefit (no existing users in v0.1.0)
- Risk of continued use of deprecated field
- Clean break preferred for security-critical fix

### Alternative 4: Separate Decision Types

```python
class RequestDecision(PolicyDecision):
    modified_request: Optional[MCPRequest] = None

class ResponseDecision(PolicyDecision):  
    modified_response: Optional[MCPResponse] = None
```

**Rejected because**:
- Plugin interface complexity increases significantly
- Method signatures become more complex
- Plugin manager needs type-specific handling

## Consequences

### Positive

- **Security Fix**: Resolves critical vulnerability in request modification handling 
- **Unified Architecture**: Single field supports all content modification use cases
- **Type Safety**: Runtime type checking prevents misuse
- **Clean Design**: No deprecated fields or backward compatibility complexity
- **Future Proof**: Supports any future MCP message types
- **Backward Compatible**: Existing plugins that don't modify content continue to work unchanged

### Negative

- **Breaking Changes**: Any plugins using `modified_response` must be updated (none exist in v0.1.0)
- **Implementation Effort**: Requires updates across codebase and test suite
- **Documentation Updates**: All documentation and examples must be updated
- **Interface Complexity**: `PolicyDecision` now has Union types requiring type checking

### Implementation Requirements

1. **PolicyDecision Interface**: Replace `modified_response` with `modified_content`
2. **Plugin Manager Updates**: Must handle `modified_content` field in all processing pipelines
3. **Security Plugins**: Update PII filter and other plugins to use new field
4. **Test Suite**: Update all tests referencing `modified_response`
5. **Validation**: Content modifications must be validated for correctness and type safety
6. **Logging**: Plugin decisions with modifications need appropriate audit logging

### Migration Strategy

Since this is v0.1.0 with no existing users:
- **No backward compatibility** required
- **Clean removal** of response-specific design
- **Complete migration** to generic content modification architecture

### Risk Mitigation

- **Comprehensive Testing**: Full test coverage for all modification scenarios
- **Code Review**: Careful review of all plugin manager changes  
- **Documentation**: Clear migration guide and security considerations

## Implementation Details

### PolicyDecision Extension

```python
@dataclass
class PolicyDecision:
    """Decision from a policy plugin about whether to allow an operation."""
    
    allowed: bool
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    modified_content: Optional[Union[MCPRequest, MCPResponse, MCPNotification]] = None
    
    def __post_init__(self):
        """Validate PolicyDecision after initialization."""
        if self.modified_content is not None and not self.allowed:
            raise ValueError("Cannot provide modified_content when allowed=False")
```

### Plugin Manager Processing

```python
async def process_request(self, request: MCPRequest) -> PolicyDecision:
    """Process request through all plugins sequentially."""
    current_request = request
    final_decision = PolicyDecision(
        allowed=True,
        reason="Allowed by all security plugins", 
        metadata={"plugin_count": len(self.security_plugins)}
    )
    
    for plugin in self.security_plugins:
        decision = await plugin.check_request(current_request)
        
        if not decision.allowed:
            return decision
            
        # Handle request modifications
        if decision.modified_content and isinstance(decision.modified_content, MCPRequest):
            current_request = decision.modified_content
            final_decision.modified_content = current_request
            final_decision.reason = decision.reason
            final_decision.metadata = decision.metadata
    
    return final_decision

async def process_response(self, request: MCPRequest, response: MCPResponse) -> PolicyDecision:
    """Process response through all plugins sequentially."""
    current_response = response
    final_decision = PolicyDecision(
        allowed=True,
        reason="Response allowed by all security plugins",
        metadata={"plugin_count": len(self.security_plugins)}
    )
    
    for plugin in self.security_plugins:
        decision = await plugin.check_response(request, current_response)
        
        if not decision.allowed:
            return decision
        
        # Handle response modifications    
        if decision.modified_content and isinstance(decision.modified_content, MCPResponse):
            current_response = decision.modified_content
            final_decision.modified_content = current_response
            final_decision.reason = decision.reason
            final_decision.metadata = decision.metadata
    
    return final_decision
```

