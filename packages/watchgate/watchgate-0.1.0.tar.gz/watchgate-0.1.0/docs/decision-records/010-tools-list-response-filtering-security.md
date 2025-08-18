# ADR-010: Tools/List Response Filtering Security Model

**Status**: Accepted  

## Context

Watchgate's tool allowlist plugin originally controlled tool execution by blocking `tools/call` requests for disallowed tools. However, this approach had a security and user experience gap: clients could still discover blocked tools through `tools/list` requests, leading to:

1. **Information Disclosure**: Clients learn about tools they cannot execute
2. **Poor User Experience**: Users see tools they cannot use, causing confusion
3. **Security Inconsistency**: Policy applies to execution but not discovery
4. **Attack Surface**: Attackers can enumerate all available tools regardless of permissions

### Original Implementation Gap

```yaml
# Configuration allows specific tools
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file"]
```

**Existing behavior**:
- `tools/call` with `read_file` → ✅ Allowed
- `tools/call` with `delete_file` → ❌ Blocked
- `tools/list` → Shows all tools including `delete_file` ⚠️ **Information leak**

## Decision

We will **extend the tool allowlist plugin to filter `tools/list` responses** according to the same policy that controls tool execution, ensuring consistent security enforcement across both tool discovery and tool execution.

### Unified Security Model

```python
class ToolAllowlistPlugin:
    async def check_request(self, request: MCPRequest) -> PolicyDecision:
        """Control tool execution (existing functionality)."""
        # Block tools/call for disallowed tools
        
    async def check_response(self, response: MCPResponse) -> PolicyDecision:
        """Filter tool discovery (new functionality)."""
        # Filter tools/list to show only allowed tools
```

### Policy Application

**For all three modes (allowlist, blocklist, allow_all)**:

| Mode | tools/call Behavior | tools/list Behavior |
|------|-------------------|-------------------|
| `allowlist` | Allow only tools in list | Show only tools in list |
| `blocklist` | Block tools in list | Hide tools in list |
| `allow_all` | Allow all tools | Show all tools |

### Implementation Example

```python
async def check_response(self, response: MCPResponse) -> PolicyDecision:
    if response.result and "tools" in response.result:
        # Filter tools list based on policy
        original_tools = response.result["tools"]
        filtered_tools = self._filter_tools_by_policy(original_tools)
        
        if len(filtered_tools) != len(original_tools):
            # Create modified response with filtered tools
            modified_response = create_filtered_response(response, filtered_tools)
            return PolicyDecision(
                allowed=True,
                reason=f"Filtered {len(original_tools) - len(filtered_tools)} tools",
                modified_response=modified_response
            )
    
    return PolicyDecision(allowed=True, reason="No filtering needed")
```

## Alternatives Considered

### Alternative 1: Warning-Based Approach

Show all tools but warn when blocked tools are called:

```json
{
  "tools": [
    {"name": "read_file", "description": "Read a file"},
    {"name": "delete_file", "description": "⚠️ Restricted - Delete a file"}
  ]
}
```

**Rejected because**:
- **Still leaks information**: Attackers learn about restricted tools
- **User confusion**: Users don't understand why some tools are marked restricted
- **Inconsistent security**: Discovery policy differs from execution policy
- **Implementation complexity**: Requires response modification anyway

### Alternative 2: Separate Discovery Policy

Allow different policies for discovery vs. execution:

```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        execution_mode: "allowlist"
        execution_tools: ["read_file"]
        discovery_mode: "allow_all"  # Show all, block execution
```

**Rejected because**:
- **Configuration complexity**: Doubles the configuration surface area
- **Security inconsistency**: Policies can diverge and create gaps
- **User confusion**: Hard to understand why visible tools can't be executed
- **Maintenance burden**: Two policies to keep in sync

### Alternative 3: Client-Side Filtering

Let clients discover all tools but expect them to respect allowlists:

**Rejected because**:
- **Zero security value**: Clients can ignore filtering entirely
- **Information disclosure**: Attackers learn full tool inventory
- **Trust model violation**: Security enforcement should be server-side
- **Poor user experience**: Clients must implement their own filtering logic

### Alternative 4: Dynamic Tool Registration

Only register allowed tools with the upstream server:

**Rejected because**:
- **Architectural complexity**: Requires upstream server modification
- **Runtime inflexibility**: Can't change policies without server restart
- **Multiple client support**: Hard to support different policies per client
- **Proxy bypass**: Defeats the purpose of a security proxy

## Consequences

### Positive

- **Consistent Security**: Same policy controls both discovery and execution
- **Information Protection**: Clients only see tools they can actually use
- **Better User Experience**: No confusion about unavailable tools
- **Security Defense in Depth**: Multiple layers enforce the same policy
- **Clean Mental Model**: One policy, consistent enforcement

### Negative

- **Response Modification Complexity**: Requires sophisticated response filtering
- **Performance Overhead**: Additional processing for every tools/list response
- **Debugging Complexity**: Tools "disappear" from discovery, harder to troubleshoot
- **Client Assumption Breaking**: Clients might assume discovery == availability

### Risk Mitigation

1. **Comprehensive Audit Logging**: Log all filtering decisions for transparency
2. **Detailed Documentation**: Explain filtering behavior and troubleshooting
3. **Allow-All Mode**: Provide escape hatch for debugging and development
4. **Error Handling**: Graceful degradation when filtering fails

## Implementation Details

### Filtering Logic by Mode

```python
def _filter_tools_by_policy(self, tools_list: List[Dict]) -> List[Dict]:
    """Filter tools list according to current policy mode."""
    if self.mode == "allow_all":
        return tools_list
    
    filtered_tools = []
    for tool in tools_list:
        if not isinstance(tool, dict) or "name" not in tool:
            continue  # Skip malformed tools
            
        tool_name = tool["name"]
        
        if self.mode == "allowlist":
            if tool_name in self.tools:
                filtered_tools.append(tool)
        elif self.mode == "blocklist":
            if tool_name not in self.tools:
                filtered_tools.append(tool)
    
    return filtered_tools
```

### Audit Logging

```python
# Log filtering decisions for security audit
logger.info(
    f"Tool allowlist filtered tools/list response: "
    f"original={len(original_tools)} tools, filtered={len(filtered_tools)} tools, "
    f"removed={removed_tool_names}, allowed={allowed_tool_names}, "
    f"mode={self.mode}, request_id={response.id}"
)
```

### Configuration Example

```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        mode: "allowlist"
        tools:
          - "read_file"
          - "write_file"
          - "list_directory"
        # This policy now applies to BOTH:
        # 1. tools/call requests (execution control)
        # 2. tools/list responses (discovery control)
```

### Error Handling

```python
try:
    # Attempt to filter tools/list response
    filtered_tools = self._filter_tools_by_policy(tools_list)
    return create_filtered_response(response, filtered_tools)
except Exception as e:
    # Fail closed: block response if filtering fails
    return PolicyDecision(
        allowed=False,
        reason=f"Error filtering tools/list response: {str(e)}"
    )
```

This unified security model ensures that Watchgate provides consistent, comprehensive protection against both unauthorized tool execution and unauthorized tool discovery, eliminating information disclosure vulnerabilities while improving user experience.
