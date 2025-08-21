# Claude Integration Guide for MakeMCP

## Overview

MakeMCP is a wrapper library that simplifies creating MCP (Model Context Protocol) servers using the **official MCP Python SDK** (`mcp` package). This guide helps Claude and other AI assistants understand how to properly work with this codebase.

## Important: Use the Official MCP Python SDK

MakeMCP is built on top of the official MCP Python SDK from Anthropic. It is **NOT** compatible with FastMCP or other third-party MCP implementations.

### Required Dependencies

```bash
# Install using uv (recommended - 10-100x faster than pip)
uv pip install mcp

# Or using pip
pip install mcp
```

### UV Integration

MakeMCP is fully integrated with `uv` for blazing-fast package management:

1. **Automatic Detection**: All install commands auto-detect if `uv` is available
2. **Fallback Support**: Gracefully falls back to `pip` if `uv` is not installed
3. **Setup Script**: `setup.sh` automatically installs `uv` if not present
4. **Test Runner**: `run_tests.sh` uses `uv run` for faster test execution
5. **Dependency Errors**: Missing dependency errors show `uv pip install` commands when available

The official MCP SDK package is `mcp` (not `mcp-python`, `fastmcp`, or any other variant).

## Architecture Overview

MakeMCP provides a decorator-based API that internally uses the official SDK's handler-based approach:

1. **Decorators** (`@server.tool()`, `@server.resource()`, `@server.prompt()`) - Simple API for users
2. **Handler Registration** - MakeMCP registers handlers with the MCP Server internally
3. **Official SDK Server** - The underlying `mcp.server.Server` handles the protocol
4. **Discovery System** - Two-tier discovery for stdio and network servers
5. **Registry** - Local registry for stdio server management
6. **CLI** - Command-line interface for server management

## Key Implementation Details

### Server Initialization

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, Prompt, TextContent

class MakeMCPServer:
    def __init__(self, name: str, version: str = "1.0.0"):
        # Create the official SDK server
        self._server = Server(name, version=version)
        
        # Register handlers
        self._register_handlers()
```

### Async Function Support

MakeMCP provides **full support for async functions**. The factory system automatically detects and properly wraps async functions while preserving their async nature.

#### Key Async Features:

1. **Automatic Detection**: Uses `inspect.iscoroutinefunction()` to detect async functions
2. **Proper Wrapping**: Creates async wrappers that maintain coroutine behavior
3. **Mixed Support**: Sync and async functions can coexist in the same server
4. **Class Methods**: Both sync and async methods in classes are supported
5. **Decorator Support**: The `@mcp_tool` decorator preserves async functions

#### Async Function Wrapping Pattern:

```python
# In MCPFactory._register_function_as_tool()
if inspect.iscoroutinefunction(func):
    async def tool_wrapper(**kwargs):
        # Type conversion and validation
        converted_args = self._convert_arguments(kwargs, sig, type_hints)
        
        # Call the original async function
        result = await func(**converted_args)
        
        # Convert result to JSON-serializable format
        return self._convert_result(result)
else:
    def tool_wrapper(**kwargs):
        # Sync function wrapper
        # ...
```

#### Usage Examples:

```python
from makemcp.factory import create_mcp_from_module, mcp_tool
import asyncio

# Async functions are automatically detected
async def async_process(data: str) -> str:
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Processed: {data}"

@mcp_tool
async def decorated_async(value: int) -> int:
    await asyncio.sleep(0.1)
    return value * 2

# Class with mixed sync/async methods
class AsyncProcessor:
    async def async_method(self, x: int) -> int:
        await asyncio.sleep(0.1)
        return x * 2
    
    def sync_method(self, x: int) -> int:
        return x * 3
```

### Handler Registration Pattern

The official MCP SDK uses a handler-based approach, NOT decorators on the Server class:

```python
def _register_handlers(self):
    @self._server.list_tools()
    async def list_tools():
        # Return list of Tool objects
        return [Tool(...) for tool in self._tools]
    
    @self._server.call_tool()
    async def call_tool(name: str, arguments: dict):
        # Execute tool and return TextContent
        result = await self._tools[name](**arguments)
        return [TextContent(type="text", text=str(result))]
```

### Important: The Server Class Does NOT Have Tool/Resource/Prompt Methods

The official `mcp.server.Server` class does **NOT** have these methods:
- ❌ `server.tool()` - Does not exist
- ❌ `server.resource()` - Does not exist  
- ❌ `server.prompt()` - Does not exist

Instead, it has handler registration methods:
- ✅ `server.list_tools()` - Register handler for listing tools
- ✅ `server.call_tool()` - Register handler for calling tools
- ✅ `server.list_resources()` - Register handler for listing resources
- ✅ `server.read_resource()` - Register handler for reading resources
- ✅ `server.list_prompts()` - Register handler for listing prompts
- ✅ `server.get_prompt()` - Register handler for getting prompts

## Running Tests

The test suite validates compatibility with the official MCP SDK:

```bash
# Make test script executable
chmod +x run_tests.sh

# Run all tests
./run_tests.sh

# Or run with pytest directly
pytest tests/ -v
```

## Transport Modes

### stdio Transport (Default)
```python
async def run_stdio(self):
    # Create initialization options
    init_options = InitializationOptions(
        server_name=self.name,
        server_version=self.version,
        capabilities=ServerCapabilities(...),
        instructions=self.description
    )
    
    # Run with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await self._server.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options=init_options
        )
```

**Important**: For stdio transport:
- Logging is automatically redirected to stderr
- Autodiscovery is disabled (not applicable for child processes)
- Server responds to `--info` flag for metadata discovery

### SSE Transport
Requires additional dependencies: `pip install starlette uvicorn`
- Autodiscovery via UDP multicast is enabled
- Server broadcasts on network automatically

## Common Pitfalls to Avoid

1. **Don't try to use FastMCP patterns** - FastMCP has a different API that's incompatible
2. **Don't call non-existent methods** - The Server class doesn't have decorator methods
3. **Always use handler registration** - This is how the official SDK works
4. **Return proper types** - Tools must return TextContent objects, not raw values

## Development Workflow

When making changes to MakeMCP:

1. **Ensure official SDK is installed**: `uv pip install mcp`
2. **Run tests after changes**: `./run_tests.sh`
3. **Check coverage**: Open `htmlcov/index.html` after running tests
4. **Follow the handler pattern**: Don't try to add methods to the Server class

## Code Style Guidelines

- Use type hints for all function parameters and return values
- Follow the async/await pattern for all handlers
- Generate JSON schemas from function signatures when possible
- Keep the decorator API simple for end users

## Example Implementation Pattern

When adding new functionality, follow this pattern:

```python
# In MakeMCPServer class

def new_feature(self, **kwargs):
    """User-facing decorator."""
    def decorator(func):
        # Store function and metadata
        self._features[name] = func
        self._feature_metadata[name] = {...}
        return func
    return decorator

def _register_handlers(self):
    @self._server.list_features()  # If such handler exists
    async def list_features():
        # Return appropriate MCP types
        return [...]
```

## Testing New Features

When adding features:

1. Add unit tests in `tests/test_*.py`
2. Test both sync and async functions
3. Verify handler registration works
4. Ensure proper type conversion (to TextContent, etc.)

## Questions to Ask When Debugging

1. Is the official MCP SDK installed? (`pip show mcp`)
2. Are we using handler registration, not method decoration?
3. Are we returning the correct MCP types?
4. Is the async/await pattern used correctly?

## Discovery System

MakeMCP uses a two-tier discovery system:

### 1. Registry-based Discovery (stdio servers)
- Servers are registered in `~/.makemcp/registry.json`
- Can be discovered via filesystem scanning
- Exported to Gleitzeit-compatible configuration
- Managed via CLI: `makemcp register/list/discover`

### 2. Network Discovery (SSE/HTTP servers)
- Servers broadcast via UDP multicast (239.255.41.42:42424)
- Automatic discovery for network-based servers
- Only enabled for non-stdio transports

## CLI Commands

MakeMCP provides a CLI for server management:

```bash
# Server management
makemcp register <name> <command>  # Register a server
makemcp unregister <name>          # Remove a server
makemcp list                       # List registered servers
makemcp info <name>                # Show server details

# Discovery
makemcp discover --scan-filesystem  # Find servers in filesystem
makemcp discover --scan-network    # Find network servers

# Export
makemcp export --format yaml       # Export for Gleitzeit
```

## Server Metadata Protocol

Servers respond to `--info` flag with JSON metadata:

```python
if "--info" in sys.argv:
    info = {
        "name": self.name,
        "version": self.version,
        "description": self.description,
        "capabilities": {
            "tools": self.list_tools(),
            "resources": self.list_resources(),
            "prompts": self.list_prompts()
        }
    }
    print(json.dumps(info))
    sys.exit(0)
```

## MCP Factory System

MakeMCP includes a powerful factory system for automatically generating MCP servers from existing Python code.

### Core Factory Features

1. **Module Analysis**: Automatically discovers functions, classes, and decorated code
2. **Type Preservation**: Maintains original function signatures and type hints
3. **Async Support**: Full support for async/await patterns
4. **Multiple Sources**: Can create servers from modules, classes, functions, or decorated code

### Factory Usage Examples

```python
from makemcp.factory import MCPFactory, create_mcp_from_module

# Create server from a Python module
server = create_mcp_from_module("my_utils.py")

# Or use the factory directly
factory = MCPFactory(name="custom-server")
server = factory.from_module("my_utils.py")

# From a class
server = factory.from_class(MyProcessor)

# From specific functions
functions = {"add": lambda x, y: x + y, "multiply": multiply_func}
server = factory.from_functions(functions)

# From decorated functions only
server = factory.from_file_with_decorators("my_tools.py", decorator_name="mcp_tool")
```

### CLI Factory Command

```bash
# Generate MCP server from Python file
mcp-factory my_utils.py --name utils-server

# Filter specific functions
mcp-factory my_utils.py --include "calculate_*" --exclude "_private"

# Run with custom transport
mcp-factory my_utils.py --transport sse --port 8080
```

### Async Factory Support

The factory system fully supports async functions:

```python
# All these patterns work automatically
async def fetch_data(url: str) -> dict: ...        # Async function
def sync_process(data: str) -> str: ...             # Sync function
@mcp_tool async def decorated(x: int) -> int: ...   # Decorated async

class MixedProcessor:
    async def async_method(self, data): ...         # Async method
    def sync_method(self, data): ...                # Sync method
```

**Key Point**: The factory preserves the async nature of functions - async functions remain async, sync functions remain sync.

## Additional Resources

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)
- [MakeMCP Repository](https://github.com/leifmarkthaler/makemcp)
- [Gleitzeit Integration](https://github.com/leifmarkthaler/gleitzeit)