# Victor Album 备忘录

## 1. 目的

本文档记录 `agent-vik/victor-album` 项目的完整信息，为本项目的未来维护提供便利。

**重要提示：** 每次新增或修改功能后，请务必更新此备忘录，确保文档的准确性和时效性。

## 2. 项目概览

### 2.1 基本信息
- **GitHub**: https://github.com/agent-vik/victor-album
- **在线地址**: https://album.victor42.work
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
fetch_data.py → articles.json → build.py → 静态 HTML/CSS/JS
```

手动触发：用户告知新文章 → 更新 `src/fetch_data.py` 中的 `ARTICLES` 列表 → 运行 `fetch_data.py` → 运行 `build.py` → git push。

### 3.2 部署

- Cloudflare Pages 从 `main` 分支根目录自动部署
- 自定义域名 `album.victor42.work`（CNAME 指向 Cloudflare Pages）
- 图片直接引用 CDN 原图：`https://cdn.victor42.work/posts/{YYYY-MM}/{文件名}`
- 图片已由博客压缩过（webp），直接引用无需生成缩略图
- 推送即部署，构建在本地完成

---

## 4. 文件结构

```
victor-album/
├── CNAME                          # 自定义域名 album.victor42.work
├── css/
│   └── style.css                  # 全局样式（由 build.py 生成）
├── js/
│   └── main.js                    # 主题切换 + 瀑布流布局 + Lightbox（由 build.py 生成）
├── album/
│   ├── {slug}/
│   │   └── index.html             # 各游记详情页（由 build.py 生成）
│   └── ...
├── src/
│   ├── config.json                # 站点配置（站点名称、描述、预览数量）
│   ├── fetch_data.py              # 从博客抓取图片数据
│   ├── build.py                   # 核心构建脚本（CSS + HTML + JS 模板）
│   └── data/
│       └── articles.json          # 抓取到的图片数据（封面 + 正文图片 + alt 文本）
├── .gitignore
├── notes.md                       # 本文档
└── README.md                      # 仓库说明
```

**数据源**: `src/fetch_data.py` 中硬编码文章列表（slug + 标题），从博客 HTML 抓取数据

**配置**: `src/config.json`（站点名称、描述、预览数量）

**构建**: `src/fetch_data.py` 解析博客 HTML 提取图片；`src/build.py` 包含 CSS/HTML/JS 模板，生成全部页面

**产物**: `index.html`（首页）、`album/{slug}/index.html`（详情页）、`css/style.css`、`js/main.js`

---

## 5. 技术实现

### 5.1 数据抓取（fetch_data.py）

使用 urllib 直连博客 IPFS 站点，解析 Hugo Stack 主题的 HTML 结构：

- **封面图**：从 `<meta property="og:image" content="...">` 提取 OG 封面
- **日期**：从 `<time datetime=...>` 提取（无引号属性格式）
- **正文图片**：精确提取 `<section class=article-content>` 到 `<footer class=article-footer>` 之间的图片，排除头图和底部关联推荐（`related-content--wrapper`）
- **属性解析**：博客使用无引号 HTML 属性（`src=https://... alt=文本`），正则使用 `\S+` 和 `[^\s>]+` 匹配
- **过滤**：alt 关键词过滤（表情包/搞笑/恶搞/简笔/搞怪/截图/卡片截图/开支明细/开支构成/消费明细）
- **输出**：按日期倒序排列，cover 为字符串 URL，images 为 `[{src, alt}]` 数组

### 5.2 视觉体系

对齐博客 Stack Theme 的设计系统。主色调 `#2A9D8F`，字体 Lato，亮暗双主题通过 CSS 变量 + `[data-scheme="dark"]` 选择器切换。所有样式定义集中在 `src/build.py` 的 `generate_css()` 中。

### 5.3 瀑布流布局

PC 端使用 JS 实现真正的 Pinterest 式瀑布流（4 列，按最短列分配），移动端退化为单列自然流。图片加载期间网格 `height: 0; visibility: hidden`，加载完成后展开并显示布局。核心难点在于浏览器 DOM 操作是批量的，必须先用 `display: block` 让元素获得自然高度，再用 `offsetHeight` 预量后分配。

### 5.4 Lightbox

动态创建全屏遮罩 DOM，点击图片放大查看。支持键盘方向键、移动端 touch swipe 前后切换。由于瀑布流布局会重建 DOM，通过 MutationObserver 等待布局完成后再绑定点击事件。

---

## 6. 维护指南

### 6.1 新增文章

1. 在 `src/fetch_data.py` 的 `ARTICLES` 列表中添加条目
2. 运行 `python3 src/fetch_data.py`
3. 运行 `python3 src/build.py`
4. `git add -A && git commit -m "data: add {title}" && git push origin main`

### 6.2 更新已有文章的图片/alt

直接运行 `fetch_data.py` → `build.py` → push，脚本会重新抓取并覆盖 `articles.json`。

### 6.3 Git 提交身份

- **Name**: Agent Vik
- **Email**: agent-vik@victor42.work
- 沙盒环境需在每次会话开始时执行 `git config --global` 配置