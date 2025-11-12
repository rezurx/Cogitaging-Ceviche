# Rollback Instructions - Cogitating Ceviche
## How to Restore the Site Before Ceviche Engine Migration

**Created:** 2025-11-10
**Backup Location:** `/home/resurx/websites/cogitating-ceviche-pre-ceviche-engine-backup-20251110-221800.tar.gz`
**Git Tag:** `pre-ceviche-engine`

---

## If Something Goes Wrong

### Quick Rollback (Git Tag Method)

```bash
cd ~/websites/cogitating-ceviche

# Stash any uncommitted changes
git stash

# Reset to pre-migration state
git reset --hard pre-ceviche-engine

# Force push to GitHub (CAUTION: This overwrites remote)
git push origin main --force

# Rebuild and deploy
hugo --gc --minify
# Then deploy to hosting
```

**Time to rollback:** ~2 minutes

---

### Full Restore (Backup Archive Method)

If git tag doesn't work or repo is corrupted:

```bash
# Move current directory out of the way
cd ~/websites
mv cogitating-ceviche cogitating-ceviche-broken

# Extract backup
tar -xzf cogitating-ceviche-pre-ceviche-engine-backup-20251110-221800.tar.gz

# Verify contents
cd cogitating-ceviche
ls -la

# Rebuild Hugo site
hugo --gc --minify

# Test locally
hugo serve
# Visit http://localhost:1313

# If good, deploy to hosting
```

**Time to restore:** ~5 minutes

---

## What's Preserved in the Backup

✅ All Hugo source files (content/, layouts/, static/)
✅ Configuration (hugo.toml, automation_config.yaml)
✅ Existing automation scripts (automation_manager.py, scripts/)
✅ CSS and styling (static/css/, grid-styles.css)
✅ Images and assets (static/images/)
✅ Data files (data/posts.json if present)
✅ Documentation and guides
✅ Cloudflare worker configuration

**NOT included (excluded for size):**
- .git directory (use git tag instead)
- node_modules (reinstall if needed)
- .venv, subagent-env (virtual environments - reinstall)
- public/ (rebuilt directory - regenerate with `hugo`)

---

## Verification Steps After Rollback

### 1. Check Git Status
```bash
git status
git log --oneline -5
# Should show commits from before migration
```

### 2. Test Hugo Build
```bash
hugo --gc --minify
# Should build without errors
```

### 3. Test Local Server
```bash
hugo serve
# Visit http://localhost:1313
# Verify homepage card grid displays
# Check article links work
```

### 4. Verify Homepage Grid
- Open http://localhost:1313
- Should see 30 articles in card grid
- Cards should be responsive (test at different widths)
- Hover effects should work
- Images should load
- Links should go to Substack

### 5. Check Data Integrity
```bash
# If posts.json exists in public/data/
cat public/data/posts.json | jq '.items | length'
# Should show 200+ articles

# Check first article
cat public/data/posts.json | jq '.items[0]'
# Should show article data
```

---

## Common Issues and Fixes

### Issue: "Hugo command not found"

**Solution:**
```bash
# Reinstall Hugo
sudo snap install hugo --channel=extended
```

### Issue: "Module not found" errors in Python scripts

**Solution:**
```bash
# Recreate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: Homepage shows no articles

**Solution:**
```bash
# Regenerate posts.json
cd scripts
python3 ingest_substack.py

# Check if created
ls -lh ../public/data/posts.json
```

### Issue: Git push rejected

**Solution:**
```bash
# Force push (CAUTION: overwrites remote)
git push origin main --force

# Or create new branch
git checkout -b rollback-$(date +%Y%m%d)
git push origin rollback-$(date +%Y%m%d)
```

---

## Files Locations

**Backup Archive:**
- Path: `/home/resurx/websites/cogitating-ceviche-pre-ceviche-engine-backup-20251110-221800.tar.gz`
- Size: ~9.1 MB
- Contains: Complete site source (excluding .git, node_modules, venvs, public/)

**Git Tag:**
- Name: `pre-ceviche-engine`
- Date: 2025-11-10
- Location: In git repository
- View: `git show pre-ceviche-engine`

**Migration Analysis Documents:**
- MIGRATION_README.md
- CEVICHE_MIGRATION_ANALYSIS.md
- MIGRATION_QUICK_REFERENCE.md
- MIGRATION_SUMMARY.txt

---

## Testing Rollback (Dry Run)

Before you need it, test the rollback procedure:

```bash
# Create test directory
mkdir -p ~/test-rollback
cd ~/test-rollback

# Extract backup
tar -xzf ~/websites/cogitating-ceviche-pre-ceviche-engine-backup-20251110-221800.tar.gz

# Verify structure
ls -la cogitating-ceviche/

# Test Hugo build
cd cogitating-ceviche
hugo --gc --minify

# Clean up
cd ~
rm -rf ~/test-rollback
```

**Expected result:** Hugo builds successfully, no errors

---

## Emergency Contact Information

If rollback fails or you need help:

1. **Check migration analysis documents** (detailed diagnostics)
2. **Check automation logs**: `cat automation_logs/automation.log`
3. **Check Hugo logs**: `cat hugo.log`
4. **Git history**: `git log --oneline --graph -20`

---

## Prevention: Before Making Changes

Always before modifying the site:

```bash
# 1. Ensure git is clean
git status

# 2. Commit any changes
git add .
git commit -m "Pre-migration checkpoint"

# 3. Create a branch
git checkout -b ceviche-engine-migration

# 4. Work on branch, not main
# ... make changes ...

# 5. Test thoroughly before merging to main
```

---

## Success Criteria for Rollback

After rollback, the site should:
- ✅ Build with Hugo without errors
- ✅ Display homepage with card grid
- ✅ Show 200+ articles
- ✅ Links work to Substack
- ✅ Images load correctly
- ✅ Responsive at all breakpoints
- ✅ Automation scripts run without errors

If all checked, rollback was successful.

---

**Keep this file for reference. Do not delete the backup archive until Ceviche Engine is stable in production for at least 30 days.**
