#!/usr/bin/env bash
# 加密文件管理器 - Linux/macOS 一键打包脚本

set -e

echo "=========================================="
echo "  加密文件管理器 - Linux/macOS 打包脚本"
echo "=========================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi

echo ""
echo "[1/3] 安装 Python 依赖..."
pip3 install -r requirements.txt

echo ""
echo "[2/3] 正在打包..."
pyinstaller --onefile --windowed --name "encrypted_file_manager" main.py

echo ""
echo "[3/3] 打包完成！"
echo "可执行文件位于: dist/encrypted_file_manager"
