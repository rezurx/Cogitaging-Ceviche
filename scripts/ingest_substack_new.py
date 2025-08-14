#!/usr/bin/env python3

import time, re, json, logging, os
from datetime import datetime
import requests
import feedparser
from html import unescape

SUBSTACK_FEEDS = [
    "https://thecogitatingceviche.substack.com/feed",
    "https://thecyberneticceviche.substack.com/feed",
]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
HDRS = {
    "User-Agent": UA,
    "Accept": "application/rss+xml, application/xml;q=0.9, text/html;q=0.8, */*;q=0.7",
    "Connection": "keep-alive",
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

def fetch_rss(url, max_retries=8, backoff=4.0):
    """Fetch RSS with enhanced error handling and fallback strategies"""
    for i in range(max_retries):
        try:
            # Try different User-Agent strings for better success
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "PostmanRuntime/7.32.2"
            ]
            
            headers = HDRS.copy()
            headers["User-Agent"] = user_agents[i % len(user_agents)]
            
            # Add more browser-like headers
            headers.update({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none"
            })
            
            resp = requests.get(url, headers=headers, timeout=30)
            
            if resp.status_code == 200:
                return resp.text
            elif resp.status_code in (403, 429):
                # Wait longer for rate limiting/blocking
                wait_time = backoff * (i + 1) * 2
                logging.warning(f"Got {resp.status_code} for {url}, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.warning(f"GET {url} returned {resp.status_code}; retrying...")
                time.sleep(backoff * (i + 1))
                
        except requests.RequestException as e:
            logging.warning(f"GET error {e}; retrying...")
            time.sleep(backoff * (i + 1))
    
    # If all retries failed, return empty string instead of raising
    logging.error(f"Failed to fetch feed after {max_retries} retries: {url}")
    return ""

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
    return trim_to_word_window(cleaned, min_words=min_words, max_words=max_words)

def extract_first_image(html):
    m = re.search(r'<img[^>]+src="([^"]+)"', html or "", re.I)
    return m.group(1) if m else ""

def parse_feed(xml_text, source_hint):
    d = feedparser.parse(xml_text)
    items = []
    for it in d.entries:
        html = it.get("content", [{}])[0].get("value") if it.get("content") else it.get("summary", "")
        items.append({
            "title": it.get("title", "") or "",
            "url": it.get("link", "") or "",
            "published": it.get("published", it.get("updated", "")) or "",
            "image": extract_first_image(html),
            "excerpt": sanitize_preview(html, 25, 40),
            "source": source_hint,
        })
    return items

def ingest_substacks():
    all_items = []
    successful_feeds = 0
    
    for feed in SUBSTACK_FEEDS:
        try:
            print(f"Fetching {feed}...")
            xml = fetch_rss(feed)
            if xml:  # Only process if we got content
                items = parse_feed(xml, source_hint="substack")
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
        json.dump({"generatedAt": datetime.utcnow().isoformat(), "items": items}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    items = ingest_substacks()
    write_output(items)
    print(f"Wrote {len(items)} items")