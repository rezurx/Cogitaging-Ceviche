# Content Improvement Plan - July 1, 2025

## Overview

Following the successful RSS feed fix, two content quality issues have been identified that need addressing to improve the user experience on the cogitating-ceviche website.

## Issue #1: Substack Articles Need 100-word Previews

### Current State
- Substack RSS feeds only provide brief summaries (1-2 sentences)
- Articles appear with minimal content, not engaging for readers
- Full article content is available on source URLs but not being extracted

### Proposed Solution
**Difficulty: Easy**
- Modify `ingest_external_articles.py` to fetch full article content via web scraping
- Use BeautifulSoup to extract article body content from Substack article URLs
- Process and clean the HTML content to remove formatting
- Truncate to approximately 100 words for preview
- Preserve existing summary as fallback if scraping fails

### Implementation Steps
1. Add full content fetching function for Substack URLs
2. Integrate BeautifulSoup HTML parsing
3. Implement text cleaning and truncation logic
4. Update the RSS processing loop to use enhanced content
5. Add error handling for failed content fetches

**Estimated Time:** 2-3 hours

### Files to Modify
- `/home/resurx/websites/cogitating-ceviche/ingest_external_articles.py`

## Issue #2: Fix Vocal Media Dead Links

### Current State
- Vocal articles have broken canonical URLs
- Links show pattern: `https://vocal.media/None/article-slug`
- Should show pattern: `https://vocal.media/community/article-slug`
- Example broken: `https://vocal.media/None/cry-me-a-discourse`
- Should be: `https://vocal.media/humans/cry-me-a-discourse`

### Root Cause
- Vocal scraper incorrectly parsing community/publication data from `__NEXT_DATA__` JSON
- The current code assumes a simple structure but Vocal publishes to specific communities
- Community field extraction is failing, defaulting to "None"

### Proposed Solution
**Difficulty: Medium**
- Analyze Vocal's `__NEXT_DATA__` JSON structure more thoroughly
- Identify correct field path for community/publication names
- Update the URL construction logic in the Vocal scraper
- Test with multiple Vocal articles to ensure consistent field mapping
- Add fallback logic if community data is unavailable

### Implementation Steps
1. Inspect multiple Vocal article pages to understand JSON structure variations
2. Map the correct path to community/publication data
3. Update the `scrape_vocal_page()` function URL construction
4. Test with existing articles to verify link fixes
5. Re-run ingestion to update existing broken links

**Estimated Time:** 1-2 hours

### Files to Modify
- `/home/resurx/websites/cogitating-ceviche/ingest_external_articles.py` (Vocal scraper section)

## Technical Notes for Implementation

### Required Libraries
- `BeautifulSoup4` (likely already available)
- `requests` (already in use)
- Standard library modules for text processing

### Testing Strategy
1. Test Substack content extraction on a few sample articles
2. Verify Vocal link construction with known working URLs
3. Run full ingestion script with verbose logging
4. Check generated markdown files for quality improvements

### Success Criteria
- Substack articles show engaging ~100-word previews
- All Vocal media links are clickable and lead to correct articles
- No regression in existing Medium/Vocal functionality
- Maintain existing duplicate detection logic

## Priority Assessment

**Both fixes are achievable and worthwhile:**
- **Substack preview fix:** High impact on user engagement
- **Vocal link fix:** Critical for functionality (dead links are unacceptable)

These improvements will significantly enhance the quality and usability of the external articles section.

## Future CLI AI Reference

When implementing these fixes:
1. Always backup the working `ingest_external_articles.py` before modifications
2. Test changes incrementally rather than implementing both fixes simultaneously
3. Use verbose logging during development to debug issues
4. Verify that existing articles from Medium and working Vocal links remain unaffected
5. Consider adding configuration options for preview length and fallback behavior