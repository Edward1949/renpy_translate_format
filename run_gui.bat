@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
echo 正在启动 RenPy 翻译工具 GUI...
python gui_tkinter.py 
pause