"""
Spider MCP Client - Official Python client for Spider MCP web scraping API
"""

__version__ = "0.1.0"
__author__ = "Spider MCP Team"
__email__ = "support@spider-mcp.com"

from .client import SpiderMCPClient
from .exceptions import (
    SpiderMCPError,
    AuthenticationError,
    ParserNotFoundError,
    RateLimitError,
    ServerError,
)

__all__ = [
    "SpiderMCPClient",
    "SpiderMCPError",
    "AuthenticationError", 
    "ParserNotFoundError",
    "RateLimitError",
    "ServerError",
]
