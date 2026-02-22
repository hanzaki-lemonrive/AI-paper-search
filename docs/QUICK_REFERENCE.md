# 🎯 快速参考 - 论文检索助手

## ⚡ 30 秒快速开始

```bash
1. 双击: start_advanced.bat
2. 打开: http://localhost:5000
3. 输入: machine learning and healthcare
4. 点击: 开始检索
5. 等待 10-30 秒
6. 点击: 📂 打开文件夹按钮
```

---

## 📁 论文保存在哪里？

### 默认位置

```
D:\projects\paper-search\papers\search_YYYYMMDD_HHMMSS\
├── results.json    # 检索结果
└── pdfs\           # 下载的 PDF
    ├── paper1.pdf
    └── paper2.pdf
```

### 自定义位置

**Web 界面：**
- 在"保存位置"输入框填写路径
- 相对路径：`my_papers`
- 绝对路径：`D:\MyDocuments\Research`

**命令行：**
```bash
-o my_papers           # 相对路径
-o "D:\MyDocs"         # 绝对路径
```

---

## ✅ 已修复的问题

| 问题 | 状态 | 说明 |
|------|------|------|
| ❌ 邮件通知 | ✅ 已移除 | 不再发送邮件 |
| ❌ 文件位置不明确 | ✅ 已修复 | 清晰显示位置 + 自动打开 |
| ❌ 无法自定义路径 | ✅ 已添加 | 支持相对/绝对路径 |

---

## 🔑 GLM-4 API Key 配置

### 是否需要配置？

- ❌ **检索功能**：不需要
- ✅ **问答功能**：需要

### 配置步骤

1. 访问 https://open.bigmodel.cn/
2. 创建 API Key
3. 打开 Web 界面 → 设置标签页
4. 粘贴 API Key
5. 点击"保存配置"

详见：[docs/GLM4_API_SETUP.md](GLM4_API_SETUP.md)

---

## 📖 重要文档

| 文档 | 说明 |
|------|------|
| [docs/QUICK_START.md](QUICK_START.md) | 快速开始 ⭐⭐⭐ |
| [docs/GLM4_API_SETUP.md](GLM4_API_SETUP.md) | API 配置指南 ⭐⭐ |
| [docs/FIXES.md](FIXES.md) | 本次修改说明 ⭐⭐ |
| [docs/FINAL_SUMMARY.md](FINAL_SUMMARY.md) | 完整总结 |

---

**最后更新：** 2026-02-22
