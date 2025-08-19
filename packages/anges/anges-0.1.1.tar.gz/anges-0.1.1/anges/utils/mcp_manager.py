"""
MCP (Model Context Protocol) Client Manager

Provides two main components:

1. McpStdioClient: Single MCP server stdio connection client
   - Establishes stdio communication with MCP servers
   - Provides tool listing and tool execution capabilities
   - Handles connection lifecycle and error management

2. McpManager: Multi-MCP client manager
   - Unified management of multiple MCP client connections
   - Supports persistent storage and loading of client configurations
   - Provides CRUD operations for clients
   - Batch tool discovery and management

Key Features:
- Connection lifecycle management
- Async operation support
- Configuration persistence
- Tool discovery and execution
- Error handling and logging

"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Any

from mcp import StdioServerParameters, stdio_client, ClientSession, Tool
from mcp.shared.exceptions import McpError
from mcp.types import CallToolResult

from anges.utils.shared_base import get_data_dir


class McpStdioClient:
    """
    MCP Stdio Client for connecting to MCP servers via stdio communication.

    This client provides a high-level interface for listing available tools
    and executing tool calls with proper error handling. Each operation
    establishes a temporary connection to the MCP server.
    """

    def __init__(self, name: str, command: str, args: List[str]):
        """
        Initialize the MCP Stdio Client.

        Args:
            name (str): The name of the MCP server
            command (str): The command to execute (e.g., path to python executable)
            args (List[str]): Command line arguments
        """
        self.name = name
        self.command = command
        self.args = args

    async def list_tools(self) -> List[Tool]:
        """
        List available tools from the MCP server.

        Returns:
            List[Tool]: List of available tools

        Raises:
            Exception: If connection or tool listing fails
        """
        try:
            server_params = StdioServerParameters(command=self.command, args=self.args)
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    return response.tools
        except Exception as e:
            logging.error(f"Failed to list tools for mcp server '{self.name}': {e}")
            raise

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> CallToolResult:
        """
        Call a specific tool on the MCP server.

        Args:
            tool_name (str): Name of the tool to call
            tool_args (Dict[str, Any]): Arguments to pass to the tool

        Returns:
            CallToolResult: Result of the tool call

        Raises:
            RuntimeError: If the tool call returns an error
            Exception: If connection or tool execution fails
        """
        try:
            server_params = StdioServerParameters(command=self.command, args=self.args)
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    response = await session.call_tool(tool_name, tool_args)
                    if response.isError:
                        contents = [content.text for content in (response.content or [])]
                        raise McpError("\n".join(contents))
                    elif hasattr(response, "structuredContent"):
                        return response.structuredContent.get("result")
                    else:
                        return response.content[0].text
        except Exception as e:
            logging.error(f"Failed to call tool '{tool_name}' on '{self.name}': {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert client configuration to dictionary.

        Returns:
            Dict[str, Any]: Client configuration dictionary
        """
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args
        }


class McpManager:
    """
    Manages multiple MCP client connections.

    Responsible for initialization, persistence, and operations of MCP clients.
    Provides a unified interface for managing multiple MCP server connections.
    """

    def __init__(self, mcp_config: Dict[str, Any]):
        """
        Initialize MCP Manager.

        Args:
            mcp_config: Dictionary containing MCP configuration.
        """
        self.mcp_config = mcp_config
        self.mcp_clients: Dict[str, McpStdioClient] = {}
        self.load_mcp_clients()

    def load_mcp_clients(self) -> None:
        """
        Load MCP clients from configuration dictionary.

        Creates empty clients if configuration doesn't exist.
        Logs warnings for any loading errors but continues operation.
        """
        self.mcp_clients = {}
        try:
            for mcp_name, mcp_params in self.mcp_config.items():
                mcp_client = McpStdioClient(
                    name=mcp_name,
                    command=mcp_params["command"],
                    args=mcp_params["args"]
                )
                self.mcp_clients[mcp_name] = mcp_client

        except Exception as e:
            # Log error but don't fail completely
            logging.warning(f"Failed to load MCP clients from configuration: {e}")



    def get_mcp_client(self, mcp_name: str) -> McpStdioClient:
        """
        Get MCP client by name.

        Args:
            mcp_name (str): Name of the MCP client

        Returns:
            McpStdioClient: The requested MCP client, or None if not found
        """
        return self.mcp_clients.get(mcp_name)

    def call_mcp_tool(self, mcp_name: str, tool_name: str, tool_args: Dict[str, Any]) -> CallToolResult:
        """
        Call a tool on a specific MCP client.

        Args:
            mcp_name (str): Name of the MCP client
            tool_name (str): Name of the tool to call
            tool_args (Dict[str, Any]): Arguments to pass to the tool

        Returns:
            CallToolResult: Result of the tool call

        Raises:
            ValueError: If the specified MCP client is not found
        """
        if mcp_name in self.mcp_clients:
            return asyncio.run(self.mcp_clients[mcp_name].call_tool(tool_name, tool_args))
        else:
            raise ValueError(f"MCP client '{mcp_name}' not found")

    def remove_mcp_client(self, mcp_name: str) -> bool:
        """
        Remove an MCP client.

        Args:
            mcp_name (str): Name of the MCP client to remove

        Returns:
            bool: True if client was removed, False if client was not found
        """
        if mcp_name in self.mcp_clients:
            del self.mcp_clients[mcp_name]
            return True
        return False

    def add_mcp_client(self, mcp_name: str, command: str, args: List[str]) -> None:
        """
        Add a new MCP client.

        Args:
            mcp_name (str): Name of the MCP client
            command (str): Command to execute
            args (List[str]): Command line arguments
        """
        mcp_client = McpStdioClient(
            name=mcp_name,
            command=command,
            args=args
        )
        self.mcp_clients[mcp_name] = mcp_client

    def update_mcp_client(self, mcp_name: str, command: str, args: List[str]) -> bool:
        """
        Update an existing MCP client configuration.

        Args:
            mcp_name (str): Name of the MCP client to update
            command (str): New command to execute
            args (List[str]): New command line arguments

        Returns:
            bool: True if client was updated, False if client was not found
        """
        if mcp_name in self.mcp_clients:
            # Update the client configuration
            self.mcp_clients[mcp_name].command = command
            self.mcp_clients[mcp_name].args = args
            return True
        return False

    def list_client_tools(self, mcp_name: str) -> List[Tool]:
        """
        List tools available on a specific MCP client.

        Args:
            mcp_name (str): Name of the MCP client

        Returns:
            List[Tool]: List of available tools

        Raises:
            ValueError: If the specified MCP client is not found
        """
        client = self.get_mcp_client(mcp_name)
        if client:
            return asyncio.run(client.list_tools())
        else:
            raise ValueError(f"MCP client '{mcp_name}' not found")

    def list_mcp_clients(self) -> List[dict]:
        """
        List all available MCP client info.

        Returns:
            List[dict]: List of MCP client info
        """
        result = []
        for mcp_name, mcp_client in self.mcp_clients.items():
            info = mcp_client.to_dict()
            try:
                tools = self.list_client_tools(mcp_name)
                info["tools"] = tools
                info["status"] = True
            except Exception as e:
                info["tools"] = []
                info["status"] = False
            result.append(info)
        return result


