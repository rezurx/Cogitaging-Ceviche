#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ceviche Engine - Pipeline Orchestrator
Main entry point for running the complete content pipeline
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Import all pipeline modules
from config import LOGS_DIR, ensure_directories
from utils import setup_logging
from ingest_substack import ingest_all_feeds, get_ingestion_stats
from build_qa import build_all_qa  # Phase 2
from build_articles import build_all_articles
from build_schema import build_all_schemas

# ============================================================================
# Pipeline Orchestration
# ============================================================================

def run_full_pipeline(dry_run: bool = False) -> Dict[str, Any]:
    """
    Run the complete Ceviche Engine pipeline.

    Args:
        dry_run: If True, don't write files (validation only)

    Returns:
        Pipeline execution stats
    """
    start_time = datetime.now()
    logging.info("=" * 60)
    logging.info("Ceviche Engine Pipeline Starting")
    logging.info("=" * 60)

    pipeline_stats = {
        "start_time": start_time.isoformat(),
        "dry_run": dry_run,
        "success": False,
        "errors": [],
    }

    try:
        # Step 1: Ingest RSS Feeds
        logging.info("\n[1/4] Ingesting RSS Feeds...")
        entries = ingest_all_feeds()

        if not entries:
            error_msg = "No entries ingested from RSS feeds"
            logging.error(error_msg)
            pipeline_stats["errors"].append(error_msg)
            pipeline_stats["success"] = False
            return pipeline_stats

        ingestion_stats = get_ingestion_stats(entries)
        pipeline_stats["ingestion"] = ingestion_stats

        logging.info(f"Ingested {ingestion_stats['total_entries']} entries")
        logging.info(f"  Conrad entries: {ingestion_stats['conrad_entries']}")
        logging.info(f"  Guest entries: {ingestion_stats['guest_entries']}")
        logging.info(f"  Unique authors: {ingestion_stats['unique_authors']}")

        if dry_run:
            logging.info("DRY RUN: Skipping file writes")
            pipeline_stats["success"] = True
            return pipeline_stats

        # Step 2: Extract Topics and Q&A (Phase 2)
        logging.info("\n[2/4] Extracting Topics and Q&A...")
        qa_stats, enriched_entries = build_all_qa(entries)
        pipeline_stats["qa"] = qa_stats

        logging.info(f"Articles with Q&A: {qa_stats['articles_with_qna']}")
        logging.info(f"Total Q&A pairs: {qa_stats['total_qna_pairs']}")
        logging.info(f"Avg topics/article: {qa_stats['avg_topics_per_article']:.1f}")

        # Use enriched entries for remaining steps
        entries = enriched_entries

        # Step 3: Build Hugo Articles
        logging.info("\n[3/4] Building Hugo Articles...")
        article_stats = build_all_articles(entries)
        pipeline_stats["articles"] = article_stats

        logging.info(f"Created {article_stats['hugo_files_created']} Hugo files")
        logging.info(f"Generated posts.json: {article_stats['posts_json_created']}")

        # Step 4: Build JSON-LD Schemas
        logging.info("\n[4/4] Building JSON-LD Schemas...")
        schema_stats = build_all_schemas(entries)
        pipeline_stats["schemas"] = schema_stats

        logging.info(f"Created {schema_stats['article_schemas_created']} article schemas")
        logging.info(f"Person schema: {schema_stats['person_schema_created']}")
        logging.info(f"WebSite schema: {schema_stats['website_schema_created']}")

        # Success!
        pipeline_stats["success"] = True

    except Exception as e:
        error_msg = f"Pipeline failed with error: {e}"
        logging.error(error_msg, exc_info=True)
        pipeline_stats["errors"].append(error_msg)
        pipeline_stats["success"] = False

    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        pipeline_stats["end_time"] = end_time.isoformat()
        pipeline_stats["duration_seconds"] = duration

        logging.info("\n" + "=" * 60)
        if pipeline_stats["success"]:
            logging.info("Pipeline completed successfully!")
        else:
            logging.error("Pipeline completed with errors")
        logging.info(f"Duration: {duration:.2f} seconds")
        logging.info("=" * 60)

    return pipeline_stats

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Ceviche Engine - Semantic Amplification Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                  # Run full pipeline
  python run_pipeline.py --dry-run        # Validate without writing
  python run_pipeline.py --debug          # Enable debug logging
  python run_pipeline.py --log-file my.log # Custom log file
        """
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate pipeline without writing files"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Custom log file path"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (log file only)"
    )

    args = parser.parse_args()

    # Setup directories
    ensure_directories()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    log_file = args.log_file if args.log_file else LOGS_DIR / "pipeline.log"

    if args.quiet:
        # Log file only, no console
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file)]
        )
    else:
        setup_logging(log_file, log_level)

    # Print banner
    if not args.quiet:
        print()
        print("T" + "P" * 58 + "W")
        print("Q" + " " * 12 + "Ceviche Engine Pipeline" + " " * 23 + "Q")
        print("Q" + " " * 11 + "Semantic Amplification v1.0" + " " * 20 + "Q")
        print("Z" + "P" * 58 + "]")
        print()

    # Run pipeline
    stats = run_full_pipeline(dry_run=args.dry_run)

    # Print summary
    if not args.quiet:
        print("\nPipeline Summary:")
        print("-" * 60)
        print(f"Status: {' SUCCESS' if stats['success'] else ' FAILED'}")
        print(f"Duration: {stats['duration_seconds']:.2f}s")

        if "ingestion" in stats:
            print(f"\nIngestion:")
            print(f"  Total Entries: {stats['ingestion']['total_entries']}")
            print(f"  Conrad: {stats['ingestion']['conrad_entries']}")
            print(f"  Guests: {stats['ingestion']['guest_entries']}")

        if "articles" in stats:
            print(f"\nArticles:")
            print(f"  Hugo Files: {stats['articles']['hugo_files_created']}")
            print(f"  posts.json: {'' if stats['articles']['posts_json_created'] else ''}")

        if "schemas" in stats:
            print(f"\nSchemas:")
            print(f"  Article Schemas: {stats['schemas']['article_schemas_created']}")
            print(f"  Person Schema: {'' if stats['schemas']['person_schema_created'] else ''}")
            print(f"  WebSite Schema: {'' if stats['schemas']['website_schema_created'] else ''}")

        if stats.get("errors"):
            print(f"\nErrors:")
            for error in stats["errors"]:
                print(f"  - {error}")

        print("-" * 60)

    # Exit with appropriate code
    sys.exit(0 if stats["success"] else 1)

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
