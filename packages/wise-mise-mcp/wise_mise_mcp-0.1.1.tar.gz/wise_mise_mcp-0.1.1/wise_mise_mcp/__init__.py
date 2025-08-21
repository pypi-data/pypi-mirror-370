"""
Wise Mise MCP Server

An intelligent MCP server for wise mise task management and organization.
"""

import sys
from importlib.metadata import version, PackageNotFoundError

from .server import app

try:
    __version__ = version("wise-mise-mcp")
except PackageNotFoundError:
    # Fallback for development installations
    __version__ = "dev"

__all__ = ["app"]
