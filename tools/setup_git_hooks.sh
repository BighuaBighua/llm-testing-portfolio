#!/bin/bash
#
# Git Hooks 启用脚本
# 功能：启用自动更新文档的 Git Hook
#

set -e

echo "🔧 Git Hooks 启用脚本"
echo "================================"
echo

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    echo "❌ 错误：当前目录不是 Git 仓库"
    exit 1
fi

# 检查 .githooks 目录是否存在
if [ ! -d ".githooks" ]; then
    echo "❌ 错误：.githooks 目录不存在"
    exit 1
fi

# 启用 Git Hooks
echo "📝 配置 Git 使用 .githooks 目录..."
git config core.hooksPath .githooks

# 验证配置
HOOKS_PATH=$(git config --get core.hooksPath)
if [ "$HOOKS_PATH" = ".githooks" ]; then
    echo "✅ Git Hooks 已启用"
    echo
    echo "📋 当前配置："
    echo "  Git Hooks 路径: .githooks/"
    echo "  pre-commit: 自动更新文档"
    echo
    echo "🎯 功能说明："
    echo "  - 每次执行 git commit 时，会自动检查 project_data.json 是否有变化"
    echo "  - 如果有变化，会自动运行 python3 tools/generate_docs.py --auto-update"
    echo "  - 更新后的文档会自动添加到暂存区"
    echo
    echo "💡 手动运行文档生成器："
    echo "  python3 tools/generate_docs.py              # 生成内容，手动替换"
    echo "  python3 tools/generate_docs.py --auto-update # 自动更新所有文档"
    echo
    echo "🚫 禁用 Git Hooks："
    echo "  git config --unset core.hooksPath"
else
    echo "❌ 配置失败"
    exit 1
fi

echo
echo "================================"
echo "✅ 设置完成！"
