# GitHub Actions Integration Guide

This guide explains how to use GitHub Actions to automate website capture and feed results into GitHub Issues or Pull Requests.

## Table of Contents
- [Basic GitHub Actions Setup](#basic-github-actions-setup)
- [Scheduled Captures](#scheduled-captures)
- [Feeding Output to GitHub Issues](#feeding-output-to-github-issues)
- [Feeding Output to Pull Requests](#feeding-output-to-pull-requests)
- [Advanced Workflows](#advanced-workflows)
- [Complete Examples](#complete-examples)

---

## Basic GitHub Actions Setup

### Simple Capture Workflow

Create `.github/workflows/capture-site.yml`:

```yaml
name: Capture Website

on:
  workflow_dispatch:  # Manual trigger
    inputs:
      url:
        description: 'Website URL to capture'
        required: true
      source:
        description: 'Source type (wayback, wix, or wordpress)'
        required: true
        default: 'wayback'

jobs:
  capture:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run capture
        env:
          FFC_SOURCE: ${{ inputs.source }}
          FFC_URL: ${{ inputs.url }}
        run: |
          python3 ffc_capture.py "$FFC_SOURCE" "$FFC_URL" -o ./captured_site
      
      - name: Upload captured site as artifact
        uses: actions/upload-artifact@v4
        with:
          name: captured-site-${{ github.run_number }}
          path: ./captured_site
          retention-days: 30
```

**Usage:** Go to Actions tab → Capture Website → Run workflow

---

## Scheduled Captures

### Automated Daily Captures

Create `.github/workflows/scheduled-capture.yml`:

```yaml
name: Scheduled Site Capture

on:
  schedule:
    # Run every day at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  capture:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Capture website
        run: |
          python3 ffc_capture.py wayback https://example.org -o ./output
      
      - name: Create timestamped archive
        run: |
          timestamp=$(date +%Y%m%d_%H%M%S)
          tar -czf "capture_${timestamp}.tar.gz" ./output
      
      - name: Upload to release or artifact
        uses: actions/upload-artifact@v4
        with:
          name: scheduled-capture-${{ github.run_number }}
          path: "*.tar.gz"
          retention-days: 90
```

---

## Feeding Output to GitHub Issues

### Create Issue with Capture Summary

Create `.github/workflows/capture-and-report.yml`:

```yaml
name: Capture and Report to Issue

on:
  workflow_dispatch:
    inputs:
      url:
        description: 'Website URL to capture'
        required: true
      source:
        description: 'Source type'
        required: true
        default: 'wayback'

permissions:
  issues: write
  contents: read

jobs:
  capture-and-report:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run capture and capture output
        id: capture
        env:
          FFC_SOURCE: ${{ inputs.source }}
          FFC_URL: ${{ inputs.url }}
        run: |
          # Run capture and save output
          # Use environment variables so inputs are passed as single, safely-quoted arguments
          python3 ffc_capture.py "$FFC_SOURCE" "$FFC_URL" -o ./captured_site 2>&1 | tee capture_log.txt
          
          # Extract statistics
          file_count=$(find ./captured_site -type f | wc -l)
          total_size=$(du -sh ./captured_site | cut -f1)
          
          # Save to GitHub output
          echo "file_count=${file_count}" >> $GITHUB_OUTPUT
          echo "total_size=${total_size}" >> $GITHUB_OUTPUT
          
          # Create summary for issue
          cat > issue_body.md << EOF
          ## Website Capture Completed
          
          **Source:** ${{ inputs.source }}
          **URL:** ${{ inputs.url }}
          **Date:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
          **Workflow Run:** [#${{ github.run_number }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
          
          ### Statistics
          - **Files captured:** ${file_count}
          - **Total size:** ${total_size}
          
          ### Download
          The captured site is available as a workflow artifact:
          [Download captured site](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
          
          ### Log Output
          \`\`\`
          $(tail -50 capture_log.txt)
          \`\`\`
          EOF
      
      - name: Upload captured site
        uses: actions/upload-artifact@v4
        with:
          name: captured-site-${{ github.run_number }}
          path: ./captured_site
          retention-days: 30
      
      - name: Create GitHub Issue
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const issueBody = fs.readFileSync('issue_body.md', 'utf8');
            
            const issue = await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Site Capture: ${{ inputs.url }} - ${new Date().toISOString().split('T')[0]}`,
              body: issueBody,
              labels: ['automated-capture', '${{ inputs.source }}']
            });
            
            console.log(`Created issue #${issue.data.number}`);
```

**Result:** Creates a new GitHub issue with:
- Capture summary and statistics
- Link to download artifacts
- Log output excerpt
- Labeled for easy filtering

---

## Feeding Output to Pull Requests

### Create PR with Captured Content

Create `.github/workflows/capture-to-pr.yml`:

```yaml
name: Capture and Create PR

on:
  workflow_dispatch:
    inputs:
      url:
        description: 'Website URL to capture'
        required: true
      source:
        description: 'Source type'
        required: true

permissions:
  contents: write
  pull-requests: write

jobs:
  capture-and-pr:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Create branch
        run: |
          timestamp=$(date +%Y%m%d_%H%M%S)
          branch_name="capture/${timestamp}"
          git checkout -b "${branch_name}"
          echo "BRANCH_NAME=${branch_name}" >> $GITHUB_ENV
      
      - name: Run capture
        id: capture
        env:
          FFC_SOURCE: ${{ inputs.source }}
          FFC_URL: ${{ inputs.url }}
        run: |
          # Create captures directory if it doesn't exist
          mkdir -p captures
          
          # Run capture
          timestamp=$(date +%Y%m%d_%H%M%S)
          output_dir="captures/capture_${timestamp}"
          
          python3 ffc_capture.py "$FFC_SOURCE" "$FFC_URL" -o "${output_dir}" 2>&1 | tee capture_log.txt
          
          # Get statistics
          file_count=$(find "${output_dir}" -type f | wc -l)
          total_size=$(du -sh "${output_dir}" | cut -f1)
          
          echo "file_count=${file_count}" >> $GITHUB_OUTPUT
          echo "total_size=${total_size}" >> $GITHUB_OUTPUT
          echo "output_dir=${output_dir}" >> $GITHUB_OUTPUT
      
      - name: Create README for capture
        run: |
          cat > ${{ steps.capture.outputs.output_dir }}/README.md << EOF
          # Captured Website
          
          **Source:** ${{ inputs.source }}
          **Original URL:** ${{ inputs.url }}
          **Captured:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
          **Workflow:** [Run #${{ github.run_number }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
          
          ## Statistics
          - Files: ${{ steps.capture.outputs.file_count }}
          - Size: ${{ steps.capture.outputs.total_size }}
          
          ## Contents
          - \`index.html\` - Homepage
          - \`css/\` - Stylesheets
          - \`js/\` - JavaScript files
          - \`images/\` - Images and media
          
          ## Viewing Locally
          Open \`index.html\` in a web browser to view the captured site.
          EOF
      
      - name: Commit changes
        env:
          COMMIT_URL: ${{ inputs.url }}
          COMMIT_SOURCE: ${{ inputs.source }}
          COMMIT_FILE_COUNT: ${{ steps.capture.outputs.file_count }}
          COMMIT_SIZE: ${{ steps.capture.outputs.total_size }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add captures/
          cat << 'COMMIT_MSG_TEMPLATE' > commit_message_template.txt
          Add captured site from ${COMMIT_URL}
          
          Source: ${COMMIT_SOURCE}
          Files: ${COMMIT_FILE_COUNT}
          Size: ${COMMIT_SIZE}
          COMMIT_MSG_TEMPLATE
          
          envsubst '${COMMIT_URL} ${COMMIT_SOURCE} ${COMMIT_FILE_COUNT} ${COMMIT_SIZE}' < commit_message_template.txt > commit_message.txt
          
          git commit -F commit_message.txt
      
      - name: Push changes
        run: |
          git push origin "${BRANCH_NAME}"
      
      - name: Create Pull Request
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const logContent = fs.readFileSync('capture_log.txt', 'utf8');
            const lastLines = logContent.split('\n').slice(-30).join('\n');
            
            const pr = await github.rest.pulls.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Add captured site: ${{ inputs.url }}`,
              head: process.env.BRANCH_NAME,
              base: 'main',
              body: `## Automated Website Capture
              
              This PR adds a captured version of the website.
              
              **Details:**
              - **URL:** ${{ inputs.url }}
              - **Source:** ${{ inputs.source }}
              - **Captured:** ${new Date().toISOString()}
              - **Workflow:** [Run #${{ github.run_number }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
              
              **Statistics:**
              - Files captured: ${{ steps.capture.outputs.file_count }}
              - Total size: ${{ steps.capture.outputs.total_size }}
              
              **Output directory:** \`${{ steps.capture.outputs.output_dir }}\`
              
              ### Capture Log (last 30 lines)
              \`\`\`
              ${lastLines}
              \`\`\`
              
              ### Next Steps
              - [ ] Review captured content
              - [ ] Verify all resources downloaded correctly
              - [ ] Test the captured site locally
              - [ ] Merge if everything looks good
              
              ---
              *This PR was created automatically by GitHub Actions.*`
            });
            
            console.log(`Created PR #${pr.data.number}`);
```

**Result:** Creates a pull request containing:
- The captured website files
- README with capture metadata
- Detailed PR description with statistics
- Checklist for review

---

## Advanced Workflows

### Comment on Existing Issue with Results

```yaml
name: Update Issue with Capture Results

on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number to update'
        required: true
      url:
        description: 'Website URL to capture'
        required: true

permissions:
  issues: write
  contents: read

jobs:
  capture-and-comment:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run capture
        env:
          URL: ${{ inputs.url }}
        run: |
          python3 ffc_capture.py wayback "$URL" -o ./output 2>&1 | tee log.txt
          
          file_count=$(find ./output -type f | wc -l)
          echo "FILE_COUNT=${file_count}" >> $GITHUB_ENV
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: capture-${{ github.run_number }}
          path: ./output
      
      - name: Comment on issue
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const log = fs.readFileSync('log.txt', 'utf8');
            
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ inputs.issue_number }},
              body: `## ✅ Capture Completed
              
              **URL:** ${{ inputs.url }}
              **Files captured:** ${process.env.FILE_COUNT}
              **Artifact:** [Download here](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
              
              <details>
              <summary>Capture Log</summary>
              
              \`\`\`
              ${log}
              \`\`\`
              </details>`
            });
```

### Add PR Review Comment with Capture Status

```yaml
name: Add PR Comment with Capture

on:
  workflow_dispatch:
    inputs:
      pr_number:
        description: 'Pull request number'
        required: true
      url:
        description: 'Website URL to capture'
        required: true

permissions:
  pull-requests: write
  contents: read

jobs:
  capture-and-review:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run capture
        id: capture
        env:
          URL: ${{ inputs.url }}
        run: |
          python3 ffc_capture.py wayback "$URL" -o ./output 2>&1 | tee log.txt
          
          # Check if capture succeeded
          if [ $? -eq 0 ]; then
            echo "status=success" >> $GITHUB_OUTPUT
            echo "message=✅ Capture completed successfully" >> $GITHUB_OUTPUT
          else
            echo "status=failure" >> $GITHUB_OUTPUT
            echo "message=❌ Capture failed" >> $GITHUB_OUTPUT
          fi
          
          file_count=$(find ./output -type f 2>/dev/null | wc -l)
          echo "file_count=${file_count}" >> $GITHUB_OUTPUT
      
      - name: Upload artifact
        if: steps.capture.outputs.status == 'success'
        uses: actions/upload-artifact@v4
        with:
          name: pr-${{ inputs.pr_number }}-capture
          path: ./output
      
      - name: Add review comment
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.pulls.createReview({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: ${{ inputs.pr_number }},
              event: 'COMMENT',
              body: `${{ steps.capture.outputs.message }}
              
              **Captured:** ${{ inputs.url }}
              **Files:** ${{ steps.capture.outputs.file_count }}
              **Download:** [Artifact](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})`
            });
```

---

## Complete Examples

### End-to-End: Scheduled Capture → Issue Report

Create `.github/workflows/weekly-charity-backup.yml`:

```yaml
name: Weekly Charity Website Backup

on:
  schedule:
    # Every Sunday at 3 AM UTC
    - cron: '0 3 * * 0'
  workflow_dispatch:

permissions:
  issues: write
  contents: write

jobs:
  backup-sites:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        site:
          - url: https://charity1.org
            source: wordpress
          - url: https://charity2.wixsite.com/site
            source: wix
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Capture site
        id: capture
        run: |
          timestamp=$(date +%Y%m%d)
          # Create a unique identifier from the URL for use in tags
          site_id=$(echo ${{ matrix.site.url }} | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-30)
          output="backups/${timestamp}_${site_id}"
          
          python3 ffc_capture.py ${{ matrix.site.source }} ${{ matrix.site.url }} -o "${output}" 2>&1 | tee log.txt
          
          # Statistics
          file_count=$(find "${output}" -type f | wc -l)
          total_size=$(du -sh "${output}" | cut -f1)
          
          # Archive
          tar -czf "${output}.tar.gz" "${output}"
          
          echo "file_count=${file_count}" >> $GITHUB_OUTPUT
          echo "total_size=${total_size}" >> $GITHUB_OUTPUT
          echo "archive=${output}.tar.gz" >> $GITHUB_OUTPUT
          echo "timestamp=${timestamp}" >> $GITHUB_OUTPUT
          echo "site_id=${site_id}" >> $GITHUB_OUTPUT
      
      - name: Upload to releases
        uses: softprops/action-gh-release@c062e08bd532815e2082a85e87e3ef29c3e6d191  # v2.0.8
        with:
          tag_name: backup-${{ steps.capture.outputs.timestamp }}-${{ steps.capture.outputs.site_id }}
          name: Weekly Backup ${{ steps.capture.outputs.timestamp }} - ${{ matrix.site.url }}
          files: ${{ steps.capture.outputs.archive }}
          body: |
            Automated weekly backup of charity websites.
            
            **${{ matrix.site.url }}**
            - Files: ${{ steps.capture.outputs.file_count }}
            - Size: ${{ steps.capture.outputs.total_size }}
      
      - name: Create summary issue
        uses: actions/github-script@v7
        with:
          script: |
            const date = new Date().toISOString().split('T')[0];
            const timestamp = '${{ steps.capture.outputs.timestamp }}';
            const siteId = '${{ steps.capture.outputs.site_id }}';
            
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Weekly Backup Report - ${date} - ${{ matrix.site.url }}`,
              body: `## Automated Backup Completed
              
              **Site:** ${{ matrix.site.url }}
              **Type:** ${{ matrix.site.source }}
              **Date:** ${date}
              
              ### Statistics
              - Files: ${{ steps.capture.outputs.file_count }}
              - Size: ${{ steps.capture.outputs.total_size }}
              
              ### Download
              The backup is available in [Releases](../../releases/tag/backup-${timestamp}-${siteId})
              
              ### Next Backup
              Scheduled for: ${new Date(Date.now() + 7*24*60*60*1000).toISOString().split('T')[0]}`,
              labels: ['automated-backup', 'weekly']
            });
```

---

## Environment Variables and Secrets

### Storing API Keys

If your captures need authentication:

1. Go to Settings → Secrets → Actions
2. Add secrets like `WAYBACK_API_KEY`
3. Use in workflow:

```yaml
- name: Run capture with auth
  env:
    API_KEY: ${{ secrets.WAYBACK_API_KEY }}
    URL: ${{ inputs.url }}
  run: |
    python3 ffc_capture.py wayback "$URL" -o ./output
```

---

## Best Practices

### 1. **Use Artifacts for Large Captures**
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: capture-${{ github.run_number }}
    path: ./output
    retention-days: 30  # Auto-delete after 30 days
```

### 2. **Matrix Builds for Multiple Sites**
```yaml
strategy:
  matrix:
    url: [site1.org, site2.com, site3.net]
```

### 3. **Conditional Issue Creation**
Only create issue if capture succeeds:
```yaml
- name: Create issue
  if: success()
  uses: actions/github-script@v7
```

### 4. **Add Labels for Organization**
```yaml
labels: ['automated', 'wayback-capture', 'charity-backup']
```

### 5. **Store Large Files in Releases**
Use releases for permanent storage instead of artifacts (which expire).

---

## Troubleshooting

### Common Issues

**Problem:** Workflow times out  
**Solution:** Add timeout and split large captures
```yaml
timeout-minutes: 60
```

**Problem:** Out of disk space  
**Solution:** Clean up before capture
```yaml
- name: Free disk space
  run: |
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
```

**Problem:** Rate limiting  
**Solution:** Use GitHub App token for higher limits
```yaml
- uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
```

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [GitHub Script Action](https://github.com/actions/github-script)
- [Upload Artifact Action](https://github.com/actions/upload-artifact)
- [Creating Releases](https://github.com/softprops/action-gh-release)

---

## Summary

GitHub Actions enables powerful automation:

✅ **Scheduled captures** - Run daily/weekly backups automatically  
✅ **Issue reporting** - Create issues with capture summaries  
✅ **PR creation** - Submit captured content for review  
✅ **Artifact storage** - Download captures from workflow runs  
✅ **Release publishing** - Permanent storage in GitHub Releases  
✅ **Matrix builds** - Capture multiple sites in parallel  
✅ **Integration** - Feed results into existing issues/PRs  

Choose the workflow that matches your needs and customize as required!
