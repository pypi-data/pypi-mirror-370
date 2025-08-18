# Phase 2: Monorepo Structure Setup

## Overview

Reorganize the current monolithic structure into a monorepo with separate directories for core functionality and TUI, while maintaining a single installable package. This prepares for future selective publishing capabilities.

## Prerequisites

- Phase 1 (Command Structure) must be completed
- All tests passing with new command structure

## Objectives

- Split codebase into logical core and TUI components
- Maintain current single-package installation model
- Prepare structure for future selective publishing
- Keep development workflow simple and unified

## Current State

```
watchgate/
├── watchgate/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   ├── proxy/
│   ├── plugins/
│   └── tui/
├── pyproject.toml
├── LICENSE
└── tests/
```

## Target State

```
watchgate/
├── watchgate-core/              # Apache 2.0 core functionality
│   ├── watchgate/
│   │   ├── __init__.py
│   │   ├── main.py              # gateway_main() only
│   │   ├── config/
│   │   ├── proxy/
│   │   └── plugins/
│   ├── pyproject.toml           # Core package definition
│   ├── LICENSE                  # Apache 2.0
│   └── README.md
├── watchgate-tui/               # Proprietary TUI functionality  
│   ├── watchgate_tui/
│   │   ├── __init__.py
│   │   ├── main.py              # tui_main() function
│   │   ├── app.py
│   │   └── screens/
│   ├── pyproject.toml           # TUI package definition
│   ├── LICENSE.PROPRIETARY      # Proprietary freeware
│   └── README.md
├── pyproject.toml               # Main package (depends on both)
├── LICENSE                      # Apache 2.0 (covers main package)
├── tests/                       # All tests remain here
├── docs/                        # All documentation
└── scripts/                     # Build and release scripts
```

## Detailed Requirements

### 1. Create Core Package Structure

**Create directory: `watchgate-core/`**

**File: `watchgate-core/pyproject.toml`**
```toml
[project]
name = "watchgate-core"
version = "0.1.0"
description = "Watchgate MCP Security Gateway - Core Functionality"
readme = "README.md"
license = {text = "Apache-2.0"}
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0.2",
    "aiohttp>=3.12.4", 
    "pydantic>=2.11.5",
    "pathspec>=0.12.1",
]
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]

[project.scripts]
watchgate-gateway = "watchgate.main:gateway_main"

[project.optional-dependencies]
dev = [
    "pytest>=8.3.5",
    "pytest-asyncio>=1.0.0",
    "pytest-cov>=6.1.1",
    "black>=25.1.0",
    "ruff>=0.11.12",
    "mypy>=1.16.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
testpaths = ["../tests/unit", "../tests/integration"]
```

**File: `watchgate-core/README.md`**
```markdown
# Watchgate Core

Core MCP security gateway functionality for Watchgate.

This package provides the essential proxy, security, and auditing capabilities 
that make up the Watchgate Security Gateway. It can be used standalone or as 
part of the full Watchgate package with TUI.

## Installation

```bash
# Standalone core (gateway only)
pip install watchgate-core

# Full package with TUI
pip install watchgate
```

## Usage

```bash
watchgate-gateway --config config.yaml
```

## License

Apache License 2.0 - see LICENSE file for details.
```

**File: `watchgate-core/LICENSE`**
```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

[Full Apache 2.0 license text]
```

### 2. Move Core Components

**Move these directories from `watchgate/` to `watchgate-core/watchgate/`:**
- `config/`
- `proxy/`  
- `plugins/`

**Update `watchgate-core/watchgate/__init__.py`:**
```python
"""Watchgate Core - MCP Security Gateway"""

__version__ = "0.1.0"

# Core exports
from .config.loader import ConfigLoader
from .config.models import ProxyConfig
from .plugins.manager import PluginManager

__all__ = [
    'ConfigLoader',
    'ProxyConfig', 
    'PluginManager',
]
```

**Create `watchgate-core/watchgate/main.py`:**
```python
"""Main entry point for Watchgate Gateway"""

import argparse
import logging
import sys
from pathlib import Path

from .config.loader import ConfigLoader
from .proxy.server import MCPProxy


def gateway_main():
    """Entry point for gateway (watchgate-gateway command)"""
    parser = argparse.ArgumentParser(
        description="Watchgate Security Gateway for MCP"
    )
    parser.add_argument("--config", type=Path, required=True,
                       help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--validate-only", action="store_true",
                       help="Validate configuration and exit")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    if args.validate_only:
        try:
            loader = ConfigLoader()
            config = loader.load_from_file(args.config)
            print(f"Configuration valid: {args.config}")
            sys.exit(0)
        except Exception as e:
            print(f"Configuration invalid: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Run the gateway
    run_gateway(args.config, args.verbose)


def setup_logging(verbose: bool = False):
    """Configure logging for the gateway"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
    )


def run_gateway(config_path: Path, verbose: bool = False):
    """Run Watchgate as MCP gateway/proxy"""
    # Implementation moved from original main.py
    # This contains the proxy server logic
    pass


if __name__ == "__main__":
    gateway_main()
```

### 3. Create TUI Package Structure

**Create directory: `watchgate-tui/`**

**File: `watchgate-tui/pyproject.toml`**
```toml
[project]
name = "watchgate-tui"
version = "0.1.0"
description = "Watchgate TUI - Terminal User Interface for Watchgate Configuration"
readme = "README.md"
license = {text = "Proprietary - See LICENSE.PROPRIETARY"}
requires-python = ">=3.11"
dependencies = [
    "watchgate-core>=0.1.0",
    "textual>=0.47.0",
]
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]

[project.scripts]
watchgate = "watchgate_tui.main:tui_main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Prevent source distribution creation
[tool.setuptools]
include-package-data = false
```

**File: `watchgate-tui/README.md`**
```markdown
# Watchgate TUI

Terminal User Interface for Watchgate Security Gateway configuration.

This package provides an intuitive visual interface for configuring Watchgate
security policies, managing MCP servers, and monitoring gateway status.

## Installation

```bash
# Full Watchgate package (recommended)
pip install watchgate

# TUI package only (advanced users)
pip install watchgate-tui
```

## Usage

```bash
watchgate                        # Launch TUI
watchgate --config config.yaml   # Launch with specific config
```

## License

Proprietary freeware - see LICENSE.PROPRIETARY for details.
```

**File: `watchgate-tui/LICENSE.PROPRIETARY`**
```
Watchgate TUI - Proprietary Freeware License

Copyright (c) 2024 [Your Name]

Permission is hereby granted to use this software free of charge, subject to 
the following conditions:

1. The software may be used for any legal purpose
2. The software may NOT be redistributed as part of commercial products
3. The software may NOT be rebranded or white-labeled  
4. The software may NOT be included in competitive products

This software is provided "as is" without warranty of any kind.

Violators will be pursued under copyright law.
```

### 4. Move TUI Components

**Move `watchgate/tui/` to `watchgate-tui/watchgate_tui/`**

**Update imports in TUI files:**
```python
# Old imports in TUI files
from watchgate.config.loader import ConfigLoader
from watchgate.config.models import ProxyConfig

# New imports  
from watchgate_core.config.loader import ConfigLoader
from watchgate_core.config.models import ProxyConfig
```

**Create `watchgate-tui/watchgate_tui/__init__.py`:**
```python
"""Watchgate TUI - Configuration Interface"""

__version__ = "0.1.0"

from .main import tui_main

__all__ = ['tui_main']
```

**Create `watchgate-tui/watchgate_tui/main.py`:**
```python
"""Main entry point for Watchgate TUI"""

import argparse
import sys
from pathlib import Path
from typing import Optional


def tui_main():
    """Entry point for TUI (watchgate command)"""
    parser = argparse.ArgumentParser(
        description="Watchgate Security Gateway Configuration Interface"
    )
    parser.add_argument("--config", type=Path, 
                       help="Open TUI with specific configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Launch TUI
    run_tui(args.config)


def run_tui(config_path: Optional[Path] = None):
    """Launch the Watchgate TUI application"""
    try:
        from .app import WatchgateConfigApp
        app = WatchgateConfigApp(config_path)
        app.run()
    except Exception as e:
        print(f"Error launching TUI: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    tui_main()
```

### 5. Update Main Package

**Update root `pyproject.toml`:**
```toml
[project]
name = "watchgate"
version = "0.1.0"
description = "Watchgate MCP Security Gateway with TUI"
readme = "README.md"
license = {text = "Apache-2.0"}
requires-python = ">=3.11"
dependencies = [
    "watchgate-core==0.1.0",
    "watchgate-tui==0.1.0",
]
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]

[project.scripts]
watchgate = "watchgate_tui.main:tui_main"
watchgate-gateway = "watchgate_core.main:gateway_main"

[project.optional-dependencies]
dev = [
    "pytest>=8.3.5",
    "pytest-asyncio>=1.0.0",
    "pytest-cov>=6.1.1",
    "black>=25.1.0",
    "ruff>=0.11.12",
    "mypy>=1.16.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
```

**Update root `README.md`:**
```markdown
# Watchgate

A secure MCP (Model Context Protocol) gateway with visual configuration interface.

## Installation

```bash
pip install watchgate
```

## Usage

```bash
# Launch configuration interface
watchgate

# Run as MCP gateway  
watchgate-gateway --config config.yaml
```

## Components

- **watchgate-core**: Core gateway functionality (Apache 2.0)
- **watchgate-tui**: Configuration interface (Proprietary freeware)

## License

Core functionality: Apache License 2.0
TUI interface: Proprietary freeware

See LICENSE files in component directories for details.
```

### 6. Update Tests

**Update test imports:**

1. **Find and update imports in test files:**
   ```bash
   find tests/ -name "*.py" -exec grep -l "from watchgate\." {} \;
   ```

2. **Update import patterns:**
   ```python
   # Old imports
   from watchgate.config.loader import ConfigLoader
   from watchgate.proxy.server import MCPProxy
   
   # New imports
   from watchgate_core.config.loader import ConfigLoader  
   from watchgate_core.proxy.server import MCPProxy
   ```

3. **Update TUI test imports:**
   ```python
   # Old imports
   from watchgate.tui.app import WatchgateConfigApp
   
   # New imports
   from watchgate_tui.app import WatchgateConfigApp
   ```

### 7. Create Build Scripts

**File: `scripts/build-all.sh`**
```bash
#!/bin/bash
set -e

echo "Building all packages..."

# Build core package
echo "Building watchgate-core..."
cd watchgate-core
python -m build
cd ..

# Build TUI package (wheel only)
echo "Building watchgate-tui..."
cd watchgate-tui
python -m build --wheel  # No source distribution
cd ..

# Build main package
echo "Building watchgate..."
python -m build

echo "All packages built successfully!"
```

**File: `scripts/test-all.sh`**
```bash
#!/bin/bash
set -e

echo "Running tests for all packages..."

# Test from root (covers integration)
pytest tests/ -v

echo "All tests passed!"
```

### 8. Update Documentation

**Update any remaining documentation that references old structure:**

1. **ADR files**: Update any that reference import paths
2. **Configuration examples**: Ensure they work with new structure
3. **Development docs**: Update with new directory layout

## Validation Steps

**After reorganization:**

1. **Build all packages:**
   ```bash
   ./scripts/build-all.sh
   ```

2. **Install and test locally:**
   ```bash
   pip install -e watchgate-core/
   pip install -e watchgate-tui/
   pip install -e .
   
   # Test commands
   watchgate --help
   watchgate-gateway --help
   ```

3. **Run test suite:**
   ```bash
   ./scripts/test-all.sh
   ```

4. **Verify imports work:**
   ```python
   # Should work
   import watchgate_core
   import watchgate_tui
   
   # Test entry points
   from watchgate_core.main import gateway_main
   from watchgate_tui.main import tui_main
   ```

## Success Criteria

- [ ] All three packages build successfully
- [ ] Commands work: `watchgate` and `watchgate-gateway`
- [ ] All tests pass after import updates
- [ ] TUI can import and use core functionality
- [ ] Core package works independently
- [ ] Main package provides both commands
- [ ] Directory structure is clean and logical

## Rollback Plan

If issues arise:
1. Revert directory moves using git
2. Restore original pyproject.toml
3. Revert test file changes
4. Restore original import structure

## Implementation Notes

### Package Interdependencies

- `watchgate-core`: Standalone, no dependencies on other packages
- `watchgate-tui`: Depends on `watchgate-core`  
- `watchgate`: Depends on both core and TUI packages

### Version Synchronization

All packages must maintain synchronized versions (0.1.0) to avoid dependency conflicts.

### Development Workflow

After this phase:
- Developers can work on core and TUI simultaneously
- Changes to core automatically available to TUI
- Packages can be built and tested independently
- Prepared for selective publishing in future phases