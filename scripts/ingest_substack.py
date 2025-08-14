#!/usr/bin/env python3

import time, re, json, logging, os
from datetime import datetime
import requests
import feedparser
from html import unescape

# --- Configuration ---
SUBSTACK_FEEDS = [
    "https://thecogitatingceviche.substack.com/feed",
    "https://thecyberneticceviche.substack.com/feed",
]

# Enhanced request headers for 403 resistance
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
HDRS = {
    "User-Agent": UA,
    "Accept": "application/rss+xml, application/xml;q=0.9, text/html;q=0.8, */*;q=0.7",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

# Phrases/lines to remove from teaser text
BANNED_LINE_PATTERNS = [
    r"^image created with generative ai$",
    r"^share$",
    r"^subscribe$",
    r"^voice[- ]?over provided by notebooklm$",
    r"^discussion by notebooklm$",
    r"^voice[- ]?over provided by amazon polly$",
    r"^also, check out eleven labs.*$",
    r"^the cogitating cevich[eé].*reader[- ]supported publication.*$",
    r"^the cybernetic cevich[eé].*reader[- ]supported publication.*$",
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
    r"the cogitating cevich[eé]",
    r"the cybernetic cevich[eé]",
]

ELLIPSIS = "..."

# --- Enhanced Helper Functions ---

def setup_logging():
    """Configure comprehensive logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('automation_logs/ingestion.log', mode='a')
        ]
    )
    return logging.getLogger(__name__)

def fetch_rss(url, max_retries=4, backoff=2.0):
    """Enhanced RSS fetching with exponential backoff and comprehensive error handling."""
    logger = logging.getLogger(__name__)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
            
            # Add jitter to prevent thundering herd
            if attempt > 0:
                jitter = backoff * (attempt + 1) * (0.5 + 0.5 * hash(url) % 100 / 100)
                time.sleep(jitter)
            
            resp = requests.get(url, headers=HDRS, timeout=30)
            
            if resp.status_code == 200:
                logger.info(f"Successfully fetched {url}")
                return resp.text
            elif resp.status_code == 403:
                logger.warning(f"403 Forbidden for {url}, trying with different headers")
                # Fallback headers for 403 issues
                fallback_headers = HDRS.copy()
                fallback_headers["User-Agent"] = "Mozilla/5.0 Content Hub/1.0"
                resp = requests.get(url, headers=fallback_headers, timeout=30)
                if resp.status_code == 200:
                    return resp.text
            elif resp.status_code == 429:
                logger.warning(f"Rate limited on {url}, waiting longer")
                time.sleep(backoff * (attempt + 2) * 2)  # Longer wait for rate limits
                continue
            
            logger.warning(f"GET {url} returned {resp.status_code}")
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error for {url}: {e}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error for {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
    
    raise RuntimeError(f"Failed to fetch feed after {max_retries} retries: {url}")

def strip_html_to_text(html: str) -> str:
    """Convert HTML to clean text with proper formatting."""
    if not html:
        return ""
    
    # Preserve line breaks
    txt = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    txt = re.sub(r"</p\s*>", "\n", txt, flags=re.I)
    txt = re.sub(r"</div\s*>", "\n", txt, flags=re.I)
    
    # Remove all HTML tags
    txt = re.sub(r"<[^>]+>", " ", txt)
    
    # Decode HTML entities and normalize whitespace
    txt = unescape(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    
    return txt

def remove_banned(text: str) -> str:
    """Remove banned phrases and promotional content with improved pattern matching."""
    if not text:
        return ""
    
    # Split into lines and filter out banned line patterns
    lines = [ln.strip() for ln in re.split(r"[.\n]+", text) if ln.strip()]
    kept = []
    
    for ln in lines:
        # Skip lines that match banned patterns
        if any(re.search(pat, ln, re.I) for pat in BANNED_LINE_PATTERNS):
            logging.debug(f"Removed banned line: {ln}")
            continue
        kept.append(ln)
    
    # Rejoin and remove inline banned patterns
    cleaned = " ".join(kept)
    
    for pat in BANNED_INLINE_PATTERNS:
        before = cleaned
        cleaned = re.sub(pat, "", cleaned, flags=re.I)
        if before != cleaned:
            logging.debug(f"Removed inline pattern: {pat}")
    
    # Normalize whitespace
    return re.sub(r"\s{2,}", " ", cleaned).strip()

def trim_to_word_window(text: str, min_words: int = 25, max_words: int = 40) -> str:
    """Trim text to 25-40 words with proper sentence handling and ellipsis."""
    if not text:
        return ""
    
    # Split into sentences more carefully
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if not sentences:
        return ""
    
    # Start with first sentence
    teaser = sentences[0].strip()
    words = teaser.split()
    
    # Add more sentences if needed to reach minimum
    i = 1
    while len(words) < min_words and i < len(sentences):
        more_words = sentences[i].strip().split()
        needed = min(max_words - len(words), len(more_words))
        words.extend(more_words[:needed])
        i += 1
        
        if len(words) >= max_words:
            break
    
    # Trim to maximum if exceeded
    if len(words) > max_words:
        words = words[:max_words]
    
    # Clean up the ending
    result = " ".join(words).rstrip()
    
    # Remove trailing punctuation except for proper sentence endings
    result = re.sub(r"[^\w)\]}"\"']+$", "", result).rstrip()
    
    # Always end with ellipsis unless it's a complete sentence
    if not result.endswith(('.', '!', '?', ELLIPSIS)):
        result = f"{result}{ELLIPSIS}"
    elif result.endswith(('.', '!', '?')) and len(words) == max_words:
        # If we hit max words but have a complete sentence, still add ellipsis
        result = f"{result[:-1]}{ELLIPSIS}"
    
    return result

def sanitize_preview(raw_html: str, min_words: int = 25, max_words: int = 40) -> str:
    """Complete preview sanitization pipeline with error handling."""
    try:
        if not raw_html:
            return ""
        
        # Convert HTML to plain text
        plain = strip_html_to_text(raw_html)
        if not plain:
            return ""
        
        # Remove banned content
        cleaned = remove_banned(plain)
        if not cleaned:
            return ""
        
        # Trim to word window
        trimmed = trim_to_word_window(cleaned, min_words=min_words, max_words=max_words)
        
        logging.debug(f"Preview: {len(plain)} chars -> {len(cleaned)} chars -> {len(trimmed)} chars")
        return trimmed
        
    except Exception as e:
        logging.error(f"Error in sanitize_preview: {e}")
        return ""

def extract_first_image(html):
    """Extract first image from HTML content with fallback options."""
    if not html:
        return ""
    
    # Try different image patterns
    patterns = [
        r'<img[^>]+src="([^"]+)"',  # Standard img tags
        r'src="([^"]*\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',  # Image extensions
        r'content="([^"]*\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',  # Meta content
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return match.group(1)
    
    return ""

def parse_feed(xml_text, source_hint):
    """Parse RSS feed with enhanced error handling and validation."""
    logger = logging.getLogger(__name__)
    
    try:
        d = feedparser.parse(xml_text)
        
        if d.bozo:
            logger.warning(f"Feed parsing had issues: {d.bozo_exception}")
        
        items = []
        for entry in d.entries:
            try:
                # Get content with fallback
                html_content = ""
                if hasattr(entry, 'content') and entry.content:
                    html_content = entry.content[0].get('value', '')
                elif hasattr(entry, 'summary'):
                    html_content = entry.summary
                
                # Extract and validate data
                title = getattr(entry, 'title', '') or 'Untitled'
                url = getattr(entry, 'link', '') or ''
                published = getattr(entry, 'published', getattr(entry, 'updated', '')) or ''
                
                if not url:
                    logger.warning(f"Skipping entry without URL: {title}")
                    continue
                
                # Generate preview and extract image
                excerpt = sanitize_preview(html_content, 25, 40)
                image = extract_first_image(html_content)
                
                item = {
                    "title": title,
                    "url": url,
                    "published": published,
                    "image": image,
                    "excerpt": excerpt,
                    "source": source_hint,
                }
                
                items.append(item)
                logger.debug(f"Parsed item: {title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error parsing feed entry: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(items)} items from feed")
        return items
        
    except Exception as e:
        logger.error(f"Error parsing feed: {e}")
        return []

def ingest_substacks():
    """Ingest articles from all Substack feeds with enhanced error handling."""
    logger = logging.getLogger(__name__)
    all_items = []
    successful_feeds = 0
    
    for feed_url in SUBSTACK_FEEDS:
        try:
            logger.info(f"Processing feed: {feed_url}")
            xml = fetch_rss(feed_url)
            items = parse_feed(xml, source_hint="substack")
            
            if items:
                all_items.extend(items)
                successful_feeds += 1
                logger.info(f"Added {len(items)} items from {feed_url}")
            else:
                logger.warning(f"No items found in feed: {feed_url}")
            
            # Rate limiting between feeds
            time.sleep(1.5)
            
        except Exception as e:
            logger.error(f"Failed to process feed {feed_url}: {e}")
            # Continue with other feeds even if one fails
            continue
    
    if successful_feeds == 0:
        raise RuntimeError("No feeds were successfully processed")
    
    # Sort by publication date
    def timestamp_from_string(date_str):
        try:
            # Try various date formats
            for fmt in [
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
            ]:
                try:
                    return int(datetime.strptime(date_str, fmt).timestamp())
                except ValueError:
                    continue
            
            # Fallback: try feedparser's time parsing
            import time as time_module
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return int(time_module.mktime(parsed_time))
            
        except Exception as e:
            logger.debug(f"Date parsing error for '{date_str}': {e}")
        
        return 0  # Fallback to epoch
    
    all_items.sort(key=lambda x: timestamp_from_string(x["published"]), reverse=True)
    
    logger.info(f"Total items collected: {len(all_items)} from {successful_feeds} feeds")
    return all_items

def write_output(items, out_path="public/data/posts.json"):
    """Write items to JSON with enhanced metadata and error handling."""
    logger = logging.getLogger(__name__)
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        # Prepare output data with metadata
        output_data = {
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "totalItems": len(items),
            "sources": list(set(item.get("source", "unknown") for item in items)),
            "items": items
        }
        
        # Write to temporary file first, then move (atomic operation)
        temp_path = f"{out_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Atomic move
        os.rename(temp_path, out_path)
        
        logger.info(f"Successfully wrote {len(items)} items to {out_path}")
        
        # Validate the written file
        with open(out_path, "r", encoding="utf-8") as f:
            validation_data = json.load(f)
            if len(validation_data.get("items", [])) != len(items):
                raise RuntimeError("Written file validation failed")
        
    except Exception as e:
        logger.error(f"Error writing output to {out_path}: {e}")
        # Clean up temp file if it exists
        temp_path = f"{out_path}.tmp"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

def main():
    """Main execution function with comprehensive error handling."""
    # Ensure log directory exists
    os.makedirs("automation_logs", exist_ok=True)
    
    logger = setup_logging()
    
    try:
        logger.info("Starting enhanced Substack ingestion...")
        
        # Validate configuration
        if not SUBSTACK_FEEDS:
            raise RuntimeError("No Substack feeds configured")
        
        # Ingest content
        items = ingest_substacks()
        
        if not items:
            logger.warning("No items found, but continuing to write empty output")
        
        # Write output
        write_output(items)
        
        # Success summary
        logger.info(f"✅ Enhanced ingestion completed successfully!")
        logger.info(f"📊 Statistics:")
        logger.info(f"   - Total items: {len(items)}")
        logger.info(f"   - Feeds processed: {len(SUBSTACK_FEEDS)}")
        logger.info(f"   - Output: public/data/posts.json")
        
        # Return success code
        return 0
        
    except Exception as e:
        logger.error(f"❌ Enhanced ingestion failed: {e}")
        logger.error("Stack trace:", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)