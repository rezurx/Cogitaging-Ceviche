#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ceviche Engine - RSS Ingestion Module
Fetches and processes RSS feeds with author detection
Cannibalized from scripts/ingest_substack.py with enhancements
"""

import time
import logging
import random
import requests
import feedparser
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Import from our modules
from config import (
    RSS_FEEDS,
    PRIMARY_AUTHOR_NAMES,
    PRIMARY_AUTHOR_METADATA,
    RSS_RETRY_ATTEMPTS,
    RSS_RETRY_DELAY,
    RSS_RETRY_BACKOFF,
    RSS_TIMEOUT,
    USER_AGENT,
    MIN_CONTENT_LENGTH,
)
from utils import (
    parse_date,
    format_date_iso,
    normalize_author,
    generate_excerpt,
    extract_topics_from_tags,
    slugify,
)

# ============================================================================
# RSS Fetching (Cannibalized from scripts/ingest_substack.py)
# ============================================================================

# Multiple realistic User-Agent strings to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_browser_headers(url: str) -> Dict[str, str]:
    """
    Generate realistic browser headers for a given URL.

    Args:
        url: The URL being requested

    Returns:
        Dictionary of HTTP headers
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": base_url,
    }

def fetch_rss_with_retry(url: str) -> Optional[str]:
    """
    Enhanced RSS fetching with exponential backoff and comprehensive error handling.
    Uses session-based requests with realistic browser behavior.

    Returns:
        RSS feed XML as string, or None if all retries failed
    """
    # Create a session for cookie persistence
    session = requests.Session()

    for attempt in range(RSS_RETRY_ATTEMPTS):
        try:
            logging.info(f"Fetching {url} (attempt {attempt + 1}/{RSS_RETRY_ATTEMPTS})")

            # Add small random delay to mimic human behavior
            if attempt == 0:
                delay = random.uniform(0.5, 1.5)
            else:
                # Add jitter and exponential backoff for retries
                jitter = RSS_RETRY_DELAY * (attempt + 1) * RSS_RETRY_BACKOFF * (0.5 + random.random() * 0.5)
                delay = jitter

            logging.debug(f"Waiting {delay:.2f}s before request")
            time.sleep(delay)

            # Generate fresh headers for each attempt
            headers = get_browser_headers(url)

            # First attempt: Visit homepage to get cookies (only on first attempt for each URL)
            if attempt == 0:
                parsed = urlparse(url)
                home_url = f"{parsed.scheme}://{parsed.netloc}"
                try:
                    logging.debug(f"Pre-visiting homepage: {home_url}")
                    session.get(home_url, headers=headers, timeout=10)
                    time.sleep(random.uniform(0.3, 0.8))  # Brief pause between requests
                except Exception as e:
                    logging.debug(f"Homepage pre-visit failed (non-critical): {e}")

            # Now fetch the actual RSS feed
            resp = session.get(url, headers=headers, timeout=RSS_TIMEOUT)

            if resp.status_code == 200:
                logging.info(f"Successfully fetched {url}")
                return resp.text

            elif resp.status_code == 403:
                logging.warning(f"403 Forbidden for {url} (attempt {attempt + 1})")
                # On 403, try with different User-Agent on next iteration
                continue

            elif resp.status_code == 429:
                logging.warning(f"Rate limited on {url}, waiting longer")
                time.sleep(RSS_RETRY_DELAY * (attempt + 2) * 3)  # Longer wait for rate limits
                continue

            logging.warning(f"GET {url} returned {resp.status_code}")

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError as e:
            logging.warning(f"Connection error for {url}: {e}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request error for {url}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error fetching {url}: {e}")
        finally:
            # Small delay between all attempts
            if attempt < RSS_RETRY_ATTEMPTS - 1:
                time.sleep(random.uniform(1, 2))

    session.close()
    logging.error(f"Failed to fetch feed after {RSS_RETRY_ATTEMPTS} retries: {url}")
    return None

# ============================================================================
# Entry Processing with Author Detection
# ============================================================================

def extract_image_url(entry: Any, html_content: str) -> str:
    """
    Extract image URL from feed entry.

    Args:
        entry: feedparser entry object
        html_content: HTML content to search for images

    Returns:
        Image URL or empty string
    """
    import re

    # Try entry media content first
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']

    # Try entry enclosures
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if 'url' in enc and enc.get('type', '').startswith('image/'):
                return enc['url']

    # Search HTML content for images
    if html_content:
        patterns = [
            r'<img[^>]+src="([^"]+)"',  # Standard img tags
            r'src="([^"]*\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',  # Image extensions
            r'content="([^"]*\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',  # Meta content
        ]

        for pattern in patterns:
            match = re.search(pattern, html_content, re.I)
            if match:
                return match.group(1)

    return ""

def extract_author_from_entry(entry: Any) -> str:
    """
    Extract author name from feed entry.
    Tries multiple fields where author might be stored.

    Args:
        entry: feedparser entry object

    Returns:
        Author name or "Unknown"
    """
    # Try standard author field
    if hasattr(entry, 'author') and entry.author:
        return entry.author.strip()

    # Try author_detail
    if hasattr(entry, 'author_detail') and entry.author_detail:
        if 'name' in entry.author_detail:
            return entry.author_detail['name'].strip()

    # Try contributors
    if hasattr(entry, 'contributors') and entry.contributors:
        for contributor in entry.contributors:
            if 'name' in contributor:
                return contributor['name'].strip()

    # Try dc:creator (Dublin Core)
    if hasattr(entry, 'dc_creator') and entry.dc_creator:
        return entry.dc_creator.strip()

    return "Unknown"

def process_feed_entry(entry: Any, feed_url: str) -> Optional[Dict[str, Any]]:
    """
    Process a single RSS feed entry into structured data.

    Args:
        entry: feedparser entry object
        feed_url: Source feed URL for logging

    Returns:
        Processed entry dict or None if invalid
    """
    try:
        # Extract basic fields
        title = getattr(entry, 'title', '').strip() or 'Untitled'
        url = getattr(entry, 'link', '').strip()

        if not url:
            logging.warning(f"Skipping entry without URL: {title}")
            return None

        # Get HTML content (try content first, fallback to summary)
        html_content = ""
        if hasattr(entry, 'content') and entry.content:
            html_content = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary'):
            html_content = entry.summary

        if not html_content or len(html_content) < MIN_CONTENT_LENGTH:
            logging.warning(f"Skipping entry with insufficient content: {title}")
            return None

        # Extract author and detect if it's Conrad
        raw_author = extract_author_from_entry(entry)
        author_name, is_conrad = normalize_author(raw_author, PRIMARY_AUTHOR_NAMES)

        # Parse and format date
        raw_date = getattr(entry, 'published', getattr(entry, 'updated', ''))
        parsed_date = parse_date(raw_date)
        if not parsed_date:
            logging.warning(f"Could not parse date for: {title}")
            parsed_date = datetime.now()

        date_iso = format_date_iso(parsed_date)

        # Generate excerpt
        excerpt = generate_excerpt(html_content)
        if not excerpt:
            logging.warning(f"Could not generate excerpt for: {title}")
            excerpt = title  # Fallback to title

        # Extract topics from tags
        tags = getattr(entry, 'tags', [])
        topics = extract_topics_from_tags(tags)

        # Extract image
        image_url = extract_image_url(entry, html_content)

        # Generate slug from title
        slug = slugify(title)

        # Build structured entry
        processed_entry = {
            "title": title,
            "slug": slug,
            "url": url,
            "author": author_name,
            "is_conrad": is_conrad,
            "published_date": date_iso,
            "published_timestamp": parsed_date.timestamp(),
            "excerpt": excerpt,
            "content_html": html_content,
            "image_url": image_url,
            "topics": topics,
            "feed_source": feed_url,
        }

        # Add full author metadata if it's Conrad
        if is_conrad:
            processed_entry["author_metadata"] = PRIMARY_AUTHOR_METADATA
        else:
            processed_entry["author_metadata"] = {
                "name": author_name,
            }

        logging.debug(f"Processed entry: {title[:50]}... (author: {author_name}, is_conrad: {is_conrad})")
        return processed_entry

    except Exception as e:
        logging.error(f"Error processing feed entry: {e}")
        return None

# ============================================================================
# Main Ingestion Function
# ============================================================================

def ingest_all_feeds() -> List[Dict[str, Any]]:
    """
    Ingest all RSS feeds and return processed entries.

    Returns:
        List of processed entry dicts
    """
    all_entries = []

    logging.info(f"Starting ingestion of {len(RSS_FEEDS)} feeds")

    for feed_url in RSS_FEEDS:
        try:
            logging.info(f"Processing feed: {feed_url}")

            # Fetch RSS feed
            xml_text = fetch_rss_with_retry(feed_url)
            if not xml_text:
                logging.error(f"Failed to fetch feed: {feed_url}")
                continue

            # Parse feed
            feed = feedparser.parse(xml_text)

            if feed.bozo:
                logging.warning(f"Feed parsing had issues: {feed.bozo_exception}")

            if not hasattr(feed, 'entries') or not feed.entries:
                logging.warning(f"No entries found in feed: {feed_url}")
                continue

            logging.info(f"Found {len(feed.entries)} entries in {feed_url}")

            # Process each entry
            for entry in feed.entries:
                processed = process_feed_entry(entry, feed_url)
                if processed:
                    all_entries.append(processed)

        except Exception as e:
            logging.error(f"Error processing feed {feed_url}: {e}")

    logging.info(f"Ingestion complete: {len(all_entries)} total entries processed")

    # Sort by published date (newest first)
    all_entries.sort(key=lambda x: x['published_timestamp'], reverse=True)

    return all_entries

# ============================================================================
# Statistics
# ============================================================================

def get_ingestion_stats(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate statistics about ingested entries.

    Args:
        entries: List of processed entries

    Returns:
        Stats dict
    """
    total = len(entries)
    conrad_entries = [e for e in entries if e['is_conrad']]
    guest_entries = [e for e in entries if not e['is_conrad']]

    # Collect unique authors
    authors = set(e['author'] for e in entries)

    # Collect unique topics
    all_topics = set()
    for e in entries:
        all_topics.update(e['topics'])

    # Entries with images
    with_images = len([e for e in entries if e['image_url']])

    stats = {
        "total_entries": total,
        "conrad_entries": len(conrad_entries),
        "guest_entries": len(guest_entries),
        "unique_authors": len(authors),
        "authors": sorted(list(authors)),
        "unique_topics": len(all_topics),
        "topics": sorted(list(all_topics)),
        "entries_with_images": with_images,
        "image_percentage": round(with_images / total * 100, 1) if total > 0 else 0,
    }

    return stats

# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    from utils import setup_logging
    from config import LOGS_DIR, ensure_directories

    # Setup
    ensure_directories()
    setup_logging(LOGS_DIR / "ingest_test.log", logging.DEBUG)

    print("Testing RSS Ingestion")
    print("=" * 60)

    # Ingest feeds
    entries = ingest_all_feeds()

    # Show stats
    stats = get_ingestion_stats(entries)

    print(f"\nIngestion Statistics:")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Conrad Entries: {stats['conrad_entries']}")
    print(f"  Guest Entries: {stats['guest_entries']}")
    print(f"  Unique Authors: {stats['unique_authors']}")
    print(f"    Authors: {', '.join(stats['authors'])}")
    print(f"  Unique Topics: {stats['unique_topics']}")
    print(f"  Entries with Images: {stats['entries_with_images']} ({stats['image_percentage']}%)")
    print()

    # Show sample entries
    if entries:
        print(f"Sample Entries (first 3):")
        for i, entry in enumerate(entries[:3], 1):
            print(f"\n{i}. {entry['title'][:60]}...")
            print(f"   Author: {entry['author']} (is_conrad: {entry['is_conrad']})")
            print(f"   Date: {entry['published_date']}")
            print(f"   URL: {entry['url']}")
            print(f"   Topics: {', '.join(entry['topics'][:5])}")
            print(f"   Excerpt: {entry['excerpt'][:80]}...")

    print("=" * 60)
    print(f"Ingestion test complete [OK]")
