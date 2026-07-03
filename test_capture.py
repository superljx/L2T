"""
测试屏幕捕捉功能
运行此脚本验证屏幕截图是否正常工作
"""

import cv2
import numpy as np
from mss import mss
import time


def test_screen_capture():
    """测试屏幕捕捉"""
    print("=" * 60)
    print("测试屏幕捕捉功能")
    print("=" * 60)

    sct = mss()

    # 显示所有显示器信息
    print("\n可用显示器：")
    for i, monitor in enumerate(sct.monitors):
        print(f"  显示器 {i}: {monitor}")

    # 使用主显示器
    monitor = sct.monitors[1]
    print(f"\n使用主显示器: {monitor}")

    print("\n正在捕捉屏幕... (将捕捉5张，每秒1张)")

    for i in range(5):
        start_time = time.time()

        # 捕捉屏幕
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 计算捕捉时间
        capture_time = time.time() - start_time

        # 保存图片
        filename = f"test_capture_{i+1}.png"
        cv2.imwrite(filename, img)

        print(f"  [{i+1}/5] 捕捉完成 ({capture_time*1000:.1f}ms) - 已保存: {filename}")
        print(f"         分辨率: {img.shape[1]}x{img.shape[0]}")

        time.sleep(1)

    print("\n✓ 屏幕捕捉测试完成")
    print("请检查生成的 test_capture_*.png 文件")
    print("=" * 60)

    sct.close()


if __name__ == "__main__":
    try:
        test_screen_capture()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
