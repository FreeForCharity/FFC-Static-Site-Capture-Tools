#!/usr/bin/env python3
"""
WordPress Site Static Capture Tool

This module provides functionality to capture static content from WordPress
websites by scraping pages and downloading all associated resources.
"""

import os
import re
import sys
import time
import requests
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
from typing import Set, List, Optional
from bs4 import BeautifulSoup


class WordPressCapture:
    """Capture static site content from WordPress websites."""
    
    def __init__(self, base_url: str, output_dir: str = "wordpress_capture"):
        """
        Initialize WordPress site capture.
        
        Args:
            base_url: The WordPress site URL to capture
            output_dir: Directory to save captured content
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.downloaded_urls: Set[str] = set()
        self.pages: List[str] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def close(self) -> None:
        """Close the underlying HTTP session and release resources."""
        if hasattr(self, 'session') and self.session is not None:
            self.session.close()
            self.session = None
    
    def __enter__(self) -> "WordPressCapture":
        """Enter the runtime context related to this object."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the runtime context and close the HTTP session."""
        self.close()
    
    def __del__(self) -> None:
        """Ensure the HTTP session is closed when the object is garbage collected."""
        self.close()
        
    def discover_pages_via_api(self) -> List[str]:
        """
        Discover pages using WordPress REST API.
        
        Returns:
            List of page URLs
        """
        pages = []
        
        try:
            # Try to get posts via REST API
            api_endpoints = [
                f"{self.base_url}/wp-json/wp/v2/posts?per_page=100",
                f"{self.base_url}/wp-json/wp/v2/pages?per_page=100",
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        items = response.json()
                        for item in items:
                            if 'link' in item:
                                pages.append(item['link'])
                                print(f"Discovered: {item['link']}")
                except Exception as e:
                    print(f"API endpoint {endpoint} not available: {e}")
                    
        except Exception as e:
            print(f"Error discovering pages via API: {e}")
        
        return pages
    
    def discover_pages_via_sitemap(self) -> List[str]:
        """
        Discover pages using sitemap.xml.
        
        Returns:
            List of page URLs
        """
        pages = []
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/wp-sitemap.xml",
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    # Try lxml-xml parser first, fall back to xml if not available
                    try:
                        soup = BeautifulSoup(response.content, 'lxml-xml')
                    except Exception:
                        soup = BeautifulSoup(response.content, 'xml')
                    
                    # Extract URLs from sitemap
                    for loc in soup.find_all('loc'):
                        url = loc.text.strip()
                        if url.endswith('.xml'):
                            # This is a sitemap index, fetch the child sitemap
                            pages.extend(self._parse_sitemap(url))
                        else:
                            pages.append(url)
                            print(f"Discovered from sitemap: {url}")
                    break
            except Exception as e:
                print(f"Sitemap {sitemap_url} not available: {e}")
        
        return pages
    
    def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """Parse a sitemap and extract URLs."""
        pages = []
        try:
            response = self.session.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                # Try lxml-xml parser first, fall back to xml if not available
                try:
                    soup = BeautifulSoup(response.content, 'lxml-xml')
                except Exception:
                    soup = BeautifulSoup(response.content, 'xml')
                    
                for loc in soup.find_all('loc'):
                    url = loc.text.strip()
                    if not url.endswith('.xml'):
                        pages.append(url)
        except Exception as e:
            print(f"Error parsing sitemap {sitemap_url}: {e}")
        
        return pages
    
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
        
        # Handle WordPress media library URLs
        if '/wp-content/' in path or '/wp-includes/' in path:
            # Keep the WordPress structure for assets
            pass
        else:
            # For pages, create a friendly structure
            if not path or path.endswith('/'):
                path = os.path.join(path, 'index.html')
            elif '.' not in os.path.basename(path):
                path = os.path.join(path, 'index.html')
        
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
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_urls.add(url)
            print(f"Downloaded: {local_path}")
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
    
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
            ('img', 'srcset'),
            ('img', 'data-src'),
            ('source', 'src'),
            ('source', 'srcset'),
            ('video', 'src'),
            ('audio', 'src'),
            ('iframe', 'src'),
        ]:
            for element in soup.find_all(tag):
                value = element.get(attr)
                if not value:
                    continue
                    
                # Handle srcset which can have multiple URLs and optional descriptors (e.g., "2x", "1920w")
                if attr == 'srcset':
                    # Split on commas to get individual candidates, each of form: "url [descriptor]"
                    for candidate in value.split(','):
                        candidate = candidate.strip()
                        if not candidate:
                            continue
                        # The URL is the first token before any descriptor (e.g., "2x", "1920w")
                        url_part = candidate.split()[0] if candidate.split() else candidate
                        if not url_part or url_part.startswith(('data:', 'mailto:', 'javascript:', '#')):
                            continue
                        full_url = urljoin(base_url, url_part)
                        resources.add(full_url)
                elif not value.startswith(('data:', 'mailto:', 'javascript:', '#')):
                    full_url = urljoin(base_url, value)
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
    
    def capture_page(self, url: str) -> None:
        """
        Capture a single page and its resources.
        
        Args:
            url: URL to capture
        """
        if url in self.downloaded_urls:
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
                # Only download resources from the same domain
                if urlparse(resource_url).netloc == urlparse(self.base_url).netloc:
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
            
        except Exception as e:
            print(f"Error capturing page {url}: {e}")
    
    def capture_site(self) -> None:
        """Capture entire WordPress site."""
        print(f"Capturing WordPress site")
        print(f"Base URL: {self.base_url}")
        print(f"Output directory: {self.output_dir}")
        print("-" * 60)
        
        # Discover pages
        print("Discovering pages via WordPress REST API...")
        api_pages = self.discover_pages_via_api()
        
        print("\nDiscovering pages via sitemap...")
        sitemap_pages = self.discover_pages_via_sitemap()
        
        # Combine and deduplicate
        all_pages = list(set([self.base_url] + api_pages + sitemap_pages))
        print(f"\nFound {len(all_pages)} pages to capture")
        print("-" * 60)
        
        # Capture each page
        for page_url in all_pages:
            self.capture_page(page_url)
        
        print("-" * 60)
        print(f"Capture complete! Downloaded {len(self.downloaded_urls)} files")
        print(f"Files saved to: {self.output_dir.absolute()}")


def main():
    """Main entry point for WordPress capture tool."""
    if len(sys.argv) < 2:
        print("Usage: python wordpress_capture.py <url> [output_dir]")
        print("\nExamples:")
        print("  python wordpress_capture.py https://example.com")
        print("  python wordpress_capture.py https://example.com ./my_capture")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "wordpress_capture"
    
    capturer = WordPressCapture(url, output_dir)
    try:
        capturer.capture_site()
    finally:
        capturer.close()


if __name__ == "__main__":
    main()
