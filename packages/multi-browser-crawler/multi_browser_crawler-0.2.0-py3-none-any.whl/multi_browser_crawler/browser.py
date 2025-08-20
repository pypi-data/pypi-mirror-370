#!/usr/bin/env python3
"""
Clean Browser Pool Manager
==========================

Minimal, clean browser pool management with direct undetected-chromedriver integration.
No dependencies on other browser managers - handles everything directly.
"""

import asyncio
import os
import time
import uuid
import logging
from typing import Dict, Optional, Set, List, Any
from dataclasses import dataclass
from enum import Enum

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
except ImportError:
    raise ImportError("undetected-chromedriver and selenium are required. Install with: pip install undetected-chromedriver selenium")

from .debug_port_manager import DebugPortManager

logger = logging.getLogger(__name__)


@dataclass
class BrowserInstance:
    """Represents a browser instance in the pool"""
    browser_id: str
    driver: uc.Chrome  # Direct undetected Chrome driver
    session_id: Optional[str]  # None = non-persistent, str = persistent
    debug_port: int
    user_data_dir: Optional[str]
    proxy_config: Optional[Dict]
    created_at: float
    last_used: float
    in_use: bool = False
    request_count: int = 0

    @property
    def is_persistent(self) -> bool:
        """Check if this is a persistent browser (has session_id)"""
        return self.session_id is not None


class BrowserPoolManager:
    """
    Clean, minimal browser pool manager with direct undetected-chromedriver integration.
    No dependencies on other browser managers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize browser pool manager.
        
        Args:
            config: Configuration dictionary with:
                - BROWSER_DATA_DIR: Directory for browser data (required)
                - DOWNLOAD_IMAGES_DIR: Directory for downloaded images (optional)
                - PROXY_FILE_PATH: Path to proxy file (optional)
                - BROWSER_HEADLESS: Whether to run headless (default: True)
                - BROWSER_TIMEOUT: Browser timeout in milliseconds (default: 30000)
                - min_browsers: Minimum browsers in pool (default: 2)
                - max_browsers: Maximum browsers in pool (default: 10)
                - browser_timeout: Browser lifetime in seconds (default: 3600)
                - max_requests_per_browser: Max requests per browser (default: 100)
                - idle_timeout: Idle timeout in seconds (default: 600)
        """
        self.config = config
        
        # Required directories
        self.browser_data_dir = config.get('BROWSER_DATA_DIR')
        if not self.browser_data_dir:
            raise ValueError("BROWSER_DATA_DIR is required")

        self.download_images_dir = config.get('DOWNLOAD_IMAGES_DIR', '/tmp/browser_images')

        # Create timestamped run folder with subfolders for this run
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_base_dir = os.path.join(self.browser_data_dir, timestamp)
        self.session_dir = os.path.join(self.run_base_dir, "sessions")  # Persistent sessions
        self.temp_dir = os.path.join(self.run_base_dir, "temp")        # Non-persistent browsers
        self.proxy_file_path = config.get('PROXY_FILE_PATH')
        
        # Browser settings
        self.headless = config.get('BROWSER_HEADLESS', True)
        self.timeout = config.get('BROWSER_TIMEOUT', 30000) / 1000  # Convert to seconds
        
        # Pool configuration
        self.min_browsers = config.get('min_browsers', 2)
        self.max_browsers = config.get('max_browsers', 10)
        self.browser_timeout = config.get('browser_timeout', 3600)  # 1 hour
        self.max_requests_per_browser = config.get('max_requests_per_browser', 100)
        self.idle_timeout = config.get('IDLE_TIMEOUT', 600)  # 10 minutes
        
        # Pool state
        self.browsers: Dict[str, BrowserInstance] = {}
        self.persistent_sessions: Dict[str, str] = {}  # session_id -> browser_id

        # Debug port management
        debug_port_start = config.get('DEBUG_PORT_START', 9222)
        debug_port_end = config.get('DEBUG_PORT_END', 9322)
        self.debug_port_manager = DebugPortManager(debug_port_start, debug_port_end)
        
        # Use simplified ProxyManager
        self.proxy_manager = None
        if self.proxy_file_path:
            from .proxy_manager import ProxyManager
            try:
                self.proxy_manager = ProxyManager(proxy_file=self.proxy_file_path)
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Failed to initialize ProxyManager: {e}")
                self.proxy_manager = None
        
        # Thread safety
        self._pool_lock = asyncio.Lock()

        # Cleanup task
        self._cleanup_task = None
        self._shutdown_event = asyncio.Event()
        
        # Clean up any leftover browser data from previous runs
        self._cleanup_leftover_browser_data()

        # Ensure directories exist
        os.makedirs(self.browser_data_dir, exist_ok=True)
        if self.download_images_dir:
            os.makedirs(self.download_images_dir, exist_ok=True)

        # Initialize proxy manager
        if self.proxy_manager:
            asyncio.create_task(self._initialize_proxy_manager())

        # Start cleanup task for idle browsers
        self._cleanup_task = asyncio.create_task(self._cleanup_idle_browsers())

        logger.info(f"BrowserPoolManager initialized: {self.min_browsers}-{self.max_browsers} browsers")
        logger.info(f"Proxy support: {'enabled' if self.proxy_manager else 'disabled'}")
        logger.info(f"Idle timeout: {self.idle_timeout} seconds")

    def _cleanup_leftover_browser_data(self):
        """Clean up any leftover browser data from previous runs."""
        if not os.path.exists(self.browser_data_dir):
            return

        logger.info(f"Checking for leftover browser data in: {self.browser_data_dir}")

        try:
            # Get all items in browser data directory
            items = os.listdir(self.browser_data_dir)
            timestamped_dirs = []

            # Look for timestamped directories (YYYYMMDD_HHMMSS pattern)
            import re
            timestamp_pattern = re.compile(r'^\d{8}_\d{6}$')

            for item in items:
                item_path = os.path.join(self.browser_data_dir, item)
                if os.path.isdir(item_path) and timestamp_pattern.match(item):
                    timestamped_dirs.append(item_path)

            # Clean up old timestamped directories (simple removal)
            if timestamped_dirs:
                logger.info(f"Found {len(timestamped_dirs)} leftover timestamped run folders")
                for timestamped_dir in timestamped_dirs:
                    self._safe_remove_directory(timestamped_dir, "leftover run folder")

            if not timestamped_dirs:
                logger.debug("No leftover timestamped session folders found")

        except Exception as e:
            logger.error(f"Error during startup cleanup: {e}")

    def _setup_user_data_directory(self, session_id: Optional[str], browser_id: str) -> str:
        """
        Setup user data directory for browser.

        Args:
            session_id: Session ID for persistent browsers (None for non-persistent)
            browser_id: Unique browser identifier

        Returns:
            Path to the user data directory
        """
        if session_id:  # Persistent browser
            user_data_dir = os.path.join(self.session_dir, session_id)
        else:  # Non-persistent browser
            user_data_dir = os.path.join(self.temp_dir, f"temp_{browser_id}")

        os.makedirs(user_data_dir, exist_ok=True)
        return user_data_dir

    def _safe_remove_directory(self, dir_path: str, description: str = "directory") -> bool:
        """
        Safely remove a directory with proper error handling and logging.

        Args:
            dir_path: Path to the directory to remove
            description: Human-readable description for logging

        Returns:
            True if removal was successful, False otherwise
        """
        try:
            import shutil
            shutil.rmtree(dir_path)
            dir_name = os.path.basename(dir_path)
            logger.info(f"Cleaned up {description}: {dir_name}")
            return True
        except Exception as e:
            dir_name = os.path.basename(dir_path)
            logger.debug(f"Could not clean up {description} {dir_name}: {e} (not critical)")
            return False

    def _set_browser_state(self, browser: BrowserInstance, in_use: bool, session_id: Optional[str] = None) -> None:
        """
        Set browser state and update last used time.

        Args:
            browser: Browser instance to update
            in_use: Whether browser is in use
            session_id: Optional session ID to assign (for reusing browsers)
        """
        browser.in_use = in_use
        browser.last_used = time.time()

        # Update session_id if provided (for browser reuse)
        if session_id is not None:
            browser.session_id = session_id

    async def _initialize_proxy_manager(self):
        """Initialize the proxy manager"""
        try:
            await self.proxy_manager.load_and_test_proxies()
            stats = await self.proxy_manager.get_stats()
            logger.info(f"ProxyManager initialized: {stats}")
        except Exception as e:
            logger.error(f"Failed to initialize ProxyManager: {e}")

    async def _cleanup_idle_browsers(self):
        """Background task to cleanup idle browsers"""
        logger.info(f"Starting idle browser cleanup task (idle_timeout: {self.idle_timeout}s)")
        while not self._shutdown_event.is_set():
            try:
                # Wait for either shutdown or cleanup interval
                cleanup_interval = min(10, self.idle_timeout / 3)
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=cleanup_interval
                )
                break  # Shutdown event was set
            except asyncio.TimeoutError:
                # Time to check for idle browsers
                logger.debug(f"Running idle browser cleanup check")
                await self._cleanup_idle_browsers_now()
        logger.info("Idle browser cleanup task stopped")

    async def _cleanup_idle_browsers_now(self):
        """Clean up browsers that have been idle too long"""
        current_time = time.time()
        browsers_to_remove = []

        async with self._pool_lock:
            logger.debug(f"Checking {len(self.browsers)} browsers for idle cleanup")
            for browser_id, browser in self.browsers.items():
                idle_time = current_time - browser.last_used
                logger.debug(f"Browser {browser_id}: idle={idle_time:.1f}s, persistent={browser.is_persistent}, in_use={browser.in_use}")

                # Only cleanup persistent browsers that are idle and not in use
                if (browser.is_persistent and
                    not browser.in_use and
                    idle_time > self.idle_timeout):
                    browsers_to_remove.append(browser_id)
                    logger.info(f"Marking idle browser {browser_id} for cleanup (idle: {idle_time:.1f}s)")

        # Remove idle browsers
        for browser_id in browsers_to_remove:
            try:
                await self._remove_browser(browser_id)
                logger.info(f"Cleaned up idle browser: {browser_id}")
            except Exception as e:
                logger.error(f"Error cleaning up idle browser {browser_id}: {e}")

    def _create_chrome_options(self, debug_port: int, user_data_dir: Optional[str],
                              proxy_config: Optional[Dict] = None) -> ChromeOptions:
        """Create Chrome options for undetected-chromedriver"""
        options = ChromeOptions()
        
        # Basic options
        if self.headless:
            options.add_argument("--headless=new")
        
        # Window and performance options
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # Debug port
        options.add_argument(f"--remote-debugging-port={debug_port}")
        
        # User data directory for persistent browsers
        if user_data_dir:
            options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Proxy configuration (proxy_config is already Chrome-ready format)
        if proxy_config:
            proxy_string = f"{proxy_config['host']}:{proxy_config['port']}"
            options.add_argument(f"--proxy-server={proxy_string}")

            if 'username' in proxy_config and 'password' in proxy_config:
                # For authenticated proxies, we'll need to handle this differently
                # This is a simplified version - full auth proxy support needs more work
                pass
        
        return options
    




    async def _get_proxy(self, random_selection: bool = False) -> Optional[Dict]:
        """Get proxy configuration from ProxyManager (Chrome-ready format)"""
        if not self.proxy_manager:
            return None

        return await self.proxy_manager.get_proxy(random=random_selection)

    async def _test_proxy_if_failed(self, proxy_config: Optional[Dict]) -> bool:
        """
        Test a proxy if there was an exception.
        Returns True if proxy is good, False if proxy failed (and marks it failed).
        Upper app can use this to determine if exception was proxy-related.
        """
        if not proxy_config or not self.proxy_manager:
            return False

        return await self.proxy_manager.test_proxy(proxy_config)
    
    async def _create_browser(self, session_id: Optional[str],
                             use_proxy: bool = False) -> BrowserInstance:
        """Create a new browser instance with direct undetected-chromedriver"""
        browser_id = f"browser_{uuid.uuid4().hex[:8]}"
        debug_port = await self.debug_port_manager.allocate_port()
        
        # Setup proxy configuration using ProxyManager (Chrome-ready format)
        proxy_config = None
        if use_proxy:
            proxy_config = await self._get_proxy(random_selection=True)
        
        # Setup user data directory for browsers
        user_data_dir = self._setup_user_data_directory(session_id, browser_id)
        
        # Create Chrome options
        options = self._create_chrome_options(debug_port, user_data_dir, proxy_config)
        
        # Create undetected Chrome driver directly
        try:
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                driver_executable_path=None,  # Auto-download if needed
            )
            
            # Set timeouts
            driver.set_page_load_timeout(self.timeout)
            driver.implicitly_wait(10)  # 10 seconds for element finding
            
        except Exception as e:
            await self.debug_port_manager.release_port(debug_port)
            raise RuntimeError(f"Failed to create Chrome driver: {e}")
        
        # Create browser instance
        browser = BrowserInstance(
            browser_id=browser_id,
            driver=driver,
            session_id=session_id,
            debug_port=debug_port,
            user_data_dir=user_data_dir,
            proxy_config=proxy_config,
            created_at=time.time(),
            last_used=time.time(),
            in_use=True
        )
        
        # Add to pool
        self.browsers[browser_id] = browser
        
        # Register persistent session
        if session_id:  # Persistent browser
            self.persistent_sessions[session_id] = browser_id

        browser_type_str = "persistent" if session_id else "non-persistent"
        logger.info(f"Created browser {browser_id} (type: {browser_type_str}, proxy: {bool(proxy_config)})")
        return browser

    async def get_browser(self, session_id: Optional[str] = None,
                         use_proxy: Optional[bool] = None) -> BrowserInstance:
        """
        Get a browser instance from the pool.

        Args:
            session_id: Session ID for persistent browsers (None = non-persistent)
            use_proxy: Whether to use proxy for this browser (None = auto-detect from proxy availability)

        Returns:
            BrowserInstance ready for use
        """
        # Auto-detect proxy usage if not specified
        if use_proxy is None:
            use_proxy = self.proxy_manager is not None
        async with self._pool_lock:
            # Check for existing persistent session
            if session_id:  # Persistent browser
                if session_id in self.persistent_sessions:
                    browser_id = self.persistent_sessions[session_id]
                    if browser_id in self.browsers:
                        browser = self.browsers[browser_id]
                        if not browser.in_use and not self._should_rotate_browser(browser):
                            self._set_browser_state(browser, in_use=True)
                            logger.info(f"Reusing persistent session browser {browser_id}")
                            return browser

            # Try to find available browser of requested type
            available_browser = self._find_available_browser(session_id, use_proxy)
            if available_browser:
                self._set_browser_state(available_browser, in_use=True, session_id=session_id)

                # Register persistent session
                if session_id:  # Persistent browser
                    self.persistent_sessions[session_id] = available_browser.browser_id

                logger.info(f"Assigned existing browser {available_browser.browser_id}")
                return available_browser

            # Create new browser if under max limit
            if len(self.browsers) < self.max_browsers:
                browser = await self._create_browser(session_id, use_proxy)
                logger.info(f"Created new browser {browser.browser_id}")
                return browser

            # Wait for browser to become available (simplified - just raise error for now)
            raise RuntimeError("Browser pool at capacity and no browsers available")

    def _find_available_browser(self, session_id: Optional[str], use_proxy: bool = False) -> Optional[BrowserInstance]:
        """Find an available browser of the specified type and proxy requirement"""
        is_persistent = session_id is not None

        for browser in self.browsers.values():
            if (not browser.in_use and
                browser.is_persistent == is_persistent and
                not self._should_rotate_browser(browser) and
                bool(browser.proxy_config) == use_proxy):  # Match proxy requirement
                return browser
        return None

    def _should_rotate_browser(self, browser: BrowserInstance) -> bool:
        """Check if browser should be rotated"""
        # Rotate based on request count
        if browser.request_count >= self.max_requests_per_browser:
            return True

        # Rotate based on age
        age = time.time() - browser.created_at
        if age > self.browser_timeout:
            return True

        return False

    async def return_browser(self, browser: BrowserInstance):
        """Return a browser to the pool"""
        async with self._pool_lock:
            if browser.browser_id in self.browsers:
                self._set_browser_state(browser, in_use=False)
                logger.debug(f"Returned browser {browser.browser_id} to pool")

    async def _remove_browser(self, browser_id: str):
        """Remove and cleanup a browser"""
        if browser_id not in self.browsers:
            return

        browser = self.browsers[browser_id]

        try:
            # Close browser driver
            browser.driver.quit()
        except Exception as e:
            logger.warning(f"Error closing browser {browser_id}: {e}")

        # Release debug port
        await self.debug_port_manager.release_port(browser.debug_port)

        # Clean up user data directory if it exists
        if browser.user_data_dir and os.path.exists(browser.user_data_dir):
            self._safe_remove_directory(browser.user_data_dir, "user data directory")

        # Remove from persistent sessions if applicable
        if browser.session_id and browser.session_id in self.persistent_sessions:
            if self.persistent_sessions[browser.session_id] == browser_id:
                del self.persistent_sessions[browser.session_id]

        # Remove from pool
        del self.browsers[browser_id]
        logger.info(f"Removed browser {browser_id} from pool")

    async def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        total_browsers = len(self.browsers)
        in_use = sum(1 for b in self.browsers.values() if b.in_use)
        persistent = sum(1 for b in self.browsers.values() if b.is_persistent)

        return {
            'total_browsers': total_browsers,
            'in_use': in_use,
            'available': total_browsers - in_use,
            'persistent_browsers': persistent,
            'non_persistent_browsers': total_browsers - persistent,
            'persistent_sessions': len(self.persistent_sessions),
            'debug_port_stats': await self.debug_port_manager.get_stats(),
            'proxy_stats': await self.proxy_manager.get_stats() if self.proxy_manager else None,
            'idle_timeout': self.idle_timeout
        }

    async def shutdown(self):
        """Shutdown the browser pool and clean up all resources"""
        logger.info("Shutting down BrowserPoolManager...")

        # Stop cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._shutdown_event.set()
            try:
                await asyncio.wait_for(self._cleanup_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Cleanup task did not finish in time, cancelling")
                self._cleanup_task.cancel()

        async with self._pool_lock:
            # Close all browsers
            for browser_id in list(self.browsers.keys()):
                await self._remove_browser(browser_id)

            # Clean up current run folder
            if os.path.exists(self.run_base_dir):
                self._safe_remove_directory(self.run_base_dir, "current run folder")

            # Reset state
            self.browsers.clear()
            self.persistent_sessions.clear()
            await self.debug_port_manager.reset()

        logger.info("BrowserPoolManager shutdown complete")

    # High-level fetch_html method

    async def fetch_html(self, url: str, session_id: Optional[str] = None,
                        use_proxy: Optional[bool] = None, js_action: Optional[str] = None,
                        timeout: Optional[int] = None, headless: Optional[bool] = None,
                        wait_until: str = "domcontentloaded") -> Dict[str, Any]:
        """
        Fetch HTML content from a URL using browser pool management.

        Args:
            url: URL to fetch
            session_id: Session ID for persistent browsers (None for non-persistent)
            use_proxy: Whether to use proxy (None = auto-detect from proxy availability)
            js_action: JavaScript to execute after page load
            timeout: Request timeout in seconds (None = use default)
            headless: Override headless setting (None = use default)
            wait_until: Wait condition ('domcontentloaded', 'load', 'networkidle')

        Returns:
            Dictionary with HTML content and metadata:
            {
                'html': str,
                'url': str,
                'title': str,
                'cookies': List[Dict],
                'load_time': float,
                'status': str,
                'browser_metadata': Dict
            }
        """
        # Get browser from pool (browser type determined by session_id)
        browser = await self.get_browser(session_id, use_proxy)

        start_time = time.time()

        try:
            # Navigate to URL
            logger.info(f"Navigating to: {url}")
            browser.driver.get(url)

            # Wait for page load based on condition
            if wait_until == "domcontentloaded":
                WebDriverWait(browser.driver, timeout or self.timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            elif wait_until == "load":
                WebDriverWait(browser.driver, timeout or self.timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            elif wait_until == "networkidle":
                # Simple networkidle simulation - wait a bit after page load
                WebDriverWait(browser.driver, timeout or self.timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                await asyncio.sleep(2)  # Wait for additional network requests

            # Execute custom JavaScript if provided
            if js_action:
                try:
                    result = browser.driver.execute_script(js_action)
                    logger.info(f"JavaScript execution result: {result}")
                except Exception as e:
                    logger.warning(f"JavaScript execution failed: {e}")

            # Get page content
            html_content = browser.driver.page_source
            final_url = browser.driver.current_url
            title = browser.driver.title

            # Get cookies
            cookies = []
            for cookie in browser.driver.get_cookies():
                cookies.append({
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', ''),
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False)
                })

            load_time = time.time() - start_time

            # Update browser usage
            browser.request_count += 1
            browser.last_used = time.time()

            logger.info(f"Successfully fetched {url} in {load_time:.2f}s")

            return {
                'html': html_content,
                'url': final_url,
                'title': title,
                'cookies': cookies,
                'load_time': load_time,
                'status': 'success',
                'browser_metadata': {
                    'browser_id': browser.browser_id,
                    'session_id': browser.session_id,
                    'proxy_config': browser.proxy_config,
                    'request_count': browser.request_count
                }
            }

        except Exception as e:
            load_time = time.time() - start_time
            error_msg = str(e)

            # Test proxy on any failure if proxy is configured
            proxy_failed = False
            if browser.proxy_config:
                proxy_failed = not await self._test_proxy_if_failed(browser.proxy_config)
                if proxy_failed:
                    logger.warning(f"Confirmed proxy failure for {browser.proxy_config['host']}:{browser.proxy_config['port']}")
                else:
                    logger.info(f"Proxy test passed, error was not proxy-related: {error_msg}")

            logger.error(f"Error fetching {url}: {e}")

            return {
                'html': '',
                'url': url,
                'title': '',
                'cookies': [],
                'load_time': load_time,
                'status': 'error',
                'error': str(e),
                'browser_metadata': {
                    'browser_id': browser.browser_id,
                    'session_id': browser.session_id,
                    'proxy_config': browser.proxy_config,
                    'request_count': browser.request_count,
                    'proxy_failed': proxy_failed if browser.proxy_config else False
                }
            }

        finally:
            # Return browser to pool
            await self.return_browser(browser)
