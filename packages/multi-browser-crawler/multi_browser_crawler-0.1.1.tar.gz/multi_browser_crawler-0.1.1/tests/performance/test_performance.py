"""
Performance tests for multi-browser-crawler.
"""

import pytest
import asyncio
import time
import tempfile
from statistics import mean, median

from multi_browser_crawler import BrowserCrawler, BrowserConfig


@pytest.mark.performance
@pytest.mark.browser
class TestBrowserCrawlerPerformance:
    """Performance tests for BrowserCrawler."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration for performance tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=5,
                data_folder=temp_dir,
                fetch_limit=100
            )
    
    @pytest.mark.asyncio
    async def test_single_fetch_performance(self, config):
        """Test performance of single fetch operations."""
        async with BrowserCrawler(config) as crawler:
            times = []
            
            for i in range(10):
                start_time = time.time()
                result = await crawler.fetch("https://httpbin.org/html")
                end_time = time.time()
                
                assert result.success is True
                times.append(end_time - start_time)
            
            avg_time = mean(times)
            median_time = median(times)
            
            print(f"\nSingle fetch performance:")
            print(f"  Average time: {avg_time:.2f}s")
            print(f"  Median time: {median_time:.2f}s")
            print(f"  Min time: {min(times):.2f}s")
            print(f"  Max time: {max(times):.2f}s")
            
            # Performance assertions (adjust based on expected performance)
            assert avg_time < 10.0, f"Average fetch time too slow: {avg_time:.2f}s"
            assert max(times) < 15.0, f"Slowest fetch too slow: {max(times):.2f}s"
    
    @pytest.mark.asyncio
    async def test_batch_fetch_performance(self, config):
        """Test performance of batch fetch operations."""
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json", 
            "https://httpbin.org/xml",
            "https://httpbin.org/robots.txt",
            "https://httpbin.org/status/200"
        ]
        
        async with BrowserCrawler(config) as crawler:
            start_time = time.time()
            results = await crawler.fetch_batch(urls, max_concurrent=3)
            end_time = time.time()
            
            total_time = end_time - start_time
            successful = sum(1 for r in results if r.success)
            
            print(f"\nBatch fetch performance:")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  URLs processed: {len(urls)}")
            print(f"  Successful: {successful}")
            print(f"  Average per URL: {total_time/len(urls):.2f}s")
            
            # Performance assertions
            assert total_time < 30.0, f"Batch fetch too slow: {total_time:.2f}s"
            assert successful >= len(urls) * 0.8, f"Too many failures: {successful}/{len(urls)}"
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions_performance(self, config):
        """Test performance with multiple concurrent sessions."""
        async def fetch_with_session(crawler, session_id):
            session_name = f"perf_session_{session_id}"
            start_time = time.time()
            result = await crawler.fetch(
                "https://httpbin.org/html",
                session_name=session_name
            )
            end_time = time.time()
            return result, end_time - start_time
        
        async with BrowserCrawler(config) as crawler:
            # Test with different concurrency levels
            for concurrency in [1, 2, 3, 5]:
                start_time = time.time()
                
                tasks = [
                    fetch_with_session(crawler, i)
                    for i in range(concurrency)
                ]
                
                results = await asyncio.gather(*tasks)
                total_time = time.time() - start_time
                
                successful = sum(1 for r, _ in results if r.success)
                individual_times = [t for _, t in results]
                
                print(f"\nConcurrency {concurrency}:")
                print(f"  Total time: {total_time:.2f}s")
                print(f"  Successful: {successful}/{concurrency}")
                print(f"  Average individual time: {mean(individual_times):.2f}s")
                
                # Performance assertions
                assert successful >= concurrency * 0.8, f"Too many failures at concurrency {concurrency}"
                assert total_time < 20.0, f"Too slow at concurrency {concurrency}: {total_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_javascript_execution_performance(self, config):
        """Test performance of JavaScript execution."""
        js_code = """
        return {
            title: document.title,
            links: document.querySelectorAll('a').length,
            images: document.querySelectorAll('img').length,
            timestamp: Date.now()
        };
        """
        
        async with BrowserCrawler(config) as crawler:
            times = []
            
            for i in range(5):
                start_time = time.time()
                result = await crawler.execute_js("https://httpbin.org/html", js_code)
                end_time = time.time()
                
                assert result['success'] is True
                times.append(end_time - start_time)
            
            avg_time = mean(times)
            
            print(f"\nJavaScript execution performance:")
            print(f"  Average time: {avg_time:.2f}s")
            print(f"  Min time: {min(times):.2f}s")
            print(f"  Max time: {max(times):.2f}s")
            
            # Performance assertions
            assert avg_time < 8.0, f"JavaScript execution too slow: {avg_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, config):
        """Test memory usage stability over multiple operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async with BrowserCrawler(config) as crawler:
            # Perform many operations
            for i in range(20):
                result = await crawler.fetch("https://httpbin.org/html")
                assert result.success is True
                
                # Check memory every 5 operations
                if i % 5 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = current_memory - initial_memory
                    
                    print(f"Operation {i}: Memory usage: {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
                    
                    # Memory shouldn't grow excessively
                    assert memory_increase < 500, f"Memory usage too high: +{memory_increase:.1f}MB"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - initial_memory
        
        print(f"\nMemory usage summary:")
        print(f"  Initial: {initial_memory:.1f}MB")
        print(f"  Final: {final_memory:.1f}MB")
        print(f"  Total increase: {total_increase:.1f}MB")
    
    @pytest.mark.asyncio
    async def test_session_cleanup_performance(self, config):
        """Test performance of session cleanup operations."""
        async with BrowserCrawler(config) as crawler:
            # Create multiple sessions
            session_names = [f"cleanup_test_{i}" for i in range(5)]
            
            # Use each session
            for session_name in session_names:
                result = await crawler.fetch(
                    "https://httpbin.org/html",
                    session_name=session_name
                )
                assert result.success is True
            
            # Test cleanup performance
            start_time = time.time()
            await crawler.cleanup()
            cleanup_time = time.time() - start_time
            
            print(f"\nSession cleanup performance:")
            print(f"  Sessions cleaned: {len(session_names)}")
            print(f"  Cleanup time: {cleanup_time:.2f}s")
            print(f"  Average per session: {cleanup_time/len(session_names):.2f}s")
            
            # Performance assertions
            assert cleanup_time < 10.0, f"Cleanup too slow: {cleanup_time:.2f}s"


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmarks and comparisons."""
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self):
        """Benchmark throughput with different configurations."""
        test_url = "https://httpbin.org/html"
        num_requests = 10
        
        configs = [
            ("Single Session", BrowserConfig(headless=True, max_sessions=1)),
            ("Multiple Sessions", BrowserConfig(headless=True, max_sessions=3)),
            ("High Concurrency", BrowserConfig(headless=True, max_sessions=5))
        ]
        
        results = {}
        
        for config_name, config in configs:
            with tempfile.TemporaryDirectory() as temp_dir:
                config.data_folder = temp_dir
                
                async with BrowserCrawler(config) as crawler:
                    start_time = time.time()
                    
                    # Create batch of URLs
                    urls = [test_url] * num_requests
                    batch_results = await crawler.fetch_batch(urls, max_concurrent=config.max_sessions)
                    
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    successful = sum(1 for r in batch_results if r.success)
                    throughput = successful / total_time
                    
                    results[config_name] = {
                        'total_time': total_time,
                        'successful': successful,
                        'throughput': throughput
                    }
        
        print(f"\nThroughput benchmark ({num_requests} requests):")
        for config_name, result in results.items():
            print(f"  {config_name}:")
            print(f"    Time: {result['total_time']:.2f}s")
            print(f"    Success: {result['successful']}/{num_requests}")
            print(f"    Throughput: {result['throughput']:.2f} req/s")
        
        # Verify that higher concurrency generally performs better
        single_throughput = results["Single Session"]["throughput"]
        multi_throughput = results["Multiple Sessions"]["throughput"]
        
        # Allow some variance, but multi-session should generally be faster
        assert multi_throughput >= single_throughput * 0.8, "Multi-session should be competitive with single session"
