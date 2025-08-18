"""
Custom exception hierarchy for multi-browser-crawler.
"""


class BrowserCrawlerError(Exception):
    """Base exception for all browser crawler errors."""
    pass


class BrowserInitializationError(BrowserCrawlerError):
    """Raised when browser initialization fails."""
    pass


class SessionError(BrowserCrawlerError):
    """Raised when session management operations fail."""
    pass


class ProxyError(BrowserCrawlerError):
    """Raised when proxy operations fail."""
    pass


class JavaScriptExecutionError(BrowserCrawlerError):
    """Raised when JavaScript execution fails."""
    pass


class ImageDownloadError(BrowserCrawlerError):
    """Raised when image download operations fail."""
    pass


class ResourceCleanupError(BrowserCrawlerError):
    """Raised when resource cleanup operations fail."""
    pass


class ConfigurationError(BrowserCrawlerError):
    """Raised when configuration is invalid."""
    pass


class NetworkError(BrowserCrawlerError):
    """Raised when network operations fail."""
    pass


class TimeoutError(BrowserCrawlerError):
    """Raised when operations timeout."""
    pass
