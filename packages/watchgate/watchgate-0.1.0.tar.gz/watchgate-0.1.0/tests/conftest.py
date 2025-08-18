"""Test configuration and fixtures for Watchgate tests."""

import pytest
import pytest_asyncio
import sys
import asyncio
from pathlib import Path
from typing import Optional

# Add the watchgate package to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import plugin interfaces for fixtures
from watchgate.plugins.interfaces import SecurityPlugin, AuditingPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification

# Configure pytest-asyncio
pytest_plugins = ['pytest_asyncio']


@pytest_asyncio.fixture(autouse=True)
async def ensure_async_cleanup():
    """Ensure async tasks have time to clean up before logging system is torn down."""
    yield
    # Wait for all running tasks to complete before test teardown
    # This prevents logging errors when tasks try to log after logging system cleanup
    try:
        # Get all tasks except the current one
        current_task = asyncio.current_task()
        tasks = [task for task in asyncio.all_tasks() if task is not current_task and not task.done()]
        
        if tasks:
            # Cancel all remaining tasks
            for task in tasks:
                task.cancel()
            
            # Wait for them to finish cancellation with a reasonable timeout
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=2.0)
            except asyncio.TimeoutError:
                # If tasks don't cancel within timeout, log warning but continue
                try:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Some async tasks did not cancel within timeout: {len(tasks)} tasks")
                except ValueError:
                    # If logging is already torn down, just continue
                    pass
    except Exception:
        # If cleanup fails, don't fail the test
        pass


# Mock Plugin Classes for Testing
class MockSecurityPlugin(SecurityPlugin):
    """Mock security plugin for testing."""
    
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.allowed = config.get("allowed", True)
        self.reason = config.get("reason", "Mock decision")
        self.blocked_methods = config.get("blocked_methods", [])
        self.blocked_keywords = config.get("blocked_keywords", [])
    
    async def check_request(self, request, server_name: Optional[str] = None):
        # Check if method is in blocked methods list
        if request.method in self.blocked_methods:
            return PolicyDecision(
                allowed=False,
                reason=f"Method '{request.method}' blocked by security policy",
                metadata={"plugin": "mock_security"}
            )
            
        # Check for blocked keywords in params
        if request.params:
            param_str = str(request.params)
            for keyword in self.blocked_keywords:
                if keyword.lower() in param_str.lower():
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Request contains blocked keyword '{keyword}'",
                        metadata={"plugin": "mock_security"}
                    )
        
        # If not blocked, use the default allowed setting
        return PolicyDecision(
            allowed=self.allowed,
            reason=self.reason,
            metadata={"plugin": "mock_security"}
        )
        
    async def check_response(self, request, response, server_name: Optional[str] = None):
        return PolicyDecision(
            allowed=self.allowed,
            reason=f"Response {self.reason}",
            metadata={"plugin": "mock_security"}
        )
        
    async def check_notification(self, notification, server_name: Optional[str] = None):
        return PolicyDecision(
            allowed=self.allowed,
            reason=f"Notification {self.reason}",
            metadata={"plugin": "mock_security"}
        )


class MockAuditingPlugin(AuditingPlugin):
    """Mock auditing plugin for testing."""
    
    def __init__(self, config):
        self.config = config
        self.logged_requests = []
        self.logged_responses = []
        self.logged_notifications = []
        # Add these attributes to match what test_proxy_integration.py expects
        self.request_log = []
        self.response_log = []
    
    async def log_request(self, request, decision, server_name: Optional[str] = None):
        self.logged_requests.append((request, decision))
        # Also store in format expected by test_proxy_integration.py
        self.request_log.append({
            "method": request.method,
            "id": request.id,
            "decision": {
                "allowed": decision.allowed,
                "reason": decision.reason
            }
        })
    
    async def log_response(self, request, response, decision=None, server_name: Optional[str] = None):
        # Support both old and new signatures during transition
        if decision is not None:
            self.logged_responses.append((request, response, decision))
        else:
            self.logged_responses.append((request, response))
        # Also store in format expected by test_proxy_integration.py
        self.response_log.append({
            "id": response.id,
            "result": response.result,
            "error": response.error
        })
        
    async def log_notification(self, notification, decision, server_name: Optional[str] = None):
        self.logged_notifications.append((notification, decision))


class FailingSecurityPlugin(SecurityPlugin):
    """Security plugin that always fails for testing error handling."""
    
    def __init__(self, config):
        super().__init__(config)
        self.config = config
    
    async def check_request(self, request, server_name: Optional[str] = None):
        raise RuntimeError("Plugin failure simulation")
        
    async def check_response(self, request, response, server_name: Optional[str] = None):
        raise RuntimeError("Response check failure simulation")
        
    async def check_notification(self, notification, server_name: Optional[str] = None):
        raise RuntimeError("Notification check failure simulation")


class FailingAuditingPlugin(AuditingPlugin):
    """Auditing plugin that always fails for testing error handling."""
    
    def __init__(self, config):
        self.config = config
    
    async def log_request(self, request, decision, server_name: Optional[str] = None):
        raise RuntimeError("Request logging failure")
    
    async def log_response(self, request, response, decision=None, server_name: Optional[str] = None):
        raise RuntimeError("Response logging failure")
        
    async def log_notification(self, notification, decision, server_name: Optional[str] = None):
        raise RuntimeError("Notification logging failure")


# Plugin Fixtures
@pytest.fixture
def mock_security_plugin():
    """Create a mock security plugin that allows all requests."""
    return MockSecurityPlugin({"allowed": True, "reason": "Test approval"})


@pytest.fixture
def blocking_security_plugin():
    """Create a mock security plugin that blocks all requests."""
    return MockSecurityPlugin({"allowed": False, "reason": "Test blocked"})


@pytest.fixture
def mock_auditing_plugin():
    """Create a mock auditing plugin for testing."""
    return MockAuditingPlugin({})


@pytest.fixture
def failing_security_plugin():
    """Create a security plugin that raises errors for testing error handling."""
    return FailingSecurityPlugin({})


@pytest.fixture
def failing_auditing_plugin():
    """Create an auditing plugin that raises errors for testing error handling."""
    return FailingAuditingPlugin({})


# Configuration Fixtures
@pytest.fixture
def minimal_proxy_config_dict():
    """Minimal valid proxy configuration dictionary."""
    return {
        "proxy": {
            "transport": "stdio",
            "upstreams": [{
                "name": "test_server",
                "command": ["python", "-m", "my_mcp_server"]
            }],
            "timeouts": {
                "connection_timeout": 30,
                "request_timeout": 60
            }
        }
    }


@pytest.fixture
def complete_proxy_config_dict():
    """Complete proxy configuration dictionary with all options."""
    return {
        "proxy": {
            "transport": "http",
            "upstreams": [{
                "name": "test_server",
                "command": ["python", "-m", "my_mcp_server"],
                "restart_on_failure": True,
                "max_restart_attempts": 5
            }],
            "timeouts": {
                "connection_timeout": 45,
                "request_timeout": 90
            },
            "http": {
                "host": "0.0.0.0",
                "port": 9090
            }
        }
    }


@pytest.fixture
def standard_proxy_config():
    """Standard ProxyConfig object for testing."""
    from watchgate.config.models import ProxyConfig, UpstreamConfig, TimeoutConfig
    return ProxyConfig(
        transport="stdio",
        upstreams=[UpstreamConfig(name="example_server", command=["python", "-m", "example_server"])],
        timeouts=TimeoutConfig()
    )


@pytest.fixture
def plugin_yaml_config():
    """YAML configuration string with plugins for integration testing."""
    return """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: ["python", "-m", "test_server"]
  timeouts:
    connection_timeout: 30
    request_timeout: 60

plugins:
  security:
    _global:
      - policy: "tool_allowlist"
        enabled: true
        config:
          mode: "allow_all"
  
  auditing:
    _global:
      - policy: "json_auditing"
        enabled: true
        config:
          output_file: "/tmp/test_audit.log"
          format: "json"
"""


# MCP Message Fixtures
@pytest.fixture
def sample_mcp_request():
    """Sample MCP request for testing."""
    return {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "req-1"
    }


@pytest.fixture
def sample_mcp_response():
    """Sample MCP response for testing."""
    return {
        "jsonrpc": "2.0",
        "id": "req-1",
        "result": {
            "tools": [
                {"name": "echo", "description": "Echo input"}
            ]
        }
    }


@pytest.fixture
def sample_mcp_error_response():
    """Sample MCP error response for testing."""
    return {
        "jsonrpc": "2.0",
        "id": "req-1",
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }


@pytest.fixture
def sample_initialize_request():
    """Sample MCP initialize request."""
    return {
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": "init-1",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }


@pytest.fixture
def sample_tools_call_request():
    """Sample tools/call request."""
    return {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": "tool-1",
        "params": {
            "name": "echo",
            "arguments": {"text": "Hello, World!"}
        }
    }


@pytest.fixture
def sample_resources_read_request():
    """Sample resources/read request."""
    return {
        "jsonrpc": "2.0",
        "method": "resources/read",
        "id": "resource-1",
        "params": {
            "uri": "file://test.txt"
        }
    }


@pytest.fixture
def blocked_tool_request():
    """Request that should be blocked by security policies."""
    return {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": "blocked-1",
        "params": {
            "name": "dangerous_tool",
            "arguments": {"action": "delete_all"}
        }
    }


@pytest.fixture
def malicious_request():
    """Request containing malicious content for security testing."""
    return {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": "malicious-1",
        "params": {
            "name": "file_operations",
            "arguments": {"content": "malicious payload"}
        }
    }
