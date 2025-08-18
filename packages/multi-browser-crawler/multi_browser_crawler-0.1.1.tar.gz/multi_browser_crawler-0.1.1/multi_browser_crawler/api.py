"""
Main API Interface for Multi-Browser Crawler
============================================

Simple, clean API for browser automation and web crawling.
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
import logging

from .core.browser_manager import BrowserManager
from .config.settings import BrowserConfig, CrawlResult
from .exceptions.errors import BrowserCrawlerError, ConfigurationError

logger = logging.getLogger(__name__)


class BrowserCrawler:
    """
    Main entry point for browser automation and web crawling.
    
    Provides a simple, clean API for common browser operations.
    """
    
    def __init__(self, config: Union[BrowserConfig, Dict[str, Any]] = None):
        """
        Initialize the browser crawler.
        
        Args:
            config: Browser configuration (BrowserConfig object or dict)
        """
        # Handle configuration
        if config is None:
            self.config = BrowserConfig()
        elif isinstance(config, dict):
            self.config = BrowserConfig.from_dict(config)
        elif isinstance(config, BrowserConfig):
            self.config = config
        else:
            raise ConfigurationError("config must be BrowserConfig object or dictionary")
        
        # Initialize browser manager
        self._browser_manager = None
        self._initialized = False
        
        logger.info("BrowserCrawler initialized")
    
    async def _get_browser_manager(self) -> BrowserManager:
        """Get or create browser manager instance."""
        if self._browser_manager is None:
            self._browser_manager = await BrowserManager.get_instance(self.config.to_dict())
        return self._browser_manager
    
    async def _ensure_initialized(self):
        """Ensure browser manager is initialized."""
        if not self._initialized:
            await self._get_browser_manager()
            self._initialized = True
    
    async def fetch(self, url: str, **options) -> CrawlResult:
        """
        Fetch content from a single URL.
        
        Args:
            url: URL to fetch
            **options: Additional options:
                - session_name: Browser session name (default: "default")
                - use_cache: Whether to use cached content (default: False)
                - clean_html: Whether to clean HTML content (default: True)
                - download_images: Whether to download images (default: False)
                - execute_js: JavaScript code to execute after page load
                - wait_for: CSS selector to wait for before returning
                
        Returns:
            CrawlResult object with fetched content
        """
        try:
            await self._ensure_initialized()
            browser_manager = await self._get_browser_manager()
            
            # Extract options
            session_name = options.get('session_name', 'default')
            use_cache = options.get('use_cache', False)
            clean_html = options.get('clean_html', True)
            download_images = options.get('download_images', self.config.download_images)
            execute_js = options.get('execute_js')
            wait_for = options.get('wait_for')
            
            # Initialize browser session
            await browser_manager.initialize_browser(session_name)
            
            # Fetch HTML content
            result = await browser_manager.fetch_html(url, use_cache=use_cache, clean=clean_html)
            
            # Execute JavaScript if provided
            js_result = None
            if execute_js:
                js_result = await browser_manager.execute_javascript(execute_js)
            
            # Wait for selector if provided
            if wait_for:
                await browser_manager.js_executor.wait_for_element(browser_manager.page, wait_for)
            
            # Download images if requested
            images = []
            if download_images:
                image_result = await browser_manager.download_images_from_page(url)
                images = image_result.get('images', [])
            
            # Create crawl result
            crawl_result = CrawlResult(
                url=url,
                html=result.get('html', ''),
                title=result.get('title', ''),
                success=True,
                metadata={
                    'session_id': result.get('session_id'),
                    'timestamp': result.get('timestamp'),
                    'js_result': js_result,
                    'options': options
                },
                images=images
            )
            
            logger.info(f"Successfully fetched content from {url}")
            return crawl_result
            
        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {e}")
            return CrawlResult(
                url=url,
                html='',
                success=False,
                error=str(e)
            )
    
    async def fetch_batch(self, urls: List[str], **options) -> List[CrawlResult]:
        """
        Fetch content from multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            **options: Additional options (same as fetch method):
                - max_concurrent: Maximum concurrent requests (default: 5)
                - session_prefix: Prefix for session names (default: "batch")
                
        Returns:
            List of CrawlResult objects
        """
        try:
            await self._ensure_initialized()
            
            max_concurrent = options.get('max_concurrent', 5)
            session_prefix = options.get('session_prefix', 'batch')
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def fetch_with_semaphore(url: str, index: int) -> CrawlResult:
                async with semaphore:
                    # Use different session for each concurrent request
                    session_name = f"{session_prefix}_{index % max_concurrent}"
                    fetch_options = {**options, 'session_name': session_name}
                    return await self.fetch(url, **fetch_options)
            
            # Execute all fetches concurrently
            tasks = [fetch_with_semaphore(url, i) for i, url in enumerate(urls)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(CrawlResult(
                        url=urls[i],
                        html='',
                        success=False,
                        error=str(result)
                    ))
                else:
                    final_results.append(result)
            
            successful = sum(1 for r in final_results if r.success)
            logger.info(f"Batch fetch completed: {successful}/{len(urls)} successful")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Batch fetch failed: {e}")
            # Return error results for all URLs
            return [CrawlResult(url=url, html='', success=False, error=str(e)) for url in urls]
    
    async def execute_js(self, url: str, js_code: str, **options) -> Dict[str, Any]:
        """
        Execute JavaScript code on a page.
        
        Args:
            url: URL to navigate to
            js_code: JavaScript code to execute
            **options: Additional options:
                - session_name: Browser session name (default: "default")
                - wait_for: CSS selector to wait for before executing JS
                
        Returns:
            Dictionary with execution result
        """
        try:
            await self._ensure_initialized()
            browser_manager = await self._get_browser_manager()
            
            session_name = options.get('session_name', 'default')
            wait_for = options.get('wait_for')
            
            # Initialize browser session
            await browser_manager.initialize_browser(session_name)
            
            # Navigate to URL
            await browser_manager.navigate_to_url(url)
            
            # Wait for selector if provided
            if wait_for:
                await browser_manager.js_executor.wait_for_element(browser_manager.page, wait_for)
            
            # Execute JavaScript
            result = await browser_manager.execute_javascript(js_code)
            
            logger.info(f"Successfully executed JavaScript on {url}")
            
            return {
                'url': url,
                'result': result,
                'success': True,
                'session_name': session_name
            }
            
        except Exception as e:
            logger.error(f"Failed to execute JavaScript on {url}: {e}")
            return {
                'url': url,
                'result': None,
                'success': False,
                'error': str(e)
            }

    async def discover_apis(self, url: str, **options) -> Dict[str, Any]:
        """
        Discover all API calls made during page load.

        Args:
            url: URL to analyze for API calls
            **options: Additional options:
                - session_name: Browser session name (default: "default")

        Returns:
            Dictionary with discovered API calls and metadata
        """
        try:
            await self._ensure_initialized()
            browser_manager = await self._get_browser_manager()

            session_name = options.get('session_name', 'default')

            # Initialize browser session
            await browser_manager.initialize_browser(session_name)

            # Discover API calls
            result = await browser_manager.fetch_all_api_calls(url)

            logger.info(f"API discovery completed for {url}: {result.get('total_api_calls', 0)} APIs found")

            return result

        except Exception as e:
            logger.error(f"Failed to discover APIs for {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'total_api_calls': 0,
                'api_calls': []
            }

    async def fetch_api_response(self, api_pattern: str, page_url: str, **options) -> Dict[str, Any]:
        """
        Fetch complete response from a specific API call.

        Args:
            api_pattern: Pattern to match API URL
            page_url: Page URL that triggers the API call
            **options: Additional options:
                - session_name: Browser session name (default: "default")

        Returns:
            Dictionary with complete API response data
        """
        try:
            await self._ensure_initialized()
            browser_manager = await self._get_browser_manager()

            session_name = options.get('session_name', 'default')

            # Initialize browser session
            await browser_manager.initialize_browser(session_name)

            # Fetch API response
            result = await browser_manager.fetch_complete_api_response(api_pattern, page_url)

            if result.get('success'):
                logger.info(f"Successfully fetched API response for pattern '{api_pattern}'")
            else:
                logger.warning(f"Failed to fetch API response for pattern '{api_pattern}': {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Failed to fetch API response for pattern '{api_pattern}': {e}")
            return {
                'success': False,
                'error': str(e),
                'pattern': api_pattern,
                'page_url': page_url
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""
        try:
            if self._browser_manager:
                return await self._browser_manager.get_session_stats()
            else:
                return {
                    'initialized': False,
                    'total_sessions': 0,
                    'active_sessions': 0
                }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'error': str(e)}
    
    async def cleanup(self):
        """Clean up all browser resources."""
        try:
            if self._browser_manager:
                await self._browser_manager.cleanup_all_sessions()
                self._browser_manager = None
            
            self._initialized = False
            logger.info("BrowserCrawler cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


# Convenience functions for simple usage
async def fetch(url: str, config: Union[BrowserConfig, Dict[str, Any]] = None, **options) -> CrawlResult:
    """
    Convenience function to fetch a single URL.
    
    Args:
        url: URL to fetch
        config: Browser configuration
        **options: Additional options
        
    Returns:
        CrawlResult object
    """
    async with BrowserCrawler(config) as crawler:
        return await crawler.fetch(url, **options)


async def fetch_batch(urls: List[str], config: Union[BrowserConfig, Dict[str, Any]] = None, **options) -> List[CrawlResult]:
    """
    Convenience function to fetch multiple URLs.
    
    Args:
        urls: List of URLs to fetch
        config: Browser configuration
        **options: Additional options
        
    Returns:
        List of CrawlResult objects
    """
    async with BrowserCrawler(config) as crawler:
        return await crawler.fetch_batch(urls, **options)
