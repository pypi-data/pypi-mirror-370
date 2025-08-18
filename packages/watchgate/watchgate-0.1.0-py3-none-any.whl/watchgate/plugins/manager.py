"""Plugin manager for Watchgate MCP gateway.

This module provides the central orchestration of the plugin system,
including plugin discovery, loading, lifecycle management, and request/response
processing through the plugin pipeline.
"""

from typing import List, Dict, Any, Optional
import logging
import importlib
import importlib.util
from pathlib import Path
from watchgate.plugins.interfaces import SecurityPlugin, AuditingPlugin, PolicyDecision, PathResolvablePlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.utils.namespacing import create_denamespaced_request_params

logger = logging.getLogger(__name__)


class PluginManager:
    """Central orchestration of plugin system.
    
    The PluginManager handles loading plugins from configuration, managing their
    lifecycle, and orchestrating request/response flow through the plugin pipeline.
    It ensures proper error isolation so plugin failures don't crash the system.
    """
    
    def __init__(self, plugins_config: Dict[str, Any], config_directory: Optional[Path] = None):
        """Initialize with plugin configuration from YAML.
        
        Args:
            plugins_config: Dictionary containing 'security' and 'auditing' plugin configs
                          Expected format (upstream-scoped):
                          {
                              "security": {
                                  "_global": [{"policy": "plugin_name", "enabled": True, "config": {...}}],
                                  "upstream_name": [{"policy": "plugin_name", "enabled": True, "config": {...}}]
                              },
                              "auditing": {
                                  "_global": [{"policy": "plugin_name", "enabled": True, "config": {...}}],
                                  "upstream_name": [{"policy": "plugin_name", "enabled": True, "config": {...}}]
                              }
                          }
            config_directory: Directory containing the configuration file (for path resolution)
        """
        self.plugins_config = plugins_config
        self.config_directory = config_directory
        
        # Upstream-scoped plugin storage: upstream_name -> [plugins]
        self.upstream_security_plugins: Dict[str, List[SecurityPlugin]] = {}
        self.upstream_auditing_plugins: Dict[str, List[AuditingPlugin]] = {}
        
        
        self._initialized = False
        self._load_failures: List[Dict[str, str]] = []  # Track plugin load failures
    
    @property
    def security_plugins(self) -> List[SecurityPlugin]:
        """Get global security plugins for compatibility."""
        return self.upstream_security_plugins.get("_global", [])
    
    @security_plugins.setter
    def security_plugins(self, plugins: List[SecurityPlugin]) -> None:
        """Set global security plugins for compatibility."""
        self.upstream_security_plugins["_global"] = plugins
    
    @property
    def auditing_plugins(self) -> List[AuditingPlugin]:
        """Get global auditing plugins for compatibility."""
        return self.upstream_auditing_plugins.get("_global", [])
    
    @auditing_plugins.setter
    def auditing_plugins(self, plugins: List[AuditingPlugin]) -> None:
        """Set global auditing plugins for compatibility."""
        self.upstream_auditing_plugins["_global"] = plugins
    
    async def load_plugins(self) -> None:
        """Discover and load configured plugins.
        
        Loads security and auditing plugins from configuration. Plugin loading
        failures are logged but don't prevent other plugins from loading or
        crash the system.
        
        Raises:
            Exception: Only if no plugins can be loaded and configuration requires them
        """
        if self._initialized:
            logger.warning("Plugin manager already initialized, skipping reload")
            return
        
        logger.info("Loading plugins from configuration")
        
        # Load plugins - dictionary format only
        security_config = self.plugins_config.get("security", {})
        auditing_config = self.plugins_config.get("auditing", {})
        
        # Load upstream-scoped plugins
        self._load_upstream_scoped_security_plugins(security_config)
        self._load_upstream_scoped_auditing_plugins(auditing_config)
        
        self._initialized = True
        
        # Count total plugins across all upstreams
        total_security = sum(len(plugins) for plugins in self.upstream_security_plugins.values())
        total_auditing = sum(len(plugins) for plugins in self.upstream_auditing_plugins.values())
        
        logger.info(
            f"Plugin loading complete: {total_security} security, "
            f"{total_auditing} auditing plugins loaded across {len(self.upstream_security_plugins)} upstreams"
        )
    
    def has_load_failures(self) -> bool:
        """Check if there were any plugin load failures.
        
        Returns:
            bool: True if any plugins failed to load, False otherwise
        """
        return len(self._load_failures) > 0
    
    def get_load_failures(self) -> List[Dict[str, str]]:
        """Get details of plugin load failures.
        
        Returns:
            List[Dict[str, str]]: List of failure details with 'type', 'policy', and 'error' keys
        """
        return self._load_failures.copy()
    
    def get_plugins_for_upstream(self, upstream_name: str) -> Dict[str, List]:
        """Get plugins for a specific upstream with global fallback.
        
        Returns plugins for the specified upstream, combining global policies
        with upstream-specific policies. Upstream-specific policies override
        global policies with the same name.
        
        Args:
            upstream_name: Name of the upstream to get plugins for
            
        Returns:
            Dict with 'security' and 'auditing' keys containing plugin lists
        """
        if not self._initialized:
            logger.warning("Plugin manager not initialized, returning empty plugin sets")
            return {"security": [], "auditing": []}
        
        # Get security plugins for upstream
        security_plugins = self._resolve_plugins_for_upstream(
            self.upstream_security_plugins, upstream_name
        )
        
        # Get auditing plugins for upstream
        auditing_plugins = self._resolve_plugins_for_upstream(
            self.upstream_auditing_plugins, upstream_name
        )
        
        return {
            "security": security_plugins,
            "auditing": auditing_plugins
        }
    
    def _resolve_plugins_for_upstream(self, upstream_plugins_dict: Dict[str, List], upstream_name: str) -> List:
        """Resolve plugins for an upstream with global fallback and policy override.
        
        Args:
            upstream_plugins_dict: Dictionary of upstream -> plugin lists
            upstream_name: Name of the upstream to resolve plugins for
            
        Returns:
            List of plugins for the upstream (global + upstream-specific with overrides)
        """
        resolved_plugins = []
        plugin_names_added = set()
        
        # Start with global plugins if they exist
        global_plugins = upstream_plugins_dict.get("_global", [])
        for plugin in global_plugins:
            plugin_policy = getattr(plugin, 'policy', plugin.__class__.__name__)
            resolved_plugins.append(plugin)
            plugin_names_added.add(plugin_policy)
        
        # Add upstream-specific plugins, overriding global ones with same policy name
        upstream_plugins = upstream_plugins_dict.get(upstream_name, [])
        for plugin in upstream_plugins:
            plugin_policy = getattr(plugin, 'policy', plugin.__class__.__name__)
            
            if plugin_policy in plugin_names_added:
                # Override: remove global plugin with same policy name
                resolved_plugins = [p for p in resolved_plugins 
                                  if getattr(p, 'policy', p.__class__.__name__) != plugin_policy]
            
            resolved_plugins.append(plugin)
            plugin_names_added.add(plugin_policy)
        
        # Sort by priority (lower number = higher priority)
        resolved_plugins.sort(key=lambda p: getattr(p, 'priority', 50))
        
        return resolved_plugins
    
    async def _execute_plugin_check(self, plugin, check_method_name: str, *args, **kwargs) -> PolicyDecision:
        """Execute a plugin check method with automatic metadata injection.
        
        Args:
            plugin: The plugin instance to execute
            check_method_name: Name of the method to call ('check_request', 'check_response', 'check_notification')
            *args: Arguments to pass to the check method
            **kwargs: Keyword arguments to pass to the check method
            
        Returns:
            PolicyDecision: Decision with plugin name automatically added to metadata
        """
        plugin_name = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
        logger.debug(f"Executing security plugin {plugin_name} with priority {getattr(plugin, 'priority', 50)}")
        
        check_method = getattr(plugin, check_method_name)
        decision = await check_method(*args, **kwargs)
        
        # Automatically add plugin name to metadata
        if decision.metadata is None:
            decision.metadata = {}
        decision.metadata["plugin"] = plugin_name
        
        return decision


    async def process_request(self, request: MCPRequest, server_name: Optional[str] = None) -> PolicyDecision:
        """Run request through upstream-scoped security plugins in priority order.
        
        Processes the request through security plugins for the specified upstream.
        Combines global (_global) plugins with upstream-specific plugins, where
        upstream-specific plugins override global ones with the same policy name.
        
        Args:
            request: The MCP request to evaluate
            server_name: Name of the target upstream server
            
        Returns:
            PolicyDecision: Combined decision from security plugins for the upstream
        """
        if not self._initialized:
            await self.load_plugins()
        
        
        # Get upstream-specific plugins
        upstream_plugins = self.get_plugins_for_upstream(server_name or "unknown")
        security_plugins = upstream_plugins["security"]
        
        # If no security plugins for this upstream, allow by default
        if not security_plugins:
            return PolicyDecision(
                allowed=True, 
                reason=f"No security plugins configured for upstream '{server_name or 'unknown'}'", 
                metadata={
                    "plugin_count": 0,
                    "upstream": server_name,
                    "plugins_applied": []
                }
            )
        
        # Plugins are already sorted by priority during resolution
        # Log the plugin execution order at debug level
        plugin_info = [(getattr(p, 'plugin_id', p.__class__.__name__), getattr(p, 'priority', 50)) for p in security_plugins]
        logger.debug(f"Plugin execution order for upstream '{server_name}': {plugin_info}")
        
        # Process through all security plugins in priority order
        # Create clean request for plugin processing (plugins should see clean tool names)
        if server_name and request.params:
            denamespaced_params = create_denamespaced_request_params(request.method, request.params)
            current_request = MCPRequest(
                jsonrpc=request.jsonrpc,
                method=request.method,
                id=request.id,
                params=denamespaced_params,
                sender_context=request.sender_context
            )
        else:
            current_request = request
        
        plugin_names = [getattr(p, 'plugin_id', p.__class__.__name__) for p in security_plugins]
        final_decision = PolicyDecision(
            allowed=True,
            reason=f"Allowed by all security plugins for upstream '{server_name or 'unknown'}'",
            metadata={
                "plugin_count": len(security_plugins),
                "upstream": server_name,
                "plugins_applied": plugin_names
            }
        )
        
        for plugin in security_plugins:
            try:
                decision = await self._execute_plugin_check(plugin, 'check_request', current_request, server_name=server_name)
                
                # If any plugin denies, stop processing and return denial
                if not decision.allowed:
                    logger.info(
                        f"Request denied by security plugin {decision.metadata['plugin']}: {decision.reason}"
                    )
                    return decision
                
                # Handle successful decisions - preserve meaningful context
                if decision.reason and decision.reason != "Request allowed":
                    # Plugin provided meaningful context, preserve it
                    final_decision.reason = decision.reason
                    # Merge plugin metadata with existing metadata (preserve plugin_count)
                    plugin_metadata = decision.metadata or {}
                    final_decision.metadata.update(plugin_metadata)
                
                # Handle request modifications
                if decision.modified_content and isinstance(decision.modified_content, MCPRequest):
                    current_request = decision.modified_content
                    final_decision.modified_content = current_request
                    final_decision.reason = decision.reason
                    # For content modifications, replace metadata but preserve plugin_count
                    plugin_count = final_decision.metadata.get("plugin_count", len(security_plugins))
                    final_decision.metadata = decision.metadata or {}
                    final_decision.metadata["plugin_count"] = plugin_count
                    logger.debug(
                        f"Request modified by security plugin {getattr(plugin, 'plugin_id', plugin.__class__.__name__)}: {decision.reason}"
                    )
                    
            except Exception as e:
                # Check if plugin is critical to determine failure behavior
                plugin_name = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
                
                if hasattr(plugin, 'is_critical') and not plugin.is_critical():
                    # Non-critical plugin failure: log warning and continue
                    logger.warning(f"Non-critical security plugin {plugin_name} failed: {e}")
                    
                    # Continue processing with remaining plugins
                    continue
                else:
                    # Critical plugin failure: fail closed for security
                    logger.error(
                        f"Critical security plugin {plugin_name} failed: {e}",
                        exc_info=True
                    )
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Critical security plugin {plugin_name} failed",
                        metadata={"error": str(e), "plugin_failure": True}
                    )
        
        # All plugins allowed the request
        return final_decision
        
    async def process_response(self, request: MCPRequest, response: MCPResponse, server_name: Optional[str] = None) -> PolicyDecision:
        """Run response through upstream-scoped security plugins.
        
        Processes the response through security plugins for the specified upstream.
        Combines global (_global) plugins with upstream-specific plugins, where
        upstream-specific plugins override global ones with the same policy name.
        
        Args:
            request: The original MCP request for correlation
            response: The MCP response to evaluate
            server_name: Optional name of the source server
            
        Returns:
            PolicyDecision: Combined decision from security plugins for the upstream
        """
        if not self._initialized:
            await self.load_plugins()
        
        
        # Get upstream-specific plugins
        upstream_plugins = self.get_plugins_for_upstream(server_name or "unknown")
        security_plugins = upstream_plugins["security"]
        
        # If no security plugins for this upstream, allow by default
        if not security_plugins:
            return PolicyDecision(
                allowed=True, 
                reason=f"No security plugins configured for upstream '{server_name or 'unknown'}'", 
                metadata={
                    "plugin_count": 0,
                    "upstream": server_name,
                    "plugins_applied": []
                }
            )
        
        # For aggregated tools/list responses (server_name=None), we need special handling
        # to provide proper server context to plugins for each tool
        if server_name is None and request.method == "tools/list":
            return await self._process_aggregated_tools_list_response(request, response)
        
        # For other responses, process normally
        return await self._process_single_server_response(request, response, server_name)

    async def _process_single_server_response(self, request: MCPRequest, response: MCPResponse, server_name: Optional[str]) -> PolicyDecision:
        """Process response from a single server through upstream-scoped security plugins.
        
        Args:
            request: The original MCP request
            response: The MCP response from specific server
            server_name: Name of the source server (None for non-aggregated responses)
            
        Returns:
            PolicyDecision: Decision from processing the response
        """
        # Get upstream-specific plugins
        upstream_plugins = self.get_plugins_for_upstream(server_name or "unknown")
        security_plugins = upstream_plugins["security"]
        
        # Plugins are already sorted by priority during resolution
        server_label = server_name if server_name else "unknown"
        logger.debug(f"Direct server response filtering for server '{server_label}': {[(getattr(p, 'plugin_id', p.__class__.__name__), getattr(p, 'priority', 50)) for p in security_plugins]}")
        
        # For tools/list responses, ensure plugins see clean tools even if response is pre-namespaced
        if request.method == "tools/list" and server_name and response.result and "tools" in response.result:
            from watchgate.utils.namespacing import denamespace_tools_response, namespace_tools_response
            
            tools_list = response.result["tools"]
            # Check if tools are already namespaced (from broadcast aggregation)
            if any(isinstance(tool, dict) and "name" in tool and isinstance(tool["name"], str) and "__" in tool["name"] for tool in tools_list):
                logger.debug(f"De-namespacing tools for server {server_name}")
                # Tools are namespaced, need to extract just this server's tools
                tools_by_server = denamespace_tools_response(tools_list)
                clean_tools = tools_by_server.get(server_name, [])
                
                # Create clean response for plugin processing
                current_response = MCPResponse(
                    jsonrpc=response.jsonrpc,
                    id=response.id,
                    result={**response.result, "tools": clean_tools},
                    error=response.error,
                    sender_context=response.sender_context
                )
                # Mark as denamespaced so we can re-namespace the result
                current_response._was_denamespaced = True
            else:
                # Tools are already clean
                current_response = response
        else:
            # Process through all security plugins in priority order
            current_response = response
        final_decision = PolicyDecision(
            allowed=True,
            reason=f"Response allowed by all security plugins for upstream '{server_label}'",
            metadata={
                "plugin_count": len(security_plugins),
                "upstream": server_name,
                "plugins_applied": [getattr(p, 'plugin_id', p.__class__.__name__) for p in security_plugins]
            }
        )
        
        for plugin in security_plugins:
            try:
                # For direct server responses, tools are already clean (non-namespaced)
                decision = await self._execute_plugin_check(plugin, 'check_response', request, current_response, server_name=server_name)
                
                # If any plugin denies, stop processing and return denial
                if not decision.allowed:
                    logger.info(
                        f"Response denied by security plugin {decision.metadata['plugin']}: {decision.reason}"
                    )
                    return decision
                
                # If plugin modified the response, use it for subsequent plugins
                if decision.modified_content and isinstance(decision.modified_content, MCPResponse):
                    current_response = decision.modified_content
                    final_decision.modified_content = current_response
                    # Preserve meaningful plugin context
                    final_decision.reason = decision.reason
                    # For content modifications, replace metadata but preserve plugin_count and upstream
                    plugin_count = final_decision.metadata.get("plugin_count", len(security_plugins))
                    upstream = final_decision.metadata.get("upstream", server_name)
                    final_decision.metadata = decision.metadata or {}
                    final_decision.metadata["plugin_count"] = plugin_count
                    final_decision.metadata["upstream"] = upstream
                    logger.debug(
                        f"Response modified by security plugin {plugin.__class__.__name__}: {decision.reason}"
                    )
                    
            except Exception as e:
                # Check if plugin is critical to determine failure behavior
                plugin_name = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
                
                if hasattr(plugin, 'is_critical') and not plugin.is_critical():
                    # Non-critical plugin failure: log warning and continue
                    logger.warning(f"Non-critical security plugin {plugin_name} failed on response: {e}")
                    continue
                else:
                    # Critical plugin failure: fail closed for security
                    logger.error(
                        f"Critical security plugin {plugin_name} failed on response: {e}",
                        exc_info=True
                    )
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Critical security plugin {plugin_name} failed on response",
                        metadata={"error": str(e), "plugin_failure": True}
                    )
        
        # For tools/list responses that were de-namespaced, re-namespace the filtered result
        if (request.method == "tools/list" and server_name and 
            hasattr(current_response, '_was_denamespaced') and current_response._was_denamespaced):
            
            logger.debug(f"Re-namespacing tools for server {server_name}")
            from watchgate.utils.namespacing import namespace_tools_response
            
            # Determine which response to re-namespace
            if final_decision.modified_content and isinstance(final_decision.modified_content, MCPResponse):
                # Plugin modified the response, re-namespace the modified version
                modified_response = final_decision.modified_content
            else:
                # No plugin modification, but we still need to re-namespace the de-namespaced response
                modified_response = current_response
                
            if modified_response.result and "tools" in modified_response.result:
                clean_tools = modified_response.result["tools"]
                namespaced_tools = namespace_tools_response(server_name, clean_tools)
                
                final_decision.modified_content = MCPResponse(
                    jsonrpc=modified_response.jsonrpc,
                    id=modified_response.id,
                    result={**modified_response.result, "tools": namespaced_tools},
                    error=modified_response.error,
                    sender_context=modified_response.sender_context
                )
        
        # All plugins allowed the response
        return final_decision

    async def _process_aggregated_tools_list_response(self, request: MCPRequest, response: MCPResponse) -> PolicyDecision:
        """Process aggregated tools/list response by grouping tools by server and processing each group.
        
        This method handles tools/list responses that contain namespaced tools from multiple servers
        (or a single named server). It groups tools by server and processes each group with the 
        appropriate server context.
        
        Args:
            request: The original MCP request
            response: The aggregated MCP response with namespaced tools
            
        Returns:
            PolicyDecision: Decision from processing all tool groups
        """
        from watchgate.utils.namespacing import denamespace_tools_response, namespace_tools_response
        
        # Get total count of all security plugins across all upstreams for metadata
        total_plugin_count = sum(len(plugins) for plugins in self.upstream_security_plugins.values())
        
        # Validate response structure
        if not response.result or "tools" not in response.result:
            return PolicyDecision(
                allowed=True,
                reason="No tools in response to filter",
                metadata={"plugin_count": total_plugin_count}
            )
        
        tools_list = response.result["tools"]
        if not isinstance(tools_list, list):
            return PolicyDecision(
                allowed=False,
                reason="Malformed tools/list response: tools field is not an array",
                metadata={"plugin_count": total_plugin_count}
            )
        
        # Group tools by server using utility function
        tools_by_server = denamespace_tools_response(tools_list)
        
        # Process each server's tools through plugins
        final_tools = []
        for server_name, clean_tools in tools_by_server.items():
            # Create a temporary response for this server's tools
            temp_response = MCPResponse(
                jsonrpc=response.jsonrpc,
                id=response.id,
                result={"tools": clean_tools},
                error=response.error,
                sender_context=response.sender_context
            )
            
            # Get upstream-specific plugins for this server
            upstream_plugins = self.get_plugins_for_upstream(server_name)
            server_security_plugins = upstream_plugins["security"]
            
            # Process through all security plugins with proper server context
            current_response = temp_response
            for plugin in server_security_plugins:
                try:
                    decision = await self._execute_plugin_check(plugin, 'check_response', request, current_response, server_name=server_name)
                    
                    if not decision.allowed:
                        logger.info(
                            f"Aggregated response denied by security plugin {decision.metadata['plugin']}: {decision.reason}"
                        )
                        return decision
                    
                    # If plugin modified the response, use it for subsequent plugins
                    if decision.modified_content and isinstance(decision.modified_content, MCPResponse):
                        current_response = decision.modified_content
                        
                except Exception as e:
                    # Check if plugin is critical to determine failure behavior
                    plugin_name = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
                    
                    if hasattr(plugin, 'is_critical') and not plugin.is_critical():
                        # Non-critical plugin failure: log warning and continue
                        logger.warning(f"Non-critical security plugin {plugin_name} failed on aggregated response: {e}")
                        continue
                    else:
                        # Critical plugin failure: fail closed for security
                        logger.error(
                            f"Critical security plugin {plugin_name} failed on aggregated response: {e}",
                            exc_info=True
                        )
                        return PolicyDecision(
                            allowed=False,
                            reason=f"Critical security plugin {plugin_name} failed on aggregated response",
                            metadata={"error": str(e), "plugin_failure": True}
                        )
            
            # Re-namespace the filtered tools and add to final list
            if current_response.result and "tools" in current_response.result:
                filtered_clean_tools = current_response.result["tools"]
                if server_name:
                    # Re-namespace the tools for the final response
                    namespaced_tools = namespace_tools_response(server_name, filtered_clean_tools)
                    final_tools.extend(namespaced_tools)
                else:
                    # No namespacing needed for tools without server context
                    final_tools.extend(filtered_clean_tools)
        
        # Create final response
        if len(final_tools) == len(tools_list):
            # No filtering occurred
            return PolicyDecision(
                allowed=True,
                reason="No tools filtered from aggregated response",
                metadata={"plugin_count": total_plugin_count}
            )
        else:
            # Some tools were filtered
            modified_response = MCPResponse(
                jsonrpc=response.jsonrpc,
                id=response.id,
                result={
                    **response.result,
                    "tools": final_tools
                },
                error=response.error,
                sender_context=response.sender_context
            )
            
            return PolicyDecision(
                allowed=True,
                reason=f"Filtered aggregated response: {len(tools_list) - len(final_tools)} tools removed",
                metadata={
                    "plugin_count": total_plugin_count,
                    "original_count": len(tools_list),
                    "filtered_count": len(final_tools)
                },
                modified_content=modified_response
            )
    
    async def process_notification(self, notification: MCPNotification, server_name: Optional[str] = None) -> PolicyDecision:
        """Run notification through upstream-scoped security plugins.
        
        Processes the notification through security plugins for the specified upstream.
        Combines global (_global) plugins with upstream-specific plugins, where
        upstream-specific plugins override global ones with the same policy name.
        
        Args:
            notification: The MCP notification to evaluate
            server_name: Optional name of the source server
            
        Returns:
            PolicyDecision: Combined decision from security plugins for the upstream
        """
        if not self._initialized:
            await self.load_plugins()
        
        
        # Get upstream-specific plugins
        upstream_plugins = self.get_plugins_for_upstream(server_name or "unknown")
        security_plugins = upstream_plugins["security"]
        
        # If no security plugins for this upstream, allow by default
        if not security_plugins:
            return PolicyDecision(
                allowed=True, 
                reason=f"No security plugins configured for upstream '{server_name or 'unknown'}'", 
                metadata={
                    "plugin_count": 0,
                    "upstream": server_name,
                    "plugins_applied": []
                }
            )
        
        # Plugins are already sorted by priority during resolution
        # Log the plugin execution order at debug level
        plugin_info = [(getattr(p, 'plugin_id', p.__class__.__name__), getattr(p, 'priority', 50)) for p in security_plugins]
        logger.debug(f"Notification plugin execution order for upstream '{server_name}': {plugin_info}")
        
        # Process through all security plugins in priority order
        # Track notification modifications
        current_notification = notification
        plugin_names = [getattr(p, 'plugin_id', p.__class__.__name__) for p in security_plugins]
        final_decision = PolicyDecision(
            allowed=True,
            reason=f"Notification allowed by all security plugins for upstream '{server_name or 'unknown'}'",
            metadata={
                "plugin_count": len(security_plugins),
                "upstream": server_name,
                "plugins_applied": plugin_names
            }
        )
        
        for plugin in security_plugins:
            try:
                decision = await self._execute_plugin_check(plugin, 'check_notification', current_notification, server_name=server_name)
                
                # If any plugin denies, stop processing and return denial
                if not decision.allowed:
                    logger.info(
                        f"Notification denied by security plugin {decision.metadata['plugin']}: {decision.reason}"
                    )
                    return decision
                
                # Handle notification modifications
                if decision.modified_content and isinstance(decision.modified_content, MCPNotification):
                    current_notification = decision.modified_content
                    final_decision.modified_content = current_notification
                    final_decision.reason = decision.reason
                    # For content modifications, replace metadata but preserve plugin_count and upstream
                    plugin_count = final_decision.metadata.get("plugin_count", len(security_plugins))
                    upstream = final_decision.metadata.get("upstream", server_name)
                    final_decision.metadata = decision.metadata or {}
                    final_decision.metadata["plugin_count"] = plugin_count
                    final_decision.metadata["upstream"] = upstream
                    logger.debug(
                        f"Notification modified by security plugin {plugin.__class__.__name__}: {decision.reason}"
                    )
                    
            except Exception as e:
                # Check if plugin is critical to determine failure behavior
                plugin_name = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
                
                if hasattr(plugin, 'is_critical') and not plugin.is_critical():
                    # Non-critical plugin failure: log warning and continue
                    logger.warning(f"Non-critical security plugin {plugin_name} failed on notification: {e}")
                    
                    # Continue processing with remaining plugins
                    continue
                else:
                    # Critical plugin failure: fail closed for security
                    logger.error(
                        f"Critical security plugin {plugin_name} failed on notification: {e}",
                        exc_info=True
                    )
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Critical security plugin {plugin_name} failed on notification",
                        metadata={"error": str(e), "plugin_failure": True}
                    )
        
        # All plugins allowed the notification
        return final_decision
        
    async def log_request(self, request: MCPRequest, decision: PolicyDecision, server_name: Optional[str] = None) -> None:
        """Send request to upstream-scoped auditing plugins.
        
        Sends the request and policy decision to auditing plugins configured
        for the specified upstream. Combines global and upstream-specific plugins.
        
        Args:
            request: The MCP request being processed
            decision: The security policy decision for this request
            server_name: Name of the target upstream server
        """
        if not self._initialized:
            await self.load_plugins()
        
        
        # Get upstream-specific auditing plugins
        upstream_plugins = self.get_plugins_for_upstream(server_name or "unknown")
        auditing_plugins = upstream_plugins["auditing"]
        
        # Add upstream context to decision metadata
        if decision.metadata is None:
            decision.metadata = {}
        decision.metadata["upstream"] = server_name
        
        # Send to all auditing plugins for this upstream in priority order
        for plugin in auditing_plugins:
            try:
                await plugin.log_request(request, decision, server_name=server_name)
                logger.debug(f"Auditing plugin {plugin.plugin_id} logged request for upstream '{server_name}'")
            except Exception as e:
                # Auditing failures are logged but don't block processing
                logger.error(
                    f"Auditing plugin {plugin.plugin_id} failed to log request for upstream '{server_name}': {e}",
                    exc_info=True
                )
        
    async def log_response(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: Optional[str] = None) -> None:
        """Send response to upstream-scoped auditing plugins.
        
        Sends the request, response, and security decision to auditing plugins
        configured for the specified upstream. Combines global and upstream-specific plugins.
        
        Args:
            request: The original MCP request for correlation
            response: The MCP response from the upstream server
            decision: The policy decision made by security plugins for this response
            server_name: Name of the source upstream server
        """
        if not self._initialized:
            await self.load_plugins()
        
        
        # Get upstream-specific auditing plugins
        upstream_plugins = self.get_plugins_for_upstream(server_name or "unknown")
        auditing_plugins = upstream_plugins["auditing"]
        
        # Add upstream context to decision metadata
        if decision.metadata is None:
            decision.metadata = {}
        decision.metadata["upstream"] = server_name
        
        # Send to all auditing plugins for this upstream in priority order
        for plugin in auditing_plugins:
            try:
                await plugin.log_response(request, response, decision, server_name=server_name)
                logger.debug(f"Auditing plugin {plugin.plugin_id} logged response for upstream '{server_name}'")
            except Exception as e:
                # Auditing failures are logged but don't block processing
                logger.error(
                    f"Auditing plugin {plugin.plugin_id} failed to log response for upstream '{server_name}': {e}",
                    exc_info=True
                )
                
    async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, server_name: Optional[str] = None) -> None:
        """Send notification to upstream-scoped auditing plugins.
        
        Sends the notification and policy decision to auditing plugins configured
        for the specified upstream. Combines global and upstream-specific plugins.
        
        Args:
            notification: The MCP notification being processed
            decision: The policy decision from security plugins
            server_name: Optional name of the source server
        """
        if not self._initialized:
            await self.load_plugins()
        
        
        # Get upstream-specific auditing plugins
        upstream_plugins = self.get_plugins_for_upstream(server_name or "unknown")
        auditing_plugins = upstream_plugins["auditing"]
        
        # Add upstream context to decision metadata
        if decision.metadata is None:
            decision.metadata = {}
        decision.metadata["upstream"] = server_name
        
        # Send to all auditing plugins for this upstream in priority order
        for plugin in auditing_plugins:
            try:
                await plugin.log_notification(notification, decision, server_name=server_name)
                logger.debug(f"Auditing plugin {plugin.plugin_id} logged notification for upstream '{server_name}'")
            except Exception as e:
                # Auditing failures are logged but don't block processing
                logger.error(
                    f"Auditing plugin {getattr(plugin, 'plugin_id', plugin.__class__.__name__)} failed to log notification for upstream '{server_name}': {e}",
                    exc_info=True
                )
    
    def _create_plugin_instance(self, plugin_class, plugin_config: Dict[str, Any], policy_name: str, plugin_type: str):
        """Create a plugin instance with proper configuration and validation.
        
        Args:
            plugin_class: The plugin class to instantiate
            plugin_config: Plugin configuration dictionary
            policy_name: Name of the policy
            plugin_type: Type of plugin ("security" or "auditing")
            
        Returns:
            Plugin instance or None if creation failed
        """
        # Validate plugin interface
        self._validate_plugin_interface(plugin_type, plugin_class, policy_name)
        
        # Create plugin instance with original config (no config_directory injection)
        plugin_config_dict = plugin_config.get("config", {}).copy()
        # Include priority in the config passed to plugin
        if "priority" in plugin_config:
            plugin_config_dict["priority"] = plugin_config["priority"]
        
        plugin_instance = plugin_class(plugin_config_dict)
        
        # Set policy name for tracking
        if hasattr(plugin_instance, 'policy') or not hasattr(plugin_instance, 'policy'):
            plugin_instance.policy = policy_name
        
        # Set config directory if plugin implements PathResolvablePlugin
        if self.config_directory is not None and isinstance(plugin_instance, PathResolvablePlugin):
            plugin_instance.set_config_directory(self.config_directory)
            logger.debug(f"Set config directory for {plugin_type} plugin {policy_name}: {self.config_directory}")
                
            # Validate paths for PathResolvablePlugin instances
            path_errors = plugin_instance.validate_paths()
            if path_errors:
                # Check if plugin is critical to determine error handling
                is_critical = plugin_config_dict.get("critical", True)
                if is_critical:
                    raise ValueError(
                        f"{plugin_type.capitalize()} plugin '{policy_name}' path validation failed: " +
                        "; ".join(path_errors)
                    )
                else:
                    # For non-critical plugins, log warning but continue
                    logger.warning(
                        f"Non-critical {plugin_type} plugin '{policy_name}' has path validation errors: {'; '.join(path_errors)}"
                    )
        
        return plugin_instance
    
    def _load_upstream_scoped_security_plugins(self, security_config: Dict[str, List[Dict[str, Any]]]) -> None:
        """Load security plugins from upstream-scoped configuration.
        
        Args:
            security_config: Dictionary mapping upstream names to lists of security plugin configurations
        """
        # Clear existing plugins
        self.upstream_security_plugins.clear()
        
        if not security_config:
            logger.info("No security plugin configuration found")
            return
        
        # Discover available security policies
        available_policies = self._discover_policies("security")
        
        for upstream_name, plugin_configs in security_config.items():
            logger.debug(f"Loading security plugins for upstream '{upstream_name}'")
            upstream_plugins = []
            
            for plugin_config in plugin_configs:
                if not plugin_config.get("enabled", True):
                    logger.debug(f"Skipping disabled security plugin: {plugin_config.get('policy', 'unknown')}")
                    continue
                    
                policy_name = plugin_config.get("policy")
                
                if not policy_name:
                    logger.error(f"Security plugin configuration missing 'policy' field for upstream '{upstream_name}'")
                    continue
                    
                if policy_name not in available_policies:
                    available_names = ", ".join(available_policies.keys())
                    raise ValueError(f"Policy '{policy_name}' not found. Available policies: {available_names}")
                    
                try:
                    plugin_class = available_policies[policy_name]
                    plugin_instance = self._create_plugin_instance(
                        plugin_class, plugin_config, policy_name, "security"
                    )
                    if plugin_instance:
                        upstream_plugins.append(plugin_instance)
                        logger.debug(f"Loaded security plugin '{policy_name}' for upstream '{upstream_name}'")
                except Exception as e:
                    logger.error(f"Failed to load security plugin '{policy_name}' for upstream '{upstream_name}': {e}")
                    self._load_failures.append({
                        "type": "security",
                        "policy": policy_name,
                        "upstream": upstream_name,
                        "error": str(e)
                    })
            
            # Sort plugins by priority (lower number = higher priority)
            upstream_plugins.sort(key=lambda p: getattr(p, 'priority', 50))
            self.upstream_security_plugins[upstream_name] = upstream_plugins
            
            logger.info(f"Loaded {len(upstream_plugins)} security plugins for upstream '{upstream_name}'")
    
    def _load_upstream_scoped_auditing_plugins(self, auditing_config: Dict[str, List[Dict[str, Any]]]) -> None:
        """Load auditing plugins from upstream-scoped configuration.
        
        Args:
            auditing_config: Dictionary mapping upstream names to lists of auditing plugin configurations
        """
        # Clear existing plugins
        self.upstream_auditing_plugins.clear()
        
        if not auditing_config:
            logger.info("No auditing plugin configuration found")
            return
        
        # Discover available auditing policies
        available_policies = self._discover_policies("auditing")
        
        for upstream_name, plugin_configs in auditing_config.items():
            logger.debug(f"Loading auditing plugins for upstream '{upstream_name}'")
            upstream_plugins = []
            
            for plugin_config in plugin_configs:
                if not plugin_config.get("enabled", True):
                    logger.debug(f"Skipping disabled auditing plugin: {plugin_config.get('policy', 'unknown')}")
                    continue
                    
                policy_name = plugin_config.get("policy")
                
                if not policy_name:
                    logger.error(f"Auditing plugin configuration missing 'policy' field for upstream '{upstream_name}'")
                    continue
                    
                if policy_name not in available_policies:
                    available_names = ", ".join(available_policies.keys())
                    raise ValueError(f"Policy '{policy_name}' not found. Available policies: {available_names}")
                    
                try:
                    plugin_class = available_policies[policy_name]
                    plugin_instance = self._create_plugin_instance(
                        plugin_class, plugin_config, policy_name, "auditing"
                    )
                    if plugin_instance:
                        upstream_plugins.append(plugin_instance)
                        logger.debug(f"Loaded auditing plugin '{policy_name}' for upstream '{upstream_name}'")
                except Exception as e:
                    logger.error(f"Failed to load auditing plugin '{policy_name}' for upstream '{upstream_name}': {e}")
                    self._load_failures.append({
                        "type": "auditing",
                        "policy": policy_name,
                        "upstream": upstream_name,
                        "error": str(e)
                    })
            
            # Sort plugins by priority (lower number = higher priority)
            upstream_plugins.sort(key=lambda p: getattr(p, 'priority', 50))
            self.upstream_auditing_plugins[upstream_name] = upstream_plugins
            
            logger.info(f"Loaded {len(upstream_plugins)} auditing plugins for upstream '{upstream_name}'")
    

    def _validate_plugin_interface(self, plugin_type: str, plugin_class: type, plugin_identifier: str):
        """Validate that plugin class implements the correct interface.
        
        Args:
            plugin_type: Type of plugin ('security' or 'auditing')
            plugin_class: Plugin class to validate
            plugin_identifier: Plugin path for error messages
        """
        if plugin_type == "security" and not issubclass(plugin_class, SecurityPlugin):
            raise TypeError(f"Security plugin '{plugin_identifier}' must inherit from SecurityPlugin")
        elif plugin_type == "auditing" and not issubclass(plugin_class, AuditingPlugin):
            raise TypeError(f"Auditing plugin '{plugin_identifier}' must inherit from AuditingPlugin")
    
    def _discover_policies(self, category: str) -> Dict[str, type]:
        """Discover all policies available in a plugin category.
        
        Args:
            category: Plugin category ('security' or 'auditing')
            
        Returns:
            Dict mapping policy names to plugin classes
        """
        policies = {}
        
        # Determine the plugin directory to scan
        base_dir = Path(__file__).parent
        plugin_dir = base_dir / category
        
        if not plugin_dir.exists():
            logger.debug(f"Plugin directory not found: {plugin_dir}")
            return policies
            
        # Scan all Python files in the category directory
        for py_file in plugin_dir.glob("**/*.py"):
            if not py_file.is_file() or py_file.name.startswith("__"):
                continue
                
            try:
                # Load the module
                module_name = py_file.stem
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec is None or spec.loader is None:
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check for POLICIES manifest
                if hasattr(module, 'POLICIES') and isinstance(module.POLICIES, dict):
                    for policy_name, policy_class in module.POLICIES.items():
                        if not isinstance(policy_name, str):
                            logger.warning(f"Invalid policy name type in {py_file}: {type(policy_name)}")
                            continue
                            
                        if not callable(policy_class):
                            logger.warning(f"Invalid policy class in {py_file}: {policy_class}")
                            continue
                            
                        # Check for duplicate policy names
                        if policy_name in policies:
                            logger.warning(f"Duplicate policy name '{policy_name}' found in {py_file}")
                            continue
                            
                        policies[policy_name] = policy_class
                        logger.debug(f"Discovered policy '{policy_name}' in {py_file}")
                        
            except Exception as e:
                logger.debug(f"Failed to load module {py_file}: {e}")
                continue
                
        logger.info(f"Discovered {len(policies)} policies in {category} category")
        return policies
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources.
        
        This method safely cleans up all loaded plugins. Plugin cleanup failures
        are logged but don't prevent other plugins from being cleaned up.
        """
        logger.info("Cleaning up plugin manager")
        
        # Cleanup upstream-scoped plugins
        for upstream_name, plugins in self.upstream_security_plugins.items():
            for plugin in plugins:
                try:
                    if hasattr(plugin, 'cleanup') and callable(getattr(plugin, 'cleanup')):
                        await plugin.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up security plugin {plugin.__class__.__name__} for upstream {upstream_name}: {e}")
        
        for upstream_name, plugins in self.upstream_auditing_plugins.items():
            for plugin in plugins:
                try:
                    if hasattr(plugin, 'cleanup') and callable(getattr(plugin, 'cleanup')):
                        await plugin.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up auditing plugin {plugin.__class__.__name__} for upstream {upstream_name}: {e}")
        
        logger.info("Plugin manager cleanup completed")
    
    def register_security_plugin(self, plugin: SecurityPlugin) -> None:
        """Register a security plugin with validation."""
        self._validate_plugin_priority(plugin)
        if "_global" not in self.upstream_security_plugins:
            self.upstream_security_plugins["_global"] = []
        self.upstream_security_plugins["_global"].append(plugin)
        # Sort immediately after adding to maintain priority order
        self.upstream_security_plugins["_global"].sort(key=lambda p: getattr(p, 'priority', 50))
        logger.info(f"Registered security plugin: {plugin.plugin_id} with priority {plugin.priority}")
    
    def register_auditing_plugin(self, plugin: AuditingPlugin) -> None:
        """Register an auditing plugin with validation."""
        self._validate_plugin_priority(plugin)
        if "_global" not in self.upstream_auditing_plugins:
            self.upstream_auditing_plugins["_global"] = []
        self.upstream_auditing_plugins["_global"].append(plugin)
        # Sort immediately after adding to maintain priority order
        self.upstream_auditing_plugins["_global"].sort(key=lambda p: getattr(p, 'priority', 50))
        logger.info(f"Registered auditing plugin: {plugin.plugin_id} with priority {plugin.priority}")

    def _validate_plugin_priority(self, plugin) -> None:
        """Validate plugin priority is in valid range.
        
        Args:
            plugin: The plugin to validate
            
        Raises:
            ValueError: If priority is not in 0-100 range
        """
        if not hasattr(plugin, 'priority') or not isinstance(plugin.priority, int):
            raise ValueError(f"Plugin {plugin.plugin_id} must have an integer priority attribute")
        
        if not 0 <= plugin.priority <= 100:
            raise ValueError(
                f"Plugin {plugin.plugin_id} priority {plugin.priority} must be between 0 and 100"
            )
    
    def _sort_plugins_by_priority(self, plugins: List) -> List:
        """Sort plugins by priority (0-100, lower numbers = higher priority).
        
        Args:
            plugins: List of plugins to sort
            
        Returns:
            List of plugins sorted by priority (ascending - lower numbers first)
        """
        return sorted(plugins, key=lambda p: getattr(p, 'priority', 50))
    
    async def audit_request(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> None:
        """Send request to auditing plugins in priority order."""
        await self.log_request(request, decision, server_name)
    
    
