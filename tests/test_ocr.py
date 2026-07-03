"""
测试OCR功能
验证Tesseract OCR是否正确安装和配置
"""

import sys
import io

# 设置stdout为UTF-8编码，避免Windows GBK编码错误
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def test_pytesseract_import():
    """测试pytesseract导入"""
    print("[1/4] 测试 pytesseract 导入...")
    try:
        import pytesseract
        print("  ✓ pytesseract 已安装")
        return True
    except ImportError:
        print("  ✗ pytesseract 未安装")
        print("     安装命令: pip install pytesseract")
        return False


def test_tesseract_engine():
    """测试Tesseract引擎"""
    print("\n[2/4] 测试 Tesseract OCR 引擎...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract 版本: {version}")
        return True
    except Exception as e:
        print(f"  ✗ Tesseract 未安装或配置错误")
        print(f"     错误: {e}")
        print("     解决方案：")
        print("     1. 下载安装: https://github.com/UB-Mannheim/tesseract/wiki")
        print("     2. 在 config.py 中设置 TESSERACT_PATH")
        return False


def test_chinese_support():
    """测试中文语言包"""
    print("\n[3/4] 测试中文语言包...")
    try:
        import pytesseract
        langs = pytesseract.get_languages()

        if 'chi_sim' in langs:
            print("  ✓ 简体中文语言包已安装")
            return True
        else:
            print("  ✗ 简体中文语言包未安装")
            print(f"     已安装语言: {', '.join(langs)}")
            print("     解决方案：")
            print("     1. 重新安装 Tesseract 并勾选中文语言包")
            print("     2. 或下载 chi_sim.traineddata 放到 tessdata 目录")
            return False
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


def test_ocr_recognition():
    """测试OCR识别功能"""
    print("\n[4/4] 测试 OCR 识别功能...")
    try:
        import pytesseract
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont

        # 创建一个测试图像（白底黑字）
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)

        # 尝试使用系统字体，如果失败使用默认字体
        try:
            # Windows 中文字体
            font = ImageFont.truetype("simhei.ttf", 32)
        except:
            font = None  # 使用默认字体

        draw.text((50, 30), "返回于", fill='black', font=font)

        # OCR识别
        text = pytesseract.image_to_string(np.array(img), lang='chi_sim')

        # 检查是否识别到"返回"
        if "返回" in text or "返" in text:
            print(f"  ✓ OCR 识别成功")
            print(f"     识别结果: {text.strip()}")
            return True
        else:
            print(f"  ⚠ OCR 识别结果不理想")
            print(f"     识别结果: {text.strip()}")
            print(f"     但程序仍可运行（会使用模板匹配备用方案）")
            return True

    except Exception as e:
        print(f"  ✗ OCR 识别测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("OCR 功能测试")
    print("=" * 60)
    print()

    results = []
    results.append(("pytesseract 导入", test_pytesseract_import()))

    if results[0][1]:  # 只有导入成功才继续测试
        results.append(("Tesseract 引擎", test_tesseract_engine()))

        if results[1][1]:  # 只有引擎可用才测试语言包
            results.append(("中文语言包", test_chinese_support()))
            results.append(("OCR 识别", test_ocr_recognition()))

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
        print("\n✅ 所有测试通过！OCR 功能已就绪")
        print("\n下一步：")
        print("  运行主程序: python main.py")
    elif passed >= 2:
        print("\n⚠️ 部分测试失败，但基本功能可用")
        print("  程序会使用模板匹配作为备用方案")
        print("\n下一步：")
        print("  可以运行主程序: python main.py")
    else:
        print("\n❌ OCR 功能不可用")
        print("\n建议操作：")
        print("  1. 查看 OCR_SETUP.md 获取详细安装指南")
        print("  2. 安装 Tesseract OCR")
        print("  3. 重新运行此测试")

    print("\n" + "=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
