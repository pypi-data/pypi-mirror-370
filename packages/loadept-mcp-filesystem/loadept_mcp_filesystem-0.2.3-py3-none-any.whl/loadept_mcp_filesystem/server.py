from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from sys import stderr
from .schemas import *
from .tools import *
from .utils import ToolRegister, SchemaRegister


async def serve():
    server = Server('filesystem')

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        schemas = SchemaRegister.get_schemas()
        return [
            Tool(
                name=scheme,
                description=schemas[scheme]['description'],
                inputSchema=schemas[scheme]['json_schema'],
            )
            for scheme in schemas.keys()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        tools = ToolRegister.get_tools()
        if name not in tools:
            raise ValueError(f"Herramienta desconocida: {name}")

        return tools[name](**arguments)

    server_options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server_options, raise_exceptions=True)

def main():
    import asyncio
    try:
        print("Starting MCP server...")
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("MCP server stopped by user.", file=stderr)
