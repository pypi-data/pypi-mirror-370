# What is Watchgate?

*[Home](../../README.md) > [User Guide](../README.md) > [Core Concepts](README.md) > What is Watchgate?*

Watchgate is a security proxy for Model Context Protocol (MCP) servers that provides comprehensive protection for AI agent interactions with external tools and resources. It acts as an intelligent security layer between AI clients (like Claude Desktop) and MCP servers, controlling what tools can be executed and what content can be accessed.

## The Problem Watchgate Solves

Modern AI assistants are increasingly powerful and can interact with external systems through MCP servers. While this capability enables powerful workflows, it also introduces security risks:

- **Unrestricted Tool Access**: AI agents might execute dangerous operations like deleting files or running system commands
- **Sensitive Data Exposure**: AI agents could access confidential files, API keys, or private information
- **Lack of Audit Trail**: No visibility into what operations AI agents are performing
- **No Policy Enforcement**: No way to enforce organizational security policies on AI interactions

## How Watchgate Works

Watchgate sits between your AI client and MCP servers, intercepting and evaluating every request:

```
AI Client (Claude Desktop) → Watchgate → MCP Server (Filesystem, etc.)
                          ↙         ↘
                   Security      Audit
                   Plugins       Plugins
```

### Request Flow

1. **AI client** sends a request to what it thinks is the MCP server
2. **Watchgate** intercepts the request
3. **Security plugins** evaluate whether the request should be allowed
4. **If allowed**: Request passes through to the actual MCP server
5. **If blocked**: Security policy message is returned to the AI client
6. **Audit plugins** log the entire interaction for compliance and monitoring

**Note**: Watchgate processes multiple requests concurrently, enabling high-performance scenarios with multiple clients or rapid request sequences.

## Core Capabilities

### Tool Access Control
- **Allowlist Mode**: Only permit specific tools to be executed
- **Blocklist Mode**: Block dangerous tools while allowing others
- **Tool Discovery Filtering**: Hide blocked tools from AI agents entirely

### Content Access Control
- **Resource-Level Security**: Control which files/resources can be accessed
- **Pattern-Based Rules**: Use gitignore-style patterns for flexible access control
- **Directory Protection**: Protect sensitive directories and file types

### Comprehensive Auditing
- **Complete Request Logs**: Every AI interaction is logged
- **Security Event Monitoring**: Special emphasis on blocked operations
- **Multiple Log Formats**: Simple text, JSON, or detailed formats for different use cases
- **Configurable Verbosity**: From critical security events to detailed debugging

### Plugin Architecture
- **Modular Design**: Add or remove security controls as needed
- **Priority System**: Control the order of security checks
- **Extensible**: Custom plugins for specialized security requirements

## Key Benefits

### Security
- **Zero Trust Model**: Every request is evaluated against security policies
- **Defense in Depth**: Multiple layers of protection (tool + content + audit)
- **Policy Enforcement**: Organizational security policies are automatically enforced
- **Risk Mitigation**: Prevents accidental or malicious operations

### Compliance
- **Audit Trail**: Complete logs of all AI agent activities
- **Policy Documentation**: Security rules are clearly defined and versioned
- **Compliance Reporting**: Logs support regulatory and internal audit requirements

### Operational Visibility
- **Real-Time Monitoring**: See exactly what AI agents are doing
- **Security Analytics**: Understand AI agent behavior patterns
- **Incident Response**: Detailed logs for investigating security events

### Developer Experience
- **Transparent Operation**: Works with existing MCP clients and servers
- **Easy Configuration**: YAML-based configuration with clear documentation
- **Flexible Policies**: Adapt security controls to different environments and use cases

## Use Cases

### Individual Users
- **Personal AI Safety**: Protect personal files from accidental AI operations
- **Workspace Protection**: Ensure AI agents only access intended directories
- **Learning and Development**: Safely experiment with AI tools

### Development Teams
- **Code Repository Protection**: Prevent AI from accessing sensitive code or credentials
- **Environment Separation**: Different security policies for dev/staging/production
- **Team Collaboration**: Consistent security policies across team members

### Enterprises
- **Data Loss Prevention**: Prevent AI agents from accessing confidential information
- **Compliance Requirements**: Meet regulatory requirements for AI system auditing
- **Policy Enforcement**: Implement organizational AI usage policies
- **Risk Management**: Control and monitor AI agent interactions with business systems

## Watchgate vs. Other Security Approaches

### Traditional Application Security
- **Watchgate**: Specialized for AI agent interactions and MCP protocol
- **Traditional**: Generic application security, not AI-aware

### Built-in MCP Server Security
- **Watchgate**: Centralized, configurable security policies across all MCP servers
- **Built-in**: Limited, server-specific, often hardcoded restrictions

### Client-Side Restrictions
- **Watchgate**: Server-side enforcement, cannot be bypassed by clients
- **Client-Side**: Relies on client compliance, can be bypassed or misconfigured

### Network-Level Security
- **Watchgate**: Application-aware, understands MCP semantics and AI context
- **Network-Level**: Protocol-agnostic, limited understanding of AI-specific risks

## When to Use Watchgate

### Perfect For
- **Production AI deployments** requiring security controls
- **Sensitive data environments** where AI access must be controlled
- **Compliance-required environments** needing audit trails
- **Multi-user AI systems** requiring consistent policies
- **Development environments** where you want to safely experiment

### Consider Alternatives When
- **Simple, trusted, single-user scenarios** with low-risk operations
- **Development environments** where you need unrestricted access for debugging
- **Performance-critical applications** where any proxy overhead is unacceptable

## Getting Started

Ready to protect your AI interactions? Start with:

1. **[Installation](../getting-started/installation.md)**: Get Watchgate installed on your system
2. **[Quick Setup](../getting-started/quick-setup.md)**: Configure basic protection in minutes
3. **[Your First Plugin](../getting-started/first-plugin.md)**: Learn how security plugins work

## Next Steps

- **Learn the Architecture**: Understand [how plugins work](plugin-architecture.md)
- **Understand Security**: Explore Watchgate's [security model](security-model.md)
- **See It in Action**: Follow the [securing tool access tutorial](../tutorials/securing-tool-access.md)
