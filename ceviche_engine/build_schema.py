#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ceviche Engine - JSON-LD Schema Builder
Generates Schema.org structured data for semantic amplification
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import from our modules
from config import (
    SCHEMA_DIR,
    SITE_URL,
    SITE_NAME,
    SITE_DESCRIPTION,
    SITE_LOGO,
    PRIMARY_AUTHOR_METADATA,
    DEFAULT_ARTICLE_IMAGE,
    ensure_directories,
)
from utils import format_date_iso, slugify

# ============================================================================
# Person Schema (Conrad T. Hannon)
# ============================================================================

def build_person_schema() -> Dict[str, Any]:
    """
    Build Schema.org Person schema for Conrad T. Hannon.

    Returns:
        Person schema dict
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": f"{SITE_URL}/about/#person",
        "name": PRIMARY_AUTHOR_METADATA["name"],
        "url": PRIMARY_AUTHOR_METADATA["url"],
        "description": PRIMARY_AUTHOR_METADATA["description"],
        "sameAs": [
            f"{SITE_URL}/about/",
        ],
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{SITE_URL}/about/"
        },
    }

    # Add email if available
    if PRIMARY_AUTHOR_METADATA.get("email"):
        schema["email"] = PRIMARY_AUTHOR_METADATA["email"]

    return schema

# ============================================================================
# WebSite Schema
# ============================================================================

def build_website_schema() -> Dict[str, Any]:
    """
    Build Schema.org WebSite schema for cogitating-ceviche.com.

    Returns:
        WebSite schema dict
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": SITE_URL,
        "name": SITE_NAME,
        "description": SITE_DESCRIPTION,
        "publisher": {
            "@type": "Person",
            "@id": f"{SITE_URL}/about/#person"
        },
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{SITE_URL}/search?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        }
    }

    return schema

# ============================================================================
# Article Schema
# ============================================================================

def build_article_schema(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build Schema.org Article schema for a single entry.

    Args:
        entry: Processed entry dict from ingest_substack.py

    Returns:
        Article schema dict
    """
    # Determine article URL (on our site)
    article_url = f"{SITE_URL}/posts/{entry['slug']}/"

    # Build basic article schema
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": article_url,
        "headline": entry['title'],
        "url": article_url,
        "datePublished": entry['published_date'],
        "dateModified": entry['published_date'],  # Use published date as modified for now
        "description": entry.get('excerpt', ''),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": article_url
        },
    }

    # Add image (required for Article schema)
    if entry.get('image_url'):
        schema["image"] = {
            "@type": "ImageObject",
            "url": entry['image_url'],
            "width": 1456,  # Substack standard
            "height": 1456,
        }
    else:
        schema["image"] = {
            "@type": "ImageObject",
            "url": DEFAULT_ARTICLE_IMAGE,
        }

    # Add author
    if entry['is_conrad']:
        # Link to Conrad's Person schema
        schema["author"] = {
            "@type": "Person",
            "@id": f"{SITE_URL}/about/#person",
            "name": entry['author']
        }
    else:
        # Guest author - simple Person object
        schema["author"] = {
            "@type": "Person",
            "name": entry['author']
        }

    # Add publisher (always Conrad's site)
    schema["publisher"] = {
        "@type": "Person",
        "@id": f"{SITE_URL}/about/#person",
        "name": PRIMARY_AUTHOR_METADATA["name"],
        "url": PRIMARY_AUTHOR_METADATA["url"]
    }

    # Add keywords if topics available
    if entry.get('topics'):
        schema["keywords"] = ", ".join(entry['topics'])

    # Add word count estimate (very rough - 5 words per sentence, 200 words per minute read time)
    if entry.get('content_html'):
        word_count = len(entry['content_html'].split()) // 5  # Rough estimate
        schema["wordCount"] = word_count

    # Add canonical URL (back to Substack)
    schema["isBasedOn"] = {
        "@type": "CreativeWork",
        "url": entry['url']
    }

    return schema

# ============================================================================
# FAQPage Schema (Phase 2)
# ============================================================================

def build_faqpage_schema(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Build Schema.org FAQPage schema for articles with Q&A pairs.
    Phase 2 feature for Answer Engine Optimization.

    Args:
        entry: Processed entry dict with 'qna' field

    Returns:
        FAQPage schema dict or None if no Q&A
    """
    # Only generate if Q&A exists
    if not entry.get('qna') or len(entry.get('qna', [])) == 0:
        return None

    article_url = f"{SITE_URL}/posts/{entry['slug']}/"

    # Build FAQ schema
    main_entity = []
    for qa in entry['qna']:
        question_entity = {
            "@type": "Question",
            "name": qa['question'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": qa['answer']
            }
        }
        main_entity.append(question_entity)

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": f"{article_url}#faq",
        "url": article_url,
        "mainEntity": main_entity
    }

    return schema

# ============================================================================
# Schema File Writing
# ============================================================================

def write_schema_file(schema: Dict[str, Any], filename: str, output_dir: Path) -> Path:
    """
    Write a schema to a JSON file.

    Args:
        schema: Schema dict
        filename: Output filename (e.g., "person.json")
        output_dir: Directory to write file

    Returns:
        Path to written file
    """
    file_path = output_dir / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    logging.debug(f"Wrote schema to {file_path}")
    return file_path

# ============================================================================
# Main Schema Building Function
# ============================================================================

def build_all_schemas(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build all JSON-LD schemas from processed entries.

    Args:
        entries: List of processed entries from ingest_substack.py

    Returns:
        Build statistics dict
    """
    logging.info(f"Building schemas for {len(entries)} entries")

    # Ensure directories exist
    ensure_directories()

    # Build and write Person schema
    person_schema = build_person_schema()
    person_path = write_schema_file(person_schema, "person.json", SCHEMA_DIR)

    # Build and write WebSite schema
    website_schema = build_website_schema()
    website_path = write_schema_file(website_schema, "website.json", SCHEMA_DIR)

    # Build and write Article schemas
    article_files = []
    faqpage_files = []
    for entry in entries:
        try:
            article_schema = build_article_schema(entry)
            filename = f"article_{entry['slug']}.json"
            article_path = write_schema_file(article_schema, filename, SCHEMA_DIR)
            article_files.append(article_path)

            # Phase 2: Build FAQPage schema if Q&A exists
            faqpage_schema = build_faqpage_schema(entry)
            if faqpage_schema:
                faqpage_filename = f"faqpage_{entry['slug']}.json"
                faqpage_path = write_schema_file(faqpage_schema, faqpage_filename, SCHEMA_DIR)
                faqpage_files.append(faqpage_path)
                logging.info(f"Generated FAQPage schema for: {entry['title']}")

        except Exception as e:
            logging.error(f"Failed to build schema for {entry['title']}: {e}")

    # Build manifest of all schemas for easy loading
    manifest = {
        "generatedAt": datetime.now().isoformat(),
        "person_schema": "person.json",
        "website_schema": "website.json",
        "article_schemas": [f"article_{entry['slug']}.json" for entry in entries],
        "faqpage_schemas": [f"faqpage_{entry['slug']}.json" for entry in entries if entry.get('qna')],
        "total_articles": len(entries),
        "total_faqpages": len(faqpage_files),
    }

    manifest_path = write_schema_file(manifest, "manifest.json", SCHEMA_DIR)

    # Copy schemas to assets/ directory for Hugo resources.Get
    assets_schema_dir = Path("assets/schemas")
    assets_schema_dir.mkdir(parents=True, exist_ok=True)

    import shutil
    for schema_file in SCHEMA_DIR.glob("*.json"):
        shutil.copy2(schema_file, assets_schema_dir / schema_file.name)

    logging.info(f"Copied {len(list(SCHEMA_DIR.glob('*.json')))} schemas to assets/schemas/")

    # Build stats
    stats = {
        "total_entries": len(entries),
        "person_schema_created": person_path.exists(),
        "website_schema_created": website_path.exists(),
        "article_schemas_created": len(article_files),
        "manifest_created": manifest_path.exists(),
        "schema_dir": str(SCHEMA_DIR),
        "assets_schema_dir": str(assets_schema_dir),
    }

    logging.info(f"Schema build complete: {len(article_files)} article schemas created")
    return stats

# ============================================================================
# Schema Validation
# ============================================================================

def validate_schema(schema: Dict[str, Any]) -> bool:
    """
    Basic validation of schema structure.

    Args:
        schema: Schema dict

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["@context", "@type"]

    for field in required_fields:
        if field not in schema:
            logging.error(f"Schema missing required field: {field}")
            return False

    return True

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
    setup_logging(LOGS_DIR / "schema_test.log", logging.DEBUG)

    print("Testing Schema Builder")
    print("=" * 60)

    # Ingest feeds
    print("Ingesting RSS feeds...")
    entries = ingest_all_feeds()
    print(f"Ingested {len(entries)} entries")
    print()

    # Build schemas
    print("Building schemas...")
    stats = build_all_schemas(entries)

    print(f"\nSchema Build Statistics:")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Person Schema Created: {stats['person_schema_created']}")
    print(f"  WebSite Schema Created: {stats['website_schema_created']}")
    print(f"  Article Schemas Created: {stats['article_schemas_created']}")
    print(f"  Manifest Created: {stats['manifest_created']}")
    print(f"  Schema Directory: {stats['schema_dir']}")
    print()

    # Show sample schemas
    person_schema_path = SCHEMA_DIR / "person.json"
    if person_schema_path.exists():
        print("Sample Person Schema:")
        print("-" * 60)
        with open(person_schema_path, 'r', encoding='utf-8') as f:
            person_schema = json.load(f)
            print(json.dumps(person_schema, indent=2)[:400])
            print("...")
        print("-" * 60)
        print()

    # Validate a sample article schema
    if entries:
        sample_article_path = SCHEMA_DIR / f"article_{entries[0]['slug']}.json"
        if sample_article_path.exists():
            print(f"Sample Article Schema ({entries[0]['title'][:40]}...):")
            print("-" * 60)
            with open(sample_article_path, 'r', encoding='utf-8') as f:
                article_schema = json.load(f)
                print(json.dumps(article_schema, indent=2)[:600])
                print("...")
            print("-" * 60)
            print()

            # Validate
            is_valid = validate_schema(article_schema)
            print(f"Schema validation: {'[OK]' if is_valid else '[FAILED]'}")

    print("=" * 60)
    print(f"Schema builder test complete [OK]")
