# Runtime Environment & Alternatives

This document provides guidance on where and how to run these Python scripts, along with comprehensive information about alternative solutions—both open-source and commercial—that could replace or complement these tools.

## Where to Run These Scripts

### Local Execution (Recommended for Most Users)

**Requirements:**
- Python 3.7 or higher
- 4GB RAM minimum (8GB+ recommended for large sites)
- Sufficient disk space for captured content
- Internet connection

**Platforms:**
- **Windows**: Command Prompt, PowerShell, or Windows Terminal
- **macOS**: Terminal.app or iTerm2
- **Linux**: Any terminal emulator (bash, zsh, etc.)

**Setup Instructions:**
```bash
# 1. Clone the repository
git clone https://github.com/FreeForCharity/FFC-Static-Site-Capture-Tools.git
cd FFC-Static-Site-Capture-Tools

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the tools
python3 ffc_capture.py wayback https://example.org -o ./output
```

### Cloud Execution Options

**GitHub Actions / GitLab CI:**
- Schedule automated captures
- Store results in repository or cloud storage
- No local machine required
- Free for public repositories

**AWS Lambda / Google Cloud Functions:**
- Serverless execution for periodic captures
- Pay only for execution time
- Can trigger via cron or webhooks
- Requires containerization for dependencies

**VPS / Cloud Servers:**
- DigitalOcean, Linode, AWS EC2, etc.
- Full control over execution environment
- Good for large or frequent captures
- Can run scheduled cron jobs

**Docker Containers:**
- Portable execution environment
- Easy deployment to any platform
- Consistent dependencies across systems

### Example Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "ffc_capture.py", "wayback", "https://example.org"]
```

---

## Alternative Open-Source Solutions

### 1. Wayback Machine / Archive Capture Alternatives

#### **ArchiveBox** ⭐ Highly Recommended
- **GitHub**: https://github.com/ArchiveBox/ArchiveBox
- **Type**: Self-hosted web archiving platform
- **Features**:
  - Multiple format saving (HTML, PDF, screenshots, WARC)
  - Scheduled crawls and monitoring
  - Browser history import
  - Git-friendly storage
  - Web UI for management
- **Best For**: Long-term archiving, compliance, research
- **Installation**: `pip install archivebox`
- **Actively Maintained**: Yes (1.6k+ commits, 20k+ stars)

#### **HTTrack**
- **Website**: https://www.httrack.com/
- **GitHub**: https://github.com/xroche/httrack
- **Type**: Desktop GUI and CLI
- **Features**:
  - Preserves directory structure
  - Scheduling and filtering
  - Mirror entire websites offline
- **Best For**: Simple offline browsing, beginners
- **Actively Maintained**: Yes (but less frequent updates)

#### **Wget**
- **Website**: https://www.gnu.org/software/wget/
- **Type**: Command-line tool
- **Features**:
  - Powerful recursive download
  - Resume support
  - Scriptable automation
- **Best For**: Automated mirroring, server environments
- **Example**: `wget -r -p -k https://example.org`

#### **grab-site**
- **GitHub**: https://github.com/ArchiveTeam/grab-site
- **Type**: CLI archiver with WARC output
- **Features**:
  - Dashboard for monitoring
  - Dynamic ignore patterns
  - Integration with Archive Team
- **Best For**: Large-scale archival projects

#### **Crawlee**
- **GitHub**: https://github.com/apify/crawlee
- **Type**: Node.js/Python library
- **Features**:
  - API-driven scraping
  - Browser automation (Puppeteer/Playwright)
  - Anti-blocking features
  - Persistent queue
- **Best For**: Complex, dynamic sites requiring JavaScript execution

### 2. Wix Site Capture Alternatives

#### **Cloneable**
- **GitHub**: https://github.com/CloneableApp/Cloneable
- **Type**: Desktop application (Electron/React)
- **Features**:
  - GUI for site cloning
  - Uses wget internally
  - Smart resource linkage
- **Best For**: All-in-one desktop solution
- **Platform**: Windows, macOS, Linux

#### **Cyotek WebCopy**
- **Website**: https://www.cyotek.com/cyotek-webcopy
- **Type**: GUI tool (Windows only)
- **Features**:
  - Configurable crawling
  - Link remapping
  - Resource scanning
- **Best For**: Windows users wanting simple interface
- **Free**: Yes

#### **SiteSucker** (macOS)
- **Website**: https://ricks-apps.com/osx/sitessucker/
- **Type**: macOS application
- **Features**:
  - Native Mac app
  - Multi-threaded downloading
  - Scheduled operations
- **Free**: Basic version free, Pro version paid

### 3. WordPress Capture Alternatives

#### **Simply Static** ⭐ Highly Recommended
- **WordPress Plugin**: https://wordpress.org/plugins/simply-static/
- **GitHub**: https://github.com/Simply-Static/simply-static
- **Type**: WordPress plugin
- **Features**:
  - Direct export from WordPress dashboard
  - Multiple deployment options (ZIP, SFTP, GitHub Pages)
  - Search integration (Fuse.js/Algolia)
  - Form support (Contact Form 7, Gravity Forms)
- **Best For**: WordPress site owners with admin access
- **Free**: Yes
- **Actively Maintained**: Yes (active development)

#### **WP2Static**
- **WordPress Plugin**: https://wordpress.org/plugins/static-html-output-plugin/
- **GitHub**: https://github.com/WP2Static/wp2static
- **Type**: WordPress plugin
- **Features**:
  - Static site generation
  - Automated deployment
  - CloudFlare, S3, Netlify integration
- **Best For**: WordPress to static hosting migration
- **Free**: Yes

#### **Staatic**
- **WordPress Plugin**: https://wordpress.org/plugins/staatic/
- **Type**: WordPress plugin
- **Features**:
  - Static HTML generation
  - Automatic deployment
  - Multiple publishing methods
- **Best For**: WordPress users wanting JAMstack deployment

---

## Commercial Solutions

### 1. Website Scraping & Archiving Services

#### **ScraperAPI**
- **Website**: https://www.scraperapi.com/
- **Type**: SaaS web scraping service
- **Features**:
  - Automated proxy rotation
  - CAPTCHA solving
  - API-based extraction
  - 99.9% uptime SLA
- **Pricing**: From $49/month
- **Best For**: Developers needing scalable, reliable scraping

#### **Apify**
- **Website**: https://apify.com/
- **Type**: Web scraping and automation platform
- **Features**:
  - Wayback Machine integration
  - Scheduled crawling
  - WARC export
  - API access
  - Pre-built actors/scrapers
- **Pricing**: Free tier available, paid from $49/month
- **Best For**: Automated archiving and scraping workflows

#### **Octoparse**
- **Website**: https://www.octoparse.com/
- **Type**: No-code scraping platform
- **Features**:
  - Visual point-and-click interface
  - Cloud-based or desktop
  - Template workflows
  - Scheduled extraction
- **Pricing**: From $99/month
- **Best For**: Non-technical users

#### **ParseHub**
- **Website**: https://www.parsehub.com/
- **Type**: Visual web scraping tool
- **Features**:
  - No-code setup
  - JavaScript rendering
  - API access
  - Scheduled runs
- **Pricing**: Free tier, paid from $189/month
- **Best For**: Structured data extraction

#### **Bright Data (formerly Luminati)**
- **Website**: https://brightdata.com/
- **Type**: Enterprise data collection platform
- **Features**:
  - Massive proxy network
  - Compliance tools
  - Global coverage
  - 24/7 support
- **Pricing**: Custom/enterprise (typically $500+/month)
- **Best For**: Large-scale enterprise needs

### 2. Wix Migration Services

#### **SiteBuilders.PRO**
- **Website**: https://sitebuilders.pro/wix-to-html-migration
- **Type**: Professional migration service
- **Features**:
  - Manual hand-crafted conversion
  - SEO optimization
  - Fixed pricing
  - 5-10 day turnaround
- **Best For**: Custom Wix sites requiring precise replication

#### **Wixipy**
- **Website**: https://wixipy.com/
- **Type**: Website migration specialists
- **Features**:
  - Zero downtime migration
  - Data protection
  - Multi-platform support (Wix, WordPress, Shopify)
  - Ongoing support
- **Best For**: Business sites requiring professional migration

#### **CronixWeb**
- **Website**: https://cronixweb.com/
- **Type**: eCommerce migration specialists
- **Features**:
  - Product data preservation
  - Customer data migration
  - SEO retention
  - Stress-free process
- **Best For**: Wix eCommerce stores

### 3. Website Archiving Services

#### **Archive.today**
- **Website**: https://archive.today/
- **Type**: Free instant archiving service
- **Features**:
  - Permanent snapshots
  - No account required
  - Fast archival
- **Free**: Yes
- **Best For**: Quick one-off snapshots

#### **PageFreezer**
- **Website**: https://www.pagefreezer.com/
- **Type**: Compliance archiving platform
- **Features**:
  - Automated scheduled archiving
  - Legal compliance
  - Social media archiving
  - Tamper-proof records
- **Pricing**: Custom/enterprise
- **Best For**: Regulated industries, legal compliance

#### **Stillio**
- **Website**: https://stillio.com/
- **Type**: Visual website archiving
- **Features**:
  - Automatic screenshots
  - Scheduled captures
  - Change detection
  - Visual timeline
- **Pricing**: From $29/month
- **Best For**: Visual archiving, change tracking

---

## Comparison: When to Use Each Solution

### Use This Repository's Scripts When:
- ✅ You need a lightweight, customizable solution
- ✅ You want to understand and modify the code
- ✅ You're on a tight budget (completely free)
- ✅ You need basic capture for charity websites
- ✅ You want Python-based tools you can integrate into workflows

### Use ArchiveBox When:
- ✅ You need comprehensive, multi-format archiving
- ✅ You want a web UI for management
- ✅ You're archiving many sites regularly
- ✅ You need WARC format for preservation

### Use Simply Static (WordPress) When:
- ✅ You have WordPress admin access
- ✅ You want the easiest export process
- ✅ You need built-in deployment to hosting platforms
- ✅ You want to maintain forms and search

### Use Commercial Services When:
- ✅ You need guaranteed uptime and SLAs
- ✅ You're dealing with complex, anti-bot sites
- ✅ You need professional support
- ✅ Scale is critical (thousands of sites)
- ✅ Legal compliance is required
- ✅ You lack technical expertise

### Use HTTrack/Wget When:
- ✅ You need battle-tested, mature tools
- ✅ You're comfortable with command-line
- ✅ You want maximum configurability
- ✅ Your sites are relatively simple/static

---

## Recommendations by Use Case

### Charity Lost Website Recovery
**Primary**: This repository's Wayback Machine tool  
**Alternative**: ArchiveBox (if need ongoing archiving)  
**Commercial**: Archive.today (for quick snapshots)

### Wix to Static Migration
**Primary**: This repository's Wix capture tool  
**Alternative**: Cloneable (if prefer GUI)  
**Commercial**: SiteBuilders.PRO (if need professional service)

### WordPress Static Export
**Primary**: Simply Static plugin (if have admin access)  
**Alternative**: This repository's WordPress tool (if no admin access)  
**Commercial**: WP2Static with hosting integration

### Enterprise/Large-Scale
**Primary**: ArchiveBox (self-hosted)  
**Alternative**: Apify (if need cloud-based)  
**Commercial**: Bright Data or Octoparse

---

## Contributing Alternative Tools

If you know of other excellent tools that should be listed here, please:
1. Open an issue on GitHub
2. Include: tool name, link, brief description, and why it's valuable
3. Specify if it's open-source or commercial
4. Note if it's actively maintained

---

## License & Legal Considerations

**Important**: Always ensure you have permission to capture website content:
- Respect robots.txt and terms of service
- For charity websites: obtain written permission when possible
- For archived sites: verify you have rights to the content
- Commercial tools may have their own license restrictions
- Review copyright laws in your jurisdiction

This repository and its tools are provided for legitimate archival and migration purposes, particularly for charitable organizations. Use responsibly and ethically.
