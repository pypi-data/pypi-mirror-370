# Multi-Browser Crawler

Enterprise-grade browser automation with advanced features like session isolation, proxy rotation, JavaScript execution, and multiprocess crawling capabilities.

## Features

- **Session Management**: Unique browser sessions with automatic cleanup
- **Proxy Support**: File-based proxy rotation with health monitoring
- **JavaScript Execution**: Execute custom JavaScript with DOM state waiting
- **Image Processing**: Bulk image download with format conversion
- **Multiprocess Support**: True multiprocess crawling with isolated sessions
- **Anti-Detection**: Stealth techniques to avoid bot detection
- **Clean API**: Simple, intuitive interface for common operations

## Installation

```bash
pip install multi-browser-crawler
```

### Install Playwright browsers

```bash
playwright install chromium
```

## Quick Start

### Simple Usage

```python
import asyncio
from multi_browser_crawler import BrowserCrawler

async def main():
    async with BrowserCrawler() as crawler:
        result = await crawler.fetch("https://example.com")
        print(result.html)
        print(result.title)

asyncio.run(main())
```

### Advanced Configuration

```python
from multi_browser_crawler import BrowserCrawler, BrowserConfig

config = BrowserConfig(
    headless=True,
    max_sessions=5,
    proxy=ProxyConfig(
        enabled=True,
        proxy_file="proxies.txt"
    )
)

async with BrowserCrawler(config) as crawler:
    result = await crawler.fetch(
        "https://example.com",
        execute_js="document.querySelector('#load-more').click()",
        wait_for="#dynamic-content",
        download_images=True
    )
```

### Batch Processing

```python
urls = [
    "https://example1.com",
    "https://example2.com", 
    "https://example3.com"
]

async with BrowserCrawler() as crawler:
    results = await crawler.fetch_batch(urls, max_concurrent=3)
    
    for result in results:
        if result.success:
            print(f"✅ {result.url}: {len(result.html)} chars")
        else:
            print(f"❌ {result.url}: {result.error}")
```

### JavaScript Execution

```python
async with BrowserCrawler() as crawler:
    result = await crawler.execute_js(
        "https://spa-site.com",
        """
        return {
            title: document.title,
            links: Array.from(document.querySelectorAll('a')).length,
            images: Array.from(document.querySelectorAll('img')).length
        };
        """
    )
    print(result['result'])
```

## Configuration

### Browser Configuration

```python
from multi_browser_crawler import BrowserConfig

config = BrowserConfig(
    headless=True,                    # Run in headless mode
    max_sessions=10,                  # Maximum concurrent sessions
    fetch_limit=1000,                 # Maximum fetches per session
    cache_expiry=3600,                # Cache expiry in seconds
    stealth_mode=True,                # Enable anti-detection
    download_images=False,            # Download images by default
    browser_args=['--no-sandbox']     # Additional browser arguments
)
```

### Proxy Configuration

```python
from multi_browser_crawler import ProxyConfig

proxy_config = ProxyConfig(
    enabled=True,
    proxy_file="proxies.txt",         # File containing proxy list
    recycle_threshold=0.5,            # Recycle when 50% fail
    test_timeout=10,                  # Proxy test timeout
    allow_direct_connection=True      # Fallback to direct connection
)
```

### Environment Variables

You can also configure using environment variables:

```bash
export BROWSER_HEADLESS=true
export BROWSER_MAX_SESSIONS=10
export PROXY_ENABLED=true
export PROXY_FILE=proxies.txt
```

## Proxy File Format

Create a `proxies.txt` file with one proxy per line:

```
proxy1.example.com:8080
proxy2.example.com:3128
user:pass@proxy3.example.com:8080
```

## Multiprocess Usage

```python
import multiprocessing
from multi_browser_crawler import BrowserCrawler

async def crawl_worker(urls):
    config = BrowserConfig(max_sessions=2)
    async with BrowserCrawler(config) as crawler:
        results = []
        for url in urls:
            result = await crawler.fetch(url)
            results.append(result)
        return results

def main():
    urls = ["https://example.com"] * 100
    url_chunks = [urls[i:i+25] for i in range(0, len(urls), 25)]
    
    with multiprocessing.Pool(4) as pool:
        results = pool.map(crawl_worker, url_chunks)
```

## API Reference

### BrowserCrawler

Main class for browser automation.

#### Methods

- `fetch(url, **options)` - Fetch content from a single URL
- `fetch_batch(urls, **options)` - Fetch content from multiple URLs
- `execute_js(url, js_code, **options)` - Execute JavaScript on a page
- `get_stats()` - Get crawler statistics
- `cleanup()` - Clean up all resources

#### Options

- `session_name` - Browser session name
- `use_cache` - Use cached content
- `clean_html` - Clean HTML content
- `download_images` - Download images
- `execute_js` - JavaScript to execute
- `wait_for` - CSS selector to wait for
- `max_concurrent` - Maximum concurrent requests (batch only)

### CrawlResult

Result object returned by fetch operations.

#### Properties

- `url` - The fetched URL
- `html` - HTML content
- `title` - Page title
- `success` - Whether the fetch was successful
- `error` - Error message (if any)
- `metadata` - Additional metadata
- `images` - Downloaded images
- `timestamp` - Fetch timestamp

## Development

### Setup Development Environment

```bash
git clone https://github.com/spider-mcp/multi-browser-crawler.git
cd multi-browser-crawler
pip install -e ".[dev]"
playwright install chromium
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
flake8 .
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

- GitHub Issues: https://github.com/spider-mcp/multi-browser-crawler/issues
- Documentation: https://multi-browser-crawler.readthedocs.io/
