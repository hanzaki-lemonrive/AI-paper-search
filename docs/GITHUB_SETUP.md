# GitHub 上传指南

## ✅ 已完成的清理

### 1. 创建 .gitignore
已排除以下文件：
- 虚拟环境：`venv/`
- 检索结果：`papers/`
- 敏感配置：`config/.env`
- 会话记忆：`.session_memory.md`
- 临时文件：`test_*/`, `*.pyc`, 等

### 2. 清理敏感信息
- ✅ README.md - 移除邮箱地址
- ✅ README.md - 移除作者信息
- ✅ CLAUDE.md - 移除邮箱和邮件通知引用
- ✅ 移除 Web 界面相关引用

## 📦 将上传到 GitHub 的文件

### 核心文件
```
paper-search/
├── .gitignore                  # ✅ Git 忽略规则
├── README.md                   # ✅ 主文档（已清理）
├── CLAUDE.md                   # ✅ Claude Code 指南（已清理）
├── paper_search.py             # ✅ 最小化 CLI
├── script/
│   └── paper_research.py       # ✅ 完整版
├── docs/
│   ├── MINIMAL_CLI_USAGE.md    # ✅ 使用指南
│   ├── MULTI_DATABASE_SEARCH.md # ✅ 多数据库说明
│   └── QUICK_REFERENCE.md      # ✅ 快速参考
├── config/
│   ├── config.py               # ✅ 配置模块
│   └── env.example             # ✅ 环境变量示例
└── queries/
    └── test_query.txt          # ✅ 示例查询
```

### 总大小
- **代码 + 文档：** ~100KB
- **不上传大文件：** venv/ (610MB), papers/ (93MB)

## 🚀 上传步骤

### 1. 初始化 Git 仓库

```bash
cd D:\projects\paper-search
git init
```

### 2. 添加文件

```bash
# 添加所有文件（.gitignore 会自动排除敏感文件）
git add .

# 检查将要上传的文件
git status
```

### 3. 创建首次提交

```bash
git commit -m "Initial commit: Paper Search Assistant

- Minimal CLI for AI agent consumption
- Multi-database search (arXiv, PubMed, ACM)
- Automatic PDF download for arXiv papers
- JSON output with clear exit codes
- Optimized for Copaw integration"
```

### 4. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库：`paper-search`
3. **不要**初始化 README、.gitignore 或 license（我们已经有了）
4. 点击 "Create repository"

### 5. 推送到 GitHub

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/paper-search.git

# 推送到主分支
git branch -M main
git push -u origin main
```

## 🔒 安全检查清单

### ✅ 已清理的敏感信息
- [x] 邮箱地址 (hanzaki@126.com)
- [x] 作者姓名
- [x] 真实项目路径

### 🚫 被 .gitignore 排除
- [x] `config/.env` - 包含 OPENAI_API_KEY
- [x] `.session_memory.md` - 包含会话历史
- [x] `papers/` - 检索结果（太大）
- [x] `venv/` - 虚拟环境（太大）
- [x] `test_*/` - 测试文件夹

### ⚠️ 用户需要自行配置
- [ ] 创建 `config/.env` 文件（参考 `config/env.example`）
- [ ] 添加自己的 API keys（如果需要 IEEE/Scopus）

## 📝 上传后的 README

README.md 中的以下信息需要用户自行替换：

```markdown
**项目地址：** https://github.com/yourusername/paper-search
```

## 🔧 常见问题

### Q: 如果不小心上传了敏感文件怎么办？

```bash
# 从 Git 历史中完全删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/.env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

### Q: 如何验证 .gitignore 是否生效？

```bash
# 检查哪些文件会被忽略
git check-ignore -v config/.env
git check-ignore -v papers/
git check-ignore -v .session_memory.md

# 应该显示匹配的 .gitignore 规则
```

### Q: 如何添加 License？

在 GitHub 仓库设置中：
1. Settings → Licenses
2. 选择合适的开源协议（推荐 MIT）

## 📊 预期的仓库大小

- **首次上传：** ~100KB（仅代码和文档）
- **克隆后：** 用户需要自行创建 `venv/` 和 `config/.env`

## ✅ 完成后的验证清单

- [ ] 访问 GitHub 仓库页面
- [ ] 检查文件列表（不应有 .env, papers/, venv/）
- [ ] 尝试 `git clone` 测试
- [ ] 按照 README 快速开始指南测试

---

**准备就绪！** 可以开始上传了。
