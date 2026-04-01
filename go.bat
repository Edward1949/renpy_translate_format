@echo off
chcp 65001 > nul
echo 正在启动交互式翻译处理工具...
echo 若需帮助，请使用 --help 参数查看可用选项。
echo.

:: 检查 Python 是否可用
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python 命令，请确保 Python 已安装并加入 PATH。
    pause
    exit /b 1
)

:: 调用 interactive_format.py，将所有命令行参数传递给它
python interactive_format.py %format

:: 如果执行出错，暂停以便查看
if errorlevel 1 (
    echo.
    echo 程序执行出错，请检查上方信息。
    pause
)