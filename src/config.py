"""
配置文件 - 所有可调参数集中管理
"""

class Config:
    """系统配置类"""

    # ==================== 检测参数 ====================

    # 屏幕捕捉参数
    CAPTURE_FPS = 8  # 检测帧率（建议5-10）
    CAPTURE_REGION = None  # None=全屏，或指定区域 {"top": 0, "left": 0, "width": 1920, "height": 1080}

    # OCR检测参数
    USE_OCR = True  # 是否使用OCR文字识别（推荐）
    TESSERACT_PATH = None  # Tesseract安装路径（None则使用系统PATH）
    # Windows示例: r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # 防误判参数
    CONFIRM_FRAMES = 2  # 连续N帧确认才触发（防止闪烁误判）
    COOLDOWN_SECONDS = 15  # 触发后冷却时间（秒），防止重复触发

    # ==================== 窗口控制参数 ====================

    # Edge浏览器参数
    EDGE_PROCESS_NAME = "msedge.exe"
    EDGE_WINDOW_TITLE_KEYWORDS = ["Edge", "Microsoft Edge"]
    TARGET_URL = "https://www.douyin.com/?recommend=1"

    # 窗口切换参数
    WINDOW_SWITCH_DELAY = 0.5  # 切换窗口后等待时间（秒）
    WINDOW_FOCUS_RETRY = 3  # 窗口激活重试次数

    # ==================== 浏览器控制参数 ====================

    # 页面加载参数
    PAGE_LOAD_WAIT = 3.0  # 页面加载等待时间（秒）
    PAGE_READY_CHECK_INTERVAL = 0.5  # 页面就绪检查间隔（秒）
    MAX_PAGE_LOAD_WAIT = 10.0  # 最大等待时间（秒）

    # 播放控制参数
    PLAY_KEY = "space"  # 播放/暂停键
    PLAY_KEY_DELAY = 0.3  # 按键前等待时间（秒）

    # ==================== 性能参数 ====================

    # 性能优化
    ENABLE_PERFORMANCE_MODE = True  # 启用性能模式（降低检测精度以提升速度）
    MAX_CPU_PERCENT = 15  # 最大CPU占用百分比

    # Watchdog参数
    WATCHDOG_ENABLED = True  # 启用看门狗
    WATCHDOG_TIMEOUT = 10  # 看门狗超时时间（秒）

    # ==================== 日志参数 ====================

    # 日志配置
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_TO_FILE = True  # 是否保存日志到文件
    LOG_FILE = "lol_auto_switch.log"

    # 调试模式
    DEBUG_MODE = True  # 调试模式（显示更多信息）
    DEBUG_SHOW_BRIGHTNESS = False  # 显示实时亮度值
    DEBUG_SAVE_SCREENSHOTS = False  # 保存触发时的截图
    DEBUG_SAVE_TIMER_ROI = True  # 保存倒计时识别区域（用于调试）

    # ==================== 游戏检测参数 ====================

    # LOL游戏检测
    LOL_PROCESS_NAME = "League of Legends.exe"
    REQUIRE_LOL_RUNNING = True  # 是否要求LOL必须运行才开始检测


    @classmethod
    def validate(cls):
        """验证配置参数的有效性"""
        errors = []

        if cls.CAPTURE_FPS < 1 or cls.CAPTURE_FPS > 30:
            errors.append("CAPTURE_FPS应在1-30之间")

        if cls.CONFIRM_FRAMES < 1:
            errors.append("CONFIRM_FRAMES至少为1")

        if cls.COOLDOWN_SECONDS < 0:
            errors.append("COOLDOWN_SECONDS不能为负数")

        if errors:
            raise ValueError(f"配置验证失败：{'; '.join(errors)}")

        return True

    @classmethod
    def print_config(cls):
        """打印当前配置"""
        print("=" * 60)
        print("当前系统配置：")
        print("=" * 60)
        print(f"检测帧率: {cls.CAPTURE_FPS} FPS")
        print(f"检测方式: {'OCR文字识别' if hasattr(cls, 'USE_OCR') and cls.USE_OCR else '模板匹配'}")
        print(f"确认帧数: {cls.CONFIRM_FRAMES}")
        print(f"冷却时间: {cls.COOLDOWN_SECONDS}秒")
        print(f"目标URL: {cls.TARGET_URL}")
        print(f"调试模式: {'开启' if cls.DEBUG_MODE else '关闭'}")
        print(f"看门狗: {'开启' if cls.WATCHDOG_ENABLED else '关闭'}")
        print("=" * 60)


# 预设配置方案
class PresetConfigs:
    """预设配置方案"""

    @staticmethod
    def high_performance():
        """高性能模式（低延迟，可能误判）"""
        Config.CAPTURE_FPS = 10
        Config.CONFIRM_FRAMES = 2

    @staticmethod
    def balanced():
        """平衡模式（推荐）"""
        Config.CAPTURE_FPS = 8
        Config.CONFIRM_FRAMES = 2

    @staticmethod
    def stable():
        """稳定模式（低误判，延迟略高）"""
        Config.CAPTURE_FPS = 6
        Config.CONFIRM_FRAMES = 3

    @staticmethod
    def debug():
        """调试模式"""
        Config.DEBUG_MODE = True
        Config.DEBUG_SHOW_BRIGHTNESS = True
        Config.LOG_LEVEL = "DEBUG"
