#!/usr/bin/env python3
"""Fetch image data from blog posts for victor-album using z-ai CLI."""

import json
import re
import subprocess
import time
import os

BLOG_BASE = "https://victor42.eth.limo"
OUTPUT_DIR = "/home/z/my-project/agent-workspace/lab/victor-album/data"

ARTICLES = [
    {"slug": "trip-to-xi-an", "title": "西安初夏休闲6天5夜"},
    {"slug": "trip-to-xishuangbanna", "title": "西双版纳景洪春季休闲6天5夜"},
    {"slug": "trip-to-zhuhai-and-macao", "title": "珠海澳门春节9天8夜"},
    {"slug": "3596", "title": "敦煌自驾5天4夜"},
    {"slug": "3580", "title": "北京4天5夜"},
    {"slug": "inner-mongolia-north-ningxia-self-driving-tour", "title": "蒙西宁夏国庆小众自驾6天5夜"},
    {"slug": "a-revisit-to-dunhuang", "title": "敦煌二刷遛娃5天4夜"},
    {"slug": "1870", "title": "纯净的海"},
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
        # Support both SDK direct format and CLI wrapper format
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
    
    # Find <article> element
    article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if not article_match:
        # Try to find section directly if no article wrapper
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
    
    # Extract all <img> tags
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
    # Also check meta tags
    meta_match = re.search(r'property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']', html)
    if meta_match:
        return meta_match.group(1)
    return None

def extract_cover(html):
    """Extract OG cover image."""
    og_match = re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
    if og_match:
        return og_match.group(1)
    # Try content before property order
    og_match2 = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html)
    if og_match2:
        return og_match2.group(1)
    return None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []
    
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
        
        # Also save raw HTML for reference
        raw_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        result = {
            "slug": slug,
            "title": article["title"],
            "url": url,
            "date": date,
            "cover": cover,
            "images": images,
            "image_count": len(images),
        }
        results.append(result)
        print(f"  Date: {date}, Images: {len(images)}, Cover: {cover}")
        
        time.sleep(0.5)
    
    # Sort by date descending (newest first)
    results.sort(key=lambda x: x.get("date") or "", reverse=True)
    
    print(f"\n=== Summary ===")
    total = 0
    for r in results:
        print(f"  {r['title']}: {r['image_count']} images ({r.get('date', 'no date')})")
        total += r['image_count']
    print(f"  Total: {total} images")
    
    # Save combined data
    output_path = os.path.join(OUTPUT_DIR, "articles.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    main()
