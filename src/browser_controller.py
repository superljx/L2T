"""
浏览器控制模块
控制Edge浏览器打开页面和管理标签页
"""

import subprocess
import time
from typing import Optional
from utils import setup_logger
from config import Config


class BrowserController:
    """Edge浏览器控制器"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger("BrowserController", config.LOG_LEVEL, config.LOG_TO_FILE, config.LOG_FILE)
        self.logger.info("浏览器控制器初始化完成")

    def open_edge_with_url(self, url: str) -> bool:
        """
        打开Edge浏览器并访问指定URL

        Args:
            url: 目标URL

        Returns:
            bool: 是否成功启动
        """
        try:
            self.logger.info(f"正在打开Edge浏览器: {url}")

            # 使用subprocess启动Edge
            # 注意：在Windows上，msedge.exe通常在PATH中
            subprocess.Popen([
                "msedge.exe",
                url
            ], shell=True)

            self.logger.info("Edge浏览器启动命令已发送")
            return True

        except FileNotFoundError:
            self.logger.error("未找到msedge.exe，请确保Edge浏览器已安装")
            return False
        except Exception as e:
            self.logger.error(f"打开Edge失败: {e}")
            return False

    def open_target_page(self) -> bool:
        """
        打开目标页面（抖音）

        Returns:
            bool: 是否成功
        """
        return self.open_edge_with_url(self.config.TARGET_URL)

    def wait_for_page_load(self, timeout: float = None) -> bool:
        """
        等待页面加载完成

        Args:
            timeout: 超时时间（秒），None则使用配置值

        Returns:
            bool: 是否在超时前完成
        """
        if timeout is None:
            timeout = self.config.MAX_PAGE_LOAD_WAIT

        wait_time = self.config.PAGE_LOAD_WAIT
        self.logger.info(f"等待页面加载 {wait_time}秒...")

        time.sleep(wait_time)
        return True

    def is_url_accessible(self, url: str) -> bool:
        """
        检查URL是否可访问（简单实现）

        Args:
            url: 目标URL

        Returns:
            bool: 是否可访问
        """
        try:
            import urllib.request
            import urllib.error

            # 简单的HEAD请求检查
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            self.logger.warning(f"URL可访问性检查失败: {e}")
            return True  # 默认返回True，不阻塞操作

    def ensure_page_ready(self, url: str = None) -> bool:
        """
        确保页面已就绪

        Args:
            url: 目标URL，None则使用配置的TARGET_URL

        Returns:
            bool: 页面是否就绪
        """
        if url is None:
            url = self.config.TARGET_URL

        self.logger.info("检查页面就绪状态...")

        # 等待页面加载
        self.wait_for_page_load()

        # 可以在这里添加更复杂的就绪检查逻辑
        # 例如通过selenium检查DOM元素

        self.logger.info("页面应该已就绪")
        return True
