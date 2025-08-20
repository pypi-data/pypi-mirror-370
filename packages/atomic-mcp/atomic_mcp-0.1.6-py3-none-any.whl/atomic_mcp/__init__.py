"""
Atomic MCP - A framework for building MCP Servers using Atomic Agents and FastMCP.

Main exports for easy importing:
    - MCPServer: Main server class for creating MCP servers
    - Tool, Resource: Abstract base classes for implementing tools and resources
    - ToolResponse, ResourceResponse: Response models
    - BaseToolInput: Base class for tool input models

"""

from .server import (
    MCPServer,
    Tool,
    Resource,
    ToolResponse,
    ResourceResponse,
    BaseToolInput,
)

try:
    from importlib.metadata import version
    __version__ = version("atomic-mcp")
except ImportError:
    __version__ = "unknown"

__all__ = [
    "MCPServer",
    "Tool",
    "Resource",
    "ToolResponse",
    "ResourceResponse",
    "BaseToolInput",
]
