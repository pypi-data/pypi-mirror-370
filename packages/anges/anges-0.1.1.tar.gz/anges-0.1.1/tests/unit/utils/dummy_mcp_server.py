"""
Simple MCP Server using mcp.server.fastmcp.FastMCP

This is a minimal MCP server that provides an echo tool for testing purposes.
"""

import logging
import sys
import asyncio
from mcp.server.fastmcp import FastMCP

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("dummy-mcp-server")

@mcp.tool()
def echo(text: str) -> str:
    """
    Echo tool that returns the input text.
    
    Args:
        text: The text to echo back
        
    Returns:
        The echoed text
    """
    logger.info(f"Echo tool called with text: {text}")
    return f"Echo: {text}"

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of the two numbers
    """
    logger.info(f"Add numbers tool called with a={a}, b={b}")
    result = a + b
    logger.info(f"Add numbers result: {result}")
    return result

if __name__ == "__main__":
    try:
        logger.info("Starting dummy MCP server...")
        # Run the server with stdio transport
        mcp.run("stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)