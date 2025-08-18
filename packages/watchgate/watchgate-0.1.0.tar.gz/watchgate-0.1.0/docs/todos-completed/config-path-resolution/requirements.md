# Configuration Path Resolution and Organization

## Feature Overview

Watchgate currently has inconsistent path handling that causes issues when users specify relative paths in configurations. Since Watchgate runs as an MCP server with unpredictable working directories (determined by the MCP client), relative paths often fail to resolve correctly. This feature aims to implement consistent path resolution relative to the configuration file location and organize configuration files in a clear, scalable structure.

## Problem Statement

### Current Path Resolution Issues
1. **Working Directory Dependency**: Relative paths in config files are resolved relative to the working directory where the MCP client started Watchgate
2. **Unpredictable Behavior**: Users can't reliably use relative paths because they don't control the working directory
3. **Tutorial/Example Failures**: Sample configs with relative paths fail when run from different directories
4. **Poor User Experience**: Users must use absolute paths, which aren't portable across systems

### Current Config Organization Issues
1. **Scattered Configs**: Configuration files are spread across the codebase (root, docs/tutorials, etc.)
2. **No Clear Structure**: No standard location for example, tutorial, or environment-specific configs
3. **Discoverability**: Users struggle to find appropriate configuration examples
4. **Maintenance Burden**: Config files in documentation directories are harder to maintain

### Example Scenario
```yaml
# Current behavior - fails if working directory isn't as expected
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        output_file: "./logs/audit.log"  # Fails if CWD isn't project root
```

## Proposed Solution

### Part 1: Path Resolution Strategy

Implement a consistent path resolution strategy where all relative paths in configuration files are resolved relative to the configuration file's location, not the current working directory.

#### Key Principles
1. **Config-Relative Resolution**: All relative paths resolve relative to the config file's parent directory
2. **Explicit Behavior**: Clear, documented path resolution rules
3. **Backward Compatibility**: Absolute paths continue to work unchanged
4. **User Home Support**: Support `~` expansion for user home directory

#### Implementation Components

##### 1. Path Resolution Utility Module (`watchgate/utils/paths.py`)
```python
def resolve_config_path(path: str, config_dir: Path) -> Path:
    """
    Resolve a path from configuration, handling:
    - Absolute paths (returned as-is)
    - Home directory expansion (~)
    - Relative paths (resolved relative to config_dir)
    """
    
def ensure_absolute_path(path: str, base_dir: Path) -> Path:
    """Ensure a path is absolute, resolving relative to base_dir if needed."""
    
def expand_user_path(path: str) -> Path:
    """Expand ~ to user home directory."""
```

##### 2. ConfigLoader Enhancement
- Store the configuration file's directory when loading
- Pass config directory to all components that need path resolution
- Resolve the config file path itself to absolute before loading

##### 3. Plugin Path Resolution
- Update FileAuditingPlugin to resolve `output_file` relative to config directory
- Update any other plugins that use file paths
- Provide config directory context to plugins during initialization

##### 4. Logging Path Resolution
- Update LoggingConfig to resolve log file paths relative to config directory
- Ensure system logging paths are consistently resolved

### Part 2: Configuration Organization

Create a clear, organized structure for configuration files that separates concerns and improves discoverability.

#### Directory Structure
```
watchgate/
├── configs/                           # All configuration files
│   ├── watchgate.yaml               # Default/reference configuration
│   ├── examples/                     # Example configurations
│   │   ├── minimal.yaml             # Minimal working config
│   │   ├── full-example.yaml        # All options documented
│   │   ├── development.yaml         # Development setup
│   │   └── production.yaml          # Production-ready config
│   ├── tutorials/                    # Tutorial configurations
│   │   ├── 1-securing-tool-access.yaml
│   │   ├── 2-implementing-audit-logging.yaml
│   │   ├── 3-protecting-sensitive-content.yaml
│   │   ├── 4-multi-plugin-security.yaml
│   │   └── 5-logging-configuration.yaml
│   └── testing/                      # Test configurations
│       └── test-config.yaml         # Config for test suite
```

#### Migration Plan
1. Create `configs/` directory structure
2. Move existing configs to appropriate subdirectories
3. Update documentation to reference new locations
4. Update tests to use new config paths
5. Add temporary compatibility (symlink or copy in root)

## Implementation Requirements

### Core Requirements

#### R1: Path Resolution Module
- **R1.1**: Create `watchgate/utils/paths.py` with path resolution utilities
- **R1.2**: Support absolute paths (pass-through unchanged)
- **R1.3**: Support home directory expansion (`~` and `~user`)
- **R1.4**: Resolve relative paths relative to config file directory
- **R1.5**: Handle edge cases (empty paths, `.`, `..`, invalid paths)
- **R1.6**: Provide clear error messages for path resolution failures

#### R2: ConfigLoader Updates
- **R2.1**: Store config file's absolute path and directory
- **R2.2**: Pass config directory to schema validation
- **R2.3**: Update `from_schema` methods to accept config directory
- **R2.4**: Resolve config file path to absolute before loading

#### R3: Plugin Path Resolution
- **R3.1**: Update FileAuditingPlugin to use path resolution utilities
- **R3.2**: Resolve `output_file` during plugin initialization
- **R3.3**: Create parent directories if they don't exist (with appropriate permissions)
- **R3.4**: Provide helpful error messages when path resolution fails

#### R4: Configuration Organization
- **R4.1**: Create `configs/` directory structure
- **R4.2**: Move `watchgate.yaml` to `configs/watchgate.yaml`
- **R4.3**: Create `configs/examples/` with documented example configs
- **R4.4**: Move tutorial configs from `docs/user/tutorials/configs/` to `configs/tutorials/`
- **R4.5**: Update all documentation to reference new config locations

### Testing Requirements

#### T1: Path Resolution Tests
- **T1.1**: Test absolute path pass-through
- **T1.2**: Test home directory expansion
- **T1.3**: Test relative path resolution with various inputs
- **T1.4**: Test behavior with symlinks
- **T1.5**: Test error handling for invalid paths
- **T1.6**: Test Unicode path support

#### T2: Integration Tests
- **T2.1**: Test config loading from different working directories
- **T2.2**: Test FileAuditingPlugin with relative paths
- **T2.3**: Test logging configuration with relative paths
- **T2.4**: Test config loading with new directory structure

#### T3: Migration Tests
- **T3.1**: Ensure existing configs continue to work
- **T3.2**: Test config discovery in new locations
- **T3.3**: Verify documentation links are updated

### Documentation Requirements

#### D1: User Documentation
- **D1.1**: Document path resolution behavior in configuration guide
- **D1.2**: Provide examples of relative vs absolute paths
- **D1.3**: Explain config-relative resolution clearly
- **D1.4**: Add troubleshooting section for path issues

#### D2: Migration Guide
- **D2.1**: Document new configuration structure
- **D2.2**: Provide migration instructions for existing users
- **D2.3**: Update all tutorials to use new config locations

#### D3: API Documentation
- **D3.1**: Document path resolution utilities
- **D3.2**: Document config directory parameter in plugin interfaces
- **D3.3**: Update plugin development guide

## Success Criteria

1. **Consistent Path Resolution**: All relative paths resolve predictably relative to config file
2. **Cross-Platform Support**: Path resolution works on Windows, macOS, and Linux
3. **Backward Compatibility**: Existing absolute path configs continue to work
4. **Clear Organization**: Users can easily find appropriate config examples
5. **Robust Error Handling**: Clear error messages when paths can't be resolved
6. **Comprehensive Testing**: >90% test coverage for path resolution code
7. **User-Friendly**: Tutorials and examples work regardless of working directory

## Implementation Plan

### Phase 1: Path Resolution Infrastructure
1. Create path resolution utility module with tests
2. Update ConfigLoader to track config directory
3. Implement path resolution in configuration models

### Phase 2: Plugin Integration
1. Update FileAuditingPlugin to use path resolution
2. Update LoggingConfig to use path resolution
3. Add integration tests for plugin path handling

### Phase 3: Configuration Organization
1. Create new directory structure
2. Move existing configurations
3. Update documentation references
4. Add migration documentation

### Phase 4: Testing and Documentation
1. Run full test suite with different working directories
2. Update all documentation
3. Create migration guide
4. Test tutorials with new structure

## Risk Mitigation

### Risk 1: Breaking Existing Configurations
- **Mitigation**: Maintain backward compatibility for absolute paths
- **Mitigation**: Provide clear migration guide
- **Mitigation**: Add deprecation warnings if needed

### Risk 2: Cross-Platform Path Issues
- **Mitigation**: Use pathlib for all path operations
- **Mitigation**: Test on all supported platforms
- **Mitigation**: Handle platform-specific path formats

### Risk 3: Security Implications
- **Mitigation**: Validate resolved paths don't escape expected directories
- **Mitigation**: Set appropriate file permissions on created directories
- **Mitigation**: Log path resolution for audit purposes

## Related Work

- Similar to Django's `BASE_DIR` approach
- Similar to how mypy resolves paths in config files
- Follows Python logging module's config file path resolution pattern

## Open Questions

1. Should we support environment variable expansion in paths (e.g., `$HOME/logs/`)?
2. Should we provide a `--config-dir` override for CI/CD scenarios?
3. How should we handle path resolution in plugin-provided configurations?
4. Should tutorial configs use relative paths or be self-contained?

## References

- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Django Settings Best Practices](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Click Path Type](https://click.palletsprojects.com/en/stable/types/#path)