#!/usr/bin/env bash
# 同步 toutiao_publisher 技能更新到 GitHub
# 每次更新技能后运行此脚本

cd "$(dirname "$0")"

# 添加所有更新文件
git add -A

# 检查是否有变动
if git diff --cached --quiet; then
    echo "[*] 没有更新，跳过"
    exit 0
fi

# 提交并推送
git commit -m "update: $(date '+%Y-%m-%d %H:%M')"
git push -u origin main 2>&1 || git push -u origin master 2>&1

echo "[✓] 已同步到 GitHub"
