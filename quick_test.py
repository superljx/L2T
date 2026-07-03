"""
快速测试脚本 - 验证所有模块是否正常工作
"""

def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("快速测试 - 模块导入检查")
    print("=" * 60)

    modules = [
        ('config', 'Config'),
        ('utils', 'setup_logger'),
        ('detector', 'GameStateDetector'),
        ('window_manager', 'WindowManager'),
        ('browser_controller', 'BrowserController'),
        ('input_controller', 'InputController'),
    ]

    all_ok = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_name}.{class_name} - {e}")
            all_ok = False

    return all_ok


def test_dependencies():
    """测试依赖库"""
    print("\n" + "=" * 60)
    print("快速测试 - 依赖库检查")
    print("=" * 60)

    deps = {
        'mss': 'mss',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'win32gui': 'pywin32',
        'psutil': 'psutil',
        'pyautogui': 'pyautogui',
    }

    all_ok = True
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - 未安装")
            all_ok = False

    return all_ok


def test_basic_functionality():
    """测试基础功能"""
    print("\n" + "=" * 60)
    print("快速测试 - 基础功能检查")
    print("=" * 60)

    all_ok = True

    # 测试截图
    try:
        from mss import mss
        import numpy as np

        with mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            img = np.array(screenshot)
        print(f"  ✓ 屏幕捕捉 ({img.shape[1]}x{img.shape[0]})")
    except Exception as e:
        print(f"  ✗ 屏幕捕捉 - {e}")
        all_ok = False

    # 测试窗口管理
    try:
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        print(f"  ✓ 窗口管理")
    except Exception as e:
        print(f"  ✗ 窗口管理 - {e}")
        all_ok = False

    # 测试配置验证
    try:
        from config import Config
        Config.validate()
        print(f"  ✓ 配置验证")
    except Exception as e:
        print(f"  ✗ 配置验证 - {e}")
        all_ok = False

    return all_ok


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "    LOL 自动切换系统 - 快速测试工具".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    results = []

    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("依赖库", test_dependencies()))
    results.append(("基础功能", test_basic_functionality()))

    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = "✓ 通过" if ok else "✗ 失败"
        print(f"  {status:8s} {name}")

    print("\n" + "─" * 60)
    print(f"  总计: {passed}/{total} 通过")
    print("=" * 60)

    if passed == total:
        print("\n✅ 所有测试通过！")
        print("\n下一步：")
        print("  • 运行完整测试: python test_integration.py")
        print("  • 启动主程序: python main.py")
        print("  • 或直接运行: start.bat")
    else:
        print("\n⚠️ 存在失败的测试项")
        print("\n建议操作：")
        print("  • 运行诊断: python diagnostics.py")
        print("  • 查看文档: README.md")
        print("  • 安装依赖: pip install -r requirements.txt")

    print("\n" + "=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
