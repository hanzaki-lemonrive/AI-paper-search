# Paper Search Assistant (论文检索助手)

> **AI Agent 驱动的学术论文检索工具**
> 实际执行者：AI Agent | 用户交互：自然语言

---

## 项目概述

这是一个专为 **AI Agent（如 Claude Code、Copaw）** 设计的论文检索和下载工具。用户只需用自然语言提出需求，Agent 会自动调用相应的检索命令并返回结果。

### 核心特性

- [x] **多数据库检索** - arXiv、PubMed、ACM 等
- [x] **影响因子筛选** - 基于 Scimago Journal Rank (SJR) 的期刊质量筛选
- [x] **智能 PDF 下载** - 自动尝试 PMC、Unpaywall、直接链接等多种方式
- [x] **免费全文筛选** - 仅检索可免费获取的论文
- [x] **JSON 格式输出** - 结构化结果，易于 Agent 解析
- [x] **标准退出码** - 0=成功，1=失败，便于 Agent 判断执行状态

---

## 🎯 使用场景（AI Agent 视角）

### 用户提问示例

```
User: "帮我找一些关于运动康复和脊柱的论文，要影响因子高的"

User: "搜索最近5年的深度学习在医学影像中的应用论文"

User: "下载 10 篇关于 AI 医疗应用的免费论文"

User: "找到 SJR 分数大于 2.0 的癌症研究论文"
```

### Agent 执行流程

1. **理解用户意图** - 提取关键词、筛选条件
2. **调用检索命令** - 执行相应的 CLI 命令
3. **解析 JSON 结果** - 提取关键信息
4. **生成自然语言回复** - 向用户展示结果

---

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd paper-search

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate.bat

# 安装基础依赖
pip install findpapers arxiv pymed python-dotenv requests
```

### 2. 配置环境变量（可选）

创建 `config/.env` 文件：

```bash
# NCBI / PubMed 配置（用于 PubMed 搜索）
NCBI_EMAIL=your_email@example.com
NCBI_API_KEY=your_api_key  # 可选，提高速率限制

# 影响因子筛选
MIN_SJR_SCORE=1.0  # 默认最小 SJR 分数

# PDF 下载选项
ENABLE_UNPAYWALL=true
```

### 3. 基础使用

#### arXiv 搜索（默认模式）

```bash
# 搜索 arXiv 论文
python paper_search.py "[machine learning]" -l 10

# JSON 输出（推荐给 Agent）
python paper_search.py "[deep learning]" --json -l 5
```

#### PubMed 专用模式（带影响因子筛选）

```bash
# 基础 PubMed 搜索
python paper_search.py "[cancer]" --pubmed-mode -l 10

# 按影响因子筛选（SJR >= 2.0）
python paper_search.py "[AI]" --pubmed-mode --min-sjr 2.0 -l 20

# 仅检索免费全文
python paper_search.py "[biology]" --pubmed-mode --free-only -l 15

# 组合筛选
python paper_search.py "[sports] AND [rehabilitation]" \
    --pubmed-mode \
    --min-sjr 1.5 \
    --free-only \
    --date-range 2020 2024 \
    -l 30
```

---

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `query` | 检索查询（必填） | `"[AI] AND [healthcare]"` |
| `-l, --limit` | 结果数量限制 | `-l 20` |
| `--pubmed-mode` | 启用 PubMed 专用模式 | `--pubmed-mode` |
| `--min-sjr` | 最小 SJR 分数 | `--min-sjr 2.0` |
| `--free-only` | 仅检索免费全文 | `--free-only` |
| `--date-range` | 按年份筛选 | `--date-range 2020 2024` |
| `--no-pdf` | 跳过 PDF 下载 | `--no-pdf` |
| `--json` | JSON 格式输出 | `--json` |

---

## 查询格式

### 基本规则

- 术语用方括号：`[term]`
- 布尔运算符大写：`AND`, `OR`, `AND NOT`
- 短语用引号：`["phrase"]`

### 示例

```bash
# 单个术语
[machine learning]

# AND 查询
[AI] AND [healthcare]

# OR 查询
[deep learning] OR [neural networks]

# 复杂查询
(["machine learning"] OR [AI]) AND [healthcare] AND NOT [review]

# PubMed 模式示例
"[sports rehabilitation] AND [spine]" --pubmed-mode
```

---

## 输出结构

每次检索会在 `papers/` 目录下创建一个时间戳文件夹：

```
papers/
└── search_20260227_204717/
    ├── results.json              # 检索结果（JSON 格式）
    ├── unavailable_papers.md     # 无法下载的论文列表
    └── pdfs/                     # 下载的 PDF 文件
        ├── PMID_41727319.pdf
        └── arxiv_2401.12345.pdf
```

### JSON 输出示例

```json
{
  "status": "success",
  "query": "[sports rehabilitation] AND [spine]",
  "total": 3,
  "papers": [
    {
      "title": "Current insights into circulating biomarkers",
      "authors": ["Author 1", "Author 2"],
      "year": "2026",
      "abstract": "...",
      "database": "PubMed",
      "pmid": "41727319",
      "doi": "10.3389/fcell.2026.1760636",
      "journal": "Frontiers in Cell Science",
      "sjr_score": 3.5,
      "sjr_quartile": "Q1",
      "has_free_full_text": true,
      "pdf_path": "papers/.../PMID_41727319.pdf",
      "pdf_downloaded": true
    }
  ]
}
```

---

## 高级功能

### SJR 影响因子筛选

SJR（Scimago Journal Rank）是衡量期刊学术影响力的指标。

#### 设置 SJR 数据库

```bash
# 运行交互式设置助手
python script/setup_sjr_simple.py

# 或直接导入 CSV 文件
python script/setup_sjr_simple.py path/to/sjr_2024.csv 2024
```

**注意：** SJR 数据需要从 [Scimago](https://www.scimagojr.com/) 手动下载（免费）。

#### 按影响因子筛选

```bash
# 仅检索 Q1 期刊（SJR >= 2.5）
python paper_search.py "[cancer]" --pubmed-mode --min-sjr 2.5 -l 20

# 仅检索 Q2 期刊（SJR >= 1.5）
python paper_search.py "[AI]" --pubmed-mode --min-sjr 1.5 -l 30
```

### 免费全文筛选

自动检测 Unpaywall 开放获取状态和 PMC 可用性：

```bash
# 仅检索有免费全文的论文
python paper_search.py "[biology]" --pubmed-mode --free-only -l 20
```

**成功率：** 约 15-25% 的论文有免费全文

---

## 支持的数据库

| 数据库 | 状态 | 说明 |
|--------|------|------|
| **arXiv** | ✅ 免费 | 计算机科学、物理、数学，PDF 自动下载 |
| **PubMed** | ✅ 免费 | 生物医学、生命科学，智能获取 PDF |
| **ACM Digital Library** | ✅ 免费 | 计算机科学，需手动下载 |
| **IEEE** | ⚠️ 需 API | 工程技术（需注册） |
| **Scopus** | ⚠️ 需 API | 多学科（需订阅） |

---

## Agent 集成指南

### Claude Code 使用示例

```python
# Agent 调用示例
def search_papers(query: str, limit: int = 10):
    """搜索论文并返回结构化结果"""
    import subprocess
    import json

    cmd = f"python paper_search.py \"{query}\" --json -l {limit}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data['papers']
    else:
        return None
```

### 返回给用户的自然语言回复

```python
def format_response(papers):
    """将检索结果转换为自然语言"""
    if not papers:
        return "抱歉，没有找到符合条件的论文。"

    response = f"找到 {len(papers)} 篇论文：\n\n"

    for i, paper in enumerate(papers, 1):
        response += f"{i}. **{paper['title']}**\n"
        response += f"   - 作者: {', '.join(paper['authors'][:3])}\n"
        response += f"   - 期刊: {paper.get('journal', 'N/A')}\n"
        response += f"   - 年份: {paper['year']}\n"
        if paper.get('sjr_score'):
            response += f"   - 影响因子: {paper['sjr_score']} ({paper['sjr_quartile']})\n"
        response += f"   - 链接: https://doi.org/{paper['doi']}\n\n"

    return response
```

---

## 故障排除

### 问题 1：模块未找到

```
ModuleNotFoundError: No module named 'pymed'
```

**解决：**
```bash
pip install pymed
```

### 问题 2：SJR 数据库为空

```
[INFO] SJR database is empty, cannot filter by impact factor
```

**解决：**
```bash
python script/setup_sjr_simple.py
```

### 问题 3：PDF 下载失败

**现象：** 大部分论文无法下载

**说明：** 这是正常现象
- 约 15-25% 的论文有免费全文
- 其余需要机构订阅或付费

### 问题 4：PubMed 速率限制

**现象：** 搜索速度慢

**解决：** 获取免费的 NCBI API Key
1. 访问 https://www.ncbi.nlm.nih.gov/account/
2. 注册账户并生成 API Key
3. 添加到 `config/.env`：`NCBI_API_KEY=your_key`

**效果：** 速率从 3 请求/秒提升到 10 请求/秒

---

## 项目结构

```
paper-search/
├── paper_search.py          # 主 CLI（Agent 调用入口）
├── config/
│   ├── config.py            # 配置管理
│   └── .env                 # 环境变量（需创建）
├── script/
│   ├── pubmed_searcher.py   # PubMed 搜索模块
│   ├── pdf_downloader.py    # PDF 下载管理器
│   ├── impact_filter.py     # SJR 影响因子过滤
│   └── setup_sjr_simple.py  # SJR 数据导入助手
├── papers/                  # 检索结果存储
├── queries/                 # 查询文件存储
├── venv/                    # Python 虚拟环境
├── README.md                # 本文件
├── PUBMED_GUIDE.md          # PubMed 集成详细指南
└── OPTIMIZATION_SUMMARY.md  # 优化总结
```

---

## 详细文档

| 文档 | 说明 |
|------|------|
| **[PUBMED_GUIDE.md](PUBMED_GUIDE.md)** | PubMed 集成完整指南 |
| **[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)** | 最新优化总结 |
| **[CLAUDE.md](CLAUDE.md)** | Claude Code 开发指南 |

---

## 常见问题 (FAQ)

### Q: 为什么很多论文无法下载 PDF？

A: 约 30-40% 的学术论文需要订阅。系统会自动尝试：
1. Unpaywall（开放获取）
2. PubMed Central（免费档案）
3. 直接链接（期刊网站）

只有约 15-25% 的论文能免费获取全文。

### Q: SJR 数据多久更新一次？

A: 建议每年更新一次。Scimago 通常在年初发布新数据。

### Q: 如何提高检索速度？

A:
1. 获取免费的 NCBI API Key（速率提升 3 倍）
2. 使用 `--free-only` 筛选减少结果数量
3. 使用 `--no-pdf` 跳过 PDF 下载

### Q: 支持中文检索吗？

A: 支持，但 PubMed 主要使用英文 MeSH 术语。建议使用英文关键词检索。

---

## 更新日志

### 2026-02-27
- 🆕 **PubMed 专用模式** - 使用 pymed 直接搜索 PubMed
- 🆕 **SJR 影响因子筛选** - 支持按期刊质量筛选
- 🆕 **多策略 PDF 下载** - Unpaywall + PMC + 直接链接
- 🆕 **SJR 数据导入助手** - 交互式设置工具
- ✅ **优化用户体验** - 消除错误信息，友好提示
- ✅ **完整文档** - PUBMED_GUIDE.md, OPTIMIZATION_SUMMARY.md

### 2026-02-22
- ✅ **最小化 CLI** - 专为 AI Agent 设计
- ✅ **JSON 输出** - 结构化结果，易于解析
- ✅ **标准退出码** - 便于 Agent 判断状态

---

## 许可证

MIT License

---

## 联系方式

- Issues: https://github.com/yourusername/paper-search/issues
- Email: your_email@example.com

---

**最后更新：** 2026-02-27
**维护者：** Claude Code Agent
**适用对象：** AI Agent（Claude Code、Copaw 等）
