"""
输入控制模块
模拟键盘和鼠标输入
"""

import time
import pyautogui
from typing import Optional
from utils import setup_logger
from config import Config


class InputController:
    """键盘鼠标输入控制器"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger("InputController", config.LOG_LEVEL, config.LOG_TO_FILE, config.LOG_FILE)

        # 配置pyautogui
        pyautogui.PAUSE = 0.1  # 每次操作后的暂停时间
        pyautogui.FAILSAFE = True  # 鼠标移到屏幕角落时抛出异常（安全措施）

        self.logger.info("输入控制器初始化完成")

    def press_key(self, key: str, delay: float = 0.0) -> bool:
        """
        按下指定按键

        Args:
            key: 按键名称（如 'space', 'enter', 'a'）
            delay: 按键前的延迟（秒）

        Returns:
            bool: 是否成功
        """
        try:
            if delay > 0:
                time.sleep(delay)

            self.logger.debug(f"按下按键: {key}")
            pyautogui.press(key)
            return True

        except Exception as e:
            self.logger.error(f"按键操作失败: {e}")
            return False

    def press_play_key(self) -> bool:
        """
        按下播放/暂停键（空格键）

        Returns:
            bool: 是否成功
        """
        self.logger.info(f"发送播放键: {self.config.PLAY_KEY}")
        return self.press_key(
            self.config.PLAY_KEY,
            delay=self.config.PLAY_KEY_DELAY
        )

    def hotkey(self, *keys) -> bool:
        """
        按下组合键

        Args:
            *keys: 按键序列（如 'ctrl', 'c'）

        Returns:
            bool: 是否成功
        """
        try:
            self.logger.debug(f"按下组合键: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True

        except Exception as e:
            self.logger.error(f"组合键操作失败: {e}")
            return False

    def type_text(self, text: str, interval: float = 0.1) -> bool:
        """
        输入文本

        Args:
            text: 要输入的文本
            interval: 每个字符之间的间隔（秒）

        Returns:
            bool: 是否成功
        """
        try:
            self.logger.debug(f"输入文本: {text[:50]}...")
            pyautogui.write(text, interval=interval)
            return True

        except Exception as e:
            self.logger.error(f"文本输入失败: {e}")
            return False

    def click(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1) -> bool:
        """
        点击鼠标

        Args:
            x: X坐标（None则点击当前位置）
            y: Y坐标
            clicks: 点击次数

        Returns:
            bool: 是否成功
        """
        try:
            if x is not None and y is not None:
                self.logger.debug(f"点击位置: ({x}, {y})")
                pyautogui.click(x, y, clicks=clicks)
            else:
                self.logger.debug(f"点击当前位置")
                pyautogui.click(clicks=clicks)
            return True

        except Exception as e:
            self.logger.error(f"点击操作失败: {e}")
            return False

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        移动鼠标

        Args:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动持续时间（秒）

        Returns:
            bool: 是否成功
        """
        try:
            self.logger.debug(f"移动鼠标到: ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            return True

        except Exception as e:
            self.logger.error(f"鼠标移动失败: {e}")
            return False

    def get_mouse_position(self) -> tuple:
        """
        获取当前鼠标位置

        Returns:
            tuple: (x, y)
        """
        return pyautogui.position()

    def get_screen_size(self) -> tuple:
        """
        获取屏幕尺寸

        Returns:
            tuple: (width, height)
        """
        return pyautogui.size()
