# Cogitating Ceviche Engine  
### Technical Specification v1.2 (Consolidated Full Version)

---

## 0. Purpose and Context

This document defines the plan to **upgrade the existing `cogitating-ceviche.com` Hugo site** into a semantic, search-optimized hub for:

- **The Cogitating Ceviche** (Substack A)  
- **The Cybernetic Ceviche** (Substack B)  
- **Author entity:** Conrad T. Hannon (primary focus)

It is intended for:
- **Design & planning** by a reasoning model (e.g., ChatGPT)
- **Implementation** by **Claude Code 2.x** in VS Code

Core goals:

1. Increase **programmatic visibility** (SEO + knowledge graph + AI citation), not social-media marketing.
2. Make `cogitating-ceviche.com` the **canonical semantic hub** for Conrad’s work, even though the full text lives on Substack.
3. Build an architecture that can later be **reused** for:
   - The Elephant Island Chronicles
   - The Human Factors Brief

This spec includes near-term implementable Phases 1–6 in detail and long-term Phases 7–13 at an architectural level.

---

## 1. Current State Summary

**Site:** `https://cogitating-ceviche.com/`  
**Hosting:** GitHub Pages + Hugo static site

Key characteristics:
- Front page uses a JS card grid from `/data/posts.json`.
- Cards link directly to Substack posts.
- No per-article pages on-site.
- No structured schema beyond meta tags.
- Built with Hugo and minimal automation scripts.

---

## 2. Target Architecture (High-Level)

Turn the site into a **semantic hub** powered by a Python content engine, `Ceviche Engine`, responsible for ingesting Substack feeds, generating Hugo content and schema, and maintaining structured JSON APIs.

**Major Components:**
1. `Ceviche Engine (Python)` — handles ingest, content generation, schema, and enrichment.
2. `Hugo Site (Front-End)` — renders structured content and schema.
3. `Automation` — via GitHub Actions or local scripts; future VPS optional.

---

## 3. Phased Roadmap

### Phase 1 – Semantic Amplifier (Core Upgrade)

Create per-article Hugo pages with canonical links and JSON-LD schema for `Article`, `Person`, and `WebSite` types.

Key tasks:
- Add `/ceviche_engine/` folder with modular Python scripts:
  - `ingest_substack.py`
  - `build_articles.py`
  - `build_schema.py`
  - `utils.py`
- Ingest Substack RSS feeds (Cogitating + Cybernetic)
- Generate per-article Markdown under `content/articles/<slug>/index.md`
- Build global and per-article schema partials.
- Add GitHub Action to auto-run 1–2x/day.

---

### Phase 2 – Knowledge Mirror & AEO (Answer Engine Optimization)

Add automated **Q&A extraction** to improve search/AEO.

- Use LLM (Anthropic Haiku preferred) for 3–5 concise Q&A pairs per article.
- Generate static JSON files under `static/api/`.
- Add `FAQPage` JSON-LD for articles with Q&A.

---

### Phases 3–6 (Later Implementation)

**Phase 3 – Echo Chamber:** Draft social snippets (no auto-posting).  
**Phase 4 – Authority Reactor:** SEO/link opportunity reports.  
**Phase 5 – Cogitation Index:** Client-side search (Fuse.js/Lunr).  
**Phase 6 – Synthetic Persona Network:** Future persona simulation framework (architecture only).

---

## 4. Long-Term Aspirational Phases (7–13)

Future extensions include knowledge graph relationships, multi-author network (Ceviche Commons), AI alignment of essays with real-world events, multimodal outputs, tokenized reputation tracking, conversational assistant, and long-term decentralized archiving (IPFS/Arweave).

---

## 5. Implementation Stack

- **Python 3.11+**
- **Hugo** static site generator
- **GitHub Actions** for automation
- **Anthropic API** for Q&A (later)
- **Feedparser, BeautifulSoup, Requests** for parsing
- **Optional:** spaCy or similar NLP libs (future)

---

## 6. Repo Structure

```text
cogitating-ceviche/
├── config.toml
├── content/
│   ├── about/
│   ├── articles/<slug>/index.md
│   ├── authors/conrad-t-hannon/index.md
│   ├── echoes/
│   └── reports/
├── layouts/
│   ├── articles/single.html
│   └── partials/schema.html
├── static/api/
│   ├── posts.json
│   ├── posts/<slug>.json
│   └── topics/<topic>.json
├── ceviche_engine/
│   ├── ingest_substack.py
│   ├── build_articles.py
│   ├── build_schema.py
│   ├── build_qa.py
│   ├── utils.py
│   └── config.py
└── .github/workflows/update_site.yml
```

---

## 7. GitHub Actions Plan

**Workflow:** `update_site.yml`  
Triggers: manual or scheduled (`0 */12 * * *`)

Steps:
1. Checkout repo
2. Setup Python
3. Run `ingest_substack.py`, `build_articles.py`, `build_schema.py`
4. Run `build_qa.py` if configured
5. Commit and push changes only if content updated

---

## 8. Error Handling & Rollback

- Log all errors; skip failed items, don’t crash pipeline.
- RSS or API failure → skip and retry next run.
- Validate JSON-LD with Rich Results Test.
- Test locally before PR to `main`.

---

## 9. Phase 1 Implementation Order

1. **`ingest_substack.py`** → Parse and normalize RSS feeds.
2. **`build_articles.py`** → Generate Hugo article content.
3. **`build_schema.py`** → Add schema.
4. **`update_site.yml`** → GitHub Action skeleton.

Each must work independently before combining.

---

## 10. Phase 2 Implementation Guidelines

- Use content hashing to avoid redundant LLM calls.
- Cache Q&A under `data/qa/<slug>.json`.
- Generate `FAQPage` schema inline.
- Skip gracefully if no API key.
- Keep cost under $2/month.

---

## 11. Author-Aware System (v1.2 Integration)

### 11.1 Multi-Author Handling

Not all articles are by Conrad. The engine must correctly reflect authorship while still prioritizing Conrad’s content.

**Ingest Rules:**
```python
author_name: str
author_slug: str
is_conrad: bool
```
Determined via `PRIMARY_AUTHOR_NAMES` in config.

### 11.2 Front Matter Updates

Add:
```yaml
author: "Conrad T. Hannon"
author_slug: "conrad-t-hannon"
is_conrad: true
```
Hugo templates should show author name and optionally a badge for Conrad.

### 11.3 JSON-LD Author Attribution

- Use actual author in `Article` schema.
- If `is_conrad == true`, include full `Person` object with canonical author page URL.
- If not, use minimal author object.

### 11.4 Global Person Schema

Keep a global `Person` node for Conrad:
```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Conrad T. Hannon",
  "url": "https://cogitating-ceviche.com/authors/conrad-t-hannon/",
  "worksFor": {"@type": "Organization", "name": "The Cogitating Ceviche"}
}
```

### 11.5 Conrad-Centric Bias

- Always run enrichment (Q&A, topics) on Conrad’s articles first.
- Include `is_conrad` in all API data.
- Rank Conrad’s work higher in internal search and metadata.
- Create and maintain an author page under `/authors/conrad-t-hannon/`.

### 11.6 LLM Provider Flexibility

LLM provider and model should come from config/env:
```python
QA_GENERATION_PROVIDER = "anthropic"  # default
QA_MODEL = "claude-haiku-20250514"
```
Swapping providers must not break pipeline.

### 11.7 Phase 1 Independence

Phase 1 must:
- NOT depend on Anthropic or `.env`.
- Use only lightweight dependencies.
- Generate schema and content purely from RSS.

Phase 2 adds LLM features modularly.

---

## 12. Success Criteria

### Phase 1
- RSS feeds parsed
- Articles generated with authors & schema
- Hugo renders successfully
- Schema validates
- Homepage grid preserved

### Phase 2
- Q&A generation works, cached & schema-valid
- API endpoints populate
- Pipeline stable under GitHub Actions

---

## 13. Final Principles

- **Incremental & reversible** development.
- **Truthful attribution**, **Conrad-focused promotion**.
- **Modular**, testable Python scripts.
- **No reliance** on continuous VPS until justified.
- **Extensible** for future reuse by Elephant Island and Human Factors Brief.

---

**End of Technical Specification v1.2 (Consolidated)**

