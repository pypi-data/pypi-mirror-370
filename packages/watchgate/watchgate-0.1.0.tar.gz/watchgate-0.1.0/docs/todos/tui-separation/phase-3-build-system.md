# Phase 3: Build System Setup

## Overview

Set up automated build system for creating and distributing the three packages (watchgate-core, watchgate-tui, watchgate) with proper wheel-only distribution for the TUI component.

## Prerequisites

- Phase 1 (Command Structure) completed
- Phase 2 (Monorepo Setup) completed  
- All three packages building successfully locally

## Objectives

- Create automated build pipeline for all packages
- Set up wheel-only distribution for TUI (no source code)
- Prepare for PyPI publishing (actual publishing deferred)
- Ensure version synchronization across packages
- Create release automation scripts

## Current State

After Phase 2:
- Three separate packages with their own pyproject.toml files
- Manual build process using `python -m build`
- No automated version management
- No publishing pipeline

## Target State

- Automated build system that creates all packages
- TUI distributed as wheel-only (compiled bytecode)
- Version synchronization across all packages
- Release scripts ready for PyPI publishing
- CI/CD pipeline configured for automated builds

## Detailed Requirements

### 1. Version Management System

**File: `scripts/update-version.py`**
```python
#!/usr/bin/env python3
"""Update version across all packages"""

import re
import sys
from pathlib import Path


def update_version(new_version: str):
    """Update version in all pyproject.toml files"""
    
    version_pattern = r'version\s*=\s*"[^"]+"'
    new_version_line = f'version = "{new_version}"'
    
    files_to_update = [
        "pyproject.toml",
        "watchgate-core/pyproject.toml", 
        "watchgate-tui/pyproject.toml"
    ]
    
    for file_path in files_to_update:
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: {file_path} not found")
            continue
            
        content = path.read_text()
        updated_content = re.sub(version_pattern, new_version_line, content)
        
        if content != updated_content:
            path.write_text(updated_content)
            print(f"Updated {file_path}")
        else:
            print(f"No changes needed in {file_path}")


def get_current_version():
    """Get current version from main pyproject.toml"""
    content = Path("pyproject.toml").read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        current = get_current_version()
        print(f"Current version: {current}")
        print("Usage: python update-version.py <new_version>")
        print("Example: python update-version.py 0.1.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format (basic)
    if not re.match(r'\d+\.\d+\.\d+', new_version):
        print("Error: Version must be in format X.Y.Z")
        sys.exit(1)
    
    update_version(new_version)
    print(f"Version updated to {new_version}")
```

### 2. TUI Compilation Setup

**File: `scripts/compile-tui.py`**
```python
#!/usr/bin/env python3
"""Compile TUI to bytecode for distribution"""

import py_compile
import shutil
import sys
from pathlib import Path


def compile_tui_directory(source_dir: Path, target_dir: Path):
    """Compile Python files to bytecode"""
    
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    target_dir.mkdir(parents=True)
    
    for py_file in source_dir.rglob("*.py"):
        # Calculate relative path
        rel_path = py_file.relative_to(source_dir)
        
        # Create target directory structure
        target_file = target_dir / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Compile to bytecode
        try:
            py_compile.compile(py_file, target_file.with_suffix('.pyc'), doraise=True)
            print(f"Compiled: {rel_path}")
        except Exception as e:
            print(f"Failed to compile {rel_path}: {e}")
            return False
    
    return True


def create_init_files(target_dir: Path):
    """Create __init__.py files to make packages importable"""
    
    for pyc_file in target_dir.rglob("*.pyc"):
        init_file = pyc_file.parent / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"Created: {init_file.relative_to(target_dir)}")


if __name__ == "__main__":
    source_dir = Path("watchgate-tui/watchgate_tui")
    target_dir = Path("build/compiled-tui/watchgate_tui")
    
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} not found")
        sys.exit(1)
    
    print("Compiling TUI to bytecode...")
    
    if compile_tui_directory(source_dir, target_dir):
        create_init_files(target_dir)
        print("TUI compilation successful")
    else:
        print("TUI compilation failed")
        sys.exit(1)
```

### 3. Build Pipeline Scripts

**File: `scripts/build-packages.sh`**
```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting package build process...${NC}"

# Validate current directory
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}Error: Must run from project root${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build/
rm -rf dist/
rm -rf watchgate-core/dist/
rm -rf watchgate-core/build/
rm -rf watchgate-tui/dist/
rm -rf watchgate-tui/build/

# Build core package (source + wheel)
echo -e "${YELLOW}Building watchgate-core...${NC}"
cd watchgate-core
python -m build
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Failed to build watchgate-core${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✓ watchgate-core built successfully${NC}"

# Build TUI package (wheel only, compiled bytecode)
echo -e "${YELLOW}Building watchgate-tui...${NC}"

# Option 1: Simple wheel (recommended for Phase 3)
cd watchgate-tui
python -m build --wheel
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Failed to build watchgate-tui${NC}"
    exit 1
fi
cd ..

# Option 2: Compiled bytecode (uncomment if desired)
# echo "Compiling TUI bytecode..."
# python scripts/compile-tui.py
# cd watchgate-tui
# # Temporarily replace source with compiled version
# mv watchgate_tui watchgate_tui.source
# cp -r ../build/compiled-tui/watchgate_tui .
# python -m build --wheel
# # Restore source
# rm -rf watchgate_tui
# mv watchgate_tui.source watchgate_tui
# cd ..

echo -e "${GREEN}✓ watchgate-tui built successfully${NC}"

# Build main package
echo -e "${YELLOW}Building main watchgate package...${NC}"
python -m build
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Failed to build main package${NC}"
    exit 1
fi
echo -e "${GREEN}✓ watchgate built successfully${NC}"

# Verify builds
echo -e "${YELLOW}Verifying builds...${NC}"

echo "Core package contents:"
ls -la watchgate-core/dist/

echo -e "\nTUI package contents:"
ls -la watchgate-tui/dist/

echo -e "\nMain package contents:"
ls -la dist/

echo -e "${GREEN}All packages built successfully!${NC}"

# Show install command for testing
echo -e "\n${YELLOW}To test locally:${NC}"
echo "pip install watchgate-core/dist/watchgate_core-*.whl"
echo "pip install watchgate-tui/dist/watchgate_tui-*.whl"  
echo "pip install dist/watchgate-*.whl"
```

### 4. Publishing Preparation Scripts

**File: `scripts/prepare-release.sh`**
```bash
#!/bin/bash
set -e

# This script prepares for release but does not publish
# Actual publishing is deferred to pre-launch phase

VERSION=$1
if [[ -z "$VERSION" ]]; then
    echo "Usage: ./prepare-release.sh <version>"
    echo "Example: ./prepare-release.sh 0.1.0"
    exit 1
fi

echo "Preparing release $VERSION..."

# Update versions
python scripts/update-version.py $VERSION

# Build all packages
./scripts/build-packages.sh

# Run tests
echo "Running tests..."
pytest tests/ -v

if [[ $? -ne 0 ]]; then
    echo "Tests failed! Aborting release."
    exit 1
fi

# Create release directory
RELEASE_DIR="releases/$VERSION"
mkdir -p "$RELEASE_DIR"

# Copy built packages
cp watchgate-core/dist/* "$RELEASE_DIR/"
cp watchgate-tui/dist/* "$RELEASE_DIR/"
cp dist/* "$RELEASE_DIR/"

# Create release notes template
cat > "$RELEASE_DIR/RELEASE_NOTES.md" << EOF
# Release $VERSION

## Changes

- [Add your changes here]

## Installation

\`\`\`bash
pip install watchgate==$VERSION
\`\`\`

## Files

Core package (Apache 2.0):
- watchgate_core-$VERSION.tar.gz (source)
- watchgate_core-$VERSION-py3-none-any.whl

TUI package (Proprietary):
- watchgate_tui-$VERSION-py3-none-any.whl (wheel only)

Main package:
- watchgate-$VERSION.tar.gz (source)
- watchgate-$VERSION-py3-none-any.whl
EOF

echo "Release $VERSION prepared in $RELEASE_DIR"
echo "Review RELEASE_NOTES.md before publishing"

# Show next steps
echo ""
echo "Next steps:"
echo "1. Review files in $RELEASE_DIR"
echo "2. Update $RELEASE_DIR/RELEASE_NOTES.md"
echo "3. Create git tag: git tag v$VERSION"
echo "4. Publish when ready (see publishing scripts)"
```

### 5. GitHub Actions Workflow

**File: `.github/workflows/build-packages.yml`**
```yaml
name: Build Packages

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ created ]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build pytest pytest-asyncio
    
    - name: Install packages in development mode
      run: |
        pip install -e watchgate-core/
        pip install -e watchgate-tui/
        pip install -e .
    
    - name: Run tests
      run: |
        pytest tests/ -v
    
    - name: Build packages
      run: |
        ./scripts/build-packages.sh
    
    - name: Test installation from wheels
      run: |
        # Create fresh virtual environment for testing
        python -m venv test-env
        source test-env/bin/activate
        
        # Install from built wheels
        pip install watchgate-core/dist/watchgate_core-*.whl
        pip install watchgate-tui/dist/watchgate_tui-*.whl
        pip install dist/watchgate-*.whl
        
        # Test commands
        watchgate --help
        watchgate-gateway --help
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      if: matrix.python-version == '3.11'  # Only upload once
      with:
        name: packages
        path: |
          watchgate-core/dist/
          watchgate-tui/dist/
          dist/
```

### 6. Dependency Management

**File: `scripts/check-dependencies.py`**
```python
#!/usr/bin/env python3
"""Check dependency consistency across packages"""

import re
from pathlib import Path


def extract_dependencies(pyproject_path: Path):
    """Extract dependencies from pyproject.toml"""
    content = pyproject_path.read_text()
    
    # Find dependencies section
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not deps_match:
        return []
    
    deps_text = deps_match.group(1)
    deps = re.findall(r'"([^"]+)"', deps_text)
    
    return deps


def normalize_dep(dep: str):
    """Normalize dependency for comparison"""
    # Extract package name (before version specifiers)
    match = re.match(r'^([a-zA-Z0-9_-]+)', dep)
    return match.group(1) if match else dep


def check_consistency():
    """Check dependency consistency across packages"""
    
    packages = {
        "main": Path("pyproject.toml"),
        "core": Path("watchgate-core/pyproject.toml"),
        "tui": Path("watchgate-tui/pyproject.toml")
    }
    
    all_deps = {}
    
    for name, path in packages.items():
        if path.exists():
            deps = extract_dependencies(path)
            all_deps[name] = {normalize_dep(dep): dep for dep in deps}
            print(f"{name}: {len(deps)} dependencies")
        else:
            print(f"Warning: {path} not found")
    
    # Check for version conflicts
    conflicts = []
    
    # Common dependencies that should have same versions
    common_deps = set()
    if "core" in all_deps and "tui" in all_deps:
        core_names = set(all_deps["core"].keys())
        tui_names = set(all_deps["tui"].keys())
        common_deps = core_names & tui_names
    
    for dep_name in common_deps:
        core_version = all_deps["core"][dep_name]
        tui_version = all_deps["tui"][dep_name]
        
        if core_version != tui_version:
            conflicts.append(f"{dep_name}: core='{core_version}' vs tui='{tui_version}'")
    
    if conflicts:
        print("\nDependency conflicts found:")
        for conflict in conflicts:
            print(f"  {conflict}")
        return False
    else:
        print("\nNo dependency conflicts found")
        return True


if __name__ == "__main__":
    import sys
    
    if not check_consistency():
        sys.exit(1)
```

### 7. Local Testing Scripts

**File: `scripts/test-installation.sh`**
```bash
#!/bin/bash
set -e

echo "Testing package installation..."

# Create temporary directory for testing
TEST_DIR=$(mktemp -d)
echo "Using test directory: $TEST_DIR"

# Create virtual environment
python -m venv "$TEST_DIR/venv"
source "$TEST_DIR/venv/bin/activate"

# Install packages
echo "Installing watchgate-core..."
pip install watchgate-core/dist/watchgate_core-*.whl

echo "Installing watchgate-tui..."
pip install watchgate-tui/dist/watchgate_tui-*.whl

echo "Installing main package..."
pip install dist/watchgate-*.whl

# Test commands
echo "Testing commands..."

echo "Testing watchgate --help:"
watchgate --help

echo "Testing watchgate-gateway --help:"
watchgate-gateway --help

# Test imports
echo "Testing imports..."
python -c "import watchgate_core; print('✓ Core import successful')"
python -c "import watchgate_tui; print('✓ TUI import successful')" 

# Test with dummy config
if [[ -f "configs/dummy/basic.yaml" ]]; then
    echo "Testing config validation..."
    watchgate-gateway --config configs/dummy/basic.yaml --validate-only
    echo "✓ Config validation successful"
fi

echo "All installation tests passed!"

# Cleanup
deactivate
rm -rf "$TEST_DIR"
```

## Validation Steps

**After implementing build system:**

1. **Test version management:**
   ```bash
   python scripts/update-version.py 0.1.1
   python scripts/check-dependencies.py
   ```

2. **Test build process:**
   ```bash
   ./scripts/build-packages.sh
   ```

3. **Test local installation:**
   ```bash
   ./scripts/test-installation.sh
   ```

4. **Test release preparation:**
   ```bash
   ./scripts/prepare-release.sh 0.1.0
   ```

5. **Verify CI/CD:**
   - Push to GitHub and check Actions run successfully
   - Verify artifacts are created correctly

## Success Criteria

- [ ] All packages build successfully via automation
- [ ] Version synchronization works across packages
- [ ] TUI distributes as wheel-only (no source)
- [ ] Local testing scripts validate installation
- [ ] CI/CD pipeline runs and passes
- [ ] Release preparation creates correct artifacts
- [ ] Dependency consistency is maintained
- [ ] Commands work correctly after automated build

## Dependencies

- Phases 1 and 2 must be completed
- GitHub Actions runner configured
- PyPI accounts prepared (for future publishing)

## Next Steps

After Phase 3:
- License header updates (deferred todo)
- Documentation updates (deferred todo) 
- Public repository sync setup (deferred todo)
- PyPI publishing configuration (deferred todo)

## Implementation Notes

### Build Strategy

- **Core**: Source + wheel distribution (full transparency)
- **TUI**: Wheel-only distribution (source protection)
- **Main**: Standard source + wheel (depends on both)

### Security Considerations

- TUI wheel compilation protects source code
- Version pinning prevents dependency confusion
- CI/CD pipeline uses secure artifact handling

### Rollback Plan

If build system fails:
1. Revert scripts and CI/CD changes
2. Continue with manual build process
3. Fix issues and retry automation

### Performance Impact

- Build time increases due to multiple packages
- CI/CD runs take longer but provide better validation
- No runtime performance impact