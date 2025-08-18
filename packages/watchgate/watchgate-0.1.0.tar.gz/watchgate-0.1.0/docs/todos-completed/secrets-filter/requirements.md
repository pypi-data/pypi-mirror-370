# Secrets Filter Plugin

**Status**: Implemented

## Problem Statement
MCP communications may contain secrets, tokens, and credentials that should be detected and filtered to prevent credential leaks and maintain security.

## Requirements
- Detect well-known secrets and tokens (AWS keys, GitHub tokens, API keys, etc.)
- Support multiple actions: block, redact, audit_only
- High-confidence detection with minimal false positives
- Conservative entropy analysis for unknown secrets
- Configurable secret types (enable/disable individually)
- Custom organization-specific patterns
- Tool and path exemptions for trusted sources
- Integration with audit trail via PolicyDecision

## Success Criteria
- [x] Detects AWS access keys (AKIA-prefixed)
- [x] Detects GitHub tokens (ghp_, gho_, ghu_, ghs_, ghr_ prefixes)
- [x] Detects Google API keys (AIza-prefixed)
- [x] Detects JWT tokens (3-part base64url structure)
- [x] Detects SSH private keys (PEM format)
- [x] Conservative entropy detection for unknown secrets
- [x] Configurable allowlist for testing patterns
- [x] Tool and path exemptions
- [x] Audit integration with detailed metadata

## Constraints
- Must prioritize avoiding false positives over comprehensive coverage
- Regex-based for v0.1.0 (established patterns only)
- Performance impact <50ms per request
- No logging of actual secret values

## Implementation Notes
- Uses high-confidence regex patterns with unique identifiers
- Modular detection system for enabling/disabling secret types
- Conservative entropy thresholds to minimize false positives
- Pre-compiled patterns for performance optimization

## Configuration
```yaml
plugins:
  security:
    - policy: "basic_secrets_filter"
      enabled: true
      priority: 10
      config:
        action: "block"  # or "redact" or "audit_only"
        detection_types:
          aws_access_keys:
            enabled: true
          github_tokens:
            enabled: true
          google_api_keys:
            enabled: true
          jwt_tokens:
            enabled: true
          ssh_private_keys:
            enabled: true
        entropy_detection:
          enabled: true
          min_entropy: 5.5
          min_length: 32
          max_length: 200
        custom_patterns:
          - name: "company_api_key"
            pattern: "COMP-[A-Za-z0-9]{32}"
            enabled: true
        allowlist:
          patterns: 
            - "test_key_*"
            - "demo_token_*"
        exemptions:
          tools: ["development_tool"]
          paths: ["test/*", "examples/*"]
```

## References
- Implementation: `watchgate/plugins/security/basic_secrets_filter.py`
- Tests: `tests/unit/test_secrets_filter_plugin.py`
- Integration: `tests/integration/test_secrets_filter_integration.py`