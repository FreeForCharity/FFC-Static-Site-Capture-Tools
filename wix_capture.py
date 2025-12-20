#!/usr/bin/env python3
"""
Wix Site Static Capture Tool

This module provides functionality to capture static content from Wix-generated
websites. Since Wix doesn't provide an export feature, this tool scrapes the
static HTML and downloads all associated resources.
"""

import os
import re
import sys
import time
import hashlib
import requests
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
from typing import Set, Optional
from bs4 import BeautifulSoup


class WixCapture:
    """Capture static site content from Wix websites."""
    
    def __init__(self, base_url: str, output_dir: str = "wix_capture"):
        """
        Initialize Wix site capture.
        
        Args:
            base_url: The Wix site URL to capture
            output_dir: Directory to save captured content
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.downloaded_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def close(self) -> None:
        """Close the underlying HTTP session and release resources."""
        if hasattr(self, 'session') and self.session is not None:
            self.session.close()
            self.session = None
    
    def __enter__(self) -> "WixCapture":
        """Enter the runtime context related to this object."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the runtime context and close the HTTP session."""
        self.close()
    
    def __del__(self) -> None:
        """Ensure the HTTP session is closed when the object is garbage collected."""
        self.close()
        
    def url_to_path(self, url: str) -> Path:
        """
        Convert a URL to a local file path.
        
        Args:
            url: URL to convert
            
        Returns:
            Local file path
        """
        parsed = urlparse(url)
        path = unquote(parsed.path)
        
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
        
        # Handle query parameters for assets
        if parsed.query:
            # For Wix assets with query params, create a safe filename
            path = path.replace('/', '_').replace('\\', '_')
            if not path:
                path = 'index'
            # Use hashlib for consistent hashing across runs
            query_hash = hashlib.md5(parsed.query.encode()).hexdigest()[:8]
            path = f"{path}_{query_hash}"
        
        # Default to index.html if path is empty or ends with /
        if not path or path.endswith('/'):
            path = os.path.join(path, 'index.html')
        
        # Ensure proper extension based on content type
        if '.' not in os.path.basename(path):
            path += '.html'
        
        return self.output_dir / path
    
    def _is_css_file(self, url: str) -> bool:
        """
        Check if a URL points to a CSS file.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be a CSS file
        """
        parsed = urlparse(url)
        # Get the path without query parameters or fragments
        path = parsed.path.lower()
        return path.endswith('.css')
    
    def download_file(self, url: str, local_path: Optional[Path] = None) -> bool:
        """
        Download a file from the URL.
        
        Args:
            url: URL to download
            local_path: Optional local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        if url in self.downloaded_urls:
            return True
        
        if local_path is None:
            local_path = self.url_to_path(url)
        
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Determine file extension from content type if not present
            if local_path.suffix == '':
                content_type = response.headers.get('Content-Type', '')
                ext = self._get_extension_from_content_type(content_type)
                if ext:
                    local_path = local_path.with_suffix(ext)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_urls.add(url)
            print(f"Downloaded: {local_path}")
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def _get_extension_from_content_type(self, content_type: str) -> Optional[str]:
        """Get file extension from content type."""
        content_type_map = {
            'text/html': '.html',
            'text/css': '.css',
            'application/javascript': '.js',
            'text/javascript': '.js',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/webp': '.webp',
            'font/woff': '.woff',
            'font/woff2': '.woff2',
            'font/ttf': '.ttf',
            'font/otf': '.otf',
        }
        
        for ct, ext in content_type_map.items():
            if ct in content_type:
                return ext
        return None
    
    def extract_resources_from_html(self, html_content: str, base_url: str) -> Set[str]:
        """
        Extract all resource URLs from HTML content.
        
        Args:
            html_content: HTML content as string
            base_url: Base URL for resolving relative URLs
            
        Returns:
            Set of resource URLs
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
        except Exception:
            # Fallback to built-in parser if lxml is unavailable or fails
            soup = BeautifulSoup(html_content, 'html.parser')
        resources = set()
        
        # Extract from various tags
        for tag, attr in [
            ('link', 'href'),
            ('script', 'src'),
            ('img', 'src'),
            ('img', 'data-src'),  # Lazy loaded images
            ('source', 'src'),
            ('video', 'src'),
            ('audio', 'src'),
            ('iframe', 'src'),
        ]:
            for element in soup.find_all(tag):
                url = element.get(attr)
                if url and not url.startswith(('data:', 'mailto:', 'javascript:', '#')):
                    full_url = urljoin(base_url, url)
                    resources.add(full_url)
        
        # Extract URLs from inline CSS
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_urls = self._extract_urls_from_css(style_tag.string, base_url)
                resources.update(css_urls)
        
        # Extract from style attributes
        for element in soup.find_all(style=True):
            css_urls = self._extract_urls_from_css(element['style'], base_url)
            resources.update(css_urls)
        
        return resources
    
    def _extract_urls_from_css(self, css_content: str, base_url: str) -> Set[str]:
        """Extract URLs from CSS content."""
        resources = set()
        # Match url() in CSS
        url_pattern = r'url\(["\']?([^"\'()]+)["\']?\)'
        matches = re.findall(url_pattern, css_content)
        
        for match in matches:
            if not match.startswith(('data:', '#')):
                full_url = urljoin(base_url, match)
                resources.add(full_url)
        
        return resources
    
    def process_css_file(self, css_path: Path, base_url: str) -> None:
        """
        Process CSS file to download referenced resources.
        
        Args:
            css_path: Path to CSS file
            base_url: Base URL for resolving relative URLs
        """
        try:
            with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
                css_content = f.read()
            
            resources = self._extract_urls_from_css(css_content, base_url)
            
            for resource_url in resources:
                self.download_file(resource_url)
                
        except Exception as e:
            print(f"Error processing CSS {css_path}: {e}")
    
    def capture_page(self, url: str, depth: int = 0, max_depth: int = 2) -> None:
        """
        Capture a single page and its resources.
        
        Args:
            url: URL to capture
            depth: Current recursion depth
            max_depth: Maximum recursion depth
        """
        if depth > max_depth or url in self.downloaded_urls:
            return
        
        print(f"Capturing page: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            html_content = response.text
            
            # Save HTML
            local_path = self.url_to_path(url)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.downloaded_urls.add(url)
            print(f"Saved HTML: {local_path}")
            
            # Extract and download resources
            resources = self.extract_resources_from_html(html_content, url)
            
            for resource_url in resources:
                # Download CSS files and process them
                if self._is_css_file(resource_url):
                    if self.download_file(resource_url):
                        css_path = self.url_to_path(resource_url)
                        self.process_css_file(css_path, resource_url)
                else:
                    # Download other resources
                    self.download_file(resource_url)
                
                # Add small delay to be respectful
                time.sleep(0.1)
            
            # Extract and follow internal links (only on same domain)
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except Exception:
                # Fallback to built-in parser if lxml is unavailable or fails
                soup = BeautifulSoup(html_content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
                    full_url = urljoin(url, href)
                    parsed_link = urlparse(full_url)
                    parsed_base = urlparse(self.base_url)
                    
                    # Only follow links on the same domain
                    if parsed_link.netloc == parsed_base.netloc:
                        # Remove fragment
                        full_url = full_url.split('#')[0]
                        self.capture_page(full_url, depth + 1, max_depth)
            
        except Exception as e:
            print(f"Error capturing page {url}: {e}")
    
    def capture_site(self, max_depth: int = 2) -> None:
        """
        Capture entire Wix site.
        
        Args:
            max_depth: Maximum depth for crawling
        """
        print(f"Capturing Wix site")
        print(f"Base URL: {self.base_url}")
        print(f"Output directory: {self.output_dir}")
        print(f"Max depth: {max_depth}")
        print("-" * 60)
        
        self.capture_page(self.base_url, depth=0, max_depth=max_depth)
        
        print("-" * 60)
        print(f"Capture complete! Downloaded {len(self.downloaded_urls)} files")
        print(f"Files saved to: {self.output_dir.absolute()}")


def main():
    """Main entry point for Wix capture tool."""
    if len(sys.argv) < 2:
        print("Usage: python wix_capture.py <url> [output_dir] [max_depth]")
        print("\nExamples:")
        print("  python wix_capture.py https://example.wixsite.com/mysite")
        print("  python wix_capture.py https://example.wixsite.com/mysite ./my_capture")
        print("  python wix_capture.py https://example.wixsite.com/mysite ./my_capture 3")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "wix_capture"
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    capturer = WixCapture(url, output_dir)
    capturer.capture_site(max_depth=max_depth)


if __name__ == "__main__":
    main()
