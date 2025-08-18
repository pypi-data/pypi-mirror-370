"""
Playwright Client for Multi-Browser Crawler
===========================================

Low-level Playwright abstraction layer that provides direct access
to Playwright browser automation capabilities.
"""

import asyncio
from typing import Dict, Any, Optional, List
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from ..exceptions.errors import BrowserInitializationError, JavaScriptExecutionError

logger = logging.getLogger(__name__)


class PlaywrightClient:
    """Low-level Playwright abstraction layer."""
    
    def __init__(self):
        """Initialize the Playwright client."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._initialized = False
    
    async def initialize(self, 
                        headless: bool = True,
                        user_data_dir: str = None,
                        proxy_config: Dict[str, Any] = None,
                        **kwargs) -> None:
        """
        Initialize Playwright browser.
        
        Args:
            headless: Whether to run browser in headless mode
            user_data_dir: User data directory for persistent sessions
            proxy_config: Proxy configuration dictionary
            **kwargs: Additional browser launch options
        """
        try:
            if self._initialized:
                return
            
            self.playwright = await async_playwright().start()
            
            # Filter out user_data_dir from kwargs to avoid conflicts
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'user_data_dir'}

            # Prepare browser launch options
            launch_options = {
                "headless": headless,
                "channel": "chrome",
                **filtered_kwargs
            }

            # Prepare context options
            context_options = {}

            if proxy_config:
                context_options["proxy"] = proxy_config
            
            # Add anti-detection arguments
            if "args" not in launch_options:
                launch_options["args"] = []
            
            launch_options["args"].extend([
                "--disable-blink-features=AutomationControlled",
                "--disable-features=VizDisplayCompositor",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",  # Disable image loading for faster browsing
                "--disable-javascript",  # Can be overridden per page
            ])
            
            # Launch browser with persistent context if user_data_dir provided
            if user_data_dir:
                # Ensure context_options doesn't contain user_data_dir
                persistent_context_options = {k: v for k, v in context_options.items() if k != 'user_data_dir'}

                self.context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=headless,
                    **persistent_context_options
                )
                self.browser = None  # Not needed for persistent context
            else:
                self.browser = await self.playwright.chromium.launch(**launch_options)
                self.context = await self.browser.new_context(**context_options)
            
            # Create initial page
            self.page = await self.context.new_page()
            
            # Apply stealth techniques
            await self._apply_stealth_techniques()
            
            self._initialized = True
            logger.info("Playwright client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright client: {e}")
            await self.cleanup()
            raise BrowserInitializationError(f"Playwright initialization failed: {e}")
    
    async def _apply_stealth_techniques(self):
        """Apply stealth techniques to avoid detection."""
        if not self.page:
            return
        
        try:
            # Override navigator.webdriver
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Override plugins
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            # Override languages
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
        except Exception as e:
            logger.warning(f"Failed to apply stealth techniques: {e}")
    
    async def navigate_to(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
        """
        if not self.page:
            raise BrowserInitializationError("Playwright client not initialized")
        
        try:
            await self.page.goto(url, wait_until=wait_until)
            logger.debug(f"Navigated to {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    async def get_html(self) -> str:
        """Get the current page HTML content."""
        if not self.page:
            raise BrowserInitializationError("Playwright client not initialized")
        
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page HTML: {e}")
            raise
    
    async def execute_javascript(self, js_code: str) -> Any:
        """
        Execute JavaScript code on the current page.
        
        Args:
            js_code: JavaScript code to execute
            
        Returns:
            Result of JavaScript execution
        """
        if not self.page:
            raise BrowserInitializationError("Playwright client not initialized")
        
        try:
            result = await self.page.evaluate(js_code)
            logger.debug(f"Executed JavaScript: {js_code[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            raise JavaScriptExecutionError(f"JavaScript execution failed: {e}")
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """
        Wait for a selector to appear on the page.
        
        Args:
            selector: CSS selector to wait for
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise BrowserInitializationError("Playwright client not initialized")
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            logger.debug(f"Found selector: {selector}")
        except Exception as e:
            logger.error(f"Failed to find selector {selector}: {e}")
            raise
    
    async def click_element(self, selector: str) -> None:
        """
        Click an element by selector.
        
        Args:
            selector: CSS selector of element to click
        """
        if not self.page:
            raise BrowserInitializationError("Playwright client not initialized")
        
        try:
            await self.page.click(selector)
            logger.debug(f"Clicked element: {selector}")
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            raise
    
    async def type_text(self, selector: str, text: str) -> None:
        """
        Type text into an element.
        
        Args:
            selector: CSS selector of input element
            text: Text to type
        """
        if not self.page:
            raise BrowserInitializationError("Playwright client not initialized")
        
        try:
            await self.page.fill(selector, text)
            logger.debug(f"Typed text into {selector}")
        except Exception as e:
            logger.error(f"Failed to type text into {selector}: {e}")
            raise
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get information about the current page."""
        if not self.page:
            return {}
        
        try:
            return {
                "url": self.page.url,
                "title": await self.page.title(),
                "viewport": self.page.viewport_size
            }
        except Exception as e:
            logger.error(f"Failed to get page info: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup Playwright resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self._initialized = False
            logger.info("Playwright client cleaned up")
            
        except Exception as e:
            logger.error(f"Error during Playwright cleanup: {e}")
    
    def is_initialized(self) -> bool:
        """Check if the client is initialized."""
        return self._initialized
