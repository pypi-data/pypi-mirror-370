"""
Web Utilities for Multi-Browser Crawler
=======================================

Utilities for processing and cleaning HTML content.
"""

import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup, Comment
import logging

logger = logging.getLogger(__name__)


class HTMLCleaner:
    """Clean and process HTML content."""
    
    def __init__(self):
        """Initialize the HTML cleaner."""
        pass
    
    def clean_html(self, 
                   html_content: str,
                   remove_auxiliary_content: bool = True,
                   remove_hidden_elements: bool = True,
                   remove_interactive_widgets: bool = True,
                   remove_comments_section: bool = True) -> str:
        """
        Clean HTML content by removing unwanted elements and attributes.
        
        Args:
            html_content: The raw HTML string to clean
            remove_auxiliary_content: If True, removes sidebars and auxiliary content
            remove_hidden_elements: If True, removes hidden elements
            remove_interactive_widgets: If True, removes popups, modals, etc.
            remove_comments_section: If True, removes comment sections
            
        Returns:
            Cleaned HTML string
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html5lib')

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove unwanted tags
        unwanted_tags = [
            'script', 'style', 'iframe', 'noscript', 'meta', 'link', 
            'object', 'embed', 'form'
        ]
        for tag_name in unwanted_tags:
            for element in soup.find_all(tag_name):
                element.decompose()

        # Remove navigation and header/footer sections
        for tag_name in ['header', 'nav', 'footer']:
            for element in soup.find_all(tag_name):
                if element.parent:
                    element.decompose()

        # Remove auxiliary content
        if remove_auxiliary_content:
            aux_keywords = [
                'sidebar', 'aside', 'related', 'popular', 'trending', 
                'recommend', 'complementary', 'secondary'
            ]
            
            # Remove aside tags
            for element in soup.find_all('aside'):
                if element.parent:
                    element.decompose()
            
            # Remove elements with auxiliary keywords in id/class
            for keyword in aux_keywords:
                for element in soup.select(f'[id*="{keyword}"], [class*="{keyword}"]'):
                    if element.parent and element.name not in ['body', 'main', 'article']:
                        element.decompose()

        # Remove comment sections
        if remove_comments_section:
            comment_keywords = ['comment', 'discussion', 'replies', 'disqus']
            for keyword in comment_keywords:
                for element in soup.select(f'[id*="{keyword}"], [class*="{keyword}"]'):
                    if element.parent and element.name != 'article':
                        element.decompose()

        # Remove interactive widgets
        if remove_interactive_widgets:
            widget_keywords = [
                'popup', 'modal', 'tooltip', 'dropdown', 'menu', 
                'accordion', 'tab', 'carousel', 'slider'
            ]
            widget_roles = ['tooltip', 'dialog', 'menu', 'alert']

            # Remove by role attribute
            for role in widget_roles:
                for element in soup.find_all(attrs={"role": role}):
                    if element.parent and element.name not in ['main', 'article', 'body']:
                        element.decompose()
            
            # Remove by keyword in id/class
            for keyword in widget_keywords:
                for element in soup.select(f'[id*="{keyword}"], [class*="{keyword}"]'):
                    if element.parent and element.name not in ['main', 'article', 'body']:
                        element.decompose()

        # Remove ad-related elements
        self._remove_ads(soup)

        # Remove hidden elements
        if remove_hidden_elements:
            self._remove_hidden_elements(soup)

        # Clean up attributes
        self._clean_attributes(soup)

        # Format output
        clean_html = str(soup)
        clean_html = self._format_html(clean_html)

        return clean_html
    
    def _remove_ads(self, soup):
        """Remove ad-related elements."""
        ad_patterns = [
            re.compile(r'\bad[s]?\b', re.IGNORECASE),
            re.compile(r'\bbanner\b', re.IGNORECASE),
            re.compile(r'\badvertise(ment)?\b', re.IGNORECASE),
            re.compile(r'\bsponsor(ed)?\b', re.IGNORECASE),
            re.compile(r'\bpromo(tion)?\b', re.IGNORECASE)
        ]

        # Remove elements with ad-related ids or classes
        for element in soup.find_all(attrs={"id": True}):
            if not element.parent:
                continue
            if 'id' in element.attrs:
                for pattern in ad_patterns:
                    if pattern.search(element['id']):
                        element.decompose()
                        break

        for element in soup.find_all(attrs={"class": True}):
            if not element.parent:
                continue
            if 'class' in element.attrs:
                class_str = ' '.join(element['class']) if isinstance(element['class'], list) else element['class']
                for pattern in ad_patterns:
                    if pattern.search(class_str):
                        element.decompose()
                        break
    
    def _remove_hidden_elements(self, soup):
        """Remove elements that are likely hidden."""
        hidden_keywords = ['hidden', 'invisible', 'sr-only', 'screen-reader']
        
        for keyword in hidden_keywords:
            for element in soup.select(f'[class*="{keyword}"]'):
                if element.parent:
                    element.decompose()
        
        # Remove elements with display:none or visibility:hidden
        for element in soup.find_all(attrs={"style": True}):
            if not element.parent:
                continue
            style = element.get('style', '').lower()
            if 'display:none' in style or 'visibility:hidden' in style:
                element.decompose()
    
    def _clean_attributes(self, soup):
        """Clean unwanted attributes from elements."""
        # Attributes to remove
        unwanted_attrs = [
            'style', 'onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout',
            'data-*', 'aria-*'
        ]
        
        for element in soup.find_all():
            if not element.parent:
                continue
            
            # Remove unwanted attributes
            attrs_to_remove = []
            for attr in element.attrs:
                if attr in unwanted_attrs or attr.startswith('data-') or attr.startswith('aria-'):
                    attrs_to_remove.append(attr)
            
            for attr in attrs_to_remove:
                del element.attrs[attr]
    
    def _format_html(self, html_content: str) -> str:
        """Format HTML content for better readability."""
        # Consolidate multiple <br> tags
        html_content = re.sub(r'(<br\s*/?>\s*){2,}', '<br/>\n', html_content, flags=re.IGNORECASE)
        
        # Remove excessive newlines
        html_content = re.sub(r'\n\s*\n', '\n', html_content)
        
        # Collapse multiple spaces
        html_content = re.sub(r' +', ' ', html_content)
        
        # Remove spaces between tags
        html_content = re.sub(r'>\s+\n\s+<', '>\n<', html_content)
        
        # Remove leading/trailing whitespace
        html_content = html_content.strip()
        
        return html_content
    
    def extract_text(self, html_content: str) -> str:
        """Extract plain text from HTML content."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html5lib')
        
        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, html_content: str, base_url: str = None) -> list:
        """Extract all links from HTML content."""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html5lib')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Resolve relative URLs if base_url provided
            if base_url and not href.startswith(('http://', 'https://')):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            
            links.append({
                'url': href,
                'text': text,
                'title': link.get('title', '')
            })
        
        return links
