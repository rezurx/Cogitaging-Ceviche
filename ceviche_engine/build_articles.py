#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ceviche Engine - Article Builder
Generates Hugo markdown files and posts.json from processed RSS entries
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import frontmatter

# Import from our modules
from config import (
    CONTENT_DIR,
    PUBLIC_DATA_DIR,
    SITE_URL,
    ensure_directories,
)
from utils import strip_html_to_text, format_date_display

# ============================================================================
# Hugo Markdown Generation
# ============================================================================

def build_hugo_frontmatter(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build Hugo TOML front matter from processed entry.

    Args:
        entry: Processed entry dict from ingest_substack.py

    Returns:
        Front matter dict
    """
    # Determine source label
    if "cogitatingceviche" in entry['feed_source']:
        source = "Cogitating-Ceviche"
    elif "cyberneticceviche" in entry['feed_source']:
        source = "Cybernetic-Ceviche"
    else:
        source = "Unknown"

    # Build front matter
    front_matter = {
        "title": entry['title'],
        "date": entry['published_date'],
        "draft": False,
        "canonicalUrl": entry['url'],
        "source": source,
        "slug": entry['slug'],
        "author": entry['author'],
        "is_conrad": entry['is_conrad'],
    }

    # Add featured image if available
    if entry.get('image_url'):
        front_matter["featured_image"] = entry['image_url']

    # Add topics if available
    if entry.get('topics'):
        front_matter["tags"] = entry['topics']

    # Add excerpt
    if entry.get('excerpt'):
        front_matter["description"] = entry['excerpt']

    return front_matter

def generate_hugo_content(entry: Dict[str, Any]) -> str:
    """
    Generate full Hugo markdown content (front matter + body).

    Args:
        entry: Processed entry dict

    Returns:
        Full markdown content as string
    """
    # Get front matter
    fm = build_hugo_frontmatter(entry)

    # Build TOML front matter manually
    toml_lines = ["+++"]

    for key, value in fm.items():
        if isinstance(value, bool):
            toml_lines.append(f"{key} = {str(value).lower()}")
        elif isinstance(value, list):
            # Format array
            array_items = ', '.join([f'"{item}"' for item in value])
            toml_lines.append(f"{key} = [{array_items}]")
        elif isinstance(value, str):
            # Escape quotes in strings
            escaped_value = value.replace('"', '\\"')
            toml_lines.append(f'{key} = "{escaped_value}"')
        else:
            toml_lines.append(f'{key} = "{value}"')

    toml_lines.append("+++")

    # Convert HTML content to plain text (for now, we'll use the excerpt)
    # In a future phase, we might preserve HTML or convert to markdown
    body = entry.get('excerpt', '')

    # Add canonical link at bottom
    body += f"\n\n[Read the full article on Substack]({entry['url']})"

    # Combine front matter and body
    return "\n".join(toml_lines) + "\n\n" + body

def write_hugo_article(entry: Dict[str, Any], output_dir: Path) -> Path:
    """
    Write Hugo markdown file for an entry.

    Args:
        entry: Processed entry dict
        output_dir: Directory to write markdown file

    Returns:
        Path to written file
    """
    # Generate filename from slug
    filename = f"{entry['slug']}.md"
    file_path = output_dir / filename

    # Generate content
    content = generate_hugo_content(entry)

    # Write file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logging.debug(f"Wrote Hugo article: {file_path}")
    return file_path

# ============================================================================
# posts.json Generation (for Homepage Card Grid)
# ============================================================================

def build_posts_json_item(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a posts.json item from processed entry.

    Args:
        entry: Processed entry dict

    Returns:
        posts.json item dict
    """
    # Parse the title for subtitle (common format: "Title: Subtitle")
    title_parts = entry['title'].split(':', 1)
    if len(title_parts) == 2:
        title = title_parts[0].strip()
        subtitle = title_parts[1].strip()
    else:
        title = entry['title']
        subtitle = ""

    # Convert date to GMT format for consistency with existing posts.json
    try:
        dt = datetime.fromisoformat(entry['published_date'].replace('Z', '+00:00'))
        published_gmt = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    except:
        published_gmt = entry['published_date']

    item = {
        "title": title,
        "subtitle": subtitle,
        "url": entry['url'],
        "published": published_gmt,
        "image": entry.get('image_url', ''),
        "excerpt": entry.get('excerpt', ''),
        "source": "substack",
        "author": entry['author'],
        "is_conrad": entry['is_conrad'],
    }

    return item

def generate_posts_json(entries: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Generate posts.json file for homepage card grid.

    Args:
        entries: List of processed entries (already sorted by date)
        output_path: Path to write posts.json
    """
    # Build items
    items = [build_posts_json_item(entry) for entry in entries]

    # Build full JSON structure
    posts_json = {
        "generatedAt": datetime.now().isoformat(),
        "items": items,
    }

    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(posts_json, f, indent=2, ensure_ascii=False)

    logging.info(f"Generated posts.json with {len(items)} items at {output_path}")

# ============================================================================
# Main Build Function
# ============================================================================

def build_all_articles(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build all Hugo articles and posts.json from processed entries.

    Args:
        entries: List of processed entries from ingest_substack.py

    Returns:
        Build statistics dict
    """
    logging.info(f"Building articles for {len(entries)} entries")

    # Ensure directories exist
    ensure_directories()

    # Write Hugo markdown files
    hugo_files = []
    for entry in entries:
        try:
            file_path = write_hugo_article(entry, CONTENT_DIR)
            hugo_files.append(file_path)
        except Exception as e:
            logging.error(f"Failed to write Hugo article for {entry['title']}: {e}")

    # Generate posts.json
    posts_json_path = PUBLIC_DATA_DIR / "posts.json"
    try:
        generate_posts_json(entries, posts_json_path)
    except Exception as e:
        logging.error(f"Failed to generate posts.json: {e}")
        raise

    # Build stats
    stats = {
        "total_entries": len(entries),
        "hugo_files_created": len(hugo_files),
        "posts_json_created": posts_json_path.exists(),
        "posts_json_path": str(posts_json_path),
    }

    logging.info(f"Build complete: {stats['hugo_files_created']} Hugo files created")
    return stats

# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    from utils import setup_logging
    from config import LOGS_DIR
    from ingest_substack import ingest_all_feeds

    # Setup
    ensure_directories()
    setup_logging(LOGS_DIR / "build_test.log", logging.DEBUG)

    print("Testing Article Builder")
    print("=" * 60)

    # Ingest feeds
    print("Ingesting RSS feeds...")
    entries = ingest_all_feeds()
    print(f"Ingested {len(entries)} entries")
    print()

    # Build articles
    print("Building articles...")
    stats = build_all_articles(entries)

    print(f"\nBuild Statistics:")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Hugo Files Created: {stats['hugo_files_created']}")
    print(f"  posts.json Created: {stats['posts_json_created']}")
    print(f"  posts.json Path: {stats['posts_json_path']}")
    print()

    # Show sample Hugo file
    if stats['hugo_files_created'] > 0:
        sample_file = CONTENT_DIR / f"{entries[0]['slug']}.md"
        if sample_file.exists():
            print("Sample Hugo File:")
            print("-" * 60)
            with open(sample_file, 'r', encoding='utf-8') as f:
                print(f.read()[:500])
                print("...")
            print("-" * 60)

    print("=" * 60)
    print(f"Article builder test complete [OK]")
