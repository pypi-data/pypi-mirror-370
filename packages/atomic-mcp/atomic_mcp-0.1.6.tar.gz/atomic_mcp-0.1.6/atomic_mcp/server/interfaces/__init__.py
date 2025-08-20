"""Interfaces for atomic-mcp server components."""

from .tool import Tool, ToolResponse, ToolContent, BaseToolInput
from .resource import Resource, ResourceResponse, ResourceContent

__all__ = [
    "Tool",
    "ToolResponse",
    "ToolContent",
    "BaseToolInput",
    "Resource",
    "ResourceResponse",
    "ResourceContent",
]
