# Multi-Server Support Requirements

## Overview
Watchgate needs to support connecting to multiple different MCP servers (e.g., filesystem, GitHub, JIRA) through a single proxy instance. This will allow clients to access multiple services while maintaining centralized security policies and auditing.

## Core Requirements

### 1. Configuration Structure
- Support multiple upstream servers in configuration
- Each server must have:
  - Unique name/identifier (required for all servers)
  - Transport type (stdio or http)
  - Connection details (command for stdio, URL for http)
  - Optional server-specific configuration
- The top-level `transport` defines how clients connect to Watchgate
- Each upstream can use a different transport mechanism
- Name field requirements:
  - **Required** when configuring multiple upstream servers
  - **Optional** when configuring only one upstream server
  - Used to identify servers in tool calls and plugin overrides
- Example structures:

  **Multiple servers (name required):**
  ```yaml
  proxy:
    transport: stdio  # How clients connect to Watchgate
    upstreams:
      - name: filesystem  # Your choice - used to identify this server
        transport: stdio
        command: ["npx", "@modelcontextprotocol/server-filesystem", "/path"]
      - name: github  # Your choice - used to identify this server
        transport: stdio
        command: ["npx", "@modelcontextprotocol/server-github"]
      - name: remote-api  # Your choice - used to identify this server
        transport: http
        url: "https://api.example.com/mcp"
        auth:
          type: bearer
          token: "${REMOTE_API_TOKEN}"
  ```

  **Single server (name optional):**
  ```yaml
  proxy:
    transport: stdio
    upstreams:
      - command: ["npx", "@modelcontextprotocol/server-filesystem", "/path"]
        # No name needed when using just one server
  ```

### 2. Client Transparency
- Clients SHOULD be aware they're connected to multiple servers
- Server information should be exposed in responses where appropriate
- Error messages should identify which server failed
- Initialize response should indicate which capabilities come from which server

### 3. Tool Namespacing
- Automatic namespacing to handle conflicts between servers
- Format: `{server_name}__{tool_name}` (e.g., `github__create_repository`)
- Single server configuration: No namespacing applied
- Multiple server configuration: All tools are namespaced with their server name
- Tools unique to one server can optionally be accessed without namespace
- Namespace separator: Use double underscore (`__`), following MCP spec compliance

### 4. Routing
- Simple routing based on tool namespace
- Extract server identifier from tool name
- Route request to appropriate upstream server
- Track which request went to which server for response correlation

### 5. Connection Management
- Eager connection: Connect to all configured servers at startup
- Maintain separate transport instance for each server
- Handle individual server failures gracefully
- Support different connection parameters per server
- Graceful degradation: If some servers fail to connect at startup, continue operating with available servers
- Log clear warnings for failed connections but don't fail the entire proxy startup
- Mark failed servers as unavailable and return appropriate errors for requests to those servers

### 6. Initialize Handling
- Query each upstream server for capabilities during startup
- Merge capabilities from all servers
- Send standard MCP initialize response with merged capabilities
- For one server: Pass through capabilities unchanged (no namespacing)
- For multiple servers: Server information is implicit in the namespaced tool/resource names
- Example response structures:

  **Single server (no namespacing):**
  ```json
  {
    "protocolVersion": "1.0",
    "capabilities": {
      "tools": {
        "read_file": { /* tool definition */ },
        "write_file": { /* tool definition */ }
      },
      "resources": {
        "file": { /* resource definition */ }
      }
    }
  }
  ```

  **Multiple servers (with namespacing):**
  ```json
  {
    "protocolVersion": "1.0",
    "capabilities": {
      "tools": {
        "filesystem__read_file": { /* tool definition */ },
        "filesystem__write_file": { /* tool definition */ },
        "github__create_repository": { /* tool definition */ }
      },
      "resources": {
        "filesystem__file": { /* resource definition */ },
        "github__repository": { /* resource definition */ }
      }
    }
  }
  ```

### 7. Error Handling
- Include server identification in error responses
- Clear error messages indicating which server failed
- Handle partial failures (some servers down)
- Don't fail startup if optional servers are unavailable

### 8. Plugin Integration
- Plugins receive server context in requests/responses
- Support both global and server-specific plugin configuration
- Server-specific plugins supplement or override global plugins
- Audit logs include server identification
- Example configuration:
  ```yaml
  plugins:
    # Global plugins apply to all servers
    security:
      - policy: "rate_limiting"
        enabled: true
        
    # Server-specific plugin overrides
    upstream-overrides:
      github:  # Must match the name you chose in upstreams config
        security:
          - policy: "github_token_validation"
            enabled: true
      filesystem:  # Must match the name you chose in upstreams config
        security:
          - policy: "path_restrictions"
            enabled: true
            config:
              allowed_paths: ["/safe/directory"]
  ```

### 9. Request/Response Processing
- Modify request processing pipeline to:
  1. Identify target server from tool name
  2. Apply global security plugins
  3. Apply server-specific security plugins
  4. Route to appropriate upstream
  5. Apply response filtering
  6. Include server attribution in audit logs

### 10. Notification Handling
- Server-initiated notifications must be attributed to their source server
- Use method name namespacing for notifications (same pattern as tools)
- Format: `{server_name}__{notification_method}` (e.g., `filesystem__notifications/resources/updated`)
- Single server configuration: No namespacing applied to notifications
- Multiple server configuration: All notification methods are namespaced
- This ensures clients can identify which server sent a notification
- Maintains consistency with tool namespacing approach

### 11. State Management
- Maintain per-server state (connection status, capabilities)
- Handle stateful operations (like resource subscriptions) per server
- Track server health and availability

### 12. Connection State Synchronization

**Simple approach for v1 - Isolated Failure Handling:**

1. **Server Isolation**: Each server connection fails independently
   - If one server crashes, others continue working
   - Watchgate itself never crashes due to upstream failures

2. **Clear Error Attribution**: When a server is down, return errors that identify the failed server
   - Error format: `Server 'filesystem' is unavailable: connection lost`
   - Include server name in all connection-related errors
   - Users can clearly see which server is the problem

3. **Simple Reconnection** (optional for v1):
   - When a request comes in for a disconnected server:
     - Check if transport is still connected
     - If not, attempt ONE reconnection
     - If reconnection fails, return clear error
   - No complex retry logic or exponential backoff
   - No background reconnection attempts

4. **Connection Status Tracking**:
   - Track each server's status: `connected`, `disconnected`, `reconnecting`
   - Log server status changes prominently
   - Consider exposing server health in a future version

5. **In-flight Request Handling**:
   - Requests in progress when server disconnects get connection error
   - No request queuing or replay
   - Clean up pending requests properly to avoid hangs

**Benefits**:
- Watchgate stays reliable even with flaky upstream servers
- Users can identify problematic servers
- Simple enough to implement correctly in v1
- Can be enhanced in future versions

## Implementation Phases

### Phase 1: Core Multi-Server Support
- Configuration schema updates
- Multiple transport management
- Basic routing by tool namespace
- Initialize response merging

### Phase 2: Plugin Integration
- Server context in plugin interfaces
- Server-specific plugin configuration
- Updated audit logging

### Phase 3: Advanced Features
- Health monitoring per server
- Dynamic server management (future)
- Optimized request batching per server

## Open Questions for Implementation

1. **Tool Name Conflicts**: Double underscore (`__`) separator should handle most conflicts, but monitor for edge cases in practice
2. **Protocol Version Mismatch**: How to handle if servers support different MCP protocol versions?
3. **Optional vs Required Servers**: Should we support marking servers as optional (don't fail startup if unavailable)?
4. **Resource Subscriptions**: How to handle stateful subscriptions that are server-specific?
5. **Performance**: Should we implement request queuing per server to prevent one slow server from blocking others?

## Success Criteria

1. Watchgate can connect to multiple MCP servers simultaneously
2. Clients can access tools from all connected servers through one Watchgate instance
3. Tool naming conflicts are automatically resolved
4. Security policies can be applied globally or per-server
5. Audit logs clearly identify which server handled each request
6. Server failures are isolated and don't affect other servers
7. Existing plugin functionality continues to work with server context

## Security Considerations

1. Each server connection should be isolated
2. Server-specific credentials should be supported
3. Plugins must be able to apply different policies per server
4. Audit trails must maintain clear server attribution
5. Error messages should not leak sensitive server configuration

## Testing Requirements

1. Unit tests for multi-server configuration parsing
2. Unit tests for routing logic
3. Integration tests with multiple mock MCP servers
4. Tests for conflict resolution and namespacing
5. Tests for partial server failures
6. Plugin compatibility tests
7. Performance tests with multiple concurrent requests to different servers