"""
Proxy Utilities for Multi-Browser Crawler
=========================================

Utilities for proxy validation and testing.
"""

import asyncio
import aiohttp
import re
from typing import Dict, List, Optional, Tuple
import logging

from ..exceptions.errors import ProxyError

logger = logging.getLogger(__name__)


class ProxyValidator:
    """Validate proxy configurations and formats."""
    
    @staticmethod
    def validate_proxy_format(proxy: str) -> bool:
        """
        Validate proxy format.
        
        Args:
            proxy: Proxy string in format "host:port" or "user:pass@host:port"
            
        Returns:
            True if format is valid
        """
        if not proxy or not isinstance(proxy, str):
            return False
        
        # Basic format: host:port
        basic_pattern = r'^[a-zA-Z0-9.-]+:\d+$'
        if re.match(basic_pattern, proxy):
            return True
        
        # Format with auth: user:pass@host:port
        auth_pattern = r'^[^:]+:[^@]*@[a-zA-Z0-9.-]+:\d+$'
        if re.match(auth_pattern, proxy):
            return True
        
        return False
    
    @staticmethod
    def parse_proxy(proxy: str) -> Dict[str, Optional[str]]:
        """
        Parse proxy string into components.
        
        Args:
            proxy: Proxy string
            
        Returns:
            Dictionary with host, port, username, password
        """
        if not ProxyValidator.validate_proxy_format(proxy):
            raise ProxyError(f"Invalid proxy format: {proxy}")
        
        result = {
            'host': None,
            'port': None,
            'username': None,
            'password': None
        }
        
        # Check if proxy has authentication
        if '@' in proxy:
            auth_part, host_part = proxy.rsplit('@', 1)
            if ':' in auth_part:
                result['username'], result['password'] = auth_part.split(':', 1)
        else:
            host_part = proxy
        
        # Parse host and port
        if ':' in host_part:
            result['host'], port_str = host_part.rsplit(':', 1)
            try:
                result['port'] = int(port_str)
            except ValueError:
                raise ProxyError(f"Invalid port in proxy: {proxy}")
        
        return result
    
    @staticmethod
    def format_proxy_for_playwright(proxy: str) -> Dict[str, str]:
        """
        Format proxy for Playwright configuration.
        
        Args:
            proxy: Proxy string
            
        Returns:
            Playwright proxy configuration dictionary
        """
        parsed = ProxyValidator.parse_proxy(proxy)
        
        config = {
            'server': f"http://{parsed['host']}:{parsed['port']}"
        }
        
        if parsed['username']:
            config['username'] = parsed['username']
        if parsed['password']:
            config['password'] = parsed['password']
        
        return config


class ProxyTester:
    """Test proxy connectivity and performance."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize proxy tester.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.test_urls = [
            'https://httpbin.org/ip',
            'https://api.ipify.org?format=json',
            'https://ifconfig.me/ip'
        ]
    
    async def test_proxy(self, proxy: str, test_url: str = None) -> Dict[str, any]:
        """
        Test a single proxy.
        
        Args:
            proxy: Proxy string to test
            test_url: URL to test against (optional)
            
        Returns:
            Dictionary with test results
        """
        if not ProxyValidator.validate_proxy_format(proxy):
            return {
                'proxy': proxy,
                'success': False,
                'error': 'Invalid proxy format',
                'response_time': None,
                'ip_address': None
            }
        
        test_url = test_url or self.test_urls[0]
        proxy_url = f"http://{proxy}"
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                
                async with session.get(test_url, proxy=proxy_url) as response:
                    end_time = asyncio.get_event_loop().time()
                    response_time = end_time - start_time
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            ip_address = data.get('origin') or data.get('ip', 'unknown')
                        except:
                            ip_address = 'unknown'
                        
                        return {
                            'proxy': proxy,
                            'success': True,
                            'error': None,
                            'response_time': response_time,
                            'ip_address': ip_address,
                            'status_code': response.status
                        }
                    else:
                        return {
                            'proxy': proxy,
                            'success': False,
                            'error': f'HTTP {response.status}',
                            'response_time': response_time,
                            'ip_address': None,
                            'status_code': response.status
                        }
        
        except asyncio.TimeoutError:
            return {
                'proxy': proxy,
                'success': False,
                'error': 'Timeout',
                'response_time': None,
                'ip_address': None
            }
        except Exception as e:
            return {
                'proxy': proxy,
                'success': False,
                'error': str(e),
                'response_time': None,
                'ip_address': None
            }
    
    async def test_proxies(self, proxies: List[str], max_concurrent: int = 10) -> List[Dict[str, any]]:
        """
        Test multiple proxies concurrently.
        
        Args:
            proxies: List of proxy strings to test
            max_concurrent: Maximum concurrent tests
            
        Returns:
            List of test results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def test_with_semaphore(proxy):
            async with semaphore:
                return await self.test_proxy(proxy)
        
        tasks = [test_with_semaphore(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    'proxy': proxies[i],
                    'success': False,
                    'error': str(result),
                    'response_time': None,
                    'ip_address': None
                })
            else:
                final_results.append(result)
        
        return final_results
    
    async def find_working_proxies(self, proxies: List[str], max_concurrent: int = 10) -> List[str]:
        """
        Find working proxies from a list.
        
        Args:
            proxies: List of proxy strings to test
            max_concurrent: Maximum concurrent tests
            
        Returns:
            List of working proxy strings
        """
        results = await self.test_proxies(proxies, max_concurrent)
        working_proxies = [result['proxy'] for result in results if result['success']]
        
        logger.info(f"Found {len(working_proxies)} working proxies out of {len(proxies)} tested")
        
        return working_proxies
    
    def load_proxies_from_file(self, file_path: str) -> List[str]:
        """
        Load proxies from a text file.
        
        Args:
            file_path: Path to proxy file
            
        Returns:
            List of proxy strings
        """
        try:
            with open(file_path, 'r') as f:
                proxies = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ProxyValidator.validate_proxy_format(line):
                            proxies.append(line)
                        else:
                            logger.warning(f"Invalid proxy format in file: {line}")
                
                logger.info(f"Loaded {len(proxies)} valid proxies from {file_path}")
                return proxies
                
        except FileNotFoundError:
            logger.error(f"Proxy file not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading proxies from file: {e}")
            return []
