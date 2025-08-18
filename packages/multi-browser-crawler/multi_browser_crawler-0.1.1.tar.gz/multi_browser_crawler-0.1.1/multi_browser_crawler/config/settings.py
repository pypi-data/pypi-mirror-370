"""
Configuration Settings for Multi-Browser Crawler
================================================

Main configuration classes for browser operations.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..exceptions.errors import ConfigurationError


@dataclass
class BrowserConfig:
    """Configuration for browser operations."""
    
    # Core settings (essential only - undetected ChromeDriver handles the rest)
    headless: bool = True
    data_folder: str = field(default_factory=lambda: os.path.join(os.getcwd(), "data"))

    # Performance settings
    page_timeout: int = 30000  # milliseconds

    # Proxy settings
    proxy: Optional['ProxyConfig'] = None

    # Image settings
    download_images: bool = False
    image_web_prefix: Optional[str] = None

    # Legacy compatibility (with sensible defaults - undetected ChromeDriver manages these)
    browser_type: str = "chromium"  # Not used by undetected ChromeDriver but kept for compatibility
    channel: str = "chrome"  # Not used by undetected ChromeDriver but kept for compatibility
    max_sessions: int = 10  # Not used by undetected ChromeDriver but kept for compatibility
    session_timeout_hours: int = 24  # Not used by undetected ChromeDriver but kept for compatibility
    fetch_limit: int = 1000  # Not used by undetected ChromeDriver but kept for compatibility
    cache_expiry: int = 3600  # Not used by undetected ChromeDriver but kept for compatibility
    stealth_mode: bool = True  # Not used by undetected ChromeDriver but kept for compatibility
    user_agent: Optional[str] = None  # Not used by undetected ChromeDriver but kept for compatibility
    browser_args: List[str] = field(default_factory=list)  # Not used by undetected ChromeDriver but kept for compatibility
    viewport_size: Optional[Dict[str, int]] = None  # Not used by undetected ChromeDriver but kept for compatibility
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self):
        """Validate configuration values."""
        if self.max_sessions <= 0:
            raise ConfigurationError("max_sessions must be positive")
        
        if self.fetch_limit <= 0:
            raise ConfigurationError("fetch_limit must be positive")
        
        if self.cache_expiry < 0:
            raise ConfigurationError("cache_expiry must be non-negative")
        
        if self.page_timeout <= 0:
            raise ConfigurationError("page_timeout must be positive")
        
        if self.browser_type not in ["chromium", "firefox", "webkit"]:
            raise ConfigurationError(f"Invalid browser_type: {self.browser_type}")
        
        # Ensure data folder exists
        os.makedirs(self.data_folder, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {
            'headless': self.headless,
            'data_folder': self.data_folder,
            'page_timeout': self.page_timeout,
            'download_images': self.download_images,
            'image_web_prefix': self.image_web_prefix,
            # Legacy compatibility attributes (not used by undetected ChromeDriver)
            'browser_type': self.browser_type,
            'channel': self.channel,
            'max_sessions': self.max_sessions,
            'session_timeout_hours': self.session_timeout_hours,
            'fetch_limit': self.fetch_limit,
            'cache_expiry': self.cache_expiry,
            'stealth_mode': self.stealth_mode,
            'user_agent': self.user_agent,
            'browser_args': self.browser_args,
            'viewport_size': self.viewport_size
        }
        
        if self.proxy:
            result['proxy'] = self.proxy.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BrowserConfig':
        """Create configuration from dictionary."""
        proxy_config = config_dict.pop('proxy', None)
        if proxy_config:
            from .proxy_config import ProxyConfig
            proxy_config = ProxyConfig.from_dict(proxy_config)
        
        return cls(proxy=proxy_config, **config_dict)
    
    @classmethod
    def from_env(cls) -> 'BrowserConfig':
        """Create simplified configuration from environment variables."""
        config = cls()

        # Core settings (undetected ChromeDriver handles browser type, channel, stealth automatically)
        config.headless = os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true'
        config.data_folder = os.getenv('BROWSER_DATA_FOLDER', config.data_folder)

        # Performance settings
        config.page_timeout = int(os.getenv('BROWSER_PAGE_TIMEOUT', '30000'))

        # Image settings
        config.download_images = os.getenv('BROWSER_DOWNLOAD_IMAGES', 'false').lower() == 'true'
        config.image_web_prefix = os.getenv('BROWSER_IMAGE_WEB_PREFIX')

        # Proxy configuration
        if os.getenv('PROXY_ENABLED', 'false').lower() == 'true':
            from .proxy_config import ProxyConfig
            config.proxy = ProxyConfig.from_env()
        
        config.validate()
        return config
    
    def get_browser_launch_options(self) -> Dict[str, Any]:
        """Get simplified browser launch options - undetected ChromeDriver handles stealth automatically."""
        return {
            'headless': self.headless
            # Note: undetected ChromeDriver automatically handles:
            # - Channel selection (uses best available Chrome)
            # - Stealth arguments (automation hiding)
            # - Browser arguments (optimal defaults)
        }
    
    def get_context_options(self, user_data_dir: str = None, proxy_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get simplified browser context options - undetected ChromeDriver handles most automatically."""
        options = {}

        if user_data_dir:
            options['user_data_dir'] = user_data_dir

        if proxy_config:
            options['proxy'] = proxy_config

        # Note: undetected ChromeDriver automatically handles:
        # - Viewport size (realistic defaults)
        # - User agent (realistic, rotating agents)
        # - Context fingerprinting (automatic)

        return options


@dataclass
class CrawlResult:
    """Result of a crawl operation."""
    
    url: str
    html: str
    title: str = ""
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    images: List[Dict[str, str]] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'url': self.url,
            'html': self.html,
            'title': self.title,
            'success': self.success,
            'error': self.error,
            'metadata': self.metadata,
            'images': self.images,
            'links': self.links,
            'timestamp': self.timestamp
        }
