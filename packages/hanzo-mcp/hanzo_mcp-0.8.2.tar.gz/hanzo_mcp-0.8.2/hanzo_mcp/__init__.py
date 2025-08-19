"""Hanzo AI - Implementation of Hanzo capabilities using MCP."""

# Configure FastMCP logging globally for stdio transport
import os
import warnings

# Suppress litellm deprecation warnings about event loop
warnings.filterwarnings("ignore", message="There is no current event loop", category=DeprecationWarning)

if os.environ.get("HANZO_MCP_TRANSPORT") == "stdio":
    try:
        from fastmcp.utilities.logging import configure_logging

        configure_logging(level="ERROR")
    except ImportError:
        pass

__version__ = "0.7.7"
