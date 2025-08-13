# Deployment Troubleshooting Guide
## The Cogitating Ceviche - GitHub Pages Issues & Solutions

---

## 🚨 CSS 404 Error Fix (RESOLVED)

### Problem
Website showing error: `main.min.a435900c9526553f612703c08ba3e4d4d06b303313ad79f8c5e26ef4b75d634b.css:1 Failed to load resource: the server responded with a status of 404 ()`

### Root Cause
Hugo was generating CSS files with incorrect baseURL paths for GitHub Pages deployment with custom domain.

### Solution Steps

1. **Verify Configuration**
   ```bash
   # Check hugo.toml baseURL setting
   cat hugo.toml | grep baseURL
   # Should show: baseURL = "https://cogitating-ceviche.com"
   ```

2. **Rebuild with Correct BaseURL**
   ```bash
   hugo --minify --baseURL "https://cogitating-ceviche.com/"
   ```

3. **Commit and Deploy**
   ```bash
   git add .
   git commit -m "Rebuild site with correct baseURL and fix CSS deployment issue

   🤖 Generated with [Claude Code](https://claude.ai/code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   git push origin main
   ```

4. **Verify Files**
   - ✅ CSS file exists: `public/ananke/css/main.min.a435900c9526553f612703c08ba3e4d4d06b303313ad79f8c5e26ef4b75d634b.css`
   - ✅ CNAME file correct: `cogitating-ceviche.com`
   - ✅ BaseURL matches domain in hugo.toml

### Prevention
Always use the full baseURL when building for deployment:
```bash
hugo --minify --baseURL "https://cogitating-ceviche.com/"
```

---

## 🔧 Common GitHub Pages Issues

### Issue: Custom Domain Not Working

**Symptoms:**
- Site accessible via github.io URL but not custom domain
- SSL certificate errors
- DNS resolution failures

**Diagnosis:**
```bash
# Check CNAME file
cat public/CNAME
# Should contain: cogitating-ceviche.com

# Check DNS settings
nslookup cogitating-ceviche.com
dig cogitating-ceviche.com
```

**Solution:**
1. Verify CNAME file in public/ directory
2. Check GitHub Pages settings in repository
3. Verify DNS A records point to GitHub Pages IPs:
   - 185.199.108.153
   - 185.199.109.153
   - 185.199.110.153
   - 185.199.111.153

### Issue: Build Failures

**Symptoms:**
- GitHub Actions failing
- Site not updating after push
- Build timeout errors

**Diagnosis:**
```bash
# Check GitHub Actions logs
gh run list
gh run view [run-id]

# Local build test
hugo --minify --baseURL "https://cogitating-ceviche.com/"
```

**Solution:**
1. Ensure hugo.toml is valid
2. Check theme compatibility
3. Verify all content files have valid frontmatter
4. Clear Hugo cache: `hugo mod clean`

### Issue: Assets Not Loading

**Symptoms:**
- Images showing 404
- CSS/JS files missing
- Broken asset paths

**Diagnosis:**
```bash
# Check asset paths in HTML
curl -s https://cogitating-ceviche.com | grep -E "(href|src)="

# Verify files exist locally
ls -la public/ananke/css/
ls -la public/images/
```

**Solution:**
1. Rebuild with correct baseURL
2. Check theme asset configuration
3. Verify static file placement
4. Update asset references in templates

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] Hugo configuration validated (`hugo.toml`)
- [ ] BaseURL set to production domain
- [ ] CNAME file contains correct domain
- [ ] All content has valid YAML frontmatter
- [ ] Local build successful

### Build Process
```bash
# Standard deployment build
hugo --minify --baseURL "https://cogitating-ceviche.com/"

# Verify critical files exist
ls -la public/CNAME
ls -la public/index.html
ls -la public/ananke/css/

# Check for broken links (optional)
hugo --minify --baseURL "https://cogitating-ceviche.com/" --printUnusedTemplates
```

### Post-Deployment
- [ ] Site loads at custom domain
- [ ] CSS/JS assets loading properly
- [ ] Images displaying correctly
- [ ] Internal links working
- [ ] SSL certificate valid

### Verification Commands
```bash
# Test site accessibility
curl -I https://cogitating-ceviche.com

# Check CSS loading
curl -I https://cogitating-ceviche.com/ananke/css/main.min.[hash].css

# Verify HTTPS redirect
curl -I http://cogitating-ceviche.com
```

---

## 🛠️ Quick Fix Commands

### Complete Site Rebuild
```bash
# Clean everything and rebuild
rm -rf public/ resources/
hugo --minify --baseURL "https://cogitating-ceviche.com/"
git add .
git commit -m "Complete site rebuild"
git push origin main
```

### CSS Fix Only
```bash
# Just rebuild and push (preserves other changes)
hugo --minify --baseURL "https://cogitating-ceviche.com/"
git add public/
git commit -m "Fix CSS deployment paths"
git push origin main
```

### Emergency Rollback
```bash
# Revert to last working commit
git log --oneline -5  # Find last good commit
git reset --hard [commit-hash]
git push --force origin main
```

---

## 📊 Monitoring & Maintenance

### Regular Checks
- Weekly: Verify site accessibility and asset loading
- Monthly: Update Hugo version and theme
- Quarterly: Review and update DNS settings

### Monitoring Tools
- **GitHub Actions**: Automatic build status
- **Browser Dev Tools**: Check for 404s and loading issues
- **Online Tools**: SSL Labs, GTmetrix for performance

### Log Locations
- **GitHub Actions**: Repository → Actions tab
- **Browser Console**: F12 → Console tab
- **Hugo Logs**: `hugo --verbose` for detailed output

---

## 🆘 Emergency Contacts & Resources

### Key Resources
- **Hugo Documentation**: https://gohugo.io/documentation/
- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **Ananke Theme**: https://github.com/theNewDynamic/gohugo-theme-ananke

### Support Commands
```bash
# Get help
hugo help
gh --help

# Version information
hugo version
git --version
gh --version

# Repository status
git status
git remote -v
gh repo view
```

---

**Last Updated**: August 13, 2025  
**Status**: CSS 404 Issue Resolved ✅