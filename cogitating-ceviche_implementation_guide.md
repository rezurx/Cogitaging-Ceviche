
# Cogitating Ceviche — Cohesive Implementation Guide

This document consolidates the site improvements into a single, copy‑pasteable plan that you can hand to any engineer (or drop into Claude Code). It covers ingestion (Substack‑only, with a 403‑proof path), teaser sanitization (25–40 words), layout/menu/hero adjustments, responsive grid behavior, accessibility, and SEO. All snippets are self‑contained and can be added incrementally.

---

## 0) Goals & Scope

- **Hosting**: GitHub Pages (static).  
- **Sources**: Substack RSS only (no Medium/Vocal).  
- **Purpose**: Pull posts server‑side on a schedule, generate a static `public/data/posts.json`, and render cards client‑side.  
- **Teasers**: 25–40 words, always end with `...`, with platform boilerplate removed.  
- **Design**: Smaller hero, higher logo contrast, subtitle `Food for Thought`, responsive grid that scales at wide viewports, and accessible navigation.

---

## 1) Substack‑Only Ingestion (w/ 403‑resistant fetch)

Create `scripts/ingest_substack.py` and call it in CI to write `public/data/posts.json`. The script sets a real browser UA, retries on errors, and sanitizes previews on the server.

```python
# scripts/ingest_substack.py
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

def fetch_rss(url, max_retries=4, backoff=2.0):
    for i in range(max_retries):
        try:
            resp = requests.get(url, headers=HDRS, timeout=25)
            if resp.status_code == 200:
                return resp.text
            logging.warning(f"GET {url} returned {resp.status_code}; retrying...")
        except requests.RequestException as e:
            logging.warning(f"GET error {e}; retrying...")
        time.sleep(backoff * (i + 1))
    raise RuntimeError(f"Failed to fetch feed after retries: {url}")

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
    out = re.sub(r"[^\w)\]}”\"']+$", "", out).rstrip()
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
    for feed in SUBSTACK_FEEDS:
        xml = fetch_rss(feed)
        all_items.extend(parse_feed(xml, source_hint="substack"))
        time.sleep(1.5)
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
```

### Optional: Cloudflare Worker proxy (if GitHub IPs are 403'ed)

```js
// worker.js
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const target = url.searchParams.get("feed");
    if (!target) return new Response("Missing ?feed=", { status: 400 });
    const r = await fetch(target, {
      headers: {
        "User-Agent": "Mozilla/5.0 Content Hub",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"
      }
    });
    const body = await r.text();
    return new Response(body, {
      status: r.status,
      headers: {
        "content-type": r.headers.get("content-type") || "application/rss+xml",
        "access-control-allow-origin": "*"
      }
    });
  }
};
```

If needed, point `SUBSTACK_FEEDS` to `https://your-worker.workers.dev/?feed=<encodedFeedUrl>`.

---

## 2) GitHub Actions Workflow (hourly)

Create `.github/workflows/ingest.yml`:

```yaml
name: Ingest Substack feeds

on:
  schedule:
    - cron: "0 * * * *"    # hourly
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install requests feedparser

      - name: Build posts.json
        run: |
          python scripts/ingest_substack.py

      - name: Commit data
        run: |
          if [[ -n "$(git status --porcelain)" ]]; then
            git config user.name "github-actions[bot]"
            git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
            git add -A
            git commit -m "data: update posts.json"
            git push
          fi
```

---

## 3) Front‑End Read (static JSON)

```html
<script>
async function loadCards() {
  const res = await fetch("/data/posts.json", { cache: "no-cache" });
  const { items } = await res.json();
  renderCards(items.slice(0, 30));
}
document.addEventListener("DOMContentLoaded", loadCards);
</script>
```

---

## 4) Card Markup, Menu, and Hero

### Card (entire card is clickable; consistent image ratio; tidy meta row)

```html
<article class="card">
  <a class="card-link" href="{{url}}" aria-label="{{title}}">
    {{#if image}}
      <img src="{{image}}" alt="{{alt}}" loading="lazy" decoding="async" width="1200" height="675">
    {{else}}
      <div class="placeholder" aria-hidden="true">TC</div>
    {{/if}}
    <div class="card-body">
      <h3>{{title}}</h3>
      <p class="excerpt">{{excerpt}}</p>
      <div class="meta-row">
        <span class="chip">Substack</span>
        <time datetime="{{isoDate}}">{{prettyDate}}</time>
      </div>
    </div>
  </a>
</article>
```

### Menu (responsive with accessible toggle)

```html
<nav class="site-nav">
  <div class="nav-inner">
    <a href="/" class="brand">
      <span class="logo-badge"><img src="/assets/logo.png" alt="The Cogitating Ceviche"></span>
      <span class="brand-text">The Cogitating Ceviche</span>
    </a>

    <button class="nav-toggle" aria-expanded="false" aria-controls="nav-links">Menu</button>

    <ul id="nav-links" class="nav-links">
      <li><a href="/">Home</a></li>
      <li><a href="/all/">All Posts</a></li>
      <li><a href="/topics/">Topics</a></li>
      <li><a href="/about/">About</a></li>
      <li><a href="https://thecogitatingceviche.substack.com" rel="noopener">Substack</a></li>
    </ul>
  </div>
</nav>

<script>
  const btn = document.querySelector(".nav-toggle");
  const links = document.getElementById("nav-links");
  if (btn && links) {
    btn.addEventListener("click", () => {
      const open = links.classList.toggle("show");
      btn.setAttribute("aria-expanded", String(open));
    });
  }
</script>
```

### Hero (smaller, with new subtitle)

```html
<header class="hero">
  <div class="inner">
    <h1>The Cogitating Ceviche</h1>
    <p class="subtitle">Food for Thought</p>
  </div>
</header>
```

---

## 5) Responsive Layout & Aesthetics

```css
/* Content canvas */
.page { max-width: min(1200px, 92vw); margin: 0 auto; padding: clamp(12px, 2vw, 24px); }
body { background:#0b0f14; }      /* site chrome */
main.page { background:#fbfaf6; } /* content backdrop */

/* Grid that scales as viewport grows */
.card-grid { display:grid; gap:20px; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); align-items:stretch; }
@media (min-width: 1440px){ .card-grid{ grid-template-columns:repeat(4, minmax(0,1fr)); } }
@media (min-width: 1800px){ .card-grid{ grid-template-columns:repeat(5, minmax(0,1fr)); } }

/* Hero scales down on wide/zoomed screens */
.hero{ min-height: clamp(22vh, 34vh, 38vh); padding: clamp(28px, 6vh, 56px) 16px; display:grid; place-items:center; text-align:center;
       background: radial-gradient(1200px 600px at 50% 0%, #0f1720 0%, #0b0f14 60%, #090c10 100%); }
.hero .inner{ max-width: 900px; margin: 0 auto; }
.hero h1{ font-size: clamp(2rem, 4vw + 0.5rem, 4rem); margin: 0 0 8px; color:#dbe9f1; }
.hero .subtitle{ font-size: clamp(1rem, 1.1vw + 0.4rem, 1.25rem); color:#9fb7c7; }

/* Cards */
.card{ background:#f7f2e5; border:1px solid #e6dfcf; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,.08); }
.card:hover { box-shadow: 0 10px 28px rgba(0,0,0,.12); transform: translateY(-1px); transition: box-shadow .2s, transform .2s; }
.card-link{ display:block; color:inherit; text-decoration:none; }
.card-link:focus-visible{ outline:3px solid #7ec0e4; outline-offset:3px; border-radius:12px; }
.card img{ width:100%; aspect-ratio:16/9; object-fit:cover; object-position:50% 25%; }
.placeholder{ aspect-ratio:16/9; display:grid; place-items:center; background:linear-gradient(135deg,#22303a, #0b0f14); color:#cfe3ee; font-weight:700; }
.card-body{ padding:16px; line-height:1.65; }
.card h3{ margin:0 0 8px; font-size:1.1rem; line-height:1.3; color:#0f1b22; }
.excerpt{ font-size:.98rem; color:#2d3a3f; } /* server already trims to 25–40 words */
.meta-row{ display:flex; justify-content:space-between; align-items:center; margin-top:12px; }
.chip{ font-size:.75rem; padding:4px 8px; border-radius:999px; background:#eef5f8; border:1px solid #d7e6ee; color:#27566b; }

/* Menu */
.site-nav { position: sticky; top: 0; z-index: 1000; background: #0b0f14; border-bottom: 1px solid rgba(255,255,255,0.06); }
.nav-inner { max-width: 1100px; margin: 0 auto; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; }
.brand { display: inline-flex; align-items: center; gap: 10px; text-decoration: none; }
.logo-badge { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.25); display: inline-flex; }
.logo-badge img { width: 36px; height: 36px; object-fit: contain; }
.brand-text { color: #dbe9f1; font-weight: 700; letter-spacing: .3px; }
.nav-links { display: flex; gap: 18px; list-style: none; margin: 0; padding: 0; }
.nav-links a { color: #c8d8e4; text-decoration: none; padding: 8px 6px; border-radius: 8px; }
.nav-links a:hover { background: rgba(255,255,255,0.06); color: #fff; }
.nav-toggle { display: none; background: none; color: #e7f0f6; border: 1px solid rgba(255,255,255,0.15); padding: 6px 10px; border-radius: 8px; }
@media (max-width: 820px) {
  .nav-toggle { display: inline-block; }
  .nav-links { position: absolute; right: 16px; top: 54px; background: #0b0f14; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px; display: none; flex-direction: column; min-width: 180px; }
  .nav-links.show { display: flex; }
}
```

---

## 6) Accessibility & SEO

- **Focus**: visible focus ring on cards and links (see CSS above).  
- **Alt text**: short, content‑based, not a repeat of title.  
- **Skip link**: add `<a href="#main" class="skip">Skip to content</a>` and styles.  
- **Schema**: `ItemList` on list pages; `Article` JSON‑LD on any per‑post summary pages.  
- **Sitemap**: generate from `posts.json` in CI.

**Sitemap generator** (`scripts/sitemap.py`):

```python
from datetime import datetime
import json, os
data = json.load(open("public/data/posts.json", "r", encoding="utf-8"))
urls = [it["url"] for it in data.get("items", []) if it.get("url")]
xml = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
  xml.append(f"<url><loc>{u}</loc><changefreq>weekly</changefreq></url>")
xml.append("</urlset>")
os.makedirs("public", exist_ok=True)
open("public/sitemap.xml","w",encoding="utf-8").write("\n".join(xml))
```

Call `python scripts/sitemap.py` at the end of your Action (after `posts.json` is written).

---

## 7) Validation & QA Checklist

1. **CI run**: Manually trigger the Action; confirm `public/data/posts.json` exists and is non‑empty.  
2. **Network tab**: Home page should only request `/data/posts.json` (no direct RSS fetches).  
3. **Teasers**: Cards show 25–40 words, always end with `...`, and contain none of the banned phrases.  
4. **Zoom/wide screens**: Grid expands to 4–5 columns as width/zoom increases; hero height and typography scale fluidly; content is centered.  
5. **Accessibility**: Visible focus, working skip link, descriptive `alt`.  
6. **SEO**: `sitemap.xml` present; JSON‑LD valid (use Google Rich Results test).

---

## 8) Optional Enhancements

- Client‑side **search** and **topic filters** (filter in‑memory `items` array).  
- A compact **Resources** page if you later add affiliate modules.  
- A **sticky‑on‑scroll** mini‑hero that collapses the big hero into a slim header after scrolling.

---

### File Structure (suggested)

```
/
  public/
    data/posts.json
    sitemap.xml
  scripts/
    ingest_substack.py
    sitemap.py
  .github/workflows/ingest.yml
  assets/
    logo.png
```

This guide is intentionally cohesive: add the Python script, the workflow, the HTML/CSS patches, and you’re done.
