"""Plugin interfaces for Watchgate MCP gateway.

This module defines the abstract base classes and data structures that all
plugins must implement to integrate with the Watchgate plugin system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List
from dataclasses import dataclass
from pathlib import Path
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


@dataclass
class PolicyDecision:
    """Result of security policy evaluation.
    
    Attributes:
        allowed: Whether the request should be allowed
        reason: Human-readable explanation for the decision
        metadata: Optional additional information about the decision
        modified_content: Optional modified content (request, response, or notification)
    """
    allowed: bool
    reason: str
    metadata: Dict[str, Any] = None
    modified_content: Union[MCPRequest, MCPResponse, MCPNotification, None] = None
    
    def __post_init__(self):
        """Initialize metadata to empty dict if None."""
        if self.metadata is None:
            self.metadata = {}


class PluginInterface(ABC):
    """Base interface for all Watchgate plugins.
    
    All plugins must inherit from this interface and implement the required
    initialization method. This ensures consistent plugin lifecycle management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration.
        
        Args:
            config: Plugin-specific configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
            TypeError: If configuration has wrong types
        """
        # Set default priority if not specified in config
        self.priority = config.get('priority', 50)
        # Validate priority range
        if not isinstance(self.priority, int) or not (0 <= self.priority <= 100):
            raise ValueError(f"Plugin priority {self.priority} must be between 0 and 100")
    
    @property
    def plugin_id(self) -> str:
        """Unique identifier for this plugin (class name by default)."""
        return self.__class__.__name__


class SecurityPlugin(PluginInterface):
    """Abstract base class for security policy plugins.
    
    Security plugins evaluate MCP messages (requests, responses, and notifications)
    and determine whether they should be allowed to proceed.
    
    CRITICAL SECURITY REQUIREMENT: All three check methods MUST be properly 
    implemented with comprehensive security logic:
    
    - check_request: Validates incoming requests for security violations
    - check_response: Validates outgoing responses to prevent data leakage
    - check_notification: Validates notifications to prevent information disclosure
    
    Security vulnerabilities can occur if any method is not properly implemented.
    For example, only checking requests allows malicious content in responses 
    to bypass security filters.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize security plugin with configuration.
        
        Args:
            config: Plugin-specific configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
            TypeError: If configuration has wrong types
        """
        # Initialize base class to set priority
        super().__init__(config)
        
        # Security plugins can be configured as critical or non-critical
        # Default to critical for security
        self.critical = config.get("critical", True)
    
    def is_critical(self) -> bool:
        """Return whether this plugin is critical for operation.
        
        Returns:
            bool: True if plugin failures should halt processing, False otherwise
        """
        return self.critical
    
    @abstractmethod
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        """Evaluate if request should be allowed.
        
        SECURITY REQUIREMENT: Must validate ALL request content for security 
        violations including method names, parameters, and any text content.
        
        Args:
            request: The MCP request to evaluate
            server_name: Name of the target server
            
        Returns:
            PolicyDecision: Decision on whether to allow the request
            
        Raises:
            Exception: Plugin-specific errors that should be caught and handled
                      by the plugin manager
        """
        pass
    
    @abstractmethod
    async def check_response(self, request: MCPRequest, response: MCPResponse, server_name: str) -> PolicyDecision:
        """Evaluate if response should be allowed.
        
        SECURITY REQUIREMENT: Must validate ALL response content to prevent 
        data leakage. Responses may contain sensitive information not present
        in the original request (file contents, secrets, etc.).
        
        Args:
            request: The original MCP request
            response: The MCP response to evaluate
            server_name: Name of the source server
            
        Returns:
            PolicyDecision: Decision on whether to allow the response
            
        Raises:
            Exception: Plugin-specific errors that should be caught and handled
                      by the plugin manager
        """
        pass
    
    @abstractmethod
    async def check_notification(self, notification: MCPNotification, server_name: str) -> PolicyDecision:
        """Evaluate if notification should be allowed.
        
        SECURITY REQUIREMENT: Must validate ALL notification content to prevent
        information disclosure. Notifications can leak information about 
        restricted operations, paths, or contain sensitive data.
        
        Args:
            notification: The MCP notification to evaluate
            server_name: Name of the source server
            
        Returns:
            PolicyDecision: Decision on whether to allow the notification
            
        Raises:
            Exception: Plugin-specific errors that should be caught and handled
                      by the plugin manager
        """
        pass


class AuditingPlugin(PluginInterface):
    """Abstract base class for auditing plugins.
    
    Auditing plugins log request and response information for security
    monitoring, compliance, and debugging purposes.
    """
    
    @abstractmethod
    async def log_request(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> None:
        """Log request with policy decision.
        
        Args:
            request: The MCP request being processed
            decision: The security policy decision for this request
            server_name: Name of the target server
            
        Raises:
            Exception: Plugin-specific errors that should be caught and handled
                      by the plugin manager
        """
        pass
        
    @abstractmethod
    async def log_response(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> None:
        """Log response from upstream server with security decision.
        
        Args:
            request: The original MCP request for correlation
            response: The MCP response from the upstream server
            decision: The policy decision made by security plugins for this response
            server_name: Name of the source server
            
        Raises:
            Exception: Plugin-specific errors that should be caught and handled
                      by the plugin manager
        """
        pass
        
    @abstractmethod
    async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> None:
        """Log notification message.
        
        Args:
            notification: The MCP notification being processed
            decision: The policy decision from security plugins
            server_name: Name of the source server
            
        Raises:
            Exception: Plugin-specific errors that should be caught and handled
                      by the plugin manager
        """
        pass
    
    def is_critical(self) -> bool:
        """Return whether this plugin is critical for operation.
        
        Critical plugins will cause processing to halt on failure.
        Non-critical plugins log errors but allow processing to continue.
        
        Returns:
            bool: True if plugin failures should halt processing, False otherwise
        """
        return getattr(self, 'critical', False)


class PathResolvablePlugin(ABC):
    """Abstract base class for plugins that use file paths in their configuration.
    
    This interface formalizes the contract for plugins that need path resolution
    relative to the configuration directory. Plugins implementing this interface
    will receive the config directory and can resolve relative paths accordingly.
    
    Path-aware plugins must:
    1. Implement set_config_directory() to receive the config directory
    2. Implement validate_paths() to validate resolved paths
    3. Use the config directory to resolve relative paths in their configuration
    
    This interface can be mixed with SecurityPlugin or AuditingPlugin to create
    path-aware security or auditing plugins.
    """
    
    @abstractmethod
    def set_config_directory(self, config_directory: Union[str, Path]) -> None:
        """Set the configuration directory for path resolution.
        
        This method is called by the plugin manager after plugin initialization
        to provide the directory containing the configuration file. Plugins should
        use this directory to resolve any relative paths in their configuration.
        
        Args:
            config_directory: Directory containing the configuration file
            
        Raises:
            TypeError: If config_directory is not a valid path type
            ValueError: If config_directory is invalid or inaccessible
        """
        pass
    
    @abstractmethod
    def validate_paths(self) -> List[str]:
        """Validate all paths used by this plugin.
        
        This method should validate that all paths resolved by the plugin
        are valid, accessible, and secure. It should return a list of validation
        errors, or an empty list if all paths are valid.
        
        Returns:
            List[str]: List of validation error messages, empty if no errors
            
        Examples:
            ["Log directory does not exist: /invalid/path"]
            ["Output file parent directory is not writable: /readonly/dir"]
            []  # No validation errors
        """
        pass
