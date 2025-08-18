# Command Line Interface

**Status**: Implemented

## Problem Statement
Users need a simple command-line interface to start and configure the Watchgate proxy server.

## Requirements
- Accept configuration file path via command line argument
- Support verbose logging mode for debugging
- Display version information
- Provide helpful usage examples and error messages
- Graceful handling of keyboard interrupts (Ctrl+C)
- Proper exit codes for different error conditions

## Success Criteria
- [x] Accepts config file path argument
- [x] Supports verbose logging flag
- [x] Shows version information
- [x] Provides clear help text with examples
- [x] Handles Ctrl+C gracefully
- [x] Returns appropriate exit codes
- [x] Clear error messages for common problems

## Constraints
- Must integrate with existing asyncio proxy server
- Should follow standard Unix CLI conventions
- Error messages must be user-friendly, not technical

## Implementation Notes
- Uses argparse for command line parsing
- Integrates with structured logging system
- Async integration with proxy server lifecycle
- Comprehensive error handling with user-friendly messages

## Configuration
CLI supports these options:
```bash
watchgate                                    # Use default config
watchgate --config /path/to/config.yaml     # Custom config
watchgate --verbose                          # Debug logging
watchgate --version                          # Show version
watchgate --help                             # Show help
```

## References
- Implementation: `watchgate/main.py`
- Tests: `tests/unit/test_main_cli.py`
- Integration: `tests/integration/test_console_script.py`