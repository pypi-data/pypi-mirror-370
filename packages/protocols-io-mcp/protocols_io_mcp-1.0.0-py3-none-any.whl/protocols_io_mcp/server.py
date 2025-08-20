import importlib
from fastmcp import FastMCP

mcp = FastMCP(
    name="protocols-io-mcp",
    instructions="""
        This server helps you interact with data from protocols.io.
    """
)
importlib.import_module('protocols_io_mcp.tools')