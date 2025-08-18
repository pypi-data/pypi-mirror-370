"""
Unit tests for import functionality and circular import fixes.
"""

import pytest
import sys
import importlib


class TestImports:
    """Test import functionality."""
    
    def test_main_package_import(self):
        """Test that the main package can be imported without circular dependencies."""
        # Clear any existing imports
        if 'multi_browser_crawler' in sys.modules:
            del sys.modules['multi_browser_crawler']
        
        # Import should work without errors
        import multi_browser_crawler
        assert multi_browser_crawler.__version__ == "0.1.0"
    
    def test_deferred_imports(self):
        """Test that deferred imports work correctly."""
        # Clear any existing imports
        modules_to_clear = [
            'multi_browser_crawler',
            'multi_browser_crawler.api',
            'multi_browser_crawler.core.browser_manager',
            'multi_browser_crawler.clients.browser_client',
            'multi_browser_crawler.config.settings',
            'multi_browser_crawler.config.proxy_config'
        ]
        
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Import main package
        import multi_browser_crawler
        
        # Test deferred imports
        browser_crawler = multi_browser_crawler.BrowserCrawler
        assert browser_crawler is not None
        
        fetch_func = multi_browser_crawler.fetch
        assert fetch_func is not None
        
        fetch_batch_func = multi_browser_crawler.fetch_batch
        assert fetch_batch_func is not None
        
        browser_manager = multi_browser_crawler.BrowserManager
        assert browser_manager is not None
        
        browser_client = multi_browser_crawler.BrowserClient
        assert browser_client is not None
        
        browser_config = multi_browser_crawler.BrowserConfig
        assert browser_config is not None
        
        proxy_config = multi_browser_crawler.ProxyConfig
        assert proxy_config is not None
    
    def test_invalid_attribute_access(self):
        """Test that invalid attribute access raises AttributeError."""
        import multi_browser_crawler
        
        with pytest.raises(AttributeError):
            _ = multi_browser_crawler.NonExistentClass
    
    def test_all_exports(self):
        """Test that __all__ contains all expected exports."""
        import multi_browser_crawler
        
        expected_exports = [
            "BrowserCrawler",
            "BrowserManager", 
            "BrowserClient",
            "BrowserConfig",
            "ProxyConfig",
            "fetch",
            "fetch_batch"
        ]
        
        assert hasattr(multi_browser_crawler, '__all__')
        assert set(multi_browser_crawler.__all__) == set(expected_exports)
    
    def test_direct_api_import(self):
        """Test that API classes can be imported directly."""
        from multi_browser_crawler.api import BrowserCrawler, fetch, fetch_batch
        
        assert BrowserCrawler is not None
        assert fetch is not None
        assert fetch_batch is not None
    
    def test_direct_config_import(self):
        """Test that config classes can be imported directly."""
        from multi_browser_crawler.config.settings import BrowserConfig
        from multi_browser_crawler.config.proxy_config import ProxyConfig
        
        assert BrowserConfig is not None
        assert ProxyConfig is not None
    
    def test_direct_core_import(self):
        """Test that core classes can be imported directly."""
        from multi_browser_crawler.core.browser_manager import BrowserManager
        from multi_browser_crawler.clients.browser_client import BrowserClient
        
        assert BrowserManager is not None
        assert BrowserClient is not None
    
    def test_no_circular_dependencies(self):
        """Test that there are no circular dependencies."""
        # Clear all related modules
        modules_to_clear = []
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('multi_browser_crawler'):
                modules_to_clear.append(module_name)
        
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Import should complete without hanging or errors
        try:
            import multi_browser_crawler
            from multi_browser_crawler import BrowserCrawler, fetch, fetch_batch
            from multi_browser_crawler.api import BrowserCrawler as DirectBrowserCrawler
            
            # All imports should succeed
            assert BrowserCrawler is not None
            assert DirectBrowserCrawler is not None
            assert BrowserCrawler is DirectBrowserCrawler  # Should be the same object
            
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")
    
    def test_lazy_loading_performance(self):
        """Test that lazy loading doesn't significantly impact performance."""
        import time
        
        # Clear modules
        modules_to_clear = []
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('multi_browser_crawler'):
                modules_to_clear.append(module_name)
        
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Time the import
        start_time = time.time()
        import multi_browser_crawler
        
        # Access deferred imports
        _ = multi_browser_crawler.BrowserCrawler
        _ = multi_browser_crawler.fetch
        _ = multi_browser_crawler.BrowserManager
        
        end_time = time.time()
        import_time = end_time - start_time
        
        # Should complete in reasonable time (less than 1 second)
        assert import_time < 1.0, f"Import took too long: {import_time:.3f}s"
