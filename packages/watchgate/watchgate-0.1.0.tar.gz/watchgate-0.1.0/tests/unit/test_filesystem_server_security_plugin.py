"""Tests for the FilesystemServerSecurityPlugin security plugin.

This plugin is specifically designed for @modelcontextprotocol/server-filesystem
and its tool names/argument structures.
"""

import pytest
import copy
from watchgate.plugins.security.filesystem_server import FilesystemServerSecurityPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class TestFilesystemServerSecurityPluginConfiguration:
    """Test configuration validation for FilesystemServerSecurityPlugin."""
    
    def test_valid_config_with_read_permissions(self):
        """Test valid configuration with read permissions."""
        config = {
            "read": ["docs/*", "public/**/*.txt"]
        }
        plugin = FilesystemServerSecurityPlugin(config)
        assert "read" in plugin.permissions
        assert plugin.permissions["read"] == ["docs/*", "public/**/*.txt"]
    
    def test_valid_config_with_multiple_permission_types(self):
        """Test valid configuration with multiple permission types."""
        config = {
            "read": ["docs/*", "*.txt"],
            "write": ["uploads/*", "admin/**/*"]
        }
        plugin = FilesystemServerSecurityPlugin(config)
        assert plugin.permissions["read"] == ["docs/*", "*.txt"]
        assert plugin.permissions["write"] == ["uploads/*", "admin/**/*"]
    
    def test_invalid_config_not_dict(self):
        """Test configuration validation fails for non-dict."""
        with pytest.raises(ValueError, match="Configuration must be a dictionary"):
            FilesystemServerSecurityPlugin("not_a_dict")
    
    def test_empty_config(self):
        """Test empty configuration is valid."""
        config = {}
        plugin = FilesystemServerSecurityPlugin(config)
        assert plugin.permissions == {}


class TestFilesystemToolValidation:
    """Test filesystem tool validation."""
    
    @pytest.mark.asyncio
    async def test_read_file_tool_allowed(self):
        """Test read_file tool is properly identified as filesystem tool."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "test.txt"}
            },
            id="test-1"
        )
        
        # This should pass through our minimal implementation for now
        result = await plugin.check_request(request, "test-server")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_non_filesystem_tool_ignored(self):
        """Test non-filesystem tools are ignored."""
        config = {"read": ["restricted/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "some_other_tool",
                "arguments": {"data": "test"}
            },
            id="test-2"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result is not None


class TestPathPermissionChecking:
    """Test path-based permission checking for filesystem tools."""
    
    @pytest.mark.asyncio
    async def test_read_permission_allowed_path(self):
        """Test read permission allows access to matching paths."""
        config = {"read": ["docs/*", "public/**/*.txt"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "docs/readme.md"}
            },
            id="test-3"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
        assert "Filesystem access permitted" in result.reason
    
    @pytest.mark.asyncio
    async def test_read_permission_denied_path(self):
        """Test read permission denies access to non-matching paths."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "secret/config.txt"}
            },
            id="test-4"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert "access denied" in result.reason.lower()
    
    @pytest.mark.asyncio
    async def test_non_tools_call_request_allowed(self):
        """Test non-tools/call requests are allowed through."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="resources/list",
            params={},
            id="test-5"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
        assert "Non-filesystem request" in result.reason


class TestWritePermissions:
    """Test write permission validation for filesystem tools."""
    
    @pytest.mark.asyncio
    async def test_write_file_permission_allowed(self):
        """Test write_file tool with allowed path."""
        config = {"write": ["uploads/*", "temp/*.tmp"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "write_file",
                "arguments": {
                    "path": "uploads/data.txt",
                    "content": "test content"
                }
            },
            id="test-6"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
        assert "Filesystem access permitted" in result.reason
    
    @pytest.mark.asyncio
    async def test_write_file_permission_denied(self):
        """Test write_file tool with denied path."""
        config = {"write": ["uploads/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "write_file",
                "arguments": {
                    "path": "restricted/secret.txt",
                    "content": "secret data"
                }
            },
            id="test-7"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert "access denied" in result.reason.lower()
        assert "restricted/secret.txt" in result.reason
    
    @pytest.mark.asyncio
    async def test_create_directory_permission(self):
        """Test create_directory tool (requires write permission)."""
        config = {"write": ["new/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "create_directory",
                "arguments": {"path": "new/folder"}
            },
            id="test-8"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True


class TestMoveFilePermissions:
    """Test move file permission validation for filesystem tools."""
    
    @pytest.mark.asyncio
    async def test_move_file_permission_allowed(self):
        """Test move_file tool with allowed paths."""
        config = {"write": ["uploads/*", "archive/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "move_file",
                "arguments": {
                    "source": "uploads/old.txt",
                    "destination": "archive/old.txt"
                }
            },
            id="test-9"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
        assert "Filesystem access permitted" in result.reason
    
    @pytest.mark.asyncio
    async def test_move_file_source_denied(self):
        """Test move_file tool with denied source path."""
        config = {"write": ["uploads/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "move_file",
                "arguments": {
                    "source": "restricted/file.txt",
                    "destination": "uploads/file.txt"
                }
            },
            id="test-10"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert "restricted/file.txt" in result.reason


class TestMultipleFileTools:
    """Test tools that handle multiple files."""
    
    @pytest.mark.asyncio
    async def test_read_multiple_files_all_allowed(self):
        """Test read_multiple_files with all paths allowed."""
        config = {"read": ["docs/*", "*.txt"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_multiple_files",
                "arguments": {
                    "paths": ["docs/readme.md", "config.txt"]
                }
            },
            id="test-11"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
    
    @pytest.mark.asyncio
    async def test_read_multiple_files_one_denied(self):
        """Test read_multiple_files with one path denied."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_multiple_files",
                "arguments": {
                    "paths": ["docs/readme.md", "secret/config.txt"]
                }
            },
            id="test-12"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert "secret/config.txt" in result.reason


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_missing_tool_name(self):
        """Test request without tool name."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={},
            id="test-13"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert "Missing tool name" in result.reason
    
    @pytest.mark.asyncio
    async def test_list_allowed_directories_no_read_permission(self):
        """Test list_allowed_directories when no read permission configured."""
        config = {"write": ["uploads/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "list_allowed_directories",
                "arguments": {}
            },
            id="test-14"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert "No read permissions configured" in result.reason
    
    @pytest.mark.asyncio
    async def test_list_allowed_directories_with_read_permission(self):
        """Test list_allowed_directories when read permission configured."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "list_allowed_directories",
                "arguments": {}
            },
            id="test-15"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
        assert "List allowed directories permitted" in result.reason


class TestPatternMatching:
    """Test advanced pattern matching features."""
    
    @pytest.mark.asyncio
    async def test_negative_pattern_exclusion(self):
        """Test negative patterns (exclusions) work correctly."""
        config = {"read": ["docs/*", "!docs/secret*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Should allow normal docs files
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "docs/readme.md"}
            },
            id="test-16"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
        
        # Should deny secret files even though they match docs/*
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "docs/secret.txt"}
            },
            id="test-17"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
    
    @pytest.mark.asyncio
    async def test_recursive_pattern_matching(self):
        """Test recursive pattern matching with **."""
        config = {"read": ["public/**/*.md"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "public/docs/deep/nested/file.md"}
            },
            id="test-18"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is True
    
    @pytest.mark.asyncio
    async def test_no_permission_configured_default_deny(self):
        """Test that missing permission type defaults to deny."""
        config = {"write": ["uploads/*"]}  # Only write configured, no read
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "anything.txt"}
            },
            id="test-19"
        )
        
        result = await plugin.check_request(request, "test-server")
        assert result.allowed is False
        assert "access denied" in result.reason.lower()



class TestResponseFiltering:
    """Test response filtering functionality."""
    
    @pytest.mark.asyncio
    async def test_filters_directory_listing_with_restricted_paths(self):
        """Test that directory listings filter out restricted paths."""
        config = {"read": ["public/*", "docs/*.md"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "list_directory", "arguments": {"path": "."}},
            id="test-list"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-list",
            result={
                "entries": [
                    {"path": "public/file1.txt", "type": "file"},
                    {"path": "private/secret.txt", "type": "file"},
                    {"path": "docs/readme.md", "type": "file"},
                    {"path": "docs/secret.doc", "type": "file"},
                ]
            }
        )
        
        decision = await plugin.check_response(request, response, "test-server")
        assert decision.allowed is True
        assert decision.modified_content is not None
        assert "Filtered directory listing" in decision.reason
        
        # Check filtered results
        filtered_entries = decision.modified_content.result["entries"]
        assert len(filtered_entries) == 2
        assert all(entry["path"] in ["public/file1.txt", "docs/readme.md"] for entry in filtered_entries)
    
    @pytest.mark.asyncio
    async def test_filters_search_results_with_restricted_paths(self):
        """Test that search results filter out matches in restricted paths."""
        config = {"read": ["src/**/*.py"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "search_files", "arguments": {"pattern": "TODO"}},
            id="test-search"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-search",
            result={
                "matches": [
                    {"path": "src/main.py", "line": 10, "content": "# TODO: fix this"},
                    {"path": "tests/test.py", "line": 5, "content": "# TODO: add test"},
                    {"path": "src/utils/helper.py", "line": 20, "content": "# TODO: refactor"},
                ]
            }
        )
        
        decision = await plugin.check_response(request, response, "test-server")
        assert decision.allowed is True
        assert decision.modified_content is not None
        assert "Filtered search results" in decision.reason
        
        # Check filtered results
        filtered_matches = decision.modified_content.result["matches"]
        assert len(filtered_matches) == 2
        assert all(match["path"].startswith("src/") for match in filtered_matches)
    
    @pytest.mark.asyncio
    async def test_blocks_error_with_restricted_path_info(self):
        """Test that error messages containing restricted paths are blocked."""
        config = {"read": ["allowed/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "read_file", "arguments": {"path": "secret/file.txt"}},
            id="test-error"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-error",
            error={"code": -32602, "message": "Cannot read file at /home/user/secret/file.txt"}
        )
        
        decision = await plugin.check_response(request, response, "test-server")
        assert decision.allowed is False
        assert "restricted path information" in decision.reason
    
    @pytest.mark.asyncio
    async def test_allows_response_without_path_info(self):
        """Test that responses without path information are allowed."""
        config = {"read": ["data/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "read_file", "arguments": {"path": "data/file.txt"}},
            id="test-ok"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-ok",
            result={"content": "File contents here"}
        )
        
        decision = await plugin.check_response(request, response, "test-server")
        assert decision.allowed is True
        assert decision.modified_content is None


class TestNotificationFiltering:
    """Test notification filtering functionality."""
    
    @pytest.mark.asyncio
    async def test_blocks_notification_with_restricted_path(self):
        """Test that notifications containing restricted paths are blocked."""
        config = {"read": ["public/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="file_changed",
            params={"path": "/etc/passwd", "event": "modified"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is False
        assert "restricted path information" in decision.reason
    
    @pytest.mark.asyncio
    async def test_allows_notification_with_allowed_path(self):
        """Test that notifications with allowed paths are permitted."""
        config = {"read": ["logs/**/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="file_changed",
            params={"path": "logs/app/error.log", "event": "created"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is True


class TestMetadataValidation:
    """Test that FilesystemServerSecurityPlugin adds metadata to all PolicyDecision objects."""
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_non_filesystem_request(self):
        """Test metadata is present for non-filesystem requests."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="resources/list",
            params={},
            id="test-meta-1"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["request_method"] == "resources/list"
        assert result.metadata["check_type"] == "request"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_missing_tool_name(self):
        """Test metadata is present when tool name is missing."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={},
            id="test-meta-2"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["request_method"] == "tools/call"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["error"] == "missing_tool_name"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_non_filesystem_tool(self):
        """Test metadata is present for non-filesystem tools."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "some_other_tool"},
            id="test-meta-3"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "some_other_tool"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["is_filesystem_tool"] is False
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_list_allowed_directories_permitted(self):
        """Test metadata for list_allowed_directories when permitted."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "list_allowed_directories"},
            id="test-meta-4"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "list_allowed_directories"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["special_case"] == "list_allowed_directories"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_list_allowed_directories_denied(self):
        """Test metadata for list_allowed_directories when denied."""
        config = {"write": ["uploads/*"]}  # No read permission
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "list_allowed_directories"},
            id="test-meta-5"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "list_allowed_directories"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["special_case"] == "list_allowed_directories"
        assert result.metadata["error"] == "no_read_permissions_configured"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_filesystem_access_permitted(self):
        """Test metadata for permitted filesystem access."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "docs/readme.md"}
            },
            id="test-meta-6"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "read_file"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["paths_checked"] == ["docs/readme.md"]
        assert result.metadata["is_filesystem_tool"] is True
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_filesystem_access_denied(self):
        """Test metadata for denied filesystem access."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "secret/config.txt"}
            },
            id="test-meta-7"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "read_file"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["paths_checked"] == ["secret/config.txt"]
        assert result.metadata["denied_path"] == "secret/config.txt"
        assert result.metadata["is_filesystem_tool"] is True
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_default_permitted(self):
        """Test metadata for default response permission."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "read_file"},
            id="test-meta-8"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-8",
            result={"content": "file contents"}
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "response"
        assert result.metadata["tool_name"] == "read_file"
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_error_sanitized(self):
        """Test metadata when error message is sanitized."""
        config = {"read": ["allowed/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "read_file"},
            id="test-meta-9"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-9",
            error={"code": -32602, "message": "Cannot read file at /restricted/secret.txt"}
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "response"
        # The path extraction includes the entire error message and the actual path
        # The restricted_path field contains the first path that fails permission checks
        # This could be either the error message or the actual path
        assert result.metadata["restricted_path"] in [
            "Cannot read file at /restricted/secret.txt",
            "/restricted/secret.txt"
        ]
        assert result.metadata["error_sanitized"] is True
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_directory_listing_filtered(self):
        """Test metadata when directory listing is filtered."""
        config = {"read": ["public/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "list_directory"},
            id="test-meta-10"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-10",
            result={
                "entries": [
                    {"path": "public/file1.txt"},
                    {"path": "private/secret.txt"},
                    {"path": "public/file2.txt"}
                ]
            }
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "list_directory"
        assert result.metadata["check_type"] == "response"
        assert result.metadata["original_count"] == 3
        assert result.metadata["filtered_count"] == 2
        assert result.metadata["entries_removed"] == 1
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_search_results_filtered(self):
        """Test metadata when search results are filtered."""
        config = {"read": ["src/**/*.py"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "search_files"},
            id="test-meta-11"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-11",
            result={
                "matches": [
                    {"path": "src/main.py"},
                    {"path": "tests/test.py"},
                    {"path": "src/utils.py"}
                ]
            }
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "search_files"
        assert result.metadata["check_type"] == "response"
        assert result.metadata["original_count"] == 3
        assert result.metadata["filtered_count"] == 2
        assert result.metadata["matches_removed"] == 1
    
    @pytest.mark.asyncio
    async def test_check_notification_metadata_permitted(self):
        """Test metadata for permitted notifications."""
        config = {"read": ["logs/**/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="file_changed",
            params={"path": "logs/app/error.log", "event": "created"}
        )
        
        result = await plugin.check_notification(notification, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "notification"
        assert result.metadata["notification_method"] == "file_changed"
        assert result.metadata["paths_checked"] == ["logs/app/error.log"]
    
    @pytest.mark.asyncio
    async def test_check_notification_metadata_denied(self):
        """Test metadata for denied notifications."""
        config = {"read": ["public/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="file_changed",
            params={"path": "/etc/passwd", "event": "modified"}
        )
        
        result = await plugin.check_notification(notification, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "notification"
        assert result.metadata["notification_method"] == "file_changed"
        assert result.metadata["restricted_path"] == "/etc/passwd"
        assert result.metadata["paths_checked"] == ["/etc/passwd"]
    
    @pytest.mark.asyncio
    async def test_blocks_notification_with_path_in_method(self):
        """Test detection of paths in notification method names."""
        config = {"read": ["safe/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="error:/secret/data/file.db",
            params={"error": "Database locked"}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is False
        assert "/secret/data/file.db" in decision.reason
    
    @pytest.mark.asyncio
    async def test_allows_notification_without_paths(self):
        """Test that notifications without path information are allowed."""
        config = {"read": ["data/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="status_update",
            params={"status": "ready", "workers": 4}
        )
        
        decision = await plugin.check_notification(notification, "test-server")
        assert decision.allowed is True


class TestMetadataValidation:
    """Test that FilesystemServerSecurityPlugin adds metadata to all PolicyDecision objects."""
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_non_filesystem_request(self):
        """Test metadata is present for non-filesystem requests."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="resources/list",
            params={},
            id="test-meta-1"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["request_method"] == "resources/list"
        assert result.metadata["check_type"] == "request"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_missing_tool_name(self):
        """Test metadata is present when tool name is missing."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={},
            id="test-meta-2"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["request_method"] == "tools/call"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["error"] == "missing_tool_name"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_non_filesystem_tool(self):
        """Test metadata is present for non-filesystem tools."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "some_other_tool"},
            id="test-meta-3"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "some_other_tool"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["is_filesystem_tool"] is False
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_list_allowed_directories_permitted(self):
        """Test metadata for list_allowed_directories when permitted."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "list_allowed_directories"},
            id="test-meta-4"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "list_allowed_directories"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["special_case"] == "list_allowed_directories"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_list_allowed_directories_denied(self):
        """Test metadata for list_allowed_directories when denied."""
        config = {"write": ["uploads/*"]}  # No read permission
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "list_allowed_directories"},
            id="test-meta-5"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "list_allowed_directories"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["special_case"] == "list_allowed_directories"
        assert result.metadata["error"] == "no_read_permissions_configured"
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_filesystem_access_permitted(self):
        """Test metadata for permitted filesystem access."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "docs/readme.md"}
            },
            id="test-meta-6"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "read_file"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["paths_checked"] == ["docs/readme.md"]
        assert result.metadata["is_filesystem_tool"] is True
    
    @pytest.mark.asyncio
    async def test_check_request_metadata_filesystem_access_denied(self):
        """Test metadata for denied filesystem access."""
        config = {"read": ["docs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "read_file",
                "arguments": {"path": "secret/config.txt"}
            },
            id="test-meta-7"
        )
        
        result = await plugin.check_request(request, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "read_file"
        assert result.metadata["required_permission"] == "read"
        assert result.metadata["check_type"] == "request"
        assert result.metadata["paths_checked"] == ["secret/config.txt"]
        assert result.metadata["denied_path"] == "secret/config.txt"
        assert result.metadata["is_filesystem_tool"] is True
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_default_permitted(self):
        """Test metadata for default response permission."""
        config = {"read": ["*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "read_file"},
            id="test-meta-8"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-8",
            result={"content": "file contents"}
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "response"
        assert result.metadata["tool_name"] == "read_file"
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_error_sanitized(self):
        """Test metadata when error message is sanitized."""
        config = {"read": ["allowed/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "read_file"},
            id="test-meta-9"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-9",
            error={"code": -32602, "message": "Cannot read file at /restricted/secret.txt"}
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "response"
        # The path extraction includes the entire error message and the actual path
        # The restricted_path field contains the first path that fails permission checks
        # This could be either the error message or the actual path
        assert result.metadata["restricted_path"] in [
            "Cannot read file at /restricted/secret.txt",
            "/restricted/secret.txt"
        ]
        assert result.metadata["error_sanitized"] is True
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_directory_listing_filtered(self):
        """Test metadata when directory listing is filtered."""
        config = {"read": ["public/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "list_directory"},
            id="test-meta-10"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-10",
            result={
                "entries": [
                    {"path": "public/file1.txt"},
                    {"path": "private/secret.txt"},
                    {"path": "public/file2.txt"}
                ]
            }
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "list_directory"
        assert result.metadata["check_type"] == "response"
        assert result.metadata["original_count"] == 3
        assert result.metadata["filtered_count"] == 2
        assert result.metadata["entries_removed"] == 1
    
    @pytest.mark.asyncio
    async def test_check_response_metadata_search_results_filtered(self):
        """Test metadata when search results are filtered."""
        config = {"read": ["src/**/*.py"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/call",
            params={"name": "search_files"},
            id="test-meta-11"
        )
        
        response = MCPResponse(
            jsonrpc="2.0",
            id="test-meta-11",
            result={
                "matches": [
                    {"path": "src/main.py"},
                    {"path": "tests/test.py"},
                    {"path": "src/utils.py"}
                ]
            }
        )
        
        result = await plugin.check_response(request, response, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["tool_name"] == "search_files"
        assert result.metadata["check_type"] == "response"
        assert result.metadata["original_count"] == 3
        assert result.metadata["filtered_count"] == 2
        assert result.metadata["matches_removed"] == 1
    
    @pytest.mark.asyncio
    async def test_check_notification_metadata_permitted(self):
        """Test metadata for permitted notifications."""
        config = {"read": ["logs/**/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="file_changed",
            params={"path": "logs/app/error.log", "event": "created"}
        )
        
        result = await plugin.check_notification(notification, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "notification"
        assert result.metadata["notification_method"] == "file_changed"
        assert result.metadata["paths_checked"] == ["logs/app/error.log"]
    
    @pytest.mark.asyncio
    async def test_check_notification_metadata_denied(self):
        """Test metadata for denied notifications."""
        config = {"read": ["public/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        notification = MCPNotification(
            jsonrpc="2.0",
            method="file_changed",
            params={"path": "/etc/passwd", "event": "modified"}
        )
        
        result = await plugin.check_notification(notification, server_name="test-server")
        assert result.metadata is not None
        assert result.metadata["plugin"] == "filesystem_server"
        assert result.metadata["server_name"] == "test-server"
        assert result.metadata["check_type"] == "notification"
        assert result.metadata["notification_method"] == "file_changed"
        assert result.metadata["restricted_path"] == "/etc/passwd"
        assert result.metadata["paths_checked"] == ["/etc/passwd"]
