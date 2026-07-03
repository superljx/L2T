"""
系统诊断工具
检测系统环境和依赖是否正确安装
"""

import sys
import io

# 设置stdout为UTF-8编码，避免Windows GBK编码错误
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import platform


def check_python_version():
    """检查Python版本"""
    print("[1/8] 检查Python版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python版本过低: {version.major}.{version.minor}")
        print(f"    需要Python 3.8或更高版本")
        return False


def check_platform():
    """检查操作系统"""
    print("\n[2/8] 检查操作系统...")
    system = platform.system()
    if system == "Windows":
        release = platform.release()
        print(f"  ✓ Windows {release}")
        return True
    else:
        print(f"  ⚠ 非Windows系统: {system}")
        print(f"    本程序设计用于Windows，可能无法正常工作")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n[3/8] 检查依赖包...")

    dependencies = {
        'mss': 'mss',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'win32gui': 'pywin32',
        'psutil': 'psutil',
        'pyautogui': 'pyautogui',
        'PIL': 'pillow'
    }

    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} 未安装")
            print(f"    安装命令: pip install {package}")
            all_ok = False

    return all_ok


def check_edge_browser():
    """检查Edge浏览器"""
    print("\n[4/8] 检查Edge浏览器...")
    import subprocess
    try:
        result = subprocess.run(
            ['where', 'msedge.exe'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✓ Edge浏览器已安装")
            print(f"    路径: {result.stdout.strip().splitlines()[0]}")
            return True
        else:
            print(f"  ✗ 未找到Edge浏览器")
            return False
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


def check_screen_capture():
    """检查屏幕捕捉"""
    print("\n[5/8] 检查屏幕捕捉...")
    try:
        from mss import mss
        import numpy as np

        with mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)

            print(f"  ✓ 屏幕捕捉正常")
            print(f"    分辨率: {img.shape[1]}x{img.shape[0]}")
            return True
    except Exception as e:
        print(f"  ✗ 屏幕捕捉失败: {e}")
        return False


def check_window_management():
    """检查窗口管理"""
    print("\n[6/8] 检查窗口管理...")
    try:
        import win32gui

        # 获取前台窗口
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)

        print(f"  ✓ 窗口管理功能正常")
        print(f"    当前窗口: {title[:50]}")
        return True
    except Exception as e:
        print(f"  ✗ 窗口管理失败: {e}")
        return False


def check_input_control():
    """检查输入控制"""
    print("\n[7/8] 检查输入控制...")
    try:
        import pyautogui

        # 获取屏幕尺寸
        size = pyautogui.size()

        print(f"  ✓ 输入控制功能正常")
        print(f"    屏幕尺寸: {size[0]}x{size[1]}")
        return True
    except Exception as e:
        print(f"  ✗ 输入控制失败: {e}")
        return False


def check_lol_process():
    """检查LOL进程（可选）"""
    print("\n[8/8] 检查LOL进程（可选）...")
    try:
        import psutil

        lol_running = False
        for proc in psutil.process_iter(['name']):
            if 'league' in proc.info['name'].lower():
                print(f"  ✓ 检测到LOL相关进程: {proc.info['name']}")
                lol_running = True
                break

        if not lol_running:
            print(f"  ℹ LOL未运行（这是正常的）")
            print(f"    使用时请先启动游戏")

        return True
    except Exception as e:
        print(f"  ⚠ 进程检查失败: {e}")
        return True  # 这不是关键错误


def run_diagnostics():
    """运行完整诊断"""
    print("=" * 60)
    print("系统诊断工具")
    print("=" * 60)
    print()

    results = []

    results.append(("Python版本", check_python_version()))
    results.append(("操作系统", check_platform()))
    results.append(("依赖包", check_dependencies()))
    results.append(("Edge浏览器", check_edge_browser()))
    results.append(("屏幕捕捉", check_screen_capture()))
    results.append(("窗口管理", check_window_management()))
    results.append(("输入控制", check_input_control()))
    results.append(("LOL进程", check_lol_process()))

    # 统计结果
    print("\n" + "=" * 60)
    print("诊断结果汇总")
    print("=" * 60)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")

    print()
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n✅ 所有检查通过！系统可以正常运行")
        print("\n下一步：")
        print("  1. 运行测试: python test_integration.py")
        print("  2. 启动程序: python main.py")
    else:
        print("\n⚠️ 存在问题需要解决")
        print("\n建议操作：")
        print("  1. 安装缺失的依赖包")
        print("  2. 检查系统环境配置")
        print("  3. 查看README.md获取更多帮助")

    print("=" * 60)


if __name__ == "__main__":
    try:
        run_diagnostics()
    except KeyboardInterrupt:
        print("\n\n用户中断诊断")
    except Exception as e:
        print(f"\n\n✗ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
