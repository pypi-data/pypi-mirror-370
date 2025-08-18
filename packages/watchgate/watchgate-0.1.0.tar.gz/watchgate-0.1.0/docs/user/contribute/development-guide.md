# Development Guide

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Contribute](../README.md) → Development Guide*

Interested in contributing to Watchgate's development? This guide will help you set up a development environment, understand the codebase, and contribute code improvements, new features, or plugins.

## Getting Started

### Development Environment Setup

#### Prerequisites
- **Python 3.11+**: Required for Watchgate development
- **Git**: For version control and contributing changes
- **uv**: Recommended for dependency management
- **Node.js**: For testing with MCP servers
- **Code Editor**: VS Code, PyCharm, or your preferred editor

#### Clone and Setup
```bash
# Clone the repository
git clone https://github.com/watchgate/watchgate.git
cd watchgate

# Install development dependencies
uv sync --group dev

# Or with pip
pip install -e ".[dev]"

# Verify installation
watchgate --version
```

#### Development Dependencies
The development environment includes:
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks for code quality

### Development Workflow

#### Code Quality
We maintain high code quality standards:

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/

# Run all quality checks
pre-commit run --all-files
```

#### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=watchgate

# Run specific test files
pytest tests/unit/test_plugin_manager.py

# Run tests in watch mode
pytest-watch
```

#### Pre-commit Hooks
Set up pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Now quality checks run automatically on each commit
git commit -m "Your commit message"
```

## Codebase Overview

### Project Structure
```
watchgate/
├── src/watchgate/           # Main source code
│   ├── __main__.py          # CLI entry point
│   ├── main.py              # Application main
│   ├── config/              # Configuration handling
│   │   ├── loader.py        # Config file loading
│   │   └── models.py        # Configuration data models
│   ├── plugins/             # Plugin system
│   │   ├── interfaces.py    # Plugin interfaces
│   │   ├── manager.py       # Plugin management
│   │   ├── security/        # Security plugins
│   │   └── auditing/        # Auditing plugins
│   ├── protocol/            # MCP protocol handling
│   │   ├── messages.py      # Message types
│   │   ├── validation.py    # Message validation
│   │   └── errors.py        # Protocol errors
│   ├── proxy/               # Proxy server implementation
│   │   ├── server.py        # Main proxy server
│   │   └── stdio_server.py  # STDIO transport
│   └── transport/           # Transport layer
│       ├── base.py          # Transport interface
│       └── stdio.py         # STDIO implementation
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Test configuration
├── docs/                   # Documentation
└── pyproject.toml          # Project configuration
```

### Key Components

#### Plugin System (`plugins/`)
The plugin system is the heart of Watchgate's extensibility:

- **Interfaces**: Define contracts for security and auditing plugins
- **Manager**: Handles plugin loading, ordering, and execution
- **Security Plugins**: Implement access control and security policies
- **Auditing Plugins**: Implement logging and monitoring capabilities

#### Protocol Layer (`protocol/`)
Handles MCP protocol communication:

- **Messages**: Define MCP message types and structures
- **Validation**: Validate incoming and outgoing messages
- **Errors**: Handle protocol-level errors and exceptions

#### Proxy Server (`proxy/`)
Implements the core proxy functionality:

- **Server**: Main proxy logic and request routing
- **STDIO Server**: Handles STDIO transport for MCP communication

## Contributing Code

### Types of Contributions

#### Bug Fixes
- **Fix existing issues**: Address bugs reported in GitHub issues
- **Add tests**: Ensure bugs are covered by tests to prevent regression
- **Update documentation**: Fix any related documentation issues

#### New Features
- **Enhance existing functionality**: Improve current features
- **Add new capabilities**: Implement new features requested by users
- **Improve performance**: Optimize code for better performance

#### Plugin Development
- **Security plugins**: New access control mechanisms
- **Auditing plugins**: New logging and monitoring capabilities
- **Integration plugins**: Support for new external systems

### Development Process

#### 1. Choose an Issue
- **Browse open issues**: Look for issues labeled "good first issue" or "help wanted"
- **Discuss in advance**: For large features, discuss the approach first
- **Assign yourself**: Comment on the issue to let others know you're working on it

#### 2. Create a Branch
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b bugfix/issue-description
```

#### 3. Write Code
Follow these guidelines:

- **Write tests first**: Use test-driven development (TDD) when possible
- **Follow code style**: Use black for formatting, follow PEP 8
- **Add type hints**: Use type annotations for better code clarity
- **Document your code**: Add docstrings and comments for complex logic

#### 4. Test Your Changes
```bash
# Run tests to ensure nothing breaks
pytest

# Test with real MCP servers
watchgate --config test-config.yaml --verbose

# Test edge cases and error conditions
pytest tests/integration/
```

#### 5. Submit a Pull Request
- **Write clear commit messages**: Explain what and why, not just what
- **Update documentation**: Add or update relevant documentation
- **Add tests**: Ensure your changes are tested
- **Fill out PR template**: Provide context for reviewers

### Plugin Development

#### Creating a Security Plugin

**CRITICAL**: Security plugins must implement ALL THREE check methods to prevent security vulnerabilities.

```python
from typing import Dict, Any
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification

class MySecurityPlugin(SecurityPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.rules = config.get('rules', [])
    
    async def check_request(self, request: MCPRequest) -> PolicyDecision:
        """
        Check if incoming request should be allowed.
        
        SECURITY REQUIREMENT: Must validate ALL request content for security violations.
        """
        if self._is_request_allowed(request):
            return PolicyDecision(
                allowed=True,
                reason="Request allowed by security policy",
                metadata={"plugin": "my_security_plugin", "check_type": "request"}
            )
        else:
            return PolicyDecision(
                allowed=False,
                reason="Request blocked by security policy",
                metadata={"plugin": "my_security_plugin", "check_type": "request"}
            )
    
    async def check_response(self, request: MCPRequest, response: MCPResponse) -> PolicyDecision:
        """
        Check if outgoing response should be allowed.
        
        SECURITY REQUIREMENT: Must validate ALL response content to prevent data leakage.
        Responses may contain sensitive information that wasn't in the original request.
        """
        if self._is_response_allowed(request, response):
            return PolicyDecision(
                allowed=True,
                reason="Response allowed by security policy",
                metadata={"plugin": "my_security_plugin", "check_type": "response"}
            )
        else:
            return PolicyDecision(
                allowed=False,
                reason="Response blocked - contains sensitive information",
                metadata={"plugin": "my_security_plugin", "check_type": "response"}
            )
    
    async def check_notification(self, notification: MCPNotification) -> PolicyDecision:
        """
        Check if notification should be allowed.
        
        SECURITY REQUIREMENT: Must validate ALL notification content.
        Notifications can leak information about restricted operations or paths.
        """
        if self._is_notification_allowed(notification):
            return PolicyDecision(
                allowed=True,
                reason="Notification allowed by security policy",
                metadata={"plugin": "my_security_plugin", "check_type": "notification"}
            )
        else:
            return PolicyDecision(
                allowed=False,
                reason="Notification blocked - contains restricted information",
                metadata={"plugin": "my_security_plugin", "check_type": "notification"}
            )
    
    def _is_request_allowed(self, request: MCPRequest) -> bool:
        """Implement your request security logic here"""
        # Example: Check if method is in allowed list
        allowed_methods = self.rules.get('allowed_methods', [])
        return request.method in allowed_methods if allowed_methods else True
    
    def _is_response_allowed(self, request: MCPRequest, response: MCPResponse) -> bool:
        """Implement your response security logic here"""
        # Example: Check if response contains sensitive patterns
        if response.result:
            response_text = str(response.result)
            sensitive_patterns = self.rules.get('sensitive_patterns', [])
            for pattern in sensitive_patterns:
                if pattern in response_text:
                    return False
        return True
    
    def _is_notification_allowed(self, notification: MCPNotification) -> bool:
        """Implement your notification security logic here"""
        # Example: Check if notification method is allowed
        blocked_notification_methods = self.rules.get('blocked_notification_methods', [])
        return notification.method not in blocked_notification_methods
```

#### Security Plugin Development Best Practices

1. **Implement All Three Methods**: Never leave any check method unimplemented or with just `pass`
2. **Fail Secure**: When in doubt, deny access rather than allow it
3. **Check All Content**: Validate all text content in requests, responses, and notifications
4. **Use Comprehensive Patterns**: Don't just check obvious fields - scan all string content
5. **Log Security Decisions**: Always provide clear reasons for allow/deny decisions
6. **Test All Three Paths**: Write tests that cover request, response, and notification scenarios

#### Creating an Auditing Plugin

```python
from watchgate.plugins.interfaces import AuditingPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse

class MyAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.log_file = config.get('log_file', 'audit.log')
    
    def audit_request(self, request: MCPRequest, context: RequestContext):
        """Log incoming request"""
        with open(self.log_file, 'a') as f:
            f.write(f"REQUEST: {request.method} - {request.params}\n")
    
    def audit_response(self, response: MCPResponse, context: ResponseContext):
        """Log outgoing response"""
        with open(self.log_file, 'a') as f:
            f.write(f"RESPONSE: {response.id} - {response.result}\n")
```

#### Plugin Registration

```python
# In your plugin module
from watchgate.plugins.manager import PluginManager

def register_plugin():
    """Register plugin with the plugin manager"""
    PluginManager.register_security_plugin('my_security_plugin', MySecurityPlugin)
    PluginManager.register_auditing_plugin('my_auditing_plugin', MyAuditingPlugin)
```

### Code Style Guidelines

#### Python Style
We follow PEP 8 with some specific preferences:

```python
# Use type hints
def process_request(self, request: MCPRequest) -> SecurityDecision:
    pass

# Use descriptive variable names
allowed_tools = config.get('tools', [])
security_decision = self._evaluate_request(request)

# Use docstrings for all public methods
def process_request(self, request: MCPRequest) -> SecurityDecision:
    """
    Process an incoming MCP request and make a security decision.
    
    Args:
        request: The incoming MCP request to evaluate
        
    Returns:
        SecurityDecision indicating whether to allow or deny the request
    """
    pass
```

#### Configuration Style
```yaml
# Use clear, descriptive configuration keys
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      priority: 30
      config:
        mode: "allowlist"
        allowed_tools: ["read_file", "write_file"]
        block_message: "Tool access denied by policy"
```

### Testing Guidelines

#### Unit Tests
Test individual components in isolation. **Security plugins MUST test all three check methods:**

```python
import pytest
from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification

@pytest.mark.asyncio
async def test_tool_allowlist_all_methods():
    """Test that all three security check methods work correctly"""
    config = {
        'mode': 'allowlist',
        'tools': ['read_file', 'write_file']
    }
    plugin = ToolAllowlistPlugin(config)
    
    # Test check_request - allowed tool
    request = MCPRequest(
        jsonrpc="2.0",
        method='tools/call', 
        params={'name': 'read_file'},
        id=1
    )
    decision = await plugin.check_request(request)
    assert decision.allowed is True
    
    # Test check_request - blocked tool
    request = MCPRequest(
        jsonrpc="2.0",
        method='tools/call', 
        params={'name': 'delete_file'},
        id=2
    )
    decision = await plugin.check_request(request)
    assert decision.allowed is False
    
    # Test check_response - tools/list filtering
    request = MCPRequest(
        jsonrpc="2.0",
        method='tools/list',
        id=3
    )
    response = MCPResponse(
        jsonrpc="2.0",
        id=3,
        result={
            "tools": [
                {"name": "read_file", "description": "Read files"},
                {"name": "delete_file", "description": "Delete files"}
            ]
        }
    )
    decision = await plugin.check_response(request, response)
    # Should filter out 'delete_file' and keep only 'read_file'
    assert decision.allowed is True
    if decision.modified_content:
        tools = decision.modified_content.result["tools"]
        tool_names = [tool["name"] for tool in tools]
        assert "read_file" in tool_names
        assert "delete_file" not in tool_names
    
    # Test check_notification - should be allowed (tool access control doesn't restrict notifications)
    notification = MCPNotification(
        jsonrpc="2.0",
        method="progress",
        params={"percent": 50}
    )
    decision = await plugin.check_notification(notification)
    assert decision.allowed is True
```

#### Security Plugin Testing Requirements

**All security plugins MUST have tests that cover:**

1. **Request Testing**: Test both allowed and blocked requests
2. **Response Testing**: Test response filtering and modification 
3. **Notification Testing**: Test notification validation
4. **Edge Cases**: Test malformed inputs, missing fields, etc.
5. **Security Bypasses**: Test potential ways security could be circumvented

Example comprehensive test structure:
```python
class TestMySecurityPlugin:
    """Comprehensive tests for security plugin - ALL THREE METHODS REQUIRED"""
    
    @pytest.mark.asyncio
    async def test_check_request_allows_valid_requests(self):
        """Test that valid requests are allowed"""
        pass
    
    @pytest.mark.asyncio 
    async def test_check_request_blocks_invalid_requests(self):
        """Test that invalid requests are blocked"""
        pass
    
    @pytest.mark.asyncio
    async def test_check_response_allows_clean_responses(self):
        """Test that clean responses are allowed"""
        pass
    
    @pytest.mark.asyncio
    async def test_check_response_blocks_sensitive_responses(self):
        """Test that responses with sensitive data are blocked"""
        pass
    
    @pytest.mark.asyncio
    async def test_check_notification_allows_safe_notifications(self):
        """Test that safe notifications are allowed"""
        pass
    
    @pytest.mark.asyncio
    async def test_check_notification_blocks_restricted_notifications(self):
        """Test that notifications with restricted content are blocked"""
        pass
```

#### Integration Tests
Test complete workflows:

```python
def test_complete_security_workflow():
    """Test that security plugins work together correctly"""
    config = load_test_config('multi_plugin_config.yaml')
    proxy = create_test_proxy(config)
    
    # Test that tool control and content control work together
    result = proxy.process_request(create_read_file_request('public/test.txt'))
    assert result.allowed == True
    
    result = proxy.process_request(create_read_file_request('private/secret.txt'))
    assert result.allowed == False
```

### Documentation

#### Code Documentation
- **Docstrings**: All public classes and methods need docstrings
- **Type hints**: Use type annotations for better code clarity
- **Comments**: Explain complex logic or business rules

#### User Documentation
- **Update guides**: Keep tutorials and guides current with code changes
- **Add examples**: Include configuration examples for new features
- **Update reference**: Keep the configuration reference up to date

## Release Process

### Version Management
We use semantic versioning (semver):

- **Major version** (X.0.0): Breaking changes
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

### Release Checklist
1. **Run full test suite**: Ensure all tests pass
2. **Update documentation**: Reflect any changes
3. **Update changelog**: Document new features and fixes
4. **Tag release**: Create git tag with version number
5. **Build and publish**: Automated via CI/CD

## Getting Help

### Development Questions
- **GitHub Discussions**: General development questions
- **Code Review**: Ask for feedback on your approach
- **Architecture Decisions**: Discuss significant design choices

### Development Resources
- **Codebase walkthrough**: Schedule with maintainers for complex features
- **Plugin examples**: Look at existing plugins for patterns
- **Testing patterns**: Follow existing test structure and patterns

### Community
- **Regular contributors**: Join the regular contributor community
- **Development chat**: Real-time discussion with other developers
- **Code review**: Participate in reviewing others' code

Thank you for contributing to Watchgate! Your contributions help make AI interactions safer for everyone.
