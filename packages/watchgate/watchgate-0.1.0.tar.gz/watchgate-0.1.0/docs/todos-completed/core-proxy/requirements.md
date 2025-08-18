# MCP Gateway Server

**Status**: Implemented

## Problem Statement
Need a proxy server to intercept and forward MCP communications between clients and servers, enabling security and auditing functionality.

## Requirements
- Accept MCP client connections (JSON-RPC over stdio)
- Forward requests to single upstream MCP server
- Maintain protocol compatibility with MCP specification
- Handle basic connection lifecycle (initialization, requests, cleanup)
- Enhanced message forwarding with sender context for plugins
- Integrate with plugin pipeline for security and auditing

## Success Criteria
- [x] Accepts MCP client connections via stdio
- [x] Successfully forwards requests to upstream server
- [x] Maintains MCP protocol compatibility
- [x] Handles connection lifecycle properly
- [x] Provides sender context to plugins
- [x] Integrates with security and auditing plugins
- [x] Handles basic error conditions gracefully

## Constraints
- stdio transport only for v0.1.0
- One or more upstream servers supported
- Plugin pipeline must not introduce significant latency

## Implementation Notes
- Built using asyncio for concurrent operation
- Uses custom WriteProtocol for stream handling
- Plugin pipeline processes requests/responses sequentially
- Maintains message sender context throughout pipeline

## Configuration
```yaml
upstream:
  command: "python my_mcp_server"  # or ["python", "my_mcp_server.py"]
```

## References
- Implementation: `watchgate/proxy/stdio_server.py`
- Tests: `tests/integration/test_proxy_integration.py`
- Transport: `watchgate/transport/stdio.py`