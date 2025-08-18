"""
Multi-Browser Crawler Package
============================

A standalone Python package for enterprise-grade browser automation with advanced features
like session isolation, proxy rotation, JavaScript execution, and multiprocess crawling.

Main Components:
- BrowserCrawler: Main entry point for browser operations
- BrowserManager: Core browser session management
- ProxyManager: File-based proxy rotation with health monitoring
- SessionManager: Session lifecycle and persistence
"""

from .core.browser_manager import BrowserManager
from .clients.browser_client import BrowserClient
from .config.settings import BrowserConfig
from .config.proxy_config import ProxyConfig

__version__ = "0.1.0"
__author__ = "Spider MCP Team"
__email__ = "team@spider-mcp.com"



# Deferred imports to avoid circular dependencies
def __getattr__(name):
    """Lazy import to avoid circular dependencies."""
    if name == "BrowserCrawler":
        from .api import BrowserCrawler
        return BrowserCrawler
    elif name == "fetch":
        from .api import fetch
        return fetch
    elif name == "fetch_batch":
        from .api import fetch_batch
        return fetch_batch
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Update exports
__all__ = [
    "BrowserCrawler",
    "BrowserManager",
    "BrowserClient",
    "BrowserConfig",
    "ProxyConfig",
    "fetch",
    "fetch_batch"
]
