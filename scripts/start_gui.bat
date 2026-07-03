@echo off
chcp 65001 > nul
echo ====================================
echo LOL 自动切换系统 GUI
echo ====================================
echo.
echo 正在启动图形界面...
echo.
python gui.py
if errorlevel 1 (
    echo.
    echo 启动失败！
    echo 请确保已安装所有依赖：
    echo pip install customtkinter pillow
    echo.
    pause
)
