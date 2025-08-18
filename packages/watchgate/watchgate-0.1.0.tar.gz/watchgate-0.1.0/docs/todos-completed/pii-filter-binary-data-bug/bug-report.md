# PII Filter Binary Data Corruption Bug Report

## Priority: HIGH - Critical Functionality Broken

## Executive Summary
The PII filter plugin is incorrectly scanning and redacting base64-encoded binary image data for PII patterns, which corrupts the data and causes tool responses to fail. This breaks screenshot functionality and potentially any other tool that returns binary data encoded as base64.

## Bug Description
The PII filter plugin treats all string content as plain text and scans it for PII patterns, including base64-encoded binary data. When PII-like patterns are found within base64 image data, they are replaced with redaction text (e.g., `[PHONE REDACTED by Watchgate]`), which corrupts the base64 encoding and renders the data invalid.

## Evidence from Logs
During validation testing with the Puppeteer screenshot tool:

1. **Tool Response**: Puppeteer screenshot tool returned base64-encoded PNG image data
2. **PII Filter Action**: The filter detected phone number patterns within the base64 data string
3. **Redaction Applied**: Replaced detected patterns with `[PHONE REDACTED by Watchgate]`
4. **Result**: Corrupted base64 encoding caused Claude Desktop connection errors

Example of corrupted base64 data:
```
Original: iVBORw0KGgoAAAANSUhEUgAA...
Corrupted: iVBORw0KGgoAAAANSUhEUgAA[PHONE REDACTED by Watchgate]...
```

## Impact Assessment

### Immediate Impact
- **Screenshot Tools**: Puppeteer and similar tools fail to return valid image data
- **Binary Data Tools**: Any tool returning base64-encoded binary data is affected
- **Validation Testing**: Current validation efforts are blocked by this issue
- **User Experience**: Tools appear broken with unclear error messages

### Broader Impact
- **Data Integrity**: Binary data corruption violates fundamental data integrity expectations
- **Security Paradox**: Security plugin designed to protect data is actually corrupting it
- **Trust**: Users may lose confidence in Watchgate's ability to handle data correctly
- **Compatibility**: Breaks compatibility with legitimate MCP tools that handle binary data

## Steps to Reproduce

1. Configure Watchgate with PII filter plugin enabled
2. Configure upstream MCP server with screenshot capability (e.g., Puppeteer)
3. Request a screenshot through Watchgate
4. Observe that the returned base64 image data contains PII redaction text
5. Attempt to decode/display the image - it will fail due to corrupted base64

## Expected vs Actual Behavior

### Expected Behavior
- PII filter should distinguish between text content and binary data
- Base64-encoded binary data should be exempt from PII scanning
- Screenshot tools should return valid, usable image data
- Binary data integrity should be preserved

### Actual Behavior
- PII filter scans all string content regardless of data type
- Base64-encoded data gets corrupted by PII redactions
- Screenshot tools return invalid, corrupted data
- Binary data integrity is violated

## Root Cause Analysis

The PII filter plugin's `check_response` method processes all string values in tool responses without considering:

1. **Data Type Context**: No differentiation between text and binary data
2. **Content Format**: No recognition of base64 encoding patterns
3. **Tool Context**: No consideration of which tools legitimately return binary data
4. **Data Structure**: No analysis of response structure to identify binary fields

## Proposed Solutions

### Solution 1: Base64 Detection and Exemption (Recommended)
- **Approach**: Detect base64-encoded data patterns and exempt them from PII scanning
- **Implementation**: Add base64 detection logic to PII filter
- **Benefits**: Preserves binary data integrity while maintaining PII protection for text
- **Risks**: Low - base64 detection is well-established

### Solution 2: Tool-Aware Filtering
- **Approach**: Configure PII filter to skip certain response types based on tool context
- **Implementation**: Add tool-specific exemption rules to PII filter configuration
- **Benefits**: Granular control over which tools get PII filtering
- **Risks**: Requires manual configuration for each binary-returning tool

### Solution 3: Response Structure Analysis
- **Approach**: Analyze response structure to identify binary data fields
- **Implementation**: Add logic to detect common binary data field patterns
- **Benefits**: Automatic detection of binary data contexts
- **Risks**: More complex implementation, potential for false positives

### Solution 4: Content-Type Awareness
- **Approach**: Use content-type hints or metadata to determine data type
- **Implementation**: Extend MCP protocol to include content-type information
- **Benefits**: Most accurate data type identification
- **Risks**: Requires protocol changes, not backward compatible

## Recommended Implementation Plan

### Phase 1: Immediate Fix (Solution 1)
1. Add base64 pattern detection to PII filter
2. Exempt detected base64 strings from PII scanning
3. Add configuration option to enable/disable base64 exemption
4. Test with screenshot tools and other binary data tools

### Phase 2: Enhanced Solution (Solution 2)
1. Add tool-specific exemption configuration
2. Allow fine-grained control over which tools/responses get filtered
3. Document configuration options for common binary data tools

### Phase 3: Long-term Enhancement (Solution 3)
1. Implement response structure analysis
2. Add intelligent binary data detection
3. Provide automatic recommendations for exemption rules

## Testing Requirements

### Unit Tests
- Base64 detection accuracy
- PII scanning behavior with binary data
- Configuration option handling
- Edge cases (malformed base64, mixed content)

### Integration Tests
- Screenshot tool functionality through Watchgate
- Various binary data tools (file operations, image processing)
- PII filter effectiveness on legitimate text content
- Performance impact of base64 detection

### Validation Tests
- End-to-end screenshot workflows
- Binary data integrity verification
- PII protection still effective for text content
- No regression in existing functionality

## Configuration Impact

### New Configuration Options
```yaml
plugins:
  pii-filter:
    enabled: true
    exempt_base64: true  # New option
    min_base64_length: 100  # Minimum length to consider base64
    base64_patterns:  # Customizable patterns
      - "^data:image/[^;]+;base64,"
      - "^[A-Za-z0-9+/]{100,}={0,2}$"
```

### Backward Compatibility
- Default behavior should preserve binary data integrity
- Existing configurations should continue to work
- Add deprecation warnings for potentially problematic configurations

## Related Issues

### Security Considerations
- Ensure base64 exemption doesn't create PII bypass opportunities
- Consider if attackers could abuse base64 encoding to hide PII
- Maintain security-first approach while fixing functionality

### Performance Considerations
- Base64 detection should be efficient for large responses
- Consider caching detection results for repeated patterns
- Monitor impact on overall response processing time

## Success Criteria

1. **Functional**: Screenshot tools return valid, usable image data
2. **Security**: Text content still gets appropriate PII filtering
3. **Performance**: No significant impact on response processing time
4. **Compatibility**: Existing configurations continue to work
5. **Validation**: All current validation tests pass

## Timeline Estimate

- **Investigation**: 1-2 hours (pattern analysis, test case creation)
- **Implementation**: 4-6 hours (base64 detection, configuration, testing)
- **Testing**: 2-3 hours (unit tests, integration tests, validation)
- **Documentation**: 1 hour (configuration updates, usage examples)

**Total**: 8-12 hours for comprehensive fix

## Additional Context

This bug was discovered during validation testing of Watchgate with multiple servers configured. The validation process involves testing various MCP tools, including screenshot functionality, which revealed this critical issue with binary data handling.

The bug represents a fundamental conflict between security (PII protection) and functionality (binary data integrity). The solution must balance both concerns while maintaining Watchgate's security-first philosophy.