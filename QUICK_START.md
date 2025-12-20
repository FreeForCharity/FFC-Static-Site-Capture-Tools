# Quick Start Guide

This guide will help you get started quickly with the FFC Static Site Capture Tools.

## Installation (5 minutes)

1. **Ensure you have Python 3.7+:**
   ```bash
   python3 --version
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/FreeForCharity/FFC-Static-Site-Capture-Tools.git
   cd FFC-Static-Site-Capture-Tools
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Examples

### Capture from Wayback Machine
```bash
# Capture the latest snapshot
python3 ffc_capture.py wayback https://example.org -o ./captured_site

# Capture from a specific date (January 1, 2020)
python3 ffc_capture.py wayback https://example.org -t 20200101000000 -o ./captured_site
```

### Capture from Wix
```bash
python3 ffc_capture.py wix https://yoursite.wixsite.com/sitename -o ./wix_site
```

### Capture from WordPress
```bash
python3 ffc_capture.py wordpress https://your-wordpress-site.com -o ./wp_site
```

## What Happens Next?

After running a capture command:

1. **The tool will start downloading:** You'll see progress messages as files are downloaded
2. **Files are organized:** Content is saved in the output directory with the original structure
3. **Resources are included:** CSS, JavaScript, images, and other assets are downloaded
4. **Completion message:** You'll see a summary when the capture is complete

## Output Structure

After capture, you'll have:
```
output_directory/
├── index.html           # Homepage
├── about/
│   └── index.html       # About page
├── css/                 # Stylesheets
├── js/                  # JavaScript files
├── images/              # Images
└── ...                  # Other resources
```

## Common Options

- `-o` or `--output`: Specify output directory (default: `<source>_capture`)
- `-d` or `--max-depth`: Set crawl depth for Wayback/Wix (default: 2)
- `-t` or `--timestamp`: Wayback Machine timestamp (YYYYMMDDHHMMSS format)

## Tips

- **Start with depth 1-2:** For large sites, use lower depth to test
- **Be patient:** Large sites may take time to download
- **Check disk space:** Ensure you have enough space for the captured content
- **Respect websites:** The tool includes delays to be respectful to servers

## Troubleshooting

### Connection errors?
- Check your internet connection
- The site might have rate limiting (try again later)
- Some sites may block automated access

### Missing content?
- Some dynamic content may not be captured (JavaScript-generated)
- Increase the `--max-depth` value
- For Wayback Machine, try a different timestamp

### Need help?
- Check the full [README.md](README.md) for detailed documentation
- Open an issue on GitHub for support

## Next Steps

- Read the full [README.md](README.md) for more features
- Automate captures with [GitHub Actions](GITHUB_ACTIONS.md)
- Check [ALTERNATIVES.md](ALTERNATIVES.md) for other tools
- Check [examples.py](examples.py) for programmatic usage
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute improvements

## Automation with GitHub Actions

Want to automate your captures? GitHub Actions can:
- Run scheduled backups (daily, weekly, monthly)
- Create Issues with capture reports
- Create Pull Requests with captured content
- No server needed - runs in the cloud for free!

**See [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)** for complete setup guides and examples.

---

**Happy capturing! 🚀**

This tool is part of the Free For Charity initiative to help charities maintain their web presence.
