# Victor Album — 项目计划

> 从 Victor42 博客（victor42.eth.limo）的长途游记中提取图片，做成静态网页相册。

- **GitHub**：[agent-vik/victor-album](https://github.com/agent-vik/victor-album)
- **在线地址**：[agent-vik.github.io/victor-album](https://agent-vik.github.io/victor-album/)
- **博客地址**：[victor42.eth.limo](https://victor42.eth.limo)

---

## 项目阶段

| # | 阶段 | 状态 |
|---|------|------|
| 1 | 信息调研（博客结构、CDN、命名规律） | ✅ |
| 2 | 文章筛选与图片数据采集 | ✅ |
| 3 | GitHub 仓库创建 & 项目初始化 | ✅ |
| 4 | 相册页面开发 & 构建流程 | ✅ |
| 5 | 部署到 GitHub Pages | ✅ |
| 6 | 视觉对齐博客 Stack Theme | ✅ |
| 7 | 移动端适配 & UI 细节打磨 | ✅ |
| 8 | 真瀑布流布局（Pinterest 式） | ✅ |
| 9 | 容器宽度 & 列数调整（1200px / 4列） | ✅ |
| 10 | README 署名对齐博客仓库格式 | ⬜ 待 API 限流解除后处理 |

---

## 技术架构

### 构建流程

```
config.json → fetch_data.py → articles.json → build.py → 静态 HTML/CSS/JS
```

| 文件 | 作用 |
|------|------|
| `src/config.json` | 文章列表配置（slug、标题、博客URL） |
| `src/fetch_data.py` | 从博客抓取图片数据，输出 `src/data/articles.json` |
| `src/build.py` | 核心构建脚本，读取配置和数据，生成全部静态页面 |
| `src/data/articles.json` | 抓取到的图片数据（798张） |
| `src/plan.md` | 早期计划文档（已归档，本文件为最新版） |

### 页面结构

```
/                      ← 首页（列表页，时间倒序）
├── css/style.css      ← 全局样式
├── js/main.js         ← 主题切换 + localStorage 持久化
├── album/
│   ├── {slug}/index.html  ← 各游记详情页（瀑布流）
│   └── ...
└── README.md
```

### 部署

- GitHub Pages 从 `main` 分支根目录部署
- 图片直接引用 CDN 原图：`cdn.victor42.work/posts/{YYYY-MM}/{文件名}`
- 无需构建步骤，推送即部署

### 布局规格

| 项目 | 值 |
|------|-----|
| 容器最大宽度 | 1200px |
| 容器水平内边距 | 20px |
| PC 瀑布流列数 | 4 列（JS 动态分配到最短列） |
| 移动端布局 | 单列自然流（无 masonry） |
| 瀑布流间距 | 12px（列间） |
| 首页预览网格 | PC 6列 / 平板 4列 / 手机 3列 |

### 技术特点

- **纯静态**：Python 生成 HTML，无前端框架依赖
- **零构建开销**：不需要 CI/CD，build.py 本地运行后直接 push
- **CDN 原图**：图片已由博客压缩过（webp），直接引用无需生成缩略图
- **真瀑布流**：JS 动态 Pinterest 式布局，round-robin 播种 + 最短列分配
- **响应式**：PC / 平板 / 手机三档适配

---

## 已实现的设计决策

### 视觉体系（对齐博客 Stack Theme）

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

### 首页列表页

- 按文章发布时间倒序排列
- 每篇文章一张卡片，包含：
  - **胶囊封面**（16:9 比例，两端圆角）
  - **标题**
  - **日期 + 图片数量**（灰色小字）
  - **24张预览图网格**（3-4-6列响应式）
  - **"查看全部"按钮**（渐变遮罩覆盖在预览图末尾）

### 详情页

- 顶部 sticky 导航栏（返回链接 + 主题切换）
- Hero 卡片（与首页共享卡片组件：胶囊封面 + 标题 + 日期 + 图片数量）
- **阅读原文按钮**（accent 底色，PC端在卡片右端居中，移动端在日期下方居中）
- 瀑布流图片展示（PC 2列，移动端 1列）
- 每张图片保留 alt 文本说明
- 懒加载（首屏 eager，其余 lazy）

### 页脚

- `© 2011 - 2026 Victor42`（带博客链接）
- 格式与博客仓库一致

---

## 入选文章（8篇长途游记）

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

### 维护方式

手动触发：用户告知新文章 → 更新 `config.json` → 运行 `fetch_data.py` → 运行 `build.py` → git push。

---

## 迭代记录

### v1.0 — 初始上线

- 搭建构建流程（config → fetch → build → push）
- 首页列表页 + 8个详情页，共 798 张图片
- GitHub Pages 部署上线
- 亮暗切换 + localStorage 持久化

### v1.1 — 视觉对齐

- 从博客实际 CSS 提取 design tokens，逐一对齐
- Accent `#2A9D8F`、背景色、暗色模式色值全部统一
- CJK 字体回退链补全

### v1.2 — 移动端 & UI 打磨

- 修复移动端标题过长时居中失效（`justify-content: center`）
- 统一页脚格式对齐博客
- Victor42 链接指向博客
- 统一卡片组件（首页和详情页共享）
- 胶囊封面 2:1 → 16:9
- "张照片" → "张图片"
- "查看全部"渐变遮罩效果（背景从透明过渡到卡片背景色）
- 详情页导航栏分隔线限制在 container 内
- 阅读原文改为 accent 底色按钮，PC端右端居中 / 移动端下方居中
- README 去掉相册列表，避免后续维护负担

### v1.3 — 瀑布流 & 布局优化

- 替换 CSS column-count（假瀑布流）为 JS 动态 Pinterest 式真瀑布流
- 等待图片加载完成后布局，避免高度计算错误
- 前 N 张图 round-robin 播种确保所有列都有内容
- 移动端跳过 masonry，单列自然流直接显示
- PC 端显示加载动画（SVG spinner），布局完成后移除
- 详情页导航栏 padding 覆盖问题修复（简写→具体属性）
- 统一卡片和照片卡片的背景色与阴影
- 移动端 blog-link 特异性覆盖修复（`align-self: center`）
- 暗色模式按钮颜色固定为 `#2A9D8F`（不随 theme variable 变化）
- 返回相册 / 阅读原文箭头文字替换为 SVG 图标
- Hero 卡片 padding 增大（32px 24px），元素间距收紧（gap 8px）
- 容器最大宽度从 960px 扩大到 1200px
- PC 端瀑布流列数从 2 列调整为 4 列

---

## 博客技术背景（参考）

| 项目 | 详情 |
|------|------|
| 博客框架 | Hugo 0.152.2 |
| 主题 | Stack（v3.32.0） |
| 域名 | victor42.eth.limo（IPFS + ENS） |
| 博客主站 | victor42.work |
| 图片 CDN | `cdn.victor42.work/posts/{YYYY-MM}/{文件名}` |
| 博主 GitHub | github.com/greenzorro |
