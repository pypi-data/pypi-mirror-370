"""
Unit tests for configuration classes.
"""

import pytest
import os
import tempfile
from unittest.mock import patch

from multi_browser_crawler.config.settings import BrowserConfig, CrawlResult
from multi_browser_crawler.config.proxy_config import ProxyConfig
from multi_browser_crawler.exceptions.errors import ConfigurationError


class TestBrowserConfig:
    """Test BrowserConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = BrowserConfig()
        
        assert config.headless is True
        assert config.browser_type == "chromium"
        assert config.max_sessions == 10
        assert config.fetch_limit == 1000
        assert config.cache_expiry == 3600
        assert config.stealth_mode is True
        assert config.download_images is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = BrowserConfig(
            headless=False,
            max_sessions=5,
            fetch_limit=500,
            stealth_mode=False
        )
        
        assert config.headless is False
        assert config.max_sessions == 5
        assert config.fetch_limit == 500
        assert config.stealth_mode is False
    
    def test_validation_errors(self):
        """Test configuration validation errors."""
        with pytest.raises(ConfigurationError):
            BrowserConfig(max_sessions=0)
        
        with pytest.raises(ConfigurationError):
            BrowserConfig(fetch_limit=-1)
        
        with pytest.raises(ConfigurationError):
            BrowserConfig(cache_expiry=-1)
        
        with pytest.raises(ConfigurationError):
            BrowserConfig(browser_type="invalid")
    
    def test_to_dict(self):
        """Test configuration to dictionary conversion."""
        config = BrowserConfig(headless=False, max_sessions=5)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['headless'] is False
        assert config_dict['max_sessions'] == 5
        assert 'browser_type' in config_dict
    
    def test_from_dict(self):
        """Test configuration from dictionary creation."""
        config_dict = {
            'headless': False,
            'max_sessions': 5,
            'fetch_limit': 500
        }
        
        config = BrowserConfig.from_dict(config_dict)
        
        assert config.headless is False
        assert config.max_sessions == 5
        assert config.fetch_limit == 500
    
    @patch.dict(os.environ, {
        'BROWSER_HEADLESS': 'false',
        'BROWSER_MAX_SESSIONS': '5',
        'BROWSER_FETCH_LIMIT': '500'
    })
    def test_from_env(self):
        """Test configuration from environment variables."""
        config = BrowserConfig.from_env()
        
        assert config.headless is False
        assert config.max_sessions == 5
        assert config.fetch_limit == 500
    
    def test_browser_launch_options(self):
        """Test browser launch options generation."""
        config = BrowserConfig(stealth_mode=True)
        options = config.get_browser_launch_options()
        
        assert isinstance(options, dict)
        assert 'headless' in options
        assert 'args' in options
        assert any('--disable-blink-features=AutomationControlled' in arg for arg in options['args'])
    
    def test_context_options(self):
        """Test browser context options generation."""
        config = BrowserConfig()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            options = config.get_context_options(user_data_dir=temp_dir)
            
            assert isinstance(options, dict)
            assert options['user_data_dir'] == temp_dir


class TestProxyConfig:
    """Test ProxyConfig class."""
    
    def test_default_config(self):
        """Test default proxy configuration."""
        config = ProxyConfig()
        
        assert config.enabled is False
        assert config.proxy_file == "proxies.txt"
        assert config.allow_direct_connection is True
        assert config.recycle_threshold == 0.5
        assert config.test_timeout == 10
    
    def test_custom_config(self):
        """Test custom proxy configuration."""
        config = ProxyConfig(
            enabled=True,
            proxy_file="custom_proxies.txt",
            recycle_threshold=0.7,
            test_timeout=15
        )
        
        assert config.enabled is True
        assert config.proxy_file == "custom_proxies.txt"
        assert config.recycle_threshold == 0.7
        assert config.test_timeout == 15
    
    def test_validation_errors(self):
        """Test proxy configuration validation errors."""
        with pytest.raises(ConfigurationError):
            ProxyConfig(recycle_threshold=-0.1)
        
        with pytest.raises(ConfigurationError):
            ProxyConfig(recycle_threshold=1.1)
        
        with pytest.raises(ConfigurationError):
            ProxyConfig(test_timeout=0)
        
        with pytest.raises(ConfigurationError):
            ProxyConfig(max_concurrent_tests=0)
    
    def test_to_dict(self):
        """Test proxy configuration to dictionary conversion."""
        config = ProxyConfig(enabled=True, test_timeout=15)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['enabled'] is True
        assert config_dict['test_timeout'] == 15
    
    def test_from_dict(self):
        """Test proxy configuration from dictionary creation."""
        config_dict = {
            'enabled': True,
            'proxy_file': 'test_proxies.txt',
            'test_timeout': 15
        }
        
        config = ProxyConfig.from_dict(config_dict)
        
        assert config.enabled is True
        assert config.proxy_file == 'test_proxies.txt'
        assert config.test_timeout == 15
    
    @patch.dict(os.environ, {
        'PROXY_ENABLED': 'true',
        'PROXY_FILE': 'env_proxies.txt',
        'PROXY_TEST_TIMEOUT': '15'
    })
    def test_from_env(self):
        """Test proxy configuration from environment variables."""
        config = ProxyConfig.from_env()
        
        assert config.enabled is True
        assert config.proxy_file == 'env_proxies.txt'
        assert config.test_timeout == 15
    
    def test_proxy_manager_config(self):
        """Test proxy manager configuration generation."""
        config = ProxyConfig(enabled=True, recycle_threshold=0.7)
        manager_config = config.get_proxy_manager_config()
        
        assert isinstance(manager_config, dict)
        assert manager_config['enabled'] is True
        assert manager_config['recycle_threshold'] == 0.7


class TestCrawlResult:
    """Test CrawlResult class."""
    
    def test_default_result(self):
        """Test default crawl result."""
        result = CrawlResult(url="https://example.com", html="<html></html>")
        
        assert result.url == "https://example.com"
        assert result.html == "<html></html>"
        assert result.success is True
        assert result.error is None
        assert isinstance(result.metadata, dict)
        assert isinstance(result.images, list)
        assert isinstance(result.timestamp, float)
    
    def test_error_result(self):
        """Test error crawl result."""
        result = CrawlResult(
            url="https://example.com",
            html="",
            success=False,
            error="Connection failed"
        )
        
        assert result.success is False
        assert result.error == "Connection failed"
    
    def test_to_dict(self):
        """Test crawl result to dictionary conversion."""
        result = CrawlResult(
            url="https://example.com",
            html="<html></html>",
            title="Test Page"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['url'] == "https://example.com"
        assert result_dict['html'] == "<html></html>"
        assert result_dict['title'] == "Test Page"
        assert result_dict['success'] is True
