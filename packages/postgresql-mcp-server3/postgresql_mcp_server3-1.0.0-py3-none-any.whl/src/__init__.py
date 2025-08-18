"""
PostgreSQL MCP Server

A Model Context Protocol (MCP) server for PostgreSQL/RaseSQL databases.
"""
from typing import TYPE_CHECKING

__version__ = "1.0.0"
__author__ = "Frank Jin"
__email__ = "j00131120@163.com"
__description__ = "A Model Context Protocol (MCP) server that enables secure interaction with PostgreSQL databases."
__license__ = "MIT"
__url__ = "https://github.com/j00131120/mcp_database_server/tree/main/postgresql_mcp_server"

# Public API
__all__ = [
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__license__",
    "__url__",

    # Core modules (available via explicit import)
    "server",
    "utils",
    "resources",
    "tools",
]


def get_version() -> str:
    """Get the current version of the PostgreSQL MCP Server."""
    return __version__


def get_package_info() -> dict[str, str]:
    """Get comprehensive package information."""
    return {
        "name": "postgresql-mcp-server3",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "license": __license__,
        "url": __url__,
    }