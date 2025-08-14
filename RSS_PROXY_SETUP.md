# RSS Proxy Setup Instructions

Your RSS ingestion is failing in GitHub Actions because Substack blocks CI runner IP addresses. The solution is to deploy a Cloudflare Worker proxy.

## 🚨 Current Status
- ✅ Local RSS fetching works perfectly
- ❌ GitHub Actions gets blocked by Substack  
- 🔧 **Solution Ready**: Cloudflare Worker proxy prepared

## Step-by-Step Deployment

### 1. Deploy the Cloudflare Worker

```bash
# Install Wrangler CLI (if needed)
npm install -g wrangler

# Navigate to worker directory  
cd cloudflare-worker

# Login to Cloudflare
wrangler login

# Deploy the worker
wrangler deploy
```

After deployment, you'll get a URL like:
`https://cogitating-ceviche-rss-proxy.your-subdomain.workers.dev`

### 2. Update GitHub Actions

Edit `.github/workflows/ingest.yml` and replace:

```yaml
WORKER_PROXY_URL: ""  # Empty = use direct URLs
```

With your actual Worker URL:

```yaml
WORKER_PROXY_URL: "https://your-actual-worker.workers.dev"
```

### 3. Test the Setup

1. **Test Worker directly**:
   ```bash
   curl "https://your-worker.workers.dev/?feed=https://thecogitatingceviche.substack.com/feed"
   ```

2. **Test script with proxy**:
   ```bash
   WORKER_PROXY_URL="https://your-worker.workers.dev" python3 scripts/ingest_substack_new.py
   ```

3. **Trigger GitHub Actions**:
   - Go to Actions tab in GitHub
   - Run "Ingest Substack feeds" workflow manually
   - Should succeed without 403 errors

## How It Works

**Without Proxy (Current - Fails in CI)**:
```
GitHub Actions → Substack RSS → ❌ 403 Blocked
```

**With Proxy (Solution)**:
```
GitHub Actions → Cloudflare Worker → Substack RSS → ✅ Success
```

## Files Created

- `cloudflare-worker/worker.js` - The proxy code
- `cloudflare-worker/wrangler.toml` - Deployment config
- `scripts/ingest_substack_new.py` - Updated with proxy support
- `.github/workflows/ingest.yml` - Updated with env variable

## Security Features

- Only proxies approved Substack feeds
- Includes CORS headers for GitHub Actions
- 5-minute caching to prevent rate limiting
- Proper error handling

## Next Steps

1. Deploy the Worker using the commands above
2. Update the GitHub Actions workflow with your Worker URL
3. The hourly RSS ingestion will then work automatically

**Estimated Time**: 5-10 minutes to deploy and configure