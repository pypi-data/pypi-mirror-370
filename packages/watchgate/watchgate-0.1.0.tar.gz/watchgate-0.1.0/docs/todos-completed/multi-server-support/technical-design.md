# Multi-Server Support Technical Design

## Overview

This document outlines the technical design for adding multiple upstream server support to Watchgate, based on analysis of existing MCP gateway implementations.

## Design Goals

1. **Consistent Architecture**: Unified behavior for all server configurations
2. **Minimal Client Changes**: MCP clients should work without modification
3. **Clean Architecture**: Extend existing patterns, don't break them
4. **Security First**: Maintain Watchgate's security model across all servers
5. **Performance**: Efficient connection management and request routing

## Configuration Design

### Chosen Approach: Flat List Configuration

Based on the analysis, we'll use a flat list structure that extends the current single-server pattern:

```yaml
# Single server (backward compatible)
upstream_server:
  command: "npx"
  args: ["-y", "@modelcontextprotocol/server-filesystem", "/"]

# Multiple servers (new)
upstream_servers:
  - name: "filesystem"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/"]
    env:
      WORKSPACE: "/home/user"
  - name: "github"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
```

### Configuration Schema Updates

```python
class ServerConfig(BaseModel):
    """Configuration for a single upstream server"""
    name: str = Field(..., description="Unique server identifier")
    command: str = Field(..., description="Command to start the server")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    
class GatewayConfig(BaseModel):
    """Updated gateway configuration"""
    # Existing fields...
    upstream_server: Optional[ServerConfigLegacy] = None  # Backward compatibility
    upstream_servers: Optional[List[ServerConfig]] = None  # New multi-server
    
    @validator('upstream_servers')
    def validate_server_config(cls, v, values):
        if v and values.get('upstream_server'):
            raise ValueError("Cannot specify both upstream_server and upstream_servers")
        return v
```

## Architecture Design

### Connection Management

Create a new `ServerManager` class to handle multiple server connections:

```python
class ServerManager:
    """Manages multiple upstream MCP server connections"""
    
    def __init__(self):
        self.servers: Dict[str, UpstreamServer] = {}
        self._lock = asyncio.Lock()
        
    async def add_server(self, config: ServerConfig) -> None:
        """Add and start a new server"""
        server = UpstreamServer(
            name=config.name,
            command=config.command,
            args=config.args,
            env=config.env
        )
        await server.start()
        self.servers[config.name] = server
        
    async def start_all(self, configs: List[ServerConfig]) -> Dict[str, Exception]:
        """Start all servers concurrently, return any errors"""
        tasks = []
        for config in configs:
            tasks.append(self.add_server(config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        errors = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors[configs[i].name] = result
        return errors
        
    async def get_server(self, name: str) -> Optional[UpstreamServer]:
        """Get a server by name"""
        return self.servers.get(name)
        
    async def shutdown_all(self) -> None:
        """Shutdown all servers gracefully"""
        tasks = [server.shutdown() for server in self.servers.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
```

### Updated UpstreamServer Class

Extend the existing `UpstreamServer` to support named instances:

```python
class UpstreamServer:
    def __init__(self, name: str = "default", command: str = None, 
                 args: List[str] = None, env: Dict[str, str] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}
        # ... existing fields ...
        
    async def list_tools(self) -> List[ToolInfo]:
        """List tools with server name prefix"""
        tools = await self._list_tools_raw()
        # Prefix tool names for multi-server mode
        return [
            ToolInfo(
                name=f"{self.name}_{tool.name}",
                description=tool.description,
                inputSchema=tool.inputSchema,
                _server_name=self.name,
                _original_name=tool.name
            )
            for tool in tools
        ]
```

### Request Routing

Implement a routing layer in the `GatewayServer`:

```python
class GatewayServer:
    def __init__(self, config: GatewayConfig):
        # ... existing init ...
        self.server_manager = ServerManager()
        self.is_multi_server = bool(config.upstream_servers)
        
    async def start(self):
        if self.is_multi_server:
            # Start multiple servers
            errors = await self.server_manager.start_all(self.config.upstream_servers)
            if errors:
                logger.warning(f"Some servers failed to start: {errors}")
        else:
            # Backward compatibility - single server
            server = UpstreamServer(name="default", ...)
            await server.start()
            self.server_manager.servers["default"] = server
            
    def _parse_tool_name(self, tool_name: str) -> Tuple[str, str]:
        """Parse server name and original tool name"""
        if self.is_multi_server and '_' in tool_name:
            parts = tool_name.split('_', 1)
            if parts[0] in self.server_manager.servers:
                return parts[0], parts[1]
        return "default", tool_name
        
    async def handle_tool_call(self, request: ToolCallRequest) -> ToolCallResponse:
        server_name, original_tool = self._parse_tool_name(request.name)
        server = await self.server_manager.get_server(server_name)
        
        if not server:
            raise ToolNotFoundError(f"Server '{server_name}' not found")
            
        # Update request with original tool name
        request.name = original_tool
        
        # Apply security plugins with server context
        context = SecurityContext(server_name=server_name, ...)
        decision = await self.plugin_manager.check_request(request, context)
        
        if not decision.allowed:
            raise SecurityViolationError(decision.reason)
            
        # Forward to appropriate server
        response = await server.call_tool(request)
        
        # Check response
        response_decision = await self.plugin_manager.check_response(
            request, response, context
        )
        
        return response
```

## Plugin Integration

Update plugin interfaces to support server context:

```python
class SecurityContext(BaseModel):
    """Extended context for multi-server support"""
    server_name: str = "default"
    # ... existing fields ...
    
class SecurityPlugin(ABC):
    async def check_request(self, request: MCPRequest, 
                           context: SecurityContext) -> PolicyDecision:
        """Check request with server context"""
        pass
```

## Tool Discovery and Registration

### Capability Aggregation

```python
async def discover_all_tools(self) -> List[types.Tool]:
    """Aggregate tools from all servers"""
    all_tools = []
    
    for server_name, server in self.server_manager.servers.items():
        try:
            tools = await server.list_tools()
            all_tools.extend(tools)
        except Exception as e:
            logger.error(f"Failed to list tools from {server_name}: {e}")
            
    return all_tools
```

### Caching Strategy

```python
class ToolCache:
    """Cache for discovered tools"""
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.ttl = ttl
        
    async def get_tools(self, server_name: str) -> Optional[List[ToolInfo]]:
        entry = self.cache.get(server_name)
        if entry and not entry.is_expired():
            return entry.tools
        return None
        
    async def set_tools(self, server_name: str, tools: List[ToolInfo]):
        self.cache[server_name] = CacheEntry(
            tools=tools,
            timestamp=time.time()
        )
```

## Error Handling

### Graceful Degradation

```python
async def start_with_fallback(self):
    """Start servers with graceful degradation"""
    if self.is_multi_server:
        errors = await self.server_manager.start_all(self.config.upstream_servers)
        
        # Check if any servers started successfully
        if len(errors) == len(self.config.upstream_servers):
            raise RuntimeError("All upstream servers failed to start")
            
        # Log warnings for failed servers
        for server_name, error in errors.items():
            logger.error(f"Server '{server_name}' failed to start: {error}")
            await self.audit_logger.log_server_failure(server_name, error)
            
        # Continue with available servers
        active_count = len(self.server_manager.servers)
        logger.info(f"Started {active_count} of {len(self.config.upstream_servers)} servers")
```

### Connection Recovery

```python
class UpstreamServer:
    async def ensure_connected(self) -> bool:
        """Ensure server is connected, attempt reconnection if needed"""
        if self.is_connected():
            return True
            
        try:
            await self.reconnect()
            return True
        except Exception as e:
            logger.error(f"Failed to reconnect to {self.name}: {e}")
            return False
```

## Migration Strategy

### Phase 1: Infrastructure (No Breaking Changes)
1. Add `ServerManager` class
2. Update `UpstreamServer` to support names
3. Add configuration schema for `upstream_servers`
4. Implement config validation and loading

### Phase 2: Core Functionality
1. Update `GatewayServer` to use `ServerManager`
2. Implement tool name prefixing
3. Add request routing logic
4. Update plugin context

### Phase 3: Enhanced Features
1. Add connection health monitoring
2. Implement tool caching
3. Add per-server metrics
4. Enhanced error handling

### Phase 4: Testing and Documentation
1. Comprehensive test suite
2. Update documentation
3. Migration guide
4. Example configurations

## Testing Strategy

### Unit Tests
- Server manager lifecycle
- Tool name parsing
- Configuration validation
- Error handling

### Integration Tests
- Multi-server startup
- Request routing
- Plugin integration
- Graceful degradation

### E2E Tests
- Real MCP servers
- Client compatibility
- Performance testing

## Security Considerations

1. **Per-Server Policies**: Allow different security rules per server
2. **Audit Logging**: Track which server handled each request
3. **Resource Isolation**: Prevent servers from affecting each other
4. **Configuration Security**: Secure handling of per-server credentials

## Performance Considerations

1. **Concurrent Operations**: Start/stop servers in parallel
2. **Connection Pooling**: Reuse connections efficiently
3. **Tool Caching**: Reduce discovery overhead
4. **Lazy Loading**: Only connect to servers when needed

## Open Questions

1. Should we support dynamic server addition/removal?
2. How to handle tool name conflicts between servers?
3. Should servers have priority/weight for load balancing?
4. How to expose server health/status to clients?