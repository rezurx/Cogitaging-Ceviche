#!/usr/bin/env python3

import time, re, json, logging, os, subprocess
from datetime import datetime
import feedparser
from html import unescape

# RSS Feed Configuration
# Direct URLs work locally, but GitHub Actions needs the Cloudflare Worker proxy
DIRECT_SUBSTACK_FEEDS = [
    "https://thecogitatingceviche.substack.com/feed",
    "https://thecyberneticceviche.substack.com/feed",
]

# Set WORKER_PROXY_URL environment variable to use Cloudflare Worker
# Example: https://your-worker.workers.dev
WORKER_PROXY_URL = os.environ.get("WORKER_PROXY_URL")

if WORKER_PROXY_URL:
    # Use Cloudflare Worker proxy (for CI environments)
    SUBSTACK_FEEDS = [
        f"{WORKER_PROXY_URL}/?feed=https://thecogitatingceviche.substack.com/feed",
        f"{WORKER_PROXY_URL}/?feed=https://thecyberneticceviche.substack.com/feed",
    ]
    print(f"🔄 Using Cloudflare Worker proxy: {WORKER_PROXY_URL}")
else:
    # Use direct URLs (for local development)
    SUBSTACK_FEEDS = DIRECT_SUBSTACK_FEEDS
    print("🔗 Using direct Substack URLs (local mode)")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

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
    r"^is a now$",
    r"^now$",
    r"^is a$",
    r"^preface$",
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
    r"\bis a now\b",
    r"^now\b",
    r"^is a\b",
    r"^preface\b",
]

ELLIPSIS = "..."

def fetch_with_curl(url):
    """Use curl to fetch RSS content with multiple fallback strategies"""
    
    # Strategy 1: Standard curl with browser headers
    try:
        cmd = [
            'curl', '-s', '-L',
            '-H', f'User-Agent: {UA}',
            '-H', 'Accept: application/rss+xml, application/xml;q=0.9, text/html;q=0.8, */*;q=0.7',
            '-H', 'Connection: keep-alive',
            '--max-time', '30',
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        if result.returncode == 0 and result.stdout.strip():
            content = result.stdout.strip()
            # Quick check if it's actually RSS XML
            if content.startswith('<?xml') and '<rss' in content:
                return content
    except Exception:
        pass
    
    # Strategy 2: Use a simpler user agent that might be less likely to get blocked
    try:
        simple_ua = "feedreader/1.0"
        cmd = [
            'curl', '-s', '-L', '--max-time', '30',
            '-H', f'User-Agent: {simple_ua}',
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        if result.returncode == 0 and result.stdout.strip():
            content = result.stdout.strip()
            if content.startswith('<?xml') and '<rss' in content:
                return content
    except Exception:
        pass
    
    # Strategy 3: Use wget as fallback
    try:
        cmd = [
            'wget', '-q', '-O', '-', '--timeout=30',
            '--user-agent', UA,
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        if result.returncode == 0 and result.stdout.strip():
            content = result.stdout.strip()
            if content.startswith('<?xml') and '<rss' in content:
                return content
    except Exception:
        pass
    
    print(f"  ❌ All fetch strategies failed for {url}")
    return None

def parse_feed_direct(url, source_hint):
    """Parse feed using multiple fetch strategies"""
    try:
        # Try to fetch with multiple fallback strategies
        xml_content = fetch_with_curl(url)
        if not xml_content:
            return []
            
        # Parse the fetched content
        d = feedparser.parse(xml_content)
        
        # Check for parsing errors (keep minimal debug for CI)
        if hasattr(d, 'bozo') and d.bozo:
            print(f"  ⚠️  Feed parsing warning: {d.get('bozo_exception', 'Unknown')}")
        
        if not hasattr(d, 'entries') or not d.entries:
            print(f"  ❌ No entries found - feed title: '{d.feed.get('title', 'N/A')}'")
            # In CI, the content might be HTML instead of RSS - check first few chars
            if not xml_content.startswith('<?xml'):
                print(f"  🔍 Content doesn't appear to be XML: {xml_content[:100]}...")
            return []
            
        items = []
        for it in d.entries:
            html = it.get("content", [{}])[0].get("value") if it.get("content") else it.get("summary", "")
            # Extract subtitle from summary if available
            subtitle = ""
            if it.get("summary"):
                subtitle_text = strip_html_to_text(it.get("summary", ""))
                # Take first 80-100 chars as subtitle if different from title
                if subtitle_text and subtitle_text.lower() != it.get("title", "").lower():
                    subtitle = subtitle_text[:100] + ("..." if len(subtitle_text) > 100 else "")
            
            items.append({
                "title": it.get("title", "") or "",
                "subtitle": subtitle,
                "url": it.get("link", "") or "",
                "published": it.get("published", it.get("updated", "")) or "",
                "image": extract_first_image(html),
                "excerpt": sanitize_preview(html, 25, 40),
                "source": source_hint,
            })
        return items
        
    except Exception as e:
        print(f"  ❌ Error parsing feed {url}: {e}")
        return []

def strip_html_to_text(html: str) -> str:
    txt = re.sub(r"<br\s*/?>", "\n", html or "", flags=re.I)
    txt = re.sub(r"</p\s*>", "\n", txt, flags=re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)  # remove tags
    txt = unescape(re.sub(r"\s+", " ", txt)).strip()
    return txt

def remove_banned(text: str) -> str:
    lines = [ln.strip() for ln in re.split(r"[.\n]+", text) if ln.strip()]
    kept = []
    for ln in lines:
        if any(re.search(pat, ln, re.I) for pat in BANNED_LINE_PATTERNS):
            continue
        kept.append(ln)
    cleaned = " ".join(kept)
    for pat in BANNED_INLINE_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.I)
    return re.sub(r"\s{2,}", " ", cleaned).strip()

def trim_to_word_window(text: str, min_words: int = 25, max_words: int = 40) -> str:
    if not text: return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    teaser = sentences[0].strip()
    words = teaser.split()
    i = 1
    while len(words) < min_words and i < len(sentences):
        more = sentences[i].strip().split()
        needed = min(max_words - len(words), len(more))
        words.extend(more[:needed])
        i += 1
        if len(words) >= max_words:
            break
    if len(words) > max_words:
        words = words[:max_words]
    out = " ".join(words).rstrip()
    out = re.sub(r"[^\w)\]}\"']+$", "", out).rstrip()
    if not out.endswith(ELLIPSIS):
        out = f"{out}{ELLIPSIS}"
    return out

def sanitize_preview(raw_html: str, min_words: int = 25, max_words: int = 40) -> str:
    plain = strip_html_to_text(raw_html or "")
    cleaned = remove_banned(plain)
    if not cleaned: return ""
    
    # Additional cleanup for common fragment words at start
    cleaned = re.sub(r'^\s*(is\s+a\s+now|now|is\s+a|preface)\s+', '', cleaned, flags=re.I)
    cleaned = re.sub(r'^\s*(discussion\s+(via|by)\s+notebooklm)\s+', '', cleaned, flags=re.I)
    cleaned = re.sub(r'^\s*(image\s+created?\s+with\s+generative\s+ai)\s+', '', cleaned, flags=re.I)
    cleaned = re.sub(r'^\s*(also,?\s+check\s+out)\s+', '', cleaned, flags=re.I)
    cleaned = re.sub(r'^\s*(read\s+more\.\.\.)\s*$', '', cleaned, flags=re.I)
    
    if not cleaned: return ""
    return trim_to_word_window(cleaned, min_words=min_words, max_words=max_words)

def extract_first_image(html):
    m = re.search(r'<img[^>]+src="([^"]+)"', html or "", re.I)
    return m.group(1) if m else ""

def ingest_substacks():
    all_items = []
    successful_feeds = 0
    
    for feed in SUBSTACK_FEEDS:
        try:
            print(f"Fetching {feed}...")
            items = parse_feed_direct(feed, source_hint="substack")
            if items:  # Only process if we got content
                all_items.extend(items)
                successful_feeds += 1
                print(f"  ✅ Found {len(items)} items")
            else:
                print(f"  ❌ Failed to fetch {feed}")
        except Exception as e:
            print(f"  ❌ Error processing {feed}: {e}")
            continue
        
        time.sleep(1.5)  # Be nice to servers
    
    if successful_feeds == 0:
        print("⚠️  Warning: No feeds were successfully processed")
        # Don't fail completely, just return empty list
        return []
    
    print(f"✅ Successfully processed {successful_feeds}/{len(SUBSTACK_FEEDS)} feeds")
    
    def ts(s):
        try:
            return int(datetime.fromisoformat(s).timestamp())
        except Exception:
            return 0
    
    all_items.sort(key=lambda x: ts(x["published"]), reverse=True)
    return all_items

def write_output(items, out_path="public/data/posts.json"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"generatedAt": datetime.now().isoformat(), "items": items}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    items = ingest_substacks()
    write_output(items)
    print(f"Wrote {len(items)} items")