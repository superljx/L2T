"""
测试亮度检测功能
运行此脚本查看实时亮度值，帮助调整阈值
"""

import cv2
import numpy as np
from mss import mss
import time
import sys


def calculate_brightness(image: np.ndarray) -> float:
    """计算图像亮度"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]
    brightness = np.mean(v_channel)
    return float(brightness / 255.0 * 100.0)


def test_brightness_detection():
    """测试亮度检测"""
    print("=" * 60)
    print("实时亮度检测测试")
    print("=" * 60)
    print("\n这个测试将显示实时屏幕亮度值")
    print("请在LOL游戏中测试：")
    print("  1. 正常游戏时记录亮度值")
    print("  2. 角色阵亡时记录亮度值")
    print("  3. 计算差值，设置合适的 BRIGHTNESS_THRESHOLD")
    print("\n按 Ctrl+C 停止测试\n")

    time.sleep(2)

    sct = mss()
    monitor = sct.monitors[1]

    brightness_history = []
    max_history = 30

    try:
        frame_count = 0
        while True:
            # 捕捉屏幕
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # 计算亮度
            brightness = calculate_brightness(img)
            brightness_history.append(brightness)

            if len(brightness_history) > max_history:
                brightness_history.pop(0)

            # 计算统计值
            avg_brightness = np.mean(brightness_history)
            min_brightness = np.min(brightness_history)
            max_brightness = np.max(brightness_history)

            # 清屏并显示（简单实现）
            if frame_count % 5 == 0:  # 每5帧更新一次显示
                print("\r" + " " * 100, end="")  # 清除当前行
                print(f"\r当前亮度: {brightness:5.1f} | "
                      f"平均: {avg_brightness:5.1f} | "
                      f"范围: {min_brightness:5.1f}-{max_brightness:5.1f} | "
                      f"波动: {max_brightness-min_brightness:5.1f}",
                      end="", flush=True)

            frame_count += 1
            time.sleep(0.2)  # 5 FPS

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("测试结束")
        print("=" * 60)
        print(f"\n统计结果（最近{len(brightness_history)}帧）：")
        print(f"  平均亮度: {avg_brightness:.1f}")
        print(f"  最小亮度: {min_brightness:.1f}")
        print(f"  最大亮度: {max_brightness:.1f}")
        print(f"  亮度波动: {max_brightness-min_brightness:.1f}")
        print("\n💡 建议设置：")
        print(f"  如果正常游戏亮度约为 {avg_brightness:.1f}")
        print(f"  阵亡时亮度通常会降低 20-40 点")
        print(f"  建议 BRIGHTNESS_THRESHOLD 设置为 25-35")
        print("=" * 60)
    finally:
        sct.close()


if __name__ == "__main__":
    try:
        test_brightness_detection()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
