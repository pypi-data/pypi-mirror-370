# ADR-019: TUI Distribution and Licensing Model

## Status

Accepted

## Context

This ADR supersedes [ADR-017: TUI Invocation Pattern](./017-tui-invocation-pattern.md) by refining the command structure from `watchgate proxy` to `watchgate-gateway` as part of a comprehensive licensing and distribution strategy.

Watchgate is a security-focused MCP (Model Context Protocol) gateway with both core proxy functionality and a Terminal User Interface (TUI) for configuration management. We need to decide on licensing and distribution strategies that:

1. **Maintain trust through transparency** - Security tools need auditable source code
2. **Protect against wholesale reselling** - Prevent competitors from simply repackaging our complete solution
3. **Preserve user convenience** - Maintain simple installation and usage patterns
4. **Enable business sustainability** - Create defensible value while staying community-friendly

### Current State

- **Single codebase**: Everything currently in one private repository under AGPL license
- **Tight coupling**: TUI directly imports from core modules (`ConfigLoader`, `ProxyConfig`, `PluginManager`)
- **Unified installation**: Users run `pip install watchgate` and get everything
- **Command structure**: `watchgate` (TUI) and `watchgate proxy` (gateway mode)

### Business Considerations

The core proxy functionality (security, auditing, MCP protocol handling) is where technical trust matters most. The TUI, while valuable for user experience, is primarily a convenience layer. Our goal is to keep the security-critical code open source for auditing while protecting the complete user experience from wholesale copying.

## Decision

We will implement a **dual-license open core model** with the following structure:

### Licensing Strategy

- **Core proxy functionality**: Apache 2.0 (permissive open source)
- **TUI components**: Proprietary freeware (closed source, free to use, not for redistribution)

### Distribution Model

- **Single package approach**: `pip install watchgate` includes both core and TUI
- **Monorepo with selective publishing**: Develop everything in private monorepo, publish selectively
- **TUI distributed as compiled wheels**: Source code for TUI not published, only pre-built packages

### Command Structure Update

Replace the current command structure with separate commands for clarity:

- **`watchgate`** - Launches TUI configuration interface
- **`watchgate-gateway --config file`** - Runs the MCP gateway/proxy (for MCP clients)

This eliminates confusion between "proxy", "server", "core" terminology by using "gateway" (which aligns with our external marketing).

### Repository Structure

```
watchgate/ (private monorepo)
├── watchgate-core/              # Apache 2.0 - will be published open source
│   ├── watchgate/
│   │   ├── __init__.py
│   │   ├── config/
│   │   ├── proxy/
│   │   └── plugins/
│   ├── pyproject.toml           # Core package configuration
│   ├── LICENSE                  # Apache 2.0
│   └── README.md
│
├── watchgate-tui/               # Proprietary - wheels only on PyPI
│   ├── watchgate_tui/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── screens/
│   ├── pyproject.toml           # TUI package configuration
│   ├── LICENSE.PROPRIETARY      # Freeware license
│   └── README.md
│
├── scripts/
│   ├── build-packages.sh        # Build both packages
│   ├── publish-public.sh        # Sync core to public GitHub
│   └── release.sh               # Full release process
│
└── docs/                        # All documentation, ADRs, etc.
```

### Package Distribution

**Single unified package** containing both components:

```toml
# watchgate/pyproject.toml (main package)
[project]
name = "watchgate"
dependencies = [
    "watchgate-tui>=0.1.0",     # TUI included by default
    "pyyaml>=6.0.2",
    "aiohttp>=3.12.4",
    # ... other core dependencies
]

[project.scripts]
watchgate = "watchgate_tui.main:tui_main"
watchgate-gateway = "watchgate.main:gateway_main"
```

**Alternative server-only package** for environments that don't need TUI:

```bash
pip install watchgate-core      # Core functionality only
```

### Build and Release Process

1. **Development**: All work happens in private monorepo
2. **Core publishing**: 
   - Build source distribution (sdist) for transparency
   - Publish to PyPI with full source code visibility
   - Sync filtered copy to public GitHub repository
3. **TUI publishing**:
   - Build wheel-only distribution (no source)
   - Optionally compile with Cython for additional obfuscation
   - Publish wheel to PyPI without source code
4. **Unified package**: Depends on both core and TUI packages

## Rationale

### License Choice: Apache 2.0 vs AGPL

**Apache 2.0 for core enables**:
- Corporate adoption (many organizations ban AGPL)
- Tight coupling between core and TUI without license violations
- Permissive use while maintaining copyright protection
- Compatibility with closed-source TUI components

**AGPL was rejected because**:
- Any code linking to AGPL must also be AGPL (makes closed TUI impossible)
- Would require complete API separation between core and TUI
- Creates adoption barriers for enterprise users
- Doesn't actually prevent the wholesale copying we're concerned about

### Command Structure: Gateway vs Proxy

**Gateway terminology chosen because**:
- Aligns with external marketing ("Watchgate Security Gateway")
- Eliminates confusion between "proxy", "server", "core" terms
- Follows industry patterns (Kong Gateway, Traefik Gateway)
- More accurate from MCP client perspective (they see Watchgate as a gateway to upstream servers)

**Separate commands chosen over subcommands because**:
- Crystal clear intent: `watchgate` = interactive, `watchgate-gateway` = automated
- No ambiguity in MCP client configurations
- Follows established patterns (docker/dockerd, gitlab/gitlab-runner)
- Easier documentation and support

### Distribution Model Analysis

We evaluated several approaches:

| Approach | Installation | Protection Level | User Friction | Maintainability |
|----------|-------------|------------------|---------------|-----------------|
| **Single package (chosen)** | `pip install watchgate` | 🔒 Medium | ✅ None | ✅ Simple |
| Two packages | `pip install watchgate[tui]` | 🔒 Medium | ⚠️ Some | ⚠️ Complex |
| Separate repos | Multiple commands | 🔒 Medium | ❌ High | ❌ Complex |

**Single package chosen because**:
- Zero user friction - familiar pip install experience
- Atomic version management - core and TUI always compatible
- Simple build and release process
- Follows successful precedents (VS Code, Docker Desktop)

### Protection Strategy

**Technical protection** (compiled wheels, bytecode) provides:
- Deterrent against casual copying
- Increased effort required for reverse engineering
- Professional appearance and licensing clarity

**Legal protection** (clear licensing, branding) provides:
- Copyright protection under intellectual property law
- Clear terms of use preventing redistribution
- Basis for enforcement action if needed

**Strategic protection** (open core) provides:
- Community trust through core transparency
- Competitive moat through UX and integration work
- Ability to accept contributions to core while protecting innovations

## Consequences

### Positive Outcomes

- **User trust**: Security-critical code remains auditable
- **Simple adoption**: Single `pip install` with no configuration needed
- **Clear boundaries**: Separate commands eliminate terminology confusion
- **Business protection**: TUI cannot be easily copied or rebranded
- **Community engagement**: Core contributions remain possible
- **Enterprise friendly**: Apache 2.0 license acceptable to corporate users

### Trade-offs

- **Development complexity**: Must manage two package builds and releases
- **Limited technical protection**: Python bytecode can be decompiled with effort
- **Licensing complexity**: Mixed licensing within single product
- **Support burden**: Must support both open and closed components

### Migration Path

1. **Phase 1 (v0.1.0)**:
   - Change license from AGPL to Apache 2.0
   - Implement `watchgate-gateway` command alongside existing `watchgate proxy`
   - Add deprecation warnings for `watchgate proxy`

2. **Phase 2 (v0.2.0)**:
   - Remove `watchgate proxy` support
   - Implement monorepo structure
   - Set up selective publishing pipeline

3. **Phase 3 (v0.3.0)**:
   - Establish separate package distribution
   - Clean up public repository and documentation

### Risks and Mitigations

**Risk**: Community backlash against closed-source components
- **Mitigation**: Clear communication that core security functionality remains open, TUI is convenience only

**Risk**: Technical protection proves insufficient
- **Mitigation**: Focus on legal protection and community building rather than technical obfuscation

**Risk**: Increased maintenance burden
- **Mitigation**: Invest in automated build and release tooling early

**Risk**: Confusion between watchgate vs watchgate-gateway
- **Mitigation**: Clear documentation, good error messages, consistent branding

## Implementation Notes

### Backward Compatibility

- Keep `watchgate proxy` as deprecated alias in v0.1.0
- Show clear migration instructions in deprecation warnings
- Update documentation with new command structure
- Provide migration guide for existing MCP client configurations

### Error Handling

```python
# If TUI not available
def tui_main():
    try:
        from watchgate_tui import run_tui
        run_tui()
    except ImportError:
        print("TUI not installed. Install with: pip install watchgate")
        print("To run the gateway: watchgate-gateway --config config.yaml")
```

### License Headers

**Core files** (Apache 2.0):
```python
# Copyright (c) 2024 [Your Name]
# Licensed under the Apache License, Version 2.0
```

**TUI files** (Proprietary):
```python
# Copyright (c) 2024 [Your Name]
# Proprietary Software - All Rights Reserved
# Free to use but not for redistribution
```

This decision provides a clear path forward that balances technical trust, user convenience, and business sustainability while following established industry patterns for open core products.