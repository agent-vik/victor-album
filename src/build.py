#!/usr/bin/env python3
"""Build static HTML pages for victor-album from fetched data."""

import json
import os
import re
import shutil
from datetime import datetime
from urllib.parse import quote

PROJECT_DIR = "/tmp/victor-album"
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
    site_name = config.get("site_name", "Victor Album")
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
            preview_imgs += f'          <img src="{src}" alt="{alt}" loading="lazy">\n'
        
        cards_html += f'''    <article class="album-card">
      <a href="album/{slug}/" class="album-link">
        <div class="album-cover">
          <img src="{cover}" alt="{title}" loading="lazy">
        </div>
        <div class="album-info">
          <h2 class="album-title">{title}</h2>
          <div class="album-meta">
            <time datetime="{article.get('date', '')}">{date}</time>
            <span class="album-count">{total} 张照片</span>
          </div>
        </div>
      </a>
      <div class="album-preview">
{preview_imgs.rstrip()}      </div>
      <a href="album/{slug}/" class="album-more">查看全部 →</a>
    </article>
'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN" data-scheme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{site_name}</title>
  <meta name="description" content="{config.get('description', '')}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
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
    <div class="container">
      <p>© 2011 - 2026 <a href="https://victor42.eth.limo" target="_blank" rel="noopener">Victor42</a></p>
    </div>
  </footer>
  <script src="js/main.js"></script>
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
    site_name = config.get("site_name", "Victor Album")
    
    # Masonry images
    images_html = ""
    for i, img in enumerate(images):
        src = img["src"]
        alt = escape_html(img["alt"])
        images_html += f'''      <figure class="photo-item">
        <img src="{src}" alt="{alt}" loading="lazy">
        {f'<figcaption>{alt}</figcaption>' if alt else ''}
      </figure>
'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN" data-scheme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title} - {site_name}</title>
  <meta name="description" content="{title}，共{total}张照片">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body>
  <header class="site-header album-header">
    <div class="container">
      <a href="../../" class="back-link">← 返回相册</a>
      <h1 class="album-page-title">{title}</h1>
      <div class="album-page-meta">
        <time datetime="{article.get('date', '')}">{date}</time>
        <span class="album-count">{total} 张照片</span>
        <a href="{blog_url}" class="blog-link" target="_blank" rel="noopener">阅读原文 →</a>
      </div>
      <button class="theme-toggle" id="themeToggle" aria-label="Toggle dark mode">
        <svg class="icon icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        <svg class="icon icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </header>
  <main class="container photo-grid">
{images_html}  </main>
  <footer class="site-footer">
    <div class="container">
      <p>© 2011 - 2026 <a href="https://victor42.eth.limo" target="_blank" rel="noopener">Victor42</a></p>
    </div>
  </footer>
  <script src="../../js/main.js"></script>
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
  max-width: 960px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ===== Header ===== */
.site-header {
  padding: 48px 0 32px;
  border-bottom: 1px solid var(--border);
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

/* ===== Album Cards (Homepage) ===== */
.album-card {
  margin-bottom: 40px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: box-shadow var(--transition);
}

.album-card:hover {
  box-shadow: var(--shadow-hover);
}

.album-link {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  color: var(--text);
  text-decoration: none;
  border-bottom: 1px solid var(--border);
}

.album-link:hover {
  color: var(--text);
  opacity: 1;
}

.album-cover {
  width: 80px;
  height: 80px;
  border-radius: 6px;
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

.album-more {
  display: block;
  text-align: center;
  padding: 12px;
  color: var(--accent);
  font-size: 0.9rem;
  border-top: 1px solid var(--border);
  transition: background-color var(--transition);
}

.album-more:hover {
  background-color: var(--bg-secondary);
  opacity: 1;
}

/* ===== Album Detail Page ===== */
.album-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: var(--bg);
  padding: 16px 0 !important;
  margin-bottom: 24px !important;
}

.album-header .container {
  gap: 8px;
}

.back-link {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.back-link:hover {
  color: var(--accent);
}

.album-page-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
}

.album-page-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-wrap: wrap;
  flex: 1;
}

.blog-link {
  margin-left: auto;
}

/* ===== Photo Masonry Grid ===== */
.photo-grid {
  column-count: 2;
  column-gap: 12px;
}

.photo-item {
  break-inside: avoid;
  margin-bottom: 12px;
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-secondary);
  box-shadow: var(--shadow);
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
  color: var(--text-muted);
  font-size: 0.85rem;
  text-align: center;
}

.site-footer a {
  color: var(--text-secondary);
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .album-preview {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .photo-grid {
    column-count: 1;
  }
  
  .album-link {
    flex-direction: column;
    text-align: center;
  }

  .album-meta {
    justify-content: center;
  }
  
  .album-cover {
    width: 120px;
    height: 120px;
  }
  
  .site-header .container {
    flex-direction: column;
    text-align: center;
  }
  
  .site-desc {
    text-align: center;
  }
  
  .album-page-meta {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .blog-link {
    margin-left: 0;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .album-preview {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .photo-grid {
    column-count: 2;
  }
}

@media (min-width: 1025px) {
  .album-preview {
    grid-template-columns: repeat(6, 1fr);
  }
  
  .photo-grid {
    column-count: 2;
  }
}
'''

def generate_js():
    """Generate the JavaScript for theme toggle."""
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
