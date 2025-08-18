"""
Pytest configuration and fixtures for multi-browser-crawler tests.
"""

import pytest
import asyncio
import tempfile
import os
import logging
from typing import Generator

from multi_browser_crawler.config.settings import BrowserConfig
from multi_browser_crawler.core.browser_manager import BrowserManager


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "browser: mark test as requiring browser automation"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        
        # Add browser marker for tests that need browser automation
        if any(marker.name == "browser" for marker in item.iter_markers()):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_config(temp_dir: str) -> BrowserConfig:
    """Create a test browser configuration."""
    return BrowserConfig(
        headless=True,
        max_sessions=2,
        data_folder=temp_dir,
        fetch_limit=50,
        cache_expiry=300,  # 5 minutes for tests
        stealth_mode=True
    )


@pytest.fixture
def proxy_file(temp_dir: str) -> str:
    """Create a temporary proxy file for testing."""
    proxy_file_path = os.path.join(temp_dir, "test_proxies.txt")
    
    with open(proxy_file_path, 'w') as f:
        f.write("# Test proxy file\n")
        f.write("127.0.0.1:8080\n")
        f.write("proxy.example.com:3128\n")
        f.write("user:pass@proxy2.example.com:8080\n")
        f.write("\n")  # Empty line
        f.write("# Another comment\n")
        f.write("192.168.1.100:8888\n")
    
    return proxy_file_path


@pytest.fixture
def test_urls():
    """Provide test URLs for integration tests."""
    return [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml",
        "https://httpbin.org/robots.txt",
        "https://httpbin.org/status/200"
    ]


@pytest.fixture
def sample_html():
    """Provide sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Test Heading</h1>
        <p>This is a test paragraph.</p>
        <div class="content">
            <p>More content here.</p>
            <img src="test-image.jpg" alt="Test Image">
        </div>
        <script>
            console.log("Test script");
        </script>
        <style>
            body { font-family: Arial; }
        </style>
    </body>
    </html>
    """


@pytest.fixture
def sample_javascript():
    """Provide sample JavaScript code for testing."""
    return """
    return {
        title: document.title,
        url: window.location.href,
        links: document.querySelectorAll('a').length,
        images: document.querySelectorAll('img').length,
        timestamp: Date.now()
    };
    """


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    # Reduce log level for tests to avoid noise
    logging.getLogger("multi_browser_crawler").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)


@pytest.fixture
def mock_proxy_response():
    """Mock response for proxy testing."""
    return {
        "origin": "1.2.3.4",
        "headers": {
            "User-Agent": "test-agent"
        }
    }


# Pytest command line options
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--run-browser",
        action="store_true", 
        default=False,
        help="run tests that require browser automation"
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )
    parser.addoption(
        "--run-performance",
        action="store_true",
        default=False,
        help="run performance tests"
    )


def pytest_runtest_setup(item):
    """Setup for individual test runs."""
    # Skip slow tests unless explicitly requested
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("need --run-slow option to run")
    
    # Skip browser tests unless explicitly requested
    if "browser" in item.keywords and not item.config.getoption("--run-browser"):
        pytest.skip("need --run-browser option to run")
    
    # Skip integration tests unless explicitly requested
    if "integration" in item.keywords and not item.config.getoption("--run-integration"):
        pytest.skip("need --run-integration option to run")
    
    # Skip performance tests unless explicitly requested
    if "performance" in item.keywords and not item.config.getoption("--run-performance"):
        pytest.skip("need --run-performance option to run")


# Async test utilities
@pytest.fixture
async def async_test_helper():
    """Helper for async test operations."""
    class AsyncTestHelper:
        @staticmethod
        async def wait_for_condition(condition_func, timeout=5.0, interval=0.1):
            """Wait for a condition to become true."""
            import time
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if await condition_func():
                    return True
                await asyncio.sleep(interval)
            
            return False
        
        @staticmethod
        async def measure_time(async_func, *args, **kwargs):
            """Measure execution time of an async function."""
            import time
            start_time = time.time()
            result = await async_func(*args, **kwargs)
            end_time = time.time()
            return result, end_time - start_time
    
    return AsyncTestHelper()


@pytest.fixture(autouse=True)
async def reset_browser_manager():
    """Reset BrowserManager singleton between tests to avoid state leakage."""
    # Reset singleton state before test
    BrowserManager._instance = None
    BrowserManager._initialized = False

    yield

    # Clean up after test
    if BrowserManager._instance:
        try:
            await BrowserManager._instance.cleanup_all_sessions()
            await BrowserManager._instance.close()
        except Exception:
            pass  # Ignore cleanup errors
        finally:
            BrowserManager._instance = None
            BrowserManager._initialized = False
