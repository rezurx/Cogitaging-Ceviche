# Hugo Build Process Guide
## The Cogitating Ceviche - Complete Build Documentation

---

## 🏗️ Build Process Overview

This guide documents the complete Hugo build process for The Cogitating Ceviche, including proper commands, configurations, and troubleshooting for GitHub Pages deployment.

---

## ⚙️ Configuration Requirements

### Hugo Configuration (hugo.toml)
```toml
baseURL = "https://cogitating-ceviche.com"
title = "The Cogitating Ceviche"
theme = "ananke"

[pagination]
  pagerSize = 35

[author]
  name = "Conrad T. Hannon"

[params]
  author = "Conrad T. Hannon"
  description = "Where history meets modern madness - satirical commentary by Conrad T. Hannon"
  favicon = "/images/fish-logo.png"
  site_logo = "/images/fish-logo.png"
  mainSections = ["external-articles"]
  recent_posts_number = 20
```

### Required Files
- `hugo.toml` - Site configuration
- `public/CNAME` - Custom domain configuration (contains: `cogitating-ceviche.com`)
- `content/external-articles/` - Blog post content
- `themes/ananke/` - Hugo theme files

---

## 🔨 Build Commands

### Standard Development Build
```bash
# Basic build for local testing
hugo

# Build with live reload server
hugo server
# Access at: http://localhost:1313
```

### Production Build (GitHub Pages)
```bash
# ALWAYS use this command for production deployment
hugo --minify --baseURL "https://cogitating-ceviche.com/"
```

**⚠️ Critical**: Always specify the full baseURL for production builds to ensure proper asset paths.

### Build Variations
```bash
# Build with verbose output (debugging)
hugo --minify --baseURL "https://cogitating-ceviche.com/" --verbose

# Build with draft content
hugo --minify --baseURL "https://cogitating-ceviche.com/" --buildDrafts

# Build with future-dated content
hugo --minify --baseURL "https://cogitating-ceviche.com/" --buildFuture

# Complete clean build
rm -rf public/ resources/
hugo --minify --baseURL "https://cogitating-ceviche.com/"
```

---

## 📁 Build Output Structure

### Generated Directory Structure
```
public/                                    # Build output directory
├── index.html                            # Homepage
├── sitemap.xml                           # Site sitemap
├── CNAME                                 # GitHub Pages custom domain
├── 404.html                              # Error page
├── ananke/                               # Theme assets
│   └── css/
│       ├── main.min.[hash].css          # Minified CSS
│       └── main.css.map                 # Source map
├── external-articles/                   # Blog posts
│   ├── index.html                       # Article listing
│   ├── index.xml                        # RSS feed
│   └── [article-slug]/
│       └── index.html                   # Individual articles
├── images/                              # Static images
├── categories/                          # Category pages
├── tags/                               # Tag pages
└── page/                               # Pagination
```

### Key Generated Files
- **index.html**: Main homepage with article grid
- **sitemap.xml**: SEO sitemap for search engines
- **CNAME**: Contains custom domain for GitHub Pages
- **CSS Files**: Minified and hashed for cache busting
- **RSS Feeds**: XML feeds for content syndication

---

## 🔄 Complete Build Workflow

### 1. Pre-Build Preparation
```bash
# Navigate to project directory
cd /home/resurx/websites/cogitating-ceviche

# Verify Hugo installation
hugo version
# Expected: Hugo v0.147.9 or later

# Check configuration
hugo config
```

### 2. Content Updates (Optional)
```bash
# Update external articles if needed
python3 ingest_external_articles.py

# Check for content validation
hugo --printUnusedTemplates
```

### 3. Production Build
```bash
# Clean previous build (recommended)
rm -rf public/ resources/

# Build for production
hugo --minify --baseURL "https://cogitating-ceviche.com/"

# Verify critical files exist
ls -la public/CNAME public/index.html public/ananke/css/
```

### 4. Deployment
```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Rebuild site with updated content

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Deploy to GitHub Pages
git push origin main
```

### 5. Verification
```bash
# Wait 1-2 minutes for GitHub Pages deployment, then test
curl -I https://cogitating-ceviche.com
curl -I https://cogitating-ceviche.com/ananke/css/main.min.[hash].css
```

---

## 🐛 Build Troubleshooting

### Common Build Errors

#### Error: Template Not Found
```
ERROR: template not found
```
**Solution:**
```bash
# Check theme installation
ls -la themes/ananke/
git submodule update --init --recursive
```

#### Error: Config File Invalid
```
ERROR: failed to parse config
```
**Solution:**
```bash
# Validate TOML syntax
hugo config
# Fix syntax errors in hugo.toml
```

#### Error: Content Parse Failure
```
ERROR: failed to parse frontmatter
```
**Solution:**
```bash
# Check YAML frontmatter in content files
hugo --printPathWarnings
# Fix invalid YAML in content/external-articles/*.md
```

### Performance Issues

#### Slow Build Times
```bash
# Check for large files
find content/ -size +1M -type f

# Use faster build (skip some optimizations)
hugo --minify --baseURL "https://cogitating-ceviche.com/" --noTimes
```

#### Memory Issues
```bash
# Reduce memory usage
hugo --minify --baseURL "https://cogitating-ceviche.com/" --gc
```

---

## 📊 Build Validation

### Automated Checks
```bash
# HTML validation (requires external tool)
htmlproofer public/ --check-html --check-external-hash

# Internal link checking
hugo --minify --baseURL "https://cogitating-ceviche.com/" --printUnusedTemplates

# Performance testing
lighthouse https://cogitating-ceviche.com --view
```

### Manual Verification Checklist
- [ ] Homepage loads with article grid
- [ ] CSS styling applied correctly
- [ ] Images display properly
- [ ] Internal links work
- [ ] RSS feeds accessible
- [ ] Mobile responsive design
- [ ] SEO meta tags present

---

## 🔧 Build Optimization

### Performance Optimizations
```bash
# Minification (already included in production build)
hugo --minify --baseURL "https://cogitating-ceviche.com/"

# Image optimization (manual)
# Optimize images before placing in static/images/

# CSS/JS bundling (handled by theme)
# Ananke theme automatically bundles assets
```

### SEO Optimizations
- Canonical URLs automatically set to baseURL
- Meta tags generated from frontmatter
- Sitemap.xml automatically generated
- RSS feeds created for content sections

### Caching Optimizations
- CSS files include content hash for cache busting
- Static assets use Hugo's fingerprinting
- Proper HTTP headers for GitHub Pages caching

---

## 📚 Build Scripts

### Automated Build Script
Create `build.sh`:
```bash
#!/bin/bash
# Production build script for The Cogitating Ceviche

echo "🏗️ Building The Cogitating Ceviche for production..."

# Clean previous build
rm -rf public/ resources/

# Build site
hugo --minify --baseURL "https://cogitating-ceviche.com/"

# Verify critical files
if [[ -f "public/index.html" && -f "public/CNAME" ]]; then
    echo "✅ Build successful!"
    echo "📁 Output directory: public/"
    echo "🌐 Ready for deployment to: https://cogitating-ceviche.com"
else
    echo "❌ Build failed - missing critical files"
    exit 1
fi
```

Make executable:
```bash
chmod +x build.sh
./build.sh
```

### Development Script
Create `dev.sh`:
```bash
#!/bin/bash
# Development server script

echo "🚀 Starting development server..."
hugo server --bind=0.0.0.0 --baseURL="" --buildDrafts --buildFuture
```

---

## 📝 Build History & Notes

### Recent Build Changes
- **August 13, 2025**: Fixed CSS 404 error by ensuring proper baseURL in production builds
- **August 12, 2025**: Updated to Hugo v0.147.9, improved build reliability
- **August 11, 2025**: Implemented automated content ingestion pipeline

### Known Issues
- Theme updates may require manual intervention
- Large content updates can cause temporary build slowdowns
- Custom CSS modifications need careful testing

### Future Improvements
- Implement automated image optimization
- Add build performance monitoring
- Consider CI/CD pipeline for content updates

---

**Last Updated**: August 13, 2025  
**Hugo Version**: v0.147.9  
**Build Status**: ✅ Stable