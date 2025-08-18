"""
Integration tests for API discovery functionality.
"""

import pytest
import asyncio
import tempfile

from multi_browser_crawler import BrowserCrawler, BrowserConfig


@pytest.mark.integration
@pytest.mark.browser
class TestAPIDiscovery:
    """Integration tests for API discovery functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=2,
                data_folder=temp_dir,
                fetch_limit=50
            )
    
    @pytest.mark.asyncio
    async def test_api_discovery_basic(self, config):
        """Test basic API discovery functionality."""
        async with BrowserCrawler(config) as crawler:
            # Test with a site that makes API calls
            result = await crawler.discover_apis("https://jsonplaceholder.typicode.com/")
            
            assert isinstance(result, dict)
            assert 'success' in result
            assert 'total_api_calls' in result
            assert 'api_calls' in result
            assert 'url' in result
            
            if result['success']:
                assert result['url'] == "https://jsonplaceholder.typicode.com/"
                assert isinstance(result['total_api_calls'], int)
                assert isinstance(result['api_calls'], list)
                
                # Should have discovered some API calls
                if result['total_api_calls'] > 0:
                    api_call = result['api_calls'][0]
                    assert 'url' in api_call
                    assert 'method' in api_call
                    assert 'status' in api_call
                    assert 'content_type' in api_call
    
    @pytest.mark.asyncio
    async def test_api_discovery_with_json_endpoint(self, config):
        """Test API discovery with a JSON endpoint."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.discover_apis("https://httpbin.org/json")
            
            assert isinstance(result, dict)
            assert 'success' in result
            
            if result['success']:
                assert result['total_api_calls'] >= 0
                assert 'api_call_summary' in result
                assert 'discovery_summary' in result
                
                # Check summary structure
                summary = result['api_call_summary']
                assert 'json_apis' in summary
                assert 'graphql_apis' in summary
                assert 'other_apis' in summary
                
                discovery = result['discovery_summary']
                assert 'domains_found' in discovery
                assert 'methods_used' in discovery
                assert 'content_types' in discovery
    
    @pytest.mark.asyncio
    async def test_fetch_complete_api_response(self, config):
        """Test fetching complete API response."""
        async with BrowserCrawler(config) as crawler:
            # Test fetching a specific API response
            result = await crawler.fetch_api_response(
                "json",  # Pattern to match
                "https://httpbin.org/json"  # Page URL
            )
            
            assert isinstance(result, dict)
            assert 'success' in result
            
            if result['success']:
                assert 'url' in result
                assert 'method' in result
                assert 'status' in result
                assert 'response_data' in result
                assert 'content_type' in result
                
                # Should have captured the JSON response
                if result['response_data']:
                    assert isinstance(result['response_data'], (dict, str))
    
    @pytest.mark.asyncio
    async def test_api_discovery_error_handling(self, config):
        """Test API discovery error handling."""
        async with BrowserCrawler(config) as crawler:
            # Test with invalid URL
            result = await crawler.discover_apis("https://invalid-domain-that-does-not-exist.com")
            
            assert isinstance(result, dict)
            assert 'success' in result
            
            # Should handle errors gracefully
            if not result['success']:
                assert 'error' in result
                assert 'url' in result
                assert result['total_api_calls'] == 0
                assert result['api_calls'] == []
    
    @pytest.mark.asyncio
    async def test_api_response_pattern_matching(self, config):
        """Test API response pattern matching."""
        async with BrowserCrawler(config) as crawler:
            # Test with a pattern that should not match
            result = await crawler.fetch_api_response(
                "nonexistent-pattern",
                "https://httpbin.org/json"
            )
            
            assert isinstance(result, dict)
            assert 'success' in result
            assert 'pattern' in result
            assert 'page_url' in result
            
            # Should not find matching pattern
            if not result['success']:
                assert 'error' in result
                assert result['pattern'] == "nonexistent-pattern"
    
    @pytest.mark.asyncio
    async def test_api_discovery_session_isolation(self, config):
        """Test API discovery with session isolation."""
        async with BrowserCrawler(config) as crawler:
            # Test with different sessions
            result1 = await crawler.discover_apis(
                "https://httpbin.org/json",
                session_name="api_session_1"
            )
            
            result2 = await crawler.discover_apis(
                "https://httpbin.org/json",
                session_name="api_session_2"
            )
            
            assert isinstance(result1, dict)
            assert isinstance(result2, dict)
            
            # Both should work independently
            assert 'success' in result1
            assert 'success' in result2
    
    @pytest.mark.asyncio
    async def test_api_discovery_comprehensive(self, config):
        """Test comprehensive API discovery features."""
        async with BrowserCrawler(config) as crawler:
            # Test with a site that has multiple types of requests
            result = await crawler.discover_apis("https://httpbin.org/")
            
            assert isinstance(result, dict)
            
            if result.get('success'):
                # Check all expected fields are present
                required_fields = [
                    'url', 'total_requests', 'total_api_calls', 'api_calls_count',
                    'other_requests_count', 'api_calls', 'other_requests',
                    'api_call_summary', 'discovery_summary', 'usage_hint'
                ]
                
                for field in required_fields:
                    assert field in result, f"Missing field: {field}"
                
                # Check data types
                assert isinstance(result['total_requests'], int)
                assert isinstance(result['total_api_calls'], int)
                assert isinstance(result['api_calls'], list)
                assert isinstance(result['other_requests'], list)
                assert isinstance(result['api_call_summary'], dict)
                assert isinstance(result['discovery_summary'], dict)
                assert isinstance(result['usage_hint'], str)
                
                # Check summary structure
                api_summary = result['api_call_summary']
                assert 'json_apis' in api_summary
                assert 'graphql_apis' in api_summary
                assert 'other_apis' in api_summary
                
                discovery_summary = result['discovery_summary']
                assert 'domains_found' in discovery_summary
                assert 'methods_used' in discovery_summary
                assert 'content_types' in discovery_summary
                
                # Check that lists contain expected data types
                assert isinstance(discovery_summary['domains_found'], list)
                assert isinstance(discovery_summary['methods_used'], list)
                assert isinstance(discovery_summary['content_types'], list)


@pytest.mark.integration
@pytest.mark.browser
class TestAPIDiscoveryPerformance:
    """Performance tests for API discovery."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=3,
                data_folder=temp_dir
            )
    
    @pytest.mark.asyncio
    async def test_api_discovery_performance(self, config):
        """Test API discovery performance."""
        import time
        
        async with BrowserCrawler(config) as crawler:
            start_time = time.time()
            
            result = await crawler.discover_apis("https://httpbin.org/json")
            
            end_time = time.time()
            discovery_time = end_time - start_time
            
            # API discovery should complete within reasonable time
            assert discovery_time < 30.0, f"API discovery too slow: {discovery_time:.2f}s"
            
            if result.get('success'):
                print(f"API discovery completed in {discovery_time:.2f}s")
                print(f"Found {result.get('total_api_calls', 0)} API calls")
    
    @pytest.mark.asyncio
    async def test_concurrent_api_discovery(self, config):
        """Test concurrent API discovery operations."""
        async with BrowserCrawler(config) as crawler:
            # Test multiple concurrent API discoveries
            urls = [
                "https://httpbin.org/json",
                "https://httpbin.org/xml",
                "https://httpbin.org/html"
            ]
            
            tasks = [
                crawler.discover_apis(url, session_name=f"concurrent_{i}")
                for i, url in enumerate(urls)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            assert len(results) == len(urls)
            
            # Check that all results are valid (not exceptions)
            for i, result in enumerate(results):
                assert not isinstance(result, Exception), f"Task {i} raised exception: {result}"
                assert isinstance(result, dict)
                assert 'success' in result
