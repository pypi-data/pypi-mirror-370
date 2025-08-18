# Trust Model and Deployment Assumptions

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Core Concepts](../README.md) → Trust Model and Deployment Assumptions*

This document explains Watchgate's trust model, deployment assumptions, and security boundaries to help security-conscious users understand the design decisions and appropriate use cases.

## Trust Model Overview

Watchgate implements a **local trust model** designed for deployment in trusted environments where the operator has full control over the system. This model prioritizes simplicity, performance, and flexibility over network-level security controls.

### Key Trust Assumptions

1. **Local Deployment Context**
   - Watchgate assumes deployment on a trusted host controlled by the operator
   - The system trusts the local environment and operating system security
   - No built-in protection against local privilege escalation or OS-level attacks

2. **Process-Level Security**
   - Security boundaries exist at the process level, not the network level
   - Watchgate runs with the same privileges as the user who starts it
   - Upstream MCP servers inherit Watchgate's process permissions

3. **Configuration Trust**
   - Configuration files are trusted and assumed to be protected by filesystem permissions
   - No built-in configuration encryption or integrity verification
   - Operators are responsible for securing configuration files

## Deployment Assumptions

### Intended Deployment Scenarios

Watchgate is designed for the following deployment patterns:

#### 1. Personal Development Environment
```
Developer Machine
├── AI Client (Claude Desktop)
├── Watchgate (same user)
└── MCP Servers (subprocesses)
```
- Single-user development workstation
- All components run as the same user
- Security focused on preventing AI mishaps, not malicious actors

#### 2. Isolated Container/VM
```
Container/VM Boundary
├── AI Client → Network → Watchgate Container
                          ├── Watchgate Process
                          └── MCP Server Subprocesses
```
- Network isolation provides the security boundary
- Container/VM prevents escape to host system
- Watchgate provides policy enforcement within the container

#### 3. Controlled Server Environment
```
Secured Server
├── Restricted User Account
│   ├── Watchgate Process
│   └── MCP Server Subprocesses
└── OS-Level Security Controls
```
- Dedicated service account with limited permissions
- OS-level security (SELinux, AppArmor) provides additional boundaries
- Network access controlled by firewall rules

### NOT Designed For

Watchgate is **not** designed for these scenarios:

1. **Multi-Tenant SaaS Deployment**
   - No user authentication or session management
   - No tenant isolation mechanisms
   - No quota or resource allocation per user

2. **Internet-Facing Services**
   - No built-in TLS/SSL support
   - No DDoS protection
   - No rate limiting by client IP

3. **Zero-Trust Network Environments**
   - No mutual TLS authentication
   - No certificate-based identity verification
   - No integration with identity providers

## Security Boundaries

### What Watchgate Protects

```
┌─────────────────────────────────────────────────┐
│              Watchgate Scope                   │
│                                                 │
│  ┌─────────────┐     ┌──────────────┐         │
│  │ AI Behavior │ ──→ │ Policy Layer │         │
│  │   Control   │     │              │         │
│  └─────────────┘     └──────────────┘         │
│                             ↓                   │
│  ┌─────────────┐     ┌──────────────┐         │
│  │   Content   │ ←── │   Auditing   │         │
│  │  Filtering  │     │              │         │
│  └─────────────┘     └──────────────┘         │
└─────────────────────────────────────────────────┘
```

**Within Scope:**
- MCP protocol message filtering and validation
- Tool access control (which tools can be called)
- Content filtering (PII, secrets, prompt injection)
- Audit logging of AI interactions
- Response modification and filtering

### What Watchgate Does NOT Protect

```
┌─────────────────────────────────────────────────┐
│            Outside Watchgate Scope             │
│                                                 │
│  • Network attacks (DDoS, MITM)                 │
│  • Authentication & Authorization               │
│  • Process isolation & sandboxing               │
│  • Resource limits (CPU, memory, disk)          │
│  • Encrypted communication channels             │
│  • OS-level security vulnerabilities            │
│  • Supply chain attacks on dependencies         │
│  • Physical security of the host                │
└─────────────────────────────────────────────────┘
```

## Authentication and Authorization Model

### Current State: No Authentication

Watchgate currently implements **no authentication mechanisms**:

- **No client authentication**: Any process that can connect to Watchgate's stdio interface is trusted
- **No upstream authentication**: MCP servers are started as subprocesses without credential exchange
- **No user identity**: All requests are processed without user context

### Authorization Through Plugins

Authorization is handled entirely through the plugin system based on request content:

```yaml
# Content-based authorization, not identity-based
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist"
        tools: ["read_file", "list_directory"]
```

### Why No Authentication?

This design decision reflects Watchgate's intended use cases:

1. **Local Development**: Authentication adds complexity without security benefit when all components run as the same user
2. **Container Isolation**: Authentication is redundant when network boundaries provide isolation
3. **Simplicity**: Reduces configuration complexity and potential misconfiguration
4. **Performance**: Eliminates authentication overhead for local operations

## Subprocess Execution Model

### Trust Relationship with Upstream Servers

```
Watchgate Process
    │
    ├─fork()─→ MCP Server Process 1
    ├─fork()─→ MCP Server Process 2
    └─fork()─→ MCP Server Process N
```

**Key Characteristics:**
- Upstream servers run as child processes of Watchgate
- Inherit Watchgate's permissions and environment
- No additional sandboxing or isolation
- Can access any resources Watchgate can access

### Security Implications

1. **Shared Privileges**: MCP servers have the same filesystem and network access as Watchgate
2. **No Resource Isolation**: No CPU, memory, or I/O limits enforced
3. **Command Execution**: Configured commands are executed directly without validation
4. **Environment Inheritance**: MCP servers inherit environment variables

## Deployment Security Guidelines

### For Personal Development

```bash
# Run as your normal user account
watchgate --config ~/watchgate.yaml

# Protect configuration file
chmod 600 ~/watchgate.yaml
```

**Security Considerations:**
- Rely on your user account permissions
- Use Watchgate to prevent accidental AI mistakes
- Not concerned with malicious actors

### For Production Deployment

```bash
# Create dedicated user
sudo useradd -r -s /bin/false watchgate

# Restrict configuration access
sudo chown watchgate:watchgate /etc/watchgate/config.yaml
sudo chmod 600 /etc/watchgate/config.yaml

# Use systemd with restrictions
sudo systemctl start watchgate.service
```

**Recommended systemd hardening:**
```ini
[Service]
User=watchgate
Group=watchgate
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
NoNewPrivileges=yes
ReadWritePaths=/var/log/watchgate
```

### For Container Deployment

```dockerfile
FROM python:3.11-slim
RUN useradd -r watchgate
USER watchgate
COPY --chown=watchgate:watchgate . /app
WORKDIR /app
CMD ["watchgate", "--config", "config.yaml"]
```

**Security Considerations:**
- Run as non-root user in container
- Mount only necessary volumes
- Use read-only root filesystem where possible
- Network isolation at container level

## Security Model Comparison

### Watchgate vs Traditional Security Proxies

| Aspect | Watchgate | Traditional Proxy |
|--------|------------|-------------------|
| Authentication | None (trust-based) | Username/password, certificates, tokens |
| Network Security | Relies on OS/container | Built-in TLS, mutual auth |
| Access Control | Content-based | Identity-based (RBAC) |
| Isolation | Process-level | Network-level |
| Resource Limits | None built-in | Quotas, rate limits |
| Audit Trail | Comprehensive | User-attributed |

### When to Use Watchgate

✅ **Good Fit:**
- Local AI development environments
- Controlled container deployments
- Single-user or small team scenarios
- When you trust the deployment environment
- Focus on preventing AI mistakes vs malicious actors

❌ **Not a Good Fit:**
- Multi-tenant environments
- Internet-facing deployments
- Zero-trust networks
- When you need user authentication
- Untrusted or shared infrastructure

## Future Security Enhancements

While maintaining the simplicity of the current trust model, future versions may add optional security features:

1. **Optional Authentication**
   - API key support for client connections
   - Upstream server authentication tokens
   - Integration with external auth providers

2. **Enhanced Isolation**
   - Subprocess sandboxing options
   - Resource limit configuration
   - Seccomp filters for Linux

3. **Network Security**
   - Optional TLS support
   - Unix domain socket support
   - Certificate-based authentication

These would remain **optional** to preserve the simplicity of local deployments while enabling higher security deployments.

## Summary

Watchgate's trust model is designed for **trusted local environments** where:

- The operator controls the deployment environment
- Security boundaries are established at the OS or container level
- The focus is on preventing AI mistakes rather than malicious attacks
- Simplicity and performance are prioritized over network-level security

Understanding these assumptions helps you deploy Watchgate appropriately:
- Use OS-level security for production deployments
- Leverage container isolation for network-accessible deployments
- Rely on Watchgate for policy enforcement, not authentication
- Add external security layers as needed for your threat model

This trust model makes Watchgate ideal for development environments and controlled deployments while keeping the codebase simple, auditable, and focused on its core mission of AI safety.