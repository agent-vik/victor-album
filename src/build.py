#!/usr/bin/env python3
"""Build static HTML pages for victor-album from fetched data."""

import json
import os
import re
import shutil
from datetime import datetime
from urllib.parse import quote

PROJECT_DIR = "/home/z/my-project/victor-album"
SRC_DIR = os.path.join(PROJECT_DIR, "src")
DATA_DIR = os.path.join(SRC_DIR, "data")
DIST_DIR = PROJECT_DIR  # Output to project root for GitHub Pages
CONFIG_PATH = os.path.join(SRC_DIR, "config.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_date(date_str):
    """Format ISO date to readable string."""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y年%m月%d日")
    except:
        return date_str[:10]

def format_date_short(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except:
        return date_str[:10]

def escape_html(text):
    """Escape HTML special characters."""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))

def generate_index_html(articles, config):
    """Generate the homepage with article list."""
    site_name = config.get("site_name", "Victor42's Album")
    ga_head = '''  <script async src="https://www.googletagmanager.com/gtag/js?id=G-14SGRFWENB"></script>\n  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-14SGRFWENB');</script>'''
    cf_beacon = '''<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v833ccba57c9e4d2798f2e76cebdd09a11778172276447" integrity="sha512-57MDmcccJXYtNnH+ZiBwzC4jb2rvgVCEokYN+L/nLlmO8rfYT/gIpW2A569iJ/3b+0UEasghjuZH/ma3wIs/EQ==" data-cf-beacon='{\"version\":\"2024.11.0\",\"token\":\"a5a3e66d648b4ae8bc4356f1a342256e\",\"r\":1}' crossorigin="anonymous"></script>'''
    preview_count = config.get("preview_count", 24)
    
    cards_html = ""
    for article in articles:
        title = escape_html(article["title"])
        date = format_date(article.get("date"))
        date_short = format_date_short(article.get("date"))
        slug = article["slug"]
        images = article.get("images", [])
        cover = article.get("cover") or (images[0]["src"] if images else "")
        total = len(images)
        
        # Preview images (grid)
        preview_imgs = ""
        for img in images[:preview_count]:
            src = img["src"]
            alt = escape_html(img["alt"])
            preview_imgs += f'          <div class="img-wrap"><img src="{src}" alt="{alt}" loading="lazy"></div>\n'
        
        cards_html += f'''    <article class="album-card">
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
'''

    html = f'''<!DOCTYPE html>
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
</html>'''
    
    return html

def generate_album_html(article, config):
    """Generate a detail page for one album."""
    title = escape_html(article["title"])
    slug = article["slug"]
    date = format_date(article.get("date"))
    blog_url = article.get("url", "")
    images = article.get("images", [])
    total = len(images)
    site_name = config.get("site_name", "Victor42's Album")
    ga_head = '''  <script async src="https://www.googletagmanager.com/gtag/js?id=G-14SGRFWENB"></script>\n  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-14SGRFWENB');</script>'''
    cf_beacon = '''<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v833ccba57c9e4d2798f2e76cebdd09a11778172276447" integrity="sha512-57MDmcccJXYtNnH+ZiBwzC4jb2rvgVCEokYN+L/nLlmO8rfYT/gIpW2A569iJ/3b+0UEasghjuZH/ma3wIs/EQ==" data-cf-beacon='{\"version\":\"2024.11.0\",\"token\":\"a5a3e66d648b4ae8bc4356f1a342256e\",\"r\":1}' crossorigin="anonymous"></script>'''
    
    # Masonry images
    images_html = ""
    for i, img in enumerate(images):
        src = img["src"]
        alt = escape_html(img["alt"])
        images_html += f'''      <figure class="photo-item">
        <div class="img-wrap"><img src="{src}" alt="{alt}" loading="lazy"></div>
        {f'<figcaption>{alt}</figcaption>' if alt else ''}
      </figure>
'''
    
    cover_img = article.get("cover", "") or (images[0]["src"] if images else "")
    
    html = f'''<!DOCTYPE html>
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
          <div class="img-wrap"><img src="{cover_img}" alt="{title}" loading="eager"></div>
        </div>
        <div class="album-info">
          <h1 class="album-title">{title}</h1>
          <div class="album-meta">
            <time datetime="{article.get('date', '')}">{date}</time>
            <span class="album-count">{total} 张图片</span>
          </div>
        </div>
        <a href="{blog_url}" class="blog-link" target="_blank" rel="noopener"><svg class="blog-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg> 阅读原文</a>
      </div>
    </article>
    <div class="photo-grid">
{images_html}    </div>
  </main>
  <footer class="site-footer">
    <p class="copyright">Created by <a href="https://victor42.eth.limo" target="_blank" rel="noopener">Victor42</a> & <a href="https://github.com/agent-vik/about-me" target="_blank" rel="noopener">Vik</a> | <a href="https://github.com/agent-vik/victor-album" target="_blank" rel="noopener">Code</a></p>
  </footer>
  <script src="../../js/main.js"></script>
{cf_beacon}
</body>
</html>'''
    
    return html

def generate_css():
    """Generate the stylesheet matching the blog's visual style."""
    return ''':root {
  --bg: #f5f5fa;
  --bg-secondary: #ededf2;
  --bg-card: #fff;
  --text: #000;
  --text-secondary: #747474;
  --text-muted: #bababa;
  --border: rgba(218,218,218,0.5);
  --accent: #2A9D8F;
  --accent-darker: #219789;
  --accent-text: #fff;
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
  --shadow-hover: 0 4px 16px rgba(0,0,0,0.12);
  --radius: 10px;
  --transition: 0.25s ease;
  --font-sys: -apple-system, BlinkMacSystemFont, "Segoe UI", "Droid Sans", "Helvetica Neue";
  --font-zh: "PingFang SC", "Hiragino Sans GB", "Droid Sans Fallback", "Microsoft YaHei";
  --font-main: "Lato", var(--font-sys), var(--font-zh), sans-serif;
}

[data-scheme=dark] {
  --bg: #303030;
  --bg-secondary: #3a3a3a;
  --bg-card: #424242;
  --text: rgba(255,255,255,0.9);
  --text-secondary: rgba(255,255,255,0.7);
  --text-muted: rgba(255,255,255,0.5);
  --border: rgba(255,255,255,0.12);
  --accent: #ecf0f1;
  --accent-darker: #bdc3c7;
  --accent-text: #000;
  --shadow: 0 2px 8px rgba(0,0,0,0.25);
  --shadow-hover: 0 4px 16px rgba(0,0,0,0.35);
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-main);
  font-weight: 400;
  line-height: 1.6;
  color: var(--text);
  background-color: var(--bg);
  transition: background-color var(--transition), color var(--transition);
}

a {
  color: var(--accent);
  text-decoration: none;
  transition: color var(--transition);
}

a:hover {
  color: var(--accent);
  opacity: 0.8;
}

img {
  display: block;
  max-width: 100%;
  height: auto;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ===== Header ===== */
.site-header {
  padding: 48px 0 32px;
  margin-bottom: 32px;
}

.site-header .container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.site-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text);
}

.site-desc {
  color: var(--text-secondary);
  font-weight: 300;
  font-size: 0.9rem;
  flex: 1;
  text-align: right;
}

/* ===== Theme Toggle ===== */
.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition);
  flex-shrink: 0;
}

.theme-toggle:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.icon-moon { display: none; }
.icon-sun { display: block; }
[data-scheme=dark] .icon-moon { display: block; }
[data-scheme=dark] .icon-sun { display: none; }

/* ===== Album Card (shared by homepage & detail) ===== */
.album-card {
  margin-bottom: 24px;
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: box-shadow var(--transition);
}

.album-card:hover {
  box-shadow: var(--shadow-hover);
}

.album-card-link {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  color: var(--text);
  text-decoration: none;
}

.album-card-link:hover {
  color: var(--text);
  opacity: 1;
}

.album-cover {
  width: 120px;
  height: 67.5px;
  border-radius: 34px;
  overflow: hidden;
  flex-shrink: 0;
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.album-info {
  flex: 1;
  min-width: 0;
}

.album-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.album-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}

/* ===== Preview Grid ===== */
.album-preview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  padding: 4px;
}

.album-preview img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 2px;
}

.album-preview-wrap {
  position: relative;
  overflow: hidden;
}

.album-more {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 40px 0 12px;
  color: var(--accent);
  font-size: 0.9rem;
  font-weight: 700;
  text-decoration: none;
  background: linear-gradient(to bottom, transparent, var(--bg-card) 60%);
  transition: padding var(--transition);
}

.album-more:hover {
  color: var(--accent-darker, var(--accent));
  opacity: 1;
  padding: 48px 0 12px;
}

/* ===== Album Detail Nav ===== */
.album-detail-nav {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: var(--bg);
}

.album-detail-nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  padding-bottom: 12px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: var(--text-muted);
  text-decoration: none;
}

.back-icon {
  flex-shrink: 0;
  vertical-align: middle;
}

.back-link:hover {
  color: var(--accent);
}

/* ===== Album Hero Card (detail page) ===== */
.album-card--hero {
  margin-top: 24px;
  margin-bottom: 24px;
}

.album-card-link--hero {
  cursor: default;
  padding: 32px 24px;
  gap: 8px;
}

.blog-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background-color: #2A9D8F;
  color: #fff;
  border-radius: var(--radius);
  text-decoration: none;
  font-size: 0.85rem;
  white-space: nowrap;
  transition: opacity var(--transition);
}

.blog-link:hover {
  opacity: 0.85;
}

.blog-icon {
  flex-shrink: 0;
  vertical-align: middle;
}

.album-card-link--hero .blog-link {
  margin-left: auto;
}

/* ===== Photo Masonry Grid ===== */
.photo-grid {
  display: flex;
  gap: 12px;
  visibility: hidden;
  height: 0;
  overflow: hidden;
}

.photo-grid.is-ready {
  visibility: visible;
  height: auto;
  overflow: visible;
}

.photo-grid-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 80px 0;
  color: var(--text-muted);
}

.photo-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.photo-item {
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-card);
  box-shadow: var(--shadow);
  cursor: pointer;
}

.photo-item img {
  width: 100%;
  display: block;
}

.photo-item figcaption {
  padding: 10px 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* ===== Footer ===== */
.site-footer {
  margin-top: 48px;
  padding: 24px 0;
  border-top: 1px solid var(--border);
  text-align: center;
}

.site-footer .copyright {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.site-footer .copyright a {
  color: var(--text-secondary);
}

/* ===== Image Loading Shimmer ===== */
.img-wrap {
  position: relative;
  overflow: hidden;
  background: var(--shimmer-bg, #e8e8e8);
}

.img-wrap img {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.img-wrap img.is-loaded {
  opacity: 1;
}

.img-wrap::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--shimmer-highlight, rgba(255,255,255,0.4)) 50%,
    transparent 100%
  );
  animation: shimmer 1.5s infinite;
  pointer-events: none;
}

.img-wrap.is-loaded::after {
  display: none;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

[data-scheme=dark] .img-wrap {
  --shimmer-bg: #2a2a2a;
  --shimmer-highlight: rgba(255,255,255,0.08);
}

.album-preview .img-wrap {
  aspect-ratio: 1;
}

.album-cover .img-wrap {
  aspect-ratio: 3 / 2;
}

.photo-item .img-wrap {
  aspect-ratio: auto;
  min-height: 120px;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .album-preview {
    grid-template-columns: repeat(4, 1fr);
  }
  
.photo-grid {
    flex-direction: column;
  }

  .photo-col {
    flex: none;
  }
  
  .album-card-link {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }

  .album-cover {
    width: 160px;
    height: 90px;
    border-radius: 45px;
  }

  .album-meta {
    justify-content: center;
  }

  .site-header .container {
    flex-direction: column;
    text-align: center;
  }

  .site-desc {
    text-align: center;
  }

  .album-card-link--hero {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }

  .album-card-link--hero .blog-link {
    margin-left: 0;
    align-self: center;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .album-preview {
    grid-template-columns: repeat(6, 1fr);
  }
  
  .photo-grid {
    flex-direction: row;
  }
}

@media (min-width: 1025px) {
  .album-preview {
    grid-template-columns: repeat(8, 1fr);
  }
  
  .photo-grid {
    flex-direction: row;
  }
}
/* ===== Lightbox ===== */
.lightbox {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 100;
  background: rgba(0, 0, 0, 0.92);
  display: none;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
}

.lightbox.is-open {
  display: flex;
}

.lightbox img {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: var(--radius);
  cursor: default;
}

.lightbox-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  line-height: 1;
}

.lightbox-close:hover {
  background: rgba(255, 255, 255, 0.25);
}

.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-nav:hover {
  background: rgba(255, 255, 255, 0.25);
}

.lightbox-prev {
  left: 16px;
}

.lightbox-next {
  right: 16px;
}

.lightbox-caption {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  max-width: 80vw;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .lightbox img {
    max-width: 95vw;
    max-height: 85vh;
  }
  .lightbox-nav {
    width: 36px;
    height: 36px;
  }
  .lightbox-prev {
    left: 8px;
  }
  .lightbox-next {
    right: 8px;
  }
  .lightbox-caption {
    font-size: 0.8rem;
    bottom: 12px;
  }
}
'''

def generate_js():
    """Generate the JavaScript: theme toggle, masonry layout, and lightbox."""
    return '''// Theme toggle
(function() {
  const toggle = document.getElementById("themeToggle");
  if (!toggle) return;
  
  // Check saved preference or system preference
  const saved = localStorage.getItem("album-theme");
  if (saved) {
    document.documentElement.dataset.scheme = saved;
  } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.dataset.scheme = "dark";
  }
  
  toggle.addEventListener("click", function() {
    const current = document.documentElement.dataset.scheme;
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.dataset.scheme = next;
    localStorage.setItem("album-theme", next);
  });
  
  // Listen for system preference changes
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function(e) {
    if (!localStorage.getItem("album-theme")) {
      document.documentElement.dataset.scheme = e.matches ? "dark" : "light";
    }
  });
})();

// Image load shimmer fade-in
document.querySelectorAll('.img-wrap img').forEach(function(img) {
  var wrap = img.parentElement;
  function reveal() {
    img.classList.add('is-loaded');
    wrap.classList.add('is-loaded');
  }
  if (img.complete) {
    reveal();
  } else {
    img.addEventListener('load', reveal);
    img.addEventListener('error', reveal);
  }
});

// Pinterest-style masonry layout (PC only, mobile uses single column)
(function() {
  function layoutMasonry(grid) {
    var items = Array.from(grid.querySelectorAll(".photo-item"));
    if (!items.length) return;

    if (grid.querySelector(".photo-col")) return;

    var numCols = 4;
    var cols = [];
    for (var c = 0; c < numCols; c++) {
      var col = document.createElement("div");
      col.className = "photo-col";
      cols.push(col);
      grid.appendChild(col);
    }

    // Temporarily make grid block-flow so items have natural height
    grid.style.display = "block";
    var colHeights = [];
    for (var c = 0; c < numCols; c++) { colHeights.push(0); }
    var gapSize = 12;

    items.forEach(function(item) {
      var h = item.offsetHeight;
      var shortest = 0;
      var minH = colHeights[0];
      for (var c = 1; c < numCols; c++) {
        if (colHeights[c] < minH) {
          minH = colHeights[c];
          shortest = c;
        }
      }
      cols[shortest].appendChild(item);
      colHeights[shortest] += h + (colHeights[shortest] > 0 ? gapSize : 0);
    });

    grid.style.display = "";
  }

  var grids = document.querySelectorAll(".photo-grid");
  if (!grids.length) return;

  var isMobile = window.innerWidth <= 768;

  // Mobile: show immediately, no masonry needed
  if (isMobile) {
    grids.forEach(function(g) { g.classList.add("is-ready"); });
    return;
  }

  // PC: show a loading spinner while images load
  grids.forEach(function(grid) {
    var spinner = document.createElement("div");
    spinner.className = "photo-grid-loader";
    spinner.innerHTML = '<svg viewBox="0 0 24 24" width="32" height="32"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4 31.4" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/></circle></svg>';
    grid.parentNode.insertBefore(spinner, grid);
  });

  var images = document.querySelectorAll(".photo-item img");
  var loaded = 0;
  var total = images.length;

  function onReady() {
    grids.forEach(layoutMasonry);
    grids.forEach(function(g) { g.classList.add("is-ready"); });
    var spinners = document.querySelectorAll(".photo-grid-loader");
    spinners.forEach(function(s) { s.remove(); });
  }

  if (total === 0) {
    onReady();
    return;
  }

  images.forEach(function(img) {
    if (img.complete) {
      loaded++;
      if (loaded === total) onReady();
    } else {
      img.addEventListener("load", function() {
        loaded++;
        if (loaded === total) onReady();
      });
      img.addEventListener("error", function() {
        loaded++;
        if (loaded === total) onReady();
      });
    }
  });

  setTimeout(onReady, 3000);
})();

// Lightbox
(function() {
  var lb = document.createElement("div");
  lb.className = "lightbox";
  lb.innerHTML = '<button class="lightbox-close">\u00d7</button>' +
    '<button class="lightbox-nav lightbox-prev"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg></button>' +
    '<button class="lightbox-nav lightbox-next"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg></button>' +
    '<img src="" alt="" />' +
    '<div class="lightbox-caption"></div>';
  document.body.appendChild(lb);

  var lbImg = lb.querySelector("img");
  var lbCaption = lb.querySelector(".lightbox-caption");
  var lbClose = lb.querySelector(".lightbox-close");
  var lbPrev = lb.querySelector(".lightbox-prev");
  var lbNext = lb.querySelector(".lightbox-next");

  var allItems = [];
  var currentIndex = 0;

  function collectItems() {
    allItems = [];
    var items = document.querySelectorAll(".photo-item");
    items.forEach(function(fig, i) {
      var img = fig.querySelector("img");
      var cap = fig.querySelector("figcaption");
      if (img) {
        allItems.push({ src: img.src, alt: img.alt, caption: cap ? cap.textContent : "" });
        fig.addEventListener("click", function() { open(i); });
      }
    });
  }

  function open(index) {
    currentIndex = index;
    show(currentIndex);
    lb.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function show(index) {
    var item = allItems[index];
    if (!item) return;
    lbImg.src = item.src;
    lbImg.alt = item.alt;
    lbCaption.textContent = item.caption;
    lbPrev.style.display = allItems.length > 1 ? "" : "none";
    lbNext.style.display = allItems.length > 1 ? "" : "none";
  }

  function close() {
    lb.classList.remove("is-open");
    lbImg.src = "";
    document.body.style.overflow = "";
  }

  function prev() {
    currentIndex = (currentIndex - 1 + allItems.length) % allItems.length;
    show(currentIndex);
  }

  function next() {
    currentIndex = (currentIndex + 1) % allItems.length;
    show(currentIndex);
  }

  lbClose.addEventListener("click", function(e) { e.stopPropagation(); close(); });
  lbPrev.addEventListener("click", function(e) { e.stopPropagation(); prev(); });
  lbNext.addEventListener("click", function(e) { e.stopPropagation(); next(); });
  lb.addEventListener("click", function(e) { if (e.target === lb || e.target === lbImg) close(); });

  document.addEventListener("keydown", function(e) {
    if (!lb.classList.contains("is-open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") prev();
    if (e.key === "ArrowRight") next();
  });

  var touchStartX = 0;
  lb.addEventListener("touchstart", function(e) { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
  lb.addEventListener("touchend", function(e) {
    var dx = e.changedTouches[0].screenX - touchStartX;
    if (dx > 50) prev();
    else if (dx < -50) next();
  }, { passive: true });

  var observer = new MutationObserver(function() {
    if (document.querySelector(".photo-col")) {
      observer.disconnect();
      collectItems();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
  setTimeout(collectItems, 3500);
})();
'''

def main():
    # Load config and data
    config = load_json(CONFIG_PATH)
    articles = load_json(os.path.join(DATA_DIR, "articles.json"))
    
    # Clean only generated output files (preserve .git, src, README, etc.)
    for d in ["css", "js", "album"]:
        p = os.path.join(DIST_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p)
    for f in ["index.html"]:
        p = os.path.join(DIST_DIR, f)
        if os.path.exists(p):
            os.remove(p)
    
    # Create directory structure
    os.makedirs(os.path.join(DIST_DIR, "css"), exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "js"), exist_ok=True)
    
    for article in articles:
        os.makedirs(os.path.join(DIST_DIR, "album", article["slug"]), exist_ok=True)
    
    # Generate CSS
    css_path = os.path.join(DIST_DIR, "css", "style.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(generate_css())
    print(f"  {css_path}")
    
    # Generate JS
    js_path = os.path.join(DIST_DIR, "js", "main.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(generate_js())
    print(f"  {js_path}")
    
    # Generate index
    index_html = generate_index_html(articles, config)
    index_path = os.path.join(DIST_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"  {index_path}")
    
    # Generate album pages
    for article in articles:
        album_html = generate_album_html(article, config)
        album_path = os.path.join(DIST_DIR, "album", article["slug"], "index.html")
        with open(album_path, "w", encoding="utf-8") as f:
            f.write(album_html)
        print(f"  {album_path}")
    
    total_images = sum(a["image_count"] for a in articles)
    print(f"\n✓ Built {len(articles)} album pages, {total_images} images total")
    print(f"  Output: {DIST_DIR}")

if __name__ == "__main__":
    main()
