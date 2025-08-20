"""Main MCP Server coordinator for atomic-mcp framework."""

import asyncio
import logging
import os
import signal
import sys
from typing import List, Optional, Callable, Any, Dict, Awaitable, Union

from fastmcp import FastMCP
from atomic_mcp.server.interfaces.tool import Tool
from atomic_mcp.server.interfaces.resource import Resource
from atomic_mcp.server.interfaces.middleware import MiddlewareChain, ToolMiddleware, ResourceMiddleware
from atomic_mcp.server.services.tool import ToolService
from atomic_mcp.server.services.resource import ResourceService


# Configure logging for subprocess environment
def _configure_stdio_logging():
    """Configure logging for STDIO transport to avoid polluting MCP communication."""
    # In STDIO mode, stdout/stderr are used for MCP protocol
    # Log to file or disable logging to avoid interference
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        # Running as subprocess - configure file logging or disable
        log_file = os.getenv("MCP_LOG_FILE")
        if log_file:
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        else:
            # Disable logging to avoid interfering with MCP protocol
            logging.getLogger().setLevel(logging.CRITICAL)
    else:
        # Normal console logging for HTTP mode
        logging.basicConfig(level=logging.INFO)


_configure_stdio_logging()
logger = logging.getLogger(__name__)


class MCPServer:
    """
    Main MCP Server coordinator that provides a simple interface for registering
    tools and resources, then running the server with FastMCP.

    Supports STDIO and HTTP transports only (SSE is deprecated).
    """

    def __init__(
        self, 
        name: str = "atomic-mcp-server", 
        description: str = "",
        # Core FastMCP parameters
        instructions: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        lifespan: Optional[Callable] = None,
        # ServerSettings parameters  
        log_level: Optional[str] = None,
        debug: Optional[bool] = None,
        # Route configuration
        enable_health_check: bool = True,
        health_check_path: str = "/health",
        version: str = "0.1.0",
        stateless_http: bool = False,
        # JWT Authentication options
        enable_jwt_validation: bool = False,
        jwt_public_key: Optional[str] = None,
        jwt_issuer: Optional[str] = None,
        jwt_audience: Optional[str] = None,
        jwt_algorithms: Optional[List[str]] = None,
        custom_auth_provider: Optional[Any] = None,
        **fastmcp_kwargs
    ):
        """
        Initialize the MCP Server.

        Args:
            name: Server name identifier
            description: Server description
            instructions: Instructions for the FastMCP server
            dependencies: List of dependencies for deployment
            lifespan: Async context manager for startup/shutdown logic
            log_level: Logging level for the server
            debug: Enable debug mode
            enable_health_check: Whether to enable the default health check route
            health_check_path: Path for the health check endpoint
            enable_jwt_validation: Enable JWT token validation for HTTP transport
            jwt_public_key: Public key for JWT verification (PEM format)
            jwt_issuer: Expected JWT issuer claim
            jwt_audience: Expected JWT audience claim
            jwt_algorithms: List of allowed JWT algorithms (default: ["RS256"])
            custom_auth_provider: Custom authentication provider instance (overrides JWT settings)
            **fastmcp_kwargs: Additional keyword arguments passed to FastMCP constructor
        """
        self.name = name
        self.description = description
        
        # Store route configuration
        self.enable_health_check = enable_health_check
        self.health_check_path = health_check_path
        
        # Store JWT configuration
        self.enable_jwt_validation = enable_jwt_validation
        self.jwt_public_key = jwt_public_key
        self.jwt_issuer = jwt_issuer
        self.jwt_audience = jwt_audience
        self.jwt_algorithms = jwt_algorithms or ["RS256"]
        self.custom_auth_provider = custom_auth_provider
        
        # Store FastMCP configuration for later use
        self._fastmcp_config = {
            "instructions": instructions,
            "dependencies": dependencies,
            "lifespan": lifespan,
            "log_level": log_level,
            "debug": debug,
            "version": version,
            "stateless_http": stateless_http,
            **fastmcp_kwargs
        }
        # Remove None values to let FastMCP use its defaults
        self._fastmcp_config = {k: v for k, v in self._fastmcp_config.items() if v is not None}

        # Initialize middleware chain
        self.middleware_chain = MiddlewareChain()
        
        # Initialize services with middleware support
        self.tool_service = ToolService(self.middleware_chain)
        self.resource_service = ResourceService(self.middleware_chain)

        # FastMCP instance (created when server runs)
        self._mcp_server: Optional[FastMCP] = None
        
        # Custom route handlers storage
        self._custom_routes: List[Dict[str, Any]] = []

        # Shutdown flag for graceful termination
        self._shutdown_requested = False

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self._shutdown_requested = True

        # Handle SIGINT (Ctrl+C) and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool instance to the server.

        Args:
            tool: Tool instance that implements the Tool interface
        """
        self.tool_service.register_tool(tool)
        logger.debug(f"Registered tool: {tool.name}")

    def add_tools(self, tools: List[Tool]) -> None:
        """
        Add multiple tool instances to the server.

        Args:
            tools: List of Tool instances
        """
        self.tool_service.register_tools(tools)
        logger.debug(f"Registered {len(tools)} tools")

    def add_resource(self, resource: Resource) -> None:
        """
        Add a resource instance to the server.

        Args:
            resource: Resource instance that implements the Resource interface
        """
        self.resource_service.register_resource(resource)
        logger.debug(f"Registered resource: {resource.name}")

    def add_resources(self, resources: List[Resource]) -> None:
        """
        Add multiple resource instances to the server.

        Args:
            resources: List of Resource instances
        """
        self.resource_service.register_resources(resources)
        logger.debug(f"Registered {len(resources)} resources")

    def add_middleware(self, middleware: Union[ToolMiddleware, ResourceMiddleware]) -> None:
        """
        Add middleware to the server.

        Args:
            middleware: Middleware instance that implements ToolMiddleware or ResourceMiddleware
        """
        if isinstance(middleware, ToolMiddleware):
            self.middleware_chain.add_tool_middleware(middleware)
            logger.debug(f"Registered tool middleware: {middleware.name}")
        
        if isinstance(middleware, ResourceMiddleware):
            self.middleware_chain.add_resource_middleware(middleware)
            logger.debug(f"Registered resource middleware: {middleware.name}")

    def add_middlewares(self, middlewares: List[Union[ToolMiddleware, ResourceMiddleware]]) -> None:
        """
        Add multiple middleware instances to the server.

        Args:
            middlewares: List of middleware instances
        """
        for middleware in middlewares:
            self.add_middleware(middleware)
        logger.debug(f"Registered {len(middlewares)} middleware instances")

    def enable_logging_middleware(
        self, 
        log_level: str = "INFO",
        log_inputs: bool = True,
        log_outputs: bool = False,
        log_timing: bool = True,
        structured_logging: bool = True,
        simple: bool = False
    ) -> None:
        """
        Enable logging middleware with convenient defaults.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_inputs: Whether to log input parameters
            log_outputs: Whether to log output results  
            log_timing: Whether to log execution timing
            structured_logging: Whether to use structured (JSON) logging
            simple: Use simple logging middleware instead of full featured one
        """
        if simple:
            from atomic_mcp.server.middleware.logging import SimpleLoggingMiddleware
            middleware = SimpleLoggingMiddleware()
        else:
            from atomic_mcp.server.middleware.logging import LoggingMiddleware
            middleware = LoggingMiddleware(
                log_level=log_level,
                log_inputs=log_inputs,
                log_outputs=log_outputs,
                log_timing=log_timing,
                structured_logging=structured_logging
            )
        
        self.add_middleware(middleware)
        logger.info(f"Enabled {'simple' if simple else 'full'} logging middleware")

    def add_route(
        self, 
        path: str, 
        handler: Callable, 
        methods: List[str] = ["GET"], 
        name: Optional[str] = None,
        include_in_schema: bool = True
    ) -> None:
        """
        Add a custom HTTP route to the server.

        Args:
            path: URL path for the route (e.g., "/custom/endpoint")
            handler: Async function that handles the route (takes Request, returns Response)
            methods: List of HTTP methods to support
            name: Optional name for the route
            include_in_schema: Whether to include in OpenAPI schema
        """
        route_config = {
            "path": path,
            "handler": handler,
            "methods": methods,
            "name": name,
            "include_in_schema": include_in_schema
        }
        self._custom_routes.append(route_config)
        logger.debug(f"Added custom route: {methods} {path}")

    def _create_health_check_handler(self):
        """Create the default health check route handler."""
        async def health_check(request):
            """Health check endpoint that returns server status."""
            try:
                # Import here to avoid issues if starlette isn't available in STDIO mode
                from starlette.responses import JSONResponse, Response
                
                health_data = {
                    "status": "healthy",
                    "server": self.name,
                    "tools": len(self.tool_service._tools),
                    "resources": len(self.resource_service._uri_patterns),
                    "version": "0.1.2"  # Could be made configurable
                }
                return JSONResponse(health_data)
            except ImportError:
                # Fallback if starlette isn't available
                logger.warning("Starlette not available for health check JSON response")
                from starlette.responses import Response
                return Response(f"OK - {self.name}")
        
        return health_check

    def _create_jwt_auth_provider(self):
        """Create JWT authentication provider for FastMCP."""
        if not self.jwt_public_key:
            raise ValueError("JWT public key is required when JWT validation is enabled")
            
        try:
            # Try the new JWTVerifier first, fall back to deprecated BearerAuthProvider
            try:
                from fastmcp.server.auth.providers.jwt import JWTVerifier
                
                auth_provider = JWTVerifier(
                    public_key=self.jwt_public_key,
                    issuer=self.jwt_issuer,
                    audience=self.jwt_audience
                )
                logger.info("JWT authentication provider configured (JWTVerifier)")
                
            except ImportError:
                # Fall back to deprecated BearerAuthProvider
                from fastmcp.server.auth import BearerAuthProvider
                from cryptography.hazmat.primitives import serialization
                
                # Parse the public key
                if self.jwt_public_key.startswith('-----BEGIN'):
                    # PEM format
                    public_key = serialization.load_pem_public_key(
                        self.jwt_public_key.encode('utf-8')
                    )
                else:
                    # Assume it's a base64 encoded key
                    import base64
                    key_data = base64.b64decode(self.jwt_public_key)
                    public_key = serialization.load_der_public_key(key_data)
                
                auth_provider = BearerAuthProvider(
                    public_key=public_key,
                    issuer=self.jwt_issuer,
                    audience=self.jwt_audience
                )
                logger.warning("Using deprecated BearerAuthProvider - consider updating FastMCP")
                logger.info("JWT authentication provider configured (BearerAuthProvider)")
            
            return auth_provider
            
        except ImportError as e:
            logger.error(f"FastMCP auth dependencies not available: {e}")
            logger.error("Install with: pip install 'fastmcp[auth]'")
            raise
        except Exception as e:
            logger.error(f"Failed to setup JWT authentication: {e}")
            raise

    def _setup_mcp_server(self) -> FastMCP:
        """Setup and configure the underlying FastMCP server."""
        if self._mcp_server is None:
            # Setup authentication if enabled
            auth_provider = None
            if self.custom_auth_provider:
                # Use custom auth provider if provided
                auth_provider = self.custom_auth_provider
                logger.info("Using custom authentication provider")
            elif self.enable_jwt_validation and self.jwt_public_key:
                # Use built-in JWT validation
                auth_provider = self._create_jwt_auth_provider()
            
            # Create FastMCP instance with stored configuration
            config = self._fastmcp_config.copy()
            if auth_provider:
                config["auth"] = auth_provider
                
            self._mcp_server = FastMCP(self.name, **config)

            # Register all tools and resources with FastMCP
            self.tool_service.register_mcp_handlers(self._mcp_server)
            self.resource_service.register_mcp_handlers(self._mcp_server)
            
            # Register custom routes
            self._setup_custom_routes()

        return self._mcp_server

    def _setup_custom_routes(self) -> None:
        """Setup custom HTTP routes including health check."""
        if self._mcp_server is None:
            return
            
        # Add default health check route if enabled
        if self.enable_health_check:
            health_handler = self._create_health_check_handler()
            self._mcp_server.custom_route(
                path=self.health_check_path,
                methods=["GET"],
                name="health_check"
            )(health_handler)
            logger.debug(f"Added health check route: GET {self.health_check_path}")
        
        # Add user-defined custom routes
        for route_config in self._custom_routes:
            self._mcp_server.custom_route(
                path=route_config["path"],
                methods=route_config["methods"],
                name=route_config["name"],
                include_in_schema=route_config["include_in_schema"]
            )(route_config["handler"])
            logger.debug(f"Added custom route: {route_config['methods']} {route_config['path']}")

    def _detect_transport(self) -> str:
        """
        Auto-detect the appropriate transport method.

        Returns:
            "stdio" if running in STDIO mode, "http" otherwise
        """
        # Check if we're running in STDIO mode (common MCP client pattern)
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return "stdio"

        # Check environment variables that might indicate STDIO mode
        if os.getenv("MCP_STDIO_MODE") or os.getenv("MCP_TRANSPORT") == "stdio":
            return "stdio"

        # Default to HTTP for development/testing
        return "http"

    async def run_async(
        self, transport: str = "auto", host: str = "localhost", port: int = 8000
    ) -> None:
        """
        Run the server asynchronously.

        Args:
            transport: Transport method ("auto", "stdio", or "http")
            host: Host for HTTP transport
            port: Port for HTTP transport
        """
        if transport == "auto":
            transport = self._detect_transport()

        mcp_server = self._setup_mcp_server()

        if transport == "stdio":
            logger.info(f"Starting {self.name} with STDIO transport")
            await mcp_server.run_async(transport="stdio")
        elif transport == "http":
            logger.info(
                f"Starting {self.name} with HTTP transport on {host}:{port}/mcp"
            )
            await mcp_server.run_async(
                transport="http", port=port, host=host, path="/mcp"
            )
        else:
            raise ValueError(
                f"Unknown transport: {transport}. Only 'stdio' and 'http' are supported."
            )

    def run(
        self, transport: str = "auto", host: str = "localhost", port: int = 8000
    ) -> None:
        """
        Run the server (blocking call).

        Args:
            transport: Transport method ("auto", "stdio", or "http")
            host: Host for HTTP transport
            port: Port for HTTP transport
        """
        try:
            asyncio.run(self.run_async(transport, host, port))
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

    def run_stdio(self) -> None:
        """Run the server with STDIO transport."""
        self.run(transport="stdio")

    def run_http(self, host: str = "localhost", port: int = 8000) -> None:
        """
        Run the server with HTTP transport.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.run(transport="http", host=host, port=port)

    def get_registered_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self.tool_service._tools.keys())

    def get_registered_resources(self) -> List[str]:
        """Get list of registered resource URI patterns."""
        return list(self.resource_service._uri_patterns.keys())

    def tool(self, name: str, description: str = ""):
        """
        Decorator for registering tool handlers with FastMCP.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Decorator function that registers the handler with FastMCP
        """
        if self._mcp_server is None:
            self._setup_mcp_server()
        # At this point _mcp_server is guaranteed to be a FastMCP instance
        assert self._mcp_server is not None
        return self._mcp_server.tool(name=name, description=description)

    def __repr__(self) -> str:
        tools_count = len(self.tool_service._tools)
        resources_count = len(self.resource_service._uri_patterns)
        return (
            f"MCPServer(name='{self.name}', "
            f"tools={tools_count}, "
            f"resources={resources_count})"
        )
