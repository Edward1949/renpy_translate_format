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

:: 设置目录，如果用户提供了参数则使用，否则使用默认值
if "%1"=="" (
    set "schinese=.\schinese"
) else (
    set "schinese=%1"
)
if "%2"=="" (
    set "english=.\english"
) else (
    set "english=%2"
)
if "%3"=="" (
    set "format=.\format"
) else (
    set "format=%3"
)

echo 使用中文目录: %schinese%
echo 使用英文目录: %english%
echo 输出目录: %format%
echo.

:: 调用 interactive_format.py
python interactive_format.py --prepare "%schinese%" "%english%" "%format%"

:: 如果执行出错，暂停以便查看
if errorlevel 1 (
    echo.
    echo 程序执行出错，请检查上方信息。
    pause
)