# Log Format Implementation Requirements

This directory contains requirements documents for implementing new log formats in the Watchgate file_auditing plugin.

## Implementation Overview

The Watchgate file_auditing plugin currently supports three formats:
- `simple` (will be renamed to `line`)
- `json` (will be renamed to `jsonl`) 
- `detailed` (will be renamed to `debug`)

We are expanding support to include industry-standard formats for better enterprise integration.

## New Formats to Implement

### Standard Enterprise Formats
- **CEF (Common Event Format)** - SIEM integration (Splunk, ArcSight)
- **Syslog** - Centralized logging servers
- **CSV** - Spreadsheet and data analysis tools

### Modern Cloud-Native Formats
- **OTEL (OpenTelemetry)** - Vendor-neutral observability
- **GELF (Graylog Extended Log Format)** - Graylog platform integration
- **LEEF (Log Event Extended Format)** - IBM QRadar SIEM

## Implementation Strategy

All implementations must:
1. **Minimal Runtime Dependencies** - Use only Python standard library
2. **Test-Only Validation** - External validators only in test environments
3. **Security-First Design** - No additional attack surface in production
4. **Configuration Compatibility** - Maintain existing config structure
5. **Centralized Version Utility** - Use `watchgate.utils.version.get_watchgate_version()` for dynamic version detection

## Testing Requirements

Each format requires:
- **Unit Tests** - Format generation with standard library only
- **Integration Tests** - Plugin lifecycle and error handling
- **Validation Tests** - External tool validation (test-only dependencies)
- **Compliance Tests** - RFC/specification adherence where applicable

## Centralized Version Utility

All log formats that include Watchgate version information must use the centralized version utility:

```python
# watchgate/utils/version.py
def get_watchgate_version() -> str:
    """Get Watchgate version dynamically"""
    try:
        # Try to get version from package metadata
        import importlib.metadata
        return importlib.metadata.version("watchgate")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        # Fallback to reading from version file
        try:
            from watchgate import __version__
            return __version__
        except ImportError:
            return "unknown"
```

**Usage in formatters:**
```python
from watchgate.utils.version import get_watchgate_version

class FormatFormatter:
    def __init__(self, version: Optional[str] = None):
        self.version = version or get_watchgate_version()
```

**Benefits:**
- DRY principle - no code duplication
- Consistent version detection across all formats
- Centralized testing and maintenance
- Future-proofing for version detection enhancements

**Testing the utility:**
```python
# tests/unit/utils/test_version.py
def test_get_watchgate_version():
    """Test centralized version utility"""
    version = get_watchgate_version()
    assert version != "unknown"  # Should detect actual version
    assert isinstance(version, str)
    assert len(version) > 0

def test_get_watchgate_version_fallback():
    """Test version utility fallback behavior"""
    # Mock failed importlib.metadata access
    with patch('importlib.metadata.version', side_effect=ImportError):
        with patch('watchgate.__version__', '1.2.3'):
            version = get_watchgate_version()
            assert version == '1.2.3'
```

## File Structure

```
log-formats/
├── README.md (this file)
├── existing-formats.md (rename specifications)
├── cef-format.md
├── syslog-format.md
├── csv-format.md
├── otel-format.md
├── gelf-format.md
└── leef-format.md
```

Each requirements document follows the same structure:
- Implementation requirements
- Testing strategy
- External validation tools
- Compliance considerations
- Risk assessment