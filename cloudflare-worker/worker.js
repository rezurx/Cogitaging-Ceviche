// Cloudflare Worker to proxy RSS feeds and bypass Substack blocking
// Deploy this to Cloudflare Workers to proxy RSS requests

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetFeed = url.searchParams.get("feed");
    
    if (!targetFeed) {
      return new Response("Missing ?feed= parameter", { 
        status: 400,
        headers: { "Content-Type": "text/plain" }
      });
    }
    
    // Validate that we're only proxying allowed Substack feeds
    const allowedFeeds = [
      "https://thecogitatingceviche.substack.com/feed",
      "https://thecyberneticceviche.substack.com/feed"
    ];
    
    if (!allowedFeeds.includes(targetFeed)) {
      return new Response("Feed not allowed", { 
        status: 403,
        headers: { "Content-Type": "text/plain" }
      });
    }
    
    try {
      // Fetch the RSS feed with headers that work well with Substack
      const response = await fetch(targetFeed, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
          "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
          "Accept-Language": "en-US,en;q=0.5",
          "Cache-Control": "no-cache"
        }
      });
      
      const body = await response.text();
      
      // Return the RSS content with CORS headers for GitHub Actions
      return new Response(body, {
        status: response.status,
        headers: {
          "Content-Type": response.headers.get("content-type") || "application/rss+xml",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          "Cache-Control": "public, max-age=300" // Cache for 5 minutes
        }
      });
      
    } catch (error) {
      return new Response(`Error fetching feed: ${error.message}`, {
        status: 500,
        headers: { 
          "Content-Type": "text/plain",
          "Access-Control-Allow-Origin": "*"
        }
      });
    }
  }
};