# Puppeteer Validation Migration

## Overview
Migrate Watchgate's validation testing from fetch MCP server to Puppeteer MCP server to enable real-world browser automation testing scenarios. The current fetch server conflicts with Claude Desktop's built-in fetch capabilities, potentially bypassing Watchgate security controls during validation.

## Problem Statement
The current validation guide uses `mcp-server-fetch` for testing scenarios with multiple servers, but Claude Desktop has built-in web fetching capabilities that take precedence over MCP server tools with the same name. This means validation tests may not actually be going through Watchgate's security controls, undermining the effectiveness of the validation process.

## Requirements

### 1. Configuration Updates
- [ ] Update `tests/validation/test-config.yaml` to replace fetch server with Puppeteer
- [ ] Update `tests/validation/test-config-single.yaml` if needed for one-server testing
- [ ] Modify tool allowlists to include Puppeteer tools instead of fetch tools
- [ ] Update logging configurations to handle Puppeteer-specific operations

**Current fetch server configuration:**
```yaml
- name: "fetch"
  command: "/Users/dbright/.local/bin/uvx mcp-server-fetch"
```

**Target Puppeteer configuration:**
```yaml
- name: "puppeteer"
  command: "npx -y @modelcontextprotocol/server-puppeteer"
```

### 2. Installation Instructions Update
- [ ] Replace fetch server installation with Puppeteer installation
- [ ] Update verification commands to test Puppeteer functionality
- [ ] Add browser dependency requirements (Chrome/Chromium)
- [ ] Document npx usage for dependency-free installation

**Current:**
```bash
uvx mcp-server-fetch --help
```

**Target:**
```bash
npx -y @modelcontextprotocol/server-puppeteer --help
```

### 3. Tool Allowlist Migration
- [ ] Research available Puppeteer MCP server tools
- [ ] Update security plugin configurations to allow appropriate Puppeteer tools
- [ ] Design blocked tool scenarios for access control testing

**Current fetch tools:**
- `fetch` - HTTP requests

**Target Puppeteer tools (to be confirmed):**
- `puppeteer_navigate` - Navigate to URLs
- `puppeteer_screenshot` - Capture screenshots
- `puppeteer_click` - Click elements
- `puppeteer_type` - Type into forms
- `puppeteer_evaluate` - Execute JavaScript (potentially blocked)

### 4. Validation Scenarios Redesign

#### 4.1 Multi-Server Tool Access Control
- [ ] **Allowed Operations**: Navigation to websites, screenshot capture, basic element interaction
- [ ] **Blocked Operations**: Dangerous JavaScript execution, file system access through browser
- [ ] **Cross-Server Operations**: Simultaneous browser automation and file operations

#### 4.2 PII Filter Testing (Redact Mode)
- [ ] **Screenshot Testing**: Navigate to pages with contact information, verify PII redaction in screenshots
- [ ] **Form Interaction**: Fill forms with PII data, verify redaction in request parameters
- [ ] **Content Extraction**: Extract text from pages containing PII, verify redaction in responses
- [ ] **Cross-Server PII**: Browser automation that writes PII to files, verify redaction in both directions

#### 4.3 Secrets Filter Testing (Block Mode)
- [ ] **Repository Navigation**: Navigate to GitHub repos with example API keys, verify blocking
- [ ] **Documentation Screenshots**: Screenshot API docs with example keys, verify blocking
- [ ] **JavaScript Execution**: Execute scripts that expose environment variables, verify blocking
- [ ] **Form Submission**: Submit forms with API keys, verify blocking before submission

#### 4.4 Prompt Injection Defense Testing (Block Mode)
- [ ] **Malicious URLs**: Navigate to URLs with injection attempts in query parameters
- [ ] **JavaScript Injection**: Execute JavaScript with prompt injection content
- [ ] **Form Injection**: Fill forms with injection attempts, verify blocking
- [ ] **Page Content**: Navigate to pages with injection patterns, verify blocking

#### 4.5 Concurrent Operations Testing
- [ ] **Browser + File Operations**: Simultaneous navigation and file system operations
- [ ] **Multiple Screenshots**: Concurrent screenshot operations
- [ ] **Cross-Server Workflows**: Browser automation results feeding into file operations

### 5. Test Website Strategy
- [ ] **Reliable Test Sites**: httpbin.org (for testing), example.com, placeholder sites
- [ ] **Local HTML Files**: Create custom pages with specific PII/secrets content for controlled testing
- [ ] **Public Demo Sites**: Contact forms, documentation sites with realistic content
- [ ] **Fallback Strategy**: Handle network failures gracefully with local alternatives

### 6. Expected Behavior Documentation
- [ ] Update expected behaviors for visual content testing
- [ ] Document browser automation timing considerations
- [ ] Add troubleshooting for headless browser issues
- [ ] Update time estimates for validation process (browser automation is slower)

### 7. Validation Guide Updates
- [ ] Rewrite Part 1 (Setup) for Puppeteer installation
- [ ] Update Part 2 (Configuration) with new tool allowlists
- [ ] Completely rewrite Part 3 (Security Testing) with browser automation scenarios
- [ ] Update Part 4 (Auditing) with Puppeteer-specific log examples
- [ ] Modify Part 5 (Error Scenarios) for browser automation errors
- [ ] Update Part 6 (Error Communication) with Puppeteer-specific error cases

## Implementation Strategy

### Phase 1: Research & Design
1. **Tool Discovery**: Research exact Puppeteer MCP server tool names and capabilities
2. **Test Site Planning**: Identify and create test websites/pages for validation scenarios
3. **Configuration Design**: Plan exact configuration changes needed
4. **Scenario Mapping**: Map each current fetch scenario to equivalent Puppeteer scenario

### Phase 2: Configuration Updates
1. **Update Config Files**: Modify test-config.yaml
2. **Tool Allowlists**: Update security plugin configurations
3. **Logging Configuration**: Ensure Puppeteer operations are properly logged

### Phase 3: Documentation Rewrite
1. **Installation Instructions**: Update setup procedures
2. **Validation Scenarios**: Rewrite all test scenarios for browser automation
3. **Expected Behaviors**: Document new expected outcomes
4. **Troubleshooting**: Add browser-specific troubleshooting

### Phase 4: Testing & Validation
1. **End-to-End Testing**: Run complete validation flow with Puppeteer
2. **Security Verification**: Confirm all security plugins work with browser automation
3. **Performance Testing**: Verify acceptable validation runtime
4. **Documentation Review**: Ensure all documentation is accurate and complete

## Technical Considerations

### Browser Dependencies
- **Chrome/Chromium**: Puppeteer requires Chrome/Chromium browser
- **Headless Mode**: Default to headless for validation, provide debugging options
- **Network Access**: Browser automation requires internet connectivity
- **Performance**: Browser automation is significantly slower than HTTP requests

### Security Implications
- **JavaScript Execution**: Puppeteer can execute arbitrary JavaScript - security risk
- **File System Access**: Browser may have file system access capabilities
- **Network Requests**: Browser makes actual HTTP requests, bypassing some controls
- **Visual Content**: Screenshots may contain sensitive information

### Reliability Concerns
- **Network Dependencies**: External websites may be unreliable
- **Timing Issues**: Browser automation has timing sensitivities
- **Browser Crashes**: Headless browsers can crash or hang
- **Version Compatibility**: Browser version dependencies

## Success Criteria

### Functional Requirements
- [ ] All current validation scenarios have equivalent Puppeteer implementations
- [ ] Security plugins correctly filter browser automation operations
- [ ] Multi-server testing validates both filesystem and browser automation
- [ ] Audit logging captures all browser automation activities
- [ ] Error handling gracefully manages browser automation failures

### Quality Requirements
- [ ] Validation remains reliable and reproducible
- [ ] Documentation is clear and comprehensive
- [ ] Setup process is straightforward for new users
- [ ] Performance is acceptable for regular validation use
- [ ] Real-world use cases are properly tested

### Security Requirements
- [ ] All security controls work correctly with browser automation
- [ ] PII redaction works with visual content (screenshots)
- [ ] Secrets detection works with dynamic web content
- [ ] Prompt injection defense works with URL parameters and JavaScript
- [ ] Access control properly limits dangerous browser operations

## Constraints & Limitations

### Technical Constraints
- **Browser Requirements**: Users must have Chrome/Chromium installed
- **Network Dependency**: Requires internet access for external test sites
- **Performance Impact**: Browser automation significantly slower than HTTP requests
- **Platform Differences**: Browser behavior may vary across operating systems

### Testing Limitations
- **Dynamic Content**: Web pages change, making some tests non-deterministic
- **External Dependencies**: Test sites may be unavailable or change
- **Timing Sensitivity**: Browser automation has inherent timing issues
- **Visual Testing**: Screenshot comparison is complex and fragile

## Migration Timeline

### Immediate (Week 1)
- Research Puppeteer MCP server capabilities
- Design test website strategy
- Create configuration changes

### Short-term (Week 2-3)
- Update configuration files
- Rewrite validation scenarios
- Create test HTML pages

### Medium-term (Week 4-5)
- Update documentation
- End-to-end testing
- Performance optimization

### Long-term (Week 6+)
- User feedback integration
- Additional scenario development
- Maintenance and updates

## References
- [Puppeteer MCP Server Documentation](https://www.npmjs.com/package/@modelcontextprotocol/server-puppeteer)
- [Current Validation Guide](../validation/quick-validation-guide.md)
- [Current Multi-Server Config](../validation/test-config.yaml)
- [Puppeteer Documentation](https://pptr.dev/)
- [MCP Specification](https://modelcontextprotocol.io/)

## Risk Assessment

### High Risk
- **Test Reliability**: Browser automation is inherently less reliable than HTTP requests
- **Setup Complexity**: Browser dependencies increase setup complexity
- **Performance Impact**: Validation time may increase significantly

### Medium Risk
- **Network Dependencies**: External test sites may become unavailable
- **Security Gaps**: New attack vectors through browser automation
- **Maintenance Burden**: More complex test scenarios require more maintenance

### Low Risk
- **User Adoption**: Most users already have browsers installed
- **Compatibility**: npx approach minimizes compatibility issues
- **Documentation**: Clear documentation can mitigate complexity

## Mitigation Strategies

### Reliability Mitigation
- **Local Test Pages**: Create local HTML files for critical test scenarios
- **Fallback Sites**: Multiple test sites for each scenario
- **Retry Logic**: Implement retry mechanisms for flaky operations
- **Timeout Handling**: Proper timeout configuration for browser operations

### Performance Mitigation
- **Parallel Operations**: Run browser operations in parallel where possible
- **Selective Testing**: Allow running subsets of validation tests
- **Caching**: Cache browser instances between operations
- **Optimization**: Optimize browser automation for speed

### Security Mitigation
- **Sandboxing**: Ensure browser runs in secure sandbox
- **Permission Limits**: Limit browser permissions and capabilities
- **Content Filtering**: Filter dangerous content before browser processing
- **Audit Trail**: Comprehensive logging of all browser operations