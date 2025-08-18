# Upstream-Scoped Plugin Configuration Requirements

## Overview
Implement upstream-scoped plugin configuration to enable different plugin policies per upstream server while maintaining global defaults. This uses a simple dictionary-based configuration structure where each upstream has its own dedicated section with clear naming conventions and optional global policies.

## Problem Statement
The current implementation only supports global plugin configurations that apply to all upstream servers uniformly:

```yaml
plugins:
  security:
    - policy: "rate_limiting"
      enabled: true
  auditing:
    - policy: "request_logging"
      enabled: true
```

This lacks the flexibility to apply different security policies per upstream server (e.g., stricter GitHub token validation for git servers, filesystem path restrictions for file servers).

## New Configuration Design

### Target Configuration Structure
```yaml
plugins:
  security:
    # Global policies for all upstreams (optional)
    _global:
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 100
    
    # Specific policies for individual upstreams
    github:
      - policy: "git_token_validation"
        enabled: true
    
    gitlab:
      - policy: "git_token_validation"
        enabled: true
    
    file-system:
      - policy: "path_restrictions"
        enabled: true
        config:
          allowed_paths: ["/safe/directory"]
  
  auditing:
    # Global auditing for all upstreams (optional)
    _global:
      - policy: "request_logging"
        enabled: true
    
    # Specific auditing for GitHub
    github:
      - policy: "sensitive_data_audit"
        enabled: true
```

### Alternative: Upstream-Specific Only (No Global)
```yaml
plugins:
  security:
    # No _global section needed - upstream-specific only
    github:
      - policy: "git_token_validation"
        enabled: true
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 50
    
    file-system:
      - policy: "path_restrictions"
        enabled: true
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 100
```

### Key Design Principles

1. **Dictionary Structure**: Each upstream has its own key in the configuration, eliminating overlap possibilities
2. **Clear Special Keys**: `_global` uses underscore prefix to indicate special meaning (YAML convention)
3. **Optional Global Section**: Global policies are optional - configurations can be purely upstream-specific
4. **Consistent Key Naming**: Upstream keys follow strict naming conventions for clarity and validation
5. **Additive Behavior**: Upstream-specific policies are combined with global (`_global`) policies when both exist
6. **Policy Override**: Upstream-specific policies override global policies with the same name

### Advantages of Dictionary-Based Approach

1. **Improved Readability**: Users can immediately find all policies for a specific upstream
2. **Simplified Validation**: Dictionary structure prevents overlapping upstream definitions
3. **Intuitive Structure**: Aligns with how users think about configuring specific entities
4. **No Overlap Complexity**: Impossible to have the same upstream in multiple places
5. **Clear Special Keys**: `_global` is unambiguously a special configuration section
6. **Flexible Scope**: Support both global+specific and purely specific configurations

### Key Naming Conventions

**Special Keys:**
- `_global`: Reserved for global policies applying to all upstreams (underscore prefix indicates special meaning)

**Upstream Keys:**
- Must match configured upstream names exactly
- Must follow pattern: `^[a-z][a-z0-9_-]*$` (lowercase alphanumeric, hyphens, underscores)
- Examples: `github`, `file-system`, `docker_registry`, `my-api`

### Handling Repetition

For upstreams that need identical policies, configuration should be repeated for clarity:

```yaml
plugins:
  security:
    github:
      - policy: "git_token_validation"
        enabled: true
    gitlab:
      - policy: "git_token_validation"  # Repeated for clarity
        enabled: true
    bitbucket:
      - policy: "git_token_validation"  # Repeated for clarity
        enabled: true
```

**Advanced Users**: YAML anchors can be used to avoid repetition without code changes:

```yaml
plugins:
  security:
    _git_policies: &git_validation  # Anchor definition (ignored by Watchgate)
      - policy: "git_token_validation"
        enabled: true
    
    github: *git_validation      # Reference
    gitlab: *git_validation      # Reference
    bitbucket: *git_validation   # Reference
```

**Note**: Keys starting with `_` that aren't `_global` are ignored by Watchgate, making them safe for anchor definitions.

## Configuration Validation Rules

### 1. Upstream Key Validation
- **Valid upstream names**: ✅ All keys (except `_global`) must exist in `upstreams` configuration
- **Key naming pattern**: ✅ Must match `^[a-z][a-z0-9_-]*$` (lowercase, alphanumeric, hyphens, underscores)
- **Case sensitivity**: ✅ Case-sensitive matching (consistent with YAML keys)
- **Reserved key**: ✅ `_global` is reserved for global policies
- **Ignored keys**: ✅ Other keys starting with `_` are ignored (useful for YAML anchors)

### 2. Policy Resolution & Precedence
- **Additive behavior**: ✅ `_global` + specific upstream policies both apply (when `_global` exists)
- **Policy override**: ✅ Upstream-specific policies override global policies with same name
- **Deterministic resolution**: ✅ Resolution order is predictable and consistent
- **Optional global**: ✅ `_global` section is completely optional

### 3. Configuration Structure
- **Dictionary format**: ✅ Each plugin type (security, auditing) contains a dictionary
- **Policy lists**: ✅ Each upstream key maps to a list of policy configurations
- **Empty sections**: ✅ Empty upstream sections are allowed
- **Flexible combinations**: ✅ Support global-only, upstream-only, or mixed configurations

### 4. Error Handling
- **Invalid upstream names**: ❌ Fail fast (configuration error)
- **Invalid key naming**: ❌ Fail fast (must follow naming pattern)
- **Upstream removed but referenced**: ❌ Fail fast (configuration error)
- **Error strategy**: ❌ Fail fast (security-first approach)

## Requirements

### 1. Configuration Schema Extension
- **Update Pydantic models** in `watchgate/config/models.py`:
  - Replace `List[PluginConfigSchema]` with dictionary-based structure
  - Add validation for upstream name existence (except `_global` and other `_*` keys)
  - Support dictionary format with string keys and policy list values
  - Enforce key naming patterns for upstream names
- **Schema Structure**:
  ```python
  import re
  from typing import Dict, List, Optional
  from pydantic import BaseModel, field_validator
  
  class PluginsConfigSchema(BaseModel):
      security: Optional[Dict[str, List[PolicyConfigSchema]]] = {}
      auditing: Optional[Dict[str, List[PolicyConfigSchema]]] = {}
      
      @field_validator('security', 'auditing')
      @classmethod
      def validate_upstream_keys(cls, v, info):
          if not v:  # Empty dict is valid
              return v
              
          for key in v.keys():
              # Skip special keys
              if key.startswith('_'):
                  if key == '_global':
                      continue  # Valid special key
                  else:
                      continue  # Ignored keys (e.g., for YAML anchors)
              
              # Validate upstream key naming pattern
              if not re.match(r'^[a-z][a-z0-9_-]*$', key):
                  raise ValueError(
                      f"Invalid upstream key '{key}': must be lowercase alphanumeric "
                      f"with hyphens/underscores (pattern: ^[a-z][a-z0-9_-]*$)"
                  )
              
              # Validate that upstream exists in configuration
              # (Will be implemented during development - needs access to full config)
          
          return v
  ```

### 2. Plugin Manager Enhancement
- **Modify `PluginManager`** in `watchgate/plugins/manager.py`:
  - Implement plugin resolution logic for dictionary-based configuration
  - Support additive behavior (global + upstream-specific) when `_global` exists
  - Handle policy override (upstream-specific overrides global with same name)
  - Support upstream-only configurations (no `_global` section)
  - Add method: `get_plugins_for_upstream(upstream_name: str) -> PluginSet`

### 3. Request Processing Integration
- **Update proxy server** in `watchgate/proxy/server.py`:
  - Pass upstream context to plugin manager during request processing
  - Apply correct plugin set based on target upstream
  - Ensure auditing plugins capture which upstream and plugin set was applied

### 4. Configuration Validation
- **Comprehensive validation rules**:
  - Ensure all upstream keys (except `_global` and other `_*`) exist in `upstreams` configuration
  - Enforce key naming patterns for all upstream references
  - Validate plugin policies are available
  - Provide clear error messages for invalid configurations
  - No overlap detection needed due to dictionary structure

## Implementation Phases

### Phase 1: Configuration Models (TDD)
- **Write failing tests first** for new dictionary-based configuration schema
- Update Pydantic schemas for upstream-scoped plugin configurations
- Add validation rules for upstream key checking and naming patterns
- Update configuration loading and validation logic
- **Test Coverage**: All validation scenarios, edge cases, error conditions, optional global section

### Phase 2: Plugin Manager Updates (TDD)
- **Write failing tests first** for plugin resolution logic
- Modify `PluginManager` to handle dictionary-based plugin configurations
- Implement plugin selection logic based on upstream context
- Support additive behavior, policy override rules, and optional global section
- **Test Coverage**: Plugin resolution with various upstream configurations (global+specific, upstream-only)

### Phase 3: Request Processing Integration (TDD)
- **Write failing tests first** for proxy server plugin application
- Update proxy server to use upstream-specific plugin sets
- Ensure auditing plugins capture upstream context
- Maintain backward compatibility where possible
- **Test Coverage**: Integration tests with multiple upstreams and plugin combinations

### Phase 4: Documentation Updates
- **Update 35+ configuration files** to reflect new format:
  - All tutorial configurations in `configs/tutorials/`
  - All example configurations in `configs/examples/`
  - All user tutorial configurations in `docs/user/tutorials/configs/`
  - Configuration reference documentation
  - ADRs that reference plugin configuration
- **Create comprehensive tutorial documentation**:
  - Dedicated tutorial for upstream-scoped configuration
  - Clear examples of global vs upstream-specific patterns
  - Migration guide with before/after examples
  - Troubleshooting guide for common configuration errors
- **Update validation guide** in `tests/validation/quick-validation-guide.md`:
  - Add upstream-scoped plugin testing scenarios
  - Include validation of plugin selection per upstream
  - Test policy override behavior
  - Test configurations with and without `_global` sections

### Phase 5: Testing & Validation
- **Comprehensive unit tests** for all configuration validation scenarios
- **Integration tests** with multiple upstreams and plugin configurations
- **Performance testing** to ensure minimal impact on request processing
- **Smoke test validation** using updated quick validation guide

## Success Criteria
- Dictionary-based upstream-scoped plugin configurations load correctly
- Requests use appropriate plugin set based on target upstream
- Global (`_global`) plugins apply when present, configurations work without global section
- Upstream-specific plugins add to or override global policies as designed
- Configuration validation catches invalid upstream references and key naming violations
- All documentation and examples reflect new configuration format with clear explanations
- Performance impact is minimal
- Full test coverage of all configuration and plugin resolution scenarios

## Security Considerations
- **Additive security**: Upstream-specific policies enhance rather than weaken global security
- **Audit transparency**: Logs clearly indicate which plugin set was applied for each upstream
- **Default security**: Missing upstream-specific configuration falls back to global policies (when present)
- **Fail-fast validation**: Invalid configurations prevent startup rather than runtime failures
- **Clear boundaries**: Dictionary structure makes it obvious which policies apply to which upstreams

## Configuration Examples

### Simple Global + Upstream-Specific
```yaml
plugins:
  security:
    _global:
      - policy: "rate_limiting"
        enabled: true
    github:
      - policy: "git_token_validation"
        enabled: true
```

### Upstream-Specific Only (No Global)
```yaml
plugins:
  security:
    github:
      - policy: "git_token_validation"
        enabled: true
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 50
    
    file-system:
      - policy: "path_restrictions"
        enabled: true
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 100
```

### Complex Multi-Upstream Example
```yaml
plugins:
  security:
    # Global security for all upstreams
    _global:
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 100
      - policy: "basic_secrets_filter"
        enabled: true
    
    # Git server specific policies
    github:
      - policy: "github_token_validation"
        enabled: true
      - policy: "repository_access_control"
        enabled: true
    
    gitlab:
      - policy: "gitlab_token_validation"
        enabled: true
      - policy: "repository_access_control"
        enabled: true
    
    # Filesystem specific policies
    file-system:
      - policy: "path_restrictions"
        enabled: true
        config:
          allowed_paths: ["/safe/directory", "/public/docs"]
      - policy: "file_type_validation"
        enabled: true
  
  auditing:
    _global:
      - policy: "request_logging"
        enabled: true
    
    github:
      - policy: "git_operation_audit"
        enabled: true
    
    file-system:
      - policy: "file_access_audit"
        enabled: true
```

### Using YAML Anchors (Advanced)
```yaml
plugins:
  security:
    # Define reusable policy sets (keys starting with _ are ignored)
    _git_policies: &git_security
      - policy: "git_token_validation"
        enabled: true
      - policy: "repository_access_control"
        enabled: true
    
    _file_policies: &file_security
      - policy: "path_restrictions"
        enabled: true
        config:
          allowed_paths: ["/safe"]
    
    # Apply to specific upstreams
    github: *git_security
    gitlab: *git_security
    bitbucket: *git_security
    file-system: *file_security
    docker-files: *file_security
```

## Documentation Update Requirements

### Files Requiring Updates (35+ files)
1. **Core Documentation**:
   - `docs/user/reference/configuration-reference.md`
   - `docs/decision-records/007-plugin-configuration-structure.md`
   - `docs/decision-records/005-configuration-management.md`

2. **Tutorial Configurations**:
   - `configs/tutorials/1-securing-tool-access.yaml`
   - `configs/tutorials/2-implementing-audit-logging.yaml`
   - `configs/tutorials/3-protecting-sensitive-content.yaml`
   - `configs/tutorials/4-multi-plugin-security.yaml`
   - `configs/tutorials/5-logging-configuration.yaml`
   - `configs/tutorials/filesystem-security-examples.yaml`

3. **Example Configurations**:
   - `configs/examples/development.yaml`
   - `configs/examples/full-example.yaml`
   - `configs/examples/minimal.yaml`
   - `configs/examples/production.yaml`

4. **Testing Configurations**:
   - `configs/testing/test-config.yaml`
   - `tests/validation/test-config.yaml`
   - `tests/validation/test-config-single.yaml`
   - `tests/validation/test-config-multi.yaml`

5. **Tutorial Documentation**:
   - `docs/user/tutorials/1-securing-tool-access.md`
   - `docs/user/tutorials/2-implementing-audit-logging.md`
   - `docs/user/tutorials/3-protecting-sensitive-content.md`
   - `docs/user/tutorials/4-multi-plugin-security.md`
   - `docs/user/tutorials/5-logging-configuration.md`
   - `docs/user/tutorials/6-filesystem-path-security.md`

6. **Tutorial Configuration Mirrors**:
   - All files in `docs/user/tutorials/configs/`

7. **Validation Documentation**:
   - `tests/validation/quick-validation-guide.md` - Add upstream-scoped plugin testing

### Critical Documentation Requirements

**⚠️ EMPHASIS: Clear Documentation is Essential**

The dictionary-based approach requires **exceptionally clear documentation** to ensure users understand:

1. **How Policy Resolution Works**:
   - When `_global` and upstream-specific policies combine
   - How override behavior works for policies with same names
   - What happens with upstream-only configurations

2. **Key Naming Rules**:
   - Valid upstream key patterns and examples
   - Why `_global` is special and what it does
   - How `_*` keys are handled (ignored except `_global`)

3. **Configuration Patterns**:
   - Global + upstream-specific examples
   - Upstream-only examples
   - YAML anchor patterns for advanced users

4. **Migration Guide**:
   - Step-by-step conversion from current format
   - Common pitfalls and how to avoid them
   - Validation error messages and solutions

### Update Requirements
- **Replace all instances** of current `plugins.security` array format
- **Show new dictionary-based format** with `_global` and specific upstream keys
- **Include configuration examples** showing both global+specific and upstream-only patterns
- **Update explanatory text** to describe upstream dictionary behavior clearly
- **Add detailed guidance on key naming** and validation rules
- **Add guidance on YAML anchors** for advanced users wanting to avoid repetition
- **Add comprehensive troubleshooting guidance** for common configuration errors
- **Create dedicated tutorial** for upstream-scoped configuration with step-by-step examples

## Testing Requirements

### Unit Test Coverage
- **Configuration validation**: Dictionary structure validation and upstream key checking
- **Key naming validation**: All valid and invalid patterns for upstream keys
- **Plugin resolution**: All upstream targeting scenarios and policy override behavior
- **Optional global section**: Configurations with and without `_global`
- **Edge cases**: Empty configurations, invalid upstream names, ignored `_*` keys
- **Error handling**: Clear error messages for all failure modes
- **YAML anchor support**: Ensure anchors work correctly with the new structure

### Integration Test Coverage
- **Multi-upstream scenarios**: Different plugin sets applied per upstream
- **Policy override behavior**: Upstream-specific policies overriding global ones
- **Additive behavior**: Global + upstream-specific plugins both applying
- **Upstream-only scenarios**: Configurations without `_global` section
- **Audit logging**: Upstream context captured in audit trails

### Validation Test Coverage
- **Smoke testing**: Updated quick validation guide scenarios
- **Configuration examples**: All updated configuration files load successfully
- **Real-world scenarios**: Complex multi-upstream, multi-plugin configurations
- **Migration scenarios**: Converting from old to new format

## Backward Compatibility Notes
- **Breaking change for v0.1.0**: Current configuration format will not be supported
- **Migration required**: Users must update configurations to new dictionary-based format
- **No migration tooling**: Manual migration with clear documentation and examples
- **Clean break**: Simplified approach aligns with v0.1.0 first release philosophy

## Migration Guide

### Converting from Current Format
**Before (Current Format):**
```yaml
plugins:
  security:
    - policy: "rate_limiting"
      enabled: true
    - policy: "secrets_filter"
      enabled: true
```

**After (New Dictionary Format):**
```yaml
plugins:
  security:
    _global:
      - policy: "rate_limiting"
        enabled: true
      - policy: "secrets_filter"
        enabled: true
```

### Adding Upstream-Specific Policies
```yaml
plugins:
  security:
    _global:
      - policy: "rate_limiting"
        enabled: true
    
    # Add upstream-specific policies
    github:
      - policy: "git_token_validation"
        enabled: true
    
    file-system:
      - policy: "path_restrictions"
        enabled: true
```

### Upstream-Only Configuration (No Global)
```yaml
plugins:
  security:
    # No _global section - each upstream configured individually
    github:
      - policy: "git_token_validation"
        enabled: true
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 50
    
    file-system:
      - policy: "path_restrictions"
        enabled: true
      - policy: "rate_limiting"
        enabled: true
        config:
          max_requests: 100
```

## Future Considerations
- **Performance optimization**: Plugin resolution caching can be added if needed
- **Extended features**: Additional plugin metadata and configuration options
- **Dynamic configuration**: Runtime configuration updates can be supported in future versions
- **Advanced YAML features**: Document additional YAML patterns for power users
- **Policy override indicators**: Optional metadata fields for explicit override documentation (non-breaking extension)
- **Inheritance syntax**: Alternative explicit inheritance syntax (non-breaking extension)