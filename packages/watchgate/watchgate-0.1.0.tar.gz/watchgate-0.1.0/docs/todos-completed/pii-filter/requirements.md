# PII Content Filter Plugin

**Status**: Implemented

## Problem Statement
MCP communications may contain personally identifiable information (PII) that should be detected and filtered to prevent data leaks and maintain compliance.

## Requirements
- Detect common PII patterns (SSN, credit cards, emails, phone numbers)
- Support multiple actions: block, redact, or audit-only
- Configurable detection patterns
- Minimal performance impact
- Integration with existing plugin architecture

## Success Criteria
- [x] Detects US Social Security Numbers
- [x] Detects major credit card formats with Luhn validation
- [x] Detects email addresses (RFC 5322 compliant)
- [x] Detects phone numbers (US and international formats)
- [x] Supports custom regex patterns
- [x] Provides audit trail via PolicyDecision
- [x] Configurable exemptions for tools/paths
- [x] Performance: <50ms per request

## Constraints
- Must not block legitimate non-PII data (low false positive rate)
- Must integrate with existing PolicyDecision architecture
- Regex-based for v0.1.0 (ML-based detection future enhancement)

## Design Notes

### Key Decisions
- **Regex-based detection**: Chose proven regex patterns over ML for v0.1.0 reliability
- **Modular PII types**: Each PII type can be enabled/disabled independently
- **Format-specific patterns**: Support regional variations (US, UK, EU phone formats)
- **Conservative defaults**: Err on the side of not blocking when uncertain

### Implementation Approach
1. Started with core PII types (SSN, credit cards)
2. Added comprehensive test suite with real-world patterns
3. Implemented configurable detection engine
4. Added redaction capability for audit-only mode
5. Integrated with PolicyDecision for audit trail

### Edge Cases Discovered
- Credit card patterns in code examples (added allowlist)
- Phone numbers in timestamps (refined regex)
- Email patterns in URLs (improved boundary detection)
- International format variations (added region-specific patterns)

## API Changes
New plugin class: `BasicPIIFilterPlugin` in `watchgate.plugins.security.basic_pii_filter`

## Configuration
```yaml
plugins:
  security:
    - policy: "basic_pii_filter"
      enabled: true
      priority: 5
      config:
        action: "redact"  # block | redact | audit_only
        pii_types:
          ssn:
            enabled: true
            formats: ["us"]
          credit_card:
            enabled: true
          email:
            enabled: true
          phone:
            enabled: true
            formats: ["us", "international"]
        custom_patterns:
          - name: "employee_id"
            pattern: "EMP-\\d{6}"
            enabled: true
        exemptions:
          tools: ["trusted_tool"]
          paths: ["test/data/*"]
```

## Testing Strategy
- Unit tests for each PII type detector
- Integration tests with real MCP messages
- Performance benchmarks
- False positive/negative analysis
- International format validation

## Performance Considerations
- Pre-compiled regex patterns on plugin init
- Early exemption checking to skip processing
- Efficient string searching with boundary anchors
- Measured: ~10-30ms per request depending on content size

## Security Considerations
- No PII data logged even in debug mode
- Redacted content uses consistent masking
- Exemptions require explicit configuration
- Audit trail includes detection confidence

## Future Improvements
- ML-based detection for context-aware filtering
- Configurable redaction patterns
- PII type confidence scoring
- Rate limiting for suspicious patterns
- Integration with external DLP systems