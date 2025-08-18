# Public Repository Sync Requirements

## Overview

Set up automated synchronization between the private development repository and a public repository that contains only the Apache 2.0 licensed core functionality, enabling community access while protecting proprietary components.

## Context

As part of the dual-license open core model, we need to:
- Maintain development in private repository with full history
- Publish only core functionality to public repository
- Filter out TUI code, private development history, and sensitive information
- Provide clean, professional public repository for community engagement

## Objectives

- Create filtered copy of private repo containing only open source components
- Establish automated sync process for releases
- Ensure public repo has clean history and professional presentation
- Enable community contributions to core functionality
- Maintain clear separation between private and public codebases

## Current State

- All development happens in private repository
- No public repository exists yet
- Private repo contains both core and TUI functionality
- Git history may contain sensitive information or development artifacts

## Target State

```
Private Repo (github.com/user/watchgate-private)
├── watchgate-core/     # → Synced to public
├── watchgate-tui/      # → Excluded from public  
├── docs/               # → Partially synced (filter sensitive docs)
├── tests/              # → Synced to public
├── configs/            # → Synced to public
└── scripts/            # → Partially synced (filter private scripts)

Public Repo (github.com/user/watchgate)
├── watchgate/          # Core functionality only
├── docs/               # Public documentation only
├── tests/              # Core tests only
├── configs/            # Example configs
├── scripts/            # Public build scripts
├── LICENSE             # Apache 2.0
└── README.md           # Public-facing README
```

## Detailed Requirements

### 1. Repository Structure Planning

**Content to Include in Public Repo**:
- Core source code (`watchgate-core/watchgate/`)
- Core tests (`tests/` filtered for core-only)
- Public documentation (`docs/` filtered)
- Example configurations (`configs/`)
- Build scripts for core (`scripts/` filtered)
- Root package files (`pyproject.toml`, `LICENSE`, `README.md`)

**Content to Exclude from Public Repo**:
- TUI source code (`watchgate-tui/`)
- Private development scripts
- Sensitive documentation (todos with business info, ADRs with competitive details)
- Development artifacts and temporary files
- Private configuration examples
- Personal/company-specific information

### 2. Git Filtering Strategy

**Option A: git-filter-repo (Recommended)**
```bash
#!/bin/bash
# scripts/create-public-repo.sh

# Create clean copy with only desired paths
git clone --mirror private-repo.git temp-repo
cd temp-repo

# Use git-filter-repo to include only public paths
git filter-repo \
  --path watchgate-core/ \
  --path tests/unit/ \
  --path tests/integration/ \
  --path configs/dummy/ \
  --path docs/decision-records/ \
  --path scripts/build-packages.sh \
  --path scripts/test-all.sh \
  --path pyproject.toml \
  --path LICENSE \
  --path README.md \
  --force

# Rewrite paths to flatten structure
git filter-repo \
  --path-rename watchgate-core/watchgate/:watchgate/ \
  --path-rename watchgate-core/pyproject.toml:pyproject.toml \
  --path-rename watchgate-core/README.md:README-CORE.md \
  --force

# Clean up git history
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Push to public repo
git push --mirror public-repo.git
```

**Option B: Subtree Strategy**
```bash
# Create public repo as subtree of core directory
git subtree push --prefix=watchgate-core public-repo main
```

### 3. Automated Sync Process

**File: `scripts/sync-public-repo.sh`**
```bash
#!/bin/bash
set -e

# Configuration
PRIVATE_REPO_PATH="."
PUBLIC_REPO_URL="git@github.com:user/watchgate.git"
TEMP_DIR=$(mktemp -d)
BRANCH="main"

echo "Syncing to public repository..."

# Validate we're in the right place
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "watchgate-core" ]]; then
    echo "Error: Must run from private repo root"
    exit 1
fi

# Create working copy
echo "Creating filtered copy..."
cd "$TEMP_DIR"
git clone --no-hardlinks "$PRIVATE_REPO_PATH" private-copy
cd private-copy

# Apply filtering
echo "Filtering repository content..."

# Remove sensitive directories entirely
rm -rf watchgate-tui/
rm -rf docs/todos/
rm -rf scripts/private/
find . -name "*.private" -delete
find . -name ".env*" -delete

# Filter sensitive files from remaining directories
echo "Filtering sensitive content..."

# Filter ADRs to remove business-sensitive information
mkdir -p docs/decision-records-public/
for adr in docs/decision-records/*.md; do
    if [[ -f "$adr" ]]; then
        # Process each ADR to remove business-sensitive sections
        python ../scripts/filter-adr.py "$adr" "docs/decision-records-public/$(basename "$adr")"
    fi
done
rm -rf docs/decision-records/
mv docs/decision-records-public/ docs/decision-records/

# Update root files for public consumption
echo "Updating public-facing files..."

# Create public README
cat > README.md << 'EOF'
# Watchgate

Open source MCP (Model Context Protocol) security gateway.

## Overview

Watchgate is a security-focused proxy that sits between MCP clients and servers,
providing comprehensive auditing, access control, and threat protection for 
AI tool interactions.

## Features

- **Security Policies**: Configurable rules for MCP tool access
- **Audit Logging**: Comprehensive logging of all MCP interactions  
- **Plugin Architecture**: Extensible security and monitoring capabilities
- **Performance**: High-throughput async proxy with minimal latency
- **Standards Compliant**: Full MCP protocol compatibility

## Installation

```bash
pip install watchgate
```

## Quick Start

```bash
# Install and configure
pip install watchgate
watchgate-gateway --config config.yaml

# For interactive configuration
pip install watchgate[tui]
watchgate
```

## License

Apache License 2.0 - see LICENSE for details.

## Contributing

We welcome contributions! See CONTRIBUTING.md for guidelines.

## Documentation

- [Configuration Guide](docs/)
- [Plugin Development](docs/plugins/)
- [Security Policies](docs/security/)
EOF

# Update pyproject.toml to reflect public package
python ../scripts/update-public-pyproject.py

# Flatten core directory structure
echo "Flattening directory structure..."
mv watchgate-core/watchgate/ .
rm -rf watchgate-core/

# Update imports in tests
echo "Updating test imports..."
find tests/ -name "*.py" -exec sed -i 's/from watchgate_core\./from watchgate./g' {} \;
find tests/ -name "*.py" -exec sed -i 's/import watchgate_core/import watchgate/g' {} \;

# Stage all changes
git add -A
git commit -m "Sync from private repository $(date -I)" || echo "No changes to commit"

# Push to public repository
echo "Pushing to public repository..."
git remote add public "$PUBLIC_REPO_URL"
git push public main --force

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo "Public repository sync complete!"
```

### 4. Content Filtering Scripts

**File: `scripts/filter-adr.py`**
```python
#!/usr/bin/env python3
"""Filter ADRs to remove business-sensitive content"""

import re
import sys
from pathlib import Path


def filter_adr_content(content: str) -> str:
    """Remove business-sensitive sections from ADR content"""
    
    # Remove business context sections
    content = re.sub(
        r'### Business Considerations.*?(?=### |## |$)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove competitive analysis
    content = re.sub(
        r'### Competitive Analysis.*?(?=### |## |$)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove internal timeline references
    content = re.sub(
        r'#### Timeline.*?(?=#### |### |## |$)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Sanitize implementation notes
    content = re.sub(
        r'## Implementation Notes.*?(?=## |$)',
        '## Implementation Notes\n\nSee source code for implementation details.\n',
        content,
        flags=re.DOTALL
    )
    
    return content


def main():
    if len(sys.argv) != 3:
        print("Usage: filter-adr.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        sys.exit(1)
    
    content = input_file.read_text()
    filtered_content = filter_adr_content(content)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(filtered_content)
    
    print(f"Filtered {input_file} -> {output_file}")


if __name__ == "__main__":
    main()
```

**File: `scripts/update-public-pyproject.py`**
```python
#!/usr/bin/env python3
"""Update pyproject.toml for public distribution"""

import re
from pathlib import Path


def update_public_pyproject():
    """Update pyproject.toml for public consumption"""
    
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    # Remove TUI dependencies
    content = re.sub(
        r'"watchgate-tui>=.*?"[,\n]',
        '',
        content
    )
    
    # Update package name to reflect core-only
    content = re.sub(
        r'name = "watchgate"',
        'name = "watchgate"',
        content
    )
    
    # Update description
    content = re.sub(
        r'description = ".*?"',
        'description = "MCP Security Gateway - Open Source Core"',
        content
    )
    
    # Update scripts to core-only
    content = re.sub(
        r'watchgate = "watchgate_tui\.main:tui_main"[,\n]',
        '',
        content
    )
    
    # Remove TUI optional dependencies
    content = re.sub(
        r'tui = \[.*?\][,\n]',
        '',
        content,
        flags=re.DOTALL
    )
    
    pyproject_path.write_text(content)
    print("Updated pyproject.toml for public distribution")


if __name__ == "__main__":
    update_public_pyproject()
```

### 5. GitHub Actions Integration

**File: `.github/workflows/sync-public.yml`**
```yaml
name: Sync Public Repository

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      force_sync:
        description: 'Force sync even without tag'
        required: false
        default: 'false'

jobs:
  sync-public:
    runs-on: ubuntu-latest
    if: github.repository == 'user/watchgate-private'  # Only run on private repo
    
    steps:
    - name: Checkout private repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Need full history for filtering
        token: ${{ secrets.PRIVATE_REPO_TOKEN }}
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install git-filter-repo
      run: |
        pip install git-filter-repo
    
    - name: Configure Git
      run: |
        git config --global user.name "GitHub Actions"
        git config --global user.email "actions@github.com"
    
    - name: Set up SSH key for public repo
      uses: webfactory/ssh-agent@v0.7.0
      with:
        ssh-private-key: ${{ secrets.PUBLIC_REPO_SSH_KEY }}
    
    - name: Sync to public repository
      run: |
        chmod +x scripts/sync-public-repo.sh
        ./scripts/sync-public-repo.sh
      env:
        PUBLIC_REPO_URL: git@github.com:user/watchgate.git
    
    - name: Create release notes
      if: startsWith(github.ref, 'refs/tags/v')
      run: |
        TAG_NAME=${GITHUB_REF#refs/tags/}
        echo "Creating release notes for $TAG_NAME"
        # Add release notes generation logic
```

### 6. Public Repository Setup

**Initial Setup Steps**:

1. **Create public GitHub repository**:
   - Repository name: `watchgate`
   - Description: "Open source MCP security gateway"
   - License: Apache 2.0
   - Initialize with basic README

2. **Configure repository settings**:
   - Enable Issues for community feedback
   - Enable Discussions for community questions
   - Set up branch protection rules
   - Configure security alerts

3. **Add community files**:
   ```
   .github/
   ├── ISSUE_TEMPLATE/
   │   ├── bug_report.md
   │   ├── feature_request.md
   │   └── security_report.md
   ├── PULL_REQUEST_TEMPLATE.md
   ├── CONTRIBUTING.md
   ├── CODE_OF_CONDUCT.md
   └── SECURITY.md
   ```

### 7. Community Guidelines

**File: `CONTRIBUTING.md`**
```markdown
# Contributing to Watchgate

We welcome contributions to the Watchgate core functionality!

## Development Setup

```bash
git clone https://github.com/user/watchgate.git
cd watchgate
pip install -e .[dev]
```

## Running Tests

```bash
pytest tests/ -v
```

## Submitting Changes

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit pull request

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for public APIs
- Keep security considerations in mind

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
```

## Validation Steps

**After initial setup**:

1. **Verify filtering works correctly**:
   ```bash
   ./scripts/sync-public-repo.sh
   # Check public repo contains only intended files
   ```

2. **Test community workflow**:
   - Create test issue on public repo
   - Test fork/clone/contribute workflow
   - Verify documentation is accessible

3. **Validate automation**:
   - Test GitHub Actions workflow
   - Verify release tagging triggers sync
   - Check error handling and notifications

## Success Criteria

- [ ] Public repository contains only open source components
- [ ] Automated sync process works reliably
- [ ] Community can easily contribute to core functionality
- [ ] No sensitive information leaks to public repo
- [ ] Professional presentation for public audience
- [ ] Clear separation between private and public codebases

## Security Considerations

- **Information Leakage**: Ensure no private/business information in public repo
- **API Keys**: Never commit secrets or credentials
- **Business Logic**: Keep competitive advantage information private
- **Development Artifacts**: Filter out temporary files and debug information

## Maintenance Requirements

- **Regular Sync**: Keep public repo reasonably current with core changes
- **Community Management**: Respond to issues and pull requests
- **Documentation**: Maintain public-facing documentation
- **Security Updates**: Promptly address security issues in public repo

## Dependencies

- **GitHub repositories**: Both private and public repos configured
- **SSH keys**: Deploy keys for automated sync
- **CI/CD access**: GitHub Actions permissions configured
- **git-filter-repo**: Tool for repository filtering

## Questions to Resolve

1. **Sync Frequency**: How often should we sync (every release, weekly, etc.)?
2. **Community Management**: Who will manage public repo issues/PRs?
3. **Release Process**: How does public sync integrate with release workflow?
4. **Contribution Workflow**: How do public contributions get merged back to private?

## Future Enhancements

- **Bidirectional Sync**: Mechanism to pull public contributions back to private
- **Automated Testing**: Run tests on public repo after sync
- **Documentation Generation**: Automated API docs for public repo
- **Release Automation**: Automatic release creation on public repo