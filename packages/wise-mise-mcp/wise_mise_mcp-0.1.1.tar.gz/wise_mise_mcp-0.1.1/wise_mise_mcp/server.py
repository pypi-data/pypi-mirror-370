"""
FastMCP server for intelligent mise task management
"""

import sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .models import TaskDomain, TaskComplexity
from .analyzer import TaskAnalyzer
from .manager import TaskManager

# Get version from package metadata
try:
    __version__ = version("wise-mise-mcp")
except PackageNotFoundError:
    __version__ = "dev"

# Request/Response models
class AnalyzeProjectRequest(BaseModel):
    project_path: str = Field(description="Path to the project directory")
