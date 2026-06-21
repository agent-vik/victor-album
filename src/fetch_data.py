#!/usr/bin/env python3
"""Fetch image data from blog posts for victor-album using z-ai CLI."""

import json
import re
import subprocess
import time
import os
import urllib.request
import io

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Warning: Pillow not available, image size filtering disabled")

BLOG_BASE = "https://victor42.eth.limo"
OUTPUT_DIR = "/tmp/victor-album/src/data"

ARTICLES = [
    {"slug": "trip-to-xi-an", "title": "\u897f\u5b89\u521d\u590f\u4f11\u95f26\u59295\u591c"},
    {"slug": "trip-to-xishuangbanna", "title": "\u897f\u53cc\u7248\u7eb3\u666f\u6d2a\u6625\u5b63\u4f11\u95f26\u59295\u591c"},
    {"slug": "trip-to-zhuhai-and-macao", "title": "\u73e0\u6d77\u6fb3\u95e8\u6625\u82829\u59298\u591c"},
    {"slug": "3596", "title": "\u6566\u714c\u81ea\u9a7e5\u59294\u591c"},
    {"slug": "3580", "title": "\u5317\u4eac4\u59295\u591c"},
    {"slug": "inner-mongolia-north-ningxia-self-driving-tour", "title": "\u8499\u897f\u5b81\u590f\u56fd\u5e86\u5c0f\u4f17\u81ea\u9a7e6\u59295\u591c"},
    {"slug": "a-revisit-to-dunhuang", "title": "\u6566\u714c\u4e8c\u5237\u9041\u5a015\u59294\u591c"},
    {"slug": "1870", "title": "\u7eaf\u51c0\u7684\u6d77"},
    {"slug": "zhejiang-mapping-and-geoinformation-museum", "title": "\u6d59\u6c5f\u6d4b\u7ed8\u4e0e\u5730\u7406\u4fe1\u606f\u79d1\u6280\u535a\u7269\u9986"},
    {"slug": "3617", "title": "\u6d59\u6c5f\u7701\u81ea\u7136\u535a\u7269\u9986\u5b89\u5409\u9986"},
]

# Alt text keywords for non-photo content (stickers, memes, screenshots, tables)
ALT_FILTER_KEYWORDS = [
    "\u8868\u60c5\u5305", "\u641e\u7b11", "\u6076\u641e", "\u7b80\u7b14", "\u641e\u602a",
    "\u622a\u56fe", "\u5361\u7247\u622a\u56fe",
    "\u5f00\u652f\u660e\u7ec6", "\u5f00\u652f\u6784\u6210", "\u6d88\u8d39\u660e\u7ec6",
]

def read_url(url):
    """Read a URL using z-ai CLI page_reader."""
    out_file = "/tmp/web_reader_temp.json"
    result = subprocess.run(
        ["z-ai", "function", "-n", "page_reader", "-a", json.dumps({"url": url}), "-o", out_file],
        capture_output=True, text=True, timeout=120
    )
    if not os.path.exists(out_file):
        print(f"  Error: no output file. stderr: {result.stderr[:200]}")
        return None
    try:
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            if data.get("code") == 200 and data.get("data", {}).get("html"):
                return data["data"]["html"]
            elif data.get("html"):
                return data["html"]
            elif data.get("data", {}).get("html"):
                return data["data"]["html"]
        return None
    except (json.JSONDecodeError, IOError) as e:
        print(f"  Error parsing output: {e}")
        return None
    finally:
        if os.path.exists(out_file):
            os.remove(out_file)

def extract_section_images(html):
    """Extract images from article <section> content only."""
    images = []
    
    article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if not article_match:
        section_match = re.search(r'<section[^>]*>(.*?)</section>', html, re.DOTALL)
        if section_match:
            content = section_match.group(1)
        else:
            return images
    else:
        article_html = article_match.group(1)
        section_match = re.search(r'<section[^>]*>(.*?)</section>', article_html, re.DOTALL)
        if section_match:
            content = section_match.group(1)
        else:
            content = article_html
    
    for img_match in re.finditer(r'<img[^>]+>', content):
        tag = img_match.group(0)
        src = re.search(r'src=["\']([^"\']+)["\']', tag)
        alt = re.search(r'alt=["\']([^"\']*)["\']', tag)
        if src:
            img_src = src.group(1)
            if "cdn.victor42.work/posts/" in img_src:
                images.append({"src": img_src, "alt": alt.group(1) if alt else ""})
    
    return images

def extract_date(html):
    """Extract publication date."""
    time_match = re.search(r'<time[^>]+datetime=["\']([^"\']+)["\']', html)
    if time_match:
        return time_match.group(1)
    meta_match = re.search(r'property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']', html)
    if meta_match:
        return meta_match.group(1)
    return None

def extract_cover(html):
    """Extract OG cover image."""
    og_match = re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
    if og_match:
        return og_match.group(1)
    og_match2 = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html)
    if og_match2:
        return og_match2.group(1)
    return None

def download_image(url, timeout=10):
    """Download image and return PIL Image, or None on failure."""
    if not HAS_PILLOW:
        return None
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        return Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        return None

def check_image_size(url):
    """Check image dimensions. Returns filter reason if should filter, or None."""
    if not HAS_PILLOW:
        return None
    img = download_image(url)
    if img is None:
        return None
    w, h = img.size
    min_dim = min(w, h)
    aspect = max(w, h) / max(min_dim, 1)
    # Extremely small image (likely icon/sticker without descriptive alt)
    if min_dim < 150:
        return f"tiny image ({w}x{h})"
    # Extremely elongated (likely table/infographic without descriptive alt)
    if aspect > 5.0:
        return f"extreme aspect ratio {aspect:.1f} ({w}x{h})"
    return None

def should_filter_by_alt(alt_text):
    """Check if alt text indicates non-photo content."""
    alt_lower = alt_text.lower()
    for keyword in ALT_FILTER_KEYWORDS:
        if keyword.lower() in alt_lower:
            return keyword
    return None

def filter_images(images):
    """Filter out non-photo images. Returns (kept_images, filtered_count)."""
    kept = []
    filtered_count = 0
    
    for img in images:
        alt = img.get("alt", "")
        src = img.get("src", "")
        
        # Check alt text first (fast, no download needed)
        alt_reason = should_filter_by_alt(alt)
        if alt_reason:
            filtered_count += 1
            print(f"    [FILTER] alt '{alt_reason}': {alt[:40]}")
            continue
        
        # Check image dimensions (requires download)
        size_reason = check_image_size(src)
        if size_reason:
            filtered_count += 1
            print(f"    [FILTER] {size_reason}: {alt[:40]}")
            continue
        
        kept.append(img)
    
    return kept, filtered_count

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []
    total_filtered = 0
    
    for article in ARTICLES:
        slug = article["slug"]
        url = f"{BLOG_BASE}/post/{slug}/"
        print(f"\nFetching: {article['title']} ({url})")
        
        html = read_url(url)
        if not html:
            print(f"  FAILED to fetch")
            results.append({
                "slug": slug, "title": article["title"], "url": url,
                "date": None, "cover": None, "images": [], "image_count": 0,
                "error": "fetch_failed"
            })
            continue
        
        images = extract_section_images(html)
        date = extract_date(html)
        cover = extract_cover(html)
        
        # Filter non-photo images
        print(f"  Extracted {len(images)} images, filtering...")
        kept_images, filtered_count = filter_images(images)
        total_filtered += filtered_count
        print(f"  Kept {len(kept_images)}/{len(images)} images (filtered {filtered_count})")
        
        raw_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        result = {
            "slug": slug,
            "title": article["title"],
            "url": url,
            "date": date,
            "cover": cover,
            "images": kept_images,
            "image_count": len(kept_images),
        }
        results.append(result)
        
        time.sleep(0.5)
    
    results.sort(key=lambda x: x.get("date") or "", reverse=True)
    
    print(f"\n=== Summary ===")
    total = 0
    for r in results:
        print(f"  {r['title']}: {r['image_count']} images ({r.get('date', 'no date')})")
        total += r['image_count']
    print(f"  Total: {total} images (filtered {total_filtered})")
    
    output_path = os.path.join(OUTPUT_DIR, "articles.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    main()
