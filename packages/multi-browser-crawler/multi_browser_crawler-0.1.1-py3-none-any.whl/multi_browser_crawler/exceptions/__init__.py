"""
Custom exceptions for multi-browser-crawler.
"""

from .errors import (
    BrowserCrawlerError,
    BrowserInitializationError,
    SessionError,
    ProxyError,
    JavaScriptExecutionError,
    ImageDownloadError
)

__all__ = [
    "BrowserCrawlerError",
    "BrowserInitializationError", 
    "SessionError",
    "ProxyError",
    "JavaScriptExecutionError",
    "ImageDownloadError"
]
