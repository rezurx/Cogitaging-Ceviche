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
print(f"Generated sitemap with {len(urls)} URLs")