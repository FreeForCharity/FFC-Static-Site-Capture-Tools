#!/usr/bin/env python3
"""
FFC Static Site Capture Tool

A unified command-line tool for capturing static website content from various
sources including Wayback Machine, Wix sites, and WordPress sites.
"""

import sys
import argparse

# Import capture modules
from wayback_capture import WaybackCapture
from wix_capture import WixCapture
from wordpress_capture import WordPressCapture


def main():
    """Main entry point for the unified capture tool."""
    parser = argparse.ArgumentParser(
        description='FFC Static Site Capture Tool - Capture static content from various sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture from Wayback Machine
  %(prog)s wayback https://example.org -o ./output
  
  # Capture from Wayback Machine with specific timestamp
  %(prog)s wayback https://example.org -t 20200101000000 -o ./output
  
  # Capture from Wix site
  %(prog)s wix https://example.wixsite.com/mysite -o ./output
  
  # Capture from WordPress site
  %(prog)s wordpress https://example.com -o ./output
        """
    )
    
    parser.add_argument(
        'source',
        choices=['wayback', 'wix', 'wordpress'],
        help='Source type to capture from'
    )
    
    parser.add_argument(
        'url',
        help='URL of the site to capture'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output directory (default: <source>_capture)'
    )
    
    parser.add_argument(
        '-t', '--timestamp',
        default=None,
        help='Wayback Machine timestamp (YYYYMMDDHHMMSS) - only for wayback source'
    )
    
    parser.add_argument(
        '-d', '--max-depth',
        type=int,
        default=2,
        help='Maximum crawl depth (default: 2) - for wix and wayback sources'
    )
    
    args = parser.parse_args()
    
    # Determine output directory
    if args.output is None:
        args.output = f"{args.source}_capture"
    
    print("=" * 60)
    print("FFC Static Site Capture Tool")
    print("=" * 60)
    
    try:
        if args.source == 'wayback':
            capturer = WaybackCapture(args.url, args.output)
            capturer.capture_site(timestamp=args.timestamp, max_depth=args.max_depth)
            
        elif args.source == 'wix':
            capturer = WixCapture(args.url, args.output)
            capturer.capture_site(max_depth=args.max_depth)
            
        elif args.source == 'wordpress':
            capturer = WordPressCapture(args.url, args.output)
            capturer.capture_site()
        
        print("\n" + "=" * 60)
        print("SUCCESS! Site capture completed successfully.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nCapture interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
