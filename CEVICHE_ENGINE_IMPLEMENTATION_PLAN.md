# Ceviche Engine Implementation Plan
## Phase 1: Semantic Amplifier - Detailed Execution Plan

**Project:** Cogitating Ceviche
**Date:** 2025-11-10
**Claude Code Version:** 2.x
**Integration:** Continuum v2.0 + CC-Subagents v2.0

---

## Executive Summary

This document provides a detailed, step-by-step implementation plan for **Phase 1 of the Ceviche Engine**, transforming cogitating-ceviche.com into a semantic hub for Conrad T. Hannon's work.

### What We're Building

A Python-based content pipeline that:
1. Ingests RSS feeds from 2 Substack publications
2. Generates per-article Hugo pages with semantic markup
3. Creates JSON-LD schema for SEO/AEO
4. Maintains structured JSON APIs
5. Automates via GitHub Actions

### Success Criteria

✅ RSS feeds parsed successfully
✅ Per-article pages generated with proper front matter
✅ Author attribution (multi-author with Conrad prioritization)
✅ JSON-LD schema validates (Google Rich Results Test)
✅ Existing homepage grid preserved
✅ GitHub Actions automation working
✅ Local testing successful with `hugo serve`

---

## CC-Subagents Analysis Results

### Project Characteristics

- **Type:** General Application (Python + Hugo static site)
- **Languages:** Python, Shell, TOML
- **Frameworks:** GitHub Actions
- **Complexity:** 3/10 (low-medium)
- **Architecture:** Static site generator with Python pipeline

### Recommended Specialized Agents

1. **Python Specialist** (haiku) - Primary implementation agent
   - RSS parsing, data normalization
   - Hugo content generation
   - Schema building

2. **Code Reviewer** (sonnet, auto-invoke) - Quality assurance
   - Code review after each module
   - Bug detection
   - Best practices validation

3. **Test Runner** (haiku, auto-invoke) - Testing
   - Unit test execution
   - Pytest coverage analysis
   - CI/CD integration

4. **Documentation Generator** (haiku) - Documentation
   - README updates
   - Inline documentation
   - API documentation

---

## Implementation Strategy

### Approach

**Modular, Test-Driven, Incremental**

1. Build each script independently
2. Test locally before integration
3. Commit after each working module
4. Use Continuum to track progress across sessions
5. Launch Task tool agents for complex operations

### Development Environment

```bash
# Project directory
cd ~/websites/cogitating-ceviche

# Virtual environment
source .venv/bin/activate

# Hugo for local testing
hugo serve

# Continuum for session tracking
# (Server should be running on :8000)
```

---

## Phase 1 Implementation Steps

### Step 1: Project Setup & Directory Structure

**Duration:** 15 minutes

**Actions:**

```bash
# Create ceviche_engine directory
mkdir -p ceviche_engine
cd ceviche_engine

# Create Python files
touch __init__.py
touch config.py
touch ingest_substack.py
touch build_articles.py
touch build_schema.py
touch utils.py

# Create requirements.txt
cat > requirements.txt <<EOF
feedparser>=6.0.10
requests>=2.31.0
beautifulsoup4>=4.12.0
python-frontmatter>=1.0.0
python-dateutil>=2.8.2
EOF

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p ../content/articles
mkdir -p ../content/authors
mkdir -p ../static/api/posts
mkdir -p ../data
mkdir -p ../.logs

# Update .gitignore
echo ".logs/" >> ../.gitignore
echo "data/rss_cache.json" >> ../.gitignore
```

**Deliverables:**
- ✅ Directory structure created
- ✅ Dependencies installed
- ✅ .gitignore updated

**Continuum Sync:**
```python
from continuum_cc2_client import ContinuumCC2Client
client = ContinuumCC2Client()
client.set_phase("Phase 1: Semantic Amplifier - Setup")
client.sync_todos([{
    "content": "Create Ceviche Engine directory structure",
    "activeForm": "Creating directory structure",
    "status": "completed"
}])
```

---

### Step 2: Implement config.py

**Duration:** 10 minutes

**Requirements:**
- RSS feed URLs for both Substacks
- Primary author detection (Conrad T. Hannon)
- Site configuration

**Implementation:**

```python
# ceviche_engine/config.py

import os
from typing import List

# RSS Feeds
RSS_FEEDS = [
    {
        "url": "https://thecogitatingceviche.substack.com/feed",
        "name": "The Cogitating Ceviche",
        "publication_slug": "cogitating-ceviche"
    },
    {
        "url": "https://thecyberneticceviche.substack.com/feed",
        "name": "The Cybernetic Ceviche",
        "publication_slug": "cybernetic-ceviche"
    }
]

# Author Configuration
PRIMARY_AUTHOR_NAMES = [
    "Conrad T. Hannon",
    "Conrad Hannon",
    "Conrad T Hannon",
    "C.T. Hannon",
    "CT Hannon"
]

PRIMARY_AUTHOR_SLUG = "conrad-t-hannon"
PRIMARY_AUTHOR_CANONICAL = "Conrad T. Hannon"

# Site Configuration
SITE_URL = "https://cogitating-ceviche.com"
SITE_NAME = "Cogitating Ceviche"

# Content Paths
CONTENT_DIR = "../content"
ARTICLES_DIR = f"{CONTENT_DIR}/articles"
AUTHORS_DIR = f"{CONTENT_DIR}/authors"
STATIC_API_DIR = "../static/api"
DATA_DIR = "../data"

# Optional: RSS Cache for offline testing
RSS_CACHE_ENABLED = os.getenv("RSS_CACHE_ENABLED", "false").lower() == "true"
RSS_CACHE_FILE = f"{DATA_DIR}/rss_cache.json"

# Logging
LOG_DIR = "../.logs"
LOG_FILE = f"{LOG_DIR}/ceviche.log"
```

**Test:**
```python
# Test config import
from ceviche_engine import config
print(f"Primary Author: {config.PRIMARY_AUTHOR_CANONICAL}")
print(f"RSS Feeds: {len(config.RSS_FEEDS)}")
```

**Continuum Sync:**
```python
client.log("Implemented config.py with RSS feeds and author configuration", "implementation")
```

---

### Step 3: Implement utils.py

**Duration:** 15 minutes

**Requirements:**
- Slugification
- Author normalization
- Date parsing
- File I/O helpers

**Implementation:**

```python
# ceviche_engine/utils.py

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dateutil import parser as date_parser

# Setup logging
def setup_logging(log_file: str, level=logging.INFO):
    """Configure logging to file and console"""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def normalize_author(author_name: str, primary_names: list) -> tuple[str, bool]:
    """
    Normalize author name and detect if it's Conrad.

    Returns:
        tuple: (canonical_name, is_conrad)
    """
    if not author_name:
        return ("Unknown", False)

    # Clean up author name
    author_clean = author_name.strip()

    # Check if it's Conrad
    for primary in primary_names:
        if author_clean.lower() == primary.lower():
            return (primary, True)

    return (author_clean, False)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    try:
        return date_parser.parse(date_str)
    except Exception as e:
        logging.error(f"Failed to parse date: {date_str} - {e}")
        return None

def safe_write_json(file_path: str, data: Any, indent: int = 2):
    """Safely write JSON to file with error handling"""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        logging.info(f"Wrote JSON to {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to write JSON to {file_path}: {e}")
        return False

def safe_read_json(file_path: str, default: Any = None) -> Any:
    """Safely read JSON from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"JSON file not found: {file_path}")
        return default
    except Exception as e:
        logging.error(f"Failed to read JSON from {file_path}: {e}")
        return default

def extract_topics_from_tags(tags: list) -> list:
    """Extract and normalize topics from feed tags"""
    if not tags:
        return []

    topics = []
    for tag in tags:
        if isinstance(tag, dict):
            term = tag.get('term', '')
        else:
            term = str(tag)

        if term:
            topics.append(slugify(term))

    return list(set(topics))  # Deduplicate
```

**Test:**
```python
# Test utils
from ceviche_engine import utils, config

# Test slugify
assert utils.slugify("The Cult of the Aesthetic Kitchen") == "the-cult-of-the-aesthetic-kitchen"

# Test author normalization
name, is_conrad = utils.normalize_author("Conrad T. Hannon", config.PRIMARY_AUTHOR_NAMES)
assert is_conrad == True
assert name == "Conrad T. Hannon"

# Test date parsing
date = utils.parse_date("2025-11-10T10:30:00Z")
assert date is not None
```

**Continuum Sync:**
```python
client.log("Implemented utils.py with helper functions", "implementation")
```

---

### Step 4: Implement ingest_substack.py

**Duration:** 30 minutes

**Requirements:**
- Parse RSS feeds from both Substacks
- Normalize article data
- Detect author and topics
- Optional: Cache for offline testing

**Implementation:**

```python
# ceviche_engine/ingest_substack.py

import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime

from . import config
from . import utils

def fetch_rss_feed(feed_url: str) -> Optional[feedparser.FeedParserDict]:
    """Fetch and parse RSS feed"""
    try:
        logging.info(f"Fetching RSS feed: {feed_url}")
        feed = feedparser.parse(feed_url)

        if feed.bozo:
            logging.warning(f"RSS feed parse warning for {feed_url}: {feed.bozo_exception}")

        return feed
    except Exception as e:
        logging.error(f"Failed to fetch RSS feed {feed_url}: {e}")
        return None

def normalize_article(entry: feedparser.FeedParserDict, publication: Dict) -> Dict:
    """
    Normalize RSS entry to standard article format.

    Returns article dict with:
    - slug, title, author, author_slug, is_conrad
    - publication, canonical_link, date_published
    - description, image, topics
    """
    # Extract basic fields
    title = entry.get('title', 'Untitled')
    slug = utils.slugify(title)
    canonical_link = entry.get('link', '')
    description = entry.get('summary', '')[:300]  # First 300 chars

    # Parse date
    date_str = entry.get('published', '')
    date_obj = utils.parse_date(date_str)
    date_published = date_obj.isoformat() if date_obj else datetime.now().isoformat()

    # Extract author
    author_raw = entry.get('author', 'Unknown')
    author_name, is_conrad = utils.normalize_author(author_raw, config.PRIMARY_AUTHOR_NAMES)
    author_slug = utils.slugify(author_name)

    # Extract image (Substack usually has og:image in content)
    image = ""
    if 'media_content' in entry:
        image = entry.media_content[0].get('url', '')
    elif 'enclosures' in entry and entry.enclosures:
        image = entry.enclosures[0].get('href', '')

    # Extract topics from tags
    tags = entry.get('tags', [])
    topics = utils.extract_topics_from_tags(tags)

    return {
        "slug": slug,
        "title": title,
        "author": author_name,
        "author_slug": author_slug,
        "is_conrad": is_conrad,
        "publication": publication['name'],
        "publication_slug": publication['publication_slug'],
        "canonical_link": canonical_link,
        "date_published": date_published,
        "description": description,
        "image": image,
        "topics": topics
    }

def ingest_all_feeds() -> List[Dict]:
    """
    Ingest all RSS feeds and return normalized articles.

    Returns:
        List of article dicts
    """
    all_articles = []

    for feed_config in config.RSS_FEEDS:
        feed = fetch_rss_feed(feed_config['url'])

        if not feed or not feed.entries:
            logging.warning(f"No entries found for {feed_config['name']}")
            continue

        logging.info(f"Processing {len(feed.entries)} entries from {feed_config['name']}")

        for entry in feed.entries:
            try:
                article = normalize_article(entry, feed_config)
                all_articles.append(article)
                logging.debug(f"Normalized: {article['slug']} by {article['author']}")
            except Exception as e:
                logging.error(f"Failed to normalize entry {entry.get('title', 'unknown')}: {e}")
                continue

    # Sort by date (most recent first)
    all_articles.sort(key=lambda x: x['date_published'], reverse=True)

    # Prioritize Conrad's articles
    conrad_articles = [a for a in all_articles if a['is_conrad']]
    other_articles = [a for a in all_articles if not a['is_conrad']]

    logging.info(f"Ingested {len(all_articles)} articles total")
    logging.info(f"  Conrad's articles: {len(conrad_articles)}")
    logging.info(f"  Other authors: {len(other_articles)}")

    # Optional: Cache for offline testing
    if config.RSS_CACHE_ENABLED:
        utils.safe_write_json(config.RSS_CACHE_FILE, all_articles)
        logging.info(f"Cached articles to {config.RSS_CACHE_FILE}")

    return all_articles

def load_from_cache() -> List[Dict]:
    """Load articles from cache (for offline testing)"""
    articles = utils.safe_read_json(config.RSS_CACHE_FILE, default=[])
    logging.info(f"Loaded {len(articles)} articles from cache")
    return articles

if __name__ == "__main__":
    # Setup logging
    utils.setup_logging(config.LOG_FILE)

    # Test ingestion
    articles = ingest_all_feeds()
    print(f"Ingested {len(articles)} articles")

    if articles:
        print(f"\nFirst article:")
        print(f"  Title: {articles[0]['title']}")
        print(f"  Author: {articles[0]['author']}")
        print(f"  Is Conrad: {articles[0]['is_conrad']}")
        print(f"  Topics: {articles[0]['topics']}")
```

**Test:**
```bash
# Test RSS ingestion
cd ceviche_engine
python -m ingest_substack
```

**Expected Output:**
```
2025-11-10 ... - INFO - Fetching RSS feed: https://thecogitatingceviche.substack.com/feed
2025-11-10 ... - INFO - Processing 50 entries from The Cogitating Ceviche
...
Ingested 100 articles
First article:
  Title: Recent Article Title
  Author: Conrad T. Hannon
  Is Conrad: True
  Topics: ['technology', 'society']
```

**Continuum Sync:**
```python
client.log("Implemented ingest_substack.py with RSS parsing", "implementation")
client.add_task("Implement build_articles.py")
```

---

### Step 5: Implement build_articles.py

**Duration:** 45 minutes

**Requirements:**
- Generate Hugo markdown files under `content/articles/<slug>/index.md`
- Include complete front matter
- Add article summary with CTA to Substack
- Maintain `/static/api/posts.json` and per-article JSON

**Implementation:**

```python
# ceviche_engine/build_articles.py

import logging
from pathlib import Path
from typing import List, Dict
import frontmatter

from . import config
from . import utils
from . import ingest_substack

ARTICLE_TEMPLATE = """
Read the full article on [{publication}]({canonical_link}).

**Subscribe:** [Subscribe to {publication}]({subscribe_url})

---

*This is a reference page for "{title}" originally published on {publication}. The full content is available at the canonical link above.*
"""

def build_front_matter(article: Dict) -> Dict:
    """Build Hugo front matter for article"""
    return {
        "title": article['title'],
        "date": article['date_published'],
        "author": article['author'],
        "author_slug": article['author_slug'],
        "is_conrad": article['is_conrad'],
        "topics": article['topics'],
        "canonical_link": article['canonical_link'],
        "description": article['description'],
        "image": article['image'],
        "publication": article['publication'],
        "publication_slug": article['publication_slug'],
        "type": "article",
        "layout": "single"
    }

def build_article_content(article: Dict) -> str:
    """Build article body with CTA"""
    subscribe_url = f"https://{article['publication_slug']}.substack.com"

    return ARTICLE_TEMPLATE.format(
        publication=article['publication'],
        canonical_link=article['canonical_link'],
        subscribe_url=subscribe_url,
        title=article['title']
    ).strip()

def write_article_file(article: Dict) -> bool:
    """Write article to Hugo content directory"""
    try:
        # Create article directory
        article_dir = Path(config.ARTICLES_DIR) / article['slug']
        article_dir.mkdir(parents=True, exist_ok=True)

        # Build article file
        article_path = article_dir / "index.md"

        # Create frontmatter post
        post = frontmatter.Post(
            content=build_article_content(article),
            **build_front_matter(article)
        )

        # Write to file
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        logging.info(f"Wrote article: {article['slug']}")
        return True

    except Exception as e:
        logging.error(f"Failed to write article {article['slug']}: {e}")
        return False

def build_api_json(articles: List[Dict]):
    """Build JSON API files"""
    # Global posts.json
    posts_json = [
        {
            "slug": a['slug'],
            "title": a['title'],
            "author": a['author'],
            "author_slug": a['author_slug'],
            "is_conrad": a['is_conrad'],
            "topics": a['topics'],
            "canonical_link": a['canonical_link'],
            "description": a['description'],
            "image": a['image'],
            "date_published": a['date_published'],
            "publication": a['publication']
        }
        for a in articles
    ]

    utils.safe_write_json(
        f"{config.STATIC_API_DIR}/posts.json",
        posts_json
    )

    # Per-article JSON
    for article in articles:
        utils.safe_write_json(
            f"{config.STATIC_API_DIR}/posts/{article['slug']}.json",
            article
        )

    logging.info(f"Built API JSON for {len(articles)} articles")

def build_all_articles(articles: List[Dict]) -> tuple[int, int]:
    """
    Build all article files and API JSON.

    Returns:
        tuple: (success_count, failure_count)
    """
    success = 0
    failure = 0

    for article in articles:
        if write_article_file(article):
            success += 1
        else:
            failure += 1

    build_api_json(articles)

    logging.info(f"Built {success} articles successfully, {failure} failures")
    return (success, failure)

if __name__ == "__main__":
    # Setup logging
    utils.setup_logging(config.LOG_FILE)

    # Ingest articles
    articles = ingest_substack.ingest_all_feeds()

    # Build articles
    success, failure = build_all_articles(articles)

    print(f"\nBuild complete:")
    print(f"  Success: {success}")
    print(f"  Failure: {failure}")
```

**Test:**
```bash
# Test article building
cd ceviche_engine
python -m build_articles

# Check output
ls -la ../content/articles/ | head -20
cat ../content/articles/*/index.md | head -50
cat ../static/api/posts.json | head -20
```

**Continuum Sync:**
```python
client.log("Implemented build_articles.py - generates Hugo content and API JSON", "implementation")
client.add_task("Implement build_schema.py")
```

---

### Step 6: Implement build_schema.py

**Duration:** 30 minutes

**Requirements:**
- Generate JSON-LD schema for Article, Person, WebSite types
- Per-article schema
- Global schema for Conrad and site

**Implementation:**

```python
# ceviche_engine/build_schema.py

import logging
from typing import Dict, List
from pathlib import Path

from . import config
from . import utils

def build_person_schema(author_name: str, author_slug: str) -> Dict:
    """Build Person schema"""
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": author_name,
        "url": f"{config.SITE_URL}/authors/{author_slug}/"
    }

def build_conrad_person_schema() -> Dict:
    """Build full Person schema for Conrad"""
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": config.PRIMARY_AUTHOR_CANONICAL,
        "url": f"{config.SITE_URL}/authors/{config.PRIMARY_AUTHOR_SLUG}/",
        "worksFor": {
            "@type": "Organization",
            "name": "The Cogitating Ceviche"
        }
    }

def build_website_schema() -> Dict:
    """Build WebSite schema"""
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": config.SITE_NAME,
        "url": config.SITE_URL
    }

def build_article_schema(article: Dict) -> Dict:
    """Build Article schema for specific article"""
    # Author schema
    if article['is_conrad']:
        author_schema = {
            "@type": "Person",
            "name": article['author'],
            "url": f"{config.SITE_URL}/authors/{article['author_slug']}/"
        }
    else:
        author_schema = {
            "@type": "Person",
            "name": article['author']
        }

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article['title'],
        "author": author_schema,
        "datePublished": article['date_published'],
        "dateModified": article['date_published'],
        "url": f"{config.SITE_URL}/articles/{article['slug']}/",
        "mainEntityOfPage": f"{config.SITE_URL}/articles/{article['slug']}/",
        "description": article['description']
    }

    # Add image if available
    if article.get('image'):
        schema['image'] = article['image']

    # Add publisher
    schema['publisher'] = {
        "@type": "Organization",
        "name": config.SITE_NAME,
        "url": config.SITE_URL
    }

    return schema

def write_article_schema(article: Dict) -> bool:
    """Write article schema to file"""
    try:
        schema = build_article_schema(article)

        # Write to data directory for Hugo to access
        schema_path = Path(f"../data/schema/articles/{article['slug']}.json")
        schema_path.parent.mkdir(parents=True, exist_ok=True)

        utils.safe_write_json(str(schema_path), schema)
        return True

    except Exception as e:
        logging.error(f"Failed to write schema for {article['slug']}: {e}")
        return False

def build_global_schemas():
    """Build global schemas (Person, WebSite)"""
    # Conrad's Person schema
    conrad_schema = build_conrad_person_schema()
    utils.safe_write_json("../data/schema/conrad_person.json", conrad_schema)

    # WebSite schema
    website_schema = build_website_schema()
    utils.safe_write_json("../data/schema/website.json", website_schema)

    logging.info("Built global schemas")

def build_all_schemas(articles: List[Dict]) -> tuple[int, int]:
    """
    Build all schema files.

    Returns:
        tuple: (success_count, failure_count)
    """
    success = 0
    failure = 0

    for article in articles:
        if write_article_schema(article):
            success += 1
        else:
            failure += 1

    build_global_schemas()

    logging.info(f"Built {success} article schemas, {failure} failures")
    return (success, failure)

if __name__ == "__main__":
    # Setup logging
    utils.setup_logging(config.LOG_FILE)

    # Import articles
    from . import ingest_substack
    articles = ingest_substack.ingest_all_feeds()

    # Build schemas
    success, failure = build_all_schemas(articles)

    print(f"\nSchema build complete:")
    print(f"  Success: {success}")
    print(f"  Failure: {failure}")
```

**Test:**
```bash
# Test schema generation
cd ceviche_engine
python -m build_schema

# Check output
ls -la ../data/schema/articles/ | head -10
cat ../data/schema/conrad_person.json
cat ../data/schema/website.json
```

**Continuum Sync:**
```python
client.log("Implemented build_schema.py - generates JSON-LD schemas", "implementation")
client.add_task("Create GitHub Actions workflow")
```

---

### Step 7: Create Main Pipeline Script

**Duration:** 15 minutes

**Requirements:**
- Single entry point to run all steps
- Error handling
- Logging

**Implementation:**

```python
# ceviche_engine/run_pipeline.py

import logging
import sys

from . import config
from . import utils
from . import ingest_substack
from . import build_articles
from . import build_schema

def run_full_pipeline():
    """Run the complete Ceviche Engine pipeline"""
    try:
        # Setup logging
        utils.setup_logging(config.LOG_FILE)
        logging.info("=" * 60)
        logging.info("Ceviche Engine Pipeline - Starting")
        logging.info("=" * 60)

        # Step 1: Ingest RSS feeds
        logging.info("Step 1: Ingesting RSS feeds...")
        articles = ingest_substack.ingest_all_feeds()

        if not articles:
            logging.error("No articles ingested. Exiting.")
            return False

        # Step 2: Build articles
        logging.info("Step 2: Building Hugo articles...")
        article_success, article_failure = build_articles.build_all_articles(articles)

        # Step 3: Build schemas
        logging.info("Step 3: Building JSON-LD schemas...")
        schema_success, schema_failure = build_schema.build_all_schemas(articles)

        # Summary
        logging.info("=" * 60)
        logging.info("Ceviche Engine Pipeline - Complete")
        logging.info("=" * 60)
        logging.info(f"Total articles: {len(articles)}")
        logging.info(f"Articles built: {article_success}")
        logging.info(f"Schemas built: {schema_success}")
        logging.info(f"Failures: articles={article_failure}, schemas={schema_failure}")

        return True

    except Exception as e:
        logging.error(f"Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_full_pipeline()
    sys.exit(0 if success else 1)
```

**Test:**
```bash
# Run full pipeline
cd ceviche_engine
python -m run_pipeline

# Check Hugo site
cd ..
hugo serve
# Open http://localhost:1313
```

---

### Step 8: Create GitHub Actions Workflow

**Duration:** 20 minutes

**Requirements:**
- Automated execution 1-2x per day
- Commit only if content changed
- Proper error handling

**Implementation:**

```yaml
# .github/workflows/update_site.yml

name: Update Ceviche Site

on:
  schedule:
    # Run every 12 hours
    - cron: '0 */12 * * *'
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd ceviche_engine
          pip install -r requirements.txt

      - name: Run Ceviche Engine
        run: |
          cd ceviche_engine
          python -m run_pipeline

      - name: Check for changes
        id: git-check
        run: |
          git diff --exit-code || echo "changes=true" >> $GITHUB_OUTPUT

      - name: Commit and push if changed
        if: steps.git-check.outputs.changes == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add content/ static/api/ data/schema/
          git commit -m "🤖 Update content from Ceviche Engine"
          git push

      - name: Deploy Hugo site
        if: steps.git-check.outputs.changes == 'true'
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build Hugo
        if: steps.git-check.outputs.changes == 'true'
        run: hugo --minify

      - name: Deploy to GitHub Pages
        if: steps.git-check.outputs.changes == 'true'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

**Test:**
```bash
# Test workflow locally with act (if installed)
act -j update

# Or test manually:
cd ceviche_engine
python -m run_pipeline
cd ..
git status  # Should show changes
```

---

### Step 9: Hugo Template Updates

**Duration:** 20 minutes

**Requirements:**
- Update article single template to include schema
- Show author attribution
- Preserve existing homepage

**Implementation:**

```html
<!-- layouts/articles/single.html -->

{{ define "main" }}
<article class="article">
  <header>
    <h1>{{ .Title }}</h1>

    <div class="article-meta">
      <span class="author">
        By
        {{ if .Params.is_conrad }}
          <strong><a href="/authors/{{ .Params.author_slug }}/">{{ .Params.author }}</a></strong>
        {{ else }}
          {{ .Params.author }}
        {{ end }}
      </span>

      <span class="date">
        {{ .Date.Format "January 2, 2006" }}
      </span>

      {{ if .Params.topics }}
      <div class="topics">
        {{ range .Params.topics }}
          <span class="topic">{{ . }}</span>
        {{ end }}
      </div>
      {{ end }}
    </div>
  </header>

  <div class="article-content">
    {{ .Content }}
  </div>

  <!-- Schema.org JSON-LD -->
  {{ partial "schema.html" . }}
</article>
{{ end }}
```

```html
<!-- layouts/partials/schema.html -->

{{ $schemaFile := printf "schema/articles/%s.json" .Params.slug }}
{{ if fileExists (printf "data/%s" $schemaFile) }}
<script type="application/ld+json">
{{ readFile (printf "data/%s" $schemaFile) | safeJS }}
</script>
{{ end }}

<!-- Global schemas -->
{{ if eq .IsHome true }}
<script type="application/ld+json">
{{ readFile "data/schema/website.json" | safeJS }}
</script>
<script type="application/ld+json">
{{ readFile "data/schema/conrad_person.json" | safeJS }}
</script>
{{ end }}
```

---

### Step 10: Testing & Validation

**Duration:** 30 minutes

**Checklist:**

1. **Local Hugo Build**
   ```bash
   hugo serve
   # Visit http://localhost:1313
   # Check article pages: /articles/slug/
   # Verify homepage still works
   ```

2. **Schema Validation**
   - Open article page
   - View source, find JSON-LD
   - Copy schema
   - Test at: https://search.google.com/test/rich-results
   - Should validate as Article type

3. **API Endpoints**
   ```bash
   # Check API files exist
   cat static/api/posts.json | jq '.[0]'
   cat static/api/posts/slug.json
   ```

4. **Author Attribution**
   - Verify Conrad's articles show "by Conrad T. Hannon"
   - Verify other authors show correctly
   - Check `is_conrad` flag in JSON

5. **Front Matter**
   ```bash
   # Check article front matter
   head -30 content/articles/slug/index.md
   # Verify all required fields present
   ```

**Continuum Sync:**
```python
client.log("Completed Phase 1 implementation and testing", "completion")
client.set_phase("Phase 1: Complete - Ready for Production")
```

---

## Post-Implementation

### Commit Strategy

```bash
# Commit structure
git add ceviche_engine/
git commit -m "feat: Add Ceviche Engine Phase 1 - Semantic Amplifier"

git add content/articles/
git commit -m "content: Generate per-article pages with schema"

git add .github/workflows/
git commit -m "ci: Add automated content update workflow"
```

### Monitoring

After deployment:
1. Check GitHub Actions runs successfully
2. Verify new articles appear within 12 hours
3. Monitor Google Search Console for schema warnings
4. Check site performance with Lighthouse

### Continuum Session Summary

```python
# End of session summary
stats = client.get_stats()
print(f"Session Summary:")
print(f"  Phase: {stats['current_phase']}")
print(f"  Todos completed: {stats['todos']['completed']}")
print(f"  Implementation time: ~4 hours")
```

---

## Success Metrics

✅ **Phase 1 Complete When:**
- [ ] All 10 implementation steps finished
- [ ] Local Hugo build works (`hugo serve`)
- [ ] Schema validates (Google Rich Results Test)
- [ ] API JSON files generated
- [ ] GitHub Actions runs successfully
- [ ] New articles auto-ingested within 12 hours
- [ ] Existing homepage grid preserved
- [ ] Conrad's authorship correctly attributed

---

## Next Steps (Phase 2)

After Phase 1 is stable:

1. Add Anthropic API key to GitHub Secrets
2. Implement `build_qa.py` for Q&A extraction
3. Add FAQPage schema
4. Test LLM cost (<$2/month target)
5. Monitor AEO improvements

---

## Appendix: Quick Reference Commands

```bash
# Activate environment
cd ~/websites/cogitating-ceviche
source .venv/bin/activate

# Run pipeline locally
cd ceviche_engine
python -m run_pipeline

# Test Hugo site
cd ..
hugo serve

# Check logs
tail -f .logs/ceviche.log

# Validate schema
# Copy from http://localhost:1313/articles/slug/
# Paste to https://search.google.com/test/rich-results

# Commit changes
git add ceviche_engine/ content/ static/
git commit -m "feat: Phase 1 implementation"
git push

# Monitor GitHub Actions
# https://github.com/USERNAME/cogitating-ceviche/actions
```

---

**End of Implementation Plan**

Use this plan with:
- **Continuum v2.0** for session tracking
- **CC-Subagents v2.0 Task tool** for autonomous agent execution
- **TodoWrite** for task persistence across sessions

This modular, test-driven approach ensures Phase 1 is stable before moving to Phase 2.
