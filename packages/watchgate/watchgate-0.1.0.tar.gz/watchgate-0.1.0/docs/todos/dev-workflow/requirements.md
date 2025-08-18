# Development Workflow Requirements

## Overview

Establish comprehensive development workflow and tooling for the new monorepo structure with dual-licensed packages, ensuring efficient development while maintaining separation between core and TUI components.

## Context

With the new monorepo structure (core + TUI packages), we need development workflows that:
- Support efficient local development and testing
- Maintain clear separation between open source and proprietary components
- Enable automated testing and validation
- Provide consistent development experience across team members
- Integrate with CI/CD pipeline

## Objectives

- Create efficient local development setup
- Establish testing workflows for both packages
- Implement automated quality checks
- Configure CI/CD pipeline for multi-package builds
- Document development processes for new contributors

## Detailed Requirements

### 1. Local Development Setup

**File**: `scripts/dev-setup.sh`

```bash
#!/bin/bash
set -e

echo "Setting up Watchgate development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.11"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "Error: Python 3.11+ required, found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
if [[ ! -d ".venv" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core package in development mode
echo "Installing watchgate-core in development mode..."
pip install -e watchgate-core/[dev]

# Install TUI package in development mode
echo "Installing watchgate-tui in development mode..."
pip install -e watchgate-tui/

# Install main package in development mode
echo "Installing main package in development mode..."
pip install -e .[dev]

# Install additional development tools
echo "Installing development tools..."
pip install \
    pre-commit \
    tox \
    coverage \
    pytest-xdist \
    pytest-mock

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Verify installation
echo "Verifying installation..."
python -c "import watchgate_core; print('✓ Core import successful')"
python -c "import watchgate_tui; print('✓ TUI import successful')"

# Test commands
watchgate --help > /dev/null && echo "✓ watchgate command works"
watchgate-gateway --help > /dev/null && echo "✓ watchgate-gateway command works"

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "To activate environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  ./scripts/test-all.sh"
echo ""
echo "To run code quality checks:"
echo "  ./scripts/check-quality.sh"
```

### 2. Testing Workflow

**File**: `scripts/test-all.sh`

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Running comprehensive test suite...${NC}"

# Ensure we're in the right place
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}Error: Must run from project root${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
fi

# Test core package
echo -e "${YELLOW}Testing watchgate-core...${NC}"
cd watchgate-core
python -m pytest tests/ -v --cov=watchgate --cov-report=xml --cov-report=term
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Core tests failed!${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✓ Core tests passed${NC}"

# Test TUI package
echo -e "${YELLOW}Testing watchgate-tui...${NC}"
cd watchgate-tui
python -m pytest tests/ -v --cov=watchgate_tui --cov-report=xml --cov-report=term
if [[ $? -ne 0 ]]; then
    echo -e "${RED}TUI tests failed!${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✓ TUI tests passed${NC}"

# Test integration
echo -e "${YELLOW}Running integration tests...${NC}"
python -m pytest tests/ -v -m "integration"
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Integration tests failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Integration tests passed${NC}"

# Test full package installation
echo -e "${YELLOW}Testing package installation...${NC}"
./scripts/test-installation.sh
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Installation test failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Installation test passed${NC}"

echo -e "${GREEN}All tests passed! 🎉${NC}"
```

**File**: `scripts/test-fast.sh`

```bash
#!/bin/bash
set -e

# Fast test runner for development
echo "Running fast test suite..."

# Run only unit tests, skip integration and slow tests
python -m pytest tests/ -v -x -m "not integration and not slow" --tb=short

echo "Fast tests complete!"
```

### 3. Code Quality Checks

**File**: `scripts/check-quality.sh`

```bash
#!/bin/bash
set -e

echo "Running code quality checks..."

# Activate virtual environment if available
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
fi

EXIT_CODE=0

# Run black formatter check
echo "Checking code formatting with black..."
black --check --diff watchgate-core/ watchgate-tui/ scripts/ || {
    echo "❌ Code formatting issues found"
    echo "Run: black watchgate-core/ watchgate-tui/ scripts/"
    EXIT_CODE=1
}

# Run ruff linter
echo "Running ruff linter..."
ruff check watchgate-core/ watchgate-tui/ scripts/ || {
    echo "❌ Linting issues found"
    echo "Run: ruff check --fix watchgate-core/ watchgate-tui/ scripts/"
    EXIT_CODE=1
}

# Run mypy type checking on core
echo "Type checking core with mypy..."
cd watchgate-core
mypy watchgate/ || {
    echo "❌ Type checking issues in core"
    EXIT_CODE=1
}
cd ..

# Run mypy type checking on TUI
echo "Type checking TUI with mypy..."
cd watchgate-tui
mypy watchgate_tui/ || {
    echo "❌ Type checking issues in TUI"
    EXIT_CODE=1
}
cd ..

# Check import sorting
echo "Checking import sorting..."
isort --check-only --diff watchgate-core/ watchgate-tui/ scripts/ || {
    echo "❌ Import sorting issues found"
    echo "Run: isort watchgate-core/ watchgate-tui/ scripts/"
    EXIT_CODE=1
}

# Security check with bandit
echo "Running security check..."
bandit -r watchgate-core/watchgate/ watchgate-tui/watchgate_tui/ -f json -o bandit-report.json || {
    echo "❌ Security issues found - see bandit-report.json"
    EXIT_CODE=1
}

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ All quality checks passed!"
else
    echo "❌ Quality checks failed"
fi

exit $EXIT_CODE
```

**File**: `scripts/fix-quality.sh`

```bash
#!/bin/bash
set -e

echo "Fixing code quality issues..."

# Activate virtual environment if available
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
fi

# Auto-fix formatting
echo "Fixing code formatting..."
black watchgate-core/ watchgate-tui/ scripts/

# Auto-fix import sorting
echo "Fixing import sorting..."
isort watchgate-core/ watchgate-tui/ scripts/

# Auto-fix linting issues where possible
echo "Fixing linting issues..."
ruff check --fix watchgate-core/ watchgate-tui/ scripts/

echo "Quality fixes applied. Run ./scripts/check-quality.sh to verify."
```

### 4. Pre-commit Configuration

**File**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=88]
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
        files: ^(watchgate-core|watchgate-tui)/
```

### 5. Development Makefile

**File**: `Makefile`

```makefile
.PHONY: help setup test test-fast quality fix build clean install dev

# Default target
help:
	@echo "Watchgate Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  setup     - Set up development environment"
	@echo "  install   - Install packages in development mode"
	@echo ""
	@echo "Testing:"
	@echo "  test      - Run full test suite"
	@echo "  test-fast - Run fast tests only"
	@echo "  coverage  - Generate test coverage report"
	@echo ""
	@echo "Quality:"
	@echo "  quality   - Run code quality checks"
	@echo "  fix       - Auto-fix code quality issues"
	@echo "  lint      - Run linter only"
	@echo "  format    - Run formatter only"
	@echo ""
	@echo "Build:"
	@echo "  build     - Build all packages"
	@echo "  clean     - Clean build artifacts"
	@echo ""
	@echo "Development:"
	@echo "  dev       - Set up and run in development mode"

setup:
	./scripts/dev-setup.sh

install:
	pip install -e watchgate-core/[dev]
	pip install -e watchgate-tui/
	pip install -e .[dev]

test:
	./scripts/test-all.sh

test-fast:
	./scripts/test-fast.sh

coverage:
	python -m pytest tests/ --cov=watchgate_core --cov=watchgate_tui --cov-report=html
	@echo "Coverage report generated in htmlcov/"

quality:
	./scripts/check-quality.sh

fix:
	./scripts/fix-quality.sh

lint:
	ruff check watchgate-core/ watchgate-tui/ scripts/

format:
	black watchgate-core/ watchgate-tui/ scripts/
	isort watchgate-core/ watchgate-tui/ scripts/

build:
	./scripts/build-packages.sh

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf watchgate-core/build/ watchgate-core/dist/ watchgate-core/*.egg-info/
	rm -rf watchgate-tui/build/ watchgate-tui/dist/ watchgate-tui/*.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

dev: setup
	@echo "Development environment ready!"
	@echo "Run 'source .venv/bin/activate' to activate"
```

### 6. VS Code Configuration

**File**: `.vscode/settings.json`

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": [
        "--profile=black"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".coverage": true,
        "htmlcov/": true,
        "*.egg-info/": true,
        "build/": true,
        "dist/": true
    },
    "search.exclude": {
        "**/node_modules": true,
        "**/bower_components": true,
        "**/.venv": true,
        "**/htmlcov": true
    }
}
```

**File**: `.vscode/launch.json`

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Watchgate TUI",
            "type": "python",
            "request": "launch",
            "module": "watchgate_tui.main",
            "args": ["--config", "configs/dummy/basic.yaml"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Watchgate Gateway",
            "type": "python",
            "request": "launch",
            "module": "watchgate_core.main",
            "args": ["--config", "configs/dummy/basic.yaml"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

**File**: `.vscode/tasks.json`

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "./scripts/test-all.sh",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Fast Tests",
            "type": "shell",
            "command": "./scripts/test-fast.sh",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Quality Check",
            "type": "shell",
            "command": "./scripts/check-quality.sh",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Build Packages",
            "type": "shell",
            "command": "./scripts/build-packages.sh",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

### 7. CI/CD Pipeline Enhancement

**File**: `.github/workflows/development.yml`

```yaml
name: Development Workflow

on:
  push:
    branches: [ main, develop, 'feature/*' ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black ruff mypy isort bandit
    
    - name: Check code formatting
      run: black --check --diff watchgate-core/ watchgate-tui/ scripts/
    
    - name: Run linter
      run: ruff check watchgate-core/ watchgate-tui/ scripts/
    
    - name: Check import sorting
      run: isort --check-only --diff watchgate-core/ watchgate-tui/ scripts/
    
    - name: Type checking
      run: |
        cd watchgate-core && mypy watchgate/
        cd ../watchgate-tui && mypy watchgate_tui/
    
    - name: Security check
      run: bandit -r watchgate-core/watchgate/ watchgate-tui/watchgate_tui/

  test:
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
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e watchgate-core/[dev]
        pip install -e watchgate-tui/
        pip install -e .[dev]
    
    - name: Run tests
      run: ./scripts/test-all.sh
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.11'
      with:
        files: ./watchgate-core/coverage.xml,./watchgate-tui/coverage.xml

  build:
    runs-on: ubuntu-latest
    needs: [quality, test]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build
        pip install -e watchgate-core/
        pip install -e watchgate-tui/
        pip install -e .
    
    - name: Build packages
      run: ./scripts/build-packages.sh
    
    - name: Test installation
      run: ./scripts/test-installation.sh
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: packages-${{ github.sha }}
        path: |
          watchgate-core/dist/
          watchgate-tui/dist/
          dist/
```

### 8. Development Documentation

**File**: `docs/development.md`

```markdown
# Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- Make (optional, for convenience commands)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/user/watchgate-private.git
   cd watchgate
   ```

2. Set up development environment:
   ```bash
   ./scripts/dev-setup.sh
   # or
   make setup
   ```

3. Activate virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Project Structure

```
watchgate/
├── watchgate-core/          # Open source core (Apache 2.0)
├── watchgate-tui/           # Proprietary TUI (Freeware)
├── tests/                   # Integration tests
├── scripts/                 # Development scripts
├── docs/                    # Documentation
└── configs/                 # Example configurations
```

## Development Workflow

### Daily Development

```bash
# Run fast tests during development
make test-fast

# Check code quality
make quality

# Fix common issues automatically
make fix

# Run full test suite before committing
make test
```

### Code Standards

- **Formatting**: Black with 88-character line length
- **Linting**: Ruff for modern Python linting
- **Type Checking**: MyPy for static type analysis
- **Import Sorting**: isort with Black profile
- **Security**: Bandit for security issue detection

### Testing

- **Unit Tests**: Fast tests for individual components
- **Integration Tests**: Tests for component interaction
- **Installation Tests**: Verify packages install and work correctly
- **Coverage**: Maintain >90% test coverage

### Working with Packages

Each package (core, TUI, main) can be developed independently:

```bash
# Work on core only
cd watchgate-core
pytest tests/

# Work on TUI only  
cd watchgate-tui
pytest tests/

# Test integration
cd ..
pytest tests/
```

## Contributing

### Before Committing

1. Run quality checks: `make quality`
2. Run tests: `make test`
3. Ensure pre-commit hooks are installed: `pre-commit install`

### Pull Request Process

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Make changes with tests
3. Ensure all checks pass
4. Submit pull request with clear description

### Code Review Guidelines

- Focus on security implications
- Verify test coverage for new features
- Check for breaking changes
- Ensure documentation is updated

## Debugging

### TUI Issues

```bash
# Run TUI with debug logging
watchgate --verbose

# Use simplified terminal if TUI fails
TERM=xterm watchgate
```

### Gateway Issues

```bash
# Test configuration validation
watchgate-gateway --config config.yaml --validate-only

# Run with debug logging
watchgate-gateway --config config.yaml --verbose
```

### Test Issues

```bash
# Run specific test
pytest tests/unit/test_specific.py -v

# Run with debug output
pytest tests/ -v -s

# Run without coverage for faster execution
pytest tests/ --no-cov
```

## Performance Profiling

```bash
# Profile gateway startup
python -m cProfile -o gateway.prof -m watchgate_core.main --config config.yaml

# Profile TUI startup
python -m cProfile -o tui.prof -m watchgate_tui.main
```

## Release Process

See [Release Guide](release.md) for complete release procedures.

## Common Issues

### Import Errors

If you see import errors after making changes:

```bash
# Reinstall in development mode
pip install -e watchgate-core/
pip install -e watchgate-tui/
pip install -e .
```

### Test Failures

If tests fail unexpectedly:

```bash
# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Reinstall packages
make install
```

### Quality Check Failures

```bash
# Auto-fix most issues
make fix

# Check what remains
make quality
```
```

## Success Criteria

- [ ] Efficient local development setup with single command
- [ ] Comprehensive testing workflow for all packages
- [ ] Automated code quality checks and fixes
- [ ] CI/CD pipeline validates all changes
- [ ] VS Code integration provides smooth development experience
- [ ] Clear documentation for new developers
- [ ] Pre-commit hooks prevent common issues
- [ ] Performance profiling tools available

## Dependencies

- Phase 2 (Monorepo Setup) must be completed
- Package structure must be finalized
- Testing framework must be established

## Timeline

- **Week 1**: Set up scripts and Makefile
- **Week 2**: Configure CI/CD pipeline and pre-commit hooks
- **Week 3**: Create VS Code configuration and documentation
- **Week 4**: Test workflow with team and refine

## Maintenance

Development workflow should be updated when:
- New packages are added
- Testing requirements change
- Quality standards evolve
- CI/CD platform changes
- Development tools are updated