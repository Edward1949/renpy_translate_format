@echo off
chcp 65001 >nul 2>&1

echo ====================================
echo   RenPy 翻译工具集 - 一键启动脚本
echo ====================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.11 或更高版本。
    echo 下载地址：https://www.python.org/downloads/
    echo.
    echo 安装时请务必勾选 "Add Python to PATH" 选项。
    echo.
    pause
    exit /b 1
)

echo [信息] Python 已安装：
python --version
echo.

REM 检查并安装依赖
if exist requirements.txt (
    echo [信息] 正在安装/更新依赖（colorama）...
    pip install -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo [警告] 依赖安装失败，请检查网络或手动安装。
        echo 可执行：pip install colorama
        echo.
    ) else (
        echo [信息] 依赖安装成功。
    )
) else (
    echo [信息] 未找到 requirements.txt，跳过依赖安装。
    echo 如需手动安装依赖，请运行：pip install colorama
)

echo.
echo [信息] 启动交互式界面...
echo.

REM 调用主程序，传递所有命令行参数
python interactive_format.py %*

REM 如果执行出错，暂停
if errorlevel 1 (
    echo.
    echo [错误] 程序执行失败，请检查上方输出信息。
    pause
) else (
    echo.
    echo [信息] 程序执行完毕。
    echo 如果中文显示为乱码，请将控制台字体设置为支持中文的字体（如 Consolas, 微软雅黑）。
    timeout /t 5 >nul 2>&1
)