"""Logging middleware for tools and resources."""

import logging
import json
import os
from typing import Any, Dict, ClassVar, Optional

from atomic_mcp.server.interfaces.middleware import (
    ToolMiddleware, 
    ResourceMiddleware, 
    MiddlewareContext
)
from atomic_mcp.server.interfaces.tool import Tool, ToolResponse, BaseToolInput
from atomic_mcp.server.interfaces.resource import Resource, ResourceResponse


class LoggingMiddleware(ToolMiddleware, ResourceMiddleware):
    """Middleware that logs tool and resource operations."""
    
    name: ClassVar[str] = "logging"
    priority: ClassVar[int] = 10  # Execute early for accurate timing
    
    def __init__(
        self, 
        logger_name: str = "atomic_mcp.middleware",
        log_level: str = "INFO",
        log_inputs: bool = True,
        log_outputs: bool = False,
        log_timing: bool = True,
        structured_logging: bool = True
    ):
        """
        Initialize the logging middleware.
        
        Args:
            logger_name: Name of the logger to use
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_inputs: Whether to log input parameters
            log_outputs: Whether to log output results
            log_timing: Whether to log execution timing
            structured_logging: Whether to use structured (JSON) logging
        """
        self.logger = logging.getLogger(logger_name)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_inputs = log_inputs
        self.log_outputs = log_outputs
        self.log_timing = log_timing
        self.structured_logging = structured_logging
        
        # Configure logger if not already configured
        if not self.logger.handlers:
            self._configure_logger()
    
    def _configure_logger(self) -> None:
        """Configure the logger for middleware use."""
        # Check if we're in STDIO mode and should log to file
        if not os.isatty(0) or not os.isatty(1):  # STDIO mode
            log_file = os.getenv("MCP_LOG_FILE", "/tmp/atomic_mcp.log")
            handler = logging.FileHandler(log_file)
        else:
            handler = logging.StreamHandler()
        
        if self.structured_logging:
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(self.log_level)
    
    def _log_structured(self, level: int, event_type: str, data: Dict[str, Any]) -> None:
        """Log structured data."""
        if self.structured_logging:
            message = json.dumps({
                "event_type": event_type,
                **data
            })
        else:
            message = f"{event_type}: {data}"
        
        self.logger.log(level, message)
    
    def _sanitize_for_logging(self, data: Any, max_length: int = 1000) -> Any:
        """Sanitize data for logging by truncating long strings and removing sensitive data."""
        if isinstance(data, str):
            if len(data) > max_length:
                return data[:max_length] + "... (truncated)"
            return data
        elif isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Skip potentially sensitive keys
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret']):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_for_logging(value, max_length)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_for_logging(item, max_length) for item in data[:10]]  # Limit list length
        else:
            return data

    # Tool middleware methods
    async def before(self, context: MiddlewareContext, tool: Tool, input_data: BaseToolInput) -> None:
        """Log before tool execution."""
        log_data = {
            "operation": "tool_execution_start",
            "tool_name": tool.name,
            "tool_description": tool.description
        }
        
        if self.log_inputs:
            log_data["input_data"] = self._sanitize_for_logging(input_data.model_dump())
        
        self._log_structured(logging.INFO, "tool_start", log_data)
    
    async def after(self, context: MiddlewareContext, result: ToolResponse, tool: Tool, input_data: BaseToolInput) -> ToolResponse:
        """Log after successful tool execution."""
        log_data = {
            "operation": "tool_execution_success",
            "tool_name": tool.name,
            "success": True
        }
        
        if self.log_timing and context.execution_time:
            log_data["execution_time_ms"] = round(context.execution_time * 1000, 2)
        
        if self.log_outputs:
            # Sanitize the result for logging
            result_data = []
            for content in result.content:
                content_data = {"type": content.type}
                if content.text:
                    content_data["text"] = self._sanitize_for_logging(content.text)
                if content.json_data:
                    content_data["json_data"] = self._sanitize_for_logging(content.json_data)
                result_data.append(content_data)
            log_data["result"] = result_data
        
        self._log_structured(logging.INFO, "tool_success", log_data)
        return result
    
    async def on_error(self, context: MiddlewareContext, error: Exception, tool: Tool, input_data: BaseToolInput) -> None:
        """Log tool execution errors."""
        log_data = {
            "operation": "tool_execution_error",
            "tool_name": tool.name,
            "success": False,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if self.log_timing and context.execution_time:
            log_data["execution_time_ms"] = round(context.execution_time * 1000, 2)
        
        self._log_structured(logging.ERROR, "tool_error", log_data)

    # Resource middleware methods (implementing the ResourceMiddleware interface)
    async def before(self, context: MiddlewareContext, resource: Resource, uri: str, params: Dict[str, str]) -> None:
        """Log before resource read."""
        log_data = {
            "operation": "resource_read_start",
            "resource_name": resource.name,
            "resource_description": resource.description,
            "uri": uri
        }
        
        if params:
            log_data["params"] = self._sanitize_for_logging(params)
        
        self._log_structured(logging.INFO, "resource_start", log_data)
    
    async def after(self, context: MiddlewareContext, result: ResourceResponse, resource: Resource, uri: str, params: Dict[str, str]) -> ResourceResponse:
        """Log after successful resource read."""
        log_data = {
            "operation": "resource_read_success",
            "resource_name": resource.name,
            "uri": uri,
            "success": True,
            "content_count": len(result.contents)
        }
        
        if self.log_timing and context.execution_time:
            log_data["execution_time_ms"] = round(context.execution_time * 1000, 2)
        
        if self.log_outputs:
            # Log basic info about contents without full text
            contents_info = []
            for content in result.contents:
                content_info = {
                    "type": content.type,
                    "uri": content.uri,
                    "mime_type": content.mime_type,
                    "text_length": len(content.text) if content.text else 0
                }
                contents_info.append(content_info)
            log_data["contents"] = contents_info
        
        self._log_structured(logging.INFO, "resource_success", log_data)
        return result
    
    async def on_error(self, context: MiddlewareContext, error: Exception, resource: Resource, uri: str, params: Dict[str, str]) -> None:
        """Log resource read errors."""
        log_data = {
            "operation": "resource_read_error",
            "resource_name": resource.name,
            "uri": uri,
            "success": False,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if self.log_timing and context.execution_time:
            log_data["execution_time_ms"] = round(context.execution_time * 1000, 2)
        
        self._log_structured(logging.ERROR, "resource_error", log_data)


class SimpleLoggingMiddleware(ToolMiddleware, ResourceMiddleware):
    """Simplified logging middleware with minimal configuration."""
    
    name: ClassVar[str] = "simple_logging"
    priority: ClassVar[int] = 10
    
    def __init__(self, logger_name: str = "atomic_mcp"):
        self.logger = logging.getLogger(logger_name)
    
    async def before(self, context: MiddlewareContext, *args, **kwargs) -> None:
        """Log operation start."""
        if context.middleware_type.value == "tool":
            tool = args[0]
            self.logger.info(f"Executing tool: {tool.name}")
        else:
            resource, uri = args[0], args[1]
            self.logger.info(f"Reading resource: {resource.name} ({uri})")
    
    async def after(self, context: MiddlewareContext, result: Any, *args, **kwargs) -> Any:
        """Log successful completion."""
        timing = f" ({context.execution_time:.3f}s)" if context.execution_time else ""
        if context.middleware_type.value == "tool":
            tool = args[0]
            self.logger.info(f"Tool completed: {tool.name}{timing}")
        else:
            resource, uri = args[0], args[1]
            self.logger.info(f"Resource read completed: {resource.name}{timing}")
        return result
    
    async def on_error(self, context: MiddlewareContext, error: Exception, *args, **kwargs) -> None:
        """Log errors."""
        timing = f" ({context.execution_time:.3f}s)" if context.execution_time else ""
        if context.middleware_type.value == "tool":
            tool = args[0]
            self.logger.error(f"Tool failed: {tool.name}{timing} - {error}")
        else:
            resource, uri = args[0], args[1]
            self.logger.error(f"Resource read failed: {resource.name}{timing} - {error}")