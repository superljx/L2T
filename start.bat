@echo off
chcp 65001 >nul
echo ========================================
echo LOL 自动切换系统 - 快速启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
python -c "import mss, cv2, win32gui, pyautogui" >nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到缺失依赖，正在安装...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo [完成] 依赖安装成功
) else (
    echo [完成] 依赖已安装
)

echo.
echo [2/3] 运行系统诊断...
python diagnostics.py
if errorlevel 1 (
    echo.
    echo [警告] 诊断发现问题，建议修复后再运行
    echo.
    choice /C YN /M "是否继续启动程序"
    if errorlevel 2 exit /b 1
)

echo.
echo [3/3] 启动主程序...
echo.
python main.py

pause
