"""
Unit tests for proxy utilities.
"""

import pytest
import tempfile
import os
from unittest.mock import AsyncMock, patch

from multi_browser_crawler.utils.proxy_utils import ProxyValidator, ProxyTester
from multi_browser_crawler.exceptions.errors import ProxyError


class TestProxyValidator:
    """Test ProxyValidator class."""
    
    def test_validate_proxy_format_valid(self):
        """Test validation of valid proxy formats."""
        valid_proxies = [
            "127.0.0.1:8080",
            "proxy.example.com:3128",
            "192.168.1.1:8888",
            "user:pass@proxy.example.com:8080",
            "username:password123@127.0.0.1:3128"
        ]
        
        for proxy in valid_proxies:
            assert ProxyValidator.validate_proxy_format(proxy), f"Should be valid: {proxy}"
    
    def test_validate_proxy_format_invalid(self):
        """Test validation of invalid proxy formats."""
        invalid_proxies = [
            "",
            None,
            "invalid",
            "127.0.0.1",
            ":8080",
            "127.0.0.1:",
            "127.0.0.1:abc",
            "user@proxy.com:8080",  # Missing password
            "@proxy.com:8080",      # Missing username
        ]
        
        for proxy in invalid_proxies:
            assert not ProxyValidator.validate_proxy_format(proxy), f"Should be invalid: {proxy}"
    
    def test_parse_proxy_basic(self):
        """Test parsing basic proxy format."""
        proxy = "127.0.0.1:8080"
        parsed = ProxyValidator.parse_proxy(proxy)
        
        assert parsed['host'] == "127.0.0.1"
        assert parsed['port'] == 8080
        assert parsed['username'] is None
        assert parsed['password'] is None
    
    def test_parse_proxy_with_auth(self):
        """Test parsing proxy with authentication."""
        proxy = "user:pass@proxy.example.com:3128"
        parsed = ProxyValidator.parse_proxy(proxy)
        
        assert parsed['host'] == "proxy.example.com"
        assert parsed['port'] == 3128
        assert parsed['username'] == "user"
        assert parsed['password'] == "pass"
    
    def test_parse_proxy_invalid(self):
        """Test parsing invalid proxy raises error."""
        with pytest.raises(ProxyError):
            ProxyValidator.parse_proxy("invalid_proxy")
    
    def test_format_proxy_for_playwright_basic(self):
        """Test formatting proxy for Playwright (basic)."""
        proxy = "127.0.0.1:8080"
        config = ProxyValidator.format_proxy_for_playwright(proxy)
        
        assert config['server'] == "http://127.0.0.1:8080"
        assert 'username' not in config
        assert 'password' not in config
    
    def test_format_proxy_for_playwright_with_auth(self):
        """Test formatting proxy for Playwright (with auth)."""
        proxy = "user:pass@proxy.example.com:3128"
        config = ProxyValidator.format_proxy_for_playwright(proxy)
        
        assert config['server'] == "http://proxy.example.com:3128"
        assert config['username'] == "user"
        assert config['password'] == "pass"


class TestProxyTester:
    """Test ProxyTester class."""
    
    def test_init(self):
        """Test ProxyTester initialization."""
        tester = ProxyTester(timeout=15)
        
        assert tester.timeout == 15
        assert isinstance(tester.test_urls, list)
        assert len(tester.test_urls) > 0
    
    @pytest.mark.asyncio
    async def test_test_proxy_invalid_format(self):
        """Test testing proxy with invalid format."""
        tester = ProxyTester()
        result = await tester.test_proxy("invalid_proxy")
        
        assert result['proxy'] == "invalid_proxy"
        assert result['success'] is False
        assert result['error'] == "Invalid proxy format"
        assert result['response_time'] is None
        assert result['ip_address'] is None
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_test_proxy_success(self, mock_get):
        """Test successful proxy testing."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"origin": "1.2.3.4"}
        mock_get.return_value.__aenter__.return_value = mock_response
        
        tester = ProxyTester()
        result = await tester.test_proxy("127.0.0.1:8080")
        
        assert result['proxy'] == "127.0.0.1:8080"
        assert result['success'] is True
        assert result['error'] is None
        assert result['ip_address'] == "1.2.3.4"
        assert result['status_code'] == 200
        assert isinstance(result['response_time'], float)
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_test_proxy_http_error(self, mock_get):
        """Test proxy testing with HTTP error."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_get.return_value.__aenter__.return_value = mock_response
        
        tester = ProxyTester()
        result = await tester.test_proxy("127.0.0.1:8080")
        
        assert result['proxy'] == "127.0.0.1:8080"
        assert result['success'] is False
        assert result['error'] == "HTTP 403"
        assert result['status_code'] == 403
    
    @pytest.mark.asyncio
    async def test_test_proxies_batch(self):
        """Test batch proxy testing."""
        tester = ProxyTester()
        
        # Mock the test_proxy method
        async def mock_test_proxy(proxy):
            return {
                'proxy': proxy,
                'success': proxy == "good_proxy:8080",
                'error': None if proxy == "good_proxy:8080" else "Connection failed",
                'response_time': 0.5 if proxy == "good_proxy:8080" else None,
                'ip_address': "1.2.3.4" if proxy == "good_proxy:8080" else None
            }
        
        tester.test_proxy = mock_test_proxy
        
        proxies = ["good_proxy:8080", "bad_proxy:8080", "another_bad:8080"]
        results = await tester.test_proxies(proxies, max_concurrent=2)
        
        assert len(results) == 3
        assert results[0]['success'] is True
        assert results[1]['success'] is False
        assert results[2]['success'] is False
    
    @pytest.mark.asyncio
    async def test_find_working_proxies(self):
        """Test finding working proxies."""
        tester = ProxyTester()
        
        # Mock the test_proxies method
        async def mock_test_proxies(proxies, max_concurrent):
            return [
                {'proxy': 'good1:8080', 'success': True},
                {'proxy': 'bad1:8080', 'success': False},
                {'proxy': 'good2:8080', 'success': True},
                {'proxy': 'bad2:8080', 'success': False}
            ]
        
        tester.test_proxies = mock_test_proxies
        
        proxies = ["good1:8080", "bad1:8080", "good2:8080", "bad2:8080"]
        working = await tester.find_working_proxies(proxies)
        
        assert len(working) == 2
        assert "good1:8080" in working
        assert "good2:8080" in working
    
    def test_load_proxies_from_file(self):
        """Test loading proxies from file."""
        tester = ProxyTester()
        
        # Create temporary proxy file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("# This is a comment\n")
            f.write("127.0.0.1:8080\n")
            f.write("proxy.example.com:3128\n")
            f.write("\n")  # Empty line
            f.write("user:pass@proxy2.example.com:8080\n")
            f.write("invalid_proxy\n")  # Invalid format
            temp_file = f.name
        
        try:
            proxies = tester.load_proxies_from_file(temp_file)
            
            assert len(proxies) == 3  # Only valid proxies
            assert "127.0.0.1:8080" in proxies
            assert "proxy.example.com:3128" in proxies
            assert "user:pass@proxy2.example.com:8080" in proxies
            assert "invalid_proxy" not in proxies
            
        finally:
            os.unlink(temp_file)
    
    def test_load_proxies_from_nonexistent_file(self):
        """Test loading proxies from non-existent file."""
        tester = ProxyTester()
        proxies = tester.load_proxies_from_file("nonexistent_file.txt")
        
        assert proxies == []
