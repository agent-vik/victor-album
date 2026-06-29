#!/usr/bin/env python3
"""Fetch image data from blog posts for victor-album."""

import json
import re
import time
import os
import urllib.request

BLOG_BASE = "https://victor42.eth.limo"
OUTPUT_DIR = "/home/z/my-project/projects/victor-album/src/data"

# Only slugs needed — title, date, cover are auto-fetched from the blog.
ARTICLES = [
    "trip-to-xi-an",
    "trip-to-xishuangbanna",
    "trip-to-zhuhai-and-macao",
    "3596",
    "3580",
    "inner-mongolia-north-ningxia-self-driving-tour",
    "a-revisit-to-dunhuang",
    "1870",
    "zhejiang-surveying-mapping-and-geoinformation-museum",
    "3617",
]

ALT_FILTER_KEYWORDS = [
    "表情包", "搞笑", "恶搞", "简笔", "搞怪",
    "截图", "卡片截图",
    "开支明细", "开支构成", "消费明细",
]


def read_url(url, timeout=30):
    """Read a URL using urllib directly."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def extract_section_images(html):
    """Extract images from <section class=article-content> only, excluding related recommendations."""
    images = []

    # Find article-content section (between <section class=article-content> and <footer class=article-footer>)
    section_match = re.search(
        r'<section[^>]*class=[^>]*article-content[^>]*>(.*?)<footer[^>]*class=[^>]*article-footer',
        html, re.DOTALL
    )
    if not section_match:
        # Fallback: find any <section> within <article>
        article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if article_match:
            section_match = re.search(r'<section[^>]*>(.*?)</section>', article_match.group(1), re.DOTALL)
        if not section_match:
            return images

    content = section_match.group(1)

    # Blog uses unquoted attributes: src=https://... alt=text
    for img_match in re.finditer(r'<img[^>]+>', content):
        tag = img_match.group(0)
        src = re.search(r'src=(https://cdn\.victor42\.work/posts/\S+)', tag)
        alt = re.search(r'alt=([^\s>]+)', tag)
        if src:
            images.append({"src": src.group(1), "alt": alt.group(1) if alt else ""})

    return images


def extract_date(html):
    """Extract publication date. Blog uses unquoted datetime= value."""
    time_match = re.search(r'<time[^>]+datetime=([^\s>]+)', html)
    if time_match:
        return time_match.group(1)
    # Fallback: og meta (may be quoted)
    meta_match = re.search(r'property=["\']article:published_time["\'][^>]*content=([^\s>]+)', html)
    if meta_match:
        return meta_match.group(1)
    return None


def extract_title(html):
    """Extract article title from <title> tag or og:title meta."""
    # <title>标签
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
    if title_match:
        return title_match.group(1).strip()
    # og:title (quoted)
    og_match = re.search(r'property=["\']og:title["\'][^>]*content=["\']([^"\' ]+)["\' ]', html)
    if og_match:
        return og_match.group(1).strip()
    return None


def extract_cover(html):
    """Extract OG cover image. Handles both quoted and unquoted attributes."""
    # Quoted: property="og:image" content="https://..."
    og_match = re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
    if og_match:
        return og_match.group(1)
    og_match2 = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html)
    if og_match2:
        return og_match2.group(1)
    # Unquoted: property="og:image" content=https://...
    og_match3 = re.search(r'property=["\']og:image["\'][^>]*content=(https?://\S+)', html)
    if og_match3:
        return og_match3.group(1)
    return None


def should_filter_by_alt(alt_text):
    """Check if alt text indicates non-photo content."""
    alt_lower = alt_text.lower()
    for keyword in ALT_FILTER_KEYWORDS:
        if keyword.lower() in alt_lower:
            return keyword
    return None


def filter_images(images):
    """Filter out non-photo images by alt text only."""
    kept = []
    filtered_count = 0

    for img in images:
        alt = img.get("alt", "")
        alt_reason = should_filter_by_alt(alt)
        if alt_reason:
            filtered_count += 1
            print(f"    [FILTER] alt '{alt_reason}': {alt[:40]}")
            continue
        kept.append(img)

    return kept, filtered_count


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []
    total_filtered = 0

    for slug in ARTICLES:
        url = f"{BLOG_BASE}/post/{slug}/"
        print(f"\nFetching: {url}")

        html = read_url(url)
        if not html:
            print(f"  FAILED to fetch")
            results.append({
                "slug": slug, "title": slug, "url": url,
                "date": None, "cover": None, "images": [], "image_count": 0,
                "error": "fetch_failed"
            })
            continue

        title = extract_title(html) or slug
        images = extract_section_images(html)
        date = extract_date(html)
        cover = extract_cover(html)

        print(f"  Title: {title}")
        print(f"  Extracted {len(images)} images, filtering...")
        kept_images, filtered_count = filter_images(images)
        total_filtered += filtered_count
        print(f"  Kept {len(kept_images)}/{len(images)} images (filtered {filtered_count})")

        result = {
            "slug": slug,
            "title": title,
            "url": url,
            "date": date,
            "cover": cover,
            "images": kept_images,
            "image_count": len(kept_images),
        }
        results.append(result)

        time.sleep(0.3)

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