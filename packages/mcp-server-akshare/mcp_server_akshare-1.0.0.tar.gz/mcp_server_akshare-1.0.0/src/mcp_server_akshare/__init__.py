"""
MCP Server AkShare - A Model Context Protocol server for AkShare financial data APIs
"""

__version__ = "1.0.0"
__all__ = ["AkShareMCPServer", "AkShareWrapper"]

from .server import AkShareMCPServer
from .wrapper import AkShareWrapper
