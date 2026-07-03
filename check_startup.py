"""
快速启动检查脚本
在运行主程序前检查所有必需的模块
"""

import sys

print("=" * 60)
print("启动检查")
print("=" * 60)
print()

errors = []

# 检查基础模块
print("[1/7] 检查基础模块...")
try:
    from config import Config
    print("  ✓ config.py")
except Exception as e:
    print(f"  ✗ config.py - {e}")
    errors.append(f"config: {e}")

try:
    from utils import setup_logger
    print("  ✓ utils.py")
except Exception as e:
    print(f"  ✗ utils.py - {e}")
    errors.append(f"utils: {e}")

# 检查检测器
print("\n[2/7] 检查检测器模块...")
try:
    from detector import GameStateDetector
    print("  ✓ detector.py")
except Exception as e:
    print(f"  ✗ detector.py - {e}")
    errors.append(f"detector: {e}")

# 检查窗口管理
print("\n[3/7] 检查窗口管理模块...")
try:
    from window_manager import WindowManager
    print("  ✓ window_manager.py")
except Exception as e:
    print(f"  ✗ window_manager.py - {e}")
    errors.append(f"window_manager: {e}")

# 检查浏览器控制
print("\n[4/7] 检查浏览器控制模块...")
try:
    from browser_controller import BrowserController
    print("  ✓ browser_controller.py")
except Exception as e:
    print(f"  ✗ browser_controller.py - {e}")
    errors.append(f"browser_controller: {e}")

# 检查输入控制
print("\n[5/7] 检查输入控制模块...")
try:
    from input_controller import InputController
    print("  ✓ input_controller.py")
except Exception as e:
    print(f"  ✗ input_controller.py - {e}")
    errors.append(f"input_controller: {e}")

# 检查主程序
print("\n[6/7] 检查主程序...")
try:
    from main import AutoSwitchController
    print("  ✓ main.py")
except Exception as e:
    print(f"  ✗ main.py - {e}")
    errors.append(f"main: {e}")

# 检查配置验证
print("\n[7/7] 验证配置...")
try:
    from config import Config
    Config.validate()
    print("  ✓ 配置验证通过")
except Exception as e:
    print(f"  ✗ 配置验证失败 - {e}")
    errors.append(f"config validation: {e}")

# 总结
print("\n" + "=" * 60)
print("检查结果")
print("=" * 60)

if not errors:
    print("\n✅ 所有检查通过！可以运行主程序")
    print("\n启动命令：")
    print("  python main.py")
    sys.exit(0)
else:
    print(f"\n❌ 发现 {len(errors)} 个问题：")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    print("\n建议：")
    print("  1. 检查是否所有文件都存在")
    print("  2. 运行 python diagnostics.py 进行完整诊断")
    print("  3. 查看上面的错误信息定位问题")
    sys.exit(1)
