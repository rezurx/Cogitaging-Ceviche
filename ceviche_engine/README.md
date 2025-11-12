# Ceviche Engine

**Semantic Amplification Pipeline for Cogitating Ceviche**

The Ceviche Engine is a Python-based content pipeline that transforms RSS feeds into semantically enriched Hugo content with full JSON-LD schema markup for AI discoverability.

## Overview

**Phase 1: Semantic Amplifier** (Current Implementation)

The Ceviche Engine automates the complete content workflow:

1. **RSS Ingestion** - Fetches and parses Substack feeds with author detection
2. **Hugo Content Generation** - Creates markdown files with TOML front matter
3. **JSON-LD Schema Generation** - Builds Schema.org structured data for Articles, Person, and WebSite
4. **Homepage Data** - Generates `posts.json` for the card grid

## Quick Start

### Requirements

- Python 3.12+
- Hugo Extended v0.147.9+
- Virtual environment (recommended)

### Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r ceviche_engine/requirements.txt
```

### Usage

```bash
# Run complete pipeline
python ceviche_engine/run_pipeline.py

# Dry run (validation only)
python ceviche_engine/run_pipeline.py --dry-run

# Debug mode
python ceviche_engine/run_pipeline.py --debug

# Build Hugo site
hugo

# Serve locally
hugo serve
```

## Architecture

```
ceviche_engine/
├── config.py              # Central configuration
├── utils.py               # Helper functions
├── ingest_substack.py     # RSS feed processing
├── build_articles.py      # Hugo markdown generation
├── build_schema.py        # JSON-LD schema generation
├── run_pipeline.py        # Main orchestrator
└── requirements.txt       # Python dependencies
```

## Configuration

Edit `config.py` to customize:

- RSS feed URLs
- Author detection patterns (Conrad T. Hannon variations)
- Site metadata (URL, name, description)
- Path configuration
- Retry settings

## Author Detection

The pipeline automatically detects Conrad T. Hannon across multiple name variations:

- Conrad T. Hannon (canonical)
- Conrad Hannon
- Conrad T Hannon
- C.T. Hannon
- CT Hannon
- Conrad Thomas Hannon

Each entry is tagged with `is_conrad` boolean for author-aware processing.

## Generated Content

### Hugo Markdown Files
Location: `content/posts/*.md`

```toml
+++
title = "Article Title"
date = "2025-11-11T07:00:00+00:00"
draft = false
canonicalUrl = "https://original-url.com"
source = "Cogitating-Ceviche"
slug = "article-slug"
author = "Conrad T. Hannon"
is_conrad = true
featured_image = "https://image-url.com"
description = "Article excerpt..."
+++

Article content...
```

### JSON-LD Schemas
Location: `static/schemas/`

- `person.json` - Conrad T. Hannon Person schema
- `website.json` - Site-wide WebSite schema
- `article_*.json` - Individual Article schemas
- `manifest.json` - Schema inventory

### Homepage Data
Location: `public/data/posts.json`

```json
{
  "generatedAt": "2025-11-11T20:29:49.717634",
  "items": [
    {
      "title": "Article Title",
      "subtitle": "Subtitle if present",
      "url": "https://substack-url.com",
      "published": "Tue, 11 Nov 2025 07:00:00 GMT",
      "image": "https://image-url.com",
      "excerpt": "Article preview...",
      "source": "substack",
      "author": "Conrad T. Hannon",
      "is_conrad": true
    }
  ]
}
```

## Automation

### GitHub Actions

The pipeline runs automatically via GitHub Actions:

- **Schedule:** Daily at 6 AM UTC (1 AM EST)
- **Manual:** Via workflow_dispatch
- **Push:** On changes to `ceviche_engine/`

Workflow file: `.github/workflows/ceviche-engine.yml`

### Pipeline Steps

1. Checkout repository
2. Setup Python 3.12 and install dependencies
3. Setup Hugo Extended
4. Run Ceviche Engine pipeline
5. Build Hugo site with `hugo --minify`
6. Commit and push changes (if any)
7. Deploy to GitHub Pages
8. Upload pipeline logs as artifacts

## Logging

Logs are written to `logs/` directory:

- `pipeline.log` - Main orchestrator logs
- `ingest_test.log` - RSS ingestion logs
- `build_test.log` - Article builder logs
- `schema_test.log` - Schema builder logs

## Testing

Each module includes standalone testing:

```bash
# Test individual modules
python ceviche_engine/utils.py
python ceviche_engine/ingest_substack.py
python ceviche_engine/build_articles.py
python ceviche_engine/build_schema.py

# Test complete pipeline
python ceviche_engine/run_pipeline.py --dry-run
```

## Performance

Typical pipeline execution:

- **RSS Ingestion:** 40 entries in ~2 seconds
- **Article Generation:** 40 Hugo files in <1 second
- **Schema Generation:** 40 article schemas + global schemas in <1 second
- **Total Pipeline:** ~2.5 seconds end-to-end
- **Hugo Build:** 96 pages in ~90ms

## Schema.org Types

### Person (Conrad T. Hannon)
- @type: Person
- @id: `https://cogitating-ceviche.com/about/#person`
- Properties: name, url, description, email, sameAs

### WebSite
- @type: WebSite
- @id: `https://cogitating-ceviche.com/#website`
- Properties: url, name, description, publisher, potentialAction (SearchAction)

### Article (per post)
- @type: Article
- @id: `https://cogitating-ceviche.com/posts/{slug}/`
- Properties: headline, url, datePublished, dateModified, description, image, author, publisher, keywords, wordCount, isBasedOn

## Validation

Validate schemas with Google Rich Results Test:

```bash
# Test individual schemas
https://search.google.com/test/rich-results?url=https://cogitating-ceviche.com/schemas/person.json
```

Or use the Schema.org validator:

```bash
https://validator.schema.org/
```

## Future Phases

This is Phase 1 of the Ceviche Engine. Future phases include:

- **Phase 2:** Q&A extraction from content
- **Phase 3:** FAQPage schema generation
- **Phase 4:** BreadcrumbList navigation
- **Phase 5:** Multi-publication aggregation
- **Phase 6:** LLM-powered content enhancement
- **Phase 7+:** Knowledge graphs, multi-author networks, AI alignment research

See `cogitating_ceviche_spec_v_1_2.md` for full specification.

## Troubleshooting

### RSS Feed 404 Errors
Check feed URLs in `config.py` - ensure they include "the" prefix:
```python
RSS_FEEDS = [
    "https://thecogitatingceviche.substack.com/feed",  # Note: "the" prefix
    "https://thecyberneticceviche.substack.com/feed",
]
```

### Encoding Errors
The pipeline uses UTF-8 encoding throughout. If you see encoding errors, check that:
- All Python files have `# -*- coding: utf-8 -*-` header
- String literals use proper escaping for special characters

### Virtual Environment Issues
If packages aren't found, ensure you've activated the venv:
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

## License

Part of the Cogitating Ceviche project. See repository LICENSE.

## Credits

**Conrad T. Hannon** - Primary author and architect

Generated with semantic precision and AI alignment in mind.
