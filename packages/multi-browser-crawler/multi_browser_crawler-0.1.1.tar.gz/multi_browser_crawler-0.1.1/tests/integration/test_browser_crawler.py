"""
Integration tests for BrowserCrawler.
"""

import pytest
import asyncio
import tempfile
import os

from multi_browser_crawler import BrowserCrawler, BrowserConfig
from multi_browser_crawler.config.settings import CrawlResult


@pytest.mark.integration
@pytest.mark.browser
class TestBrowserCrawlerIntegration:
    """Integration tests for BrowserCrawler."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=2,
                data_folder=temp_dir,
                fetch_limit=10
            )
    
    @pytest.mark.asyncio
    async def test_simple_fetch(self, config):
        """Test simple page fetch."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch("https://httpbin.org/html")
            
            assert isinstance(result, CrawlResult)
            assert result.success is True
            assert result.url == "https://httpbin.org/html"
            assert len(result.html) > 0
            assert result.error is None
    
    @pytest.mark.asyncio
    async def test_fetch_with_content(self, config):
        """Test fetch with content extraction."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch("https://httpbin.org/html")

            assert result.success is True
            assert len(result.html) > 0
            assert "Herman Melville" in result.html

    @pytest.mark.asyncio
    async def test_fetch_with_advanced_cleanup(self, config):
        """Test fetch with advanced JavaScript cleanup."""
        async with BrowserCrawler(config) as crawler:
            # Fetch with HTML cleaning enabled
            result = await crawler.fetch("https://httpbin.org/html", clean_html=True)

            assert result.success is True
            assert len(result.html) > 0
            # HTML should be cleaned (scripts, styles removed)
            assert '<script>' not in result.html.lower()
            assert '<style>' not in result.html.lower()

    @pytest.mark.asyncio
    async def test_javascript_execution(self, config):
        """Test JavaScript execution functionality."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.execute_js(
                "https://httpbin.org/html",
                "return document.title || 'No Title'"
            )

            assert result.get("success") is True
            assert "result" in result
            assert isinstance(result["result"], str)
    
    @pytest.mark.asyncio
    async def test_fetch_invalid_url(self, config):
        """Test fetch with invalid URL."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch("https://invalid-domain-that-does-not-exist.com")
            
            assert isinstance(result, CrawlResult)
            assert result.success is False
            assert result.error is not None
            assert len(result.html) == 0
    
    @pytest.mark.asyncio
    async def test_batch_fetch(self, config):
        """Test batch fetching."""
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        async with BrowserCrawler(config) as crawler:
            results = await crawler.fetch_batch(urls, max_concurrent=2)
            
            assert len(results) == 3
            assert all(isinstance(r, CrawlResult) for r in results)
            
            # At least some should be successful
            successful = [r for r in results if r.success]
            assert len(successful) > 0
    
    @pytest.mark.asyncio
    async def test_javascript_execution(self, config):
        """Test JavaScript execution."""
        js_code = """
        (() => {
            return {
                title: document.title,
                url: window.location.href,
                userAgent: navigator.userAgent
            };
        })()
        """

        async with BrowserCrawler(config) as crawler:
            result = await crawler.execute_js("https://httpbin.org/html", js_code)

            assert result['success'] is True
            assert result['url'] == "https://httpbin.org/html"
            assert isinstance(result['result'], dict)
            assert 'title' in result['result']
            assert 'url' in result['result']
            assert 'userAgent' in result['result']
    
    @pytest.mark.asyncio
    async def test_fetch_with_javascript(self, config):
        """Test fetch with JavaScript execution."""
        js_code = "(() => { document.title = 'Modified Title'; return document.title; })()"

        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch(
                "https://httpbin.org/html",
                execute_js=js_code
            )

            assert result.success is True
            assert result.metadata['js_result'] == 'Modified Title'
    
    @pytest.mark.asyncio
    async def test_session_isolation(self, config):
        """Test that different sessions are isolated."""
        async with BrowserCrawler(config) as crawler:
            # Fetch with session 1
            result1 = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="session1"
            )
            
            # Fetch with session 2
            result2 = await crawler.fetch(
                "https://httpbin.org/html", 
                session_name="session2"
            )
            
            assert result1.success is True
            assert result2.success is True
            
            # Sessions should have different IDs
            assert result1.metadata['session_id'] != result2.metadata['session_id']
    
    @pytest.mark.asyncio
    async def test_crawler_stats(self, config):
        """Test crawler statistics."""
        async with BrowserCrawler(config) as crawler:
            # Fetch a page to generate some stats
            await crawler.fetch("https://httpbin.org/html")
            
            stats = await crawler.get_stats()
            
            assert isinstance(stats, dict)
            assert 'total_sessions' in stats
            assert 'active_sessions' in stats
            assert 'fetch_count' in stats
            assert stats['fetch_count'] > 0
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, config):
        """Test HTML caching functionality."""
        async with BrowserCrawler(config) as crawler:
            # First fetch (should cache)
            result1 = await crawler.fetch(
                "https://httpbin.org/html",
                use_cache=True
            )
            
            # Second fetch (should use cache)
            result2 = await crawler.fetch(
                "https://httpbin.org/html",
                use_cache=True
            )
            
            assert result1.success is True
            assert result2.success is True
            assert result1.html == result2.html
    
    @pytest.mark.asyncio
    async def test_error_handling(self, config):
        """Test error handling in various scenarios."""
        async with BrowserCrawler(config) as crawler:
            # Test invalid JavaScript
            result = await crawler.execute_js(
                "https://httpbin.org/html",
                "invalid javascript syntax!!!"
            )
            
            assert result['success'] is False
            assert result['error'] is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, config):
        """Test concurrent operations with multiple sessions."""
        async def fetch_with_session(crawler, session_name, url):
            return await crawler.fetch(url, session_name=session_name)
        
        async with BrowserCrawler(config) as crawler:
            # Create multiple concurrent tasks
            tasks = [
                fetch_with_session(crawler, f"session_{i}", "https://httpbin.org/html")
                for i in range(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all(r.success for r in results)
            
            # All should have different session IDs
            session_ids = [r.metadata['session_id'] for r in results]
            assert len(set(session_ids)) == 3


@pytest.mark.integration
@pytest.mark.browser
class TestBrowserCrawlerConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_convenience_fetch(self):
        """Test convenience fetch function."""
        from multi_browser_crawler import fetch
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BrowserConfig(headless=True, data_folder=temp_dir)
            result = await fetch("https://httpbin.org/html", config)
            
            assert isinstance(result, CrawlResult)
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_convenience_fetch_batch(self):
        """Test convenience fetch_batch function."""
        from multi_browser_crawler import fetch_batch
        
        urls = ["https://httpbin.org/html", "https://httpbin.org/json"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BrowserConfig(headless=True, data_folder=temp_dir)
            results = await fetch_batch(urls, config)
            
            assert len(results) == 2
            assert all(isinstance(r, CrawlResult) for r in results)
