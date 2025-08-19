"""MCP KiCAD Schematic API Server

Model Context Protocol server providing KiCAD schematic manipulation tools for AI agents.
"""

import asyncio
from .server import main as async_main

__version__ = "0.1.1"

def main():
    """Synchronous entry point for the MCP server."""
    asyncio.run(async_main())

__all__ = ["main"]