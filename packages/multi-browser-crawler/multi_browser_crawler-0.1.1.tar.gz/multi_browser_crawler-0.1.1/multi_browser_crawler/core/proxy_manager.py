#!/usr/bin/env python3
"""
Multi-Browser Crawler Proxy Manager
===================================

A file-based proxy management system with:
- Automatic proxy rotation
- Health testing and monitoring  
- Failure detection and recovery
- Playwright integration
- Configurable recycling thresholds
- Flexible on/off proxy support
"""

import os
import random
import asyncio
import aiohttp
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..exceptions.errors import ProxyError
from ..utils.proxy_utils import ProxyValidator

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker for proxy failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time
        }


class ProxyManager:
    """File-based proxy manager with health monitoring"""
    
    def __init__(self,
                 proxy_file: str = "proxies.txt",
                 recycle_threshold: float = 0.5,
                 enabled: bool = True,
                 allow_direct_connection: bool = True,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 300):
        """
        Initialize the proxy manager

        Args:
            proxy_file: Path to proxy list file
            recycle_threshold: Threshold for recycling failed proxies (0.5 = 50%)
            enabled: Whether proxy support is enabled
            allow_direct_connection: Whether to allow direct connections as fallback
            failure_threshold: Circuit breaker failure threshold
            recovery_timeout: Circuit breaker recovery timeout in seconds
        """
        self.enabled = enabled
        self.allow_direct_connection = allow_direct_connection
        self.proxy_file = self._resolve_proxy_file_path(proxy_file)
        self.proxies = []
        self.working_proxies = []
        self.failed_proxies = set()
        self.current_proxy_index = 0
        self.recycle_threshold = recycle_threshold
        self.recycle_count = 0

        # Circuit breaker for proxy failures
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )

        # Proxy recovery tracking
        self.proxy_recovery_times = {}  # proxy -> last_failure_time
        self.proxy_recovery_cooldown = 600  # 10 minutes
        self.max_recycle_attempts = 3
        self.recycle_attempt_count = 0

        # Load proxies if enabled
        if self.enabled:
            self.load_proxies()
        else:
            logger.info("Proxy manager initialized but disabled")
    
    def _resolve_proxy_file_path(self, proxy_file: str) -> str:
        """Resolve proxy file path, checking multiple locations"""
        if os.path.isabs(proxy_file):
            return proxy_file
        
        # Check in current directory
        if os.path.exists(proxy_file):
            return proxy_file
        
        # Check in data directory
        data_proxy_file = os.path.join("data", proxy_file)
        if os.path.exists(data_proxy_file):
            return data_proxy_file
        
        # Return original path (will create if needed)
        return proxy_file
    
    def load_proxies(self):
        """Load proxies from file"""
        if not self.enabled:
            return

        try:
            with open(self.proxy_file, 'r') as f:
                # Filter out comments and empty lines
                self.proxies = [
                    line.strip() for line in f
                    if line.strip() and not line.strip().startswith('#')
                ]

            logger.info(f"✅ Loaded {len(self.proxies)} proxies from {self.proxy_file}")

            # Initialize working proxies with all loaded proxies
            self.working_proxies = self.proxies.copy()

        except FileNotFoundError:
            logger.warning(f"⚠️ Proxy file {self.proxy_file} not found - proxy support disabled")
            self.enabled = False
            self.proxies = []
        except Exception as e:
            logger.error(f"⚠️ Error loading proxies: {e} - proxy support disabled")
            self.enabled = False
            self.proxies = []
    
    async def test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        if not self.enabled:
            return False
        
        try:
            proxy_url = f"http://{proxy}"
            
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                
                async with session.get(
                    "https://httpbin.org/ip",
                    proxy=proxy_url
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"✅ Proxy {proxy} working - IP: {data.get('origin', 'unknown')}")
                        return True
                    else:
                        logger.debug(f"❌ Proxy {proxy} returned status {response.status}")
                        return False
        
        except Exception as e:
            logger.debug(f"❌ Proxy {proxy} failed: {str(e)[:50]}...")
            return False

    async def test_all_proxies(self, max_concurrent: int = 10):
        """Test all proxies concurrently"""
        if not self.enabled or not self.proxies:
            return []

        logger.info(f"🔍 Testing {len(self.proxies)} proxies...")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def test_with_semaphore(proxy):
            async with semaphore:
                is_working = await self.test_proxy(proxy)
                if is_working:
                    self.working_proxies.append(proxy)
                else:
                    self.failed_proxies.add(proxy)
                return is_working

        # Test all proxies
        tasks = [test_with_semaphore(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        working_count = len(self.working_proxies)
        failed_count = len(self.failed_proxies)

        if working_count + failed_count > 0:
            success_rate = (working_count / (working_count + failed_count)) * 100
            logger.info(f"📊 Proxy test results: {working_count} working, {failed_count} failed ({success_rate:.1f}% success)")

        # Shuffle working proxies for rotation
        random.shuffle(self.working_proxies)

        return self.working_proxies

    async def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy in rotation with circuit breaker and fallback support"""
        if not self.enabled:
            return None

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning("Proxy circuit breaker is open - using direct connection fallback")
            return None if not self.allow_direct_connection else "DIRECT"

        # Try to recover failed proxies if enough time has passed
        self._attempt_proxy_recovery()

        # If no working proxies but we have failed ones, try recycling (with limits)
        if not self.working_proxies and self.failed_proxies:
            if self.recycle_attempt_count < self.max_recycle_attempts:
                logger.info(f"🔄 No working proxies available - attempting emergency recycling (attempt {self.recycle_attempt_count + 1}/{self.max_recycle_attempts})...")
                self.force_recycle_all_proxies()
                self.recycle_attempt_count += 1
            else:
                logger.error("Maximum proxy recycle attempts reached - all proxies appear to be dead")
                self.circuit_breaker.record_failure()
                if self.allow_direct_connection:
                    logger.info("Falling back to direct connection")
                    return "DIRECT"
                return None

        if not self.working_proxies:
            if self.allow_direct_connection:
                logger.info("No working proxies available - using direct connection")
                return "DIRECT"
            return None

        proxy = self.working_proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.working_proxies)

        # Reset recycle attempt count on successful proxy retrieval
        self.recycle_attempt_count = 0
        self.circuit_breaker.record_success()

        return proxy

    def _attempt_proxy_recovery(self):
        """Attempt to recover failed proxies after cooldown period"""
        if not self.failed_proxies:
            return

        current_time = time.time()
        recovered_proxies = []

        for proxy in list(self.failed_proxies):
            last_failure_time = self.proxy_recovery_times.get(proxy, 0)
            if current_time - last_failure_time > self.proxy_recovery_cooldown:
                # Try to recover this proxy
                recovered_proxies.append(proxy)
                self.failed_proxies.remove(proxy)
                self.working_proxies.append(proxy)
                del self.proxy_recovery_times[proxy]
                logger.info(f"🔄 Recovered proxy after cooldown: {proxy}")

        if recovered_proxies:
            logger.info(f"✅ Recovered {len(recovered_proxies)} proxies from cooldown")

    def get_random_proxy(self) -> Optional[str]:
        """Get a random working proxy"""
        if not self.enabled or not self.working_proxies:
            return None

        return random.choice(self.working_proxies)

    async def mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed and remove from working list with time-based recovery tracking"""
        if not self.enabled or not proxy or proxy == "DIRECT":
            return

        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            self.failed_proxies.add(proxy)
            self.proxy_recovery_times[proxy] = time.time()
            self.circuit_breaker.record_failure()
            logger.warning(f"⚠️ Marked proxy {proxy} as failed - will retry after {self.proxy_recovery_cooldown}s cooldown")

            # Check if we need to recycle proxies
            self.check_and_recycle_proxies()

    def get_proxy_config_for_playwright(self, proxy: str = None) -> Dict[str, Any]:
        """Get proxy configuration for Playwright"""
        if not self.enabled:
            return {}

        if not proxy:
            # This is now async, so we can't call it directly here
            # The caller should provide the proxy
            return {}

        if not proxy or proxy == "DIRECT":
            return {}

        try:
            host, port = proxy.split(':')
            return {
                'server': f'http://{host}:{port}',
                'username': None,  # Add if proxies require auth
                'password': None   # Add if proxies require auth
            }
        except ValueError:
            logger.error(f"Invalid proxy format: {proxy}")
            return {}

    def get_working_proxy_count(self) -> int:
        """Get count of working proxies"""
        return len(self.working_proxies) if self.enabled else 0

    def check_and_recycle_proxies(self):
        """Check if we need to recycle failed proxies"""
        if not self.enabled:
            return

        total_proxies = len(self.proxies)
        failed_count = len(self.failed_proxies)

        # Calculate failure percentage
        failure_percentage = failed_count / total_proxies if total_proxies > 0 else 0

        # If we've failed more than the threshold (default 50%), recycle all proxies
        if failure_percentage >= self.recycle_threshold and failed_count > 0:
            self.recycle_all_proxies()

    def recycle_all_proxies(self):
        """Recycle all failed proxies back to working pool"""
        if not self.enabled or not self.failed_proxies:
            return

        self.recycle_count += 1
        recycled_count = len(self.failed_proxies)

        logger.info(f"♻️ PROXY RECYCLING #{self.recycle_count}")
        logger.info(f"   Recycling {recycled_count} failed proxies back to working pool")
        logger.info(f"   Reason: {len(self.failed_proxies)}/{len(self.proxies)} proxies failed ({(len(self.failed_proxies)/len(self.proxies)*100):.1f}% > {self.recycle_threshold*100:.0f}% threshold)")

        # Move all failed proxies back to working pool
        recycled_proxies = list(self.failed_proxies)
        self.working_proxies.extend(recycled_proxies)
        self.failed_proxies.clear()

        # Shuffle the working proxies to distribute load
        random.shuffle(self.working_proxies)

        # Reset index
        self.current_proxy_index = 0

        logger.info(f"✅ Recycled {recycled_count} proxies - now have {len(self.working_proxies)} working proxies")

    def force_recycle_all_proxies(self):
        """Manually force recycling of all proxies"""
        if not self.enabled:
            return

        if self.failed_proxies:
            logger.info(f"🔄 MANUAL PROXY RECYCLING")
            logger.info(f"   Force recycling {len(self.failed_proxies)} failed proxies")
            self.recycle_all_proxies()
        else:
            logger.info(f"ℹ️ No failed proxies to recycle")

    def log_proxy_stats(self):
        """Log current proxy statistics"""
        if not self.enabled:
            logger.info("📊 Proxy Manager: DISABLED")
            return

        logger.info(f"📊 Proxy Manager Stats:")
        logger.info(f"  • Total proxies loaded: {len(self.proxies)}")
        logger.info(f"  • Working proxies: {len(self.working_proxies)}")
        logger.info(f"  • Failed proxies: {len(self.failed_proxies)}")
        logger.info(f"  • Current proxy index: {self.current_proxy_index}")
        logger.info(f"  • Recycle count: {self.recycle_count}")
        logger.info(f"  • Recycle threshold: {self.recycle_threshold*100:.0f}%")
        logger.info(f"  • Circuit breaker state: {self.circuit_breaker.state}")
        logger.info(f"  • Direct connection allowed: {self.allow_direct_connection}")
        logger.info(f"  • Proxies in recovery: {len(self.proxy_recovery_times)}")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive proxy manager status"""
        return {
            'enabled': self.enabled,
            'allow_direct_connection': self.allow_direct_connection,
            'total_proxies': len(self.proxies),
            'working_proxies': len(self.working_proxies),
            'failed_proxies': len(self.failed_proxies),
            'current_proxy_index': self.current_proxy_index,
            'recycle_count': self.recycle_count,
            'recycle_threshold': self.recycle_threshold,
            'recycle_attempt_count': self.recycle_attempt_count,
            'max_recycle_attempts': self.max_recycle_attempts,
            'circuit_breaker': self.circuit_breaker.get_status(),
            'proxies_in_recovery': len(self.proxy_recovery_times),
            'proxy_recovery_cooldown': self.proxy_recovery_cooldown
        }

    def is_enabled(self) -> bool:
        """Check if proxy manager is enabled"""
        return self.enabled

    def disable(self):
        """Disable proxy manager"""
        self.enabled = False
        logger.info("Proxy manager disabled")

    def enable(self):
        """Enable proxy manager"""
        self.enabled = True
        if not self.proxies:
            self.load_proxies()
        logger.info("Proxy manager enabled")

    async def refresh_proxy_pool(self):
        """Refresh the proxy pool by testing all proxies"""
        if not self.enabled:
            return

        logger.info("🔄 Refreshing proxy pool...")
        self.working_proxies.clear()
        self.failed_proxies.clear()
        await self.test_all_proxies()
