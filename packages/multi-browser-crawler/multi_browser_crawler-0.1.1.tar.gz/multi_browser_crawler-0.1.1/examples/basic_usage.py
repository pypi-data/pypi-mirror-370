#!/usr/bin/env python3
"""
Basic usage examples for multi-browser-crawler.
"""

import asyncio
import tempfile
from multi_browser_crawler import BrowserCrawler, BrowserConfig, fetch, fetch_batch


async def example_simple_fetch():
    """Example: Simple page fetch."""
    print("=== Simple Fetch Example ===")
    
    # Simple fetch using convenience function
    result = await fetch("https://httpbin.org/html")
    
    if result.success:
        print(f"✅ Successfully fetched {result.url}")
        print(f"   Title: {result.title}")
        print(f"   HTML length: {len(result.html)} characters")
    else:
        print(f"❌ Failed to fetch: {result.error}")


async def example_configured_crawler():
    """Example: Using configured crawler."""
    print("\n=== Configured Crawler Example ===")
    
    # Create configuration
    with tempfile.TemporaryDirectory() as temp_dir:
        config = BrowserConfig(
            headless=True,
            max_sessions=3,
            data_folder=temp_dir,
            stealth_mode=True
        )
        
        # Use crawler with context manager
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch("https://httpbin.org/json")
            
            if result.success:
                print(f"✅ Successfully fetched {result.url}")
                print(f"   HTML length: {len(result.html)} characters")
                
                # Get crawler stats
                stats = await crawler.get_stats()
                print(f"   Active sessions: {stats.get('active_sessions', 0)}")
                print(f"   Fetch count: {stats.get('fetch_count', 0)}")
            else:
                print(f"❌ Failed to fetch: {result.error}")


async def example_javascript_execution():
    """Example: JavaScript execution."""
    print("\n=== JavaScript Execution Example ===")
    
    async with BrowserCrawler() as crawler:
        js_code = """
        return {
            title: document.title,
            url: window.location.href,
            links: document.querySelectorAll('a').length,
            images: document.querySelectorAll('img').length,
            timestamp: Date.now()
        };
        """
        
        result = await crawler.execute_js("https://httpbin.org/html", js_code)
        
        if result['success']:
            print(f"✅ JavaScript executed successfully")
            print(f"   Page title: {result['result']['title']}")
            print(f"   Links found: {result['result']['links']}")
            print(f"   Images found: {result['result']['images']}")
        else:
            print(f"❌ JavaScript execution failed: {result['error']}")


async def example_batch_processing():
    """Example: Batch processing."""
    print("\n=== Batch Processing Example ===")
    
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml"
    ]
    
    # Use convenience function for batch processing
    results = await fetch_batch(urls, max_concurrent=2)
    
    successful = sum(1 for r in results if r.success)
    print(f"✅ Batch processing completed: {successful}/{len(urls)} successful")
    
    for result in results:
        if result.success:
            print(f"   ✅ {result.url}: {len(result.html)} chars")
        else:
            print(f"   ❌ {result.url}: {result.error}")


async def example_session_isolation():
    """Example: Session isolation."""
    print("\n=== Session Isolation Example ===")
    
    async with BrowserCrawler() as crawler:
        # Fetch with different sessions
        result1 = await crawler.fetch(
            "https://httpbin.org/html",
            session_name="session_1"
        )
        
        result2 = await crawler.fetch(
            "https://httpbin.org/html",
            session_name="session_2"
        )
        
        if result1.success and result2.success:
            session1_id = result1.metadata.get('session_id')
            session2_id = result2.metadata.get('session_id')
            
            print(f"✅ Session isolation working")
            print(f"   Session 1 ID: {session1_id}")
            print(f"   Session 2 ID: {session2_id}")
            print(f"   Sessions are different: {session1_id != session2_id}")
        else:
            print("❌ Session isolation test failed")


async def example_advanced_features():
    """Example: Advanced features."""
    print("\n=== Advanced Features Example ===")
    
    async with BrowserCrawler() as crawler:
        # Fetch with JavaScript execution and custom options
        result = await crawler.fetch(
            "https://httpbin.org/html",
            execute_js="document.title = 'Modified by JS'; return document.title;",
            clean_html=True,
            use_cache=False
        )
        
        if result.success:
            print(f"✅ Advanced fetch successful")
            print(f"   Original title: {result.title}")
            print(f"   JS result: {result.metadata.get('js_result')}")
            print(f"   HTML is cleaned: {len(result.html) < 10000}")  # Cleaned HTML is typically shorter
        else:
            print(f"❌ Advanced fetch failed: {result.error}")


async def example_error_handling():
    """Example: Error handling."""
    print("\n=== Error Handling Example ===")
    
    async with BrowserCrawler() as crawler:
        # Try to fetch from invalid URL
        result = await crawler.fetch("https://invalid-domain-that-does-not-exist.com")
        
        if not result.success:
            print(f"✅ Error handling working correctly")
            print(f"   Error: {result.error}")
            print(f"   URL: {result.url}")
            print(f"   HTML fallback: {result.html[:50]}...")
        else:
            print("❌ Expected error but got success")


async def main():
    """Run all examples."""
    print("Multi-Browser Crawler Examples")
    print("=" * 50)
    
    examples = [
        example_simple_fetch,
        example_configured_crawler,
        example_javascript_execution,
        example_batch_processing,
        example_session_isolation,
        example_advanced_features,
        example_error_handling
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"❌ Example failed: {e}")
        
        # Small delay between examples
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
