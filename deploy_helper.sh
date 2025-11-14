#!/bin/bash

# 部署辅助脚本
# 用于检查部署前的准备工作

echo "=========================================="
echo "832工程 - 部署前检查"
echo "=========================================="

# 检查必要文件
echo ""
echo "1. 检查必要文件..."
files=("Procfile" "runtime.txt" "requirements.txt" "backend/app.py" "backend/db.py" "frontend/index.html")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file 存在"
    else
        echo "✗ $file 缺失"
    fi
done

# 检查Python依赖
echo ""
echo "2. 检查Python依赖..."
if command -v python3 &> /dev/null; then
    echo "✓ Python3 已安装"
    python3 --version
else
    echo "✗ Python3 未安装"
fi

# 检查Git状态
echo ""
echo "3. 检查Git状态..."
if [ -d ".git" ]; then
    echo "✓ Git仓库已初始化"
    echo "当前分支: $(git branch --show-current)"
    echo "未提交的更改:"
    git status --short
else
    echo "⚠ Git仓库未初始化"
    echo "建议运行: git init"
fi

# 检查数据库配置
echo ""
echo "4. 检查数据库配置..."
if grep -q "os.getenv" backend/db.py; then
    echo "✓ 数据库配置支持环境变量"
else
    echo "✗ 数据库配置需要更新"
fi

# 检查前端API配置
echo ""
echo "5. 检查前端API配置..."
if grep -q "window.API_BASE" frontend/index.html; then
    echo "✓ 前端API配置已设置"
else
    echo "✗ 前端API配置需要更新"
fi

echo ""
echo "=========================================="
echo "检查完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 确保代码已提交到GitHub"
echo "2. 按照 DEPLOY.md 中的步骤部署"
echo "3. 部署后端到 Railway"
echo "4. 部署前端到 Vercel"
echo ""

