# MCP 2025-06-18 Specification Support

## Overview
Update Watchgate to fully support the Model Context Protocol (MCP) specification version 2025-06-18. This includes implementing new features, updating existing implementations, and ensuring security compliance with the latest specification requirements.

## Requirements

### 1. Protocol Version Updates
- [x] Update hardcoded protocol version from "2024-11-05" to "2025-06-18" in proxy/server.py
- [ ] Add protocol version negotiation support
- [ ] Implement version compatibility checking between client and server versions
- [ ] Document supported MCP specification versions

### 2. New Feature: Elicitation
The 2025-06-18 spec introduces "Elicitation" - server-initiated requests for additional information from users.

- [ ] Research full Elicitation specification details (message formats, flow)
- [ ] Implement Elicitation message handling in proxy layer
- [ ] Add security plugin hooks for Elicitation requests
- [ ] Create audit logging for Elicitation interactions
- [ ] Add configuration options to enable/disable Elicitation support
- [ ] Document security implications of server-initiated user requests

### 3. Enhanced Sampling Support
The specification emphasizes user control over LLM sampling with explicit approval requirements.

- [ ] Implement `sampling/createMessage` method handling
- [ ] Add user consent verification for sampling requests
- [ ] Implement prompt visibility controls as per spec
- [ ] Add result filtering capabilities for sampling responses
- [ ] Create security plugins for sampling approval workflow
- [ ] Document sampling security model

### 4. Additional MCP Methods
Implement support for MCP methods not currently handled:

- [ ] `ping` - Health check support
- [ ] `logging/setLevel` - Dynamic log level control
- [ ] `completion/complete` - Completion support
- [ ] Add method validation against MCP specification
- [ ] Implement proper error responses for unsupported methods

### 5. Security Enhancements
Align with the expanded security principles in the 2025-06-18 specification:

- [ ] Review and update security documentation
- [ ] Implement enhanced consent flows for sensitive operations
- [ ] Add data privacy protections as per spec recommendations
- [ ] Update tool safety controls
- [ ] Document security best practices for MCP 2025-06-18

### 6. Testing Requirements
- [ ] Create unit tests for all new message types
- [ ] Add integration tests for Elicitation flow
- [ ] Test protocol version negotiation
- [ ] Create security tests for sampling approval
- [ ] Test backward compatibility with older MCP servers
- [ ] Add tests for new error scenarios

### 7. Documentation Updates
- [ ] Update ADRs with decisions about new features
- [ ] Document Elicitation security model
- [ ] Create examples for new message types
- [ ] Update configuration documentation
- [ ] Add migration guide from older MCP versions

## Implementation Strategy

1. **Phase 1: Research & Design**
   - Deep dive into MCP 2025-06-18 specification
   - Design security model for new features
   - Create ADRs for architectural decisions

2. **Phase 2: Core Implementation**
   - Implement new message handlers
   - Add security plugin interfaces
   - Update proxy message routing

3. **Phase 3: Security & Auditing**
   - Implement consent flows
   - Add audit logging
   - Create security plugins

4. **Phase 4: Testing & Documentation**
   - Comprehensive testing
   - Documentation updates
   - Example configurations

## Security Considerations

### Elicitation Risks
- Server-initiated requests could be used for social engineering
- Need strict controls on what information servers can request
- Must maintain user agency and consent

### Sampling Risks
- Recursive LLM interactions need careful control
- Prompt visibility must be managed to prevent leakage
- Result filtering critical for preventing data exfiltration

## Success Criteria
- All tests pass with new MCP 2025-06-18 features
- Security controls properly enforce consent requirements
- Backward compatibility maintained with older MCP servers
- Comprehensive documentation for new features
- No regression in existing functionality

## References
- [MCP Specification 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18)
- Current implementation: `watchgate/proxy/server.py`
- Security plugins: `watchgate/plugins/security/`