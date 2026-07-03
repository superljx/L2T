# 调参指南与优化方案

## 📊 参数调优完整指南

### 1. 亮度阈值调整（最关键）

#### 步骤1：采集数据

运行亮度测试脚本：

```bash
python test_brightness.py
```

#### 步骤2：记录数据

| 场景 | 亮度值 | 备注 |
|------|--------|------|
| 正常游戏 | 45-55 | 根据实际记录 |
| 阵亡状态 | 20-30 | 画面变暗 |
| 技能特效 | 60-70 | 可能造成干扰 |
| 加载界面 | 35-45 | 可能误判 |

#### 步骤3：计算阈值

```python
阈值 = (正常亮度 - 阵亡亮度) × 0.6  # 保留60%的安全边界

例如：
正常亮度 = 50
阵亡亮度 = 25
差值 = 25
建议阈值 = 25 × 0.6 = 15

但实际应该设置 20-30，因为：
- 15太敏感，容易误判
- 20-25：激进模式
- 25-30：平衡模式
- 30-35：保守模式
```

#### 步骤4：验证测试

```bash
python test_integration.py
```

在测试中观察：
- ✅ 阵亡时能触发
- ✅ 正常游戏不触发
- ✅ 技能特效不触发

### 2. 确认帧数调整

#### 原理

```
连续N帧都检测到阵亡 → 才确认为阵亡
```

#### 影响

| 帧数 | 延迟 | 误判风险 | 适用场景 |
|------|------|----------|----------|
| 2帧 | ~250ms | 高 | 追求极致速度 |
| 3帧 | ~375ms | 中等 | 平衡（推荐） |
| 4帧 | ~500ms | 低 | 画面闪烁严重 |
| 5帧 | ~625ms | 很低 | 稳定优先 |

#### 计算公式

```python
延迟时间 = 确认帧数 / 检测FPS

例如：
CONFIRM_FRAMES = 3
CAPTURE_FPS = 8
延迟 = 3 / 8 = 0.375秒 = 375ms
```

### 3. 检测帧率调整

#### 性能对比

| FPS | CPU占用 | 延迟 | 适用场景 |
|-----|---------|------|----------|
| 5 | ~8% | 高 | 低端电脑 |
| 8 | ~12% | 中等 | 推荐 |
| 10 | ~15% | 低 | 高性能电脑 |
| 15 | ~22% | 很低 | 过度优化 |

#### 建议

- **低端配置**：5-6 FPS
- **主流配置**：8 FPS（默认）
- **高端配置**：10 FPS

> ⚠️ 超过10 FPS收益递减，不建议

### 4. 冷却时间设置

#### 目的

防止短时间内重复触发切换。

#### 设置建议

```python
# 根据游戏场景设置
COOLDOWN_SECONDS = 15  # 推荐值

# 激进模式（快速连续触发）
COOLDOWN_SECONDS = 8

# 保守模式（避免频繁切换）
COOLDOWN_SECONDS = 20
```

#### 考虑因素

- 游戏模式（ARAM复活快 → 短冷却）
- 游戏阶段（后期复活慢 → 长冷却）
- 个人偏好

## 🎯 常见场景优化方案

### 场景1：频繁误判

**症状**：没有阵亡就切换窗口

**诊断**：

```bash
# 启用调试模式
python test_brightness.py
```

观察亮度变化，如果发现：
- 技能特效时亮度波动大 → 增加确认帧数
- 正常游戏亮度也很低 → 降低阈值不是解决方案

**解决方案**：

```python
# config.py
BRIGHTNESS_THRESHOLD = 35  # 增大阈值
CONFIRM_FRAMES = 4         # 增加确认帧数

# 或启用ROI区域检测
ROI_ENABLED = True
ROI_REGION = {
    "top": 0.45,     # 聚焦画面中下部
    "left": 0.35,    
    "width": 0.3,    
    "height": 0.15   
}
```

### 场景2：检测不到阵亡

**症状**：死了也不切换

**诊断**：

1. 运行亮度测试，观察阵亡时亮度
2. 检查基准亮度是否正确学习

**解决方案**：

```python
# config.py
BRIGHTNESS_THRESHOLD = 20  # 降低阈值
CONFIRM_FRAMES = 2         # 减少确认帧数

# 确保自适应开启
ADAPTIVE_THRESHOLD = True
ADAPTIVE_LEARNING_FRAMES = 50  # 更长的学习时间
```

### 场景3：响应延迟高

**症状**：死后很久才切换

**诊断**：

```python
延迟 = 确认帧数 / 检测FPS + 窗口切换延迟

例如：
3帧 / 5FPS + 0.5s = 1.1秒
```

**解决方案**：

```python
# config.py
CAPTURE_FPS = 10           # 提高检测频率
CONFIRM_FRAMES = 2         # 减少确认要求
WINDOW_SWITCH_DELAY = 0.3  # 减少切换等待
```

### 场景4：CPU占用高

**症状**：程序运行时电脑卡顿

**解决方案**：

```python
# config.py
CAPTURE_FPS = 5            # 降低帧率
ENABLE_PERFORMANCE_MODE = True

# 限制捕捉区域（仅捕捉游戏窗口）
CAPTURE_REGION = {
    "top": 0, 
    "left": 0, 
    "width": 1920, 
    "height": 1080
}

# 禁用不必要的功能
DEBUG_MODE = False
DEBUG_SAVE_SCREENSHOTS = False
```

### 场景5：多显示器环境

**问题**：检测到错误的屏幕

**解决方案**：

```python
# 方法1：指定主显示器区域
CAPTURE_REGION = {
    "top": 0, 
    "left": 0, 
    "width": 1920,  # 主显示器分辨率
    "height": 1080
}

# 方法2：指定第二显示器
CAPTURE_REGION = {
    "top": 0, 
    "left": 1920,   # 第二显示器从1920开始
    "width": 1920, 
    "height": 1080
}
```

## 🔬 高级优化技巧

### 1. 自适应阈值

**原理**：自动学习正常亮度，动态调整判断标准

```python
# config.py
ADAPTIVE_THRESHOLD = True
ADAPTIVE_LEARNING_FRAMES = 100  # 学习100帧建立基准
```

**优点**：
- 适应不同游戏画面风格
- 适应昼夜地图差异
- 减少手动调参

**缺点**：
- 需要初始学习期
- 如果学习期包含阵亡画面会影响基准

### 2. 区域检测（ROI）

**原理**：只检测屏幕特定区域，提高准确性

```python
# config.py
ROI_ENABLED = True
ROI_REGION = {
    "top": 0.4,      # 画面40%处开始
    "left": 0.3,     # 左边30%
    "width": 0.4,    # 宽度40%
    "height": 0.2    # 高度20%
}
```

**如何选择ROI区域**：

1. 运行 `python test_capture.py`
2. 打开生成的截图
3. 找到角色通常所在位置
4. 框选该区域，计算百分比

**推荐区域**：
- 游戏画面中心偏下（角色位置）
- 避开小地图、技能栏（UI元素）

### 3. 加权亮度计算

**原理**：画面中心权重更高

```python
# config.py
BRIGHTNESS_METHOD = "weighted"  # 默认是 "average"
```

**效果**：
- 中心区域（角色）变化更敏感
- 边缘区域（背景）影响较小

### 4. 性能监控

**启用性能监控**：

```python
# config.py
DEBUG_MODE = True

# 程序会每30帧打印一次性能信息：
# FPS: 8.2 | CPU: 12.3% | 亮度: 45.2
```

## 📈 配置模板

### 模板1：极致性能（追求速度）

```python
# config.py
CAPTURE_FPS = 10
CONFIRM_FRAMES = 2
BRIGHTNESS_THRESHOLD = 25
COOLDOWN_SECONDS = 10
WINDOW_SWITCH_DELAY = 0.3
ADAPTIVE_THRESHOLD = False  # 禁用以减少计算
```

**适合**：高性能电脑，追求极致响应速度

### 模板2：稳定可靠（追求准确）

```python
# config.py
CAPTURE_FPS = 6
CONFIRM_FRAMES = 4
BRIGHTNESS_THRESHOLD = 35
COOLDOWN_SECONDS = 20
ADAPTIVE_THRESHOLD = True
ROI_ENABLED = True
```

**适合**：画面复杂，容易误判的情况

### 模板3：低配电脑（节省资源）

```python
# config.py
CAPTURE_FPS = 5
CONFIRM_FRAMES = 3
BRIGHTNESS_THRESHOLD = 30
ENABLE_PERFORMANCE_MODE = True
CAPTURE_REGION = {"top": 0, "left": 0, "width": 1280, "height": 720}
```

**适合**：CPU性能有限的电脑

### 模板4：ARAM模式（快节奏）

```python
# config.py
CAPTURE_FPS = 10
CONFIRM_FRAMES = 2
BRIGHTNESS_THRESHOLD = 28
COOLDOWN_SECONDS = 8  # ARAM复活快
```

**适合**：ARAM等快节奏模式

## 🧪 调参流程

### 标准调参流程

```
1. 基准测试
   ↓
   运行 test_brightness.py
   记录正常/阵亡亮度值
   
2. 初步配置
   ↓
   设置阈值 = 差值 × 0.6
   确认帧数 = 3
   检测FPS = 8
   
3. 实战测试
   ↓
   运行 test_integration.py
   在游戏中验证
   
4. 调整优化
   ↓
   误判多 → 增大阈值/帧数
   漏检测 → 减小阈值/帧数
   延迟高 → 增大FPS
   CPU高 → 减小FPS
   
5. 最终验证
   ↓
   运行 main.py
   连续游戏1-2小时
   记录触发情况
```

## 💡 故障诊断决策树

```
检测不准确？
├─ 频繁误判
│  ├─ 技能特效干扰 → 增加CONFIRM_FRAMES到4-5
│  ├─ 画面闪烁 → 启用ROI_ENABLED
│  └─ 阈值太低 → 增大BRIGHTNESS_THRESHOLD到35-40
│
├─ 漏检测（死了不触发）
│  ├─ 阈值太高 → 减小BRIGHTNESS_THRESHOLD到20-25
│  ├─ 帧数太多 → 减小CONFIRM_FRAMES到2
│  └─ 基准错误 → 重启程序重新学习
│
└─ 延迟太高
   ├─ FPS太低 → 增加CAPTURE_FPS到10
   ├─ 帧数太多 → 减小CONFIRM_FRAMES到2
   └─ 切换慢 → 减小WINDOW_SWITCH_DELAY到0.3
```

---

**祝调参顺利！** 🎯
