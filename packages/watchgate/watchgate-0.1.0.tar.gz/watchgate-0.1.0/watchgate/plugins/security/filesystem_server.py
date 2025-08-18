"""
Security plugin for @modelcontextprotocol/server-filesystem MCP server.

This plugin provides path-based access control specifically for the official 
MCP filesystem server (@modelcontextprotocol/server-filesystem). It understands
the tool names and argument structures used by that server.

For other filesystem MCP servers, this plugin would need to be adapted to match
their specific tool names and argument formats.
"""

import logging
import pathspec
import re
from typing import Dict, Any, List, Tuple, Union
from pathlib import Path
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision, PathResolvablePlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification

logger = logging.getLogger(__name__)

# Tool mappings for @modelcontextprotocol/server-filesystem MCP server
# These tool names and permission requirements are specific to this server
FILESYSTEM_TOOLS = {
    "read_file": "read",
    "read_multiple_files": "read", 
    "write_file": "write",
    "edit_file": "write",
    "create_directory": "write",
    "list_directory": "read",
    "move_file": "write",
    "search_files": "read",
    "get_file_info": "read",
    "list_allowed_directories": "read"
}


class FilesystemServerSecurityPlugin(SecurityPlugin, PathResolvablePlugin):
    """
    Security plugin for @modelcontextprotocol/server-filesystem MCP server.
    
    Provides path-based access control with read/write permission levels using
    glob patterns. This plugin is specifically designed for the official MCP 
    filesystem server and its tool names/argument structures.
    
    For other filesystem MCP servers, adapt the FILESYSTEM_TOOLS mapping and
    path extraction logic to match their specific implementation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration."""
        # Validate configuration type first
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Initialize base class to set priority
        super().__init__(config)
        
        # Store permissions configuration
        self.permissions = config
        self.config_directory = None
        self.compiled_patterns = {}
        
        # Compile patterns for each permission type
        self._compile_all_patterns()
    
    def set_config_directory(self, config_directory: Union[str, Path]) -> None:
        """Set the configuration directory for path resolution.
        
        Args:
            config_directory: Directory containing the configuration file
            
        Raises:
            TypeError: If config_directory is not a valid path type
        """
        # Validate input type
        if not isinstance(config_directory, (str, Path)):
            raise TypeError(f"config_directory must be str or Path, got {type(config_directory).__name__}")
        
        # Store config directory
        self.config_directory = Path(config_directory)
        
        # Recompile patterns with new config directory context
        self._compile_all_patterns()
    
    def validate_paths(self) -> List[str]:
        """Validate all path patterns used by this plugin.
        
        Returns:
            List[str]: List of validation error/warning messages, empty if no issues
        """
        warnings = []
        
        # Validate each permission type's patterns
        for permission_type, patterns in self.permissions.items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    # Skip negation patterns for validation (they're exclusions)
                    if pattern.startswith('!'):
                        continue
                    
                    # Check if pattern matches any existing paths
                    if not self._pattern_has_matches(pattern, permission_type):
                        warnings.append(
                            f"Pattern '{pattern}' for {permission_type} permission has no matches"
                            + (f" in config directory {self.config_directory}" if self.config_directory else "")
                        )
        
        return warnings
    
    def _compile_all_patterns(self) -> None:
        """Compile all patterns for all permission types."""
        self.compiled_patterns = {}
        for permission_type, patterns in self.permissions.items():
            if isinstance(patterns, list):
                self.compiled_patterns[permission_type] = self._compile_patterns(patterns)
    
    def _pattern_has_matches(self, pattern: str, permission_type: str) -> bool:
        """Check if a pattern matches any existing paths.
        
        Args:
            pattern: Glob pattern to check
            permission_type: Permission type (for context)
            
        Returns:
            bool: True if pattern matches existing paths, False otherwise
        """
        try:
            import glob
            import os
            
            # Expand home directory if present
            if pattern.startswith('~'):
                pattern = os.path.expanduser(pattern)
            
            # If we have a config directory and pattern is relative, resolve it
            if self.config_directory and not os.path.isabs(pattern):
                pattern = str(self.config_directory / pattern)
            
            # Use glob to check for matches
            matches = glob.glob(pattern)
            return len(matches) > 0
            
        except Exception:
            # If we can't check, assume it's valid to avoid false errors
            return True
    
    def _compile_patterns(self, patterns: List[str]) -> Tuple[pathspec.PathSpec, pathspec.PathSpec]:
        """Compile positive and negative patterns separately."""
        positive_patterns = []
        negative_patterns = []
        
        for pattern in patterns:
            if pattern.startswith('!'):
                negative_patterns.append(pattern[1:])  # Remove ! prefix
            else:
                positive_patterns.append(pattern)
        
        # Use gitwildmatch for consistent behavior with other pathspec-based plugins
        positive_spec = pathspec.PathSpec.from_lines('gitwildmatch', positive_patterns) if positive_patterns else pathspec.PathSpec([])
        negative_spec = pathspec.PathSpec.from_lines('gitwildmatch', negative_patterns) if negative_patterns else pathspec.PathSpec([])
        
        return positive_spec, negative_spec
    
    def _extract_paths(self, data: Any) -> List[str]:
        """Extract potential file paths from various data structures."""
        paths = []
        
        def extract_from_value(value):
            if isinstance(value, str):
                # Look for path-like patterns
                # Match absolute paths (including after colons like "error:/path")
                absolute_paths = re.findall(r'(?:^|[\s":]|(?<=:))(/[^\s"]+)', value)
                paths.extend(absolute_paths)
                
                # Match relative paths that look like file paths
                relative_paths = re.findall(r'(?:^|[\s"])([a-zA-Z0-9_\-./]+/[a-zA-Z0-9_\-./]+)', value)
                paths.extend(relative_paths)
                
                # Match Windows-style paths
                windows_paths = re.findall(r'(?:^|[\s"])([A-Za-z]:\\[^\s"]+)', value)
                paths.extend(windows_paths)
                
                # Also add any string that looks like a file path (including simple filenames)
                # This handles cases like "anything.txt" or other filenames
                if '.' in value and not value.startswith('.') and len(value) < 256:
                    # Simple heuristic: if it contains a dot and isn't too long, treat as a path
                    paths.append(value)
            elif isinstance(value, dict):
                # Handle filesystem tool argument patterns
                if "path" in value and isinstance(value["path"], str):
                    paths.append(value["path"])
                if "paths" in value and isinstance(value["paths"], list):
                    paths.extend([p for p in value["paths"] if isinstance(p, str)])
                if "source" in value and isinstance(value["source"], str):
                    paths.append(value["source"])
                if "destination" in value and isinstance(value["destination"], str):
                    paths.append(value["destination"])
                # Continue with general extraction
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)
        
        extract_from_value(data)
        return list(set(paths))  # Remove duplicates
    
    def _check_path_permission(self, path: str, required_permission: str) -> bool:
        """Check if path is allowed for the required permission type."""
        if required_permission not in self.compiled_patterns:
            # No specific permission configured - default deny
            return False
        
        positive_spec, negative_spec = self.compiled_patterns[required_permission]
        
        # Check positive patterns first
        if positive_spec.patterns and not positive_spec.match_file(path):
            return False
            
        # Check negative patterns (exclusions)
        if negative_spec.patterns and negative_spec.match_file(path):
            return False
            
        return True
    
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        """Check if request is allowed based on filesystem security policies."""
        # Only process tools/call requests
        if request.method != "tools/call":
            return PolicyDecision(
                allowed=True, 
                reason="Non-filesystem request",
                metadata={
                    "plugin": "filesystem_server",
                    "server_name": server_name,
                    "request_method": request.method,
                    "check_type": "request"
                }
            )
        
        # Extract tool name
        if not request.params or "name" not in request.params:
            return PolicyDecision(
                allowed=False, 
                reason="Missing tool name",
                metadata={
                    "plugin": "filesystem_server",
                    "server_name": server_name,
                    "request_method": request.method,
                    "check_type": "request",
                    "error": "missing_tool_name"
                }
            )
        
        tool_name = request.params["name"]
        
        # Validate tool is a filesystem tool
        if tool_name not in FILESYSTEM_TOOLS:
            return PolicyDecision(
                allowed=True, 
                reason="Non-filesystem tool",
                metadata={
                    "plugin": "filesystem_server",
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "check_type": "request",
                    "is_filesystem_tool": False
                }
            )
        
        # Extract file path(s) based on tool type
        arguments = request.params.get("arguments", {})
        paths = self._extract_paths(arguments)
        
        # Get required permission for this tool
        required_permission = FILESYSTEM_TOOLS[tool_name]
        
        # Special case for list_allowed_directories - no path check needed
        if tool_name == "list_allowed_directories":
            # Check if read permission is configured at all
            if "read" in self.permissions:
                return PolicyDecision(
                    allowed=True, 
                    reason="List allowed directories permitted",
                    metadata={
                        "plugin": "filesystem_server",
                        "server_name": server_name,
                        "tool_name": tool_name,
                        "required_permission": "read",
                        "check_type": "request",
                        "special_case": "list_allowed_directories"
                    }
                )
            else:
                return PolicyDecision(
                    allowed=False, 
                    reason="No read permissions configured",
                    metadata={
                        "plugin": "filesystem_server",
                        "server_name": server_name,
                        "tool_name": tool_name,
                        "required_permission": "read",
                        "check_type": "request",
                        "special_case": "list_allowed_directories",
                        "error": "no_read_permissions_configured"
                    }
                )
        
        # Check permissions for each path
        for path in paths:
            if not self._check_path_permission(path, required_permission):
                return PolicyDecision(
                    allowed=False, 
                    reason=f"Filesystem access denied for path '{path}' with {required_permission} permission",
                    metadata={
                        "plugin": "filesystem_server",
                        "server_name": server_name,
                        "tool_name": tool_name,
                        "required_permission": required_permission,
                        "check_type": "request",
                        "paths_checked": paths,
                        "denied_path": path,
                        "is_filesystem_tool": True
                    }
                )
        
        return PolicyDecision(
            allowed=True, 
            reason="Filesystem access permitted",
            metadata={
                "plugin": "filesystem_server",
                "server_name": server_name,
                "tool_name": tool_name,
                "required_permission": required_permission,
                "check_type": "request",
                "paths_checked": paths,
                "is_filesystem_tool": True
            }
        )
    
    async def check_response(self, request: MCPRequest, response: MCPResponse, server_name: str) -> PolicyDecision:
        """Check response to ensure it doesn't leak information about restricted paths.
        
        Responses from filesystem operations might contain:
        - File contents from restricted paths
        - Directory listings showing restricted files
        - Error messages revealing restricted path structures
        """
        # If there's an error response, check for path information leakage
        if response.error:
            error_msg = str(response.error.get("message", "")) if isinstance(response.error, dict) else str(response.error)
            # Extract any paths mentioned in error messages
            paths = self._extract_paths({"error": error_msg})
            for path in paths:
                # Check if we have read permission for this path
                if not self._check_path_permission(path, "read"):
                    # Sanitize the error to remove restricted path information
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Error message contains restricted path information: {path}",
                        metadata={
                            "plugin": "filesystem_server",
                            "server_name": server_name,
                            "check_type": "response",
                            "restricted_path": path,
                            "error_sanitized": True
                        }
                    )
        
        # For successful responses, check based on the original request method
        if request.method == "tools/call" and request.params and response.result:
            tool_name = request.params.get("name")
            
            # For directory listings, filter out restricted paths
            if tool_name == "list_directory" and isinstance(response.result, dict):
                entries = response.result.get("entries", [])
                if entries:
                    # Check each entry to see if it should be visible
                    filtered_entries = []
                    for entry in entries:
                        if isinstance(entry, dict) and "path" in entry:
                            entry_path = entry["path"]
                            if self._check_path_permission(entry_path, "read"):
                                filtered_entries.append(entry)
                    
                    # If we filtered anything, return a modified response
                    if len(filtered_entries) < len(entries):
                        import copy
                        modified_response = copy.deepcopy(response)
                        modified_response.result["entries"] = filtered_entries
                        return PolicyDecision(
                            allowed=True,
                            reason=f"Filtered directory listing: {len(entries) - len(filtered_entries)} restricted entries removed",
                            modified_content=modified_response,
                            metadata={
                                "plugin": "filesystem_server",
                                "server_name": server_name,
                                "tool_name": tool_name,
                                "check_type": "response",
                                "original_count": len(entries),
                                "filtered_count": len(filtered_entries),
                                "entries_removed": len(entries) - len(filtered_entries)
                            }
                        )
            
            # For file search results, filter out matches in restricted paths
            elif tool_name == "search_files" and isinstance(response.result, dict):
                matches = response.result.get("matches", [])
                if matches:
                    filtered_matches = []
                    for match in matches:
                        if isinstance(match, dict) and "path" in match:
                            match_path = match["path"]
                            if self._check_path_permission(match_path, "read"):
                                filtered_matches.append(match)
                    
                    if len(filtered_matches) < len(matches):
                        import copy
                        modified_response = copy.deepcopy(response)
                        modified_response.result["matches"] = filtered_matches
                        return PolicyDecision(
                            allowed=True,
                            reason=f"Filtered search results: {len(matches) - len(filtered_matches)} restricted matches removed",
                            modified_content=modified_response,
                            metadata={
                                "plugin": "filesystem_server",
                                "server_name": server_name,
                                "tool_name": tool_name,
                                "check_type": "response",
                                "original_count": len(matches),
                                "filtered_count": len(filtered_matches),
                                "matches_removed": len(matches) - len(filtered_matches)
                            }
                        )
        
        # Default: allow the response
        return PolicyDecision(
            allowed=True, 
            reason="Response permitted",
            metadata={
                "plugin": "filesystem_server",
                "server_name": server_name,
                "check_type": "response",
                "tool_name": request.params.get("name") if request.params else None
            }
        )
    
    async def check_notification(self, notification: MCPNotification, server_name: str) -> PolicyDecision:
        """Check notification to ensure it doesn't leak information about restricted paths.
        
        Notifications might contain:
        - File change notifications for restricted paths
        - Error notifications with path information
        - Status updates mentioning file operations on restricted paths
        """
        # Extract any paths from the notification
        paths = []
        
        # Check notification method for path patterns
        if notification.method:
            method_paths = self._extract_paths({"method": notification.method})
            paths.extend(method_paths)
        
        # Check notification parameters for paths
        if notification.params:
            param_paths = self._extract_paths(notification.params)
            paths.extend(param_paths)
        
        # Check if any of the paths are restricted
        for path in paths:
            # For notifications, we check read permission since they reveal information
            if not self._check_path_permission(path, "read"):
                return PolicyDecision(
                    allowed=False,
                    reason=f"Notification contains restricted path information: {path}",
                    metadata={
                        "plugin": "filesystem_server",
                        "server_name": server_name,
                        "check_type": "notification",
                        "notification_method": notification.method,
                        "restricted_path": path,
                        "paths_checked": paths
                    }
                )
        
        # Default: allow the notification
        return PolicyDecision(
            allowed=True, 
            reason="Notification permitted",
            metadata={
                "plugin": "filesystem_server",
                "server_name": server_name,
                "check_type": "notification",
                "notification_method": notification.method,
                "paths_checked": paths
            }
        )


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "filesystem_server": FilesystemServerSecurityPlugin
}
