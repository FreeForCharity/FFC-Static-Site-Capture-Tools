# FFC Static Site Capture Tools

This repository provides tools to capture static website content for charities from various sources. These tools are particularly useful when a charity has lost access to their website or needs to migrate from platforms that don't offer export functionality.

## Use Cases

### 1. Wayback Machine (Internet Archive)
When a charity has lost access to their website, we can recover content from the Internet Archive's Wayback Machine. This tool downloads HTML, CSS, JavaScript, images, and other static assets from archived snapshots.

### 2. Wix Sites
Wix doesn't provide a native export feature for static sites. This tool scrapes the live Wix site and downloads all content and resources, creating a static copy that can be migrated to another platform.

### 3. WordPress Sites
For WordPress sites where traditional export methods aren't available or practical, this tool captures the static rendered content by crawling pages and downloading all associated resources.

## Features

- **Wayback Machine Capture**: Download archived websites from specific timestamps
- **Wix Site Capture**: Extract static content from Wix-generated sites
- **WordPress Capture**: Scrape WordPress sites including automatic page discovery via REST API and sitemaps
- **Resource Download**: Automatically download CSS, JavaScript, images, fonts, and other assets
- **Recursive Crawling**: Follow internal links to capture entire site structure
- **Respectful Scraping**: Built-in delays to avoid overwhelming servers

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/FreeForCharity/FFC-Static-Site-Capture-Tools.git
cd FFC-Static-Site-Capture-Tools
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Unified CLI Tool

The `ffc_capture.py` script provides a unified interface for all capture sources:

```bash
# Capture from Wayback Machine (latest snapshot)
python ffc_capture.py wayback https://example.org -o ./output

# Capture from Wayback Machine (specific timestamp)
python ffc_capture.py wayback https://example.org -t 20200101000000 -o ./output

# Capture from Wix site
python ffc_capture.py wix https://example.wixsite.com/mysite -o ./output

# Capture from WordPress site
python ffc_capture.py wordpress https://example.com -o ./output
```

### Individual Module Usage

You can also use the individual capture modules directly:

#### Wayback Machine Capture

```bash
# Capture latest snapshot
python wayback_capture.py https://example.org

# Capture specific timestamp (YYYYMMDDHHMMSS format)
python wayback_capture.py https://example.org 20200101000000

# Specify output directory
python wayback_capture.py https://example.org 20200101000000 ./my_output
```

#### Wix Site Capture

```bash
# Basic capture
python wix_capture.py https://example.wixsite.com/mysite

# Specify output directory
python wix_capture.py https://example.wixsite.com/mysite ./my_output

# Set maximum crawl depth (default is 2)
python wix_capture.py https://example.wixsite.com/mysite ./my_output 3
```

#### WordPress Capture

```bash
# Basic capture
python wordpress_capture.py https://example.com

# Specify output directory
python wordpress_capture.py https://example.com ./my_output
```

## Command-Line Options

### Unified Tool (`ffc_capture.py`)

```
positional arguments:
  {wayback,wix,wordpress}  Source type to capture from
  url                      URL of the site to capture

optional arguments:
  -h, --help              Show help message
  -o OUTPUT, --output OUTPUT
                          Output directory (default: <source>_capture)
  -t TIMESTAMP, --timestamp TIMESTAMP
                          Wayback Machine timestamp (YYYYMMDDHHMMSS)
                          Only for wayback source
  -d MAX_DEPTH, --max-depth MAX_DEPTH
                          Maximum crawl depth (default: 2)
                          For wix and wayback sources
```

## Output Structure

Each tool creates a directory structure that mirrors the original website:

```
output_directory/
├── index.html
├── about/
│   └── index.html
├── css/
│   └── styles.css
├── js/
│   └── script.js
├── images/
│   ├── logo.png
│   └── banner.jpg
└── wp-content/      # WordPress specific
    └── uploads/
        └── ...
```

## How It Works

### Wayback Machine Capture
1. Queries the Wayback Machine API to find available snapshots
2. Downloads HTML pages from the specified (or latest) timestamp
3. Extracts and downloads all linked resources (CSS, JS, images, etc.)
4. Recursively follows internal links up to the specified depth
5. Preserves the original site structure

### Wix Site Capture
1. Fetches the live Wix site HTML
2. Parses the HTML to extract all resource references
3. Downloads CSS, JavaScript, images, and other assets
4. Processes CSS files to download fonts and background images
5. Follows internal links to capture multiple pages

### WordPress Capture
1. Attempts to discover pages via WordPress REST API
2. Falls back to sitemap.xml for page discovery
3. Downloads each discovered page
4. Extracts and downloads all resources (themes, plugins, media)
5. Handles WordPress-specific paths (/wp-content/, /wp-includes/)

## Limitations and Considerations

- **Dynamic Content**: These tools capture static content only. Interactive features requiring server-side processing or JavaScript execution won't work in the captured version.
- **Rate Limiting**: Tools include delays to be respectful to servers. Captures may take time for large sites.
- **Authentication**: Tools don't handle password-protected content or login-required areas.
- **External Resources**: Resources hosted on external domains (CDNs, external services) are downloaded if publicly accessible.
- **Legal Compliance**: Always ensure you have permission to capture and use the website content. Respect copyright and terms of service.

## Troubleshooting

### Connection Errors
If you encounter connection errors, the site may have rate limiting. Try:
- Increasing delays between requests
- Reducing the max-depth parameter
- Running the capture during off-peak hours

### Missing Resources
Some resources may not be captured if:
- They're loaded dynamically via JavaScript
- They're behind authentication
- They're served from restricted domains
- URLs are obfuscated or encoded

### Large Sites
For very large sites:
- Use a lower max-depth to reduce scope
- Capture sections separately
- Ensure sufficient disk space

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Support

For questions or support, please open an issue on GitHub.

## Acknowledgments

This project was created to support the Free For Charity initiative in helping charities maintain and migrate their web presence.
