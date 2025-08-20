"""
Configuration for Multi-Browser Crawler
=======================================

Simple configuration for browser operations.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BrowserConfig:
    """Configuration for browser operations."""
    
    # Core settings
    headless: bool = True
    timeout: int = 30  # seconds (converted to milliseconds internally)
    
    # Required paths - must be provided by caller
    browser_data_dir: str = "tmp/browser-data"  # Browser sessions and profiles
    
    # Optional paths
    download_images_dir: Optional[str] = None  # Image downloads
    proxy_file_path: Optional[str] = None  # Proxy file
    
    # Browser pool settings
    min_browsers: int = 1
    max_browsers: int = 5
    idle_timeout: int = 300  # seconds
    
    # Debug port range
    debug_port_start: int = 9222
    debug_port_end: int = 9322
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self):
        """Validate configuration values."""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        if self.min_browsers < 1:
            raise ValueError("min_browsers must be at least 1")
        
        if self.max_browsers < self.min_browsers:
            raise ValueError("max_browsers must be >= min_browsers")
        
        if self.idle_timeout <= 0:
            raise ValueError("idle_timeout must be positive")
        
        if self.debug_port_start <= 0 or self.debug_port_end <= 0:
            raise ValueError("debug ports must be positive")
        
        if self.debug_port_end <= self.debug_port_start:
            raise ValueError("debug_port_end must be > debug_port_start")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility."""
        return {
            'HEADLESS': self.headless,
            'BROWSER_TIMEOUT': self.timeout * 1000,  # Convert to milliseconds
            'BROWSER_DATA_DIR': self.browser_data_dir,
            'DOWNLOAD_IMAGES_DIR': self.download_images_dir,
            'PROXY_FILE_PATH': self.proxy_file_path,
            'MIN_BROWSERS': self.min_browsers,
            'MAX_BROWSERS': self.max_browsers,
            'IDLE_TIMEOUT': self.idle_timeout,
            'DEBUG_PORT_START': self.debug_port_start,
            'DEBUG_PORT_END': self.debug_port_end,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BrowserConfig':
        """Create from dictionary."""
        return cls(
            headless=config_dict.get('HEADLESS', True),
            timeout=config_dict.get('BROWSER_TIMEOUT', 30000) // 1000,  # Convert from milliseconds
            browser_data_dir=config_dict.get('BROWSER_DATA_DIR', 'tmp/browser-data'),
            download_images_dir=config_dict.get('DOWNLOAD_IMAGES_DIR'),
            proxy_file_path=config_dict.get('PROXY_FILE_PATH'),
            min_browsers=config_dict.get('MIN_BROWSERS', 1),
            max_browsers=config_dict.get('MAX_BROWSERS', 5),
            idle_timeout=config_dict.get('IDLE_TIMEOUT', 300),
            debug_port_start=config_dict.get('DEBUG_PORT_START', 9222),
            debug_port_end=config_dict.get('DEBUG_PORT_END', 9322),
        )
    
    @classmethod
    def from_env(cls) -> 'BrowserConfig':
        """Create configuration from environment variables."""
        return cls(
            headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
            timeout=int(os.getenv('BROWSER_TIMEOUT', '30')),
            browser_data_dir=os.getenv('BROWSER_DATA_DIR', 'tmp/browser-data'),
            download_images_dir=os.getenv('DOWNLOAD_IMAGES_DIR'),
            proxy_file_path=os.getenv('PROXY_FILE_PATH'),
            min_browsers=int(os.getenv('MIN_BROWSERS', '1')),
            max_browsers=int(os.getenv('MAX_BROWSERS', '5')),
            idle_timeout=int(os.getenv('IDLE_TIMEOUT', '300')),
            debug_port_start=int(os.getenv('DEBUG_PORT_START', '9222')),
            debug_port_end=int(os.getenv('DEBUG_PORT_END', '9322')),
        )



