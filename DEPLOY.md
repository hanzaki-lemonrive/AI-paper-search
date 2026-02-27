# 项目部署指南

> 通过 AI Agent 部署本项目

---

## 方案一：GitHub 部署（推荐）

### 步骤 1：上传到 GitHub

```bash
# 1. 初始化 Git 仓库
git init

# 2. 添加所有文件
git add .

# 3. 创建首次提交
git commit -m "Initial commit: Paper Search Assistant"

# 4. 在 GitHub 创建仓库（访问 github.com）
# 仓库名: paper-search

# 5. 关联远程仓库
git remote add origin https://github.com/yourusername/paper-search.git

# 6. 推送到 GitHub
git push -u origin main
```

### 步骤 2：分享给女朋友

**发送给她的信息：**

```
论文搜索工具链接：https://github.com/yourusername/paper-search

使用方法：
1. 点击网页右上角的 "Code" 按钮
2. 选择 "Download ZIP"
3. 解压到任意位置（比如桌面）
4. 告诉 Agent："帮我安装这个论文搜索工具"
```

---

## 方案二：直接发送项目文件夹

### Windows

1. **压缩项目文件夹：**
   - 右键 `paper-search` 文件夹
   - 发送到 → 压缩(zipped)文件夹
   - 生成 `paper-search.zip`

2. **通过微信/网盘发送**

3. **告诉她：**
   ```
   解压这个文件夹，然后告诉 Agent："帮我安装这个工具"
   ```

---

## Agent 安装指令

让女朋友对她的 Agent 说以下任一指令：

### 指令 1：完整安装

```
请帮我安装这个论文搜索工具：
1. 检查是否安装了 Python
2. 安装所有依赖包
3. 验证安装是否成功
```

### 指令 2：快速安装

```
帮我设置这个论文搜索工具，我要用它搜论文
```

### 指令 3：搜索测试

```
安装完成后，帮我搜索 5 篇关于 AI 的论文
```

---

## Agent 需要执行的任务

如果你要手动指导 Agent，以下是完整步骤：

### 1. 检查环境

```bash
# 检查 Python 版本
python --version

# 应该显示 Python 3.12+
```

### 2. 创建虚拟环境

```bash
cd paper-search
python -m venv venv
```

### 3. 安装依赖

```bash
# Windows
venv\Scripts\activate
pip install findpapers arxiv pymed python-dotenv requests

# Mac/Linux
source venv/bin/activate
pip install findpapers arxiv pymed python-dotenv requests
```

### 4. 验证安装

```bash
python paper_search.py --help
```

应该显示帮助信息

### 5. 测试搜索

```bash
python paper_search.py "[AI]" -l 3 --no-pdf
```

---

## 给女朋友的使用说明

### 日常使用（通过 Agent）

**示例对话 1：**
```
女朋友：帮我在这个工具里搜索 10 篇关于医学 AI 的论文
Agent：[调用搜索命令]
找到 10 篇论文，已下载到 papers 文件夹
```

**示例对话 2：**
```
女朋友：搜索最近 5 年的机器学习论文，只要免费的
Agent：[执行命令]
python paper_search.py "[machine learning]" --pubmed-mode --free-only --date-range 2020 2024 -l 10
```

**示例对话 3：**
```
女朋友：搜索影响因子高的癌症研究论文
Agent：[执行命令]
python paper_search.py "[cancer]" --pubmed-mode --min-sjr 2.0 -l 15
```

---

## 快速参考卡

### 常用查询（通过 Agent）

| 需求 | 对 Agent 说的话 |
|------|----------------|
| 搜索 AI 论文 | "搜索 10 篇 AI 论文" |
| 搜索医学论文 | "搜索 15 篇医学论文" |
| 搜索免费论文 | "搜索 10 篇免费的 AI 论文" |
| 搜索高质量论文 | "搜索影响因子大于 2 的论文" |
| 搜索特定领域 | "搜索 [你想要的主题] 论文" |

### Agent 执行的命令

```bash
# 基础搜索
python paper_search.py "[主题]" -l 10

# PubMed 搜索
python paper_search.py "[主题]" --pubmed-mode -l 20

# 免费论文
python paper_search.py "[主题]" --pubmed-mode --free-only -l 15

# 影响因子筛选
python paper_search.py "[主题]" --pubmed-mode --min-sjr 2.0 -l 20
```

---

## 故障排除（Agent 用）

### 问题 1：Python 未安装

**Agent 应该：**
1. 提示用户安装 Python
2. 提供安装链接：https://www.python.org/downloads/
3. 强调勾选 "Add Python to PATH"

### 问题 2：依赖安装失败

**Agent 应该：**
1. 检查网络连接
2. 尝试使用镜像源：
   ```bash
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple findpapers arxiv pymed python-dotenv requests
   ```

### 问题 3：搜索无结果

**Agent 应该：**
1. 解释这是正常的（70% 论文需付费）
2. 建议使用 `--free-only` 参数
3. 建议使用英文关键词

---

## 文件清单

### 核心文件（必须）

```
paper-search/
├── paper_search.py          # 主程序
├── config/
│   ├── config.py
│   └── .env.example         # 环境变量模板
├── script/
│   ├── pubmed_searcher.py
│   ├── pdf_downloader.py
│   ├── impact_filter.py
│   └── setup_sjr_simple.py
├── queries/                 # 预设查询
│   └── *.txt
├── README.md                # 主文档
├── DEPLOY.md                # 本文件
└── requirements.txt         # 依赖列表（需创建）
```

### 建议添加

创建 `requirements.txt` 方便安装：

```txt
findpapers>=0.3.0
arxiv>=2.1.0
pymed>=0.9.0
python-dotenv>=1.0.0
requests>=2.31.0
```

---

## 推荐方案总结

**最简单的方式：**

1. ✅ 上传到 GitHub
2. ✅ 发送 GitHub 链接给女朋友
3. ✅ 她的 Claude Code Agent 自动完成安装

**次选方案：**

1. ✅ 压缩项目文件夹
2. ✅ 通过网盘/微信发送
3. ✅ 她的 Agent 自动完成安装

---

**注意：** 本项目专为 AI Agent 设计，用户不需要懂编程！

---

*最后更新：2026-02-27*
