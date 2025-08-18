"""
Browser Client for Multi-Browser Crawler
========================================

High-level browser operations client that provides a simple interface
for browser automation tasks.
"""

import asyncio
from typing import Dict, Any, Optional, List, TYPE_CHECKING
import logging

from ..exceptions.errors import BrowserCrawlerError, NetworkError

if TYPE_CHECKING:
    from ..core.browser_manager import BrowserManager

logger = logging.getLogger(__name__)


class BrowserClient:
    """High-level client for browser operations."""
    
    def __init__(self, browser_manager: Optional["BrowserManager"] = None):
        """
        Initialize the browser client.
        
        Args:
            browser_manager: BrowserManager instance. If None, creates a new one.
        """
        self._browser_manager = browser_manager
        self._session_name = "default"
    
    async def _get_browser_manager(self) -> "BrowserManager":
        """Get or create a browser manager instance."""
        if self._browser_manager is None:
            from ..core.browser_manager import BrowserManager
            self._browser_manager = BrowserManager()
        return self._browser_manager
    
    async def fetch_html(self, url: str, session_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: The URL to fetch HTML from
            session_name: Browser session name (defaults to "default")
            **kwargs: Additional options for browser manager
            
        Returns:
            Dictionary containing HTML content and metadata
        """
        try:
            browser_manager = await self._get_browser_manager()
            session_name = session_name or self._session_name
            
            # Initialize browser with session
            await browser_manager.initialize_browser(session_name)
            
            # Fetch HTML content
            result = await browser_manager.fetch_html(url, **kwargs)
            
            return {
                "html": result.get("html", ""),
                "url": url,
                "session_name": session_name,
                "success": True,
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error fetching HTML from {url}: {e}")
            return {
                "html": f"<!DOCTYPE html><html><body><p>Error fetching HTML: {str(e)}</p></body></html>",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def execute_javascript(self, url: str, js_code: str, session_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Execute JavaScript on a page.
        
        Args:
            url: The URL to navigate to
            js_code: JavaScript code to execute
            session_name: Browser session name (defaults to "default")
            **kwargs: Additional options
            
        Returns:
            Dictionary containing execution result
        """
        try:
            browser_manager = await self._get_browser_manager()
            session_name = session_name or self._session_name
            
            # Initialize browser with session
            await browser_manager.initialize_browser(session_name)
            
            # Navigate to URL first
            await browser_manager.navigate_to_url(url)
            
            # Execute JavaScript
            result = await browser_manager.execute_javascript(js_code)
            
            return {
                "result": result,
                "url": url,
                "session_name": session_name,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error executing JavaScript on {url}: {e}")
            return {
                "result": None,
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def download_images(self, url: str, download_path: str = None, session_name: str = None) -> Dict[str, Any]:
        """
        Download images from a page.
        
        Args:
            url: The URL to download images from
            download_path: Directory to save images (optional)
            session_name: Browser session name (defaults to "default")
            
        Returns:
            Dictionary containing download results
        """
        try:
            browser_manager = await self._get_browser_manager()
            session_name = session_name or self._session_name
            
            # Initialize browser with session
            await browser_manager.initialize_browser(session_name)
            
            # Download images
            result = await browser_manager.download_images_from_page(url, download_path)
            
            return {
                "images": result.get("images", []),
                "url": url,
                "session_name": session_name,
                "success": True,
                "download_path": download_path
            }
            
        except Exception as e:
            logger.error(f"Error downloading images from {url}: {e}")
            return {
                "images": [],
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def fetch_batch(self, urls: List[str], session_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch HTML content from multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            session_name: Browser session name (defaults to "default")
            **kwargs: Additional options
            
        Returns:
            List of dictionaries containing results for each URL
        """
        results = []
        session_name = session_name or self._session_name
        
        for url in urls:
            result = await self.fetch_html(url, session_name, **kwargs)
            results.append(result)
        
        return results
    
    async def close_session(self, session_name: str = None):
        """
        Close a browser session.
        
        Args:
            session_name: Session name to close (defaults to current session)
        """
        try:
            if self._browser_manager:
                session_name = session_name or self._session_name
                await self._browser_manager.cleanup_session(session_name)
        except Exception as e:
            logger.error(f"Error closing session {session_name}: {e}")
    
    async def close(self):
        """Close the browser client and cleanup resources."""
        try:
            if self._browser_manager:
                await self._browser_manager.cleanup_all_sessions()
                self._browser_manager = None
        except Exception as e:
            logger.error(f"Error closing browser client: {e}")
    
    def set_session_name(self, session_name: str):
        """Set the default session name for this client."""
        self._session_name = session_name
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the browser client is healthy.
        
        Returns:
            Dictionary containing health status
        """
        try:
            browser_manager = await self._get_browser_manager()
            # Try to initialize a test session
            await browser_manager.initialize_browser("health_check")
            await browser_manager.cleanup_session("health_check")
            
            return {
                "status": "healthy",
                "browser_manager": "available"
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e)
            }
