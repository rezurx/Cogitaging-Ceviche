#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ceviche Engine - Phase 2: Q&A and Topic Extraction
Generates semantic Q&A pairs and topic tags for Conrad's articles
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import os

# Import from our modules
from config import (
    QA_GENERATION_PROVIDER,
    QA_MODEL,
    ANTHROPIC_API_KEY,
    QA_MIN_QUESTIONS,
    QA_MAX_QUESTIONS,
    QA_TEMPERATURE,
    TOPIC_MIN_COUNT,
    TOPIC_MAX_COUNT,
    QA_CACHE_DIR,
    MIN_CONTENT_LENGTH_FOR_QA,
    ensure_directories,
)

# ============================================================================
# Content Hashing for Cache Management
# ============================================================================

def hash_content(text: str) -> str:
    """
    Generate SHA-256 hash of content for cache invalidation.

    Args:
        text: Content to hash

    Returns:
        Hex digest string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# ============================================================================
# Topic Extraction
# ============================================================================

def extract_topics_with_llm(content: str, title: str) -> List[str]:
    """
    Extract 3-8 semantic topics using LLM.

    Args:
        content: Article content (excerpt or full text)
        title: Article title

    Returns:
        List of topic strings
    """
    if not ANTHROPIC_API_KEY:
        logging.warning("No Anthropic API key - using fallback topic extraction")
        return extract_topics_fallback(content, title)

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""Analyze this article and extract {TOPIC_MIN_COUNT}-{TOPIC_MAX_COUNT} concise semantic topics.

Title: {title}

Content: {content[:2000]}

Requirements:
- Topics should be 1-3 words each
- Use consistent, normalized vocabulary
- Focus on substantive themes, not surface keywords
- Return ONLY a JSON array of topic strings
- Example: ["AI ethics", "cognitive science", "digital culture"]

Topics:"""

        response = client.messages.create(
            model=QA_MODEL,
            max_tokens=300,
            temperature=QA_TEMPERATURE,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        topics_text = response.content[0].text.strip()

        # Try to extract JSON array
        import re
        json_match = re.search(r'\[.*\]', topics_text, re.DOTALL)
        if json_match:
            topics = json.loads(json_match.group(0))
            # Validate and limit
            topics = [t.strip() for t in topics if isinstance(t, str)][:TOPIC_MAX_COUNT]
            logging.info(f"Extracted {len(topics)} topics: {topics}")
            return topics
        else:
            logging.warning(f"Could not parse topics from LLM response: {topics_text}")
            return extract_topics_fallback(content, title)

    except Exception as e:
        logging.error(f"Topic extraction failed: {e}")
        return extract_topics_fallback(content, title)

def extract_topics_fallback(content: str, title: str) -> List[str]:
    """
    Fallback topic extraction without LLM.
    Simple keyword-based extraction.

    Args:
        content: Article content
        title: Article title

    Returns:
        List of topic strings
    """
    # Common topic keywords for Conrad's work
    topic_keywords = {
        "AI": ["AI", "artificial intelligence", "machine learning", "neural"],
        "philosophy": ["philosophy", "philosophical", "ethics", "moral"],
        "technology": ["technology", "tech", "digital", "cyber"],
        "culture": ["culture", "cultural", "society", "social"],
        "cognition": ["cognitive", "cognition", "mind", "consciousness"],
        "history": ["history", "historical", "past"],
        "satire": ["satire", "satirical", "humor", "irony"],
        "politics": ["political", "politics", "governance", "power"],
    }

    text = (title + " " + content).lower()
    found_topics = []

    for topic, keywords in topic_keywords.items():
        if any(kw.lower() in text for kw in keywords):
            found_topics.append(topic)

    return found_topics[:TOPIC_MAX_COUNT] if found_topics else ["general"]

# ============================================================================
# Q&A Generation
# ============================================================================

def generate_qna_with_llm(content: str, title: str, author: str) -> List[Dict[str, str]]:
    """
    Generate Q&A pairs using LLM.

    Args:
        content: Article content
        title: Article title
        author: Article author

    Returns:
        List of Q&A dicts with 'question' and 'answer' keys
    """
    if not ANTHROPIC_API_KEY:
        logging.warning("No Anthropic API key - skipping Q&A generation")
        return []

    if len(content) < MIN_CONTENT_LENGTH_FOR_QA:
        logging.info(f"Content too short ({len(content)} chars) - skipping Q&A")
        return []

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""Generate {QA_MIN_QUESTIONS}-{QA_MAX_QUESTIONS} meaningful question-answer pairs for this article.

Title: {title}
Author: {author}

Content: {content[:3000]}

Requirements:
- Questions should be what readers would actually ask
- Answers should be informative and based on the article content
- Focus on key insights, themes, and arguments
- Suitable for FAQ schema and answer engines
- Return ONLY a JSON array of objects with 'question' and 'answer' keys

Example format:
[
  {{
    "question": "What is the main argument of this article?",
    "answer": "The article argues that..."
  }}
]

Q&A Pairs:"""

        response = client.messages.create(
            model=QA_MODEL,
            max_tokens=1500,
            temperature=QA_TEMPERATURE,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        qna_text = response.content[0].text.strip()

        # Extract JSON array
        import re
        json_match = re.search(r'\[.*\]', qna_text, re.DOTALL)
        if json_match:
            qna_pairs = json.loads(json_match.group(0))

            # Validate structure
            valid_pairs = []
            for pair in qna_pairs:
                if isinstance(pair, dict) and 'question' in pair and 'answer' in pair:
                    valid_pairs.append({
                        'question': pair['question'].strip(),
                        'answer': pair['answer'].strip()
                    })

            logging.info(f"Generated {len(valid_pairs)} Q&A pairs")
            return valid_pairs[:QA_MAX_QUESTIONS]
        else:
            logging.warning(f"Could not parse Q&A from LLM response: {qna_text[:200]}")
            return []

    except Exception as e:
        logging.error(f"Q&A generation failed: {e}")
        return []

# ============================================================================
# Cache Management
# ============================================================================

def load_from_cache(content_hash: str) -> Optional[Dict[str, Any]]:
    """
    Load cached Q&A and topics from disk.

    Args:
        content_hash: SHA-256 hash of content

    Returns:
        Cached data dict or None
    """
    cache_file = QA_CACHE_DIR / f"{content_hash}.json"

    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load cache {cache_file}: {e}")
            return None

    return None

def save_to_cache(content_hash: str, data: Dict[str, Any]) -> None:
    """
    Save Q&A and topics to cache.

    Args:
        content_hash: SHA-256 hash of content
        data: Data to cache (topics, qna, etc.)
    """
    QA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = QA_CACHE_DIR / f"{content_hash}.json"

    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.debug(f"Cached Q&A data to {cache_file}")
    except Exception as e:
        logging.error(f"Failed to save cache: {e}")

# ============================================================================
# Main Processing
# ============================================================================

def process_article_qa(entry: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Process a single article to extract topics and generate Q&A.

    Args:
        entry: Article entry dict from ingestion

    Returns:
        Tuple of (topics, qna_pairs)
    """
    # Extract content for processing
    content = entry.get('excerpt', '') or entry.get('content_html', '')
    title = entry.get('title', '')
    author = entry.get('author', '')
    is_conrad = entry.get('is_conrad', False)

    # Generate content hash
    content_hash = hash_content(content)

    # Check cache first
    cached = load_from_cache(content_hash)
    if cached:
        logging.info(f"Using cached Q&A for: {title}")
        return cached.get('topics', []), cached.get('qna', [])

    # Extract topics (for all articles)
    topics = extract_topics_with_llm(content, title)

    # Generate Q&A (only for Conrad's articles)
    qna = []
    if is_conrad:
        qna = generate_qna_with_llm(content, title, author)
    else:
        logging.info(f"Skipping Q&A for guest article: {title}")

    # Cache results
    cache_data = {
        'content_hash': content_hash,
        'topics': topics,
        'qna': qna,
        'processed_at': json.dumps(os.popen('date -Iseconds').read().strip())
    }
    save_to_cache(content_hash, cache_data)

    return topics, qna

def build_all_qa(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process all articles and generate Q&A data.

    Args:
        entries: List of article entries from ingestion

    Returns:
        Stats dict
    """
    logging.info(f"Processing Q&A for {len(entries)} articles")

    articles_with_qna = 0
    total_qna_pairs = 0
    total_topics = 0

    # Process each article
    enriched_entries = []
    for entry in entries:
        topics, qna = process_article_qa(entry)

        # Add to entry
        entry['topics'] = topics
        entry['qna'] = qna

        enriched_entries.append(entry)

        if qna:
            articles_with_qna += 1
            total_qna_pairs += len(qna)

        total_topics += len(topics)

    stats = {
        'total_articles': len(entries),
        'articles_with_qna': articles_with_qna,
        'total_qna_pairs': total_qna_pairs,
        'total_topics': total_topics,
        'avg_topics_per_article': total_topics / len(entries) if entries else 0,
    }

    logging.info(f"Q&A processing complete: {articles_with_qna} articles with Q&A, {total_qna_pairs} total Q&A pairs")

    return stats, enriched_entries

# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    from utils import setup_logging
    from config import LOGS_DIR
    from ingest_substack import ingest_all_feeds

    # Setup
    ensure_directories()
    setup_logging(LOGS_DIR / "qa_test.log", logging.DEBUG)

    print("Testing Q&A Generation")
    print("=" * 60)

    # Ingest feeds
    print("Ingesting RSS feeds...")
    entries = ingest_all_feeds()
    print(f"Ingested {len(entries)} entries")
    print()

    # Process Q&A
    print("Processing Q&A...")
    stats, enriched = build_all_qa(entries)

    print()
    print("=" * 60)
    print("Q&A Generation Stats:")
    print(f"  Total Articles: {stats['total_articles']}")
    print(f"  Articles with Q&A: {stats['articles_with_qna']}")
    print(f"  Total Q&A Pairs: {stats['total_qna_pairs']}")
    print(f"  Total Topics: {stats['total_topics']}")
    print(f"  Avg Topics/Article: {stats['avg_topics_per_article']:.1f}")
    print("=" * 60)

    # Show sample
    for entry in enriched:
        if entry.get('qna'):
            print(f"\nSample Q&A for: {entry['title']}")
            print(f"Topics: {', '.join(entry['topics'])}")
            for i, qa in enumerate(entry['qna'][:2], 1):
                print(f"\nQ{i}: {qa['question']}")
                print(f"A{i}: {qa['answer'][:100]}...")
            break
