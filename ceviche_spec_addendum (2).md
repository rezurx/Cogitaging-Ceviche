# Appendix: Ceviche Engine Technical Specification v1.2.1 Addendum

**Purpose:**  
This addendum refines implementation priorities for the main *Technical Specification v1.2* of the Ceviche Engine. It is intended to guide development in Claude Code (2.x) and VS Code environments.

---

## 1. Phase 1 Clarifications (Semantic Amplifier)

The Phase 1 implementation plan in v1.2 remains **authoritative**. The following clarifications ensure the build is lightweight, maintainable, and GitHub-compatible.

### 1.1 Image Handling
- Do **not** download or locally optimize Substack images in Phase 1.  
- Use existing remote URLs for `<img>` and `og:image` references.  
- Local image mirroring can be added later if performance requires it (Phase 3+).

### 1.2 Logging
- Do **not** commit log files to the GitHub repository.  
- For local debugging, use `logging` to output to `./.logs/ceviche.log` and include that directory in `.gitignore`.  
- GitHub Actions captures logs automatically; use its output for debugging.

### 1.3 RSS Caching (Optional)
- Optional feature for developer convenience.  
- Add an `rss_cache.json` file under `/data/` to support offline testing or RSS outage recovery.  
- Cache format: array of normalized article dictionaries identical to post-ingest output.

### 1.4 Monetization Metadata (Optional)
- Monetization-related metadata (affiliate links, CTA URLs) **may** be included in `/static/api/posts.json`, but should remain empty placeholders until later integration.

Example structure:
```json
{
  "slug": "the-cult-of-the-aesthetic-kitchen",
  "title": "The Cult of the Aesthetic Kitchen",
  "is_conrad": true,
  "topics": ["aesthetics", "consumer culture"],
  "cta_subscribe_url": "https://thecogitatingceviche.substack.com",
  "affiliate_links": []
}
```

### 1.5 Testing
- Once core scripts (`ingest_substack.py`, `build_articles.py`, `build_schema.py`) are stable, add unit tests using `pytest` for:
  - RSS ingestion validation
  - Front matter field integrity
  - JSON-LD schema validation

---

## 2. Integration Notes for Claude Code (2.x)

### 2.1 Compatibility
Ensure local environment uses Python 3.11+ and that `requirements.txt` includes:
```
feedparser
requests
beautifulsoup4
python-frontmatter
python-dateutil
```

### 2.2 Implementation Order
Claude Code should execute development tasks in this order:

1. **Create core directory structure**:
   ```text
   ceviche_engine/
     config.py
     ingest_substack.py
     build_articles.py
     build_schema.py
     utils.py
     requirements.txt
   ```
2. **Implement `config.py`** with:
   - RSS feed URLs for Cogitating & Cybernetic Ceviche.
   - `PRIMARY_AUTHOR_NAMES` for Conrad Hannon.
3. **Implement `ingest_substack.py`**:
   - Parse feeds using `feedparser`.
   - Normalize article data (title, author, date, link, topics, etc.).
   - Optional: cache output to `/data/rss_cache.json`.
4. **Implement `build_articles.py`**:
   - Create Hugo-compatible Markdown files under `/content/articles/<slug>/index.md`.
   - Include front matter with `is_conrad`, `topics`, canonical link, and Substack CTA.
5. **Implement `build_schema.py`**:
   - Generate per-article and global JSON-LD schemas.
   - Validate JSON before commit.
6. **Test locally** using `hugo serve` and validate with [Google’s Rich Results Test](https://search.google.com/test/rich-results).
7. **Only after local validation**, enable the GitHub Action for automation.

---

## 3. Optional Enhancements (Future-Proofing)

| Enhancement | Purpose | When to Implement |
|--------------|----------|------------------|
| RSS cache | Offline resilience | Optional now |
| Monetization metadata | Future affiliate integration | Phase 3+ |
| Local image optimization | Faster page loads | Phase 4+ |
| Unit tests (pytest) | Reliability | Phase 2–3 |
| Persona-based enrichment | AI-driven content expansion | Phase 6 |

---

## 4. Summary

This addendum maintains full compatibility with the v1.2 specification but simplifies the implementation footprint for stability and maintainability.  
**Claude Code should use v1.2 as the canonical architecture and this addendum as a practical execution guide.**

Next operational task: implement **Phase 1 (Semantic Amplifier)** using these streamlined guidelines, test locally, and confirm schema validation before enabling automation.

