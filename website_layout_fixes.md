
# Website Update Summary – Layout and Content Fixes

This document compiles all adjustments discussed today in reference to the shared screenshot of the website.

---

## 1. Button Label Clarity
**Issue:** Buttons did not clearly indicate which Substack they came from.  
**Update:**  
- Modify button text to include the originating Substack's name or shorthand (e.g., `Read on Cogitating Ceviche`, `Read on Elephant Island`).  
- Use consistent casing and spacing for all button labels.  
- Apply brand colors or small icon indicators to reinforce source identity.

---

## 2. Stray Text in Article Descriptions
**Issue:** Some article descriptions had leftover text fragments or metadata strings at the beginning.  
**Update:**  
- Strip any leading symbols, HTML tags, or leftover template variables before rendering.  
- Apply a clean text function to all post excerpts before display.

---

## 3. Article Order
**Issue:** Articles were not appearing in chronological order.  
**Update:**  
- Sort posts by published date in descending order before rendering.  
- Ensure date parsing works for both Substack feeds, converting all formats to a consistent datetime object before sorting.

---

## 4. Subtitle Display
**Issue:** Subtitles from articles were not appearing under titles.  
**Update:**  
- Check that the feed parser is retrieving the `subtitle` or `description` field correctly.  
- If a subtitle exists, display it beneath the article title in a smaller, lighter font.  
- Ensure proper truncation for long subtitles, ideally 80–100 characters max.

---

## 5. Layout Consistency
**Update:**  
- Maintain consistent spacing between article cards.  
- Align titles, subtitles, and buttons vertically for a clean look.  
- Ensure images are the same height to prevent uneven card sizes.

---

## 6. Testing and Validation
**Next Steps:**  
- Test changes with both feeds active.  
- Confirm that chronological sorting works across both sources.  
- Verify that all stray text is removed in live display.  
- Confirm subtitle rendering is correct on both desktop and mobile.

---

**Summary:**  
These updates will improve user clarity, make the site more professional-looking, and ensure content is organized and readable. Once implemented, the site should clearly show which Substack each article comes from, display subtitles, and list articles in proper order.
