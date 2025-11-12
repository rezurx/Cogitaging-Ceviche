#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ceviche Engine Configuration
Central configuration for RSS feeds, paths, and site metadata
"""

import os
from pathlib import Path

# ============================================================================
# RSS Feed URLs
# ============================================================================

RSS_FEEDS = [
    "https://thecogitatingceviche.substack.com/feed",
    "https://thecyberneticceviche.substack.com/feed",
]

# ============================================================================
# Author Configuration
# ============================================================================

# Conrad T. Hannon name variations for author detection
PRIMARY_AUTHOR_NAMES = [
    "Conrad T. Hannon",      # Canonical name (first one is always used)
    "Conrad Hannon",
    "Conrad T Hannon",
    "C.T. Hannon",
    "CT Hannon",
    "Conrad Thomas Hannon",
]

# Default author metadata for Conrad
PRIMARY_AUTHOR_METADATA = {
    "name": "Conrad T. Hannon",
    "url": "https://cogitating-ceviche.com/about/",
    "email": "conrad@cogitating-ceviche.com",  # Update if needed
    "description": "Writer, researcher, and cognitive explorer",
}

# ============================================================================
# Hugo Site Paths
# ============================================================================

# Base directory (parent of ceviche_engine)
BASE_DIR = Path(__file__).parent.parent

# Hugo content directory
CONTENT_DIR = BASE_DIR / "content" / "posts"

# Hugo static data directory (for JSON-LD schemas)
SCHEMA_DIR = BASE_DIR / "static" / "schemas"

# Public data directory (for posts.json)
PUBLIC_DATA_DIR = BASE_DIR / "public" / "data"

# Logs directory
LOGS_DIR = BASE_DIR / "logs"

# Cache directory for RSS feeds
CACHE_DIR = BASE_DIR / ".cache"

# ============================================================================
# Site Metadata
# ============================================================================

SITE_URL = "https://cogitating-ceviche.com"
SITE_NAME = "Cogitating Ceviche"
SITE_DESCRIPTION = "Semantic amplifier for cognitive exploration, AI alignment, and cultural synthesis"
SITE_LOGO = f"{SITE_URL}/images/logo.png"  # Update if logo exists

# ============================================================================
# Ingestion Settings
# ============================================================================

# Maximum number of entries to fetch per feed (None = all)
MAX_ENTRIES_PER_FEED = None

# Retry settings for RSS fetching
RSS_RETRY_ATTEMPTS = 3
RSS_RETRY_DELAY = 2  # seconds
RSS_RETRY_BACKOFF = 2  # exponential backoff multiplier

# Request timeout (seconds)
RSS_TIMEOUT = 30

# User agent for RSS requests
USER_AGENT = "CevicheEngine/1.0 (+https://cogitating-ceviche.com)"

# ============================================================================
# Content Processing
# ============================================================================

# Excerpt length for post summaries
EXCERPT_LENGTH = 250

# Minimum content length to be considered valid (characters)
MIN_CONTENT_LENGTH = 100

# ============================================================================
# Schema.org Settings
# ============================================================================

# Schema types to generate
SCHEMA_TYPES = [
    "Article",
    "Person",
    "WebSite",
]

# Image fallback if article has no image
DEFAULT_ARTICLE_IMAGE = f"{SITE_URL}/images/default-article.png"

# ============================================================================
# Logging
# ============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = LOGS_DIR / "ceviche_engine.log"

# ============================================================================
# Create directories if they don't exist
# ============================================================================

def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in [CONTENT_DIR, SCHEMA_DIR, PUBLIC_DATA_DIR, LOGS_DIR, CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Validation
# ============================================================================

if __name__ == "__main__":
    print("Ceviche Engine Configuration")
    print("=" * 60)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Content Directory: {CONTENT_DIR}")
    print(f"Schema Directory: {SCHEMA_DIR}")
    print(f"Public Data Directory: {PUBLIC_DATA_DIR}")
    print(f"Logs Directory: {LOGS_DIR}")
    print(f"Cache Directory: {CACHE_DIR}")
    print()
    print(f"RSS Feeds: {len(RSS_FEEDS)}")
    for feed in RSS_FEEDS:
        print(f"  - {feed}")
    print()
    print(f"Primary Author: {PRIMARY_AUTHOR_NAMES[0]}")
    print(f"Name Variations: {len(PRIMARY_AUTHOR_NAMES)}")
    print()

    # Create directories
    ensure_directories()
    print("All directories created successfully")
