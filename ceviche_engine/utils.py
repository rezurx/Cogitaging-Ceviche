#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ceviche Engine Utilities
Helper functions for content processing, normalization, and I/O
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dateutil import parser as date_parser
from html import unescape
from bs4 import BeautifulSoup

# ============================================================================
# Logging Setup
# ============================================================================

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
    logging.info(f"Logging initialized: {log_file}")

# ============================================================================
# Text Processing
# ============================================================================

def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug.

    Example:
        "The Cult of the Aesthetic Kitchen" � "the-cult-of-the-aesthetic-kitchen"
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove non-word chars
    text = re.sub(r'[-\s]+', '-', text)    # Replace spaces/dashes with single dash
    return text.strip('-')

def strip_html_to_text(html: str) -> str:
    """
    Strip HTML tags and return clean text.
    Cannibalized from existing ingest_substack.py
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return unescape(text)

def remove_banned_content(text: str, banned_line_patterns: List[str], banned_inline_patterns: List[str]) -> str:
    """
    Remove banned patterns from text.
    Cannibalized from existing ingest_substack.py
    """
    if not text:
        return ""

    # Remove banned lines
    lines = text.split('\n')
    filtered_lines = []

    for line in lines:
        line_lower = line.lower().strip()
        banned = False

        for pattern in banned_line_patterns:
            if re.match(pattern, line_lower, re.IGNORECASE):
                banned = True
                break

        if not banned:
            filtered_lines.append(line)

    text = '\n'.join(filtered_lines)

    # Remove banned inline patterns
    for pattern in banned_inline_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()

# Banned content patterns (from existing script)
BANNED_LINE_PATTERNS = [
    r"^image created with generative ai$",
    r"^share$",
    r"^subscribe$",
    r"^voice[- ]?over provided by notebooklm$",
    r"^discussion by notebooklm$",
    r"^voice[- ]?over provided by amazon polly$",
    r"^also, check out eleven labs.*$",
    r"^the cogitating cevich[e�].*reader[- ]supported publication.*$",
    r"^the cybernetic cevich[e�].*reader[- ]supported publication.*$",
    r"^to receive new posts and support my work.*$",
    r"^consider becoming a free or paid subscriber.*$",
]

BANNED_INLINE_PATTERNS = [
    r"image created with generative ai",
    r"\bsubscribe\b",
    r"\bshare\b",
    r"voice[- ]?over provided by notebooklm",
    r"discussion by notebooklm",
    r"voice[- ]?over provided by amazon polly",
    r"\beleven labs\b",
    r"reader[- ]supported publication",
    r"to receive new posts and support my work",
    r"consider becoming a free or paid subscriber",
]

def generate_excerpt(text: str, length: int = 250) -> str:
    """Generate excerpt from text, cleaned and truncated"""
    # Strip HTML
    clean_text = strip_html_to_text(text)

    # Remove banned content
    clean_text = remove_banned_content(clean_text, BANNED_LINE_PATTERNS, BANNED_INLINE_PATTERNS)

    # Truncate to length
    if len(clean_text) <= length:
        return clean_text

    # Truncate at word boundary
    truncated = clean_text[:length].rsplit(' ', 1)[0]
    return truncated + "..."

# ============================================================================
# Author Normalization
# ============================================================================

def normalize_author(author_name: str, primary_names: List[str]) -> tuple[str, bool]:
    """
    Normalize author name and detect if it's Conrad.

    Args:
        author_name: Raw author name from RSS feed
        primary_names: List of Conrad T. Hannon name variations

    Returns:
        tuple: (canonical_name, is_conrad)

    Example:
        normalize_author("Conrad Hannon", PRIMARY_AUTHOR_NAMES)
        � ("Conrad T. Hannon", True)
    """
    if not author_name:
        return ("Unknown", False)

    # Clean up author name
    author_clean = author_name.strip()

    # Check if it's Conrad (case-insensitive)
    for primary in primary_names:
        if author_clean.lower() == primary.lower():
            return (primary_names[0], True)  # Return first (canonical) name

    return (author_clean, False)

# ============================================================================
# Date Handling
# ============================================================================

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime object.
    Handles various RSS date formats.
    """
    if not date_str:
        return None

    try:
        return date_parser.parse(date_str)
    except Exception as e:
        logging.error(f"Failed to parse date: {date_str} - {e}")
        return None

def format_date_iso(dt: datetime) -> str:
    """Format datetime to ISO 8601 string"""
    if not dt:
        return datetime.now().isoformat()
    return dt.isoformat()

def format_date_display(dt: datetime) -> str:
    """Format datetime for display (e.g., "November 10, 2025")"""
    if not dt:
        return ""
    return dt.strftime("%B %d, %Y")

# ============================================================================
# Topic Extraction
# ============================================================================

def extract_topics_from_tags(tags: list) -> List[str]:
    """
    Extract and normalize topics from feed tags.

    Args:
        tags: List of tag dictionaries or strings from RSS feed

    Returns:
        List of normalized topic slugs
    """
    if not tags:
        return []

    topics = []
    for tag in tags:
        if isinstance(tag, dict):
            term = tag.get('term', '')
        else:
            term = str(tag)

        if term:
            # Slugify and add
            topic_slug = slugify(term)
            if topic_slug and topic_slug not in topics:
                topics.append(topic_slug)

    return topics

# ============================================================================
# File I/O
# ============================================================================

def safe_write_json(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Safely write JSON to file with error handling.

    Args:
        file_path: Path to JSON file
        data: Data to serialize
        indent: JSON indentation

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        logging.debug(f"Wrote JSON to {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to write JSON to {file_path}: {e}")
        return False

def safe_read_json(file_path: str, default: Any = None) -> Any:
    """
    Safely read JSON from file.

    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.debug(f"JSON file not found: {file_path}")
        return default
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {file_path}: {e}")
        return default
    except Exception as e:
        logging.error(f"Failed to read JSON from {file_path}: {e}")
        return default

# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    # Test utilities
    print("Testing Ceviche Engine Utilities")
    print("=" * 60)

    # Test slugify
    assert slugify("The Cult of the Aesthetic Kitchen") == "the-cult-of-the-aesthetic-kitchen"
    print(" slugify works")

    # Test author normalization
    from config import PRIMARY_AUTHOR_NAMES
    name, is_conrad = normalize_author("Conrad Hannon", PRIMARY_AUTHOR_NAMES)
    assert is_conrad == True
    assert name == "Conrad T. Hannon"
    print(" Author normalization works")

    # Test date parsing
    date = parse_date("2025-11-10T10:30:00Z")
    assert date is not None
    print(" Date parsing works")

    # Test excerpt generation
    html_content = "<p>This is <strong>test</strong> content with <em>HTML</em> tags.</p>"
    excerpt = generate_excerpt(html_content, length=20)
    assert "test" in excerpt
    assert "<" not in excerpt  # No HTML tags
    print(" Excerpt generation works")

    # Test topic extraction
    tags = [{"term": "Technology"}, {"term": "Culture"}]
    topics = extract_topics_from_tags(tags)
    assert "technology" in topics
    assert "culture" in topics
    print(" Topic extraction works")

    print("=" * 60)
    print("All utility tests passed ")
