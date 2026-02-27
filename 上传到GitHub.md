# 上传到 GitHub - 快速步骤

## 第一步：准备 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库：
   - Repository name: `paper-search`
   - Description: `AI Agent 驱动的论文检索工具`
   - 选择 Public 或 Private
   - **不要**勾选 "Add a README file"
   - 点击 "Create repository"

## 第二步：上传项目

在项目目录打开命令行（Git Bash 或 PowerShell）：

```bash
# 1. 初始化 Git
git init

# 2. 添加所有文件
git add .

# 3. 创建提交
git commit -m "Initial commit: Paper Search Assistant - AI Agent driven paper search tool"

# 4. 关联远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/paper-search.git

# 5. 推送到 GitHub
git push -u origin main
```

## 第三步：分享给女朋友

发送给她：

```
论文搜索工具：https://github.com/YOUR_USERNAME/paper-search

使用方法：
1. 点击网页右上角的 "Code" 按钮
2. 选择 "Download ZIP" 下载
3. 解压到任意位置
4. 告诉 Agent："帮我安装这个论文搜索工具"
```

## Agent 安装指令

让女朋友对她的 Agent 说：

```
请帮我安装这个论文搜索工具，位于 [解压的文件夹路径]
```

Agent 会自动：
✓ 检查 Python 环境
✓ 安装所有依赖
✓ 验证安装
✓ 测试搜索

## 常用查询示例

安装后，可以让 Agent 帮忙搜索：

```
搜索 10 篇关于 AI 的论文
搜索最近 5 年的医学 AI 论文（只要免费的）
搜索影响因子大于 2.0 的癌症研究论文
```

---

**就这么简单！** 🎉
