"""
游戏状态检测模块
使用OCR文字识别检测LOL阵亡状态（检测"返回于"字样）
并提取复活倒计时
"""

import numpy as np
import cv2
import re
from mss import mss
from typing import Optional, Tuple
from utils import setup_logger, FrameBuffer, PerformanceMonitor, save_debug_screenshot
from config import Config

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("警告: pytesseract未安装，将使用备用的模板匹配方法")


class GameStateDetector:
    """游戏状态检测器"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger("Detector", config.LOG_LEVEL, config.LOG_TO_FILE, config.LOG_FILE)

        # MSS截图对象
        self.sct = mss()

        # 帧缓冲器（用于连续帧确认）
        self.frame_buffer = FrameBuffer(config.CONFIRM_FRAMES)

        # 性能监控
        self.perf_monitor = PerformanceMonitor()

        # 状态
        self.current_state = "alive"  # "alive" 或 "dead"
        self.last_detection_result = None

        # 复活倒计时
        self.respawn_timer = None  # 复活倒计时（秒）
        self.last_timer_value = None  # 上一次的倒计时值

        # OCR配置
        if TESSERACT_AVAILABLE and hasattr(config, 'TESSERACT_PATH') and config.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

        self.logger.info("游戏状态检测器初始化完成 (OCR文字识别模式)")

    def get_capture_region(self) -> dict:
        """
        获取截图区域

        Returns:
            dict: 截图区域参数
        """
        if self.config.CAPTURE_REGION:
            return self.config.CAPTURE_REGION

        # 使用主显示器
        monitor = self.sct.monitors[1]  # monitors[0]是所有显示器的总和，monitors[1]是主显示器
        return monitor

    def capture_screen(self) -> Optional[np.ndarray]:
        """
        捕获屏幕画面

        Returns:
            np.ndarray: 图像数组（BGR格式）
        """
        try:
            region = self.get_capture_region()
            screenshot = self.sct.grab(region)

            # 转换为numpy数组（BGRA -> BGR）
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            return img
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return None

    def preprocess_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        预处理图像用于OCR识别

        Args:
            image: BGR图像数组

        Returns:
            预处理后的灰度图像
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 二值化处理，提高白色文字的识别率
        # 阵亡界面的"返回于"文字通常是白色或浅色
        _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

        # 可选：形态学处理，增强文字
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=1)

        return binary

    def preprocess_for_gold_numbers(self, image: np.ndarray) -> list:
        """
        专门用于识别金色倒计时数字的预处理
        返回多种预处理结果供尝试

        Args:
            image: BGR图像数组

        Returns:
            list: 多种预处理后的图像
        """
        results = []

        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 方法1: 提取金色/橙色/黄色区域
        # 金色的HSV范围大约是：H: 15-35, S: 100-255, V: 100-255
        lower_gold = np.array([10, 100, 100])
        upper_gold = np.array([40, 255, 255])
        mask_gold = cv2.inRange(hsv, lower_gold, upper_gold)
        results.append(mask_gold)

        # 方法2: 提取高亮度区域（金色数字通常很亮）
        _, _, v_channel = cv2.split(hsv)
        _, bright = cv2.threshold(v_channel, 150, 255, cv2.THRESH_BINARY)
        results.append(bright)

        # 方法3: 灰度高阈值
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, high_threshold = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        results.append(high_threshold)

        # 方法4: 中等阈值
        _, mid_threshold = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
        results.append(mid_threshold)

        # 方法5: OTSU自适应
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results.append(otsu)

        return results

    def extract_respawn_timer(self, image: np.ndarray, text: str) -> Optional[int]:
        """
        从OCR文本中提取复活倒计时
        专门优化识别"返回于"下方的金色数字

        Args:
            image: BGR图像数组
            text: OCR识别的文本

        Returns:
            Optional[int]: 倒计时秒数，未找到返回None
        """
        try:
            # 方法1：从完整文本中提取数字
            patterns = [
                r'返回于\s*(\d+)',  # "返回于 15"
                r'返回\s*(\d+)',    # "返回 15"
                r'复活\s*(\d+)',    # "复活 15"
                r'于\s*(\d+)',      # "于 15"
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    timer = int(match.group(1))
                    if 0 <= timer <= 100:
                        self.logger.debug(f"从文本提取倒计时: {timer}秒 (模式: {pattern})")
                        return timer

            # 方法2：查找文本中的所有数字
            all_numbers = re.findall(r'\d+', text)
            if all_numbers:
                for num_str in all_numbers:
                    num = int(num_str)
                    if 1 <= num <= 100:
                        self.logger.debug(f"从数字列表提取倒计时: {num}秒")
                        return num

            # 方法3：在"返回于"下方区域单独识别金色数字（最重要）
            if TESSERACT_AVAILABLE:
                h, w = image.shape[:2]

                # 调整为更大的中心区域，确保包含倒计时
                # 倒计时通常在画面中心略偏下的位置
                x1 = int(w * 0.3)   # 左边30%
                x2 = int(w * 0.7)   # 右边70%
                y1 = int(h * 0.4)   # 上边40%
                y2 = int(h * 0.75)  # 下边75%
                roi = image[y1:y2, x1:x2]

                # 保存ROI用于调试
                if self.config.DEBUG_SAVE_TIMER_ROI or self.config.DEBUG_MODE:
                    try:
                        import datetime
                        timestamp = datetime.datetime.now().strftime("%H%M%S")
                        filename = save_debug_screenshot(roi, f"timer_roi_{timestamp}")
                        self.logger.debug(f"已保存倒计时ROI: {filename}")

                        # 同时保存完整画面
                        filename_full = save_debug_screenshot(image, f"full_screen_{timestamp}")
                        self.logger.debug(f"已保存完整画面: {filename_full}")
                    except Exception as e:
                        self.logger.debug(f"保存ROI失败: {e}")

                # 使用专门的金色数字预处理
                processed_images = self.preprocess_for_gold_numbers(roi)

                # 尝试多种OCR配置
                configs = [
                    '--psm 7 -c tessedit_char_whitelist=0123456789',  # 单行数字
                    '--psm 8 -c tessedit_char_whitelist=0123456789',  # 单词
                    '--psm 6 -c tessedit_char_whitelist=0123456789',  # 块文本
                    '--psm 13',  # 原始单行
                ]

                for idx, binary in enumerate(processed_images):
                    for config_idx, config in enumerate(configs):
                        try:
                            text_digits = pytesseract.image_to_string(binary, lang='eng', config=config)
                            numbers = re.findall(r'\d+', text_digits)

                            if numbers:
                                timer = int(numbers[0])
                                if 1 <= timer <= 100:
                                    self.logger.debug(f"从区域识别倒计时: {timer}秒 (预处理{idx+1}, 配置{config_idx+1})")
                                    if self.config.DEBUG_MODE:
                                        self.logger.debug(f"  识别文本: '{text_digits.strip()}'")
                                    return timer
                        except Exception as e:
                            continue

            self.logger.debug("所有方法都未能提取倒计时")
            return None

        except Exception as e:
            self.logger.error(f"提取倒计时异常: {e}")
            return None

    def detect_death_text_ocr(self, image: np.ndarray) -> Tuple[bool, Optional[int]]:
        """
        使用OCR检测死亡文字（"返回于"）并提取倒计时

        Args:
            image: BGR图像数组

        Returns:
            Tuple[bool, Optional[int]]: (是否检测到死亡, 倒计时秒数)
        """
        if not TESSERACT_AVAILABLE:
            self.logger.warning("pytesseract未安装，无法使用OCR")
            return False, None

        try:
            # 检测整个画面中心区域
            h, w = image.shape[:2]
            # 先检测"返回于"文字的大区域
            x1_text = int(w * 0.2)
            x2_text = int(w * 0.8)
            y1_text = int(h * 0.3)
            y2_text = int(h * 0.8)
            roi_text = image[y1_text:y2_text, x1_text:x2_text]

            # 预处理（用于识别白色"返回于"文字）
            processed = self.preprocess_image_for_ocr(roi_text)

            # OCR识别（简体中文）
            text = pytesseract.image_to_string(processed, lang='chi_sim', config='--psm 6')

            if self.config.DEBUG_MODE:
                self.logger.debug(f"OCR识别文本: '{text.strip()}'")

            # 检测关键字
            keywords = ["返回于", "返回", "复活", "于"]
            is_dead = False
            for keyword in keywords:
                if keyword in text:
                    is_dead = True
                    break

            # 提取倒计时（使用完整画面，而不是ROI）
            timer = None
            if is_dead:
                timer = self.extract_respawn_timer(image, text)  # 传入完整画面

                if timer is not None:
                    self.logger.debug(f"OCR检测: 死亡状态, 倒计时: {timer}秒")
                else:
                    self.logger.debug(f"OCR检测: 死亡状态, 未识别到倒计时")
                    if self.config.DEBUG_MODE:
                        self.logger.debug(f"  完整文本: {text[:100]}")

            return is_dead, timer

        except Exception as e:
            self.logger.error(f"OCR识别失败: {e}")
            return False, None

    def detect_death_text_template(self, image: np.ndarray) -> bool:
        """
        使用模板匹配检测死亡界面（备用方法）
        检测画面是否变暗且中心区域有大量白色像素（死亡界面特征）

        Args:
            image: BGR图像数组

        Returns:
            bool: 是否检测到死亡特征
        """
        h, w = image.shape[:2]

        # 检测中心区域
        x1 = int(w * 0.3)
        x2 = int(w * 0.7)
        y1 = int(h * 0.4)
        y2 = int(h * 0.7)
        roi = image[y1:y2, x1:x2]

        # 转换为灰度
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # 计算整体亮度
        avg_brightness = np.mean(gray)

        # 检测白色像素（文字）
        white_pixels = np.sum(gray > 200)
        total_pixels = gray.shape[0] * gray.shape[1]
        white_ratio = white_pixels / total_pixels

        # 死亡界面特征：画面较暗但有明显白色文字
        is_dead = avg_brightness < 80 and white_ratio > 0.05

        if self.config.DEBUG_MODE and is_dead:
            self.logger.debug(f"模板检测: 亮度={avg_brightness:.1f}, 白色比例={white_ratio:.3f}")

        return is_dead

    def is_dead_state(self, image: np.ndarray) -> Tuple[bool, Optional[int]]:
        """
        判断是否为阵亡状态并提取倒计时

        Args:
            image: BGR图像数组

        Returns:
            Tuple[bool, Optional[int]]: (是否为阵亡状态, 倒计时秒数)
        """
        # 优先使用OCR
        if TESSERACT_AVAILABLE and hasattr(self.config, 'USE_OCR') and self.config.USE_OCR:
            return self.detect_death_text_ocr(image)
        else:
            # 使用模板匹配作为备用（不支持倒计时提取）
            is_dead = self.detect_death_text_template(image)
            return is_dead, None

    def detect(self) -> Tuple[str, Optional[int]]:
        """
        执行检测

        Returns:
            Tuple[str, Optional[int]]: (状态, 倒计时)
                状态: "alive", "dead", "uncertain"
                倒计时: 复活倒计时秒数，None表示未检测到或不适用
        """
        # 记录性能
        self.perf_monitor.record_frame()

        # 捕获屏幕
        image = self.capture_screen()
        if image is None:
            return "uncertain", None

        # 检测是否为阵亡状态并提取倒计时
        is_dead, timer = self.is_dead_state(image)

        # 更新倒计时
        if is_dead and timer is not None:
            self.respawn_timer = timer
            if self.last_timer_value != timer:
                self.logger.debug(f"复活倒计时: {timer}秒")
                self.last_timer_value = timer

        # 添加到帧缓冲器
        self.frame_buffer.add(is_dead)

        # 连续帧确认
        if self.frame_buffer.is_all_true():
            # 连续N帧都是阵亡状态
            if self.current_state != "dead":
                if self.respawn_timer is not None:
                    self.logger.info(f"检测到阵亡状态！复活倒计时: {self.respawn_timer}秒")
                else:
                    self.logger.info(f"检测到阵亡状态！（未识别到倒计时）")
                if self.config.DEBUG_SAVE_SCREENSHOTS:
                    save_debug_screenshot(image, "dead_state")
                self.current_state = "dead"
            return "dead", self.respawn_timer
        elif self.frame_buffer.is_all_false() and self.current_state == "alive":
            # 只有在之前就是存活状态时，才继续保持存活
            # 如果是死亡状态，不要因为看不到死亡画面就判定为复活
            return "alive", None
        else:
            # 不确定状态或者从死亡状态等待复活
            # 保持当前状态，返回uncertain
            return "uncertain", self.respawn_timer

    def reset_to_alive(self):
        """
        重置为存活状态（由主控制器在倒计时结束后调用）
        """
        if self.current_state == "dead":
            self.logger.info("检测到存活状态（已复活）")
        self.current_state = "alive"
        self.respawn_timer = None
        self.last_timer_value = None
        self.frame_buffer.clear()

    def get_stats(self) -> dict:
        """
        获取检测器统计信息

        Returns:
            dict: 统计信息
        """
        stats = self.perf_monitor.get_stats()
        stats.update({
            'current_state': self.current_state,
            'buffer_size': len(self.frame_buffer),
            'detection_method': 'OCR' if TESSERACT_AVAILABLE else 'Template',
            'respawn_timer': self.respawn_timer
        })
        return stats

    def reset(self):
        """重置检测器状态"""
        self.frame_buffer.clear()
        self.current_state = "alive"
        self.respawn_timer = None
        self.last_timer_value = None
        self.logger.info("检测器已重置")

    def close(self):
        """关闭检测器"""
        self.sct.close()
        self.logger.info("检测器已关闭")
