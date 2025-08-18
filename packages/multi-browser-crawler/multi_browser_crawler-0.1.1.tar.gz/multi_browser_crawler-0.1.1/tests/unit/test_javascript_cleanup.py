"""
Unit tests for JavaScript cleanup functionality.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, AsyncMock, patch

from multi_browser_crawler.core.browser_manager import BrowserManager
from multi_browser_crawler.config.settings import BrowserConfig


class TestJavaScriptCleanup:
    """Test JavaScript cleanup functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                data_folder=temp_dir,
                max_sessions=1
            )
    
    @pytest.fixture
    def browser_manager(self, config):
        """Create browser manager instance."""
        # Convert BrowserConfig to dict for BrowserManager
        config_dict = {
            'headless': config.headless,
            'data_folder': config.data_folder,
            'max_sessions': config.max_sessions
        }
        return BrowserManager(config_dict)
    
    def test_cleanup_js_file_exists(self):
        """Test that the cleanup JavaScript file exists."""
        cleanup_js_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 
            'multi_browser_crawler', 
            'js', 
            'cleanup_page.js'
        )
        cleanup_js_path = os.path.abspath(cleanup_js_path)
        
        assert os.path.exists(cleanup_js_path), f"Cleanup JS file not found at {cleanup_js_path}"
        
        # Check that it's not empty
        with open(cleanup_js_path, 'r') as f:
            content = f.read()
        
        assert len(content) > 100, "Cleanup JS file appears to be empty or too small"
        assert 'cleanupPageAdvanced' in content, "Cleanup function not found in JS file"
    
    def test_cleanup_js_content(self):
        """Test that the cleanup JavaScript contains expected functionality."""
        cleanup_js_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 
            'multi_browser_crawler', 
            'js', 
            'cleanup_page.js'
        )
        cleanup_js_path = os.path.abspath(cleanup_js_path)
        
        with open(cleanup_js_path, 'r') as f:
            content = f.read()
        
        # Check for key functionality
        assert 'function cleanupPageAdvanced' in content
        assert 'removeTags' in content
        assert 'removeAds' in content
        assert 'remove1x1Images' in content
        assert 'removeStyleAttribute' in content
        
        # Check for ad network targeting
        assert 'adsbygoogle' in content
        assert 'google_ads' in content
        
        # Check for return value
        assert 'return' in content
    
    @pytest.mark.asyncio
    async def test_execute_advanced_cleanup_with_page(self, browser_manager):
        """Test advanced cleanup execution with mock page."""
        # Mock page object
        mock_page = AsyncMock()
        browser_manager.page = mock_page
        
        # Mock file reading
        cleanup_js_content = """
        function cleanupPageAdvanced(options) {
            return { removed: { tags: { scripts: 5 } } };
        }
        """
        
        with patch('builtins.open', mock_open_with_content(cleanup_js_content)):
            with patch('os.path.exists', return_value=True):
                await browser_manager._execute_advanced_cleanup()
        
        # Verify that evaluate was called twice (once for script, once for function call)
        assert mock_page.evaluate.call_count == 2
        
        # Check the function call arguments
        calls = mock_page.evaluate.call_args_list
        assert cleanup_js_content in calls[0][0]  # First call loads the script
        assert 'cleanupPageAdvanced' in calls[1][0][0]  # Second call executes the function
    
    @pytest.mark.asyncio
    async def test_execute_advanced_cleanup_no_file(self, browser_manager):
        """Test advanced cleanup when JS file doesn't exist."""
        # Mock page object
        mock_page = AsyncMock()
        browser_manager.page = mock_page
        
        with patch('os.path.exists', return_value=False):
            # Should not raise an exception
            await browser_manager._execute_advanced_cleanup()
        
        # Page evaluate should not be called
        mock_page.evaluate.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_advanced_cleanup_js_error(self, browser_manager):
        """Test advanced cleanup when JavaScript execution fails."""
        # Mock page object that raises an error
        mock_page = AsyncMock()
        mock_page.evaluate.side_effect = Exception("JavaScript error")
        browser_manager.page = mock_page
        
        cleanup_js_content = "function cleanupPageAdvanced() { return {}; }"
        
        with patch('builtins.open', mock_open_with_content(cleanup_js_content)):
            with patch('os.path.exists', return_value=True):
                # Should not raise an exception (should handle gracefully)
                await browser_manager._execute_advanced_cleanup()
        
        # Should have attempted to call evaluate
        assert mock_page.evaluate.call_count > 0
    
    def test_cleanup_function_parameters(self):
        """Test that cleanup function is called with correct parameters."""
        cleanup_js_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 
            'multi_browser_crawler', 
            'js', 
            'cleanup_page.js'
        )
        cleanup_js_path = os.path.abspath(cleanup_js_path)
        
        # Read the actual cleanup script
        with open(cleanup_js_path, 'r') as f:
            content = f.read()
        
        # Check that the function accepts options parameter
        assert 'function cleanupPageAdvanced(options' in content or 'cleanupPageAdvanced = function(options' in content
        
        # Check for default options handling
        assert 'defaults' in content or 'options = options || {}' in content or 'options = {}' in content
    
    @pytest.mark.asyncio
    async def test_cleanup_integration_with_fetch(self, browser_manager):
        """Test that cleanup is integrated with fetch when clean_html=True."""
        # Mock the necessary components
        mock_page = AsyncMock()
        mock_page.content.return_value = "<html><body>Test</body></html>"
        mock_page.title.return_value = "Test Title"
        browser_manager.page = mock_page
        
        # Mock navigation
        browser_manager.navigate_to_url = AsyncMock()
        
        # Mock HTML cleaner
        browser_manager.html_cleaner = Mock()
        browser_manager.html_cleaner.clean_html.return_value = "<html><body>Cleaned</body></html>"
        
        # Mock advanced cleanup
        browser_manager._execute_advanced_cleanup = AsyncMock()

        # Mock required attributes
        browser_manager.fetch_count = 0
        browser_manager.fetch_limit = 1000
        browser_manager.current_session_id = "test_session"
        browser_manager.session_manager = Mock()
        browser_manager.session_manager.update_session_usage = Mock()
        
        # Call fetch_html with clean=True
        result = await browser_manager.fetch_html("https://example.com", clean=True)
        
        # Verify advanced cleanup was called
        browser_manager._execute_advanced_cleanup.assert_called_once()
        
        # Verify HTML cleaner was called
        browser_manager.html_cleaner.clean_html.assert_called_once()
        
        # Verify result
        assert 'html' in result
        assert result['html'] == "<html><body>Cleaned</body></html>"
        assert result['url'] == "https://example.com"


def mock_open_with_content(content):
    """Helper function to mock file opening with specific content."""
    from unittest.mock import mock_open
    return mock_open(read_data=content)
