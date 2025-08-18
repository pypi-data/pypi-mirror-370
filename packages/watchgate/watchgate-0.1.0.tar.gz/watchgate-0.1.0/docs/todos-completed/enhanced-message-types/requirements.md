# Enhanced Message Type System

**Status**: Implemented

## Problem Statement
Plugin architecture requires enhanced MCP message types with sender metadata for improved context and JSON-RPC 2.0 compliance.

## Requirements
- MessageSender enum for distinguishing CLIENT vs SERVER message origins
- Optional sender metadata on MCPRequest and MCPResponse types
- MCPNotification message type for JSON-RPC 2.0 notification support
- Plugin interface updates to leverage sender context information
- Backward compatibility with existing message usage patterns

## Success Criteria
- [x] MessageSender enum with CLIENT and SERVER values
- [x] Enhanced MCPRequest with optional sender context
- [x] Enhanced MCPResponse with optional sender context
- [x] MCPNotification type for messages without id field
- [x] Updated plugin interfaces with sender context access
- [x] Maintains backward compatibility
- [x] Comprehensive test coverage

## Constraints
- Must maintain JSON-RPC 2.0 compliance
- Cannot break existing plugin implementations
- Optional sender metadata to avoid breaking changes
- Minimal performance impact

## Implementation Notes
- Uses dataclasses for message type definitions
- SenderContext structure for extensible metadata
- Plugin interfaces enhanced with context parameters
- Test-driven development approach used

## API Changes
New types:
- `MessageSender` enum (CLIENT, SERVER)
- `SenderContext` dataclass
- `MCPNotification` for JSON-RPC notifications

Enhanced interfaces:
- `SecurityPlugin.check_request()` - access to sender context
- `SecurityPlugin.check_response()` - takes both request and response
- `AuditingPlugin` methods - enhanced with sender context

## Configuration
No configuration changes required - enhancement is transparent.

## References
- Implementation: `watchgate/protocol/messages.py`
- Tests: `tests/unit/test_protocol_messages.py`
- Plugin interfaces: `watchgate/plugins/interfaces.py`