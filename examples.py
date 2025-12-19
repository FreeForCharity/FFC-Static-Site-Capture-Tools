#!/usr/bin/env python3
"""
Example usage script demonstrating all three capture tools.

This script shows how to use the FFC Static Site Capture Tools
programmatically in your own Python code.
"""

from wayback_capture import WaybackCapture
from wix_capture import WixCapture
from wordpress_capture import WordPressCapture


def example_wayback_capture():
    """Example: Capture a site from Wayback Machine."""
    print("=" * 60)
    print("Example 1: Wayback Machine Capture")
    print("=" * 60)
    
    # Initialize the capturer
    capturer = WaybackCapture(
        base_url="https://example.org",
        output_dir="./examples/wayback_output"
    )
    
    # Capture the site (will use the latest available snapshot)
    # capturer.capture_site(max_depth=2)
    
    # Or capture from a specific timestamp
    # capturer.capture_site(timestamp="20200101000000", max_depth=2)
    
    print("\nWayback capture configured (commented out to avoid actual download)")
    print("Uncomment the capture_site() call above to run")


def example_wix_capture():
    """Example: Capture a Wix site."""
    print("\n" + "=" * 60)
    print("Example 2: Wix Site Capture")
    print("=" * 60)
    
    # Initialize the capturer
    capturer = WixCapture(
        base_url="https://example.wixsite.com/mysite",
        output_dir="./examples/wix_output"
    )
    
    # Capture the site with a maximum depth of 2
    # capturer.capture_site(max_depth=2)
    
    print("\nWix capture configured (commented out to avoid actual download)")
    print("Uncomment the capture_site() call above to run")


def example_wordpress_capture():
    """Example: Capture a WordPress site."""
    print("\n" + "=" * 60)
    print("Example 3: WordPress Site Capture")
    print("=" * 60)
    
    # Initialize the capturer
    capturer = WordPressCapture(
        base_url="https://example.com",
        output_dir="./examples/wordpress_output"
    )
    
    # Capture the site (will auto-discover pages via API and sitemap)
    # capturer.capture_site()
    
    print("\nWordPress capture configured (commented out to avoid actual download)")
    print("Uncomment the capture_site() call above to run")


def example_advanced_usage():
    """Example: Advanced usage with custom configuration."""
    print("\n" + "=" * 60)
    print("Example 4: Advanced Usage")
    print("=" * 60)
    
    # You can also capture individual pages
    from wordpress_capture import WordPressCapture
    
    capturer = WordPressCapture(
        base_url="https://example.com",
        output_dir="./examples/custom_output"
    )
    
    # Capture specific pages
    # capturer.capture_page("https://example.com/about")
    # capturer.capture_page("https://example.com/contact")
    
    print("\nAdvanced capture configured (commented out to avoid actual download)")
    print("You can capture individual pages or customize the crawling behavior")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("FFC Static Site Capture Tools - Examples")
    print("=" * 60)
    print("\nThis script demonstrates how to use the capture tools")
    print("programmatically in your Python code.")
    print("\nNOTE: All capture calls are commented out to prevent")
    print("accidental downloads. Uncomment them to test with real sites.")
    print()
    
    example_wayback_capture()
    example_wix_capture()
    example_wordpress_capture()
    example_advanced_usage()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nTo actually run captures, edit this file and uncomment")
    print("the capture_site() calls with valid URLs.")


if __name__ == "__main__":
    main()
