# LOL 游戏状态检测 + 自动浏览器切换播放系统

## 📖 项目简介

这是一款运行在 Windows 11 系统上的桌面自动化程序，能够实时监测《英雄联盟》游戏画面状态，当检测到玩家阵亡时，自动切换到 Microsoft Edge 浏览器并播放抖音视频。

### ✨ 核心功能

- **实时游戏状态检测**：通过屏幕亮度变化识别玩家阵亡状态
- **智能窗口切换**：自动切换到 Edge 浏览器窗口
- **自动播放控制**：自动发送播放指令
- **防误判机制**：连续帧确认 + 冷却时间
- **性能优化**：低CPU占用（<15%）、低延迟（<500ms）

## 🚀 快速开始

### 前置要求

- **操作系统**：Windows 11（或 Windows 10）
- **Python**：3.8 或更高版本
- **浏览器**：Microsoft Edge（已预装在Windows 11中）

### 安装步骤

1. **克隆或下载项目**

```bash
cd D:\code\L2T
```

2. **安装Python依赖**

```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. **验证安装**

```bash
python -c "import mss, cv2, win32gui, pyautogui; print('✓ 所有依赖安装成功')"
```

## 🎮 使用方法

### 基本使用

1. **启动游戏**：先打开《英雄联盟》游戏

2. **运行程序**：

```bash
python main.py
```

3. **选择运行模式**：
   - **平衡模式**（推荐）：兼顾性能和准确性
   - **高性能模式**：更低延迟，可能误判
   - **稳定模式**：更少误判，延迟稍高
   - **调试模式**：显示详细检测信息

4. **等待学习**：程序会先学习10-100帧建立基准亮度

5. **自动运行**：检测到阵亡时会自动切换并播放视频

6. **停止程序**：按 `Ctrl+C` 停止

### Edge浏览器准备（可选）

程序会自动打开Edge并访问抖音，但如果你想手动准备：

1. 打开 Microsoft Edge
2. 访问 https://www.douyin.com/?recommend=1
3. 确保视频页面已加载完成

## ⚙️ 配置调整

编辑 `config.py` 文件进行参数调整：

### 关键参数说明

```python
# 检测灵敏度
BRIGHTNESS_THRESHOLD = 30  # 亮度阈值（20-40），越小越敏感
CONFIRM_FRAMES = 3         # 确认帧数（2-5），越大越稳定

# 检测性能
CAPTURE_FPS = 8           # 检测帧率（5-10），越高响应越快

# 防重复触发
COOLDOWN_SECONDS = 15     # 冷却时间（秒），避免频繁切换

# 目标网址
TARGET_URL = "https://www.douyin.com/?recommend=1"
```

### 推荐配置组合

#### 🏆 追求低延迟
```python
CAPTURE_FPS = 10
CONFIRM_FRAMES = 2
BRIGHTNESS_THRESHOLD = 25
```

#### 🎯 追求准确性
```python
CAPTURE_FPS = 6
CONFIRM_FRAMES = 4
BRIGHTNESS_THRESHOLD = 35
```

#### ⚖️ 平衡（默认）
```python
CAPTURE_FPS = 8
CONFIRM_FRAMES = 3
BRIGHTNESS_THRESHOLD = 30
```

## 🔧 调参指南

### 如何调整亮度阈值

1. **启动调试模式**：

```python
# 在 config.py 中设置
DEBUG_MODE = True
DEBUG_SHOW_BRIGHTNESS = True
```

2. **观察亮度变化**：
   - 程序会实时显示当前亮度和基准亮度
   - 正常游戏时亮度：通常 40-60
   - 阵亡时亮度：通常 20-35
   - 差值应该 > 阈值才触发

3. **调整阈值**：
   - 如果**误触发**（没死就切换）：增大 `BRIGHTNESS_THRESHOLD`
   - 如果**漏检测**（死了不切换）：减小 `BRIGHTNESS_THRESHOLD`

### 如何调整确认帧数

- **频繁误判**：增加 `CONFIRM_FRAMES`（如4-5帧）
- **响应太慢**：减少 `CONFIRM_FRAMES`（如2帧，但可能误判）

### 区域检测优化（高级）

如果全屏检测不够准确，可以启用ROI区域检测：

```python
ROI_ENABLED = True
ROI_REGION = {
    "top": 0.4,      # 检测区域上边界（屏幕40%处）
    "left": 0.3,     # 左边界（30%处）
    "width": 0.4,    # 宽度（40%）
    "height": 0.2    # 高度（20%）
}
```

建议检测游戏画面中心偏下区域（通常是玩家角色位置）。

## 🐛 故障排查

### 问题1：检测不到阵亡

**可能原因**：
- 亮度阈值设置过高
- 游戏分辨率/画面设置特殊
- 多显示器环境

**解决方案**：
1. 启用调试模式查看实际亮度差异
2. 降低 `BRIGHTNESS_THRESHOLD` 到 20-25
3. 增加 `CAPTURE_FPS` 到 10

### 问题2：频繁误触发

**可能原因**：
- 亮度阈值设置过低
- 游戏画面闪烁或技能特效
- 确认帧数太少

**解决方案**：
1. 增大 `BRIGHTNESS_THRESHOLD` 到 35-40
2. 增加 `CONFIRM_FRAMES` 到 4-5
3. 启用 ROI 区域检测

### 问题3：切换到Edge失败

**可能原因**：
- Edge未安装或路径异常
- 窗口权限不足

**解决方案**：
1. 确认Edge浏览器已安装
2. 以管理员身份运行程序
3. 检查 `EDGE_PROCESS_NAME` 配置是否正确

### 问题4：CPU占用过高

**可能原因**：
- 检测帧率设置过高
- 屏幕分辨率过大

**解决方案**：
1. 降低 `CAPTURE_FPS` 到 5-6
2. 启用 `ENABLE_PERFORMANCE_MODE`
3. 设置较小的 `CAPTURE_REGION`

### 问题5：多显示器环境

**解决方案**：

```python
# 在 config.py 中指定主显示器区域
CAPTURE_REGION = {
    "top": 0, 
    "left": 0, 
    "width": 1920, 
    "height": 1080
}
```

## 📊 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| CPU占用 | <15% | 1080p分辨率下 |
| 检测延迟 | <500ms | 状态变化到切屏 |
| 误判率 | <5% | 根据实际游戏环境调整 |
| 内存占用 | <200MB | 稳定运行状态 |

## 📁 项目结构

```
L2T/
├── main.py                  # 主程序入口
├── config.py               # 配置文件
├── detector.py             # 游戏状态检测
├── window_manager.py       # 窗口管理
├── browser_controller.py   # 浏览器控制
├── input_controller.py     # 输入模拟
├── utils.py                # 工具函数
├── requirements.txt        # 依赖列表
├── README.md              # 本文档
└── test_*.py              # 测试脚本
```

## 🧪 测试脚本

### 测试屏幕捕捉

```bash
python test_capture.py
```

### 测试亮度检测

```bash
python test_brightness.py
```

### 测试窗口切换

```bash
python test_window.py
```

## ⚠️ 注意事项

### 安全与边界

- ✅ **仅基于屏幕和外部窗口控制**
- ✅ **不修改游戏内存**
- ✅ **不注入游戏进程**
- ✅ **不使用DLL注入/Hook**

### 使用限制

- 本程序仅用于个人学习和研究
- 不保证在所有游戏配置下都能正常工作
- 不同分辨率/画面设置可能需要调整参数
- 可能受游戏版本更新影响

### 游戏兼容性

- 推荐在**窗口化全屏**或**窗口模式**下运行游戏
- **全屏独占模式**可能影响检测效果
- 建议游戏画面亮度设置为默认值

## 🔄 更新日志

### v1.0.0 (2026-07-03)

- ✨ 初始版本发布
- ✅ 基于亮度的游戏状态检测
- ✅ 自动窗口切换
- ✅ 自动播放控制
- ✅ 完整的配置系统
- ✅ 防误判和冷却机制

## 📝 开发计划

- [ ] 支持更多视频网站（B站、YouTube等）
- [ ] 基于深度学习的状态识别（更精确）
- [ ] GUI配置界面
- [ ] 自动参数学习和优化
- [ ] 支持多种游戏

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目仅供学习交流使用。

## 💡 技术支持

遇到问题？请检查：

1. 是否已安装所有依赖
2. 是否使用管理员权限运行
3. Edge浏览器是否正常工作
4. 查看日志文件 `lol_auto_switch.log`

---

**祝游戏愉快！** 🎮
