# Cogitating Ceviche – Site Build Spec

This spec lays out every required component for **The Cogitating Ceviche** site, why it matters, and the guiding SEO principles.  
It assumes the root author domain **conradthannon.com** with either:

* a dedicated domain `cogitatingceviche.com`, or  
* a clean path `conradthannon.com/ceviche`.

---

## 🔑 Core Goals

| Goal | Outcome |
|------|---------|
| **Author authority** | All Substack / Medium / Vocal essays inherit one canonical author entity in Google. |
| **Fast, secure, lightweight** | Static build (< 250 KB CSS+JS total) on Netlify/Vercel with automatic HTTPS (Let’s Encrypt). |
| **Zero-leak pseudonymity** | No real-name platforms; Git repo and analytics avoid personal data. |
| **Automated content flow** | Publish in Substack → RSS bot opens PR → static site redeploys with proper canonical tags. |

---

## 🏗 Build Checklist

| # | Requirement | Why it matters |
|---|-------------|----------------|
| 1 | **Domain & DNS** – `conradthannon.com` + optional `cogitatingceviche.com` (301 → root) | One home base for search crawlers; short redirect for spoken promos. |
| 2 | **Static-site generator** – Hugo, Astro, or Next.js SSG | Blazing load times, no database, easy Git workflows. |
| 3 | **SSL (HTTPS)** via Let’s Encrypt | Ranking signal and removes browser warnings. |
| 4 | **Minimal theme** with dark-mode toggle | Lets satire and essays take center stage; reduces bloat. |
| 5 | **Content structure** | `/essays`, `/quick-bites`, `/about`, `/archive` – mirrors reader intent and aids crawl depth. |
| 6 | **Article template extras**<br>• `<link rel="canonical">` (points to original Substack/Medium URL)<br>• JSON-LD `schema.org/Article` (author = "Conrad T. Hannon")<br>• Open Graph + Twitter card meta | Prevents duplicate-content penalties, earns rich snippets, improves social previews. |
| 7 | **Newsletter capture** – embedded Substack or MailerLite form | Converts casual visitors into loyal readers; algorithm-proof traffic. |
| 8 | **RSS feed** (auto from generator) | Powers cross-posting bots and reader apps. |
| 9 | **Privacy-friendly analytics** – Plausible/Fathom/Matomo | Tracks engagement without tying back to a real identity or using cookies. |
|10 | **Automation hooks**<br>• GitHub repo with CI (Netlify build on push)<br>• RSS-to-PR script or n8n flow | Publish once, redeploy everywhere with canonical intact. |
|11 | **Legal & trust pages** – Privacy, Terms, Contact (alias e-mail) | Required for ad networks and professional appearance. |
|12 | **Brand kit** – logo, favicon, social-card background | Consistent visuals across site, X, Mastodon, Reddit. |
|13 | **Performance budget** – images ≤ 150 KB, CSS/JS ≤ 100 KB | Faster load → lower bounce → better rankings. |
|14 | **Back-link section** – footer links to Vocal, Medium, podcast guest spots | Feeds authority back to the root; gives humans an easy path to more work. |
|15 | **Backup/versioning** – Git is the source of truth; enable automatic daily snapshots | One-click rollback if anything breaks. |

---

## 🚀 Deployment Flow

1. **Write** in Substack (or markdown locally).  
2. **RSS bot** detects new post → converts to markdown → opens PR in GitHub.  
3. **Review & merge** → Netlify/Vercel builds static site with canonical tag pointing back to the Substack URL.  
4. **Site redeploys** in under a minute, search engines crawl updated pages automatically.  

---

## 📌 SEO Principles to Observe

* Use dashes between words in long URLs for readability and proper tokenization.  
* Keep one canonical URL per article (static copy points to the origin).  
* Ensure every page is reachable within ≤3 clicks from the homepage.  
* Include `schema.org/Person` on the root domain so Google Knowledge Graph ties all writing back to *Conrad T. Hannon*.  
* Compress images, defer non-critical JS, and preload fonts to hit < 1 s Largest Contentful Paint.  

---

## 👉 Next Steps for Gemini CLI

1. Scaffold a Hugo (or Astro) project with the directories above.  
2. Generate base templates for article pages incorporating canonical and JSON-LD blocks.  
3. Wire Netlify deploy settings and Let’s Encrypt certificate.  
4. Stub an RSS-to-PR script (Python + GitHub API) to automate content imports.  
5. Add a sample newsletter popup using Substack’s embed code.

Once these pieces land, the site will rank cleanly, stay lightning-fast, and keep your pseudonym insulated from real-ID networks—all while funneling new readers into channels you control.
