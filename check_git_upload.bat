@echo off
echo ========================================
echo GitHub 上传前检查
echo ========================================
echo.

echo [1] 检查 .gitignore 是否存在...
if exist .gitignore (
    echo   ✓ .gitignore 已创建
) else (
    echo   ✗ .gitignore 不存在！
    echo.
    pause
    exit /b 1
)
echo.

echo [2] 检查敏感文件是否被排除...
echo   检查 config/.env...
git check-ignore -q config/.env 2>nul
if %errorlevel% equ 0 (
    echo   ✓ config/.env 已被排除
) else (
    echo   ✗ 警告：config/.env 会被上传！
)
echo   检查 .session_memory.md...
git check-ignore -q .session_memory.md 2>nul
if %errorlevel% equ 0 (
    echo   ✓ .session_memory.md 已被排除
) else (
    echo   ✗ 警告：.session_memory.md 会被上传！
)
echo   检查 papers/...
git check-ignore -q papers/ 2>nul
if %errorlevel% equ 0 (
    echo   ✓ papers/ 已被排除
) else (
    echo   ✗ 警告：papers/ 会被上传！
)
echo   检查 venv/...
git check-ignore -q venv/ 2>nul
if %errorlevel% equ 0 (
    echo   ✓ venv/ 已被排除
) else (
    echo   ✗ 警告：venv/ 会被上传！
)
echo.

echo [3] 检查是否有敏感信息残留...
findstr /S /I "hanzaki@126.com" *.md *.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✗ 警告：文件中发现邮箱地址！
    echo   运行以下命令查看：
    echo   findstr /S /I "hanzaki@126.com" *.md *.py
) else (
    echo   ✓ 未发现邮箱地址
)
echo.

echo [4] 将要上传的文件列表...
echo   运行以下命令查看完整列表：
echo   git ls-files
echo.

echo [5] 预估上传大小...
echo   代码 + 文档：~100KB
echo   （已排除：venv/ 610MB, papers/ 93MB）
echo.

echo ========================================
echo 检查完成！
echo ========================================
echo.
echo 如果所有检查都通过（显示 ✓），可以安全上传。
echo.
echo 下一步：
echo   1. git init
echo   2. git add .
echo   3. git status（检查文件列表）
echo   4. git commit -m "Initial commit"
echo   5. 在 GitHub 创建仓库
echo   6. git remote add origin https://github.com/YOUR_USERNAME/paper-search.git
echo   7. git push -u origin main
echo.
pause
