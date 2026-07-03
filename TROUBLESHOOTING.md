# 🔧 常见问题排查指南

## 问题1：窗口激活失败

### 错误信息
```
[ERROR] WindowManager: 激活窗口失败: (18, 'SetForegroundWindow', '没有更多文件。')
[ERROR] WindowManager: 激活窗口失败: (0, 'SetForegroundWindow', 'No error message is available')
```

### 原因
Windows安全机制限制：当一个程序在运行时，其他程序不能随意抢占前台焦点。

### 解决方案

#### 方案1：以管理员身份运行（推荐）
```bash
# 右键点击 cmd 或 PowerShell
# 选择"以管理员身份运行"
# 然后运行程序
python main.py
```

#### 方案2：修改Windows焦点设置
1. 按 `Win + R` 打开运行
2. 输入 `regedit` 打开注册表编辑器
3. 导航到：
   ```
   HKEY_CURRENT_USER\Control Panel\Desktop
   ```
4. 找到或创建 DWORD 值：
   - `ForegroundLockTimeout` = 0
   - `ForegroundFlashCount` = 0

5. 重启计算机

#### 方案3：程序已自动优化
最新代码已经使用多种方法尝试激活窗口：
- ✅ ShowWindow + BringWindowToTop
- ✅ Shell.AppActivate（更可靠）
- ✅ 模拟Alt键获取权限
- ✅ 降级验证（窗口可见即算成功）

重新运行程序即可。

---

## 问题2：未识别到倒计时

### 错误信息
```
[INFO] 检测到阵亡状态！（未识别到倒计时）
[WARNING] 未识别到倒计时，不会自动切回游戏
```

### 原因
1. OCR识别失败
2. 游戏分辨率或UI缩放
3. 倒计时数字位置不在预期区域

### 解决方案

#### 方案1：启用调试模式查看OCR结果
编辑 `config.py`：
```python
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
```

重新运行，查看日志中的OCR识别文本。

#### 方案2：检查Tesseract OCR是否正常
```bash
python test_ocr.py
```

确保：
- ✅ Tesseract已安装
- ✅ 中文语言包已安装
- ✅ OCR识别测试通过

#### 方案3：调整游戏设置
- 使用**窗口化全屏**或**窗口模式**
- 游戏分辨率：1920×1080（推荐）
- UI缩放：100%（默认）
- 字体大小：默认

#### 方案4：手动测试OCR识别区域
最新代码已优化：
- ✅ 增加了更多数字提取模式
- ✅ 多种二值化方法尝试
- ✅ 扩大了数字搜索范围
- ✅ 使用专门的数字识别配置

#### 方案5：即使没有识别到倒计时
程序仍然会：
- ✅ 正常切换到Edge
- ✅ 播放抖音视频
- ⚠️ 需要手动切回游戏

---

## 问题3：Edge窗口切换后立即被游戏抢回

### 症状
Edge窗口闪一下就又回到游戏了。

### 解决方案
1. **以管理员身份运行程序**
2. **游戏设置为窗口模式**（不要全屏独占）
3. **增加切换延迟**：
   ```python
   # config.py
   WINDOW_SWITCH_DELAY = 1.0  # 增加到1秒
   ```

---

## 问题4：检测不到阵亡状态

### 检查清单
- [ ] Tesseract OCR已安装？
- [ ] 简体中文语言包已安装？
- [ ] 游戏使用窗口模式？
- [ ] 游戏分辨率合理（不是特别小或特别大）？
- [ ] DEBUG_MODE查看OCR识别了什么文本？

### 快速测试
```python
# 启用调试模式
DEBUG_MODE = True

# 查看日志中的OCR文本
# 应该能看到类似：
# [DEBUG] OCR检测: 死亡状态, 倒计时: 15秒, 文本: 返回于 15
```

---

## 问题5：程序运行但没有任何反应

### 可能原因
1. LOL进程检查失败
2. 检测器初始化失败
3. 没有真正进入检测循环

### 解决方案

#### 检查1：关闭LOL进程检查
```python
# config.py
REQUIRE_LOL_RUNNING = False  # 暂时关闭LOL进程检查
```

#### 检查2：运行启动检查
```bash
python check_startup.py
```

#### 检查3：查看日志文件
```bash
type lol_auto_switch.log
```

---

## 问题6：CPU占用过高

### 解决方案
```python
# config.py
CAPTURE_FPS = 5  # 降低检测帧率
```

---

## 问题7：多显示器环境检测不准

### 解决方案
```python
# config.py
# 指定捕捉主显示器
CAPTURE_REGION = {
    "top": 0, 
    "left": 0, 
    "width": 1920,  # 你的主显示器宽度
    "height": 1080  # 你的主显示器高度
}
```

---

## 🔍 调试技巧

### 1. 查看实时日志
```bash
# Windows PowerShell
Get-Content lol_auto_switch.log -Wait -Tail 20
```

### 2. 保存调试截图
```python
# config.py
DEBUG_SAVE_SCREENSHOTS = True
```

截图会保存在 `debug_screenshots/` 目录。

### 3. 逐步测试
```bash
# 测试OCR功能
python test_ocr.py

# 测试窗口切换
python test_window.py

# 测试完整流程
python test_integration.py
```

---

## 📞 获取帮助

### 1. 收集信息
运行诊断工具：
```bash
python diagnostics.py > diagnostics_report.txt
```

### 2. 查看日志
```bash
# 最后50行日志
tail -50 lol_auto_switch.log
```

### 3. 检查配置
```python
from config import Config
Config.print_config()
```

---

## ✅ 快速修复清单

遇到问题时，按顺序尝试：

1. ☐ **以管理员身份运行程序**
2. ☐ 运行 `python check_startup.py` 检查模块
3. ☐ 运行 `python test_ocr.py` 测试OCR
4. ☐ 启用 `DEBUG_MODE = True` 查看详细日志
5. ☐ 游戏设置为**窗口化全屏**
6. ☐ 检查 Tesseract OCR 是否安装中文语言包
7. ☐ 查看 `lol_auto_switch.log` 日志文件

---

**大部分问题都可以通过"以管理员身份运行"解决！** 🔑
