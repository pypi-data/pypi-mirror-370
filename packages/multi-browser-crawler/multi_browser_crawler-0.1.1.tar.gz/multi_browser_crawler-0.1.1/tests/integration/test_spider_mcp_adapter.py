"""
Integration tests for spider-mcp adapter compatibility.
"""

import pytest
import asyncio
import tempfile
import os
import sys

# Add spider_mcp to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'spider_mcp', 'backend'))

try:
    from multi_browser_adapter import PersistentBrowserManager, MultiBrowserAdapter
    ADAPTER_AVAILABLE = True
except ImportError as e:
    ADAPTER_AVAILABLE = False
    pytest.skip(f"Spider-MCP adapter not available: {e}", allow_module_level=True)


@pytest.mark.integration
@pytest.mark.browser
@pytest.mark.skipif(not ADAPTER_AVAILABLE, reason="Spider-MCP adapter not available")
class TestSpiderMCPAdapter:
    """Integration tests for spider-mcp adapter compatibility."""
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_fetch_html(self):
        """Test PersistentBrowserManager.fetch_html compatibility."""
        result = await PersistentBrowserManager.fetch_html(
            "https://httpbin.org/html",
            headless=True,
            app_name="test_adapter",
            timeout=30
        )
        
        assert isinstance(result, dict)
        assert 'html' in result
        assert 'url' in result
        
        # Should have HTML content
        assert len(result['html']) > 0
        assert result['url'] == "https://httpbin.org/html"
        
        # Should not have error
        assert 'error' not in result or result.get('error') is None
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_fetch_html_with_js(self):
        """Test PersistentBrowserManager.fetch_html with JavaScript."""
        js_action = "document.title = 'Modified Title';"
        
        result = await PersistentBrowserManager.fetch_html(
            "https://httpbin.org/html",
            headless=True,
            app_name="test_js",
            timeout=30,
            js_action=js_action
        )
        
        assert isinstance(result, dict)
        assert 'html' in result
        assert len(result['html']) > 0
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_fetch_html_with_api_capture(self):
        """Test PersistentBrowserManager.fetch_html_with_api_capture compatibility."""
        result = await PersistentBrowserManager.fetch_html_with_api_capture(
            "https://httpbin.org/json",
            api_patterns=["json"],
            headless=True,
            app_name="test_api_capture",
            timeout=30
        )
        
        assert isinstance(result, dict)
        assert 'html' in result
        assert 'api_calls' in result
        assert 'url' in result
        
        # Check API calls structure
        api_calls = result['api_calls']
        assert isinstance(api_calls, dict)
        assert 'total_api_calls' in api_calls
        assert 'api_calls' in api_calls
        assert isinstance(api_calls['total_api_calls'], int)
        assert isinstance(api_calls['api_calls'], list)
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_fetch_all_api_calls(self):
        """Test PersistentBrowserManager.fetch_all_api_calls compatibility."""
        result = await PersistentBrowserManager.fetch_all_api_calls(
            "https://httpbin.org/json",
            headless=True,
            app_name="test_all_apis",
            timeout=30
        )
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'url' in result
        assert 'total_api_calls' in result
        assert 'api_calls' in result
        
        # Should have discovered the page
        assert result['url'] == "https://httpbin.org/json"
        assert isinstance(result['total_api_calls'], int)
        assert isinstance(result['api_calls'], list)
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_fetch_complete_api_response(self):
        """Test PersistentBrowserManager.fetch_complete_api_response compatibility."""
        result = await PersistentBrowserManager.fetch_complete_api_response(
            "json",  # API pattern
            "https://httpbin.org/json",  # Page URL
            headless=True,
            app_name="test_complete_api",
            timeout=30
        )
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'pattern' in result
        assert 'page_url' in result
        
        # Check pattern and page URL
        assert result['pattern'] == "json"
        assert result['page_url'] == "https://httpbin.org/json"
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_error_handling(self):
        """Test PersistentBrowserManager error handling."""
        # Test with invalid URL
        result = await PersistentBrowserManager.fetch_html(
            "https://invalid-domain-that-does-not-exist.com",
            headless=True,
            app_name="test_error",
            timeout=10
        )
        
        assert isinstance(result, dict)
        assert 'html' in result
        assert 'error' in result
        assert 'url' in result
        
        # Should have error information
        assert result['error'] is not None
        assert result['url'] == "https://invalid-domain-that-does-not-exist.com"
        
        # HTML should contain error message
        assert "Error" in result['html'] or len(result['html']) == 0
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_session_isolation(self):
        """Test session isolation in PersistentBrowserManager."""
        # Fetch with different app names (sessions)
        result1 = await PersistentBrowserManager.fetch_html(
            "https://httpbin.org/html",
            headless=True,
            app_name="session_test_1",
            timeout=30
        )
        
        result2 = await PersistentBrowserManager.fetch_html(
            "https://httpbin.org/html",
            headless=True,
            app_name="session_test_2",
            timeout=30
        )
        
        # Both should succeed
        assert 'html' in result1
        assert 'html' in result2
        assert len(result1['html']) > 0
        assert len(result2['html']) > 0
        
        # Should work independently
        assert result1['url'] == result2['url']
    
    @pytest.mark.asyncio
    async def test_persistent_browser_manager_cleanup(self):
        """Test PersistentBrowserManager cleanup functionality."""
        # Create a session
        await PersistentBrowserManager.fetch_html(
            "https://httpbin.org/html",
            headless=True,
            app_name="cleanup_test",
            timeout=30
        )
        
        # Cleanup specific instance
        cleanup_result = await PersistentBrowserManager.cleanup_instance(
            headless=True,
            app_name="cleanup_test"
        )
        
        assert cleanup_result is True
        
        # Cleanup all
        cleanup_all_result = await PersistentBrowserManager.cleanup_all()
        assert cleanup_all_result is True
    
    @pytest.mark.asyncio
    async def test_multi_browser_adapter_direct(self):
        """Test MultiBrowserAdapter directly."""
        result = await MultiBrowserAdapter.fetch_html(
            "https://httpbin.org/html",
            headless=True,
            app_name="direct_test",
            timeout=30
        )
        
        assert isinstance(result, dict)
        assert 'html' in result
        assert 'url' in result
        assert len(result['html']) > 0
    
    @pytest.mark.asyncio
    async def test_adapter_concurrent_operations(self):
        """Test concurrent operations with adapter."""
        # Test multiple concurrent requests
        tasks = []
        for i in range(3):
            task = PersistentBrowserManager.fetch_html(
                "https://httpbin.org/html",
                headless=True,
                app_name=f"concurrent_test_{i}",
                timeout=30
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed: {result}"
            assert isinstance(result, dict)
            assert 'html' in result
            assert len(result['html']) > 0


@pytest.mark.integration
@pytest.mark.browser
@pytest.mark.skipif(not ADAPTER_AVAILABLE, reason="Spider-MCP adapter not available")
class TestSpiderMCPAdapterPerformance:
    """Performance tests for spider-mcp adapter."""
    
    @pytest.mark.asyncio
    async def test_adapter_performance(self):
        """Test adapter performance."""
        import time
        
        start_time = time.time()
        
        result = await PersistentBrowserManager.fetch_html(
            "https://httpbin.org/html",
            headless=True,
            app_name="performance_test",
            timeout=30
        )
        
        end_time = time.time()
        fetch_time = end_time - start_time
        
        # Should complete within reasonable time
        assert fetch_time < 30.0, f"Adapter fetch too slow: {fetch_time:.2f}s"
        
        # Should have valid result
        assert isinstance(result, dict)
        assert 'html' in result
        assert len(result['html']) > 0
        
        print(f"Adapter fetch completed in {fetch_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_adapter_api_discovery_performance(self):
        """Test API discovery performance through adapter."""
        import time
        
        start_time = time.time()
        
        result = await PersistentBrowserManager.fetch_all_api_calls(
            "https://httpbin.org/json",
            headless=True,
            app_name="api_performance_test",
            timeout=30
        )
        
        end_time = time.time()
        discovery_time = end_time - start_time
        
        # Should complete within reasonable time
        assert discovery_time < 45.0, f"API discovery too slow: {discovery_time:.2f}s"
        
        # Should have valid result
        assert isinstance(result, dict)
        assert 'success' in result
        
        if result.get('success'):
            print(f"API discovery completed in {discovery_time:.2f}s")
            print(f"Found {result.get('total_api_calls', 0)} API calls")
    
    @pytest.mark.asyncio
    async def test_adapter_memory_usage(self):
        """Test adapter memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple operations
        for i in range(5):
            result = await PersistentBrowserManager.fetch_html(
                "https://httpbin.org/html",
                headless=True,
                app_name=f"memory_test_{i}",
                timeout=30
            )
            assert 'html' in result
        
        # Cleanup
        await PersistentBrowserManager.cleanup_all()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        # Memory increase should be reasonable
        assert memory_increase < 500, f"Memory usage too high: +{memory_increase:.1f}MB"
