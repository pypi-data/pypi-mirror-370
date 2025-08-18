# Multi-Server Support Implementation Guide

## Overview
Implement multi-server support for Watchgate, allowing it to proxy connections to multiple MCP servers while maintaining security policies and auditing. This guide provides detailed steps for implementation.

## Critical Context
- Watchgate is a security-focused MCP gateway written in Python 3.11+ with asyncio
- Current architecture supports only one upstream server
- Must provide consistent behavior for all server configurations
- **MANDATORY**: Follow Test-Driven Development (TDD) using Red-Green-Refactor cycle
- **MANDATORY**: Run `pytest tests/` and ensure ALL tests pass before marking ANY task complete
- **MANDATORY**: Update all documentation (user, developer, ADRs) to reflect changes

## Implementation Steps

### Phase 1: Configuration Schema Updates

#### 1.1 Update Pydantic Models (`watchgate/config.py`)

Modify the configuration schema to support multiple upstreams:

```python
class UpstreamConfig(BaseModel):
    """Configuration for a single upstream MCP server"""
    name: Optional[str] = None  # Required for multi-server, optional for single
    transport: Literal["stdio", "http"] = "stdio"
    command: Optional[List[str]] = None  # For stdio transport
    args: Optional[List[str]] = None  # Deprecated, included in command
    url: Optional[HttpUrl] = None  # For http transport
    auth: Optional[AuthConfig] = None  # For http auth
    
    @model_validator(mode='after')
    def validate_transport_config(self) -> 'UpstreamConfig':
        if self.transport == "stdio" and not self.command:
            raise ValueError("stdio transport requires 'command'")
        if self.transport == "http" and not self.url:
            raise ValueError("http transport requires 'url'")
        return self

class ProxyConfig(BaseModel):
    """Updated proxy configuration"""
    transport: TransportType
    upstream: Optional[UpstreamConfig] = None  # Deprecated, for backward compat
    upstreams: Optional[List[UpstreamConfig]] = None  # New multi-server field
    
    @model_validator(mode='after')
    def validate_and_normalize_upstreams(self) -> 'ProxyConfig':
        # Handle backward compatibility
        if self.upstream and not self.upstreams:
            # Convert old single upstream to new format
            self.upstreams = [self.upstream]
            self.upstream = None
        
        if not self.upstreams:
            raise ValueError("At least one upstream server must be configured")
        
        # Validate multi-server configuration
        if len(self.upstreams) > 1:
            # All servers must have names in multi-server mode
            for i, upstream in enumerate(self.upstreams):
                if not upstream.name:
                    raise ValueError(f"Upstream server at index {i} must have a 'name' in multi-server configuration")
            
            # Names must be unique
            names = [u.name for u in self.upstreams]
            if len(names) != len(set(names)):
                raise ValueError("Upstream server names must be unique")
            
            # Names must not contain separator
            for name in names:
                if "__" in name:
                    raise ValueError(f"Server name '{name}' cannot contain '::'")
        
        return self
```

#### 1.2 Test Configuration Updates First

Create `tests/unit/test_multi_server_config.py`:

```python
import pytest
from watchgate.config import ProxyConfig, UpstreamConfig

def test_single_server_backward_compatibility():
    """Single server config should work without name field"""
    config = ProxyConfig(
        transport="stdio",
        upstream=UpstreamConfig(
            transport="stdio",
            command=["npx", "@modelcontextprotocol/server-filesystem", "/tmp"]
        )
    )
    assert len(config.upstreams) == 1
    assert config.upstreams[0].name is None

def test_multi_server_requires_names():
    """Multiple servers must all have names"""
    with pytest.raises(ValueError, match="must have a 'name'"):
        ProxyConfig(
            transport="stdio",
            upstreams=[
                UpstreamConfig(transport="stdio", command=["cmd1"]),
                UpstreamConfig(transport="stdio", command=["cmd2"])
            ]
        )

def test_server_names_must_be_unique():
    """Server names must be unique in multi-server config"""
    with pytest.raises(ValueError, match="must be unique"):
        ProxyConfig(
            transport="stdio",
            upstreams=[
                UpstreamConfig(name="fs", transport="stdio", command=["cmd1"]),
                UpstreamConfig(name="fs", transport="stdio", command=["cmd2"])
            ]
        )

def test_server_names_cannot_contain_separator():
    """Server names cannot contain :: separator"""
    with pytest.raises(ValueError, match="cannot contain '::'"):
        ProxyConfig(
            transport="stdio",
            upstreams=[
                UpstreamConfig(name="fs__bad", transport="stdio", command=["cmd"])
            ]
        )
```

### Phase 2: Server Manager Implementation

#### 2.1 Create Server Manager (`watchgate/server_manager.py`)

```python
from typing import Dict, List, Optional, Set, Tuple
import asyncio
import logging
from dataclasses import dataclass
from watchgate.config import UpstreamConfig
from watchgate.transport import StdioTransport, Transport
from mcp.types import ServerCapabilities, Tool, Resource, Prompt

logger = logging.getLogger(__name__)

@dataclass
class ServerConnection:
    """Represents a connection to an upstream MCP server"""
    name: Optional[str]
    config: UpstreamConfig
    transport: Optional[Transport] = None
    capabilities: Optional[ServerCapabilities] = None
    status: str = "disconnected"  # connected, disconnected, reconnecting
    error: Optional[str] = None

class ServerManager:
    """Manages connections to multiple upstream MCP servers"""
    
    def __init__(self, configs: List[UpstreamConfig]):
        self.configs = configs
        self.connections: Dict[Optional[str], ServerConnection] = {}
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize connection tracking for all configured servers"""
        for config in self.configs:
            self.connections[config.name] = ServerConnection(
                name=config.name,
                config=config
            )
    
    async def connect_all(self) -> Tuple[int, int]:
        """
        Connect to all configured servers.
        Returns: (successful_connections, failed_connections)
        """
        tasks = []
        for name, conn in self.connections.items():
            tasks.append(self._connect_server(conn))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        
        if successful == 0:
            logger.warning("No upstream servers connected successfully")
        elif failed > 0:
            logger.warning(f"Connected to {successful} servers, {failed} failed")
        
        return successful, failed
    
    async def _connect_server(self, conn: ServerConnection) -> bool:
        """Connect to a single server. Returns True if successful."""
        try:
            logger.info(f"Connecting to server: {conn.name or 'default'}")
            
            # Create transport based on config
            if conn.config.transport == "stdio":
                transport = StdioTransport(
                    command=conn.config.command[0],
                    args=conn.config.command[1:] if len(conn.config.command) > 1 else None
                )
            else:
                raise NotImplementedError(f"Transport {conn.config.transport} not implemented")
            
            # Connect and initialize
            await transport.connect()
            
            # Send initialize request to get capabilities
            response = await transport.send_request({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "1.0",
                    "clientInfo": {
                        "name": "watchgate",
                        "version": "0.1.0"
                    }
                },
                "id": 1
            })
            
            if "result" in response:
                conn.capabilities = response["result"].get("capabilities", {})
                conn.transport = transport
                conn.status = "connected"
                conn.error = None
                logger.info(f"Successfully connected to server: {conn.name or 'default'}")
                return True
            else:
                raise Exception(f"Invalid initialize response: {response}")
                
        except Exception as e:
            conn.status = "disconnected"
            conn.error = str(e)
            logger.error(f"Failed to connect to server {conn.name or 'default'}: {e}")
            return False
    
    async def reconnect_server(self, server_name: Optional[str]) -> bool:
        """Attempt to reconnect to a specific server"""
        conn = self.connections.get(server_name)
        if not conn:
            return False
        
        if conn.status == "connected":
            return True
        
        conn.status = "reconnecting"
        try:
            # Cleanup old transport if exists
            if conn.transport:
                await conn.transport.disconnect()
                conn.transport = None
            
            # Try to connect
            return await self._connect_server(conn)
        finally:
            if conn.status == "reconnecting":
                conn.status = "disconnected"
    
    def get_connection(self, server_name: Optional[str]) -> Optional[ServerConnection]:
        """Get connection for a specific server"""
        return self.connections.get(server_name)
    
    def get_merged_capabilities(self) -> Dict:
        """
        Merge capabilities from all connected servers.
        For multi-server: Apply namespacing to tools/resources/prompts
        For single server: Return capabilities as-is
        """
        is_multi_server = len(self.connections) > 1
        
        merged = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
        
        for name, conn in self.connections.items():
            if conn.status != "connected" or not conn.capabilities:
                continue
            
            # Tools
            if "tools" in conn.capabilities:
                for tool_name, tool_def in conn.capabilities["tools"].items():
                    key = f"{name}::{tool_name}" if is_multi_server else tool_name
                    merged["tools"][key] = tool_def
            
            # Resources  
            if "resources" in conn.capabilities:
                for resource_name, resource_def in conn.capabilities["resources"].items():
                    key = f"{name}::{resource_name}" if is_multi_server else resource_name
                    merged["resources"][key] = resource_def
            
            # Prompts
            if "prompts" in conn.capabilities:
                for prompt_name, prompt_def in conn.capabilities["prompts"].items():
                    key = f"{name}::{prompt_name}" if is_multi_server else prompt_name
                    merged["prompts"][key] = prompt_def
        
        return merged
    
    def extract_server_name(self, namespaced_name: str) -> Tuple[Optional[str], str]:
        """
        Extract server name and original name from a namespaced identifier.
        Returns: (server_name, original_name)
        """
        if "::" in namespaced_name and len(self.connections) > 1:
            parts = namespaced_name.split("::", 1)
            return parts[0], parts[1]
        return None, namespaced_name
    
    async def disconnect_all(self):
        """Disconnect from all servers"""
        tasks = []
        for conn in self.connections.values():
            if conn.transport:
                tasks.append(conn.transport.disconnect())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Reset all connections
        for conn in self.connections.values():
            conn.transport = None
            conn.status = "disconnected"
            conn.capabilities = None
```

#### 2.2 Test Server Manager

Create comprehensive tests for the ServerManager before moving forward.

### Phase 3: Update Proxy Core

#### 3.1 Modify MCPProxy (`watchgate/proxy.py`)

Update the proxy to use ServerManager:

```python
class MCPProxy:
    def __init__(self, config: Config):
        self.config = config
        self.server_manager = ServerManager(config.proxy.upstreams)
        # ... rest of init
    
    async def start(self):
        """Start the proxy server"""
        try:
            # Load plugins first
            await self._load_plugins()
            
            # Connect to all upstream servers
            successful, failed = await self.server_manager.connect_all()
            
            if successful == 0:
                # All servers failed - still start but with no capabilities
                logger.error("All upstream servers failed to connect")
            
            # Start server for client connections
            await self._start_server()
            
        except Exception as e:
            logger.error(f"Failed to start proxy: {e}")
            raise
    
    async def handle_initialize(self, request: dict) -> dict:
        """Handle initialize request from client"""
        # Get merged capabilities from all connected servers
        capabilities = self.server_manager.get_merged_capabilities()
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "1.0",
                "serverInfo": {
                    "name": "watchgate",
                    "version": "0.1.0"
                },
                "capabilities": capabilities
            }
        }
    
    async def handle_tool_call(self, request: dict) -> dict:
        """Route tool calls to appropriate server"""
        tool_name = request["params"]["name"]
        
        # Extract server name and original tool name
        server_name, original_tool_name = self.server_manager.extract_server_name(tool_name)
        
        # Get connection for this server
        conn = self.server_manager.get_connection(server_name)
        
        if not conn:
            return self._create_error_response(
                request["id"],
                -32002,  # Invalid params
                f"Unknown server in tool name: {tool_name}"
            )
        
        if conn.status != "connected":
            # Try one reconnection attempt
            if not await self.server_manager.reconnect_server(server_name):
                return self._create_error_response(
                    request["id"],
                    -32003,  # Upstream Connection Error (from ADR-004)
                    f"Server '{server_name or 'default'}' is unavailable: {conn.error or 'connection lost'}"
                )
        
        # Modify request to use original tool name
        modified_request = {
            **request,
            "params": {
                **request["params"],
                "name": original_tool_name
            }
        }
        
        try:
            # Forward to appropriate server
            response = await conn.transport.send_request(modified_request)
            return response
        except Exception as e:
            # Mark server as disconnected
            conn.status = "disconnected"
            conn.error = str(e)
            
            return self._create_error_response(
                request["id"],
                -32003,  # Upstream Connection Error
                f"Server '{server_name or 'default'}' error: {str(e)}"
            )
```

### Phase 4: Update Notification Handling

#### 4.1 Modify Notification Routing

Update the notification handler to add namespacing:

```python
async def _listen_for_upstream_notifications(self):
    """Listen for notifications from all upstream servers"""
    tasks = []
    for server_name, conn in self.server_manager.connections.items():
        if conn.status == "connected" and conn.transport:
            task = asyncio.create_task(
                self._listen_server_notifications(server_name, conn)
            )
            tasks.append(task)
    
    # Wait for all tasks (they run until cancelled)
    await asyncio.gather(*tasks, return_exceptions=True)

async def _listen_server_notifications(self, server_name: Optional[str], conn: ServerConnection):
    """Listen for notifications from a specific server"""
    is_multi_server = len(self.server_manager.connections) > 1
    
    try:
        async for notification in conn.transport.iter_notifications():
            # Apply namespacing to notification method if multi-server
            if is_multi_server and server_name:
                modified_notification = {
                    **notification,
                    "method": f"{server_name}::{notification['method']}"
                }
            else:
                modified_notification = notification
            
            # Forward to client
            await self.client_transport.send(modified_notification)
            
    except Exception as e:
        logger.error(f"Notification listener error for {server_name}: {e}")
        conn.status = "disconnected"
```

### Phase 5: Update Plugin Integration

#### 5.1 Add Server Context to Plugin Calls

Update plugin interfaces to include server context:

```python
# In SecurityPlugin.check_request
async def check_request(self, request: MCPRequest, server_name: Optional[str] = None) -> PolicyDecision:
    """Check if request should be allowed. Now includes server context."""
    # Plugins can use server_name for server-specific policies
    pass

# In proxy request handling
decision = await plugin.check_request(mcp_request, server_name)
```

### Phase 6: Integration Testing

#### 6.1 Create Integration Tests

Create comprehensive integration tests with mock MCP servers:

```python
# tests/integration/test_multi_server_integration.py

async def test_multi_server_tool_routing():
    """Test that tools are correctly routed to their servers"""
    # Start mock servers
    fs_server = MockMCPServer(tools={"read_file": {...}})
    github_server = MockMCPServer(tools={"create_issue": {...}})
    
    # Configure Watchgate
    config = {
        "proxy": {
            "transport": "stdio",
            "upstreams": [
                {"name": "fs", "command": fs_server.command},
                {"name": "github", "command": github_server.command}
            ]
        }
    }
    
    # Start proxy
    proxy = MCPProxy(config)
    await proxy.start()
    
    # Initialize client
    response = await client.initialize()
    assert "fs__read_file" in response["capabilities"]["tools"]
    assert "github__create_issue" in response["capabilities"]["tools"]
    
    # Call fs tool
    result = await client.call_tool("fs__read_file", {"path": "/tmp/test"})
    assert fs_server.received_request("tools/call")
    assert github_server.request_count == 0

async def test_server_failure_isolation():
    """Test that one server failure doesn't affect others"""
    # Test with one server that crashes
    good_server = MockMCPServer(tools={"good_tool": {...}})
    bad_server = MockMCPServer(tools={"bad_tool": {...}}, crash_after=2)
    
    # ... setup and test that good_server still works after bad_server crashes
```

## Implementation Order

1. **Day 1**: Configuration schema and tests
2. **Day 2**: ServerManager implementation and tests  
3. **Day 3**: Proxy core updates (routing, initialization)
4. **Day 4**: Notification handling and error management
5. **Day 5**: Plugin integration updates
6. **Day 6**: Integration testing and edge cases

## Key Testing Scenarios

1. **Single server backward compatibility** - Existing configs still work
2. **Multi-server tool routing** - Tools go to correct server
3. **Server failure isolation** - One failure doesn't crash proxy
4. **Graceful degradation** - Proxy starts even if some servers fail
5. **Reconnection on demand** - Failed servers can recover
6. **Clear error attribution** - Users know which server failed
7. **Notification routing** - Notifications include server source
8. **Plugin server context** - Plugins can apply per-server policies

## Common Pitfalls to Avoid

1. **Don't forget to namespace notifications** in multi-server mode
2. **Always cleanup transports** when disconnecting
3. **Handle the "no servers connected" case** gracefully
4. **Test with real MCP servers** using `npx` commands
5. **Preserve request IDs** when forwarding to upstreams
6. **Don't modify requests unnecessarily** - only change what's needed
7. **Log server names clearly** in all error messages

## Test-Driven Development Process

### TDD Red-Green-Refactor Cycle (MANDATORY)

For EVERY feature implementation:

1. **RED Phase**: Write failing tests FIRST
   - Write tests that define the expected behavior
   - Run tests to confirm they fail (if they pass, your test is wrong)
   - "No tests found" is NOT a valid RED result - fix test discovery

2. **GREEN Phase**: Write minimal code to pass
   - Implement ONLY enough code to make tests pass
   - No extra features or "nice to have" code
   - Run tests to confirm they pass

3. **REFACTOR Phase**: Improve code quality
   - Clean up implementation while keeping tests green
   - Extract common patterns
   - Add type hints and documentation
   - Run tests after each change to ensure they still pass

### Example TDD Flow

```bash
# 1. RED: Write failing test
vim tests/unit/test_multi_server_config.py  # Write test
pytest tests/unit/test_multi_server_config.py -v  # Confirm it fails

# 2. GREEN: Implement minimal code
vim watchgate/config.py  # Add just enough code
pytest tests/unit/test_multi_server_config.py -v  # Confirm it passes

# 3. REFACTOR: Improve code
vim watchgate/config.py  # Clean up, add types
pytest tests/  # Run ALL tests to ensure nothing broke
```

## Documentation Updates Required

### 1. User Documentation
- **README.md**: Add multi-server configuration examples
- **docs/getting-started.md**: Update with multi-server setup
- **docs/configuration.md**: Document new `upstreams` field and namespacing

### 2. Developer Documentation  
- **docs/development/architecture.md**: Update proxy architecture diagram
- **docs/development/plugin-development.md**: Document server context in plugins
- **CHANGELOG.md**: Document breaking changes and new features

### 3. Architecture Decision Records (ADRs)
Create new ADR: **docs/decision-records/014-multi-server-support.md**
```markdown
# ADR-014: Multi-Server Support Architecture

## Status
Accepted

## Context
[Explain why we need multi-server support]

## Decision
- Tool namespacing with :: separator
- Graceful degradation on server failures
- Simple reconnection on demand
- Server isolation for reliability

## Consequences
[Document impacts on existing functionality]
```

### 4. Configuration Examples
Update **docs/examples/configurations/**:
- Add `multi-server-basic.yaml`
- Add `multi-server-advanced.yaml`
- Update existing examples with deprecation notes

## Success Criteria

- [ ] All existing single-server tests pass (backward compatibility)
- [ ] Multi-server configuration works with real MCP servers
- [ ] Server failures are isolated and clearly reported
- [ ] Tool/notification namespacing works correctly
- [ ] Performance is acceptable with multiple servers
- [ ] All new code has >90% test coverage
- [ ] `pytest tests/` passes with no warnings
- [ ] All documentation updated to reflect changes
- [ ] New ADR created for multi-server architecture
- [ ] TDD process followed for all implementations

## Questions During Implementation

If you encounter these scenarios, here's what to do:

1. **Circular imports**: Use TYPE_CHECKING imports and string annotations
2. **Async context managers**: Prefer `async with` for transport lifecycle
3. **Configuration edge cases**: Add validation in the Pydantic model
4. **Performance concerns**: Profile first, optimize later
5. **Plugin compatibility**: Maintain backward compatibility by making server_name optional

Remember: **Write tests first**, run `pytest tests/` frequently, and ensure all tests pass before considering any task complete.