"""
Proxy Configuration for Multi-Browser Crawler
=============================================

Configuration classes for proxy management.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..exceptions.errors import ConfigurationError


@dataclass
class ProxyConfig:
    """Configuration for proxy operations."""
    
    # Basic settings
    enabled: bool = False
    proxy_file: str = "proxies.txt"
    allow_direct_connection: bool = True
    
    # Rotation settings
    recycle_threshold: float = 0.5  # Recycle when 50% of proxies fail
    max_recycle_attempts: int = 3
    
    # Health monitoring
    test_timeout: int = 10  # seconds
    test_url: str = "https://httpbin.org/ip"
    max_concurrent_tests: int = 10
    
    # Circuit breaker settings
    failure_threshold: int = 5
    recovery_timeout: int = 300  # seconds
    
    # Recovery settings
    recovery_cooldown: int = 600  # seconds (10 minutes)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self):
        """Validate configuration values."""
        if self.recycle_threshold < 0 or self.recycle_threshold > 1:
            raise ConfigurationError("recycle_threshold must be between 0 and 1")
        
        if self.max_recycle_attempts < 0:
            raise ConfigurationError("max_recycle_attempts must be non-negative")
        
        if self.test_timeout <= 0:
            raise ConfigurationError("test_timeout must be positive")
        
        if self.max_concurrent_tests <= 0:
            raise ConfigurationError("max_concurrent_tests must be positive")
        
        if self.failure_threshold <= 0:
            raise ConfigurationError("failure_threshold must be positive")
        
        if self.recovery_timeout <= 0:
            raise ConfigurationError("recovery_timeout must be positive")
        
        if self.recovery_cooldown <= 0:
            raise ConfigurationError("recovery_cooldown must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'enabled': self.enabled,
            'proxy_file': self.proxy_file,
            'allow_direct_connection': self.allow_direct_connection,
            'recycle_threshold': self.recycle_threshold,
            'max_recycle_attempts': self.max_recycle_attempts,
            'test_timeout': self.test_timeout,
            'test_url': self.test_url,
            'max_concurrent_tests': self.max_concurrent_tests,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout,
            'recovery_cooldown': self.recovery_cooldown
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ProxyConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls) -> 'ProxyConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Basic settings
        config.enabled = os.getenv('PROXY_ENABLED', 'false').lower() == 'true'
        config.proxy_file = os.getenv('PROXY_FILE', 'proxies.txt')
        config.allow_direct_connection = os.getenv('PROXY_ALLOW_DIRECT', 'true').lower() == 'true'
        
        # Rotation settings
        config.recycle_threshold = float(os.getenv('PROXY_RECYCLE_THRESHOLD', '0.5'))
        config.max_recycle_attempts = int(os.getenv('PROXY_MAX_RECYCLE_ATTEMPTS', '3'))
        
        # Health monitoring
        config.test_timeout = int(os.getenv('PROXY_TEST_TIMEOUT', '10'))
        config.test_url = os.getenv('PROXY_TEST_URL', 'https://httpbin.org/ip')
        config.max_concurrent_tests = int(os.getenv('PROXY_MAX_CONCURRENT_TESTS', '10'))
        
        # Circuit breaker settings
        config.failure_threshold = int(os.getenv('PROXY_FAILURE_THRESHOLD', '5'))
        config.recovery_timeout = int(os.getenv('PROXY_RECOVERY_TIMEOUT', '300'))
        
        # Recovery settings
        config.recovery_cooldown = int(os.getenv('PROXY_RECOVERY_COOLDOWN', '600'))
        
        config.validate()
        return config
    
    def get_proxy_manager_config(self) -> Dict[str, Any]:
        """Get configuration for ProxyManager initialization."""
        return {
            'proxy_file': self.proxy_file,
            'recycle_threshold': self.recycle_threshold,
            'enabled': self.enabled,
            'allow_direct_connection': self.allow_direct_connection,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout
        }


@dataclass
class BrowserLaunchConfig:
    """Configuration for browser launch options."""
    
    # Browser executable
    executable_path: Optional[str] = None
    
    # Launch options
    headless: bool = True
    devtools: bool = False
    slow_mo: int = 0  # milliseconds
    
    # Window options
    args: list = None
    ignore_default_args: list = None
    ignore_https_errors: bool = False
    
    # Download options
    downloads_path: Optional[str] = None
    
    # Environment
    env: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.args is None:
            self.args = []
        if self.ignore_default_args is None:
            self.ignore_default_args = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {
            'headless': self.headless,
            'devtools': self.devtools,
            'slow_mo': self.slow_mo,
            'args': self.args,
            'ignore_default_args': self.ignore_default_args,
            'ignore_https_errors': self.ignore_https_errors
        }
        
        if self.executable_path:
            result['executable_path'] = self.executable_path
        
        if self.downloads_path:
            result['downloads_path'] = self.downloads_path
        
        if self.env:
            result['env'] = self.env
        
        return result
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BrowserLaunchConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls) -> 'BrowserLaunchConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        config.executable_path = os.getenv('BROWSER_EXECUTABLE_PATH')
        config.headless = os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true'
        config.devtools = os.getenv('BROWSER_DEVTOOLS', 'false').lower() == 'true'
        config.slow_mo = int(os.getenv('BROWSER_SLOW_MO', '0'))
        config.ignore_https_errors = os.getenv('BROWSER_IGNORE_HTTPS_ERRORS', 'false').lower() == 'true'
        config.downloads_path = os.getenv('BROWSER_DOWNLOADS_PATH')
        
        # Parse browser args
        browser_args = os.getenv('BROWSER_ARGS', '')
        if browser_args:
            config.args = [arg.strip() for arg in browser_args.split(',')]
        
        # Parse ignore default args
        ignore_args = os.getenv('BROWSER_IGNORE_DEFAULT_ARGS', '')
        if ignore_args:
            config.ignore_default_args = [arg.strip() for arg in ignore_args.split(',')]
        
        return config


@dataclass
class ContextConfig:
    """Configuration for browser context options."""
    
    # Viewport
    viewport: Optional[Dict[str, int]] = None
    no_viewport: bool = False
    
    # User agent
    user_agent: Optional[str] = None
    
    # Locale and timezone
    locale: Optional[str] = None
    timezone_id: Optional[str] = None
    
    # Permissions
    permissions: list = None
    geolocation: Optional[Dict[str, float]] = None
    
    # Media
    color_scheme: Optional[str] = None  # 'light', 'dark', 'no-preference'
    reduced_motion: Optional[str] = None  # 'reduce', 'no-preference'
    
    # Storage
    storage_state: Optional[str] = None
    
    # HTTP credentials
    http_credentials: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.permissions is None:
            self.permissions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {
            'no_viewport': self.no_viewport,
            'permissions': self.permissions
        }
        
        if self.viewport:
            result['viewport'] = self.viewport
        
        if self.user_agent:
            result['user_agent'] = self.user_agent
        
        if self.locale:
            result['locale'] = self.locale
        
        if self.timezone_id:
            result['timezone_id'] = self.timezone_id
        
        if self.geolocation:
            result['geolocation'] = self.geolocation
        
        if self.color_scheme:
            result['color_scheme'] = self.color_scheme
        
        if self.reduced_motion:
            result['reduced_motion'] = self.reduced_motion
        
        if self.storage_state:
            result['storage_state'] = self.storage_state
        
        if self.http_credentials:
            result['http_credentials'] = self.http_credentials
        
        return result
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ContextConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
