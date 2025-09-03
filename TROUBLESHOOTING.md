# Cogitating Ceviche Website - Troubleshooting Guide

This document captures solutions to common issues encountered with the website deployment and functionality.

## Navigation and Menu Issues

### Problem: Navigation changes not appearing on live site
**Symptoms:** Menu configuration in `hugo.toml` works locally but doesn't show on deployed site.

**Root Cause:** Hardcoded navigation in template files bypasses Hugo's menu system.

**Solution:**
1. Check `layouts/index.html` for hardcoded navigation links
2. Replace hardcoded links with Hugo menu template:
   ```html
   <ul id="nav-links" class="nav-links">
     {{ range .Site.Menus.main }}
     <li><a href="{{ .URL }}" {{ if strings.HasPrefix .URL "http" }}rel="noopener"{{ end }}>{{ .Name }}</a></li>
     {{ end }}
   </ul>
   ```
3. Ensure `hugo.toml` has proper menu configuration:
   ```toml
   [[menu.main]]
     name = "Page Name"
     url = "/page-url/"
     weight = 10
   ```

## Deployment and Build Issues

### Problem: GitHub Actions builds succeed but site doesn't update
**Symptoms:** Workflow shows "success" but deployed site remains unchanged.

**Root Cause:** Multiple deployment methods conflicting or wrong target branch.

**Solution:**
1. Check if site is configured for GitHub Pages from `gh-pages` branch vs GitHub Actions
2. Ensure deployment workflow pushes to correct branch:
   ```yaml
   - name: Deploy to gh-pages branch
     uses: peaceiris/actions-gh-pages@v4
     with:
       github_token: ${{ secrets.GITHUB_TOKEN }}
       publish_dir: ./public
       publish_branch: gh-pages
   ```
3. Verify workflow has proper permissions:
   ```yaml
   permissions:
     contents: write
     pages: write
   ```

### Problem: Hugo theme not loading (layout warnings)
**Symptoms:** 
```
WARN found no layout file for "html" for kind "page"
```
Only 6 pages built instead of 50+.

**Root Cause:** Git submodules not initialized in GitHub Actions.

**Solution:**
Add `submodules: true` to checkout steps:
```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
    submodules: true
```

### Problem: GitHub Actions permission denied to gh-pages
**Symptoms:** `remote: Permission to repo.git denied to github-actions[bot]`

**Solution:**
1. Add `contents: write` permission to workflow
2. Use `peaceiris/actions-gh-pages@v4` action instead of manual git commands

## Page Layout and Styling Issues

### Problem: Custom pages use wrong layout/styling
**Symptoms:** Page appears with black text on black background or wrong theme.

**Root Cause:** Hugo theme layouts override custom layouts due to lookup order.

**Solutions:**
1. **Section-specific layouts:** Move page to section directory
   - Move `content/about.md` → `content/about/index.md`
   - Create `layouts/about/single.html`

2. **Layout hierarchy:** Hugo prioritizes layouts in this order:
   - `layouts/[section]/single.html`
   - `layouts/_default/single.html` 
   - `themes/[theme]/layouts/_default/single.html`

### Problem: Duplicate headings on custom pages
**Symptoms:** Page shows "About" and "About Page Title" as two headings.

**Root Cause:** Layout displays page title AND content has same heading.

**Solution:** Remove duplicate heading from content markdown file.

## Content and Data Issues

### Problem: Articles not updating despite RSS changes
**Symptoms:** New posts don't appear on site.

**Root Cause:** Multiple automation workflows conflicting or failing.

**Solution:**
1. Check active workflows in `.github/workflows/`
2. Keep only working workflows (e.g., `ingest.yml`)
3. Disable failing workflows by renaming to `.yml.disabled`

### Problem: About page returns 404
**Symptoms:** Navigation link exists but page not found.

**Root Causes & Solutions:**
1. **Page not built:** Check Hugo build includes the page
2. **Wrong path:** Ensure content file structure matches URL expectation
3. **Deployment issue:** Page built locally but not deployed
4. **Date format:** Use proper RFC 3339 format: `2025-09-02T00:00:00Z`

## Debugging Commands

### Local Testing
```bash
# Build and check locally
hugo --gc --minify --baseURL "https://cogitating-ceviche.com"
ls -la public/about/  # Check if page was built

# Test navigation configuration
hugo config | grep -A 10 menu
```

### Remote Debugging
```bash
# Check deployed page status
curl -I "https://cogitating-ceviche.com/about/"

# Check latest GitHub Actions runs
curl -s -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/rezurx/Cogitaging-Ceviche/actions/runs | \
  jq '.workflow_runs[:3] | .[] | {name: .name, status: .status, conclusion: .conclusion}'

# Sync with deployed branch
git fetch origin gh-pages
git checkout gh-pages
git reset --hard origin/gh-pages
```

### Git Submodule Issues
```bash
# Initialize submodules locally
git submodule update --init --recursive

# Check submodule status
git submodule status
```

## File Structure Reference

### Critical Files
- `hugo.toml` - Site configuration and menu settings
- `layouts/index.html` - Homepage template
- `layouts/_default/single.html` - Default page template  
- `layouts/[section]/single.html` - Section-specific templates
- `.github/workflows/deploy.yml` - Main deployment workflow
- `static/css/grid-styles.css` - Site styling

### Content Organization
- `content/` - Markdown content files
- `content/about/index.md` - About page (as section)
- `content/external-articles/` - Blog posts
- `static/` - Static assets (CSS, images)
- `public/` - Generated site (not committed)

## Common Workflow Issues

1. **Always check git status** before making changes
2. **Pull latest changes** before pushing to avoid conflicts  
3. **Monitor GitHub Actions** after pushing changes
4. **Test locally first** with `hugo server` when possible
5. **Check both `main` and `gh-pages` branches** when debugging deployment

## Emergency Fixes

If site breaks completely:
1. Check GitHub Actions for failed workflows
2. Revert to last working commit: `git revert HEAD`
3. Check `gh-pages` branch for deployment issues
4. Verify `CNAME` file exists in deployed site
5. Manually trigger workflow: GitHub → Actions → "Build and Deploy Hugo Site" → "Run workflow"