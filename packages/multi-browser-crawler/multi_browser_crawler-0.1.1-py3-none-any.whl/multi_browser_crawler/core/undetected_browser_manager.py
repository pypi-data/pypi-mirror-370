"""
Undetected ChromeDriver Browser Manager
======================================

Browser manager using undetected-chromedriver for maximum Cloudflare bypass success.
Replaces Playwright-based browser management with Selenium + undetected-chromedriver.
"""

import os
import time
import json
import asyncio
import tempfile
import shutil
from typing import Dict, Any, Optional, List
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options as ChromeOptions
except ImportError:
    raise ImportError("undetected-chromedriver is required. Install with: pip install undetected-chromedriver selenium")

from .session_manager import SessionManager
from .proxy_manager import ProxyManager
from ..utils.image_utils import ImageDownloader
from ..utils.web_utils import HTMLCleaner
from ..utils.js_utils import JavaScriptExecutor
from ..exceptions.errors import BrowserInitializationError, SessionError

logger = logging.getLogger(__name__)


class UndetectedBrowserManager:
    """Browser manager using undetected-chromedriver for Cloudflare bypass."""
    
    def __init__(self, config):
        """Initialize the undetected browser manager."""
        self.config = config

        # Skip complex dependencies for now - focus on core functionality
        # self.session_manager = SessionManager(config)
        # self.proxy_manager = ProxyManager(config)
        # self.image_downloader = ImageDownloader(config)
        # self.html_cleaner = HTMLCleaner()
        # self.js_executor = JavaScriptExecutor()

        # Browser settings
        self.headless = config.get('BROWSER_HEADLESS', False)
        self.user_data_dir = config.get('BROWSER__USER_DATA_DIR') or os.path.join(config.get('DATA__FOLDER', 'data'), 'browser_user_data')
        self.timeout = config.get('BROWSER_TIMEOUT', 60000) / 1000  # Convert to seconds

        # Active drivers for cleanup
        self.active_drivers = {}

        logger.info("UndetectedBrowserManager initialized")
    
    def _create_chrome_options(self, proxy_config=None):
        """Create Chrome options for undetected-chromedriver."""
        options = ChromeOptions()
        
        # Basic options
        if self.headless:
            options.add_argument("--headless=new")
        
        # Window size
        options.add_argument("--window-size=1920,1080")
        
        # Essential options (minimal for better stealth)
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-dev-shm-usage")
        
        # Proxy configuration
        if proxy_config:
            proxy_url = proxy_config.get('url')
            if proxy_url:
                options.add_argument(f"--proxy-server={proxy_url}")
                
                # Proxy auth (if supported)
                username = proxy_config.get('username')
                password = proxy_config.get('password')
                if username and password:
                    # Note: Basic auth in proxy URL format
                    auth_proxy = proxy_url.replace('://', f'://{username}:{password}@')
                    options.add_argument(f"--proxy-server={auth_proxy}")
        
        # User data directory for persistence
        if self.user_data_dir:
            os.makedirs(self.user_data_dir, exist_ok=True)
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        return options
    
    def _create_driver(self, proxy_config=None, session_id=None):
        """Create an undetected ChromeDriver instance."""
        try:
            options = self._create_chrome_options(proxy_config)
            
            # Create undetected Chrome driver
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                driver_executable_path=None,  # Auto-download if needed
            )
            
            # Set timeouts
            driver.set_page_load_timeout(self.timeout)
            driver.implicitly_wait(10)  # 10 seconds for element finding
            
            # Store driver for cleanup
            if session_id:
                self.active_drivers[session_id] = driver
            
            logger.info(f"Created undetected Chrome driver (session: {session_id})")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create undetected Chrome driver: {e}")
            raise BrowserInitializationError(f"Failed to create browser: {e}")
    
    async def fetch_html(self, url: str, timeout: float = None, proxy_config: Dict = None, 
                        js_action: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Fetch HTML content using undetected ChromeDriver.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            proxy_config: Proxy configuration
            js_action: JavaScript to execute after page load
            session_id: Session ID for persistent browser
            
        Returns:
            Dictionary with HTML content and metadata
        """
        driver = None
        use_existing_session = False
        
        try:
            # Use existing session if available
            if session_id and session_id in self.active_drivers:
                driver = self.active_drivers[session_id]
                use_existing_session = True
                logger.info(f"Using existing session: {session_id}")
            else:
                # Create new driver
                driver = self._create_driver(proxy_config, session_id)
            
            # Navigate to URL
            logger.info(f"Navigating to: {url}")
            start_time = time.time()
            
            driver.get(url)
            
            # Wait for initial page load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Handle Cloudflare challenges automatically
            await self._handle_cloudflare_challenge(driver)
            
            # Execute custom JavaScript if provided
            if js_action:
                try:
                    result = driver.execute_script(js_action)
                    logger.info(f"JavaScript execution result: {result}")
                except Exception as e:
                    logger.warning(f"JavaScript execution failed: {e}")
            
            # Get final page content
            html_content = driver.page_source
            final_url = driver.current_url
            title = driver.title
            
            # Get cookies
            cookies = []
            for cookie in driver.get_cookies():
                cookies.append({
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', ''),
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False)
                })
            
            load_time = time.time() - start_time
            
            logger.info(f"Successfully fetched {url} in {load_time:.2f}s")
            
            return {
                'html': html_content,
                'url': final_url,
                'title': title,
                'cookies': cookies,
                'load_time': load_time,
                'status': 'success'
            }
            
        except TimeoutException:
            logger.error(f"Timeout fetching {url}")
            return {
                'html': '',
                'url': url,
                'title': '',
                'cookies': [],
                'load_time': 0,
                'status': 'timeout',
                'error': 'Request timeout'
            }
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return {
                'html': '',
                'url': url,
                'title': '',
                'cookies': [],
                'load_time': 0,
                'status': 'error',
                'error': str(e)
            }
            
        finally:
            # Clean up driver if not using session
            if driver and not use_existing_session and not session_id:
                try:
                    driver.quit()
                except:
                    pass
    
    async def _handle_cloudflare_challenge(self, driver, max_wait=60):
        """Handle Cloudflare challenges automatically."""
        logger.info("Checking for Cloudflare challenge...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                title = driver.title
                body_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Check if we're on a Cloudflare challenge page
                if any(indicator in title.lower() for indicator in ['just a moment', 'cloudflare']):
                    logger.info("Cloudflare challenge detected, waiting...")
                    
                    # Look for checkbox
                    try:
                        checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        if checkbox and checkbox.is_displayed():
                            logger.info("Found Cloudflare checkbox, clicking...")
                            time.sleep(2)  # Human-like delay
                            checkbox.click()
                            logger.info("Clicked Cloudflare checkbox")
                            time.sleep(3)  # Wait for processing
                    except NoSuchElementException:
                        pass  # No checkbox found
                    
                    time.sleep(2)  # Wait before next check
                    continue
                
                # Check if challenge is complete
                if not any(indicator in body_text.lower() for indicator in 
                          ['just a moment', 'verifying you are human', 'cloudflare']):
                    logger.info("Cloudflare challenge completed successfully")
                    return True
                    
            except Exception as e:
                logger.warning(f"Error during Cloudflare challenge handling: {e}")
            
            time.sleep(2)
        
        logger.warning(f"Cloudflare challenge did not complete within {max_wait} seconds")
        return False
    
    def create_session(self, session_id: str = None, proxy_config: Dict = None) -> str:
        """Create a persistent browser session."""
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        try:
            driver = self._create_driver(proxy_config, session_id)
            logger.info(f"Created persistent session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            raise SessionError(f"Failed to create session: {e}")
    
    def close_session(self, session_id: str):
        """Close a persistent browser session."""
        if session_id in self.active_drivers:
            try:
                self.active_drivers[session_id].quit()
                del self.active_drivers[session_id]
                logger.info(f"Closed session: {session_id}")
            except Exception as e:
                logger.error(f"Error closing session {session_id}: {e}")
    
    def close_all_sessions(self):
        """Close all active browser sessions."""
        for session_id in list(self.active_drivers.keys()):
            self.close_session(session_id)
        logger.info("Closed all browser sessions")
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close_all_sessions()
