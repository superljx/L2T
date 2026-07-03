"""
窗口管理模块
处理Windows窗口的查找、切换和激活
"""

import time
import win32gui
import win32con
import win32process
import psutil
from typing import Optional, List
from utils import setup_logger
from config import Config


class WindowManager:
    """Windows窗口管理器"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger("WindowManager", config.LOG_LEVEL, config.LOG_TO_FILE, config.LOG_FILE)
        self.logger.info("窗口管理器初始化完成")

    def is_edge_running(self) -> bool:
        """
        检查Edge浏览器是否正在运行

        Returns:
            bool: Edge是否运行
        """
        process_name = self.config.EDGE_PROCESS_NAME.lower()
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def find_edge_windows(self) -> List[int]:
        """
        查找所有Edge浏览器窗口

        Returns:
            List[int]: Edge窗口句柄列表
        """
        edge_windows = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                # 检查窗口标题是否包含Edge关键词
                for keyword in self.config.EDGE_WINDOW_TITLE_KEYWORDS:
                    if keyword in window_text:
                        edge_windows.append(hwnd)
                        break
            return True

        win32gui.EnumWindows(callback, None)
        return edge_windows

    def get_window_process_name(self, hwnd: int) -> Optional[str]:
        """
        获取窗口对应的进程名

        Args:
            hwnd: 窗口句柄

        Returns:
            Optional[str]: 进程名
        """
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name()
        except Exception as e:
            self.logger.debug(f"获取窗口进程名失败: {e}")
            return None

    def find_edge_window_by_url(self, url_keyword: str = "douyin") -> Optional[int]:
        """
        查找包含特定URL的Edge窗口（通过标题匹配）

        Args:
            url_keyword: URL关键词

        Returns:
            Optional[int]: 窗口句柄
        """
        edge_windows = self.find_edge_windows()

        for hwnd in edge_windows:
            window_text = win32gui.GetWindowText(hwnd)
            if url_keyword.lower() in window_text.lower():
                self.logger.debug(f"找到匹配窗口: {window_text}")
                return hwnd

        # 如果没找到匹配的，返回第一个Edge窗口
        if edge_windows:
            self.logger.debug(f"未找到匹配URL的窗口，返回第一个Edge窗口")
            return edge_windows[0]

        return None

    def activate_window(self, hwnd: int) -> bool:
        """
        激活指定窗口

        Args:
            hwnd: 窗口句柄

        Returns:
            bool: 是否成功
        """
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")

            # 检查窗口是否最小化
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)

            # 方法1: 使用ShowWindow和SetForegroundWindow
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.BringWindowToTop(hwnd)

            # 方法2: 使用Shell.AppActivate（更可靠）
            try:
                # 获取窗口标题
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    shell.AppActivate(window_text)
                    time.sleep(0.3)
            except:
                pass

            # 方法3: 尝试SetForegroundWindow
            try:
                # 模拟Alt按键来获得前台权限
                shell.SendKeys('%')
                time.sleep(0.1)
                win32gui.SetForegroundWindow(hwnd)
            except Exception as e:
                self.logger.debug(f"SetForegroundWindow失败: {e}")

            time.sleep(self.config.WINDOW_SWITCH_DELAY)

            # 验证窗口是否确实被激活
            foreground_hwnd = win32gui.GetForegroundWindow()
            success = foreground_hwnd == hwnd

            if success:
                window_text = win32gui.GetWindowText(hwnd)
                self.logger.info(f"窗口已激活: {window_text}")
            else:
                # 即使不是前台窗口，只要显示出来就算部分成功
                if win32gui.IsWindowVisible(hwnd):
                    self.logger.warning(f"窗口已显示但可能不在前台")
                    return True

            return success

        except Exception as e:
            self.logger.error(f"激活窗口失败: {e}")
            return False

    def switch_to_edge(self, url_keyword: str = "douyin") -> bool:
        """
        切换到Edge浏览器窗口

        Args:
            url_keyword: URL关键词（用于查找特定标签页）

        Returns:
            bool: 是否成功
        """
        self.logger.info("正在切换到Edge浏览器...")

        # 检查Edge是否运行
        if not self.is_edge_running():
            self.logger.warning("Edge浏览器未运行")
            return False

        # 查找Edge窗口
        hwnd = self.find_edge_window_by_url(url_keyword)
        if hwnd is None:
            self.logger.warning("未找到Edge窗口")
            return False

        # 重试激活窗口
        for attempt in range(self.config.WINDOW_FOCUS_RETRY):
            if self.activate_window(hwnd):
                return True
            self.logger.warning(f"激活窗口失败，重试 {attempt + 1}/{self.config.WINDOW_FOCUS_RETRY}")
            time.sleep(0.5)

        return False

    def get_foreground_window_info(self) -> dict:
        """
        获取当前前台窗口信息

        Returns:
            dict: 窗口信息
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_text = win32gui.GetWindowText(hwnd)
            process_name = self.get_window_process_name(hwnd)

            return {
                'hwnd': hwnd,
                'title': window_text,
                'process': process_name
            }
        except Exception as e:
            self.logger.error(f"获取前台窗口信息失败: {e}")
            return {}

    def is_edge_foreground(self) -> bool:
        """
        检查Edge是否是当前前台窗口

        Returns:
            bool: Edge是否在前台
        """
        info = self.get_foreground_window_info()
        if not info:
            return False

        process_name = info.get('process', '').lower()
        return self.config.EDGE_PROCESS_NAME.lower() in process_name

    def simulate_alt_tab(self):
        """
        模拟Alt+Tab切换窗口
        注意：这种方法不如直接激活窗口可靠，保留作为备用方案
        """
        import pyautogui
        self.logger.info("执行Alt+Tab切换")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(self.config.WINDOW_SWITCH_DELAY)
