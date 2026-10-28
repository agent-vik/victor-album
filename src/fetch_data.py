#!/usr/bin/env python3
"""Fetch image data from blog posts for victor-album."""

import json
import os
import time
import urllib.request

from bs4 import BeautifulSoup

BLOG_BASE = "https://victor42.eth.limo"
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SRC_DIR, "data")

ARTICLES = [
    "yunhe-terraces-she-township-self-driving-tour",
    "trip-to-weihai",
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
    "trip-to-jinyun-xiandu",
    "trip-to-zhoushan",
]

ALT_FILTER_KEYWORDS = [
    "表情包", "搞笑", "恶搞", "简笔", "搞怪",
    "截图", "卡片截图",
    "开支明细", "开支构成", "消费明细",
    # 实测漏网变体（2026-10-23 审计）："开支分类构成"绕过"开支构成"、"账单明细"绕过"消费明细"
    "开支分类构成", "账单明细",
    # 实测漏网变体（2026-10-28 审计）：云和"按…分类的构成条形图"不含任何开支类词。
    # 图表类型词不依赖措辞组合；副作用排查：2462 条 alt 语料中命中 4 处
    # （1 漏网 + 2 已过滤开支图 + 0 正常照片），零误伤
    "条形图",
]


def read_url(url, timeout=30):
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
    soup = BeautifulSoup(html, "html.parser")
    images = []
    section = soup.find("section", class_="article-content")
    if not section:
        article = soup.find("article")
        if article:
            section = article.find("section")
    if not section:
        return images
    for img in section.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt", "")
        if src.startswith("https://cdn.victor42.work/posts/"):
            images.append({"src": src, "alt": alt})
    return images


def extract_date(html):
    soup = BeautifulSoup(html, "html.parser")
    time_tag = soup.find("time")
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"]
    meta = soup.find("meta", attrs={"property": "article:published_time"})
    if meta and meta.get("content"):
        return meta["content"]
    return None


def extract_title(html):
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        return og_title["content"].strip()
    return None


def extract_cover(html):
    soup = BeautifulSoup(html, "html.parser")
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and og_image.get("content"):
        return og_image["content"]
    return None


def should_filter_by_alt(alt_text):
    alt_lower = alt_text.lower()
    for keyword in ALT_FILTER_KEYWORDS:
        if keyword.lower() in alt_lower:
            return keyword
    return None


def filter_images(images):
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
