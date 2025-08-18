# MCP Gateway Projects Analysis: Multiple Server Support

## Overview

I analyzed 4 MCP gateway projects to understand their approaches to handling multiple server connections:

1. **mcp-gateway** - Python-based plugin gateway
2. **ms-mcp-gateway** - Microsoft's .NET-based Kubernetes gateway
3. **secure-mcp-gateway** - EnkryptAI's security-focused gateway
4. **mcp-defender** - Desktop app proxy with security scanning

## Architecture Comparison

### 1. mcp-gateway (Python)

**Architecture**: Plugin-based gateway that dynamically registers tools/prompts from multiple servers

**Key Features**:
- **True Proxy**: Acts as an MCP server to clients while proxying to multiple upstream MCP servers
- **Dynamic Registration**: Discovers and registers capabilities from all proxied servers at startup
- **Unified Interface**: Presents all server tools/prompts with prefixed names (e.g., `servername_toolname`)
- **Plugin System**: Supports guardrails and tracing plugins for security/monitoring

**Multi-Server Approach**:
```python
# Config structure (nested under gateway's own config)
{
  "mcpServers": {
    "mcp-gateway": {
      "command": "mcp-gateway",
      "args": [...],
      "servers": {
        "filesystem": { "command": "npx", "args": [...] },
        "github": { "command": "npx", "args": [...] }
      }
    }
  }
}
```

**Connection Management**:
- Creates `Server` instances for each configured server
- Manages lifecycle with `AsyncExitStack` for proper cleanup
- Starts all servers concurrently during lifespan
- Maintains active `ClientSession` for each server
- Caches capabilities (tools, resources, prompts) at startup

**Request Routing**:
- Tools/prompts are prefixed with server name (e.g., `filesystem_read_file`)
- Gateway handles the routing internally based on the prefix
- Sanitizes requests/responses through plugin system

### 2. ms-mcp-gateway (.NET/Kubernetes)

**Architecture**: Enterprise-grade reverse proxy with Kubernetes deployment

**Key Features**:
- **NOT a True MCP Gateway**: HTTP reverse proxy that routes to MCP servers in Kubernetes
- **Control Plane**: RESTful APIs for server lifecycle management
- **Data Plane**: Session-aware stateful routing
- **Kubernetes Native**: Uses StatefulSets and headless services

**Multi-Server Approach**:
```csharp
// Servers are "adapters" managed via REST API
POST /adapters
{
  "name": "mcp-example",
  "imageName": "mcp-example",
  "imageVersion": "1.0.0"
}
```

**Connection Management**:
- Servers run as Kubernetes pods
- Gateway doesn't maintain MCP connections - it's HTTP routing
- Session affinity ensures requests route to same pod

**Request Routing**:
- URL-based routing: `/adapters/{name}/sse`, `/adapters/{name}/mcp`
- Distributed session store for stateful routing
- No tool/capability discovery - pure HTTP proxy

### 3. secure-mcp-gateway (Python)

**Architecture**: Security-focused gateway with remote configuration support

**Key Features**:
- **True Proxy**: Similar to mcp-gateway, acts as MCP server to clients
- **Remote Config**: Can fetch server configurations from API
- **Guardrails**: Input/output content filtering and PII protection
- **Caching**: External cache support for tools and configurations

**Multi-Server Approach**:
```python
# Config can be local or remote
gateway_config = {
  "mcp_config": [
    {
      "server_name": "filesystem",
      "command": "npx",
      "args": [...],
      "tools": {}  # Can be pre-configured or discovered
    }
  ]
}
```

**Connection Management**:
- Similar to mcp-gateway - creates client sessions to servers
- Supports tool discovery and caching
- Handles authentication via gateway key

**Request Routing**:
- Tools are called with server name context
- Supports async guardrails for request/response filtering
- Integrates with external APIs for security checks

### 4. mcp-defender (TypeScript/Electron)

**Architecture**: Desktop app that intercepts MCP traffic between apps and servers

**Key Features**:
- **Intercepting Proxy**: Sits between MCP clients (Cursor, Claude) and servers
- **Security Scanning**: Checks requests/responses against threat signatures
- **Multi-Transport**: Supports SSE and streamable HTTP
- **Per-App Configuration**: Different server configs per application

**Multi-Server Approach**:
```typescript
// Servers organized by application
state.protectedServers = new Map<string, ProtectedServerConfig[]>()
// e.g., "Cursor" -> [filesystem_server, github_server, ...]
```

**Connection Management**:
- Maintains SSE connections map by connection ID
- Tracks pending tool calls awaiting responses
- Doesn't create upstream connections - modifies proxy URLs

**Request Routing**:
- URL pattern: `/{appName}/{serverName}/sse`
- Extracts app/server from URL path
- Routes based on URL structure, not tool names

## Key Patterns for Watchgate

### 1. Configuration Structure

**Option A: Nested (like mcp-gateway)**
```yaml
upstream_server:
  command: "watchgate"
  args: ["--config", "multi-server.yaml"]
  servers:
    filesystem:
      command: "npx"
      args: ["@modelcontextprotocol/server-filesystem", "/"]
```

**Option B: Flat List (like secure-mcp-gateway)**
```yaml
servers:
  - name: filesystem
    command: "npx"
    args: ["@modelcontextprotocol/server-filesystem", "/"]
  - name: github
    command: "npx"
    args: ["@modelcontextprotocol/server-github"]
```

### 2. Connection Management Patterns

**Concurrent Startup** (mcp-gateway style):
```python
async def start_all_servers():
    tasks = [server.start() for server in servers.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Handle failed servers gracefully
```

**Lifecycle Management**:
- Use context managers for clean shutdown
- Track server health/status
- Support reconnection on failure

### 3. Request Routing Strategies

**Tool Prefixing** (mcp-gateway):
- Pros: Simple, no ambiguity
- Cons: Changes tool names from client perspective

**URL-Based** (mcp-defender):
- Pros: Clean separation, original tool names
- Cons: Requires client configuration changes

**Header-Based**:
- Pros: Transparent to clients
- Cons: Requires client support

### 4. Capability Management

**Static Registration**:
- Pre-configure all tools in config
- No discovery needed

**Dynamic Discovery**:
- Query servers at startup
- Cache capabilities
- Handle capability changes

## Recommendations for Watchgate

1. **Use Flat Configuration** - Simpler than nested, aligns with current pattern
2. **Implement Tool Prefixing** - Most compatible with existing MCP clients
3. **Support Both Modes**:
   - Single server (current behavior)
   - Multi-server with prefixed tools
4. **Async Connection Management** - Start servers concurrently
5. **Graceful Degradation** - Continue if some servers fail
6. **Consider Caching** - Cache tool lists to improve startup time

## Security Considerations

- Each project handles authentication differently
- Plugin/guardrail systems provide security layers
- Consider per-server security policies
- Audit logging becomes more complex with multiple servers