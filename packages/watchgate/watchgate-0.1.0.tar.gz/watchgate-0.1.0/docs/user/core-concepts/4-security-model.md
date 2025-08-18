# Security Model

*[Home](../../README.md) > [User Guide](../README.md) > [Core Concepts](README.md) > Security Model*

Watchgate implements a comprehensive security model designed to protect AI agent interactions while maintaining usability and transparency. This model is based on defense-in-depth principles and zero-trust architecture.

> **Note**: For detailed information about Watchgate's trust assumptions and deployment scenarios, see the [Trust Model and Deployment](trust-model-deployment.md) guide.

## Security Principles

### Zero Trust Architecture
Watchgate operates on the principle that no request should be trusted by default:

- **Every request is evaluated** against security policies
- **No implicit trust** based on source or previous interactions
- **Explicit allow/deny decisions** for all operations
- **Continuous monitoring** and auditing of all activities

### Defense in Depth
Multiple layers of security controls provide comprehensive protection:

1. **Tool Access Control**: Controls which operations can be performed
2. **Content Access Control**: Controls which resources can be accessed
3. **Audit Logging**: Monitors and records all activities
4. **Plugin Priority System**: Ensures security checks execute in correct order

### Fail-Safe Defaults
When in doubt, Watchgate defaults to the most secure option:

- **Plugin errors default to denial**
- **Missing configurations default to restrictive settings**
- **Unknown tools are blocked by default**
- **Unmatched content patterns are denied by default**

## Threat Model

### Threats Watchgate Protects Against

#### Unauthorized Tool Execution
- **Malicious AI behavior**: AI agent attempts harmful operations
- **Prompt injection attacks**: Malicious prompts try to bypass restrictions
- **Accidental operations**: AI agent makes unintended dangerous calls

#### Sensitive Data Exposure
- **Credential leakage**: Access to API keys, passwords, or tokens
- **Personal data access**: Unauthorized access to private files
- **Business data exposure**: Access to confidential business information

#### Compliance Violations
- **Unaudited operations**: Activities that should be logged but aren't
- **Policy violations**: Operations that violate organizational policies
- **Regulatory compliance**: Failure to meet industry-specific requirements

#### Operational Risks
- **Data destruction**: Accidental deletion or corruption of important data
- **System interference**: Operations that could disrupt system functionality
- **Resource exhaustion**: Excessive operations that could impact performance

### Threats Outside Watchgate's Scope

Watchgate focuses on AI agent interactions and doesn't protect against:

- **Network-level attacks**: DDoS, packet sniffing, network intrusion
- **Host-level security**: Operating system vulnerabilities, malware
- **MCP server vulnerabilities**: Bugs or security issues in upstream servers
- **Client-side attacks**: Vulnerabilities in AI client applications

## Security Controls

### Tool Access Control

**Purpose**: Control which MCP tools AI agents can execute

**Mechanisms**:
- **Allowlist mode**: Only specified tools are permitted
- **Blocklist mode**: Specified tools are blocked, others allowed
- **Tool discovery filtering**: Hide blocked tools from AI agents

**Security Benefits**:
- Prevents execution of dangerous operations
- Reduces attack surface by limiting available tools
- Provides granular control over AI capabilities

**Example Configuration**:
```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file", "list_directory"]
```

### Content Access Control

**Purpose**: Control which files and resources AI agents can access

**Mechanisms**:
- **Pattern-based filtering**: Use gitignore-style patterns
- **Allowlist/blocklist modes**: Flexible access control strategies
- **Resource discovery filtering**: Hide blocked resources from AI agents

**Security Benefits**:
- Protects sensitive files and directories
- Prevents data leakage through AI interactions
- Enables fine-grained access control policies

**Example Configuration**:
```yaml
plugins:
  security:
    - policy: "content_access_control"
      config:
        mode: "allowlist"
        resources:
          - "public/**/*"
          - "docs/*.md"
          - "!**/*.key"
          - "!**/secrets/*"
```

### Audit Logging

**Purpose**: Monitor and record all AI agent activities

**Mechanisms**:
- **Complete request/response logging**: Every interaction is recorded
- **Security event emphasis**: Special attention to blocked operations
- **Multiple log formats**: Support for different analysis tools
- **Configurable verbosity**: From critical events to detailed debugging

**Security Benefits**:
- Provides complete audit trail for compliance
- Enables incident response and forensics
- Supports security monitoring and alerting
- Helps identify attack patterns and behaviors

**Example Configuration**:
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        file: "logs/security-audit.log"
        format: "json"
        mode: "all"
        max_file_size_mb: 50
        backup_count: 10
```

## Security Boundaries

### Trust Boundaries

Watchgate establishes clear trust boundaries:

```
Untrusted Zone        Trust Boundary        Trusted Zone
┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│ AI Client   │────▶│  Watchgate   │────▶│ MCP Server   │
│ (Claude)    │     │  Security     │     │ (Filesystem) │
│             │     │  Policies     │     │              │
└─────────────┘     └───────────────┘     └──────────────┘
```

- **AI Client**: Untrusted - Could be compromised or make harmful requests
- **Watchgate**: Trust boundary - Enforces security policies
- **MCP Server**: Trusted - Protected by Watchgate's security controls

### Security Enforcement Points

Security is enforced at multiple points:

1. **Request Interception**: All requests from AI clients are intercepted
2. **Policy Evaluation**: Each request is evaluated against security policies
3. **Response Filtering**: Responses can be filtered or modified
4. **Audit Recording**: All activities are logged for monitoring

## Configuration Security

### Secure Configuration Practices

#### File Permissions
```bash
# Restrict configuration file access
chmod 600 watchgate.yaml
chown $(whoami) watchgate.yaml
```

#### Secret Management
```yaml
# Don't put secrets directly in configuration
upstream:
  command: "server --api-key ${API_KEY}"  # Use environment variables

# Or reference secret files
config:
  api_key_file: "/secure/path/to/api.key"
```

#### Configuration Validation
```bash
# Always validate configuration before deployment
watchgate debug config --validate --config watchgate.yaml
```

### Configuration Principles

#### Principle of Least Privilege
- **Start restrictive**: Begin with minimal permissions and expand as needed
- **Explicit allow**: Require explicit configuration for access grants
- **Regular review**: Periodically review and update permissions

#### Defense in Depth
- **Multiple controls**: Use both tool and content access controls
- **Layered security**: Combine security plugins with auditing
- **Plugin ordering**: Ensure security controls execute in correct sequence

#### Fail Secure
- **Default deny**: Block access when configuration is ambiguous
- **Error handling**: Security failures should block operations
- **Missing config**: Missing security configuration should be restrictive

## Security Monitoring

### Real-Time Monitoring

Monitor security events as they happen:

```bash
# Watch security events in real-time
tail -f logs/security-audit.log | grep -E "(BLOCK|DENY|SECURITY)"

# Monitor plugin execution
watchgate --config config.yaml --verbose | grep -E "(Security|Plugin)"
```

### Security Analytics

Analyze security patterns over time:

```bash
# Most frequently blocked tools
grep "Tool blocked" logs/audit.log | cut -d':' -f2 | sort | uniq -c | sort -nr

# Security events by hour
grep "SECURITY_BLOCK" logs/audit.log | cut -d' ' -f1,2 | cut -d':' -f1,2 | uniq -c

# Failed access patterns
grep "Resource blocked" logs/audit.log | cut -d':' -f3 | sort | uniq -c
```

### Alerting and Response

Set up alerts for critical security events:

```bash
# Alert on repeated blocks (potential attack)
tail -f logs/audit.log | awk '/SECURITY_BLOCK/ {count++} count >= 5 {print "ALERT: Multiple security blocks detected"; count=0}'

# Monitor for specific sensitive file access attempts
tail -f logs/audit.log | grep -E "(secret|password|key|credential)" | while read line; do
  echo "ALERT: Sensitive file access: $line"
done
```

## Operational Security

### Environment Separation

Use different security policies for different environments:

**Development Environment**:
```yaml
# More permissive for development
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "blocklist"
        tools: ["delete_file", "execute_command"]
```

**Production Environment**:
```yaml
# Highly restrictive for production
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist"
        tools: ["read_file", "list_directory"]
```

### Incident Response

Prepare for security incidents:

1. **Immediate Response**:
   - Stop Watchgate if compromise is suspected
   - Preserve audit logs for analysis
   - Review recent security events

2. **Investigation**:
   - Analyze audit logs for attack patterns
   - Identify scope of potential compromise
   - Review configuration for misconfigurations

3. **Recovery**:
   - Update security policies to prevent recurrence
   - Test new configurations thoroughly
   - Resume operations with enhanced monitoring

## Audit Trail Integrity

### Plugin Decision Transparency

Watchgate's security model includes comprehensive audit trail integrity to ensure complete visibility into plugin decisions:

#### Decision Context Preservation
- **Denial Decisions**: Always preserve specific plugin reason and metadata
- **Modification Decisions**: Preserve plugin context when responses are modified  
- **Standard Decisions**: Use generic context when no special processing occurs

#### Compliance Benefits
**Regulatory Compliance**:
- **GDPR**: PII processing actions documented with specific plugin details
- **HIPAA**: Health information filtering recorded with detailed context
- **SOX**: Financial data access controls logged with plugin-specific reasons

**Audit Trail Quality**:
- **Forensic Analysis**: Complete plugin processing history available
- **Incident Response**: Clear understanding of what security controls were applied
- **Compliance Reporting**: Structured data available for automated compliance checks

#### Error Message Transparency

**User-Facing Messages**:
```
# Generic (no plugin modifications)
"Request processed successfully"

# Specific (plugin performed work)  
"PII detected and redacted: 2 SSNs removed from response"
```

**Audit Log Entries**:
```
# Standard processing
2024-01-01 12:00:00 - REQUEST: tools/call - ALLOWED

# Plugin-specific processing
2024-01-01 12:00:00 - REQUEST: tools/call - ALLOWED - Tool filtering applied: 3 administrative tools removed
```

For detailed information about plugin decision processing, see the [Plugin Decision Flow](plugin-decision-flow.md) guide.

## Security Best Practices

### Configuration Best Practices

1. **Start with minimal permissions** and expand as needed
2. **Use allowlist mode** in production environments
3. **Enable comprehensive auditing** for all environments
4. **Regular configuration reviews** and updates
5. **Test configurations** in staging environments first

### Operational Best Practices

1. **Monitor audit logs** regularly for security events
2. **Set up alerting** for suspicious activities
3. **Regular security reviews** of AI agent behaviors
4. **Keep Watchgate updated** with latest security patches
5. **Document security policies** and review procedures

### Development Best Practices

1. **Security-first development** - consider security implications early
2. **Test with security controls** enabled during development
3. **Use development-specific** security policies
4. **Regular security training** for development teams
5. **Security code reviews** for custom plugins

## Summary

Watchgate's security model provides:

- **Comprehensive Protection**: Multiple layers of security controls
- **Zero Trust Architecture**: No implicit trust, all requests evaluated
- **Flexible Policies**: Adaptable to different environments and use cases
- **Complete Visibility**: Full audit trail of AI agent activities
- **Fail-Safe Design**: Secure defaults and error handling

This security model enables organizations to safely deploy AI agents while maintaining control, visibility, and compliance with security requirements.
