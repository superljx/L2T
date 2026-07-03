"""
测试倒计时数字识别
使用提供的截图测试OCR能否识别金色数字
"""

import cv2
import numpy as np
import re
import sys
import io

# 设置stdout为UTF-8编码，避免Windows GBK编码错误
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("X pytesseract未安装")
    exit(1)


def preprocess_for_gold_numbers(image):
    """专门用于识别金色数字的预处理"""
    results = []

    # 转换到HSV色彩空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 方法1: 提取金色/橙色/黄色区域
    lower_gold = np.array([10, 100, 100])
    upper_gold = np.array([40, 255, 255])
    mask_gold = cv2.inRange(hsv, lower_gold, upper_gold)
    results.append(("金色提取", mask_gold))

    # 方法2: 提取高亮度区域
    _, _, v_channel = cv2.split(hsv)
    _, bright = cv2.threshold(v_channel, 150, 255, cv2.THRESH_BINARY)
    results.append(("高亮度", bright))

    # 方法3: 灰度高阈值
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, high_threshold = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    results.append(("高阈值", high_threshold))

    # 方法4: 中等阈值
    _, mid_threshold = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
    results.append(("中阈值", mid_threshold))

    # 方法5: OTSU自适应
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results.append(("OTSU", otsu))

    return results


def test_timer_recognition():
    """测试倒计时识别"""
    print("=" * 60)
    print("倒计时数字识别测试")
    print("=" * 60)

    # 读取测试图片
    image_path = "example.png"
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"\n❌ 无法读取图片: {image_path}")
            print("请确保 example.png 在当前目录")
            return

        print(f"\n✓ 已读取图片: {image.shape[1]}x{image.shape[0]}")
    except Exception as e:
        print(f"\n❌ 读取图片失败: {e}")
        return

    # 预处理图片
    print("\n[1/3] 尝试多种预处理方法...")
    processed_images = preprocess_for_gold_numbers(image)

    # OCR配置
    configs = [
        ("单行数字", '--psm 7 -c tessedit_char_whitelist=0123456789'),
        ("单词", '--psm 8 -c tessedit_char_whitelist=0123456789'),
        ("块文本", '--psm 6 -c tessedit_char_whitelist=0123456789'),
        ("原始单行", '--psm 13'),
    ]

    results = []

    print("\n[2/3] 尝试OCR识别...")
    for preprocess_name, processed in processed_images:
        for config_name, config in configs:
            try:
                text = pytesseract.image_to_string(processed, lang='eng', config=config)
                numbers = re.findall(r'\d+', text)

                if numbers:
                    for num_str in numbers:
                        num = int(num_str)
                        if 1 <= num <= 100:
                            results.append({
                                'preprocess': preprocess_name,
                                'config': config_name,
                                'number': num,
                                'text': text.strip()
                            })
                            print(f"  ✓ {preprocess_name} + {config_name}: 识别到 {num}")
            except Exception as e:
                continue

    # 总结结果
    print("\n[3/3] 识别结果总结")
    print("=" * 60)

    if results:
        print(f"\n✅ 成功识别到倒计时！共 {len(results)} 种方法成功\n")

        # 统计最常见的数字
        numbers = [r['number'] for r in results]
        most_common = max(set(numbers), key=numbers.count)
        count = numbers.count(most_common)

        print(f"最可能的倒计时: {most_common}秒 (出现{count}次)")
        print(f"\n所有识别结果:")
        for r in results:
            print(f"  • {r['number']}秒 - {r['preprocess']} + {r['config']}")

        print("\n✅ OCR配置正常，程序应该能识别倒计时")
        print("\n建议:")
        print("  1. 启用调试模式: DEBUG_MODE = True")
        print("  2. 运行主程序并查看详细日志")

    else:
        print("\n❌ 未能识别到倒计时数字\n")
        print("可能原因:")
        print("  1. Tesseract OCR配置问题")
        print("  2. 英文语言包未安装")
        print("  3. 图片分辨率过低")

        print("\n解决方案:")
        print("  1. 重新安装Tesseract OCR")
        print("  2. 确保安装了英文语言包(eng.traineddata)")
        print("  3. 运行: python test_ocr.py")

    print("=" * 60)


if __name__ == "__main__":
    try:
        test_timer_recognition()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
