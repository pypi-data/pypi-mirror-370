# Documentation Structure

This directory contains Watchgate's documentation, organized in a clean, logical structure.

## Directory Structure

```
docs/
├── overview.md                                 # High-level project overview
├── README.md                                   # This structure guide
├── user/                                       # User-facing documentation
│   ├── getting-started/                       # Installation and setup
│   │   ├── installation.md
│   │   ├── quick-setup.md
│   │   └── first-plugin.md
│   ├── core-concepts/                         # Foundational understanding
│   │   ├── what-is-watchgate.md
│   │   ├── plugin-architecture.md
│   │   ├── security-model.md
│   │   └── audit-system.md
│   ├── tutorials/                             # Practical guides
│   │   ├── securing-tool-access.md
│   │   ├── protecting-sensitive-content.md
│   │   ├── implementing-audit-logging.md
│   │   └── multi-plugin-security.md
│   ├── reference/                             # Technical details
│   │   ├── configuration-reference.md
│   │   ├── plugin-ordering.md
│   │   └── troubleshooting.md
│   └── contribute/                            # Community participation
│       ├── providing-feedback.md
│       ├── reporting-issues.md
│       └── development-guide.md
├── features/                                  # Feature-specific documentation
│   ├── core-proxy/                           # MCP gateway server
│   ├── plugin-architecture/                  # Plugin system foundation
│   ├── pii-filter/                           # PII detection and filtering
│   └── [other-features]/                     # Individual feature docs
├── decision-records/                          # Architecture decision records
├── archive/                                   # Historical documentation
│   └── v0.1.0/                               # Archived version-based docs
└── templates/                                 # Documentation templates
        ├── 001-transport-layer-architecture.md
        ├── 002-async-first-architecture.md
        ├── 003-test-driven-development.md
        ├── 004-error-handling-strategy.md
        └── 005-configuration-management.md
```

## Document Relationships

### Overview Document
- **`overview.md`** - The high-level project overview and strategic direction for all Watchgate versions

### Version-Specific Documents
Each version directory contains a complete document set:
- **`v0.1.0-requirements.md`** - Complete requirements for the initial release
- **`v0.1.0-implementation-plan.md`** - Detailed implementation strategy and component breakdown
- **`v0.1.0-test-plan.md`** - Comprehensive testing strategy for version deliverables

### Requirement Tracking System
The documentation uses a systematic approach to track requirement completion:
- **Requirement IDs**: Each requirement has a unique identifier (FR-1, TR-2, QR-3, etc.)
- **Status Tracking**: Clear visual indicators and progress updates throughout documentation
- **Cross-References**: Requirements document links to implementation plans and test strategies

### Cross-References
- All component documents link back to their version requirements document
- Version documents link back to the overview for strategic context
- **Requirement IDs**: Systematic tracking using FR-X, TR-X, QR-X identifiers
- Related documents within a version cross-reference each other

## File Naming Conventions

### Directory Names
- Use version-specific naming: `v0.1.0`, `v0.2.0`
- Use kebab-case for multi-word names: `decision-records`, `future-work`

### File Names
- Use descriptive names without prefixes: `requirements.md`, `test-plan.md`
- Use kebab-case for multi-word names: `api-spec.md`, `architecture.md`

### Document Headers
Each section document should include this header format:

```markdown
# [Component Name] - [Document Type]

**Parent Document**: [Watchgate v0.1.0 Requirements](../v0.1.0-requirements.md) - Section [N]  
**Master Overview**: [Watchgate Requirements Overview](../overview.md)  
**Related Documents**: 
- [Document Name](./document-name.md)
- [Another Document](./another-document.md)

*Version: 1.0*  
*Date: [Current Date]*  
*Scope: v0.1.0 [Context]*

> This document expands on **Section [N]: [Section Name]** from the Watchgate v0.1.0 Requirements document.
```

## Documentation Categories

### For New Users
Start here to understand Watchgate and get it running:

1. **[What is Watchgate?](user/core-concepts/what-is-watchgate.md)** - Understand the purpose and benefits
2. **[Installation](user/getting-started/installation.md)** - Get Watchgate installed on your system
3. **[Quick Setup](user/getting-started/quick-setup.md)** - Configure basic protection in minutes
4. **[Your First Plugin](user/getting-started/first-plugin.md)** - Learn how security plugins work

### For Implementers
Ready to add security to your MCP setup:

1. **[Plugin Architecture](user/core-concepts/plugin-architecture.md)** - Understand how plugins work
2. **[Security Model](user/core-concepts/security-model.md)** - Learn Watchgate's security approach
3. **[Securing Tool Access](user/tutorials/securing-tool-access.md)** - Control which tools can be used
4. **[Protecting Sensitive Content](user/tutorials/protecting-sensitive-content.md)** - Prevent data leaks
5. **[Implementing Audit Logging](user/tutorials/implementing-audit-logging.md)** - Track all MCP activity

### For Advanced Users
Deep configuration and customization:

1. **[Configuration Reference](user/reference/configuration-reference.md)** - Complete configuration options
2. **[Plugin Ordering](user/reference/plugin-ordering.md)** - Control plugin execution order
3. **[Multi-Plugin Security](user/tutorials/multi-plugin-security.md)** - Combine multiple security plugins
4. **[Troubleshooting](user/reference/troubleshooting.md)** - Solve common issues

### For Contributors
Help improve Watchgate:

1. **[Development Guide](user/contribute/development-guide.md)** - Set up development environment
2. **[Providing Feedback](user/contribute/providing-feedback.md)** - Share suggestions and ideas
3. **[Reporting Issues](user/contribute/reporting-issues.md)** - Help us fix bugs

### For Project Team
Development planning and architecture:

1. **[Project Overview](overview.md)** - High-level strategy and requirements
2. **[v0.1.0 Requirements](versions/v0.1.0/v0.1.0-requirements.md)** - Complete feature specifications
3. **[Implementation Plan](versions/v0.1.0/v0.1.0-implementation-plan.md)** - Development strategy
4. **[Test Plan](versions/v0.1.0/v0.1.0-test-plan.md)** - Quality assurance approach

## Navigation Guide

### Quick Start Path
**New to Watchgate?** Follow this path:
```
overview.md → user/core-concepts/what-is-watchgate.md → user/getting-started/installation.md → user/getting-started/quick-setup.md
```

### Implementation Path
**Ready to secure your MCP setup?** Follow this path:
```
user/core-concepts/plugin-architecture.md → user/tutorials/securing-tool-access.md → user/tutorials/protecting-sensitive-content.md
```

### Advanced Configuration Path
**Need complex security policies?** Follow this path:
```
user/reference/configuration-reference.md → user/reference/plugin-ordering.md → user/tutorials/multi-plugin-security.md
```

### Development Path
**Want to contribute?** Follow this path:
```
user/contribute/development-guide.md → versions/v0.1.0/v0.1.0-requirements.md → versions/v0.1.0/v0.1.0-implementation-plan.md
```
