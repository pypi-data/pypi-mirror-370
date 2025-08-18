"""
Integration tests for image download functionality.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from multi_browser_crawler import BrowserCrawler, BrowserConfig


@pytest.mark.integration
@pytest.mark.browser
class TestImageDownload:
    """Integration tests for image download functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration with image download enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=2,
                data_folder=temp_dir,
                download_images=True,
                fetch_limit=50
            )
    
    @pytest.mark.asyncio
    async def test_image_download_basic(self, config):
        """Test basic image download functionality."""
        async with BrowserCrawler(config) as crawler:
            # Test with a page that has images
            result = await crawler.fetch(
                "https://httpbin.org/html",
                download_images=True
            )
            
            assert isinstance(result.images, list)
            assert result.success is True
            
            # Check if any images were downloaded
            if len(result.images) > 0:
                image = result.images[0]
                assert 'original_url' in image
                assert 'local_path' in image
                assert 'web_path' in image
                
                # Check that local path exists
                local_path = os.path.join(config.data_folder, image['local_path'])
                assert os.path.exists(local_path), f"Downloaded image not found: {local_path}"
    
    @pytest.mark.asyncio
    async def test_image_download_with_crawler_method(self, config):
        """Test image download using crawler's download method."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.download_images_from_page("https://httpbin.org/html")
            
            assert isinstance(result, dict)
            assert 'images' in result
            assert 'total_found' in result
            assert 'total_downloaded' in result
            assert 'success' in result
            
            if result['success']:
                assert isinstance(result['images'], list)
                assert isinstance(result['total_found'], int)
                assert isinstance(result['total_downloaded'], int)
                
                # Check downloaded images
                for image in result['images']:
                    assert 'original_url' in image
                    assert 'local_path' in image
                    assert 'web_path' in image
                    
                    # Verify file exists
                    local_path = os.path.join(config.data_folder, image['local_path'])
                    assert os.path.exists(local_path)
    
    @pytest.mark.asyncio
    async def test_image_download_directory_structure(self, config):
        """Test that images are saved in correct directory structure."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch(
                "https://httpbin.org/html",
                download_images=True
            )
            
            if len(result.images) > 0:
                image = result.images[0]
                local_path = image['local_path']
                
                # Should follow yyyymm/timestamp_random.ext pattern
                path_parts = local_path.split('/')
                assert len(path_parts) >= 3  # downloaded_images/yyyymm/filename
                assert path_parts[0] == 'downloaded_images'
                
                # Check yyyymm format
                yyyymm = path_parts[1]
                assert len(yyyymm) == 6
                assert yyyymm.isdigit()
                
                # Check filename format (timestamp_random.ext)
                filename = path_parts[2]
                assert '_' in filename
                assert '.' in filename
    
    @pytest.mark.asyncio
    async def test_image_download_web_paths(self, config):
        """Test web path generation for downloaded images."""
        # Test with web prefix
        config.image_web_prefix = "https://example.com/static"
        
        async with BrowserCrawler(config) as crawler:
            result = await crawler.fetch(
                "https://httpbin.org/html",
                download_images=True
            )
            
            if len(result.images) > 0:
                image = result.images[0]
                web_path = image['web_path']
                
                # Should include the web prefix
                assert web_path.startswith("https://example.com/static/")
                assert 'downloaded_images' in web_path
    
    @pytest.mark.asyncio
    async def test_image_download_error_handling(self, config):
        """Test image download error handling."""
        async with BrowserCrawler(config) as crawler:
            # Test with invalid URL
            result = await crawler.download_images_from_page("https://invalid-domain-that-does-not-exist.com")
            
            assert isinstance(result, dict)
            assert 'success' in result
            
            # Should handle errors gracefully
            if not result['success']:
                assert 'error' in result or result['total_downloaded'] == 0
    
    @pytest.mark.asyncio
    async def test_image_download_session_isolation(self, config):
        """Test image download with session isolation."""
        async with BrowserCrawler(config) as crawler:
            # Download images with different sessions
            result1 = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="image_session_1",
                download_images=True
            )
            
            result2 = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="image_session_2", 
                download_images=True
            )
            
            assert result1.success is True
            assert result2.success is True
            
            # Both should work independently
            assert isinstance(result1.images, list)
            assert isinstance(result2.images, list)
    
    @pytest.mark.asyncio
    async def test_image_download_file_formats(self, config):
        """Test image download with different file formats."""
        async with BrowserCrawler(config) as crawler:
            # Test with a site that might have different image formats
            result = await crawler.download_images_from_page("https://httpbin.org/image/png")
            
            assert isinstance(result, dict)
            assert 'success' in result
            
            if result['success'] and result['total_downloaded'] > 0:
                # Check that files were actually downloaded
                for image in result['images']:
                    local_path = os.path.join(config.data_folder, image['local_path'])
                    assert os.path.exists(local_path)
                    
                    # Check file size
                    file_size = os.path.getsize(local_path)
                    assert file_size > 0, f"Downloaded image is empty: {local_path}"
    
    @pytest.mark.asyncio
    async def test_image_download_concurrent(self, config):
        """Test concurrent image download operations."""
        async with BrowserCrawler(config) as crawler:
            # Test multiple concurrent image downloads
            urls = [
                "https://httpbin.org/html",
                "https://httpbin.org/image/png",
                "https://httpbin.org/image/jpeg"
            ]
            
            tasks = [
                crawler.download_images_from_page(url)
                for url in urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            assert len(results) == len(urls)
            
            # Check that all results are valid (not exceptions)
            for i, result in enumerate(results):
                assert not isinstance(result, Exception), f"Task {i} raised exception: {result}"
                assert isinstance(result, dict)
                assert 'success' in result
    
    @pytest.mark.asyncio
    async def test_image_download_cleanup(self, config):
        """Test that image download doesn't leave temporary files."""
        async with BrowserCrawler(config) as crawler:
            # Download some images
            result = await crawler.fetch(
                "https://httpbin.org/html",
                download_images=True
            )
            
            # Check data folder structure
            data_folder = Path(config.data_folder)
            downloaded_images_dir = data_folder / "downloaded_images"
            
            if downloaded_images_dir.exists():
                # Should only contain organized directories and files
                for item in downloaded_images_dir.iterdir():
                    if item.is_dir():
                        # Should be yyyymm format
                        assert len(item.name) == 6
                        assert item.name.isdigit()
                        
                        # Check files in directory
                        for file_item in item.iterdir():
                            assert file_item.is_file()
                            assert '_' in file_item.name  # timestamp_random format
    
    @pytest.mark.asyncio
    async def test_image_download_performance(self, config):
        """Test image download performance."""
        import time
        
        async with BrowserCrawler(config) as crawler:
            start_time = time.time()
            
            result = await crawler.download_images_from_page("https://httpbin.org/html")
            
            end_time = time.time()
            download_time = end_time - start_time
            
            # Image download should complete within reasonable time
            assert download_time < 30.0, f"Image download too slow: {download_time:.2f}s"
            
            if result.get('success'):
                print(f"Image download completed in {download_time:.2f}s")
                print(f"Downloaded {result.get('total_downloaded', 0)} images")


@pytest.mark.integration
@pytest.mark.browser
class TestImageDownloadEdgeCases:
    """Test edge cases for image download."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=1,
                data_folder=temp_dir,
                download_images=True
            )
    
    @pytest.mark.asyncio
    async def test_image_download_no_images(self, config):
        """Test image download on page with no images."""
        async with BrowserCrawler(config) as crawler:
            result = await crawler.download_images_from_page("https://httpbin.org/json")
            
            assert isinstance(result, dict)
            assert result.get('success', False) is True
            assert result.get('total_found', 0) == 0
            assert result.get('total_downloaded', 0) == 0
            assert len(result.get('images', [])) == 0
    
    @pytest.mark.asyncio
    async def test_image_download_invalid_images(self, config):
        """Test image download with invalid image URLs."""
        async with BrowserCrawler(config) as crawler:
            # This should handle invalid images gracefully
            result = await crawler.download_images_from_page("https://httpbin.org/status/404")
            
            assert isinstance(result, dict)
            assert 'success' in result
            # Should not crash, even if no images are found or downloaded
