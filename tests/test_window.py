"""
测试窗口切换功能
验证Edge浏览器窗口查找和切换是否正常
"""

import time
from config import Config
from window_manager import WindowManager
from browser_controller import BrowserController
from input_controller import InputController


def test_window_management():
    """测试窗口管理"""
    print("=" * 60)
    print("窗口管理功能测试")
    print("=" * 60)

    wm = WindowManager(Config)
    bc = BrowserController(Config)
    ic = InputController(Config)

    # 测试1：检查Edge是否运行
    print("\n[测试1] 检查Edge浏览器状态")
    is_running = wm.is_edge_running()
    print(f"  Edge运行状态: {'✓ 运行中' if is_running else '✗ 未运行'}")

    if not is_running:
        print("\n正在启动Edge浏览器...")
        bc.open_target_page()
        print("  等待浏览器启动...")
        time.sleep(3)
        is_running = wm.is_edge_running()
        print(f"  Edge运行状态: {'✓ 运行中' if is_running else '✗ 仍未运行'}")

    if not is_running:
        print("\n✗ Edge浏览器未能启动，测试终止")
        return

    # 测试2：查找Edge窗口
    print("\n[测试2] 查找Edge窗口")
    edge_windows = wm.find_edge_windows()
    print(f"  找到 {len(edge_windows)} 个Edge窗口")
    for i, hwnd in enumerate(edge_windows, 1):
        import win32gui
        title = win32gui.GetWindowText(hwnd)
        print(f"  窗口 {i}: {title}")

    if not edge_windows:
        print("\n✗ 未找到Edge窗口，测试终止")
        return

    # 测试3：获取当前前台窗口
    print("\n[测试3] 当前前台窗口")
    fg_info = wm.get_foreground_window_info()
    print(f"  标题: {fg_info.get('title', 'N/A')}")
    print(f"  进程: {fg_info.get('process', 'N/A')}")

    # 测试4：切换到Edge
    print("\n[测试4] 切换到Edge浏览器")
    print("  提示：请观察屏幕是否切换到Edge窗口...")
    success = wm.switch_to_edge()
    print(f"  切换结果: {'✓ 成功' if success else '✗ 失败'}")

    if success:
        time.sleep(1)
        is_edge_fg = wm.is_edge_foreground()
        print(f"  Edge是否在前台: {'✓ 是' if is_edge_fg else '✗ 否'}")

    # 测试5：发送播放键
    print("\n[测试5] 发送播放键（空格）")
    print("  提示：如果Edge中有视频，应该会播放/暂停...")
    time.sleep(1)
    success = ic.press_play_key()
    print(f"  按键发送: {'✓ 成功' if success else '✗ 失败'}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n✓ 如果看到Edge窗口切换并且视频播放/暂停，说明功能正常")


if __name__ == "__main__":
    try:
        test_window_management()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
