"""
JavaScript Utilities for Multi-Browser Crawler
==============================================

Utilities for JavaScript injection and execution.
"""

import asyncio
from typing import Any, Dict, List, Optional
import logging

from ..exceptions.errors import JavaScriptExecutionError

logger = logging.getLogger(__name__)


class JavaScriptExecutor:
    """Execute JavaScript code in browser pages."""
    
    def __init__(self):
        """Initialize JavaScript executor."""
        self.common_scripts = {
            'remove_overlays': """
                // Remove common overlay elements
                const overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"], [class*="popup"]');
                overlays.forEach(el => el.remove());
            """,
            
            'scroll_to_bottom': """
                // Scroll to bottom of page
                window.scrollTo(0, document.body.scrollHeight);
            """,
            
            'click_load_more': """
                // Click load more buttons
                const loadMoreButtons = document.querySelectorAll('[class*="load"], [class*="more"], button[aria-label*="more"]');
                loadMoreButtons.forEach(btn => {
                    if (btn.offsetParent !== null) btn.click();
                });
            """,
            
            'wait_for_images': """
                // Wait for images to load
                return new Promise((resolve) => {
                    const images = document.querySelectorAll('img');
                    let loadedCount = 0;
                    const totalImages = images.length;
                    
                    if (totalImages === 0) {
                        resolve(true);
                        return;
                    }
                    
                    images.forEach(img => {
                        if (img.complete) {
                            loadedCount++;
                        } else {
                            img.onload = img.onerror = () => {
                                loadedCount++;
                                if (loadedCount === totalImages) {
                                    resolve(true);
                                }
                            };
                        }
                    });
                    
                    if (loadedCount === totalImages) {
                        resolve(true);
                    }
                });
            """,
            
            'get_page_info': """
                // Get page information
                return {
                    title: document.title,
                    url: window.location.href,
                    scrollHeight: document.body.scrollHeight,
                    scrollTop: window.pageYOffset,
                    viewportHeight: window.innerHeight,
                    imageCount: document.querySelectorAll('img').length,
                    linkCount: document.querySelectorAll('a').length
                };
            """,
            
            'extract_images': """
                // Extract all image URLs
                const images = Array.from(document.querySelectorAll('img'));
                return images.map(img => ({
                    src: img.src,
                    alt: img.alt,
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    visible: img.offsetParent !== null
                })).filter(img => img.src);
            """,
            
            'extract_links': """
                // Extract all links
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(link => ({
                    href: link.href,
                    text: link.textContent.trim(),
                    title: link.title
                }));
            """,
            
            'clean_page': """
                // Clean page by removing unwanted elements
                const unwantedSelectors = [
                    'script', 'style', 'iframe', 'noscript',
                    '[class*="ad"]', '[id*="ad"]',
                    '[class*="banner"]', '[id*="banner"]',
                    '[class*="popup"]', '[id*="popup"]',
                    '[class*="modal"]', '[id*="modal"]'
                ];
                
                unwantedSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => el.remove());
                });
                
                return 'Page cleaned';
            """
        }
    
    async def execute_script(self, page, script: str, *args) -> Any:
        """
        Execute JavaScript code on a page.
        
        Args:
            page: Playwright page object
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            Result of script execution
        """
        try:
            result = await page.evaluate(script, *args)
            logger.debug(f"Executed JavaScript: {script[:100]}...")
            return result
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            raise JavaScriptExecutionError(f"Script execution failed: {e}")
    
    async def execute_common_script(self, page, script_name: str) -> Any:
        """
        Execute a predefined common script.
        
        Args:
            page: Playwright page object
            script_name: Name of the common script
            
        Returns:
            Result of script execution
        """
        if script_name not in self.common_scripts:
            raise JavaScriptExecutionError(f"Unknown common script: {script_name}")
        
        script = self.common_scripts[script_name]
        return await self.execute_script(page, script)
    
    async def wait_for_element(self, page, selector: str, timeout: int = 30000) -> bool:
        """
        Wait for an element to appear using JavaScript.
        
        Args:
            page: Playwright page object
            selector: CSS selector to wait for
            timeout: Timeout in milliseconds
            
        Returns:
            True if element appeared, False if timeout
        """
        script = f"""
            return new Promise((resolve) => {{
                const checkElement = () => {{
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        resolve(true);
                    }} else {{
                        setTimeout(checkElement, 100);
                    }}
                }};
                checkElement();
                setTimeout(() => resolve(false), {timeout});
            }});
        """
        
        try:
            result = await self.execute_script(page, script)
            return result
        except Exception as e:
            logger.error(f"Error waiting for element {selector}: {e}")
            return False
    
    async def scroll_and_wait(self, page, scroll_pause: float = 1.0, max_scrolls: int = 10) -> Dict[str, Any]:
        """
        Scroll page gradually and wait for content to load.
        
        Args:
            page: Playwright page object
            scroll_pause: Pause between scrolls in seconds
            max_scrolls: Maximum number of scroll attempts
            
        Returns:
            Dictionary with scroll results
        """
        script = """
            return {
                initialHeight: document.body.scrollHeight,
                currentScroll: window.pageYOffset
            };
        """
        
        initial_info = await self.execute_script(page, script)
        scroll_count = 0
        last_height = initial_info['initialHeight']
        
        for i in range(max_scrolls):
            # Scroll down
            await self.execute_script(page, "window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(scroll_pause)
            
            # Check if new content loaded
            current_info = await self.execute_script(page, script)
            current_height = current_info['initialHeight']
            
            scroll_count += 1
            
            if current_height == last_height:
                # No new content, break
                break
            
            last_height = current_height
        
        return {
            'initial_height': initial_info['initialHeight'],
            'final_height': last_height,
            'scroll_count': scroll_count,
            'new_content_loaded': last_height > initial_info['initialHeight']
        }
    
    async def click_elements(self, page, selector: str, max_clicks: int = 5) -> Dict[str, Any]:
        """
        Click multiple elements matching a selector.
        
        Args:
            page: Playwright page object
            selector: CSS selector for elements to click
            max_clicks: Maximum number of elements to click
            
        Returns:
            Dictionary with click results
        """
        script = f"""
            const elements = Array.from(document.querySelectorAll('{selector}'));
            const visibleElements = elements.filter(el => el.offsetParent !== null);
            const clickedElements = [];
            
            for (let i = 0; i < Math.min(visibleElements.length, {max_clicks}); i++) {{
                try {{
                    visibleElements[i].click();
                    clickedElements.push({{
                        tagName: visibleElements[i].tagName,
                        className: visibleElements[i].className,
                        textContent: visibleElements[i].textContent.trim().substring(0, 50)
                    }});
                }} catch (e) {{
                    // Element might not be clickable
                }}
            }}
            
            return {{
                totalFound: elements.length,
                visibleFound: visibleElements.length,
                clicked: clickedElements.length,
                clickedElements: clickedElements
            }};
        """
        
        try:
            result = await self.execute_script(page, script)
            logger.info(f"Clicked {result['clicked']} elements matching '{selector}'")
            return result
        except Exception as e:
            logger.error(f"Error clicking elements {selector}: {e}")
            return {
                'totalFound': 0,
                'visibleFound': 0,
                'clicked': 0,
                'clickedElements': [],
                'error': str(e)
            }
    
    async def extract_data(self, page, extraction_rules: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data from page using CSS selectors.
        
        Args:
            page: Playwright page object
            extraction_rules: Dictionary mapping field names to CSS selectors
            
        Returns:
            Dictionary with extracted data
        """
        results = {}
        
        for field_name, selector in extraction_rules.items():
            script = f"""
                const elements = document.querySelectorAll('{selector}');
                if (elements.length === 0) return null;
                if (elements.length === 1) {{
                    return elements[0].textContent.trim();
                }}
                return Array.from(elements).map(el => el.textContent.trim());
            """
            
            try:
                result = await self.execute_script(page, script)
                results[field_name] = result
            except Exception as e:
                logger.error(f"Error extracting {field_name} with selector {selector}: {e}")
                results[field_name] = None
        
        return results
    
    def get_available_scripts(self) -> List[str]:
        """Get list of available common scripts."""
        return list(self.common_scripts.keys())
