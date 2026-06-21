# Victor Album

旅途中的光影记录

## 构建

本项目使用 Python 脚本从博客抓取图片数据并生成静态页面。

### 前置依赖

- Python 3
- z-ai CLI (web-reader)

### 更新相册

1. 编辑 `config.json`，添加/删除文章配置
2. 运行数据抓取脚本：

```bash
python3 fetch_data.py
```

3. 运行构建脚本生成静态页面：

```bash
python3 build.py
```

4. 将 `dist/` 目录的内容推送到 GitHub Pages

### 目录结构

```
├── config.json          # 文章列表配置（可编辑）
├── fetch_data.py        # 数据抓取脚本
├── build.py             # 静态页面构建脚本
├── data/                # 抓取的图片数据（JSON）
├── dist/                # 生成的静态站点（部署此目录）
│   ├── index.html       # 首页（相册列表）
│   ├── css/style.css    # 样式
│   ├── js/main.js       # 主题切换等
│   └── album/
│       └── {slug}/
│           └── index.html  # 相册详情页
└── plan.md              # 项目计划文档
```

## License

MIT
