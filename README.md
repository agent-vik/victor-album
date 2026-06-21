# Victor Album

旅途中的光影记录 - 从博客游记中精选照片，以瀑布流相册的形式呈现。

A static photo gallery curated from [Victor42's travel blog](https://victor42.eth.limo).

## Gallery

| Album | Photos |
|-------|--------:|
| [西安初夏休闲6天5夜](https://agent-vik.github.io/victor-album/album/trip-to-xi-an/) | 162 |
| [西双版纳景洪春季休闲6天5夜](https://agent-vik.github.io/victor-album/album/trip-to-xishuangbanna/) | 155 |
| [珠海澳门春节9天8夜](https://agent-vik.github.io/victor-album/album/trip-to-zhuhai-and-macao/) | 91 |
| [蒙西宁夏国庆小众自驾6天5夜](https://agent-vik.github.io/victor-album/album/inner-mongolia-north-ningxia-self-driving-tour/) | 41 |
| [敦煌二刷遛娃5天4夜](https://agent-vik.github.io/victor-album/album/a-revisit-to-dunhuang/) | 44 |
| [敦煌自驾5天4夜](https://agent-vik.github.io/victor-album/album/3596/) | 129 |
| [北京4天5夜](https://agent-vik.github.io/victor-album/album/3580/) | 132 |
| [纯净的海](https://agent-vik.github.io/victor-album/album/1870/) | 44 |
| **Total** | **798** |

## Features

- Responsive masonry layout with grid preview on homepage
- Dark / Light mode toggle (auto system preference detection)
- Image captions preserved from original blog post `alt` text
- Zero dependencies - pure HTML, CSS, and vanilla JS
- CDN-hosted images via Cloudflare
- Config-driven: add new albums by editing `config.json`

## Technical

| Aspect | Detail |
|--------|--------|
| **Source** | [victor42.eth.limo](https://victor42.eth.limo) (Hugo + IPFS + ENS) |
| **Image CDN** | cdn.victor42.work (Cloudflare) |
| **Font** | [Lato](https://fonts.google.com/specimen/Lato) (300/400/700) |
| **Hosting** | GitHub Pages |
| **Stack** | Python build scripts generates static HTML/CSS/JS |

## Project Structure

```
├── config.json          # Album list (editable — add/remove articles here)
├── fetch_data.py        # Scrape image data from blog posts
├── build.py             # Generate static HTML pages
├── data/                # Scraped image metadata (JSON, gitignored)
├── dist/                # Built static site (deploy this directory)
│   ├── index.html       # Homepage (album list with preview grids)
│   ├── css/style.css    # Stylesheet
│   ├── js/main.js       # Theme toggle logic
│   └── album/
│       └── {slug}/
│           └── index.html  # Album detail page (masonry grid)
├── plan.md              # Project plan & decisions
└── README.md
```

## Update Albums

To add a new blog post to the gallery:

1. Edit `config.json` - add the new article's slug, title, and URL
2. Run `python3 fetch_data.py` - scrapes images from the blog post
3. Run `python3 build.py` - regenerates all static pages
4. Commit and push the updated `dist/` to GitHub Pages

## About

Built by [Agent Vik](https://github.com/agent-vik) for [Victor42](https://victor42.work/).

Photos by Victor42. All rights reserved.

## License

MIT
