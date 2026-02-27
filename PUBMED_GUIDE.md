# PubMed 集成使用指南

## 功能概述

新增的 PubMed 集成功能包括：

1. **PubMed 专用搜索模式** - 使用 pymed 库直接搜索 PubMed
2. **多策略 PDF 下载** - PMC、Unpaywall、直接链接、机构认证
3. **SJR 影响因子筛选** - 基于 Scimago Journal Rank 的期刊质量筛选

---

## 快速开始

### 基础 PubMed 搜索

```bash
python paper_search.py "[machine learning]" --pubmed-mode -l 10
```

### 仅获取免费全文

```bash
python paper_search.py "[cancer]" --pubmed-mode --free-only -l 15
```

### 按影响因子筛选

```bash
python paper_search.py "[AI]" --pubmed-mode --min-sjr 2.0 -l 20
```

### 组合筛选

```bash
python paper_search.py "[deep learning] AND [healthcare]" \
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
| `--pubmed-mode` | 启用 PubMed 专用搜索模式 | `--pubmed-mode` |
| `--min-sjr` | 最小 SJR 分数（影响因子筛选） | `--min-sjr 2.0` |
| `--free-only` | 仅检索有免费全文的文章 | `--free-only` |
| `--date-range` | 按发表年份筛选 | `--date-range 2020 2024` |
| `-l` | 结果数量限制 | `-l 20` |
| `--no-pdf` | 跳过 PDF 下载 | `--no-pdf` |

---

## 配置环境变量

在 `config/.env` 文件中添加：

```bash
# NCBI / PubMed 配置
NCBI_EMAIL=your_email@example.com
NCBI_API_KEY=your_api_key_here  # 可选，提高速率限制

# 影响因子筛选
MIN_SJR_SCORE=1.0  # 默认最小 SJR 分数

# PDF 下载选项
ENABLE_UNPAYWALL=true
```

### 获取 NCBI API Key（可选但推荐）

1. 访问 https://www.ncbi.nlm.nih.gov/account/
2. 创建免费账户
3. 在账户设置中生成 API Key
4. 添加到 `.env` 文件

**好处：**
- 无 Key: 3 请求/秒
- 有 Key: 10 请求/秒

---

## SJR 影响因子数据设置

Scimago Journal Rank (SJR) 不提供公共 API，需要手动下载：

### 🚀 快速设置（推荐）

运行交互式设置助手：

```bash
python script/setup_sjr.py
```

助手会引导你完成下载和导入过程。

### 手动设置步骤

#### 步骤 1: 下载 SJR 数据

1. 访问 https://www.scimagojr.com/
2. 点击 "Journal Rankings"
3. 配置筛选条件：
   - Year: 选择最新年份（如 2024）
   - Areas: 选择相关领域（或选择 "All Areas"）
   - Categories: 选择相关类别
4. 点击 "Export" → "CSV"
5. 保存到 `cache/sjr_2024.csv`

#### 步骤 2: 导入数据库

**方法 A - 使用设置助手（推荐）：**
```bash
python script/setup_sjr.py cache/sjr_2024.csv 2024
```

**方法 B - 直接导入：**
```bash
python -c "from pathlib import Path; from script.impact_filter import ImpactFactorFilter; f = ImpactFactorFilter(); f.import_sjr_csv(Path('cache/sjr_2024.csv'), 2024)"
```

#### 步骤 3: 验证导入

```bash
python script/impact_filter.py
```

应该会显示：
```
数据库状态:
  路径: D:\projects\paper-search\cache\sjr_metrics.db
  期刊数: XXXX
```

### ⚠️ 重要提示

- **SJR 数据是可选的** - 如果不使用 `--min-sjr` 参数，不需要设置
- **数据更新** - 建议每年更新一次（Scimago 通常在年初发布新数据）
- **文件大小** - 完整的 SJR CSV 文件可能很大（~50MB），导入需要几分钟

---

## PDF 下载策略

系统按以下优先级尝试下载 PDF：

1. **PubMed Central (PMC)** - 完全免费的开放获取文章
2. **Unpaywall API** - 合法的开放获取定位器
3. **直接 PDF 链接** - 检查 URL 中的 .pdf 链接
4. **机构认证** - 如果配置了机构访问凭据

### 配置机构访问

在 `config/.env` 中添加：

```bash
INSTITUTIONAL_PROXY=https://your-library.edu/login
INSTITUTION_USERNAME=your_username
INSTITUTION_PASSWORD=your_password
```

---

## 输出示例

### 命令输出

```
使用 PubMed 搜索模式...
搜索查询: machine learning[All Fields]
找到 10 篇论文

下载 PDFs...
  [1/10] Machine learning in healthcare...
    ✓ PMC 下载成功: PMID_12345678.pdf
  [2/10] Deep learning for diagnosis...
    ✓ Unpaywall 下载成功: doi_10_1234_example.pdf

✓ 下载完成: 2/10 篇
```

### JSON 输出（使用 `--json` 参数）

```json
{
  "status": "success",
  "query": "[machine learning]",
  "total": 3,
  "papers": [
    {
      "title": "Machine learning in healthcare",
      "authors": ["Author 1", "Author 2"],
      "year": "2023",
      "abstract": "...",
      "database": "PubMed",
      "pmid": "12345678",
      "doi": "10.1234/example",
      "has_pmc": true,
      "sjr_score": 3.5,
      "sjr_quartile": "Q1",
      "pdf_path": "/path/to/pmc_12345678.pdf",
      "pdf_downloaded": true,
      "pdf_source": "PMC"
    }
  ]
}
```

---

## 常见问题

### Q: 为什么有些论文无法下载 PDF？

A: 约 30-40% 的学术论文需要付费订阅。系统会自动尝试查找免费版本，但部分文章只能通过机构订阅或直接购买获取。

### Q: SJR 数据需要多久更新一次？

A: 建议每年更新一次。Scimago 通常在每年年初发布新的排名数据。

### Q: 如何知道期刊的 SJR 分数？

A: 使用以下命令查询顶级期刊：

```bash
python -c "from script.impact_filter import ImpactFactorFilter; f = ImpactFactorFilter(); import json; print(json.dumps(f.list_top_journals(10), indent=2))"
```

### Q: 搜索速度太慢怎么办？

A: 获取 NCBI API Key（免费），速率限制将从 3 请求/秒提升到 10 请求/秒。

---

## 实用示例

### 搜索高质量医学期刊

```bash
python paper_search.py "[cardiovascular] AND [therapy]" \
    --pubmed-mode \
    --min-sjr 3.0 \
    --free-only \
    -l 20
```

### 搜索最近 5 年的 AI 论文

```bash
python paper_search.py "[artificial intelligence]" \
    --pubmed-mode \
    --date-range 2019 2024 \
    --min-sjr 1.5 \
    -l 50
```

### 仅下载 PDF，不保存其他信息

```bash
python paper_search.py "[cancer immunotherapy]" \
    --pubmed-mode \
    --free-only \
    -l 10
```

---

## 模块文件说明

| 文件 | 功能 |
|------|------|
| `script/pubmed_searcher.py` | PubMed 搜索核心模块 |
| `script/pdf_downloader.py` | 多策略 PDF 下载器 |
| `script/impact_filter.py` | SJR 影响因子过滤器 |
| `config/config.py` | 配置管理（已扩展） |
| `paper_search.py` | 主 CLI（已集成新模式） |

---

## 技术支持

- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- NCBI E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- Scimago Journal Rank: https://www.scimagojr.com/
- Unpaywall: https://unpaywall.org/
