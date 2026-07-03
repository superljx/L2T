"""
工具函数模块
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import psutil


def setup_logger(name: str, log_level: str = "INFO", log_to_file: bool = False, log_file: str = "app.log"):
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        log_level: 日志级别
        log_to_file: 是否记录到文件
        log_file: 日志文件名

    Returns:
        logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有处理器
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_to_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class Timer:
    """简单的计时器类"""

    def __init__(self):
        self.start_time = time.time()
        self.last_time = self.start_time

    def reset(self):
        """重置计时器"""
        self.start_time = time.time()
        self.last_time = self.start_time

    def elapsed(self) -> float:
        """返回自启动以来的时间（秒）"""
        return time.time() - self.start_time

    def lap(self) -> float:
        """返回自上次lap以来的时间（秒）"""
        current_time = time.time()
        elapsed = current_time - self.last_time
        self.last_time = current_time
        return elapsed


class Cooldown:
    """冷却时间管理器"""

    def __init__(self, cooldown_seconds: float):
        self.cooldown_seconds = cooldown_seconds
        self.last_trigger_time = 0

    def can_trigger(self) -> bool:
        """检查是否可以触发"""
        return time.time() - self.last_trigger_time >= self.cooldown_seconds

    def trigger(self):
        """标记触发"""
        self.last_trigger_time = time.time()

    def remaining(self) -> float:
        """返回剩余冷却时间"""
        remaining = self.cooldown_seconds - (time.time() - self.last_trigger_time)
        return max(0, remaining)


class FrameBuffer:
    """帧缓冲器，用于连续帧判断"""

    def __init__(self, size: int):
        self.size = size
        self.buffer = []

    def add(self, value: bool):
        """添加一个布尔值"""
        self.buffer.append(value)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)

    def is_all_true(self) -> bool:
        """检查缓冲区是否全为True"""
        return len(self.buffer) == self.size and all(self.buffer)

    def is_all_false(self) -> bool:
        """检查缓冲区是否全为False"""
        return len(self.buffer) == self.size and not any(self.buffer)

    def clear(self):
        """清空缓冲区"""
        self.buffer.clear()

    def __len__(self):
        return len(self.buffer)


def is_process_running(process_name: str) -> bool:
    """
    检查进程是否正在运行

    Args:
        process_name: 进程名称（如 "msedge.exe"）

    Returns:
        bool: 进程是否运行
    """
    process_name = process_name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def get_cpu_usage() -> float:
    """
    获取当前进程的CPU使用率

    Returns:
        float: CPU使用率百分比
    """
    try:
        process = psutil.Process()
        return process.cpu_percent(interval=0.1)
    except Exception:
        return 0.0


def ensure_directory(path: str) -> Path:
    """
    确保目录存在

    Args:
        path: 目录路径

    Returns:
        Path: 目录Path对象
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def save_debug_screenshot(image_data, prefix: str = "debug"):
    """
    保存调试截图

    Args:
        image_data: numpy数组图像数据
        prefix: 文件名前缀
    """
    try:
        import cv2
        debug_dir = ensure_directory("debug_screenshots")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = debug_dir / f"{prefix}_{timestamp}.png"
        cv2.imwrite(str(filename), image_data)
        return filename
    except Exception as e:
        logging.error(f"保存调试截图失败: {e}")
        return None


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times = []
        self.start_time = time.time()

    def record_frame(self):
        """记录一帧"""
        self.frame_times.append(time.time())
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)

    def get_fps(self) -> float:
        """获取当前FPS"""
        if len(self.frame_times) < 2:
            return 0.0
        time_span = self.frame_times[-1] - self.frame_times[0]
        if time_span == 0:
            return 0.0
        return (len(self.frame_times) - 1) / time_span

    def get_runtime(self) -> float:
        """获取运行时间（秒）"""
        return time.time() - self.start_time

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'fps': self.get_fps(),
            'runtime': self.get_runtime(),
            'cpu_usage': get_cpu_usage()
        }


class WatchdogTimer:
    """看门狗定时器"""

    def __init__(self, timeout: float):
        self.timeout = timeout
        self.last_feed_time = time.time()

    def feed(self):
        """喂狗"""
        self.last_feed_time = time.time()

    def is_timeout(self) -> bool:
        """检查是否超时"""
        return time.time() - self.last_feed_time > self.timeout

    def reset(self):
        """重置"""
        self.last_feed_time = time.time()


def format_time(seconds: float) -> str:
    """
    格式化时间

    Args:
        seconds: 秒数

    Returns:
        str: 格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}小时{minutes}分"
