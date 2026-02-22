# 论文检索助手 - 使用指南

多数据库论文检索和下载工具，支持 arXiv、PubMed、ACM 等多个数据库。

## ✨ 功能特性

- 🔍 **多数据库检索** - 一键搜索 arXiv、PubMed、ACM
- 📥 **自动下载** - arXiv 论文自动下载 PDF
- 📊 **JSON 输出** - 结构化检索结果，易于处理
- 🤖 **AI Agent 优化** - 最小化 CLI 版本，专为 Copaw 等工具设计
- 🎯 **智能去重** - 自动识别和合并重复论文

## 📦 两种使用方式

### 方式 1：最小化 CLI（推荐用于 AI Agent）

**文件：** `paper_search.py`

**特点：**
- 专为 AI Agent 设计
- 清晰的 JSON 输出
- 标准退出码（0=成功，1=失败）
- 日志输出到 stderr（不干扰 JSON 解析）
- 轻量级（7.3KB）

**快速开始：**
```bash
# 激活虚拟环境
venv\Scripts\activate.bat

# 基础搜索
python paper_search.py "[machine learning]" -l 10

# JSON 输出（用于 Agent 解析）
python paper_search.py "[AI] AND [healthcare]" --json

# 多数据库搜索
python paper_search.py "[biology]" --limit-per-db 10 -l 50
```

**详细文档：** [docs/MINIMAL_CLI_USAGE.md](docs/MINIMAL_CLI_USAGE.md)

---

### 方式 2：完整版（保留备用）

**文件：** `script/paper_research.py`

**特点：**
- 自动打开结果文件夹
- 详细的控制台输出

**快速开始：**
```bash
# 使用命令行
python script\paper_research.py --query '["AI"] AND ["healthcare"]' -l 20
```

## 📋 系统要求

- Python 3.12+
- Windows 10/11
- 依赖：`findpapers`, `arxiv`

## 🚀 快速开始

### 1. 安装依赖

```bash
cd D:\projects\paper-search
venv\Scripts\activate.bat
pip install findpapers arxiv
```

### 2. 最小化 CLI（推荐）

```bash
# 基础搜索
python paper_search.py "[machine learning]" -l 10

# JSON 输出
python paper_search.py "[AI]" --json

# 多数据库
python paper_search.py "[biology]" --limit-per-db 10
```

## 📝 查询格式

### findpapers 格式（直接使用）

**基本规则：**
- ✅ 术语用方括号：`[term]`
- ✅ 布尔运算符大写：`AND`, `OR`, `AND NOT`
- ✅ 引号用于短语：`["machine learning"]`

**示例：**
```bash
# 单个术语
[biology]

# 短语搜索
["machine learning"]

# AND 查询
[AI] AND [healthcare]

# OR 查询
[deep learning] OR [neural networks]

# 复杂查询
([machine learning] OR [AI]) AND [healthcare]

# 排除特定术语
[deep learning] AND NOT [review]
```

**注意：** 最小化 CLI (`paper_search.py`) 直接使用 findpapers 格式，无需转换。

## 📂 输出结构

每次检索会在 `papers/` 目录下创建一个时间戳文件夹：

```
papers/
└── search_20260222_005601/
    ├── results.json    # 检索结果（JSON 格式）
    └── pdfs/           # 下载的 PDF 文件
        ├── 2401.12345.pdf
        └── 2402.67890.pdf
```

## 📄 结果文件格式 (JSON)

```json
{
  "number_of_papers": 10,
  "number_of_papers_by_database": {
    "arXiv": 5,
    "PubMed": 5
  },
  "papers": [
    {
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "abstract": "Abstract text...",
      "publication_date": "2026-02-22",
      "doi": "10.1234/example",
      "urls": ["https://arxiv.org/abs/2401.12345"],
      "keywords": ["AI", "healthcare"],
      "publication": {
        "title": "Journal Name",
        "category": "Journal"
      }
    }
  ]
}
```

## 🌐 支持的数据库

| 数据库 | 状态 | 说明 |
|--------|------|------|
| **arXiv** | ✅ 免费 | 计算机科学、物理、数学 |
| **PubMed** | ✅ 免费 | 生物医学、生命科学 |
| **ACM Digital Library** | ✅ 免费 | 计算机科学 |
| **IEEE** | ⚠️ 需 API | 工程技术（需注册） |
| **Scopus** | ⚠️ 需 API | 多学科（需订阅） |

### 配置 IEEE/Scopus API（可选）

```bash
# 设置环境变量
setx FINDPAPERS_IEEE_API_TOKEN "your_token"
setx FINDPAPERS_SCOPUS_API_TOKEN "your_token"
```

## 🛠️ 故障排除

### 问题 1：导入错误

```
错误：导入模块失败: No module named 'findpapers'
```

**解决：**
```bash
venv\Scripts\activate
pip install findpapers arxiv
```

### 问题 2：查询格式错误

```
错误：Invalid query format
```

**解决：** 确保查询格式正确
- ✅ 正确：`["AI"] AND ["healthcare"]`
- ❌ 错误：`"AI" AND "healthcare"`（缺少方括号）

### 问题 3：PDF 下载失败

**现象：** 显示 "未找到 PDF 下载链接"

**原因：** 非 arXiv 论文通常需要机构订阅

**解决：**
- arXiv 论文会自动下载
- 其他数据库的论文需手动下载（已提供 URL）

### 问题 4：编码错误

```
UnicodeEncodeError: 'gbk' codec can't encode
```

**解决：** 脚本已自动处理，如仍有问题，在命令行运行：
```bash
chcp 65001
```

## 📚 示例工作流

### 示例 1：快速检索

```bash
# 1. 激活环境
venv\Scripts\activate.bat

# 2. 运行检索
python script\paper_research.py --query '["large language models"]' -l 10

# 3. 查看结果
# 结果保存在 papers/search_XXXXXX_XXXXXX/results.json
```

### 示例 2：批量检索

```bash
# 1. 创建多个查询文件
echo '["AI"] AND ["ethics"]' > queries\ai_ethics.txt
echo '["machine learning"] AND ["healthcare"]' > queries\ml_healthcare.txt

# 2. 批量检索
python script\paper_research.py -q ai_ethics.txt
python script\paper_research.py -q ml_healthcare.txt
```

### 示例 3：集成到工作流

```python
# 在你的 Python 脚本中使用
from script.paper_research import PaperResearchAssistant

assistant = PaperResearchAssistant(
    query='["AI"] AND ["healthcare"]',
    limit=20,
    output_dir='papers/my_research'
)

assistant.run(notify=True)
```

## 🔗 相关链接

- [findpapers GitHub](https://github.com/jonatasgrosman/findpapers)
- [arXiv](https://arxiv.org/)
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
- [Copaw 文档](http://copaw.agentscope.io/docs/intro)

## 📝 更新日志

### 2026-02-22 下午
- ✅ **最小化 CLI 完成** - `paper_search.py`
- ✅ **Copaw 集成优化** - JSON 输出，标准退出码
- ✅ **UTF-8 安全输出** - 修复编码问题
- ✅ **文档更新** - [MINIMAL_CLI_USAGE.md](docs/MINIMAL_CLI_USAGE.md)

### 2026-02-22 上午
- ✅ 查询格式 Bug 修复
- ✅ 多数据库搜索实现
- ✅ findpapers arXiv API Bug 修复
- ✅ Web 界面完成

### 2026-02-21
- ✅ 项目初始化
- ✅ 环境搭建

---

**项目地址：** https://github.com/yourusername/paper-search
**最后更新：** 2026-02-22

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| [docs/MINIMAL_CLI_USAGE.md](docs/MINIMAL_CLI_USAGE.md) | 最小化 CLI 完整指南 |
| [docs/MULTI_DATABASE_SEARCH.md](docs/MULTI_DATABASE_SEARCH.md) | 多数据库搜索说明 |
| [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) | 快速参考 |
