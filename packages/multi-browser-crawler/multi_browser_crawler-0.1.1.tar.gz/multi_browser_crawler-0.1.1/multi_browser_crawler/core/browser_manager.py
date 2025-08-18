"""
Browser Manager for Multi-Browser Crawler
=========================================

Main orchestrator for browser operations with session management,
proxy support, and advanced browser automation features.

Now uses undetected-chromedriver for maximum Cloudflare bypass success.
"""

import asyncio
import os
import time
import json
from typing import Dict, Any, Optional, List
import logging

# Import the new undetected browser manager
from .undetected_browser_manager import UndetectedBrowserManager
from .session_manager import SessionManager
from .proxy_manager import ProxyManager
from ..utils.image_utils import ImageDownloader
from ..utils.web_utils import HTMLCleaner
from ..utils.js_utils import JavaScriptExecutor
from ..exceptions.errors import BrowserInitializationError, SessionError

logger = logging.getLogger(__name__)


class BrowserManager:
    """Main orchestrator for browser operations."""
    
    _instance = None
    _initialized = False
    _initializing_lock = asyncio.Lock()
    
    @classmethod
    async def get_instance(cls, config: Dict[str, Any] = None):
        """Get singleton instance of BrowserManager."""
        if cls._instance is None:
            async with cls._initializing_lock:
                if cls._instance is None:
                    cls._instance = cls(config)
                    await cls._instance._initialize()
        return cls._instance
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize BrowserManager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Core browser components - now using undetected-chromedriver
        self.undetected_manager = UndetectedBrowserManager(self.config)

        # Keep for backward compatibility (deprecated)
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Configuration
        self.headless = self.config.get('headless', True)
        self.data_folder = self.config.get('data_folder', os.path.join(os.getcwd(), "data"))
        self.max_sessions = self.config.get('max_sessions', 10)
        
        # Session management
        self.session_manager = SessionManager(
            data_folder=self.data_folder,
            max_sessions=self.max_sessions
        )
        self.current_session_id = None
        self.session_name = None
        self.user_data_dir = None
        
        # Proxy management
        proxy_config = self.config.get('proxy', {})
        self.proxy_manager = ProxyManager(
            proxy_file=proxy_config.get('file', 'proxies.txt'),
            enabled=proxy_config.get('enabled', False),
            allow_direct_connection=proxy_config.get('allow_direct', True)
        )
        
        # Utility components
        self.image_downloader = ImageDownloader(
            data_folder=self.data_folder,
            web_prefix=self.config.get('web_prefix')
        )
        self.html_cleaner = HTMLCleaner()
        self.js_executor = JavaScriptExecutor()
        
        # Cache
        self.html_cache = {}
        self.cache_timestamps = {}
        self.cache_expiry = self.config.get('cache_expiry', 3600)  # 1 hour default
        
        # Counters and limits
        self.fetch_count = 0
        self.fetch_limit = self.config.get('fetch_limit', 1000)
        
        BrowserManager._initialized = True
    
    async def _initialize(self):
        """Initialize the browser manager."""
        if BrowserManager._initialized:
            return

        try:
            logger.info("Initializing BrowserManager...")

            # Test proxies if enabled
            if self.proxy_manager.is_enabled():
                await self.proxy_manager.test_all_proxies()

            BrowserManager._initialized = True
            logger.info("BrowserManager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize BrowserManager: {e}")
            raise BrowserInitializationError(f"Initialization failed: {e}")
    
    async def initialize_browser(self, session_name: str = "default") -> None:
        """
        Initialize browser with session management.
        
        Args:
            session_name: Name of the browser session
        """
        try:
            # Get session strategy
            session_id, user_data_dir, is_new_session = self.session_manager.get_session_strategy(session_name)
            
            self.current_session_id = session_id
            self.session_name = session_name
            self.user_data_dir = user_data_dir
            
            if is_new_session:
                logger.info(f"Creating new browser session: {session_id}")
            else:
                logger.info(f"Reusing existing browser session: {session_id}")
            
            # Initialize Playwright if not already done
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # Get proxy configuration
            proxy_config = None
            if self.proxy_manager.is_enabled():
                proxy = await self.proxy_manager.get_next_proxy()
                if proxy and proxy != "DIRECT":
                    proxy_config = self.proxy_manager.get_proxy_config_for_playwright(proxy)
            
            # Browser launch options - use configuration instead of hardcoded args
            launch_options = self.config.get_browser_launch_options()
            
            # Context options (excluding user_data_dir since it's passed as positional arg)
            context_options = {
                "no_viewport": True
            }

            if proxy_config:
                context_options["proxy"] = proxy_config
                logger.info(f"Using proxy: {proxy}")

            # Launch persistent context
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=self.headless,
                **context_options
            )
            
            # Get or create page
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()
            
            # Apply stealth techniques
            await self._apply_stealth_techniques()
            
            # Set up image downloader
            await self.image_downloader.set_browser_page(self.page)
            
            # Register session
            if is_new_session:
                # Get browser process PID (approximate)
                import psutil
                browser_pids = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                            cmdline = proc.info.get('cmdline', [])
                            if any(user_data_dir in arg for arg in cmdline):
                                browser_pids.append(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if browser_pids:
                    self.session_manager.register_session(session_id, browser_pids[0], session_name)
            
            logger.info(f"Browser initialized for session: {session_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise BrowserInitializationError(f"Browser initialization failed: {e}")
    
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
            
            logger.debug("Applied stealth techniques")
            
        except Exception as e:
            logger.warning(f"Failed to apply stealth techniques: {e}")
    
    async def navigate_to_url(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
        """
        if not self.page:
            raise BrowserInitializationError("Browser not initialized")
        
        try:
            await self.page.goto(url, wait_until=wait_until)
            logger.debug(f"Navigated to {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    async def fetch_html(self, url: str, use_cache: bool = False, clean: bool = True,
                        timeout: float = None, proxy_config: Dict = None,
                        js_action: str = None) -> Dict[str, Any]:
        """
        Fetch HTML content from a URL using undetected-chromedriver.

        Args:
            url: URL to fetch
            use_cache: Whether to use cached content
            clean: Whether to clean the HTML
            timeout: Request timeout in seconds
            proxy_config: Proxy configuration
            js_action: JavaScript to execute after page load

        Returns:
            Dictionary containing HTML and metadata
        """
        # Check cache first
        if use_cache and hasattr(self, 'html_cache') and url in self.html_cache:
            cache_time = getattr(self, 'cache_timestamps', {}).get(url, 0)
            cache_expiry = getattr(self, 'cache_expiry', 3600)
            if time.time() - cache_time < cache_expiry:
                logger.debug(f"Returning cached HTML for {url}")
                return self.html_cache[url]

        # Check fetch limit
        fetch_limit = getattr(self, 'fetch_limit', 1000)
        fetch_count = getattr(self, 'fetch_count', 0)
        if fetch_count >= fetch_limit:
            raise Exception(f"Fetch limit ({fetch_limit}) reached")

        try:
            # Use undetected browser manager
            result = await self.undetected_manager.fetch_html(
                url=url,
                timeout=timeout,
                proxy_config=proxy_config,
                js_action=js_action,
                session_id=self.current_session_id
            )

            # Clean HTML if requested and successful
            if clean and result.get('status') == 'success':
                html_content = result['html']
                if hasattr(self, 'html_cleaner'):
                    html_content = self.html_cleaner.clean_html(html_content)
                result['html'] = html_content

            # Add session info
            result['session_id'] = getattr(self, 'current_session_id', None)
            result['timestamp'] = time.time()

            # Cache result
            if use_cache and result.get('status') == 'success':
                if not hasattr(self, 'html_cache'):
                    self.html_cache = {}
                    self.cache_timestamps = {}
                self.html_cache[url] = result
                self.cache_timestamps[url] = time.time()

            # Update counters
            if not hasattr(self, 'fetch_count'):
                self.fetch_count = 0
            self.fetch_count += 1

            if hasattr(self, 'session_manager') and self.current_session_id:
                self.session_manager.update_session_usage(self.current_session_id)

            logger.info(f"Fetched HTML from {url} ({len(result.get('html', ''))} chars) - Status: {result.get('status')}")

            return result

        except Exception as e:
            logger.error(f"Failed to fetch HTML from {url}: {e}")
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
            raise BrowserInitializationError("Browser not initialized")

        return await self.js_executor.execute_script(self.page, js_code)

    async def download_images_from_page(self, url: str, download_path: str = None) -> Dict[str, Any]:
        """
        Download images from a page.

        Args:
            url: URL of the page
            download_path: Directory to save images (optional)

        Returns:
            Dictionary with download results
        """
        if not self.page:
            await self.initialize_browser()

        return await self.image_downloader.download_images_from_page(url, download_path)

    async def fetch_all_api_calls(self, url: str) -> Dict[str, Any]:
        """
        Discover all API calls made during page load with network sniffing.

        Args:
            url: URL to load and discover API calls from

        Returns:
            Dictionary containing discovered API calls with sample data and usage hints
        """
        try:
            if not self.page:
                await self.initialize_browser()

            logger.info(f"Starting API discovery for {url}")

            # Set up comprehensive API capture
            captured_responses = []

            async def handle_response(response):
                try:
                    # Capture all network requests
                    url_str = response.url
                    method = response.request.method
                    status = response.status
                    headers = dict(response.headers)

                    # Get response size
                    response_size = 0
                    try:
                        body = await response.body()
                        response_size = len(body) if body else 0
                    except:
                        pass

                    # Parse URL components
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(url_str)

                    # Get response preview (first 200 chars)
                    response_preview = ""
                    try:
                        if response_size > 0 and response_size < 10000:  # Only for small responses
                            body = await response.body()
                            if body:
                                response_preview = body.decode('utf-8', errors='ignore')[:200]
                    except:
                        pass

                    captured_responses.append({
                        "url": url_str,
                        "method": method,
                        "status": status,
                        "response_size": response_size,
                        "content_type": headers.get('content-type', ''),
                        "domain": parsed.netloc,
                        "path": parsed.path,
                        "query_params": parse_qs(parsed.query),
                        "headers": {k: v for k, v in headers.items() if k.lower() in ['content-type', 'content-length', 'cache-control']},
                        "response_preview": response_preview
                    })

                except Exception as e:
                    logger.warning(f"Error capturing response {response.url}: {e}")

            # Set up response handler
            self.page.on("response", handle_response)

            try:
                # Navigate to the page
                await self.page.goto(url, wait_until="networkidle", timeout=self.config.get('page_timeout', 30000))

                # Wait a bit more for any delayed API calls
                await asyncio.sleep(2)

                # Remove the response handler
                self.page.remove_listener("response", handle_response)

                # Process and categorize the captured responses
                api_calls = []
                other_requests = []

                for response in captured_responses:
                    # Categorize as API call vs other request
                    is_api = (
                        '/api/' in response['path'] or
                        '/graphql' in response['path'] or
                        response['content_type'].startswith('application/json') or
                        response['method'] in ['POST', 'PUT', 'PATCH'] or
                        any(keyword in response['path'].lower() for keyword in ['ajax', 'xhr', 'fetch', 'data'])
                    )

                    if is_api:
                        api_calls.append(response)
                    else:
                        other_requests.append(response)

                logger.info(f"API discovery completed: {len(api_calls)} API calls, {len(other_requests)} other requests")

                return {
                    "success": True,
                    "url": url,
                    "total_requests": len(captured_responses),
                    "total_api_calls": len(api_calls),
                    "api_calls_count": len(api_calls),
                    "other_requests_count": len(other_requests),
                    "api_calls": api_calls[:10],  # Limit to first 10 for display
                    "other_requests": other_requests[:5],  # Show some other requests for context
                    "api_call_summary": {
                        "json_apis": len([r for r in api_calls if 'json' in r['content_type']]),
                        "graphql_apis": len([r for r in api_calls if 'graphql' in r['path']]),
                        "other_apis": len([r for r in api_calls if 'json' not in r['content_type'] and 'graphql' not in r['path']])
                    },
                    "discovery_summary": {
                        "domains_found": list(set(r['domain'] for r in captured_responses)),
                        "methods_used": list(set(r['method'] for r in captured_responses)),
                        "content_types": list(set(r['content_type'] for r in captured_responses if r['content_type']))
                    },
                    "usage_hint": "Use fetch_complete_api_response() with specific API URL patterns to get full response data"
                }

            except Exception as e:
                # Clean up response handler
                try:
                    self.page.remove_listener("response", handle_response)
                except:
                    pass
                raise e

        except Exception as e:
            logger.exception(f"Error in fetch_all_api_calls: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "total_api_calls": 0,
                "api_calls": []
            }

    async def fetch_complete_api_response(self, api_url_pattern: str, page_url: str) -> Dict[str, Any]:
        """
        Fetch complete response from a specific API call.

        Args:
            api_url_pattern: Pattern to match API URL (e.g., "/api/posts", "graphql", "api.example.com")
            page_url: Original page URL that triggers the API call

        Returns:
            Dictionary containing the complete API response data
        """
        try:
            if not self.page:
                await self.initialize_browser()

            logger.info(f"Fetching complete API response for pattern '{api_url_pattern}' from {page_url}")

            # Set up targeted API capture
            captured_response = None

            async def handle_response(response):
                nonlocal captured_response
                try:
                    url_str = response.url

                    # Check if this response matches our pattern
                    if api_url_pattern.lower() in url_str.lower():
                        # Get complete response data
                        body = await response.body()
                        headers = dict(response.headers)

                        # Try to parse JSON response
                        response_data = None
                        if body:
                            try:
                                response_text = body.decode('utf-8', errors='ignore')
                                if headers.get('content-type', '').startswith('application/json'):
                                    import json
                                    response_data = json.loads(response_text)
                                else:
                                    response_data = response_text
                            except:
                                response_data = body.decode('utf-8', errors='ignore')

                        captured_response = {
                            "url": url_str,
                            "method": response.request.method,
                            "status": response.status,
                            "headers": headers,
                            "response_data": response_data,
                            "response_size": len(body) if body else 0,
                            "content_type": headers.get('content-type', ''),
                            "success": True
                        }

                        logger.info(f"Captured API response: {url_str} ({len(body) if body else 0} bytes)")

                except Exception as e:
                    logger.warning(f"Error capturing API response {response.url}: {e}")

            # Set up response handler
            self.page.on("response", handle_response)

            try:
                # Navigate to the page
                await self.page.goto(page_url, wait_until="networkidle", timeout=self.config.get('page_timeout', 30000))

                # Wait for API calls to complete
                await asyncio.sleep(3)

                # Remove the response handler
                self.page.remove_listener("response", handle_response)

                if captured_response:
                    logger.info(f"Successfully captured API response for pattern '{api_url_pattern}'")
                    return captured_response
                else:
                    logger.warning(f"No API response found matching pattern '{api_url_pattern}'")
                    return {
                        "success": False,
                        "error": f"No API response found matching pattern '{api_url_pattern}'",
                        "pattern": api_url_pattern,
                        "page_url": page_url
                    }

            except Exception as e:
                # Clean up response handler
                try:
                    self.page.remove_listener("response", handle_response)
                except:
                    pass
                raise e

        except Exception as e:
            logger.exception(f"Error in fetch_complete_api_response: {e}")
            return {
                "success": False,
                "error": str(e),
                "pattern": api_url_pattern,
                "page_url": page_url
            }

    async def cleanup_session(self, session_name: str = None) -> bool:
        """
        Clean up a browser session.

        Args:
            session_name: Session name to clean up (defaults to current)

        Returns:
            True if cleanup was successful
        """
        try:
            session_name = session_name or self.session_name

            if session_name and self.current_session_id:
                # Close browser resources
                if self.page:
                    await self.page.close()
                    self.page = None

                if self.context:
                    await self.context.close()
                    self.context = None

                # Unregister session
                self.session_manager.unregister_session(self.current_session_id, cleanup_directory=True)

                logger.info(f"Cleaned up session: {session_name}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error cleaning up session {session_name}: {e}")
            return False

    async def cleanup_all_sessions(self) -> Dict[str, bool]:
        """
        Clean up all browser sessions.

        Returns:
            Dictionary mapping session names to cleanup success status
        """
        results = {}

        try:
            # Get all sessions
            sessions = self.session_manager.list_sessions()

            for session in sessions:
                session_name = session.get('session_name')
                if session_name:
                    results[session_name] = await self.cleanup_session(session_name)

            # Close playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            logger.info(f"Cleaned up {len(results)} sessions")

        except Exception as e:
            logger.error(f"Error during cleanup all sessions: {e}")

        return results

    async def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about browser sessions."""
        sessions = self.session_manager.list_sessions()

        active_sessions = [s for s in sessions if s.get('is_active', False)]

        return {
            'total_sessions': len(sessions),
            'active_sessions': len(active_sessions),
            'current_session': self.current_session_id,
            'fetch_count': self.fetch_count,
            'fetch_limit': self.fetch_limit,
            'cache_size': len(self.html_cache),
            'proxy_enabled': self.proxy_manager.is_enabled(),
            'proxy_stats': self.proxy_manager.get_status() if self.proxy_manager.is_enabled() else None
        }

    async def clear_cache(self):
        """Clear HTML cache."""
        self.html_cache.clear()
        self.cache_timestamps.clear()
        logger.info("Cleared HTML cache")

    def is_initialized(self) -> bool:
        """Check if browser is initialized."""
        return self.page is not None and not self.page.is_closed()

    async def close(self):
        """Close the browser manager and cleanup all resources."""
        try:
            await self.cleanup_all_sessions()

            # Reset class state
            BrowserManager._instance = None
            BrowserManager._initialized = False

            logger.info("BrowserManager closed")

        except Exception as e:
            logger.error(f"Error closing BrowserManager: {e}")

    async def _execute_advanced_cleanup(self):
        """Execute advanced JavaScript cleanup on the current page."""
        try:
            import os
            cleanup_js_path = os.path.join(os.path.dirname(__file__), '..', 'js', 'cleanup_page.js')

            if os.path.exists(cleanup_js_path):
                with open(cleanup_js_path, 'r', encoding='utf-8') as f:
                    cleanup_js = f.read()

                # Execute the cleanup script
                await self.page.evaluate(cleanup_js)

                # Call the cleanup function with comprehensive settings
                await self.page.evaluate("""
                    cleanupPageAdvanced({
                        logResults: false,
                        removeTags: ['script', 'style', 'iframe', 'noscript', 'meta', 'link', 'object', 'embed', 'svg'],
                        remove1x1Images: true,
                        removeStyleAttribute: true,
                        removeDeprecatedStyleAttributes: true,
                        removeDataAttributes: false,
                        removeBootstrapClasses: false,
                        removeTailwindClasses: false,
                        removeAds: true,
                        removeSvgImages: true
                    });
                """)

                logger.info("Advanced JavaScript cleanup executed successfully")
            else:
                logger.warning(f"Cleanup script not found at {cleanup_js_path}")

        except Exception as e:
            logger.warning(f"Advanced cleanup failed: {e}")

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
