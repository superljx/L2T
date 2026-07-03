"""
完整的集成测试
模拟完整的检测和切换流程
"""

import time
from config import Config, PresetConfigs
from detector import GameStateDetector
from window_manager import WindowManager
from browser_controller import BrowserController
from input_controller import InputController


def test_full_integration():
    """完整集成测试"""
    print("=" * 60)
    print("完整集成测试")
    print("=" * 60)

    # 使用调试配置
    PresetConfigs.debug()
    Config.ADAPTIVE_LEARNING_FRAMES = 20  # 快速学习

    # 初始化所有模块
    print("\n[1] 初始化模块...")
    detector = GameStateDetector(Config)
    window_manager = WindowManager(Config)
    browser_controller = BrowserController(Config)
    input_controller = InputController(Config)
    print("  ✓ 所有模块初始化完成")

    # 学习基准亮度
    print("\n[2] 学习基准亮度...")
    print("  正在采样屏幕亮度...")
    for i in range(Config.ADAPTIVE_LEARNING_FRAMES):
        state, brightness = detector.detect()
        if (i + 1) % 5 == 0:
            print(f"  进度: {i+1}/{Config.ADAPTIVE_LEARNING_FRAMES} - 亮度: {brightness:.1f}")
        time.sleep(0.1)

    print("  ✓ 基准亮度学习完成")
    stats = detector.get_stats()
    print(f"  基准亮度: {stats['baseline_brightness']:.1f}")

    # 模拟检测循环
    print("\n[3] 模拟检测循环（10秒）")
    print("  提示：如果游戏角色阵亡，应该会触发切换...")
    print("  按 Ctrl+C 可提前结束\n")

    try:
        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < 10:
            state, brightness = detector.detect()

            if frame_count % 5 == 0:
                print(f"  状态: {state:10s} | 亮度: {brightness:5.1f} | "
                      f"基准: {stats['baseline_brightness']:5.1f}")

            if state == "dead":
                print("\n  🔔 检测到阵亡状态！")
                print("  正在执行切换流程...")

                # 切换到Edge
                if window_manager.switch_to_edge():
                    print("  ✓ 已切换到Edge")
                    # 发送播放键
                    if input_controller.press_play_key():
                        print("  ✓ 已发送播放键")
                else:
                    print("  ✗ 切换失败")

                print("  测试成功！")
                break

            frame_count += 1
            time.sleep(0.2)

        if state != "dead":
            print("\n  未检测到阵亡状态")
            print("  这是正常的，说明您的角色处于存活状态")

    except KeyboardInterrupt:
        print("\n\n  用户中断测试")

    # 清理
    detector.close()

    print("\n" + "=" * 60)
    print("集成测试完成")
    print("=" * 60)
    print("\n✓ 如果所有步骤都成功，可以运行 main.py 开始正式使用")


if __name__ == "__main__":
    try:
        test_full_integration()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
