import sys
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from anges.utils.mcp_manager import McpStdioClient, McpManager


class TestMcpStdioClient:
    """Test cases for McpStdioClient functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.client = McpStdioClient(
            name="dummy_mcp_server",
            command=sys.executable,
            args=["tests/unit/utils/dummy_mcp_server.py"]
        )

    def test_client_initialization(self):
        """Test MCP client initialization"""
        assert self.client.name == "dummy_mcp_server"
        assert self.client.command == sys.executable
        assert self.client.args == ["tests/unit/utils/dummy_mcp_server.py"]

    def test_to_dict(self):
        """Test client information serialization"""
        client_dict = self.client.to_dict()
        expected_keys = {"name", "command", "args"}
        assert set(client_dict.keys()) == expected_keys
        assert client_dict["name"] == "dummy_mcp_server"
        assert client_dict["command"] == sys.executable
        assert client_dict["args"] == ["tests/unit/utils/dummy_mcp_server.py"]

    @pytest.mark.asyncio
    @patch('anges.utils.mcp_manager.stdio_client')
    @patch('anges.utils.mcp_manager.ClientSession')
    async def test_list_tools_success(self, mock_session_class, mock_stdio_client):
        """Test successful tool listing"""
        # Mock stdio client
        mock_stdio = MagicMock()
        mock_writer = MagicMock()
        mock_stdio_client.return_value.__aenter__.return_value = (mock_stdio, mock_writer)
        
        # Mock client session
        mock_session = MagicMock()
        mock_session.initialize = AsyncMock()
        mock_tools_response = MagicMock()
        mock_tools_response.tools = [
            MagicMock(name="echo"),
            MagicMock(name="add_numbers")
        ]
        mock_session.list_tools = AsyncMock(return_value=mock_tools_response)
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        tools = await self.client.list_tools()
        
        assert len(tools) == 2
        mock_session.initialize.assert_called_once()
        mock_session.list_tools.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tools_failure(self):
        """Test failed tool listing"""
        with patch('anges.utils.mcp_manager.stdio_client', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                await self.client.list_tools()

    @pytest.mark.asyncio
    @patch('anges.utils.mcp_manager.stdio_client')
    @patch('anges.utils.mcp_manager.ClientSession')
    async def test_call_tool_success(self, mock_session_class, mock_stdio_client):
        """Test successful tool call"""
        # Mock stdio client
        mock_stdio = MagicMock()
        mock_writer = MagicMock()
        mock_stdio_client.return_value.__aenter__.return_value = (mock_stdio, mock_writer)
        
        # Mock client session
        mock_session = MagicMock()
        mock_session.initialize = AsyncMock()
        mock_response = MagicMock()
        mock_response.isError = False
        # Mock the structuredContent path since that's checked first
        mock_response.structuredContent.get.return_value = "Echo: test"
        mock_session.call_tool = AsyncMock(return_value=mock_response)
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        result = await self.client.call_tool("echo", {"text": "test"})
        
        assert result == "Echo: test"
        mock_session.call_tool.assert_called_once_with("echo", {"text": "test"})

    @pytest.mark.asyncio
    async def test_call_tool_failure(self):
        """Test failed tool call"""
        with patch('anges.utils.mcp_manager.stdio_client', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                await self.client.call_tool("echo", {"text": "test"})


class TestMcpManager:
    """Test cases for McpManager functionality"""

    def setup_method(self):
        """Set up test environment"""
        # Create test configuration dictionary
        self.test_config = {}

    def test_manager_initialization_empty_config(self):
        """Test MCP manager initialization with empty config"""
        manager = McpManager({})
        assert manager.mcp_config == {}
        assert len(manager.mcp_clients) == 0

    def test_manager_initialization_with_config(self):
        """Test MCP manager initialization with configuration"""
        config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            }
        }
        
        manager = McpManager(config)
        
        assert len(manager.mcp_clients) == 1
        assert "dummy_mcp_server" in manager.mcp_clients
        
        client = manager.mcp_clients["dummy_mcp_server"]
        assert client.name == "dummy_mcp_server"
        assert client.command == sys.executable

    def test_load_mcp_clients_with_config(self):
        """Test loading MCP clients from config"""
        config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            },
            "filesystem_server": {
                "command": "npx",
                "args": ["-g", "@modelcontextprotocol/server-filesystem", "/tmp"]
            }
        }
        
        manager = McpManager(config)
        
        assert len(manager.mcp_clients) == 2
        assert "dummy_mcp_server" in manager.mcp_clients
        assert "filesystem_server" in manager.mcp_clients
        
        # Check client properties
        dummy_client = manager.mcp_clients["dummy_mcp_server"]
        assert dummy_client.name == "dummy_mcp_server"
        assert dummy_client.command == sys.executable

    def test_load_mcp_clients_invalid_config(self):
        """Test loading MCP clients with invalid configuration"""
        config = {
            "invalid_server": {
                "command": "python"
                # Missing 'args' field
            }
        }
        
        # Should not raise exception, but log warning
        manager = McpManager(config)
        assert len(manager.mcp_clients) == 0

    def test_add_mcp_client(self):
        """Test adding new MCP client"""
        manager = McpManager({})
        
        manager.add_mcp_client("new_server", sys.executable, ["tests/unit/utils/dummy_mcp_server.py"])
        
        assert "new_server" in manager.mcp_clients
        client = manager.mcp_clients["new_server"]
        assert client.name == "new_server"
        assert client.command == sys.executable

    def test_remove_mcp_client(self):
        """Test removing MCP client"""
        config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            }
        }
        manager = McpManager(config)
        
        result = manager.remove_mcp_client("dummy_mcp_server")
        
        assert result
        assert "dummy_mcp_server" not in manager.mcp_clients

    def test_remove_nonexistent_client(self):
        """Test removing nonexistent MCP client"""
        manager = McpManager({})
        
        result = manager.remove_mcp_client("nonexistent")
        
        assert not result

    def test_update_mcp_client(self):
        """Test updating existing MCP client"""
        config = {
            "dummy_mcp_server": {
                "command": "old_command",
                "args": ["old_args"]
            }
        }
        manager = McpManager(config)
        
        result = manager.update_mcp_client("dummy_mcp_server", sys.executable, ["new_args"])
        
        assert result
        client = manager.mcp_clients["dummy_mcp_server"]
        assert client.command == sys.executable
        assert client.args == ["new_args"]

    def test_update_nonexistent_client(self):
        """Test updating nonexistent MCP client"""
        manager = McpManager({})
        
        result = manager.update_mcp_client("nonexistent", "command", ["args"])
        
        assert not result

    def test_get_mcp_client(self):
        """Test getting MCP client by name"""
        config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            }
        }
        manager = McpManager(config)
        
        client = manager.get_mcp_client("dummy_mcp_server")
        assert client is not None
        assert client.name == "dummy_mcp_server"
        
        # Test nonexistent client
        nonexistent_client = manager.get_mcp_client("nonexistent")
        assert nonexistent_client is None

    @patch.object(McpManager, 'list_client_tools')
    def test_list_mcp_clients(self, mock_list_tools):
        """Test listing MCP clients with status"""
        config = {
            "connected_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            },
            "disconnected_server": {
                "command": "invalid_command",
                "args": ["invalid_args"]
            }
        }
        manager = McpManager(config)
        
        # Mock list_client_tools behavior
        def mock_tools_side_effect(name):
            if name == "connected_server":
                return [MagicMock(name="echo")]
            else:
                raise Exception("Connection failed")
        
        mock_list_tools.side_effect = mock_tools_side_effect
        
        clients = manager.list_mcp_clients()
        
        assert len(clients) == 2
        
        # Find clients in results
        connected_info = next(c for c in clients if c["name"] == "connected_server")
        disconnected_info = next(c for c in clients if c["name"] == "disconnected_server")
        
        # Check connected client
        assert connected_info["status"]
        assert len(connected_info["tools"]) == 1
        
        # Check disconnected client
        assert not disconnected_info["status"]
        assert len(disconnected_info["tools"]) == 0

    @patch('asyncio.run')
    def test_call_mcp_tool(self, mock_asyncio_run):
        """Test calling MCP tool"""
        config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            }
        }
        manager = McpManager(config)
        
        mock_asyncio_run.return_value = "Echo: test"
        
        result = manager.call_mcp_tool("dummy_mcp_server", "echo", {"text": "test"})
        
        assert result == "Echo: test"
        mock_asyncio_run.assert_called_once()

    def test_call_mcp_tool_nonexistent_client(self):
        """Test calling tool on nonexistent MCP client"""
        manager = McpManager({})
        
        with pytest.raises(ValueError) as context:
            manager.call_mcp_tool("nonexistent", "echo", {"text": "test"})
        
        assert "MCP client 'nonexistent' not found" in str(context.value)

    @patch('asyncio.run')
    def test_list_client_tools(self, mock_asyncio_run):
        """Test listing tools for a specific client"""
        config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            }
        }
        manager = McpManager(config)
        
        mock_tools = [MagicMock(name="echo"), MagicMock(name="add_numbers")]
        mock_asyncio_run.return_value = mock_tools
        
        tools = manager.list_client_tools("dummy_mcp_server")
        
        assert len(tools) == 2
        mock_asyncio_run.assert_called_once()

    def test_list_client_tools_nonexistent_client(self):
        """Test listing tools for nonexistent client"""
        manager = McpManager({})
        
        with pytest.raises(ValueError) as context:
            manager.list_client_tools("nonexistent")
        
        assert "MCP client 'nonexistent' not found" in str(context.value)


if __name__ == '__main__':
    pytest.main([__file__])