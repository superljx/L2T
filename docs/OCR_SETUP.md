# OCR 检测模式安装指南

## 🎯 新的检测策略

程序已从**亮度检测**升级为**OCR文字识别**，检测死亡界面的"返回于"字样，更加准确可靠！

---

## 📦 安装步骤

### 1. 安装 Python 依赖

```bash
pip install pytesseract
```

或安装全部依赖：
```bash
pip install -r requirements.txt
```

### 2. 安装 Tesseract OCR 引擎

#### Windows 安装

**方法1：使用安装包（推荐）**

1. 下载 Tesseract 安装包：
   - 官方下载：https://github.com/UB-Mannheim/tesseract/wiki
   - 直接链接：https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

2. 运行安装程序，记住安装路径（默认：`C:\Program Files\Tesseract-OCR`）

3. **重要**：安装时勾选 **Additional language data** → **Chinese Simplified**（简体中文语言包）

4. 配置路径（如果不在默认位置）：
   编辑 `config.py`：
   ```python
   TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

**方法2：添加到系统 PATH**

如果已安装 Tesseract，确保它在系统 PATH 中：
```bash
# 测试是否可用
tesseract --version
```

---

## ✅ 验证安装

运行测试脚本：
```bash
python test_ocr.py
```

或运行主程序：
```bash
python main.py
```

如果看到：
```
游戏状态检测器初始化完成 (OCR文字识别模式)
```
说明安装成功！

---

## 🔄 备用方案

如果无法安装 Tesseract，程序会自动使用**模板匹配**作为备用方法：
- 检测画面是否变暗
- 检测中心区域是否有大量白色像素（死亡界面文字特征）

虽然不如 OCR 准确，但也能工作。

---

## 🎯 优势对比

| 方法 | 准确度 | 误判率 | 说明 |
|------|--------|--------|------|
| **OCR文字识别** | ⭐⭐⭐⭐⭐ | 极低 | 直接识别"返回于"文字 |
| 亮度检测（旧） | ⭐⭐⭐ | 中等 | 无视野区域也会误判 |
| 模板匹配（备用） | ⭐⭐⭐⭐ | 低 | 检测死亡界面特征 |

---

## 🐛 故障排查

### 问题1：提示 pytesseract 未安装

**解决**：
```bash
pip install pytesseract
```

### 问题2：提示找不到 tesseract 命令

**解决**：
1. 确认已安装 Tesseract OCR
2. 在 `config.py` 中设置路径：
   ```python
   TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

### 问题3：无法识别中文

**解决**：
1. 下载中文语言包：https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
2. 放到 Tesseract 安装目录的 `tessdata` 文件夹
3. 通常路径：`C:\Program Files\Tesseract-OCR\tessdata\`

### 问题4：识别不准确

**解决**：
- 启用调试模式查看 OCR 结果：
  ```python
  # config.py
  DEBUG_MODE = True
  ```
- 程序会自动检测"返回于"、"返回"、"复活"等关键字

---

## 🚀 立即使用

安装完成后：
```bash
python main.py
```

程序会自动：
1. ✅ 实时截取游戏画面
2. ✅ OCR 识别"返回于"文字
3. ✅ 检测到死亡后自动切换到 Edge
4. ✅ 播放抖音视频

更准确，更可靠！🎉
