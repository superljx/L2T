# 🎮 LOL 自动切换系统

> 英雄联盟阵亡时自动切换到抖音，复活时自动切回游戏

[![Version](https://img.shields.io/badge/version-1.4.2-blue.svg)](https://github.com/yourusername/lol-auto-switch)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 📖 项目简介

这是一个自动化工具，专为《英雄联盟》玩家设计。当你在游戏中阵亡时，程序会：
- 🔍 自动检测阵亡状态（OCR识别"返回于"文字）
- ⏱️ 提取复活倒计时（精确到秒）
- 🌐 自动切换到Edge浏览器的抖音页面
- 🔄 倒计时结束前2秒自动切回游戏
- ⏸️ 切回时自动暂停视频播放

**让你在等待复活的时间里看视频，复活时立即回到游戏！**

---

## ✨ 核心特性

### 🤖 完全自动化
- **智能页面管理**：自动检测抖音页面，存在则切换，不存在则打开
- **时间补偿**：自动扣除切换耗时，精准切回
- **状态管理**：倒计时期间不重复触发

### 🖥️ 现代GUI界面
- **深色主题**：保护眼睛
- **一键操作**：启动/停止
- **实时日志**：查看运行状态
- **快捷测试**：测试OCR、倒计时、系统诊断

---

## 📦 安装说明

### 系统要求

- **操作系统**：Windows 10/11
- **Python版本**：3.8 或更高
- **浏览器**：Microsoft Edge
- **游戏**：英雄联盟（LOL）

### 步骤1：克隆项目

```bash
git clone https://github.com/superljx/L2T.git
cd L2T
```

### 步骤2：安装Python依赖

```bash
pip install -r requirements.txt
```

**依赖列表**：
```
mss>=9.0.1                # 屏幕捕获
opencv-python>=4.8.0      # 图像处理
numpy>=1.24.0             # 数值计算
pywin32>=306              # Windows API
psutil>=5.9.0             # 进程管理
pyautogui>=0.9.54         # 输入模拟
pillow>=10.0.0            # 图像处理
pytesseract>=0.3.10       # OCR识别
customtkinter>=5.2.0      # GUI界面
```

### 步骤3：安装Tesseract OCR（推荐）

Tesseract OCR用于文字识别，安装后准确率可达99%。

**下载地址**：
- GitHub：https://github.com/UB-Mannheim/tesseract/wiki
- 直接下载：https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

**安装步骤**：
1. 运行安装程序
2. **重要**：勾选 "Chinese Simplified"（简体中、英文、数学语言包）
3. 记住安装路径（默认：`C:\Program Files\Tesseract-OCR`）

**配置路径**（如果未安装到默认位置）：
编辑 `src/config.py`：
```python
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### 步骤4：测试安装

```bash
# 测试所有模块
python tests/check_startup.py

# 测试OCR功能
python tests/test_ocr.py

# 系统诊断
python tests/diagnostics.py
```

---

## 🚀 使用方法

### 方法1：GUI图形界面（推荐）

**启动界面**：
```bash
python src/gui.py
```

**使用步骤**：
1. 勾选配置选项（推荐开启"使用OCR识别"）
2. 点击 "▶ 启动检测" 按钮
3. 观察日志确认启动成功
4. 开始游戏
5. 阵亡时程序自动工作
6. 完成后点击 "⏸ 停止检测"

### 方法2：命令行界面

```bash
python src/main.py
```

按 `Ctrl+C` 停止程序。

---

## ⚙️ 配置说明

编辑 `src/config.py` 修改配置：

### 核心配置

```python
# OCR识别
USE_OCR = True                    # 是否使用OCR（推荐）
TESSERACT_PATH = None             # Tesseract路径（None=自动）

# 检测参数
CAPTURE_FPS = 8                   # 检测帧率（5-10）
CONFIRM_FRAMES = 2                # 确认帧数（2-4）
COOLDOWN_SECONDS = 15             # 冷却时间（秒）

# 目标URL
TARGET_URL = "https://www.douyin.com/?recommend=1"

# 调试选项
DEBUG_MODE = False                # 调试模式
DEBUG_SAVE_TIMER_ROI = False      # 保存倒计时截图
```

### 预设配置

```python
from src.config import Config, PresetConfigs

# 高性能模式（响应快，可能误判）
PresetConfigs.high_performance()

# 平衡模式（推荐）
PresetConfigs.balanced()

# 稳定模式（误判少，延迟略高）
PresetConfigs.stable()
```

---

## 📂 项目结构

```
lol-auto-switch/
├── src/                      # 源代码
│   ├── main.py              # 主控制器
│   ├── detector.py          # OCR检测+倒计时识别
│   ├── window_manager.py    # 窗口管理
│   ├── browser_controller.py # 浏览器控制
│   ├── input_controller.py  # 输入控制
│   ├── config.py            # 配置文件
│   ├── utils.py             # 工具函数
│   └── gui.py               # GUI界面
│
├── tests/                    # 测试文件
│   ├── test_ocr.py          # OCR测试
│   ├── test_timer.py        # 倒计时测试
│   ├── test_integration.py  # 集成测试
│   ├── check_startup.py     # 启动检查
│   └── diagnostics.py       # 系统诊断
│
├── docs/                     # 文档
│   ├── START_HERE.md        # 快速开始
│   ├── TROUBLESHOOTING.md   # 故障排查
│   ├── GUI_GUIDE.md         # GUI使用说明
│   ├── OCR_SETUP.md         # OCR安装指南
│   ├── DEBUG_TIMER.md       # 倒计时调试
│   └── UPDATE_v*.md         # 版本更新说明
│
├── scripts/                  # 脚本
│   ├── start_gui.bat        # GUI启动脚本
│   └── start.bat            # 命令行启动脚本
│
├── assets/                   # 资源文件
│   └── screenshots/         # 截图
│
├── debug_screenshots/        # 调试截图（运行时生成）
├── requirements.txt          # Python依赖
├── README.md                 # 本文档
└── start_gui.bat            # 快速启动（根目录）
```

---

## 🎨 GUI界面功能

### 主要功能

- **▶ 启动检测** / **⏸ 停止检测** - 控制运行
- **🔍 测试OCR** - 测试OCR功能
- **⏱ 测试倒计时** - 测试倒计时识别
- **🔧 系统诊断** - 运行系统诊断
- **🗑 清空日志** - 清空日志显示

### 配置开关

- **使用OCR识别** - 开启OCR文字识别（推荐）
- **调试模式** - 显示详细日志

### 实时日志

- 带时间戳的日志记录
- 自动滚动到最新
- 显示所有运行状态

---

## 🔍 工作原理

```
1. 实时捕获游戏画面（8 FPS）
   ↓
2. OCR识别"返回于"文字
   ↓
3. 提取复活倒计时（如53秒）
   ↓
4. 检查抖音页面是否存在
   ├─ 存在 → 切换到该页面
   └─ 不存在 → 打开新页面
   ↓
5. 等待复活倒计时...
   ↓
6. 倒计时剩余2秒时
   ↓
7. 发送暂停键（Space）
   ↓
8. 切换回LOL游戏
   ↓
9. 继续检测，等待下次阵亡
```

---

## 🐛 故障排查

### 常见问题

#### 问题1：OCR无法识别

**解决方案**：
1. 确认已安装Tesseract OCR
2. 安装时勾选了中文语言包
3. 运行 `python tests/test_ocr.py` 测试

#### 问题2：窗口切换失败

**解决方案**：
1. 以**管理员身份**运行程序
2. 游戏使用**窗口化全屏**模式（不要全屏独占）

#### 问题3：倒计时识别失败

**解决方案**：
1. 启用调试模式：`DEBUG_MODE = True`
2. 查看日志中的OCR识别文本
3. 运行 `python tests/test_timer.py` 测试

#### 问题4：Edge无法打开抖音

**解决方案**：
1. 确认Edge浏览器已安装
2. 检查网络连接
3. 手动打开一次抖音网站测试

### 详细排查

查看 `docs/TROUBLESHOOTING.md` 获取完整的故障排查指南。

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| CPU占用 | 12-16% | 低资源占用 |
| 内存占用 | ~150MB | 轻量级 |
| 检测延迟 | <300ms | 快速响应 |
| 识别准确率 | 99% | OCR模式 |
| 倒计时识别率 | 50% | 10/20方法成功 |

---

## 🎉 版本历程

### v1.4.2 (当前版本)
- ✅ GUI图形界面
- ✅ 修复编码问题
- ✅ 完善测试工具

### v1.3.x
- 智能页面管理
- 时间补偿优化
- 取消自动播放

### v1.2.x
- 倒计时识别
- 自动切回游戏
- Bug修复

### v1.1.0
- OCR文字识别
- 准确率99%

### v1.0.0
- 基础亮度检测
- 准确率85%

查看 `docs/UPDATE_v*.md` 获取详细更新日志。

---

## 💡 使用建议

### 推荐配置

- ✅ 使用OCR识别
- ✅ 游戏窗口化全屏
- ✅ 以管理员身份运行
- ✅ 保持网络连接

### 不推荐

- ❌ 游戏全屏独占模式
- ❌ 过小的冷却时间
- ❌ 频繁修改配置

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/yourusername/lol-auto-switch.git

# 安装依赖
pip install -r requirements.txt

# 运行测试
python tests/check_startup.py
```

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - 文字识别引擎
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代GUI框架
- [mss](https://github.com/BoboTiG/python-mss) - 屏幕捕获库

---

## 📧 联系方式

- **问题反馈**：[GitHub Issues](https://github.com/yourusername/lol-auto-switch/issues)
- **讨论交流**：[GitHub Discussions](https://github.com/yourusername/lol-auto-switch/discussions)

---

## ⚠️ 免责声明

本工具仅用于学习和研究目的。使用本工具可能违反游戏服务条款，请自行承担风险。

- 本工具不修改游戏内存或注入游戏进程
- 仅基于屏幕捕获和窗口控制
- 不提供任何游戏内优势

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by [Your Name]

</div>
