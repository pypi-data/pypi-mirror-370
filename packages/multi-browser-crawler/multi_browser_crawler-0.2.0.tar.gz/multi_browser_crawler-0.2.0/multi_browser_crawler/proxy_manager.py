# File: multi_browser_crawler/core/proxy_manager.py
import asyncio
import random
import time
import os
import aiohttp
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self, proxy_file: str):
        """
        Initialize proxy manager.

        Args:
            proxy_file: Absolute path to proxy file (required)
        """
        if not proxy_file:
            raise ValueError("proxy_file is required")

        self.proxy_file = proxy_file
        self.proxies: List[Dict] = []  # Store as Chrome-ready dict format
        self.failed_proxies = set()
        self.current_index = 0

        # Single lock for all proxy operations
        self._proxy_lock = asyncio.Lock()

        # Simple failure tracking
        self.failure_counts = {}
        self.max_failures = 3
        self.test_timeout = 10  # seconds
        self.test_url = "https://httpbin.org/ip"

    async def load_and_test_proxies(self):
        """Load proxies from file, convert to Chrome format, and test them"""
        if not os.path.exists(self.proxy_file):
            raise FileNotFoundError(f"Proxy file not found: {self.proxy_file}")

        async with self._proxy_lock:
            try:
                with open(self.proxy_file, 'r') as f:
                    raw_proxies = [
                        line.strip() for line in f
                        if line.strip() and not line.strip().startswith('#')
                    ]

                # Convert to Chrome-ready dict format
                self.proxies = []
                for proxy_string in raw_proxies:
                    proxy_dict = self._parse_proxy_string(proxy_string)
                    if proxy_dict:
                        self.proxies.append(proxy_dict)

                # Shuffle for better distribution
                random.shuffle(self.proxies)

                logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")

                # Test all proxies initially
                await self._initial_proxy_test()

            except Exception as e:
                logger.error(f"Failed to load proxies from {self.proxy_file}: {e}")
                raise

    def _parse_proxy_string(self, proxy_string: str) -> Optional[Dict]:
        """Parse proxy string into Chrome-ready dict format using single regex"""
        if not proxy_string:
            return None

        import re

        # Single regex pattern that handles both formats:
        # - host:port
        # - username:password@host:port
        # Strategy: Match from the end backwards to find the last @host:port
        pattern = r'^(?:([^:]+):(.*)@)?([^:@]+):(\d+)$'

        match = re.match(pattern, proxy_string.strip())
        if not match:
            logger.warning(f"Invalid proxy format: {proxy_string}")
            return None

        username, password, host, port = match.groups()

        try:
            proxy_dict = {
                'host': host,
                'port': int(port),
                'proxy_string': proxy_string  # Keep original for identification
            }

            # Add auth if present
            if username and password:
                proxy_dict.update({
                    'username': username,
                    'password': password
                })

            return proxy_dict

        except ValueError as e:
            logger.warning(f"Invalid proxy port: {proxy_string} - {e}")
            return None

    async def get_proxy(self, random: bool = False) -> Optional[Dict]:
        """
        Get a proxy (Chrome-ready dict format).
        Returns proxies that passed initial testing. No runtime testing to avoid recursion.

        Args:
            random: If True, get random proxy. If False, use round-robin.

        Returns:
            Dict with proxy config ready for Chrome, or None if no working proxies
        """
        if not self.proxies:
            return None

        async with self._proxy_lock:
            working_proxies = [p for p in self.proxies if p['proxy_string'] not in self.failed_proxies]

            if not working_proxies:
                # All proxies failed - reset and try again
                logger.warning("All proxies failed, resetting failure tracking")
                self.failed_proxies.clear()
                self.failure_counts.clear()
                working_proxies = self.proxies.copy()

            if not working_proxies:
                return None

            # Select proxy (no testing, just return)
            if random:
                import random as rand_module
                proxy = rand_module.choice(working_proxies)
            else:
                # Round-robin through working proxies
                proxy_index = self.current_index % len(working_proxies)
                proxy = working_proxies[proxy_index]
                self.current_index = (self.current_index + 1) % len(working_proxies)

            logger.debug(f"Returning proxy: {proxy['host']}:{proxy['port']}")
            return proxy

    async def test_proxy(self, proxy_dict: Dict) -> bool:
        """
        Test a specific proxy and mark it failed if it doesn't work.
        This is called by upper applications when they encounter exceptions.

        Args:
            proxy_dict: Chrome-ready proxy dict (from get_proxy())

        Returns:
            True if proxy works, False if failed (and marked as failed)
        """
        if not proxy_dict or 'proxy_string' not in proxy_dict:
            return False

        is_working = await self._test_single_proxy(proxy_dict)

        if not is_working:
            await self._mark_proxy_failed_internal(proxy_dict['proxy_string'])
            logger.warning(f"Proxy marked as failed after test: {proxy_dict['host']}:{proxy_dict['port']}")

        return is_working

    async def _mark_proxy_failed_internal(self, proxy_string: str):
        """Internal method to mark proxy as failed"""
        async with self._proxy_lock:
            self.failure_counts[proxy_string] = self.failure_counts.get(proxy_string, 0) + 1

            if self.failure_counts[proxy_string] >= self.max_failures:
                self.failed_proxies.add(proxy_string)
                logger.info(f"Proxy permanently failed after {self.max_failures} attempts: {proxy_string}")

    async def _test_single_proxy(self, proxy_dict: Dict) -> bool:
        """Test a single proxy"""
        try:
            # Create proxy URL for aiohttp
            if 'username' in proxy_dict and 'password' in proxy_dict:
                proxy_url = f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
            else:
                proxy_url = f"http://{proxy_dict['host']}:{proxy_dict['port']}"

            timeout = aiohttp.ClientTimeout(total=self.test_timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.test_url, proxy=proxy_url) as response:
                    if response.status == 200:
                        # Try to read response to ensure proxy is working
                        await response.json()  # httpbin.org/ip returns JSON
                        return True
                    else:
                        logger.debug(f"Proxy test failed with status {response.status}: {proxy_dict['host']}:{proxy_dict['port']}")
                        return False

        except Exception as e:
            logger.debug(f"Proxy test failed with exception: {proxy_dict['host']}:{proxy_dict['port']} - {e}")
            return False

    async def _initial_proxy_test(self):
        """Test all proxies initially and mark failed ones"""
        logger.info("Testing all proxies initially...")

        test_tasks = []
        for proxy in self.proxies:
            test_tasks.append(self._test_single_proxy(proxy))

        # Test all proxies concurrently
        results = await asyncio.gather(*test_tasks, return_exceptions=True)

        failed_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception) or not result:
                await self._mark_proxy_failed_internal(self.proxies[i]['proxy_string'])
                failed_count += 1

        working_count = len(self.proxies) - failed_count
        logger.info(f"Initial proxy test complete: {working_count}/{len(self.proxies)} proxies working")

    async def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        async with self._proxy_lock:
            return {
                'total_proxies': len(self.proxies),
                'failed_proxies': len(self.failed_proxies),
                'working_proxies': len(self.proxies) - len(self.failed_proxies),
                'current_index': self.current_index,
                'failure_counts': dict(self.failure_counts)
            }
