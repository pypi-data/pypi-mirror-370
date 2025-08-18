# Configuration Path Resolution Improvements

## Context

After implementing the initial configuration path resolution feature, a code review identified several issues that need to be addressed to improve robustness, consistency, and user experience.

## Issues Identified

### 1. Silent Error Handling in FileAuditingPlugin
The FileAuditingPlugin currently has silent fallback behavior when path resolution fails:
- Falls back to unresolved paths without notifying the user
- Can hide configuration errors leading to logs in unexpected locations
- Uses broad `except Exception` which can mask bugs
- Inconsistent fallback logic between scenarios with/without config_directory

### 2. Implicit Plugin Contract
The current implementation creates an implicit contract where plugins must know to look for the `config_directory` key:
- No formal interface defining path-aware plugins
- Risk of bugs if developers forget to handle config_directory
- Inconsistent implementation across different plugins

### 3. Incomplete Path Resolution Coverage
Path resolution is only implemented for specific components:
- Only logging configuration and file_auditing plugin are covered
- Other plugins like filesystem_server_security use path-like configurations but don't support relative path resolution
- Creates inconsistent behavior across the system

### 4. Documentation Imprecision
The documentation overstates the current implementation:
- Claims "all relative paths" are resolved when only specific fields are covered
- Doesn't clearly explain which configuration fields support path resolution
- Missing guidance on error scenarios and troubleshooting

## Requirements

### R1: Improve Error Handling and Validation
- **R1.1**: Replace silent fallbacks with proper error reporting in FileAuditingPlugin
- **R1.2**: Add comprehensive path validation during configuration loading
- **R1.3**: Provide clear, actionable error messages when path resolution fails
- **R1.4**: Log path resolution decisions for debugging purposes
- **R1.5**: Validate that resolved paths are reasonable and secure

### R2: Formalize Plugin Path Resolution Contract
- **R2.1**: Create explicit `PathResolvablePlugin` interface to formalize the config_directory contract
- **R2.2**: Update PluginManager to use the new interface pattern
- **R2.3**: Provide clear guidelines for plugin developers on implementing path resolution
- **R2.4**: Ensure consistent error handling across all path-aware plugins

### R3: Extend Path Resolution Coverage
- **R3.1**: Add path resolution to filesystem_server_security plugin for `allowed_paths` and `blocked_patterns`
- **R3.2**: Review all existing plugins for path-like configuration fields
- **R3.3**: Implement path resolution for any plugins that use file paths or directory patterns
- **R3.4**: Ensure consistent behavior across all path-aware plugins
- **R3.5**: Update all plugins to use relative paths to config directory where appropriate

### R4: Enhanced Documentation and Examples
- **R4.1**: Fix documentation to precisely describe which fields support path resolution
- **R4.2**: Add clear examples of proper path configuration for each plugin
- **R4.3**: Document error scenarios and troubleshooting guidance
- **R4.4**: Update configuration examples to demonstrate best practices
- **R4.5**: Add migration guide for users updating existing configurations

### R5: Comprehensive Testing and Validation
- **R5.1**: Add early path validation during config loading to catch issues before plugin initialization
- **R5.2**: Extend test coverage for error scenarios and edge cases
- **R5.3**: Add integration tests for all newly covered plugins
- **R5.4**: Test path security to prevent directory traversal issues
- **R5.5**: Verify cross-platform compatibility of path resolution

## Implementation Requirements

### Technical Requirements
- **T1**: Follow Test-Driven Development (TDD) methodology for all new features
- **T2**: Maintain backward compatibility with existing configurations
- **T3**: Ensure cross-platform compatibility (Windows, macOS, Linux)
- **T4**: Implement proper logging for all path resolution operations
- **T5**: Add comprehensive error handling with user-friendly messages

### Documentation Requirements
- **D1**: Update all relevant user documentation to reflect the changes
- **D2**: Update developer documentation for plugin development guidelines
- **D3**: Create troubleshooting guide for path resolution issues
- **D4**: Update configuration examples to demonstrate best practices
- **D5**: Document the new PathResolvablePlugin interface

### Plugin Requirements
- **P1**: All plugins that use file paths or directory patterns must support config-relative path resolution
- **P2**: Plugins must implement the PathResolvablePlugin interface if they handle paths
- **P3**: Plugin error messages must be clear and actionable
- **P4**: Plugin path resolution must be tested with comprehensive test cases

## Success Criteria

1. **No Silent Failures**: All path resolution errors are properly reported to users
2. **Consistent Behavior**: All plugins that use paths behave consistently with config-relative resolution
3. **Clear Interface**: Plugin developers have clear guidance on implementing path resolution
4. **Comprehensive Coverage**: All path-like configuration fields support relative path resolution
5. **Robust Error Handling**: Users receive clear guidance when path configuration is incorrect
6. **Complete Testing**: >90% test coverage for all path resolution functionality
7. **Updated Documentation**: All documentation accurately reflects the current implementation

## Implementation Notes

### TDD Approach Required
- Write failing tests first for each requirement
- Implement minimal code to make tests pass
- Refactor while keeping tests green
- Ensure comprehensive test coverage for all scenarios

### Error Handling Strategy
- Fail fast during configuration loading for invalid paths
- Provide specific error messages with suggested solutions
- Log all path resolution decisions for debugging
- Never silently fall back to potentially incorrect behavior

### Plugin Development Guidelines
- Create formal interface for path-aware plugins
- Provide helper utilities for common path resolution patterns
- Document best practices for handling optional config_directory
- Ensure consistent error reporting across all plugins

### Backward Compatibility
- Existing absolute paths must continue to work unchanged
- Existing relative paths should work but may need user adjustment
- Provide clear migration guidance for any breaking changes
- Support gradual adoption of new path resolution features

## Related Files

Key files that will need updates:
- `watchgate/utils/paths.py` - Core path resolution utilities
- `watchgate/plugins/interfaces.py` - New PathResolvablePlugin interface
- `watchgate/plugins/manager.py` - Plugin loading and config_directory handling
- `watchgate/plugins/auditing/file_auditing.py` - Improved error handling
- `watchgate/plugins/security/filesystem_server_security.py` - Add path resolution
- `watchgate/config/loader.py` - Enhanced validation
- All configuration examples and documentation

This implementation should address all the identified issues while maintaining the solid architectural foundation of config-relative path resolution.