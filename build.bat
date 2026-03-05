@echo off
chcp 65001 > nul
echo ==========================================
echo   加密文件管理器 - Windows 一键打包脚本
echo ==========================================
echo.

REM 检查 Python 是否安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

REM 打包
echo.
echo [2/3] 正在打包为 exe...
pyinstaller --onefile --windowed --name "加密文件管理器" --icon=NONE main.py
if %errorlevel% neq 0 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo 可执行文件位于: dist\加密文件管理器.exe
echo.
pause
