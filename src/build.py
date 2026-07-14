#!/usr/bin/env python3
"""Build static HTML pages for victor-album from fetched data."""

import json
import os
import shutil
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_DIR, "src")
DATA_DIR = os.path.join(SRC_DIR, "data")
DIST_DIR = PROJECT_DIR  # Output to project root for GitHub Pages
CONFIG_PATH = os.path.join(SRC_DIR, "config.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def format_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y年%m月%d日")
    except Exception:
        return date_str[:10]


def format_date_short(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str[:10]


def escape_html(text):
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def ga_snippet(ga_id):
    if not ga_id:
        return ""
    return f"""  <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>"""


def cf_beacon_snippet(token):
    if not token:
        return ""
    return f"""<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v833ccba57c9e4d2798f2e76cebdd09a11778172276447" integrity="sha512-57MDmcccJXYtNnH+ZiBwzC4jb2rvgVCEokYN+L/nLlmO8rfYT/gIpW2A569iJ/3b+0UEasghjuZH/ma3wIs/EQ==" data-cf-beacon='{{"version":"2024.11.0","token":"{token}","r":1}}' crossorigin="anonymous"></script>"""


def generate_index_html(articles, config):
    site_name = config.get("site_name", "Victor42's Album")
    ga_id = config.get("ga_id", "")
    cf_token = config.get("cf_beacon_token", "")
    preview_count = config.get("preview_count", 24)
    ga_head = ga_snippet(ga_id)
    cf_beacon = cf_beacon_snippet(cf_token)

    cards_html = ""
    for article in articles:
        title = escape_html(article["title"])
        date = format_date(article.get("date"))
        slug = article["slug"]
        images = article.get("images", [])
        cover = article.get("cover") or (images[0]["src"] if images else "")
        total = len(images)
        preview_imgs = ""
        for img in images[:preview_count]:
            src = img["src"]
            alt = escape_html(img["alt"])
            preview_imgs += f'          <div class="img-wrap"><img src="{src}" alt="{alt}" loading="lazy"></div>\n'
        cards_html += f"""    <article class="album-card">
      <a href="album/{slug}/" class="album-card-link">
        <div class="album-cover">
          <div class="img-wrap"><img src="{cover}" alt="{title}" loading="lazy"></div>
        </div>
        <div class="album-info">
          <h2 class="album-title">{title}</h2>
          <div class="album-meta">
            <time datetime="{article.get('date', '')}">{date}</time>
            <span class="album-count">{total} 张图片</span>
          </div>
        </div>
      </a>
      <div class="album-preview-wrap">
        <div class="album-preview">
{preview_imgs.rstrip()}        </div>
        <a href="album/{slug}/" class="album-more">查看全部 →</a>
      </div>
    </article>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-scheme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{site_name}</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <meta name="description" content="{config.get('description', '')}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
{ga_head}
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1 class="site-title">{site_name}</h1>
      <p class="site-desc">{config.get('description', '')}</p>
      <button class="theme-toggle" id="themeToggle" aria-label="Toggle dark mode">
        <svg class="icon icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        <svg class="icon icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </header>
  <main class="container">
{cards_html}  </main>
  <footer class="site-footer">
    <p class="copyright">Created by <a href="https://victor42.eth.limo" target="_blank" rel="noopener">Victor42</a> & <a href="https://github.com/agent-vik/about-me" target="_blank" rel="noopener">Vik</a> | <a href="https://github.com/agent-vik/victor-album" target="_blank" rel="noopener">Code</a></p>
  </footer>
  <script src="js/main.js"></script>
{cf_beacon}
</body>
</html>"""
    return html


def generate_album_html(article, config):
    title = escape_html(article["title"])
    slug = article["slug"]
    date = format_date(article.get("date"))
    blog_url = article.get("url", "")
    images = article.get("images", [])
    total = len(images)
    site_name = config.get("site_name", "Victor42's Album")
    ga_id = config.get("ga_id", "")
    cf_token = config.get("cf_beacon_token", "")
    ga_head = ga_snippet(ga_id)
    cf_beacon = cf_beacon_snippet(cf_token)

    images_html = ""
    for img in images:
        src = img["src"]
        alt = escape_html(img["alt"])
        figcaption = f'<figcaption>{alt}</figcaption>' if alt else ''
        images_html += f"""      <figure class="photo-item">
        <div class="img-wrap"><img src="{src}" alt="{alt}" loading="lazy"></div>
        {figcaption}
      </figure>
"""

    cover_img = article.get("cover", "") or (images[0]["src"] if images else "")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-scheme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title} - {site_name}</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <meta name="description" content="{title}，共{total}张图片">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/style.css">
{ga_head}
</head>
<body>
  <header class="album-detail-nav">
    <div class="container album-detail-nav-inner">
      <a href="../../" class="back-link"><svg class="back-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg> 全部相册</a>
      <button class="theme-toggle" id="themeToggle" aria-label="Toggle dark mode">
        <svg class="icon icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        <svg class="icon icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </header>
  <main class="container">
    <article class="album-card album-card--hero">
      <div class="album-card-link album-card-link--hero">
        <div class="album-cover">
          <div class="img-wrap"><img src="{cover_img}" alt="{title}" loading="lazy"></div>
        </div>
        <div class="album-info">
          <h1 class="album-title">{title}</h1>
          <div class="album-meta">
            <time datetime="{article.get('date', '')}">{date}</time>
            <span class="album-count">{total} 张图片</span>
          </div>
        </div>
        <a href="{blog_url}" class="blog-link" target="_blank" rel="noopener">
          <svg class="blog-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          博客原文
        </a>
      </div>
    </article>
    <div class="photo-grid">
{images_html}    </div>
  </main>
  <footer class="site-footer">
    <p class="copyright">Created by <a href="https://victor42.eth.limo" target="_blank" rel="noopener">Victor42</a> & <a href="https://github.com/agent-vik/about-me" target="_blank" rel="noopener">Vik</a></p>
  </footer>
  <script src="../../js/main.js"></script>
{cf_beacon}
</body>
</html>"""
    return html


def main():
    config = load_json(CONFIG_PATH)
    articles = load_json(os.path.join(DATA_DIR, "articles.json"))
    css = load_text(os.path.join(SRC_DIR, "style.css"))
    js = load_text(os.path.join(SRC_DIR, "main.js"))

    for d in ["css", "js", "album"]:
        p = os.path.join(DIST_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p)
    for f in ["index.html"]:
        p = os.path.join(DIST_DIR, f)
        if os.path.exists(p):
            os.remove(p)

    os.makedirs(os.path.join(DIST_DIR, "css"), exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "js"), exist_ok=True)
    for article in articles:
        os.makedirs(os.path.join(DIST_DIR, "album", article["slug"]), exist_ok=True)

    with open(os.path.join(DIST_DIR, "css", "style.css"), "w", encoding="utf-8") as f:
        f.write(css)
    with open(os.path.join(DIST_DIR, "js", "main.js"), "w", encoding="utf-8") as f:
        f.write(js)

    index_html = generate_index_html(articles, config)
    with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    for article in articles:
        album_html = generate_album_html(article, config)
        album_path = os.path.join(DIST_DIR, "album", article["slug"], "index.html")
        with open(album_path, "w", encoding="utf-8") as f:
            f.write(album_html)

    total_images = sum(a["image_count"] for a in articles)
    print(f"\n✓ Built {len(articles)} album pages, {total_images} images total")
    print(f"  Output: {DIST_DIR}")


if __name__ == "__main__":
    main()
