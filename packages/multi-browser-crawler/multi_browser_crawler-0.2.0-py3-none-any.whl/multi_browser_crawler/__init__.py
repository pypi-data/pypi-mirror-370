"""
Multi-Browser Crawler Package - Clean and Simple
================================================

A clean browser automation package focused on browser fetching operations.

Main Components:
- BrowserPoolManager: Clean browser pool management with undetected-chromedriver
- ProxyManager: Simple proxy management with Chrome-ready format
- DebugPortManager: Debug port allocation for browser instances
- BrowserConfig: Configuration management

Key Features:
- Clean, minimal code with no redundancy
- Direct undetected-chromedriver integration
- Chrome-ready proxy format (no conversion needed)
- Robust proxy parsing with single regex
- No dangerous recursion or complex dependencies
- Built-in image downloading and API discovery
"""

from .browser import BrowserPoolManager
from .proxy_manager import ProxyManager
from .debug_port_manager import DebugPortManager
from .config import BrowserConfig

__version__ = "0.1.0-simple"
__author__ = "Spider MCP Team"
__email__ = "team@spider-mcp.com"


# Clean exports - only the essential components
__all__ = [
    "BrowserPoolManager",  # Clean browser pool management
    "ProxyManager",        # Simple proxy management
    "DebugPortManager",    # Debug port allocation
    "BrowserConfig",       # Configuration
]
