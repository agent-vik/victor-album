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

### 4.1 完整目录结构

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
├── NOTES.md                     # 本文档
└── README.md                    # 仓库说明
```

### 4.2 关键文件说明

**配置**:
- `src/config.json`: 文章列表（slug、标题、博客 URL、预览数量）
- `src/data/articles.json`: 抓取的图片数据（URL、alt 文本）

**构建**:
- `src/fetch_data.py`: 解析博客 HTML 提取图片，输出 articles.json
- `src/build.py`: 包含 CSS 模板、HTML 模板、JS 模板，生成全部页面

**生成产物**:
- `css/style.css`: 全局样式
- `js/main.js`: 主题切换 + 瀑布流 + Lightbox
- `index.html`: 首页列表页
- `album/{slug}/index.html`: 各详情页

---

## 5. 技术实现

### 5.1 视觉体系

对齐博客 Stack Theme 的设计系统。

| 项目 | 值 |
|------|-----|
| Accent 色 | `#2A9D8F` |
| 亮色背景 | `#f5f5fa` |
| 亮色卡片背景 | `#fff` |
| 暗色背景 | `#303030` |
| 暗色卡片背景 | `#424242` |
| 暗色 Accent 文字 | `#ecf0f1` |
| 字体 | Lato（Google Fonts，300/400/700） |
| CJK 字体回退 | Noto Sans SC → PingFang SC → Microsoft YaHei |
| 圆角 | `var(--radius): 8px` |
| 阴影 | `0 2px 8px rgba(0,0,0,0.08)` / hover `0 4px 16px` |
| 亮暗切换 | `[data-scheme="dark"]` 选择器 + localStorage |

### 5.2 首页列表页

- 按文章发布时间倒序排列
- 每篇文章一张卡片（`.album-card`），包含：
  - 胶囊封面（16:9 比例，两端圆角）
  - 标题
  - 日期 + 图片数量
  - 24 张预览图网格（PC 6列 / 平板 4列 / 手机 3列）
  - "查看全部"按钮（渐变遮罩覆盖在预览图末尾，背景从透明过渡到卡片背景色）

### 5.3 详情页

- 顶部 sticky 导航栏（返回链接 SVG 图标 + 主题切换按钮）
- Hero 卡片（与首页共享 `.album-card` 组件：胶囊封面 + 标题 + 日期 + 图片数量）
- 阅读原文按钮（固定 `#2A9D8F` 底色，PC 端卡片右端居中，移动端下方居中）
- Pinterest 式瀑布流图片展示
- Lightbox 大图查看（点击放大，前后切换，键盘/滑动支持）
- 每张图片保留 alt 文本说明
- 懒加载（首屏 eager，其余 lazy）

### 5.4 瀑布流布局

- PC 端：4 列，JS 动态分配
  - 临时将 grid 设为 `display: block` 让 items 有自然高度
  - 用 `item.offsetHeight` 预量每张图片高度
  - JS 变量追踪每列累计高度，分配到最短列
  - 等待所有图片加载完成后执行布局
- 移动端：跳过 masonry，单列自然流直接显示
- 加载期间显示 SVG spinner 动画

### 5.5 Lightbox 大图查看

- 点击任意图片弹出全屏遮罩查看大图
- 左右箭头按钮 + 键盘方向键前后切换
- 移动端左右滑动切换（touch swipe，50px 阈值）
- 底部显示 figcaption 图片说明文字
- 关闭方式：× 按钮 / 点击背景 / Esc 键
- PC 90vw×90vh / 移动端 95vw×85vh
- masonry 布局完成后通过 MutationObserver 收集图片元素

### 5.6 页脚

- `© 2011 - 2026 Victor42`（链接指向博客）
- 格式与博客仓库一致

---

## 6. 布局规格

| 项目 | 值 |
|------|-----|
| 容器最大宽度 | 1200px |
| 容器水平内边距 | 20px |
| PC 瀑布流列数 | 4 列 |
| 移动端布局 | 单列自然流 |
| 瀑布流间距 | 12px（列间） |
| 首页预览网格 | PC 6列 / 平板 4列 / 手机 3列 |
| Hero 卡片内边距 | 32px（上下）24px（左右） |
| Hero 卡片元素间距 | 8px |

---

## 7. 入选文章

| # | 标题 | Slug | 图片数 |
|---|------|------|--------|
| 1 | 西安初夏休闲6天5夜 | trip-to-xi-an | 162 |
| 2 | 西双版纳景洪春季休闲6天5夜 | trip-to-xishuangbanna | 155 |
| 3 | 珠海澳门春节9天8夜 | trip-to-zhuhai-and-macao | 91 |
| 4 | 敦煌自驾5天4夜 | 3596 | 129 |
| 5 | 北京4天5夜 | 3580 | 132 |
| 6 | 蒙西宁夏国庆小众自驾6天5夜 | inner-mongolia-north-ningxia-self-driving-tour | 41 |
| 7 | 敦煌二刷遛娃5天4夜 | a-revisit-to-dunhuang | 44 |
| 8 | 纯净的海 | 1870 | 44 |
| | **合计** | **798 张图片** |

---

## 8. 博客技术背景

| 项目 | 详情 |
|------|------|
| 博客框架 | Hugo 0.152.2 |
| 主题 | Stack（v3.32.0） |
| 域名 | victor42.eth.limo（IPFS + ENS） |
| 博客主站 | victor42.work |
| 图片 CDN | `cdn.victor42.work/posts/{YYYY-MM}/{文件名}` |
| 博主 GitHub | github.com/greenzorro |
