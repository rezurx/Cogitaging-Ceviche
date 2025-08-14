from datetime import datetime
import json, os

def setup_logging():
    """Configure logging for sitemap generation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_posts_data(posts_file="public/data/posts.json"):
    """Load posts data from JSON file."""
    logger = logging.getLogger(__name__)
    
    try:
        if not os.path.exists(posts_file):
            logger.warning(f"Posts file not found: {posts_file}")
            return {"items": []}
        
        with open(posts_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data.get('items', []))} posts from {posts_file}")
            return data
    
    except Exception as e:
        logger.error(f"Error loading posts data: {e}")
        return {"items": []}

def validate_url(url):
    """Validate that URL is properly formatted."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and parsed.netloc
    except Exception:
        return False

def generate_sitemap(posts_data, output_file="public/sitemap.xml", base_domain="https://cogitating-ceviche.com"):
    """Generate sitemap.xml from posts data."""
    logger = logging.getLogger(__name__)
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Start building sitemap
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            '',
            '  <!-- Main site pages -->',
            f'  <url>',
            f'    <loc>{base_domain}/</loc>',
            f'    <changefreq>daily</changefreq>',
            f'    <priority>1.0</priority>',
            f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>',
            f'  </url>',
            f'  <url>',
            f'    <loc>{base_domain}/all/</loc>',
            f'    <changefreq>daily</changefreq>',
            f'    <priority>0.8</priority>',
            f'  </url>',
            f'  <url>',
            f'    <loc>{base_domain}/topics/</loc>',
            f'    <changefreq>weekly</changefreq>',
            f'    <priority>0.7</priority>',
            f'  </url>',
            f'  <url>',
            f'    <loc>{base_domain}/about/</loc>',
            f'    <changefreq>monthly</changefreq>',
            f'    <priority>0.6</priority>',
            f'  </url>',
            '',
            '  <!-- External article links -->',
        ]
        
        # Add posts from JSON data
        valid_urls = 0
        total_items = len(posts_data.get("items", []))
        
        for item in posts_data.get("items", []):
            url = item.get("url", "")
            
            if not url or not validate_url(url):
                logger.debug(f"Skipping invalid URL: {url}")
                continue
            
            # Escape XML entities
            escaped_url = (url.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                            .replace('"', "&quot;")
                            .replace("'", "&apos;"))
            
            xml_lines.extend([
                f'  <url>',
                f'    <loc>{escaped_url}</loc>',
                f'    <changefreq>weekly</changefreq>',
                f'    <priority>0.5</priority>',
                f'  </url>'
            ])
            
            valid_urls += 1
        
        # Close sitemap
        xml_lines.extend([
            '',
            '</urlset>'
        ])
        
        # Write sitemap file
        xml_content = '\n'.join(xml_lines)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        logger.info(f"✅ Sitemap generated successfully:")
        logger.info(f"   - Output: {output_file}")
        logger.info(f"   - Valid URLs: {valid_urls}/{total_items}")
        logger.info(f"   - Size: {len(xml_content)} chars")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating sitemap: {e}")
        return False

def main():
    """Main execution function."""
    logger = setup_logging()
    
    try:
        logger.info("Starting sitemap generation...")
        
        # Load posts data
        posts_data = load_posts_data()
        
        # Generate sitemap
        success = generate_sitemap(posts_data)
        
        if success:
            logger.info("Sitemap generation completed successfully!")
            return 0
        else:
            logger.error("Sitemap generation failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Sitemap generation error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)