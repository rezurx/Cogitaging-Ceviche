# Cogitating-Ceviche to Ceviche Engine: Quick Reference Guide

## Overview
- **Current System**: Hugo-based static blog
- **Target System**: Ceviche Engine
- **Preservation Rate**: 80-85% of functionality
- **Migration Time**: 13-21 hours
- **Risk Level**: Medium (visual fidelity + data continuity critical)

---

## CRITICAL: What MUST Be Preserved

### Homepage Card Grid (THE CENTERPIECE)
```
Current: Client-side JS loads /data/posts.json → renders cards
New: Server-side render same card grid from Ceviche data

MUST PRESERVE:
✓ Responsive grid layout (3-5 columns)
✓ Card styling (colors, shadows, hovers)
✓ 200+ article metadata
✓ Sorting (newest first)
✓ Display limit (top 30)
✓ Image handling (16:9 aspect ratio)
```

### Color Palette
```css
Dark Navigation: #0b0f14
Card Background: #f7f2e5
Card Border: #e6dfcf
Text Primary: #0f1b22
Text Secondary: #6b6b6b
Link Blue: #0066cc
```

### Logo & Branding
- Fish logo PNG (1.4MB) → `/static/images/fish-logo.png`
- Typography: Charter/Georgia serif stack
- Site title: "The Cogitating Ceviche"
- Subtitle: "Food for Thought"

### Navigation Menu
1. The Cogitating Ceviche (substack.com)
2. The Cybernetic Ceviche (substack.com)
3. LinkTree
4. About

---

## PRESERVATION MATRIX

### COPY AS-IS (100% reusable)
```
/static/css/grid-styles.css          → Ceviche styles (86 lines)
/static/images/fish-logo.png         → Keep logo asset
/public/data/posts.json              → Export & migrate data
```

### PORT WITH ADAPTATION (80-85% reusable)
```
/scripts/ingest_substack.py          → Feed parsing logic
  - fetch_rss() function
  - strip_html_to_text() function
  - remove_banned() patterns
  - excerpt generation logic

/automation_config.yaml              → Configuration patterns
  - Feed sources
  - Scheduling templates
  - Error handling strategies
```

### RECREATE NEW (Replace entirely)
```
/layouts/index.html                  → Ceviche template
/layouts/_default/*                  → Ceviche layouts
/hugo.toml                           → Ceviche config
/automation_manager.py               → Ceviche automation
```

---

## PHASED MIGRATION PLAN

### Phase 1: Assets (1-2 hours)
- [ ] Copy CSS files
- [ ] Copy logo & images
- [ ] Define design tokens/variables
- [ ] Test responsive breakpoints

### Phase 2: Homepage Template (3-4 hours) ⚠️ CRITICAL
- [ ] Create card component
- [ ] Implement responsive grid
- [ ] Port all styling
- [ ] Setup server-side data rendering

### Phase 3: Data (2-3 hours)
- [ ] Export posts.json (200+ articles)
- [ ] Create import script
- [ ] Verify data integrity
- [ ] Test sorting/limiting

### Phase 4: Automation (4-6 hours)
- [ ] Port RSS feed logic
- [ ] Setup 6-hour ingestion schedule
- [ ] Implement excerpt generation
- [ ] Test posts.json generation

### Phase 5: Navigation & Pages (1-2 hours)
- [ ] Create navigation component
- [ ] Recreate About page
- [ ] Update menu items
- [ ] Test mobile menu

### Phase 6: Deployment (2-3 hours)
- [ ] Test Ceviche build
- [ ] Update deploy.py paths
- [ ] Verify Hostinger SFTP
- [ ] Setup CI/CD

**Total: 13-21 hours**

---

## KEY FILES REFERENCE

### Source Files (Current Site)
```
/layouts/index.html                  119 lines - Homepage template
/layouts/_default/baseof.html        89 lines  - Base template
/layouts/_default/single.html        Article template
/static/css/grid-styles.css          86 lines  - Main grid styling
/static/images/fish-logo.png         Logo asset
/public/data/posts.json              ~364 lines - Article data
/scripts/ingest_substack.py          150+ lines - Feed parser
/automation_manager.py               ~1000 lines - Automation
/automation_config.yaml              Automation config
/hugo.toml                           Site config
/deploy.py                           Deployment script
```

### Data Structure (posts.json)
```json
{
  "generatedAt": "2025-09-21T05:21:48.872371",
  "items": [
    {
      "title": "string",
      "subtitle": "string (optional)",
      "url": "https://thecogitatingceviche.substack.com/p/...",
      "published": "Fri, 19 Sep 2025 06:01:15 GMT",
      "image": "https://substackcdn.com/...",
      "excerpt": "150-250 words, cleaned",
      "source": "substack"
    }
    // ~200+ items, newest first
  ]
}
```

---

## CRITICAL SUCCESS FACTORS

### MUST NOT BREAK
1. ✓ Homepage grid appears correctly (visual fidelity)
2. ✓ All 200+ articles preserved (data continuity)
3. ✓ Responsive design works (mobile/tablet/desktop)
4. ✓ RSS feeds auto-update (automation)
5. ✓ Navigation works (UX)

### SHOULD WORK
1. ✓ Deployment automation (Hostinger SFTP)
2. ✓ Performance ≥ original
3. ✓ SEO preserved (canonical URLs, meta tags)

### NICE TO HAVE
1. Better performance metrics
2. Email alerting
3. Advanced analytics

---

## COMMON PITFALLS & SOLUTIONS

### Pitfall 1: Card Grid Styling Doesn't Match
**Problem**: CSS port loses hover effects or responsive behavior
**Solution**: 
- Test CSS at each breakpoint (320px, 768px, 1440px, 1800px)
- Verify grid auto-fit behavior
- Check image aspect ratio preservation

### Pitfall 2: Article Data Lost During Migration
**Problem**: Some articles don't appear after migration
**Solution**:
- Export full posts.json before starting
- Create audit script to verify counts
- Compare article titles before/after

### Pitfall 3: RSS Feed Integration Breaks
**Problem**: posts.json not updating automatically
**Solution**:
- Test feed URLs independently first
- Verify Ceviche automation triggers
- Check error logs in automation_logs/

### Pitfall 4: Navigation Links Broken
**Problem**: Menu items point to old domain
**Solution**:
- Update baseURL in Ceviche config
- Test all external links (Substack, LinkTree)
- Verify /about/ path works

### Pitfall 5: Deployment Fails to Hostinger
**Problem**: SFTP upload fails after build
**Solution**:
- Verify SSH key permissions (600)
- Test SSH connection manually first
- Update deploy.py for new build output path

---

## QUICK CHECKLIST

```
PRE-MIGRATION
[ ] Backup entire /cogitating-ceviche directory
[ ] Export posts.json (save to safe location)
[ ] Document current Hostinger credentials
[ ] List all custom styles not in grid-styles.css
[ ] Note any special content processing rules

DURING MIGRATION
[ ] Copy CSS files first
[ ] Test each breakpoint
[ ] Copy/import 200+ articles
[ ] Verify article order (newest first)
[ ] Port RSS feed logic
[ ] Test automated ingestion
[ ] Verify navigation works
[ ] Test deployment script

POST-MIGRATION
[ ] Check homepage renders correctly
[ ] Verify responsive design works
[ ] Test all menu links
[ ] Wait 6 hours, check posts.json updated
[ ] Monitor Hostinger deployment
[ ] Review error logs
[ ] Performance testing
```

---

## REFERENCE: Ceviche Engine Integration Points

### Data Layer
```
Ceviche loads posts.json from:
/data/posts.json (or configured path)

Generation timing:
- Build-time: Pre-render cards during site build
- OR Runtime: Fetch posts.json during request

Recommended: Build-time for better SEO
```

### Automation Layer
```
Ceviche automation triggers:
- RSS feed ingestion (configure schedule)
- posts.json generation
- Site rebuild
- Auto-deploy

Current schedule:
- Ingestion: Every 6 hours
- Deploy: 8 AM & 8 PM daily
```

### Deployment Layer
```
Ceviche build output → deploy.py (SFTP) → Hostinger

Update paths:
/public/         → /build/ or /dist/
/public_html/    → Keep same remote path
```

---

## Support Files

- **Full Analysis**: `CEVICHE_MIGRATION_ANALYSIS.md` (25KB)
- **Current Architecture**: All details documented
- **Code Examples**: Reusable functions marked in analysis
- **Data Export**: See posts.json in public/data/

---

**Last Updated**: 2025-11-10  
**Next Steps**: Start Phase 1 (Assets) when ready
