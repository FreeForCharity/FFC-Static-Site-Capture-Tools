#!/usr/bin/env python3
"""
Wayback Machine Static Site Capture Tool

This module provides functionality to download static website content
from the Internet Archive's Wayback Machine. Useful when a charity has
lost access to their website but it's archived.
"""

import os
import re
import sys
import requests
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
from typing import Set, Optional


class WaybackCapture:
    """Capture static site content from Wayback Machine."""
    
    def __init__(self, base_url: str, output_dir: str = "wayback_capture"):
        """
        Initialize Wayback Machine capture.
        
        Args:
            base_url: The original URL to capture from Wayback Machine
            output_dir: Directory to save captured content
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.downloaded_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; FFC-Static-Capture/1.0)'
        })
        
    def get_wayback_url(self, url: str, timestamp: Optional[str] = None) -> str:
        """
        Convert a regular URL to a Wayback Machine URL.
        
        Args:
            url: Original URL
            timestamp: Specific timestamp (YYYYMMDDHHMMSS) or None for latest
            
        Returns:
            Wayback Machine URL
        """
        if timestamp:
            return f"https://web.archive.org/web/{timestamp}/{url}"
        else:
            return f"https://web.archive.org/web/{url}"
    
    def get_latest_snapshot(self, url: str) -> Optional[str]:
        """
        Get the latest snapshot timestamp for a URL.
        
        Args:
            url: URL to check
            
        Returns:
            Timestamp of latest snapshot or None
        """
        api_url = f"https://archive.org/wayback/available?url={url}"
        try:
            response = self.session.get(api_url, timeout=10)
            data = response.json()
            if data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                timestamp = data['archived_snapshots']['closest']['timestamp']
                return timestamp
        except Exception as e:
            print(f"Error getting latest snapshot: {e}")
        return None
    
    def download_file(self, wayback_url: str, local_path: Path) -> bool:
        """
        Download a file from Wayback Machine.
        
        Args:
            wayback_url: Wayback Machine URL
            local_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            response = self.session.get(wayback_url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded: {local_path}")
            return True
        except Exception as e:
            print(f"Error downloading {wayback_url}: {e}")
            return False
    
    def _is_html_page(self, url: str) -> bool:
        """
        Check if a URL likely points to an HTML page.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be an HTML page
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check for explicit HTML extensions
        if path.endswith(('.html', '.htm')):
            return True
        
        # Check if it's a directory-like path (ends with /)
        # These typically serve index.html
        if path.endswith('/'):
            return True
        
        # If no extension and not ending with /, likely an HTML page
        # (many modern sites use clean URLs without .html)
        if '.' not in os.path.basename(path):
            return True
        
        return False
    
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
        
        # Default to index.html if path is empty or ends with /
        if not path or path.endswith('/'):
            path = os.path.join(path, 'index.html')
        
        # Add .html extension if no extension present
        if '.' not in os.path.basename(path):
            path += '.html'
        
        return self.output_dir / path
    
    def capture_site(self, timestamp: Optional[str] = None, max_depth: int = 3) -> None:
        """
        Capture entire site from Wayback Machine.
        
        Args:
            timestamp: Specific timestamp or None for latest
            max_depth: Maximum depth for crawling
        """
        if not timestamp:
            timestamp = self.get_latest_snapshot(self.base_url)
            if not timestamp:
                print(f"No snapshots found for {self.base_url}")
                return
        
        print(f"Capturing site from Wayback Machine")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {timestamp}")
        print(f"Output directory: {self.output_dir}")
        print("-" * 60)
        
        # Start with the base URL
        self._capture_url(self.base_url, timestamp, depth=0, max_depth=max_depth)
        
        print("-" * 60)
        print(f"Capture complete! Downloaded {len(self.downloaded_urls)} files")
        print(f"Files saved to: {self.output_dir.absolute()}")
    
    def _capture_url(self, url: str, timestamp: str, depth: int, max_depth: int) -> None:
        """
        Recursively capture a URL and its resources.
        
        Args:
            url: URL to capture
            timestamp: Wayback Machine timestamp
            depth: Current recursion depth
            max_depth: Maximum recursion depth
        """
        if depth > max_depth or url in self.downloaded_urls:
            return
        
        self.downloaded_urls.add(url)
        wayback_url = self.get_wayback_url(url, timestamp)
        local_path = self.url_to_path(url)
        
        if not self.download_file(wayback_url, local_path):
            return
        
        # Only parse HTML files for links
        if local_path.suffix in ['.html', '.htm']:
            self._process_html(local_path, url, timestamp, depth, max_depth)
    
    def _process_html(self, html_path: Path, base_url: str, timestamp: str, 
                     depth: int, max_depth: int) -> None:
        """
        Process HTML file to extract and download linked resources.
        
        Args:
            html_path: Path to HTML file
            base_url: Base URL for resolving relative links
            timestamp: Wayback Machine timestamp
            depth: Current depth
            max_depth: Maximum depth
        """
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find all resource URLs (links, scripts, images, stylesheets)
            patterns = [
                r'href=["\']([^"\']+)["\']',
                r'src=["\']([^"\']+)["\']',
                r'url\(["\']?([^"\'()]+)["\']?\)',
            ]
            
            urls_to_download = set()
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match.startswith(('http://', 'https://', '//')):
                        if match.startswith('//'):
                            match = 'https:' + match
                        urls_to_download.add(match)
                    elif not match.startswith(('data:', 'mailto:', 'javascript:', '#')):
                        full_url = urljoin(base_url, match)
                        urls_to_download.add(full_url)
            
            # Download resources
            for resource_url in urls_to_download:
                # Only follow links on the same domain for deeper crawling
                if urlparse(resource_url).netloc == urlparse(self.base_url).netloc:
                    # HTML pages can be crawled deeper
                    if self._is_html_page(resource_url):
                        self._capture_url(resource_url, timestamp, depth + 1, max_depth)
                    else:
                        # Download other resources without increasing depth
                        self._capture_url(resource_url, timestamp, depth, max_depth)
                        
        except Exception as e:
            print(f"Error processing HTML {html_path}: {e}")


def main():
    """Main entry point for Wayback Machine capture tool."""
    if len(sys.argv) < 2:
        print("Usage: python wayback_capture.py <url> [timestamp] [output_dir]")
        print("\nExamples:")
        print("  python wayback_capture.py https://example.org")
        print("  python wayback_capture.py https://example.org 20200101000000")
        print("  python wayback_capture.py https://example.org 20200101000000 ./my_capture")
        sys.exit(1)
    
    url = sys.argv[1]
    timestamp = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "wayback_capture"
    
    capturer = WaybackCapture(url, output_dir)
    capturer.capture_site(timestamp=timestamp)


if __name__ == "__main__":
    main()
