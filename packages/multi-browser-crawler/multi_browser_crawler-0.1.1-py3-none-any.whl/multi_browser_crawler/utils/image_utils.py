"""
Image Download and Processing Utilities
======================================

Utilities for downloading and processing images from web pages.
"""

import os
import re
import time
import random
import asyncio
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

from ..exceptions.errors import ImageDownloadError

logger = logging.getLogger(__name__)


class ImageDownloader:
    """Download and process images from web pages."""
    
    def __init__(self, data_folder: str = None, web_prefix: str = None):
        """
        Initialize the image downloader.

        Args:
            data_folder: Base data folder path (defaults to ./data)
            web_prefix: Web prefix for serving images (optional)
        """
        self.data_folder = data_folder or os.path.join(os.getcwd(), "data")
        self.base_image_dir = os.path.join(self.data_folder, "downloaded_images")
        
        # Ensure the base image directory exists
        os.makedirs(self.base_image_dir, exist_ok=True)

        self.page = None
        self.web_prefix = web_prefix or ""
        if self.web_prefix.endswith('/'):
            self.web_prefix = self.web_prefix[:-1]

        logger.info(f"Image download directory: {self.base_image_dir}")
        
    def get_web_path(self, relative_path: str) -> str:
        """Construct the full web-accessible path for a downloaded image."""
        if self.web_prefix:
            return f"{self.web_prefix}/{relative_path}"
        return f"/{relative_path}"

    async def set_browser_page(self, page):
        """Set the browser page to use for image downloading."""
        self.page = page
        
    async def download_image(self, image_url: str, base_url: Optional[str] = None) -> Optional[str]:
        """
        Download an image using the browser and save it to the appropriate folder.
        
        Args:
            image_url: URL of the image to download
            base_url: Base URL to resolve relative URLs
            
        Returns:
            Relative path to the downloaded image or None if download failed
        """
        if not self.page:
            logger.error("Browser page not set for image download")
            return None
            
        # Clean the image URL - remove whitespace and quotes
        image_url = image_url.strip().strip('"\'')
        
        # Skip if URL is too short or empty after cleaning
        if not image_url or len(image_url) < 5:
            logger.warning(f"Skipping invalid URL: {image_url}")
            return None
            
        # Resolve relative URLs
        original_url = image_url
        if base_url:
            image_url = urllib.parse.urljoin(base_url, image_url)
            if image_url != original_url:
                logger.debug(f"Resolved URL: {image_url} (from {original_url})")
            
        # Create the directory structure (yyyymm/timestamp_random)
        current_date = datetime.now()
        yyyymm = current_date.strftime("%Y%m")
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        
        # File path components
        img_subdir = os.path.join(self.base_image_dir, yyyymm)
        filename = f"{timestamp}_{random_suffix}"
        
        # Attempt to extract file extension from URL
        parsed_url = urllib.parse.urlparse(image_url)
        path = parsed_url.path
        url_extension = os.path.splitext(path)[1].lower()
        
        # Valid image extensions
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        
        # Use URL extension if it's valid, otherwise determine from content
        if url_extension and url_extension in valid_extensions:
            extension = url_extension
        else:
            extension = None  # Will be determined from response
        
        # Complete filename
        filename = f"{filename}{extension}" if extension else filename
        
        # Ensure the directory exists
        os.makedirs(img_subdir, exist_ok=True)
        
        # Full path to the image file
        temp_image_path = os.path.join(img_subdir, filename)
        logger.debug(f"Downloading image from {image_url}")
        
        try:
            # Use Playwright's request context for fetching
            api_request_context = self.page.context.request
            response = await api_request_context.get(image_url, timeout=15000)

            if not response.ok:
                logger.error(f"Image fetch failed for {image_url}: HTTP {response.status}")
                return None
            
            # Get content type and determine extension if not already set
            content_type = response.headers.get('content-type', '').lower()
            if not extension:
                # Map content types to extensions
                content_type_map = {
                    'image/jpeg': '.jpg',
                    'image/jpg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'image/webp': '.webp',
                    'image/svg+xml': '.svg',
                    'image/bmp': '.bmp',
                    'image/x-icon': '.ico',
                    'image/vnd.microsoft.icon': '.ico'
                }
                
                # Extract main content type (ignore charset etc.)
                main_content_type = content_type.split(';')[0].strip()
                extension = content_type_map.get(main_content_type, '.jpg')
                logger.debug(f"Determined extension '{extension}' from Content-Type '{content_type}'")
                
                # Update filename with determined extension
                filename = f"{timestamp}_{random_suffix}{extension}"
                temp_image_path = os.path.join(img_subdir, filename)
            
            # Validate that this is actually image content
            if content_type and not content_type.startswith('image/'):
                logger.warning(f"Content-Type '{content_type}' is not an image for URL {image_url}")
                return None

            image_data = await response.body()
            if not image_data:
                logger.error(f"Image fetch for {image_url} returned no data")
                return None

            # Save the image
            relative_path = os.path.join("downloaded_images", yyyymm, filename)
            with open(temp_image_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Successfully downloaded image: {os.path.basename(temp_image_path)}")
            return relative_path

        except Exception as e:
            logger.error(f"Error downloading image from {image_url}: {e}")
            return None
    
    async def download_images_from_page(self, url: str, download_path: str = None) -> Dict[str, Any]:
        """
        Download all images from a page.
        
        Args:
            url: URL of the page to download images from
            download_path: Directory to save images (optional)
            
        Returns:
            Dictionary containing download results
        """
        if not self.page:
            raise ImageDownloadError("Browser page not set for image download")
        
        try:
            # Navigate to the page
            await self.page.goto(url)
            
            # Find all image elements
            image_elements = await self.page.query_selector_all('img')
            
            downloaded_images = []
            for img in image_elements:
                src = await img.get_attribute('src')
                if src:
                    local_path = await self.download_image(src, url)
                    if local_path:
                        downloaded_images.append({
                            'original_url': src,
                            'local_path': local_path,
                            'web_path': self.get_web_path(local_path)
                        })
            
            return {
                'images': downloaded_images,
                'total_found': len(image_elements),
                'total_downloaded': len(downloaded_images),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error downloading images from page {url}: {e}")
            raise ImageDownloadError(f"Failed to download images from page: {e}")
    
    def is_image_url(self, url: str) -> bool:
        """
        Determine if a URL points to an image.
        
        Args:
            url: URL to check
            
        Returns:
            True if the URL appears to be an image URL
        """
        if not url or len(url) < 5:
            return False
            
        # Skip data URLs (already embedded)
        if url.startswith('data:'):
            return False
            
        # Check for common image extensions
        image_extensions = r'\.(jpg|jpeg|png|gif|webp|svg|bmp)(\?|$)'
        if re.search(image_extensions, url.lower()):
            return True
            
        # Check for image-specific patterns in the URL
        image_patterns = [
            r'/image[s]?/',
            r'/photo[s]?/',
            r'/picture[s]?/',
            r'/thumbnail[s]?/',
            r'/media/images',
            r'uploads/img',
            r'/assets/img',
            r'/static/img'
        ]
        
        for pattern in image_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    async def close(self):
        """Clean up resources."""
        # No specific cleanup needed
        pass
