# Cloudflare Worker RSS Proxy

This Cloudflare Worker proxies RSS feeds to bypass Substack's blocking of GitHub Actions IPs.

## Deployment Instructions

1. **Install Wrangler CLI** (if not already installed):
   ```bash
   npm install -g wrangler
   ```

2. **Authenticate with Cloudflare**:
   ```bash
   wrangler login
   ```

3. **Deploy the Worker**:
   ```bash
   cd cloudflare-worker
   wrangler deploy
   ```

4. **Get your Worker URL**:
   After deployment, you'll get a URL like:
   `https://cogitating-ceviche-rss-proxy.your-subdomain.workers.dev`

## Usage

Once deployed, update your RSS ingestion script to use the Worker URLs:

```python
SUBSTACK_FEEDS = [
    "https://your-worker.workers.dev/?feed=https://thecogitatingceviche.substack.com/feed",
    "https://your-worker.workers.dev/?feed=https://thecyberneticceviche.substack.com/feed",
]
```

## Testing

Test the Worker locally:
```bash
wrangler dev
```

Then visit:
`http://localhost:8787/?feed=https://thecogitatingceviche.substack.com/feed`

## Security Features

- Only allows proxying of specified Substack feeds
- Adds CORS headers for GitHub Actions
- Includes proper error handling
- Caches responses for 5 minutes to avoid rate limiting