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

### 3.2 部署与 CDN

1. **本地构建**：Python 脚本生成全部静态 HTML/CSS/JS
2. **GitHub 部署**：push → GitHub Pages 纯文件发布（仓库根 `.nojekyll` 跳过 Jekyll 构建，构建历史查 `api.github.com/repos/agent-vik/victor-album/pages/builds`）→ 托管为源站
3. **Cloudflare 上线**：域名 `album.victor42.work` 在 Cloudflare 管理，通过代理（橙云）指向 GitHub Pages 源站，对外提供访问、边缘缓存和安全防护
4. **图片 CDN**：图片直接引用 Cloudflare R2 源：`https://cdn.victor42.work/posts/{YYYY-MM}/{文件名}`，图片已由博客压缩过（webp），直接引用无需生成缩略图

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
│   ├── config.json                # 站点配置（站点名称、描述、meta 描述、站点 URL、博客地址、预览数量、GA ID、CF beacon token）
│   ├── fetch_data.py              # 从博客抓取图片数据
│   ├── build.py                   # 核心构建脚本（CSS + HTML + JS 模板 + SEO head + sitemap）
│   └── data/
│       └── articles.json          # 抓取到的图片数据（封面 + 正文图片 + alt 文本）
├── sitemap.xml                    # 站点地图（由 build.py 生成）
├── .gitignore
├── notes.md                       # 本文档
└── README.md                      # 仓库说明
```

**数据源**: `src/fetch_data.py` 中维护 slug 列表（唯一文章来源），标题、日期、封面均从博客 HTML 自动抓取

**配置**: `src/config.json`（站点名称、描述、meta 描述、站点 URL、博客地址、预览数量、Google Analytics ID、Cloudflare beacon token）

**构建**: `src/fetch_data.py` 解析博客 HTML 提取图片；`src/build.py` 包含 CSS/HTML/JS 模板，生成全部页面

**产物**: `index.html`（首页）、`album/{slug}/index.html`（详情页）、`css/style.css`、`js/main.js`、`sitemap.xml`

**路径处理**: 脚本通过 `__file__` 动态推导项目路径，不依赖硬编码绝对路径，任意环境 clone 后可直接运行

---

## 5. 技术实现

### 5.1 数据抓取（fetch_data.py）

urllib 请求博客 IPFS 站点，BeautifulSoup 解析 Hugo Stack 主题的 HTML：

- **标题**：从 `<title>` 标签提取，fallback 到 `og:title` meta
- **封面图**：从 `<meta property="og:image" content="...">` 提取 OG 封面
- **日期**：从 `<time datetime=...>` 提取，fallback 到 `article:published_time` meta
- **正文图片**：取 `<section class="article-content">` 内的 `<img>`（找不到时回退 `<article>` 内第一个 `<section>`），仅保留 `src` 以 `https://cdn.victor42.work/posts/` 开头的图片
- **过滤**：alt 关键词过滤（表情包/搞笑/恶搞/简笔/搞怪/截图/卡片截图/开支明细/开支构成/消费明细/开支分类构成/账单明细/条形图）。机制依赖博客端 img alt 与关键词的连续子串匹配，alt 措辞变体会绕过——2026-10-23 全量审计曾漏网 3 张开支图（"开支分类构成"绕过"开支构成"、"账单明细"绕过"消费明细"）后补词修复；2026-10-28 二次全量审计（14 篇博客开支章节逐图核对 + 2462 条 alt 副作用排查）补"条形图"（云和"按…分类的构成条形图"不含任何开支类词；图表类型词不依赖措辞组合，实测零误伤）。已被否决的方案：单字级关键词（开支/花费/账单/明细/消费/构成/表格/截图，会误杀西安陶俑"多民族构成"等正常照片）；按章节标题过滤开支章节（过于特化）；"图表"关键词（实测会误杀 2 张博物馆展板实拍——自然博物馆恐龙演化图表、王莽改制关系图表，且当前无漏网需要它）。新增游记发布后建议抽检开支章节的图
- **输出**：按日期倒序排列，cover 为字符串 URL，images 为 `[{src, alt}]` 数组

### 5.2 视觉体系

对齐博客 Stack Theme 的设计系统。主色调 `#2A9D8F`，字体 Lato，亮暗双主题通过 CSS 变量 + `[data-scheme="dark"]` 选择器切换。样式与脚本源码是独立文件 `src/style.css` 与 `src/main.js`，`build.py` 原样复制到产物目录。

### 5.3 瀑布流布局

PC 端使用 JS 实现真正的 Pinterest 式瀑布流（4 列，按最短列分配），移动端退化为单列自然流。图片加载期间网格 `height: 0; visibility: hidden`，加载完成后展开并显示布局。

**测量约束（2026-10-28 塌列 bug 的教训，改这块前必读）**：`layoutMasonry` 量元素高度有两个陷阱——

1. 元素脱离 DOM 后 `offsetHeight` 恒为 0。旧版重排时先删旧列再量高度，所有元素全部量出 0、全堆进第 0 列；触发源是布局完成后页面变高→滚动条出现→视口宽度微变→`resize` 事件→重排，故现象为"正常一闪而过→塌掉"。
2. 未就绪的网格是 `height: 0` 的 flex 容器，列内元素会被 flex 压缩成 0 高，直接在列内量也全为 0。

正解：在网格内挂一个 `position:absolute; visibility:hidden` 的定宽测量容器（宽度=真实列宽），元素在其中保持 DOM 连接且不受 flex 压缩，量完再分配进列。

### 5.4 Lightbox

动态创建全屏遮罩 DOM，点击图片放大查看。支持键盘方向键、移动端 touch swipe 前后切换。由于瀑布流布局会重建 DOM，通过 MutationObserver 等待布局完成后再绑定点击事件。

### 5.5 SEO

SEO 头部与站点地图均由 `build.py` 生成，不手写产物：

- **SEO head**：`seo_head_index()` / `seo_head_album()` 生成 title、canonical、robots、description、Open Graph、JSON-LD（首页为 `CollectionPage`，详情页为 `ImageGallery`，含 og:image 指向封面）
- **描述文案**：站点级 meta 描述写在 `config.json` 的 `meta_description`（已泛化，不含具体目的地列表）；详情页描述由标题 + 图片数自动生成
- **sitemap.xml**：`generate_sitemap()` 由文章列表自动生成，新增文章自动进 sitemap，无需手维护
- **robots.txt**：静态文件，指向 sitemap

标题与 meta 描述不含模型数、相册数等易变数字，避免内容变动时改动头部、影响 SEO 稳定。

---

## 6. 维护指南

### 6.1 新增文章

1. 在 `src/fetch_data.py` 的 `ARTICLES` 列表中添加 slug
2. 运行 `python3 src/fetch_data.py`（自动抓取标题、日期、封面、图片）
3. 运行 `python3 src/build.py`
4. `git add -A && git commit -m "data: add {slug}" && git push origin main`

### 6.2 更新已有文章的图片/alt

直接运行 `fetch_data.py` → `build.py` → push，脚本会重新抓取并覆盖 `articles.json`。

### 6.3 Git 提交身份

- **Name**: Agent Vik
- **Email**: agent-vik@victor42.work
- 沙盒环境需在每次会话开始时执行 `git config` 配置
