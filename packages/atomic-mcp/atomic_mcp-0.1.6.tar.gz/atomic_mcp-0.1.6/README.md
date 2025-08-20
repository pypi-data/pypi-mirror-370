# atomic-mcp

A framework for building MCP Servers using Atomic Agents and FastMCP.

Intended to be an easy to use framework for starting an MCP server and adding tools.

## Install

```bash
pip install atomic-mcp
```

## Usage

```python
from atomic_mcp import MCPServer, Tool, ToolResponse, BaseToolInput
from pydantic import Field

class HelloInput(BaseToolInput):
    name: str = Field(description="Name to greet")

class HelloTool(Tool[HelloInput]):
    name = "hello"
    description = "Say hello"
    
    async def run(self, input_data: HelloInput) -> ToolResponse:
        return ToolResponse(
            content=[{"type": "text", "text": f"Hello {input_data.name}!"}],
            is_error=False
        )

# Create server with tools
server = MCPServer("my-server")
server.register_tools([HelloTool()])

if __name__ == "__main__":
    server.run()  # STDIO for Claude Desktop
    # server.run(transport="http", port=8000, path="/mcp")  # HTTP
```

## CLI

```bash
atomic-mcp config add-stdio my-server "python" "/path/to/server.py"
```