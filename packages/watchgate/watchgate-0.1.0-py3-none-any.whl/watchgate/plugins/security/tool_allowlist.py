"""Tool allowlist security plugin implementation."""

import logging
import re
from typing import Dict, Any
from watchgate.plugins.interfaces import SecurityPlugin, PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification

logger = logging.getLogger(__name__)


class ToolAllowlistPlugin(SecurityPlugin):
    """Security plugin that implements tool allowlist/blocklist functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration."""
        # Validate configuration type first
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Initialize base class to set priority
        super().__init__(config)
        
        # Validate required mode parameter
        if "mode" not in config:
            raise ValueError("Configuration must include 'mode'")
        
        mode = config["mode"]
        if mode not in ["allow_all", "allowlist", "blocklist"]:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: allow_all, allowlist, blocklist")
        
        self.mode = mode
        
        # Handle tools parameter based on mode
        if mode in ["allowlist", "blocklist"]:
            if "tools" not in config:
                raise ValueError(f"Configuration must include 'tools' for {mode} mode")
            
            tools_config = config["tools"]
            if not isinstance(tools_config, dict):
                raise ValueError("'tools' must be a dictionary mapping server names to tool lists")
            
            # Validate that each server's tools value is a list
            for server_name, server_tools in tools_config.items():
                if not isinstance(server_tools, list):
                    raise ValueError(f"Tools for server '{server_name}' must be a list, got {type(server_tools).__name__}")
            
            self.tools_config = tools_config
        else:
            # For allow_all mode, tools parameter is ignored
            self.tools_config = {}
    
    async def check_request(self, request: MCPRequest, server_name: str) -> PolicyDecision:
        """Check if request should be allowed."""
        # Only apply policy to tools/call requests
        if request.method != "tools/call":
            return PolicyDecision(
                allowed=True,
                reason="Non-tool request always allowed",
                metadata={"mode": self.mode}
            )
        
        # Handle missing or invalid params
        if not request.params:
            return PolicyDecision(
                allowed=False,
                reason="Tool call missing tool name",
                metadata={"mode": self.mode}
            )
        
        if "name" not in request.params:
            return PolicyDecision(
                allowed=False,
                reason="Tool call missing tool name",
                metadata={"mode": self.mode}
            )
        
        tool_name = request.params["name"]
        if not isinstance(tool_name, str) or tool_name is None:
            return PolicyDecision(
                allowed=False,
                reason="Tool call missing tool name",
                metadata={"mode": self.mode}
            )
        
        # PluginManager now handles namespacing, so tool_name is always clean
        
        # Apply policy based on mode
        if self.mode == "allow_all":
            return PolicyDecision(
                allowed=True,
                reason="Allow-all mode permits all tools",
                metadata={"mode": self.mode, "tool": tool_name}
            )
        elif self.mode == "allowlist":
            server_tools = self.tools_config.get(server_name, [])
            allowed = tool_name in server_tools
            if allowed:
                reason = f"Tool '{tool_name}' is in allowlist for server '{server_name}'"
            else:
                reason = f"Tool '{tool_name}' is not in allowlist for server '{server_name}'"
            return PolicyDecision(
                allowed=allowed,
                reason=reason,
                metadata={"mode": self.mode, "tool": tool_name, "server": server_name}
            )
        elif self.mode == "blocklist":
            server_tools = self.tools_config.get(server_name, [])
            allowed = tool_name not in server_tools
            if not allowed:
                reason = f"Tool '{tool_name}' is in blocklist for server '{server_name}'"
            else:
                reason = f"Tool '{tool_name}' is not in blocklist for server '{server_name}'"
            return PolicyDecision(
                allowed=allowed,
                reason=reason,
                metadata={"mode": self.mode, "tool": tool_name, "server": server_name}
            )
        
        # Should never reach here due to validation, but just in case
        return PolicyDecision(
            allowed=False,
            reason="Unknown mode",
            metadata={"mode": self.mode}
        )
        
    async def check_response(self, request: MCPRequest, response: MCPResponse, server_name: str) -> PolicyDecision:
        """Check if response should be allowed.
        
        For tools/list responses, filters the tools list based on the allowlist/blocklist policy.
        For other responses, allows them unchanged.
        
        Args:
            request: The original MCP request
            response: The MCP response to evaluate
            
        Returns:
            PolicyDecision: Decision with potential response modification for tools/list
        """
        # Only apply filtering to tools/list requests
        if request.method != "tools/list":
            return PolicyDecision(
                allowed=True,
                reason="Tool access control plugin doesn't restrict non-tools/list responses",
                metadata={"mode": self.mode}
            )
        
        # For allow_all mode, no filtering needed
        if self.mode == "allow_all":
            return PolicyDecision(
                allowed=True,
                reason="Allow-all mode permits all tools",
                metadata={"mode": self.mode}
            )
        
        # For allowlist/blocklist modes, filter the tools/list response
        try:
            # Validate response structure
            if not response.result or "tools" not in response.result:
                return PolicyDecision(
                    allowed=False,
                    reason="Malformed tools/list response: missing tools field",
                    metadata={"mode": self.mode}
                )
            
            tools_list = response.result["tools"]
            if not isinstance(tools_list, list):
                return PolicyDecision(
                    allowed=False,
                    reason="Malformed tools/list response: tools field is not an array",
                    metadata={"mode": self.mode}
                )
            
            original_count = len(tools_list)
            
            # Filter tools based on mode and policy
            filtered_tools = []
            filtered_out_tools = []
            
            for tool in tools_list:
                # Skip tools without valid name field
                if not isinstance(tool, dict) or "name" not in tool or not tool["name"] or not isinstance(tool["name"], str):
                    continue
                
                tool_name = tool["name"]
                
                # PluginManager now handles namespacing, so tool_name is always clean
                server_tools = self.tools_config.get(server_name, [])
                check_tool_name = tool_name
                
                # Apply filtering logic based on mode
                if self.mode == "allowlist":
                    if check_tool_name in server_tools:
                        filtered_tools.append(tool)
                    else:
                        filtered_out_tools.append(tool_name)
                elif self.mode == "blocklist":
                    if check_tool_name not in server_tools:
                        filtered_tools.append(tool)
                    else:
                        filtered_out_tools.append(tool_name)
            
            filtered_count = len(filtered_tools)
            allowed_tool_names = [tool["name"] for tool in filtered_tools]
            
            # Create modified response if filtering occurred
            if original_count == 0:
                # Empty list - no modification needed
                return PolicyDecision(
                    allowed=True,
                    reason="Empty tools list requires no filtering",
                    metadata={
                        "mode": self.mode,
                        "original_count": 0,
                        "filtered_count": 0
                    }
                )
            elif filtered_count == original_count and len(filtered_out_tools) == 0:
                # No tools were filtered - no modification needed
                return PolicyDecision(
                    allowed=True,
                    reason="No tools filtered from tools/list response",
                    metadata={
                        "mode": self.mode,
                        "original_count": original_count,
                        "filtered_count": filtered_count
                    }
                )
            else:
                # Some tools were filtered - create modified response
                modified_response = MCPResponse(
                    jsonrpc=response.jsonrpc,
                    id=response.id,
                    result={
                        **response.result,  # Preserve other fields in result
                        "tools": filtered_tools
                    },
                    error=response.error,
                    sender_context=response.sender_context
                )
                
                # Log the filtering decision for audit purposes
                logger.info(
                    f"Tool access control filtered tools/list response: "
                    f"original={original_count} tools, filtered={filtered_count} tools, "
                    f"removed={filtered_out_tools}, allowed={allowed_tool_names}, "
                    f"mode={self.mode}, request_id={response.id}"
                )
                
                return PolicyDecision(
                    allowed=True,
                    reason=f"Filtered tools/list response: {len(filtered_out_tools)} tools removed",
                    metadata={
                        "mode": self.mode,
                        "original_count": original_count,
                        "filtered_count": filtered_count,
                        "filtered_tools": filtered_out_tools,
                        "allowed_tools": allowed_tool_names
                    },
                    modified_content=modified_response
                )
                
        except Exception as e:
            # If anything goes wrong during filtering, fail closed
            return PolicyDecision(
                allowed=False,
                reason=f"Error filtering tools/list response: {str(e)}",
                metadata={"mode": self.mode, "error": str(e)}
            )
        
    async def check_notification(self, notification: MCPNotification, server_name: str) -> PolicyDecision:
        """Check if notification should be allowed.
        
        This tool access control plugin doesn't enforce policy on notifications,
        so all notifications are allowed.
        
        Args:
            notification: The MCP notification to evaluate
            
        Returns:
            PolicyDecision: Always allowing the notification
        """
        return PolicyDecision(
            allowed=True,
            reason="Tool access control plugin doesn't restrict notifications",
            metadata={"mode": self.mode}
        )


# Policy manifest for policy-based plugin discovery
POLICIES = {
    "tool_allowlist": ToolAllowlistPlugin
}
