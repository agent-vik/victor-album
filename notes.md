# Victor Album 备忘录

## 1. 目的

本文档旨在详细记录 `agent-vik/victor-album` 项目的完整信息，为本项目的未来维护提供便利。

**重要提示：** 每次新增或修改功能后，请务必更新此备忘录，确保文档的准确性和时效性。

## 2. 项目概览

### 2.1 基本信息
- **GitHub**: https://github.com/agent-vik/victor-album
- **在线地址**: https://agent-vik.github.io/victor-album
- **博客地址**: https://victor42.eth.limo
- **构建工具**: Python 3 脚本生成静态 HTML/CSS/JS

### 2.2 核心特性
- 首页列表页（按时间倒序，胶囊封面卡片 + 预览网格）
- 详情页（Pinterest 式瀑布流 + Lightbox 大图查看）
- 亮/暗主题切换（localStorage 持久化）
- 响应式适配（PC / 平板 / 手机三档）
- 视觉体系对齐博客 Stack Theme

---

## 3. 整体架构

### 3.1 构建流程

```
config.json → fetch_data.py → articles.json → build.py → 静态 HTML/CSS/JS
```

手动触发：用户告知新文章 → 更新 `src/config.json` → 运行 `src/fetch_data.py` → 运行 `src/build.py` → git push。

### 3.2 部署

- GitHub Pages 从 `main` 分支根目录部署，无需 CI/CD
- 图片直接引用 CDN 原图：`https://cdn.victor42.work/posts/{YYYY-MM}/{文件名}`
- 图片已由博客压缩过（webp），直接引用无需生成缩略图
- 推送即部署，构建在本地完成

---

## 4. 文件结构

```
victor-album/
├── css/
│   └── style.css               # 全局样式（由 build.py 生成）
├── js/
│   └── main.js                  # 主题切换 + 瀑布流布局 + Lightbox（由 build.py 生成）
├── album/
│   ├── {slug}/
│   │   └── index.html          # 各游记详情页（由 build.py 生成）
│   └── ...
├── src/
│   ├── config.json             # 文章列表配置（slug、标题、博客URL）
│   ├── fetch_data.py           # 从博客抓取图片数据
│   ├── build.py                # 核心构建脚本（CSS + HTML + JS 模板）
│   └── data/
│       └── articles.json       # 抓取到的图片数据
├── .gitignore
├── notes.md                     # 本文档
└── README.md                    # 仓库说明
```

**配置**: `src/config.json`（文章列表、slug、标题、博客 URL、预览数量）和 `src/data/articles.json`（抓取的图片数据）

**构建**: `src/fetch_data.py` 解析博客 HTML 提取图片；`src/build.py` 包含 CSS/HTML/JS 模板，生成全部页面

**产物**: `index.html`（首页）、`album/{slug}/index.html`（详情页）、`css/style.css`、`js/main.js`

---

## 5. 技术实现

### 5.1 视觉体系

对齐博客 Stack Theme 的设计系统。主色调 `#2A9D8F`，字体 Lato，亮暗双主题通过 CSS 变量 + `[data-scheme="dark"]` 选择器切换。所有样式定义集中在 `src/build.py` 的 `generate_css()` 中。

### 5.2 瀑布流布局

PC 端使用 JS 实现真正的 Pinterest 式瀑布流（4 列，按最短列分配），移动端退化为单列自然流。核心难点在于浏览器 DOM 操作是批量的，必须先用 `display: block` 让元素获得自然高度，再用 `offsetHeight` 预量后分配。

### 5.3 Lightbox

动态创建全屏遮罩 DOM，点击图片放大查看。支持键盘方向键、移动端 touch swipe 前后切换。由于瀑布流布局会重建 DOM，通过 MutationObserver 等待布局完成后再绑定点击事件。
