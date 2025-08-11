#!/usr/bin/env python3

import os
import feedparser
import requests
import re
import json
from urllib.parse import urlparse, urljoin
from datetime import datetime
from bs4 import BeautifulSoup

# --- Configuration ---
HUGO_CONTENT_PATH = "content/external-articles"

# Define sources, separating by type (RSS vs. Scrape)
SOURCES = {
    "cogitating-ceviche": {
        "type": "rss",
        "url": "https://thecogitatingceviche.substack.com/feed"
    },
    "cybernetic-ceviche": {
        "type": "rss",
        "url": "https://thecyberneticceviche.substack.com/feed"
    },
    "vocal": {
        "type": "scrape",
        "url": "https://vocal.media/authors/conrad-hannon"
    }
}

# --- Helper Functions ---
def slugify(text):
    """
    Converts text to a URL-friendly slug.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text

def get_existing_article_links(content_path):
    """
    Scans the content directory to find all existing canonical URLs to avoid duplicates.
    """
    existing_links = set()
    if not os.path.exists(content_path):
        return existing_links
    for root, _, files in os.walk(content_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    match = re.search(r'canonicalUrl\s*=\s*"(.*?)"', content)
                    if match:
                        existing_links.add(match.group(1))
    return existing_links

# --- Scraper for Vocal ---
def scrape_vocal_page(url):
    """
    Scrapes a Vocal author page by parsing the __NEXT_DATA__ JSON object.
    """
    print(f"  Scraping Vocal page: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        next_data_script = soup.find('script', id='__NEXT_DATA__')
        if not next_data_script:
            print("  Warning: Could not find __NEXT_DATA__ script tag. The site structure may have changed.")
            return []

        next_data = json.loads(next_data_script.string)
        apollo_state = next_data.get('props', {}).get('pageProps', {}).get('apolloState', {})

        resolved_entries = []
        # Iterate through all items in apolloState to find post references
        for key, value in apollo_state.items():
            if key.startswith('Post:'):
                post = value
                title = post.get('name', 'No Title')
                slug = post.get('slug')
                
                # Correctly find the community (vocalSite) reference and extract its slug
                community_ref = post.get('vocalSite', {}).get('__ref')
                community_slug = apollo_state.get(community_ref, {}).get('slug', 'stories') if community_ref else 'stories'

                link = urljoin(url, f"/{community_slug}/{slug}")
                summary = post.get('summary', 'No Summary Available.')
                
                # Convert timestamp to a readable date format if necessary
                published_timestamp = post.get('publishedAt')
                if published_timestamp:
                    published = datetime.fromtimestamp(published_timestamp / 1000).strftime("%a, %d %b %Y %H:%M:%S GMT")
                else:
                    published = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

                entry = {
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published': published
                }
                resolved_entries.append(entry)

        print(f"  Found {len(resolved_entries)} articles on Vocal page.")
        return resolved_entries

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"  Error scraping Vocal page: {e}")
        return []


# --- Scraper for Substack ---
def get_substack_preview(url):
    """
    Fetches the full article from a Substack URL and returns a ~100 word preview.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Substack article bodies are often in a div with a class like 'available-content' or 'post-content'.
        # This is brittle and may need adjustment if Substack changes their layout.
        article_body = soup.find('div', class_=re.compile(r'post-content|available-content|body|single-post-body'))

        if not article_body:
            article_body = soup.find('article') # Fallback

        if article_body:
            text = article_body.get_text(separator=' ', strip=True)
            words = text.split()
            preview = ' '.join(words[:100])
            if len(words) > 100:
                preview += '...'
            return preview
        else:
            print(f"  Warning: Could not find article body in {url}. Using default summary.")
            return None # Indicates scraping failed to find content

    except requests.exceptions.RequestException as e:
        print(f"  Warning: Could not fetch Substack article at {url}: {e}")
        return None


# --- Main Script ---
def main():
    print("Starting ingestion of external articles...")

    script_dir = os.path.dirname(__file__)
    hugo_content_dir = os.path.join(script_dir, HUGO_CONTENT_PATH)
    os.makedirs(hugo_content_dir, exist_ok=True)

    existing_links = get_existing_article_links(hugo_content_dir)
    print(f"Found {len(existing_links)} existing articles.")

    for source_name, source_data in SOURCES.items():
        source_type = source_data["type"]
        source_url = source_data["url"]
        print(f"\nFetching articles from {source_name.capitalize()} ({source_url})...")

        entries = []
        try:
            if source_type == "rss":
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(source_url, headers=headers)
                response.raise_for_status()
                feed = feedparser.parse(response.content.decode('utf-8'))
                if feed.bozo:
                    print(f"  Warning: Malformed RSS feed for {source_name}: {feed.bozo_exception}")
                entries = feed.entries
            elif source_type == "scrape":
                entries = scrape_vocal_page(source_url)

            for entry in entries:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                published = entry.get('published', datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
                summary = entry.get('summary', 'No Summary Available.')
                featured_image = ''
                
                # Extract featured image from RSS if available
                if hasattr(entry, 'media_content') and entry.media_content:
                    featured_image = entry.media_content[0]['url'] if entry.media_content[0].get('url') else ''
                elif hasattr(entry, 'enclosures') and entry.enclosures:
                    for enclosure in entry.enclosures:
                        if enclosure.get('type', '').startswith('image/'):
                            featured_image = enclosure.get('href', '')
                            break

                if not link or link in existing_links:
                    if link:
                        print(f"  Skipping existing article: {title}")
                    continue

                # Clean and truncate summary for all RSS entries
                summary_cleaned = BeautifulSoup(summary, 'lxml').get_text(separator=' ', strip=True)
                words = summary_cleaned.split()
                if len(words) > 100:
                    summary_cleaned = ' '.join(words[:100]) + '...'

                if source_name in ["cogitating-ceviche", "cybernetic-ceviche"]:
                    print(f"  Fetching enhanced preview for Substack article: {title}")
                    enhanced_preview = get_substack_preview(link)
                    if enhanced_preview:
                        summary_cleaned = enhanced_preview

                slug = slugify(title)
                file_name = f"{slug}.md"
                file_path = os.path.join(hugo_content_dir, file_name)

                counter = 1
                while os.path.exists(file_path):
                    file_name = f"{slug}-{counter}.md"
                    file_path = os.path.join(hugo_content_dir, file_name)
                    counter += 1

                # Build the front matter
                front_matter = f"""+++
title = "{title.replace('"', '"')}"
date = "{published}"
draft = false
canonicalUrl = "{link}"
source = "{source_name.capitalize()}"
slug = "{slug}"""

                # Add featured image if available
                if featured_image:
                    front_matter += f'\nfeatured_image = "{featured_image}"'
                
                front_matter += "\n+++\n"

                markdown_content = f"{front_matter}\n{summary_cleaned}\n"

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                print(f"  Successfully ingested: {title}")
                existing_links.add(link)

        except Exception as e:
            print(f"Error processing source {source_name}: {e}")

    print("\nArticle ingestion complete.")

if __name__ == "__main__":
    main()
