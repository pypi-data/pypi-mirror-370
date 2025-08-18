"""
Comprehensive integration tests covering all spider-mcp functionality.
"""

import pytest
import asyncio
import tempfile
import os
import json

from multi_browser_crawler import BrowserCrawler, BrowserConfig


@pytest.mark.integration
@pytest.mark.browser
class TestComprehensiveFunctionality:
    """Comprehensive tests covering all extracted functionality."""
    
    @pytest.fixture
    def config(self):
        """Create comprehensive test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=5,
                data_folder=temp_dir,
                download_images=True,
                fetch_limit=100,
                stealth_mode=True
            )
    
    @pytest.mark.asyncio
    async def test_basic_html_fetching(self, config):
        """Test basic HTML fetching functionality."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch("https://httpbin.org/html")
            
            assert result.success is True
            assert len(result.html) > 0
            assert result.title is not None
            assert result.url == "https://httpbin.org/html"
            assert isinstance(result.metadata, dict)
            assert isinstance(result.timestamp, float)
    
    @pytest.mark.asyncio
    async def test_javascript_execution_comprehensive(self, config):
        """Test comprehensive JavaScript execution."""
        async with BrowserCrawler(config) as crawler:
            # Test basic JavaScript execution
            js_code = """
            return {
                title: document.title,
                url: window.location.href,
                links: document.querySelectorAll('a').length,
                images: document.querySelectorAll('img').length,
                bodyText: document.body.textContent.substring(0, 100),
                timestamp: Date.now(),
                userAgent: navigator.userAgent.substring(0, 50)
            };
            """
            
            result = await crawler.execute_js("https://httpbin.org/html", js_code)
            
            assert result['success'] is True
            assert isinstance(result['result'], dict)
            
            js_result = result['result']
            assert 'title' in js_result
            assert 'url' in js_result
            assert 'links' in js_result
            assert 'images' in js_result
            assert 'bodyText' in js_result
            assert 'timestamp' in js_result
            assert 'userAgent' in js_result
            
            # Verify data types
            assert isinstance(js_result['links'], int)
            assert isinstance(js_result['images'], int)
            assert isinstance(js_result['timestamp'], int)
    
    @pytest.mark.asyncio
    async def test_fetch_with_javascript_integration(self, config):
        """Test fetch with integrated JavaScript execution."""
        async with BrowserCrawler(config) as crawler:
            js_code = "document.title = 'Modified by JS'; return document.title;"
            
            result = await crawler.fetch(
                "https://httpbin.org/html",
                execute_js=js_code,
                clean_html=True
            )
            
            assert result.success is True
            assert result.metadata['js_result'] == 'Modified by JS'
            assert len(result.html) > 0
    
    @pytest.mark.asyncio
    async def test_api_discovery_comprehensive(self, config):
        """Test comprehensive API discovery functionality."""
        async with BrowserCrawler(config) as crawler:
            # Test with a site that makes API calls
            result = await crawler.discover_apis("https://jsonplaceholder.typicode.com/")
            
            assert isinstance(result, dict)
            assert 'success' in result
            assert 'total_api_calls' in result
            assert 'api_calls' in result
            assert 'api_call_summary' in result
            assert 'discovery_summary' in result
            assert 'usage_hint' in result
            
            if result['success']:
                # Check summary structure
                summary = result['api_call_summary']
                assert 'json_apis' in summary
                assert 'graphql_apis' in summary
                assert 'other_apis' in summary
                
                discovery = result['discovery_summary']
                assert 'domains_found' in discovery
                assert 'methods_used' in discovery
                assert 'content_types' in discovery
                
                # Check data types
                assert isinstance(summary['json_apis'], int)
                assert isinstance(summary['graphql_apis'], int)
                assert isinstance(summary['other_apis'], int)
                assert isinstance(discovery['domains_found'], list)
                assert isinstance(discovery['methods_used'], list)
                assert isinstance(discovery['content_types'], list)
    
    @pytest.mark.asyncio
    async def test_complete_api_response_fetching(self, config):
        """Test complete API response fetching."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch_api_response(
                "json",
                "https://httpbin.org/json"
            )
            
            assert isinstance(result, dict)
            assert 'success' in result
            assert 'pattern' in result
            assert 'page_url' in result
            
            if result['success']:
                assert 'url' in result
                assert 'method' in result
                assert 'status' in result
                assert 'response_data' in result
                assert 'content_type' in result
                
                # Should have captured JSON response
                if result['response_data']:
                    # Could be parsed JSON (dict) or raw text (str)
                    assert isinstance(result['response_data'], (dict, str))
    
    @pytest.mark.asyncio
    async def test_image_download_comprehensive(self, config):
        """Test comprehensive image download functionality."""
        async with BrowserCrawler(config) as crawler:
            # Test image download through fetch
            result = await crawler.fetch(
                "https://httpbin.org/html",
                download_images=True
            )
            
            assert result.success is True
            assert isinstance(result.images, list)
            
            # Test direct image download
            download_result = await crawler.download_images_from_page("https://httpbin.org/html")
            
            assert isinstance(download_result, dict)
            assert 'images' in download_result
            assert 'total_found' in download_result
            assert 'total_downloaded' in download_result
            assert 'success' in download_result
            
            if download_result['success']:
                for image in download_result['images']:
                    assert 'original_url' in image
                    assert 'local_path' in image
                    assert 'web_path' in image
                    
                    # Verify file exists
                    local_path = os.path.join(config.data_folder, image['local_path'])
                    if os.path.exists(local_path):
                        assert os.path.getsize(local_path) > 0
    
    @pytest.mark.asyncio
    async def test_session_management_comprehensive(self, config):
        """Test comprehensive session management."""
        async with BrowserCrawler(config) as crawler:
            # Test multiple named sessions
            sessions = ['session_a', 'session_b', 'session_c']
            results = {}
            
            for session_name in sessions:
                result = await crawler.fetch(
                    "https://httpbin.org/html",
                    session_name=session_name
                )
                results[session_name] = result
                
                assert result.success is True
                assert result.metadata.get('session_id') is not None
            
            # Verify session isolation
            session_ids = [r.metadata.get('session_id') for r in results.values()]
            assert len(set(session_ids)) == len(sessions)  # All unique
            
            # Test session reuse
            reuse_result = await crawler.fetch(
                "https://httpbin.org/json",
                session_name='session_a'
            )
            
            assert reuse_result.success is True
            assert reuse_result.metadata.get('session_id') == results['session_a'].metadata.get('session_id')
            
            # Test session stats
            stats = await crawler.get_stats()
            assert stats['active_sessions'] >= len(sessions)
            assert stats['total_sessions'] >= len(sessions)
    
    @pytest.mark.asyncio
    async def test_batch_processing_comprehensive(self, config):
        """Test comprehensive batch processing."""
        async with BrowserCrawler(config) as crawler:
            urls = [
                "https://httpbin.org/html",
                "https://httpbin.org/json",
                "https://httpbin.org/xml",
                "https://httpbin.org/robots.txt"
            ]
            
            results = await crawler.fetch_batch(
                urls,
                max_concurrent=2,
                clean_html=True,
                download_images=False
            )
            
            assert len(results) == len(urls)
            
            successful_results = [r for r in results if r.success]
            assert len(successful_results) >= len(urls) * 0.8  # At least 80% success
            
            for result in successful_results:
                assert result.url in urls
                assert len(result.html) > 0
                assert isinstance(result.metadata, dict)
                assert isinstance(result.timestamp, float)
    
    @pytest.mark.asyncio
    async def test_error_handling_comprehensive(self, config):
        """Test comprehensive error handling."""
        async with BrowserCrawler(config) as crawler:
            # Test invalid URL
            result = await crawler.fetch("https://invalid-domain-that-does-not-exist.com")
            
            assert result.success is False
            assert result.error is not None
            assert result.url == "https://invalid-domain-that-does-not-exist.com"
            
            # Test invalid JavaScript
            js_result = await crawler.execute_js(
                "https://httpbin.org/html",
                "invalid javascript syntax!!!"
            )
            
            assert js_result['success'] is False
            assert js_result['error'] is not None
            
            # Test invalid API pattern
            api_result = await crawler.fetch_api_response(
                "nonexistent-pattern",
                "https://httpbin.org/json"
            )
            
            assert api_result['success'] is False
            assert api_result['pattern'] == "nonexistent-pattern"
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, config):
        """Test caching functionality."""
        async with BrowserCrawler(config) as crawler:
            url = "https://httpbin.org/html"
            
            # First fetch (should cache)
            result1 = await crawler.fetch(url, use_cache=True)
            assert result1.success is True
            
            # Second fetch (should use cache)
            result2 = await crawler.fetch(url, use_cache=True)
            assert result2.success is True
            
            # Results should be identical when cached
            assert result1.html == result2.html
            assert result1.title == result2.title
            
            # Clear cache
            await crawler.clear_cache()
            
            # Third fetch (should fetch fresh)
            result3 = await crawler.fetch(url, use_cache=True)
            assert result3.success is True
    
    @pytest.mark.asyncio
    async def test_stealth_mode_functionality(self, config):
        """Test stealth mode functionality."""
        # Enable stealth mode
        config.stealth_mode = True
        
        async with BrowserCrawler(config) as crawler:
            # Test that stealth techniques are applied
            js_code = """
            return {
                webdriver: navigator.webdriver,
                plugins: navigator.plugins.length,
                languages: navigator.languages
            };
            """
            
            result = await crawler.execute_js("https://httpbin.org/html", js_code)
            
            if result['success']:
                stealth_result = result['result']
                
                # Webdriver should be undefined (stealth)
                assert stealth_result.get('webdriver') is None
                
                # Should have plugins (stealth)
                assert stealth_result.get('plugins', 0) > 0
                
                # Should have languages (stealth)
                assert isinstance(stealth_result.get('languages'), list)
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_comprehensive(self, config):
        """Test comprehensive concurrent operations."""
        async with BrowserCrawler(config) as crawler:
            # Test concurrent different operations
            tasks = [
                crawler.fetch("https://httpbin.org/html", session_name="concurrent_1"),
                crawler.discover_apis("https://httpbin.org/json"),
                crawler.execute_js("https://httpbin.org/html", "return document.title;"),
                crawler.download_images_from_page("https://httpbin.org/html"),
                crawler.fetch("https://httpbin.org/xml", session_name="concurrent_2")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that all operations completed
            assert len(results) == len(tasks)
            
            # Check that no exceptions occurred
            for i, result in enumerate(results):
                assert not isinstance(result, Exception), f"Task {i} failed: {result}"
            
            # Verify specific result types
            fetch_result = results[0]
            api_result = results[1]
            js_result = results[2]
            image_result = results[3]
            fetch_result2 = results[4]
            
            assert fetch_result.success is True
            assert isinstance(api_result, dict)
            assert isinstance(js_result, dict)
            assert isinstance(image_result, dict)
            assert fetch_result2.success is True
