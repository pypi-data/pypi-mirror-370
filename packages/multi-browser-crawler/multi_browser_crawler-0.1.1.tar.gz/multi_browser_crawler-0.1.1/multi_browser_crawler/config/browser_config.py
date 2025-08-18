"""
Browser Launch Configuration for Multi-Browser Crawler
======================================================

Specific configuration for browser launch and context options.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..exceptions.errors import ConfigurationError


@dataclass
class BrowserLaunchConfig:
    """Simplified configuration for browser launch - undetected ChromeDriver handles most options automatically."""

    # Essential options only
    headless: bool = True
    timeout: int = 30000  # milliseconds

    # Optional download path
    downloads_path: Optional[str] = None

    # Note: undetected ChromeDriver automatically handles:
    # - Browser executable (auto-detects and downloads)
    # - Launch arguments (optimal stealth configuration)
    # - Window options (realistic defaults)
    # - Environment variables (proper isolation)
    
    def validate(self):
        """Validate essential configuration values."""
        if self.timeout <= 0:
            raise ConfigurationError("timeout must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {
            'headless': self.headless,
            'devtools': self.devtools,
            'slow_mo': self.slow_mo,
            'args': self.args,
            'ignore_default_args': self.ignore_default_args,
            'ignore_https_errors': self.ignore_https_errors,
            'timeout': self.timeout
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
        config.timeout = int(os.getenv('BROWSER_TIMEOUT', '30000'))
        
        # Parse browser args
        browser_args = os.getenv('BROWSER_ARGS', '')
        if browser_args:
            config.args = [arg.strip() for arg in browser_args.split(',')]
        
        # Parse ignore default args
        ignore_args = os.getenv('BROWSER_IGNORE_DEFAULT_ARGS', '')
        if ignore_args:
            config.ignore_default_args = [arg.strip() for arg in ignore_args.split(',')]
        
        config.validate()
        return config
    
    def get_stealth_args(self) -> List[str]:
        """Get stealth arguments for anti-detection."""
        return [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection'
        ]
    
    def get_performance_args(self) -> List[str]:
        """Get performance optimization arguments."""
        return [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-gpu'
        ]


@dataclass
class ContextConfig:
    """Simplified configuration for browser context - undetected ChromeDriver handles most automatically."""

    # Essential options only
    storage_state: Optional[str] = None
    http_credentials: Optional[Dict[str, str]] = None
    extra_http_headers: Optional[Dict[str, str]] = None

    # Note: undetected ChromeDriver automatically handles:
    # - Viewport (realistic, rotating sizes)
    # - User agent (realistic, rotating agents)
    # - Locale and timezone (based on proxy location)
    # - Permissions (optimal defaults)
    # - Media preferences (realistic defaults)
    # - Geolocation (proxy-based when applicable)
    
    def validate(self):
        """Validate essential configuration values."""
        # Most validation is handled by undetected ChromeDriver
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert simplified configuration to dictionary."""
        result = {}

        if self.storage_state:
            result['storage_state'] = self.storage_state

        if self.http_credentials:
            result['http_credentials'] = self.http_credentials

        if self.extra_http_headers:
            result['extra_http_headers'] = self.extra_http_headers

        return result
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ContextConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls) -> 'ContextConfig':
        """Create simplified configuration from environment variables."""
        config = cls()

        # Only essential configuration - undetected ChromeDriver handles the rest
        config.storage_state = os.getenv('BROWSER_STORAGE_STATE')

        # HTTP credentials if needed
        username = os.getenv('BROWSER_HTTP_USERNAME')
        password = os.getenv('BROWSER_HTTP_PASSWORD')
        if username and password:
            config.http_credentials = {'username': username, 'password': password}
        
        config.validate()
        return config
