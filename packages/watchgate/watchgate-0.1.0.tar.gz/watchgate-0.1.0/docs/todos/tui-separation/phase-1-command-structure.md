# Phase 1: Command Structure Implementation

## Overview

Implement the new command structure to replace `watchgate proxy` with `watchgate-gateway` as decided in ADR-019. This is the first phase of TUI separation and focuses on command structure changes only.

## Objectives

- Replace `watchgate proxy` command with `watchgate-gateway`
- Update all tests to use the new command structure
- Ensure no backward compatibility is needed (pre-release)
- Maintain current functionality while improving terminology clarity

## Current State

**Current Commands:**
```bash
watchgate                      # Launches TUI
watchgate proxy --config file  # Runs proxy/gateway
```

**Target Commands:**
```bash
watchgate                        # Launches TUI (unchanged)
watchgate-gateway --config file  # Runs proxy/gateway (renamed)
```

## Detailed Requirements

### 1. Update Main Entry Points

**File: `pyproject.toml`**

Current:
```toml
[project.scripts]
watchgate = "watchgate.main:main"
```

Required:
```toml
[project.scripts]
watchgate = "watchgate.main:tui_main"
watchgate-gateway = "watchgate.main:gateway_main"
```

### 2. Refactor Main Module

**File: `watchgate/main.py`**

**Add new entry point functions:**
```python
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
    
    # Set up logging
    setup_logging(args.verbose)
    
    try:
        from watchgate.tui import run_tui
        run_tui(args.config)
    except ImportError:
        print("Error: TUI functionality requires the Textual library.")
        print()
        print("Install with TUI support:")
        print("  pip install 'watchgate[tui]'")
        print()
        print("To run the gateway without TUI:")
        print("  watchgate-gateway --config config.yaml")
        sys.exit(1)

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
        # Load and validate config
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

def main():
    """Legacy entry point - remove after Phase 1 complete"""
    # This function should be removed once new entry points are confirmed working
    print("DEPRECATED: Use 'watchgate' for TUI or 'watchgate-gateway' for proxy", 
          file=sys.stderr)
    sys.exit(1)
```

**Extract gateway functionality:**
```python
def run_gateway(config_path: Path, verbose: bool = False):
    """Run Watchgate as MCP gateway/proxy"""
    # Move existing proxy logic here from main()
    # This should contain all the current main() logic for proxy mode
    pass
```

### 3. Update TUI Entry Point

**File: `watchgate/tui/__init__.py`**

Ensure clean interface:
```python
"""Watchgate TUI module"""

def run_tui(config_path: Optional[Path] = None):
    """Launch the Watchgate TUI application"""
    from .app import WatchgateConfigApp
    app = WatchgateConfigApp(config_path)
    app.run()

__all__ = ['run_tui']
```

### 4. Test Updates

**Update all test files that reference the old command structure:**

1. **Find affected tests:**
   ```bash
   grep -r "watchgate proxy" tests/
   grep -r "proxy.*--config" tests/
   ```

2. **Update test patterns:**
   - Replace `watchgate proxy --config` with `watchgate-gateway --config`
   - Update subprocess calls in tests
   - Update documentation strings

3. **Specific files likely to need updates:**
   - `tests/unit/test_tui_invocation.py`
   - Any integration tests that spawn the proxy
   - CLI argument parsing tests

**Example test update:**
```python
# Before
result = subprocess.run(["watchgate", "proxy", "--config", "test.yaml"])

# After  
result = subprocess.run(["watchgate-gateway", "--config", "test.yaml"])
```

### 5. Configuration Examples

**Update example configurations and documentation:**

**File: `configs/dummy/basic.yaml` and similar**
- Update any comments that reference the old command structure

**MCP Client Examples:**
```json
{
  "mcpServers": {
    "secure-filesystem": {
      "command": "watchgate-gateway",
      "args": ["--config", "/path/to/watchgate.yaml"]
    }
  }
}
```

### 6. Help Text and Error Messages

**Update help text and error messages throughout codebase:**

1. **Search for references to old command:**
   ```bash
   grep -r "watchgate proxy" watchgate/
   grep -r "proxy.*config" watchgate/
   ```

2. **Update error messages:**
   ```python
   # Example error message update
   print("To run the gateway: watchgate-gateway --config config.yaml")
   ```

### 7. Validation Steps

**After implementation, verify:**

1. **Commands work correctly:**
   ```bash
   # Should launch TUI
   watchgate
   
   # Should launch TUI with specific config
   watchgate --config configs/dummy/basic.yaml
   
   # Should run gateway
   watchgate-gateway --config configs/dummy/basic.yaml
   
   # Should validate config
   watchgate-gateway --config configs/dummy/basic.yaml --validate-only
   ```

2. **Test suite passes:**
   ```bash
   pytest tests/ -v
   ```

3. **No references to old command remain:**
   ```bash
   grep -r "watchgate proxy" . --exclude-dir=.git
   # Should return no results (except this requirements file)
   ```

## Success Criteria

- [ ] `watchgate` command launches TUI successfully
- [ ] `watchgate-gateway --config file` runs the proxy successfully  
- [ ] All tests updated and passing
- [ ] No references to `watchgate proxy` remain in codebase
- [ ] Help text and error messages reference correct commands
- [ ] Both commands handle `--verbose` flag correctly
- [ ] `watchgate-gateway --validate-only` works for config validation

## Dependencies

- None (this is the first phase)

## Next Phase

After completing this phase, proceed to **Phase 2: Monorepo Setup** which will reorganize the codebase structure.

## Implementation Notes

### Testing Strategy

1. Test the new entry points manually first
2. Update tests incrementally, running the suite after each batch
3. Focus on maintaining existing functionality while changing only the command structure

### Rollback Plan

If issues arise:
1. Revert `pyproject.toml` changes
2. Revert `main.py` changes  
3. Restore original test files from git

### Performance Considerations

- No performance impact expected (same code, different entry points)
- Gateway startup time should remain identical

### Error Handling

- Provide clear error messages when users try old commands
- Ensure graceful handling when TUI dependencies are missing
- Validate config files early in gateway startup