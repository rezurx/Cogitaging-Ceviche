
# Website Updates & Affiliate Integration Guide

## 1. Website Code Updates

### HTML Adjustments
- Ensure `<title>` and `<meta>` descriptions are clear and aligned with SEO goals.
- Add `alt` text to all images for accessibility and SEO.
- Include a `<meta name="description">` tag for better search engine previews.

### CSS Fixes
- Adjust font sizes for better mobile readability.
- Ensure responsive scaling of images and embedded media.
- Improve color contrast for accessibility compliance.

### JavaScript Fixes
- Optimize lazy-loading for images to improve page load speed.
- Add smooth scrolling for navigation anchors.

---

## 2. Subtitle Display Fix
If your subtitles are not showing up, make sure:
1. The subtitle element exists in your HTML:
```html
<h2 class="subtitle">Your subtitle text here</h2>
```
2. Add CSS to make it visible and properly styled:
```css
.subtitle {
  font-size: 1.2em;
  color: #666;
  display: block;
  margin-top: 5px;
}
```
3. If subtitles are dynamically loaded via JavaScript, verify that the script is correctly inserting text into the `.subtitle` class.

---

## 3. Affiliate Strategy Notes

### Amazon Affiliate Setup
- Sign up for Amazon Associates.
- Place affiliate links within relevant articles or reviews.
- Use shortcodes or widgets to embed products neatly.

### Custom Affiliate Opportunities
- **ElevenLabs** — You already have an affiliate link as a paid user. Create your own banner or ad block:
```html
<a href="YOUR_ELEVENLABS_AFFILIATE_LINK" target="_blank">
  <img src="path-to-your-custom-banner.png" alt="Try ElevenLabs">
</a>
```
- Target affiliates related to your two Substack themes for higher conversions.

### Content-Specific Partner Ideas
- **Tech/AI Tools** — affiliate deals for AI writing, image generation, coding assistants.
- **Books & Courses** — affiliate links for books or learning platforms related to your article topics.
- **Specialty Goods** — historical replicas, niche merchandise relevant to your writing themes.

---

## 4. Implementation Tips
- Keep affiliate links contextually relevant to the content they appear in.
- Use tracking IDs for each platform to measure performance.
- Rotate ad placements to avoid banner fatigue.
- Disclose affiliate relationships in a visible but non-intrusive way.

---

## 5. Next Steps
1. Finalize styling for subtitles and other content elements.
2. Select top 3 affiliate programs to integrate first.
3. Implement code changes and test across devices.
4. Track results and adjust placements for better click-through rates.

---
_Last updated: 2025-08-14_
