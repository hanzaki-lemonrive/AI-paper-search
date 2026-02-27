# Project Structure (项目结构)

## 目录树

```
paper-search/
├── paper_search.py              # 主 CLI 入口（AI Agent 调用）
│
├── config/                      # 配置管理
│   ├── config.py               # 配置类定义
│   └── .env                    # 环境变量（需创建）
│
├── script/                      # 核心功能模块
│   ├── pubmed_searcher.py      # PubMed 搜索（pymed）
│   ├── pdf_downloader.py       # 多策略 PDF 下载器
│   ├── impact_filter.py        # SJR 影响因子过滤
│   └── setup_sjr_simple.py     # SJR 数据导入助手
│
├── cache/                       # 数据缓存
│   └── sjr_metrics.db          # SJR 影响因子数据库
│
├── papers/                      # 检索结果存储
│   └── search_YYYYMMDD_HHMMSS/
│       ├── results.json        # 检索结果（JSON 格式）
│       ├── unavailable_papers.md # 无法下载的论文列表
│       └── pdfs/               # 下载的 PDF 文件
│
├── queries/                     # 查询文件存储
│   └── *.txt                   # 查询文本文件
│
├── venv/                        # Python 虚拟环境
│
├── .claude/                     # Claude Code 配置
│   └── .session_memory.md      # 会话记忆
│
├── README.md                    # 主文档
├── PUBMED_GUIDE.md             # PubMed 集成详细指南
├── OPTIMIZATION_SUMMARY.md     # 优化总结
├── CLAUDE.md                   # Claude Code 开发指南
└── PROJECT_STRUCTURE.md        # 本文件
```

---

## 核心文件说明

### 主程序

#### `paper_search.py`
- **功能：** 主 CLI 入口，AI Agent 调用接口
- **输入：** 检索查询（findpapers 格式）
- **输出：** JSON 格式结果 + PDF 文件
- **依赖：** 所有 script/ 模块

### 核心模块 (script/)

#### `pubmed_searcher.py`
- **功能：** PubMed 搜索（使用 pymed 库）
- **主要方法：**
  - `search()` - 搜索 PubMed
  - `_check_pmc_availability()` - 检测 PMC 开放获取
- **依赖：** pymed

#### `pdf_downloader.py`
- **功能：** 多策略 PDF 下载管理器
- **下载策略：**
  1. Unpaywall API（开放获取定位）
  2. PubMed Central（PMC 免费档案）
  3. 直接 PDF 链接
  4. 机构认证（可选）
- **依赖：** requests

#### `impact_filter.py`
- **功能：** SJR 影响因子过滤
- **主要方法：**
  - `import_sjr_csv()` - 导入 SJR 数据
  - `get_journal_sjr()` - 查询期刊 SJR 分数
  - `filter_papers_by_sjr()` - 按影响因子筛选
- **数据库：** SQLite3 (cache/sjr_metrics.db)

#### `setup_sjr_simple.py`
- **功能：** SJR 数据导入助手（简化版）
- **用途：** 帮助用户下载和导入 SJR 数据
- **支持模式：** 交互式 / 命令行

### 配置 (config/)

#### `config.py`
- **功能：** 统一配置管理
- **配置项：**
  - NCBI Email / API Key
  - SJR 数据库路径
  - PDF 下载选项
  - Unpaywall 设置

#### `.env`
- **功能：** 环境变量存储
- **示例：**
  ```bash
  NCBI_EMAIL=your_email@example.com
  NCBI_API_KEY=your_api_key
  MIN_SJR_SCORE=1.0
  ENABLE_UNPAYWALL=true
  ```

### 文档

#### `README.md`
- **内容：** 项目概述、快速开始、使用指南
- **目标读者：** AI Agent、开发者

#### `PUBMED_GUIDE.md`
- **内容：** PubMed 集成详细指南
- **包含：** SJR 设置、PDF 下载、API 配置

#### `OPTIMIZATION_SUMMARY.md`
- **内容：** 最新优化总结（2026-02-27）
- **包含：** 消除错误信息、优化下载策略

#### `CLAUDE.md`
- **内容：** Claude Code 开发指南
- **包含：** 项目架构、已知问题、开发笔记

---

## 数据流

### 检索流程

```
用户自然语言请求
    ↓
AI Agent 解析意图
    ↓
调用 paper_search.py
    ↓
┌─────────────────────────────┐
│ 根据模式选择搜索引擎          │
├─────────────────────────────┤
│ --pubmed-mode               │
│   ↓                         │
│ pubmed_searcher.py          │
│   - pymed 搜索 PubMed        │
│   - 检测 PMC 可用性          │
│                              │
│ 默认模式                     │
│   ↓                         │
│ findpapers                  │
│   - arXiv 搜索              │
│   - ACM 搜索                │
└─────────────────────────────┘
    ↓
应用筛选条件
    ├─ impact_filter.py (--min-sjr)
    ├─ 免费全文筛选 (--free-only)
    └─ 年份筛选 (--date-range)
    ↓
┌─────────────────────────────┐
│ PDF 下载                     │
├─────────────────────────────┤
│ pdf_downloader.py            │
│   1. Unpaywall API           │
│   2. PubMed Central          │
│   3. 直接链接                │
│   4. 机构认证                │
└─────────────────────────────┘
    ↓
生成输出
    ├─ results.json (结构化数据)
    ├─ unavailable_papers.md (无法下载列表)
    └─ pdfs/ (已下载的 PDF)
    ↓
返回 JSON 给 Agent
    ↓
Agent 生成自然语言回复给用户
```

---

## 依赖关系

```
paper_search.py
    ├── script/pubmed_searcher.py
    │   └── pymed
    ├── script/pdf_downloader.py
    │   └── requests
    ├── script/impact_filter.py
    │   └── sqlite3
    ├── config/config.py
    │   └── python-dotenv
    └── findpapers
        └── arxiv
```

---

## 环境要求

### Python 版本
- Python 3.12+

### 核心依赖
```bash
pip install findpapers arxiv pymed python-dotenv requests
```

### 可选依赖
```bash
# PaperQA（论文问答）
pip install paper-qa

# LLM 集成
pip install openai  # 或其他 LLM 提供商
```

---

## 快速参考

### 常用命令

```bash
# arXiv 搜索
python paper_search.py "[machine learning]" -l 10

# PubMed 搜索
python paper_search.py "[cancer]" --pubmed-mode -l 20

# 影响因子筛选
python paper_search.py "[AI]" --pubmed-mode --min-sjr 2.0 -l 20

# 仅免费全文
python paper_search.py "[biology]" --pubmed-mode --free-only -l 15

# 组合筛选
python paper_search.py "[sports] AND [rehabilitation]" \
    --pubmed-mode \
    --min-sjr 1.5 \
    --free-only \
    --date-range 2020 2024 \
    -l 30
```

### SJR 数据设置

```bash
# 交互式设置
python script/setup_sjr_simple.py

# 命令行导入
python script/setup_sjr_simple.py path/to/sjr_2024.csv 2024
```

---

**最后更新：** 2026-02-27
**维护者：** Claude Code Agent
