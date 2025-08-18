"""
Functionality comparison tests to ensure all spider-mcp features are implemented.
"""

import pytest
import asyncio
import tempfile
import os
import sys

from multi_browser_crawler import BrowserCrawler, BrowserConfig

# Add spider_mcp to path for comparison
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'spider_mcp', 'backend'))

try:
    from multi_browser_adapter import PersistentBrowserManager
    ADAPTER_AVAILABLE = True
except ImportError:
    ADAPTER_AVAILABLE = False


@pytest.mark.integration
@pytest.mark.browser
class TestFunctionalityComparison:
    """Compare functionality between multi-browser-crawler and original spider-mcp."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=3,
                data_folder=temp_dir,
                download_images=True,
                fetch_limit=50
            )
    
    @pytest.mark.asyncio
    async def test_basic_html_fetching_comparison(self, config):
        """Compare basic HTML fetching between implementations."""
        url = "https://httpbin.org/html"
        
        # Test new implementation
        async with BrowserCrawler(config) as crawler:
            new_result = await crawler.fetch(url)
            
            assert new_result.success is True
            assert len(new_result.html) > 0
            assert new_result.url == url
            assert isinstance(new_result.metadata, dict)
            
            new_html_length = len(new_result.html)
            new_title = new_result.title
        
        # Test adapter (spider-mcp compatibility)
        if ADAPTER_AVAILABLE:
            adapter_result = await PersistentBrowserManager.fetch_html(url)
            
            assert 'html' in adapter_result
            assert len(adapter_result['html']) > 0
            assert adapter_result['url'] == url
            
            # Results should be similar
            adapter_html_length = len(adapter_result['html'])
            assert abs(new_html_length - adapter_html_length) < 1000  # Allow some variation
            
            await PersistentBrowserManager.cleanup_all()
    
    @pytest.mark.asyncio
    async def test_api_discovery_comparison(self, config):
        """Compare API discovery functionality."""
        url = "https://httpbin.org/json"
        
        # Test new implementation
        async with BrowserCrawler(config) as crawler:
            new_result = await crawler.discover_apis(url)
            
            assert isinstance(new_result, dict)
            assert 'success' in new_result
            assert 'total_api_calls' in new_result
            assert 'api_calls' in new_result
            
            new_api_count = new_result.get('total_api_calls', 0)
        
        # Test adapter
        if ADAPTER_AVAILABLE:
            adapter_result = await PersistentBrowserManager.fetch_all_api_calls(url)
            
            assert isinstance(adapter_result, dict)
            assert 'success' in adapter_result
            assert 'total_api_calls' in adapter_result
            
            adapter_api_count = adapter_result.get('total_api_calls', 0)
            
            # Should discover similar number of APIs
            assert abs(new_api_count - adapter_api_count) <= 2  # Allow small variation
            
            await PersistentBrowserManager.cleanup_all()
    
    @pytest.mark.asyncio
    async def test_session_management_comparison(self, config):
        """Compare session management functionality."""
        # Test new implementation
        async with BrowserCrawler(config) as crawler:
            # Create multiple sessions
            session_names = ['test_session_1', 'test_session_2']
            results = {}
            
            for session_name in session_names:
                result = await crawler.fetch(
                    "https://httpbin.org/html",
                    session_name=session_name
                )
                results[session_name] = result
                
                assert result.success is True
                assert result.metadata.get('session_id') is not None
            
            # Verify session isolation
            session_ids = [r.metadata.get('session_id') for r in results.values()]
            assert len(set(session_ids)) == len(session_names)  # All unique
            
            # Test session reuse
            reuse_result = await crawler.fetch(
                "https://httpbin.org/json",
                session_name='test_session_1'
            )
            
            assert reuse_result.success is True
            assert reuse_result.metadata.get('session_id') == results['test_session_1'].metadata.get('session_id')
            
            # Test stats
            stats = await crawler.get_stats()
            assert stats['active_sessions'] >= len(session_names)
            assert stats['total_sessions'] >= len(session_names)
    
    @pytest.mark.asyncio
    async def test_error_handling_comparison(self, config):
        """Compare error handling between implementations."""
        invalid_url = "https://invalid-domain-that-does-not-exist.com"
        
        # Test new implementation
        async with BrowserCrawler(config) as crawler:
            new_result = await crawler.fetch(invalid_url)
            
            assert new_result.success is False
            assert new_result.error is not None
            assert new_result.url == invalid_url
        
        # Test adapter
        if ADAPTER_AVAILABLE:
            adapter_result = await PersistentBrowserManager.fetch_html(invalid_url)
            
            assert isinstance(adapter_result, dict)
            assert 'error' in adapter_result
            assert adapter_result['url'] == invalid_url
            
            await PersistentBrowserManager.cleanup_all()
    
    @pytest.mark.asyncio
    async def test_javascript_execution_comparison(self, config):
        """Compare JavaScript execution functionality."""
        url = "https://httpbin.org/html"
        js_code = "(() => { return document.title || 'No Title'; })()"
        
        # Test new implementation
        async with BrowserCrawler(config) as crawler:
            new_result = await crawler.execute_js(url, js_code)
            
            assert isinstance(new_result, dict)
            assert 'success' in new_result
            
            if new_result['success']:
                assert 'result' in new_result
                assert isinstance(new_result['result'], str)
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_comparison(self, config):
        """Compare concurrent operations handling."""
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        # Test new implementation
        async with BrowserCrawler(config) as crawler:
            # Test concurrent fetches
            tasks = [
                crawler.fetch(url, session_name=f"concurrent_{i}")
                for i, url in enumerate(urls)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed
            for i, result in enumerate(results):
                assert not isinstance(result, Exception), f"Task {i} failed: {result}"
                assert result.success is True
            
            # Test concurrent API discovery
            api_tasks = [
                crawler.discover_apis(url)
                for url in urls[:2]  # Limit to 2 for performance
            ]
            
            api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
            
            for i, result in enumerate(api_results):
                assert not isinstance(result, Exception), f"API task {i} failed: {result}"
                assert isinstance(result, dict)
                assert 'success' in result
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self, config):
        """Compare performance between implementations."""
        import time
        
        url = "https://httpbin.org/html"
        
        # Test new implementation performance
        async with BrowserCrawler(config) as crawler:
            start_time = time.time()
            
            result = await crawler.fetch(url)
            
            end_time = time.time()
            new_time = end_time - start_time
            
            assert result.success is True
            assert new_time < 30.0  # Should complete within 30 seconds
        
        # Test adapter performance
        if ADAPTER_AVAILABLE:
            start_time = time.time()
            
            adapter_result = await PersistentBrowserManager.fetch_html(url)
            
            end_time = time.time()
            adapter_time = end_time - start_time
            
            assert 'html' in adapter_result
            assert adapter_time < 30.0  # Should complete within 30 seconds
            
            # Performance should be comparable (within 50% difference)
            time_ratio = max(new_time, adapter_time) / min(new_time, adapter_time)
            assert time_ratio < 2.0, f"Performance difference too large: {new_time:.2f}s vs {adapter_time:.2f}s"
            
            await PersistentBrowserManager.cleanup_all()
            
            print(f"Performance comparison - New: {new_time:.2f}s, Adapter: {adapter_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_feature_completeness(self, config):
        """Test that all major features from spider-mcp are available."""
        async with BrowserCrawler(config) as crawler:
            # Test all major methods exist and work
            url = "https://httpbin.org/html"
            
            # Basic fetch
            fetch_result = await crawler.fetch(url)
            assert fetch_result.success is True
            
            # Batch fetch
            batch_results = await crawler.fetch_batch([url, "https://httpbin.org/json"])
            assert len(batch_results) == 2
            assert all(r.success for r in batch_results)
            
            # API discovery
            api_result = await crawler.discover_apis("https://httpbin.org/json")
            assert api_result.get('success') is True
            
            # JavaScript execution
            js_result = await crawler.execute_js(url, "(() => { return 'test'; })()")
            assert isinstance(js_result, dict)
            
            # Session management
            stats = await crawler.get_stats()
            assert isinstance(stats, dict)
            assert 'active_sessions' in stats
            
            # Cleanup
            cleanup_result = await crawler.cleanup_session("default")
            assert isinstance(cleanup_result, bool)
            
            print("✅ All major features are available and functional")


@pytest.mark.integration
@pytest.mark.browser
@pytest.mark.skipif(not ADAPTER_AVAILABLE, reason="Spider-MCP adapter not available")
class TestAdapterCompatibility:
    """Test adapter compatibility with original spider-mcp interface."""
    
    @pytest.mark.asyncio
    async def test_adapter_interface_compatibility(self):
        """Test that adapter provides exact same interface as original."""
        # Test all expected methods exist
        assert hasattr(PersistentBrowserManager, 'fetch_html')
        assert hasattr(PersistentBrowserManager, 'fetch_html_with_api_capture')
        assert hasattr(PersistentBrowserManager, 'fetch_all_api_calls')
        assert hasattr(PersistentBrowserManager, 'fetch_complete_api_response')
        assert hasattr(PersistentBrowserManager, 'cleanup_all')
        assert hasattr(PersistentBrowserManager, 'cleanup_instance')
        
        # Test basic functionality
        result = await PersistentBrowserManager.fetch_html("https://httpbin.org/html")
        assert isinstance(result, dict)
        assert 'html' in result
        assert 'url' in result
        
        # Test cleanup
        cleanup_result = await PersistentBrowserManager.cleanup_all()
        assert cleanup_result is True
        
        print("✅ Adapter interface is fully compatible with spider-mcp")
