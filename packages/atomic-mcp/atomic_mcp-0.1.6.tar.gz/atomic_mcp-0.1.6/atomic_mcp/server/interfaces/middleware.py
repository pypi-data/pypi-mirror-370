"""Middleware interfaces for intercepting tool and resource operations."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, ClassVar
from enum import Enum

from atomic_mcp.server.interfaces.tool import Tool, ToolResponse, BaseToolInput
from atomic_mcp.server.interfaces.resource import Resource, ResourceResponse


class MiddlewareType(Enum):
    """Types of middleware operations."""
    TOOL = "tool"
    RESOURCE = "resource"


class MiddlewareContext:
    """Context object passed through middleware chain."""
    
    def __init__(
        self, 
        middleware_type: MiddlewareType,
        name: str,
        start_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.middleware_type = middleware_type
        self.name = name
        self.start_time = start_time or time.time()
        self.metadata = metadata or {}
        self.execution_time: Optional[float] = None
        self.error: Optional[Exception] = None
        
    def mark_completed(self) -> None:
        """Mark the operation as completed and calculate execution time."""
        self.execution_time = time.time() - self.start_time
        
    def mark_error(self, error: Exception) -> None:
        """Mark the operation as failed with an error."""
        self.execution_time = time.time() - self.start_time
        self.error = error


class BaseMiddleware(ABC):
    """Base class for all middleware."""
    
    name: ClassVar[str]
    priority: ClassVar[int] = 100  # Lower numbers execute first
    
    @abstractmethod
    async def before(self, context: MiddlewareContext, *args, **kwargs) -> None:
        """Called before the operation executes."""
        pass
    
    @abstractmethod
    async def after(self, context: MiddlewareContext, result: Any, *args, **kwargs) -> Any:
        """Called after successful operation execution."""
        pass
    
    @abstractmethod
    async def on_error(self, context: MiddlewareContext, error: Exception, *args, **kwargs) -> None:
        """Called when operation fails with an error."""
        pass


class ToolMiddleware(BaseMiddleware):
    """Base class for tool-specific middleware."""
    
    async def before(self, context: MiddlewareContext, tool: Tool, input_data: BaseToolInput) -> None:
        """Called before tool execution."""
        pass
    
    async def after(self, context: MiddlewareContext, result: ToolResponse, tool: Tool, input_data: BaseToolInput) -> ToolResponse:
        """Called after successful tool execution."""
        return result
    
    async def on_error(self, context: MiddlewareContext, error: Exception, tool: Tool, input_data: BaseToolInput) -> None:
        """Called when tool execution fails."""
        pass


class ResourceMiddleware(BaseMiddleware):
    """Base class for resource-specific middleware."""
    
    async def before(self, context: MiddlewareContext, resource: Resource, uri: str, params: Dict[str, str]) -> None:
        """Called before resource read."""
        pass
    
    async def after(self, context: MiddlewareContext, result: ResourceResponse, resource: Resource, uri: str, params: Dict[str, str]) -> ResourceResponse:
        """Called after successful resource read."""
        return result
    
    async def on_error(self, context: MiddlewareContext, error: Exception, resource: Resource, uri: str, params: Dict[str, str]) -> None:
        """Called when resource read fails."""
        pass


class MiddlewareChain:
    """Manages and executes middleware chain."""
    
    def __init__(self):
        self._tool_middleware: List[ToolMiddleware] = []
        self._resource_middleware: List[ResourceMiddleware] = []
    
    def add_tool_middleware(self, middleware: ToolMiddleware) -> None:
        """Add tool middleware to the chain."""
        self._tool_middleware.append(middleware)
        # Sort by priority (lower numbers first)
        self._tool_middleware.sort(key=lambda m: m.priority)
    
    def add_resource_middleware(self, middleware: ResourceMiddleware) -> None:
        """Add resource middleware to the chain."""
        self._resource_middleware.append(middleware)
        # Sort by priority (lower numbers first)
        self._resource_middleware.sort(key=lambda m: m.priority)
    
    async def execute_tool_middleware(
        self, 
        tool: Tool, 
        input_data: BaseToolInput,
        execute_func
    ) -> ToolResponse:
        """Execute tool middleware chain around tool execution."""
        context = MiddlewareContext(MiddlewareType.TOOL, tool.name)
        
        try:
            # Before middleware
            for middleware in self._tool_middleware:
                await middleware.before(context, tool, input_data)
            
            # Execute the actual tool
            result = await execute_func()
            context.mark_completed()
            
            # After middleware (in reverse order)
            for middleware in reversed(self._tool_middleware):
                result = await middleware.after(context, result, tool, input_data)
            
            return result
            
        except Exception as error:
            context.mark_error(error)
            
            # Error middleware
            for middleware in self._tool_middleware:
                await middleware.on_error(context, error, tool, input_data)
            
            raise
    
    async def execute_resource_middleware(
        self,
        resource: Resource,
        uri: str,
        params: Dict[str, str],
        execute_func
    ) -> ResourceResponse:
        """Execute resource middleware chain around resource read."""
        context = MiddlewareContext(MiddlewareType.RESOURCE, resource.name)
        context.metadata.update({"uri": uri, "params": params})
        
        try:
            # Before middleware
            for middleware in self._resource_middleware:
                await middleware.before(context, resource, uri, params)
            
            # Execute the actual resource read
            result = await execute_func()
            context.mark_completed()
            
            # After middleware (in reverse order)
            for middleware in reversed(self._resource_middleware):
                result = await middleware.after(context, result, resource, uri, params)
            
            return result
            
        except Exception as error:
            context.mark_error(error)
            
            # Error middleware
            for middleware in self._resource_middleware:
                await middleware.on_error(context, error, resource, uri, params)
            
            raise