"""
LOL游戏状态检测 + 自动浏览器切换播放系统
主控制模块
"""

import sys
import time
import signal
from typing import Optional
from config import Config, PresetConfigs
from detector import GameStateDetector
from window_manager import WindowManager
from browser_controller import BrowserController
from input_controller import InputController
from utils import (
    setup_logger, Cooldown, WatchdogTimer,
    is_process_running, format_time
)


class AutoSwitchController:
    """自动切换控制器"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger("MainController", config.LOG_LEVEL, config.LOG_TO_FILE, config.LOG_FILE)

        # 初始化各个模块
        self.detector = GameStateDetector(config)
        self.window_manager = WindowManager(config)
        self.browser_controller = BrowserController(config)
        self.input_controller = InputController(config)

        # 冷却管理器
        self.cooldown = Cooldown(config.COOLDOWN_SECONDS)

        # 看门狗
        self.watchdog = WatchdogTimer(config.WATCHDOG_TIMEOUT) if config.WATCHDOG_ENABLED else None

        # 运行状态
        self.is_running = False
        self.last_trigger_time = 0

        # 复活倒计时管理
        self.respawn_timer_start = None  # 倒计时开始时间
        self.respawn_duration = None     # 倒计时总时长
        self.is_waiting_respawn = False  # 是否正在等待复活

        self.logger.info("=" * 60)
        self.logger.info("自动切换控制器初始化完成")
        self.logger.info("=" * 60)

    def check_prerequisites(self) -> bool:
        """
        检查运行前提条件

        Returns:
            bool: 是否满足条件
        """
        self.logger.info("正在检查系统前提条件...")

        # 检查LOL是否运行（如果要求）
        if self.config.REQUIRE_LOL_RUNNING:
            if not is_process_running(self.config.LOL_PROCESS_NAME):
                self.logger.warning(f"未检测到LOL进程: {self.config.LOL_PROCESS_NAME}")
                self.logger.warning("如不需要此检查，请设置 REQUIRE_LOL_RUNNING = False")
                return False
            else:
                self.logger.info(f"✓ LOL进程已运行")

        # 检查Edge是否已安装（尝试启动检测）
        self.logger.info("✓ 系统前提条件检查完成")
        return True

    def switch_back_to_game(self):
        """切换回游戏并暂停视频"""
        self.logger.info("=" * 60)
        self.logger.info("复活倒计时结束，切换回游戏")
        self.logger.info("=" * 60)

        # 1. 暂停Edge中的视频
        if self.window_manager.is_edge_foreground():
            self.logger.info("暂停视频播放...")
            if self.input_controller.press_play_key():
                self.logger.info("✓ 已发送暂停键")
            time.sleep(0.3)

        # 2. 切换回LOL游戏
        self.logger.info("正在切换回游戏窗口...")

        # 查找LOL窗口
        lol_window = self.find_lol_window()
        if lol_window:
            if self.window_manager.activate_window(lol_window):
                self.logger.info("✓ 已切换回游戏")
            else:
                self.logger.warning("切换回游戏失败")
        else:
            self.logger.warning("未找到游戏窗口")

        # 3. 重置检测器为存活状态
        self.detector.reset_to_alive()

        self.logger.info("=" * 60)
        self.logger.info("切换流程完成")
        self.logger.info("=" * 60)

    def find_lol_window(self):
        """查找LOL游戏窗口"""
        import win32gui

        lol_keywords = ["League of Legends", "英雄联盟", "LOL"]
        windows = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                for keyword in lol_keywords:
                    if keyword in window_text:
                        windows.append(hwnd)
                        break
            return True

        win32gui.EnumWindows(callback, None)
        return windows[0] if windows else None

    def handle_dead_state(self, respawn_timer: Optional[int] = None):
        """
        处理阵亡状态的逻辑

        Args:
            respawn_timer: 复活倒计时（秒）
        """
        # 记录开始时间，用于计算切换耗时
        switch_start_time = time.time()

        self.logger.info("=" * 60)
        self.logger.info("触发自动切换流程")
        self.logger.info("=" * 60)

        # 1. 检查Edge是否运行，如果没运行则启动
        if not self.window_manager.is_edge_running():
            self.logger.info("Edge未运行，正在启动...")
            if not self.browser_controller.open_target_page():
                self.logger.error("启动Edge失败")
                return
            # 等待浏览器启动
            time.sleep(2)
            self.browser_controller.wait_for_page_load()
        else:
            self.logger.info("Edge已运行")

        # 2. 智能切换到抖音页面（如果存在则切换，不存在则打开）
        if not self.window_manager.switch_to_douyin_or_open(self.config.TARGET_URL):
            self.logger.error("切换到抖音失败")
            return

        # 3. 等待窗口获得焦点
        time.sleep(0.5)

        # 注意：不再自动发送播放键，由用户手动控制播放

        # 4. 计算切换耗时并补偿
        switch_elapsed = time.time() - switch_start_time

        # 5. 设置复活倒计时（扣除切换耗时）
        if respawn_timer is not None and respawn_timer > 0:
            # 扣除切换耗时，确保倒计时更准确
            adjusted_timer = max(1, respawn_timer - switch_elapsed)  # 至少保留1秒

            self.respawn_timer_start = time.time()
            self.respawn_duration = adjusted_timer
            self.is_waiting_respawn = True

            if abs(adjusted_timer - respawn_timer) >= 1:
                self.logger.info(f"✓ 已设置复活倒计时: {respawn_timer:.0f}秒 → {adjusted_timer:.1f}秒（已扣除切换耗时{switch_elapsed:.1f}秒）")
            else:
                self.logger.info(f"✓ 已设置复活倒计时: {adjusted_timer:.1f}秒")
        else:
            self.is_waiting_respawn = False
            self.logger.warning("未识别到倒计时，不会自动切回游戏")

        self.logger.info("=" * 60)
        self.logger.info(f"切换流程完成（耗时{switch_elapsed:.1f}秒）")
        self.logger.info("=" * 60)

    def run_detection_loop(self):
        """主检测循环"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("开始检测循环")
        self.logger.info("=" * 60)

        frame_delay = 1.0 / self.config.CAPTURE_FPS
        loop_count = 0
        start_time = time.time()

        try:
            while self.is_running:
                loop_start = time.time()

                # 喂狗
                if self.watchdog:
                    self.watchdog.feed()

                # 执行检测
                state, respawn_timer = self.detector.detect()

                # 检查复活倒计时是否结束
                if self.is_waiting_respawn and self.respawn_timer_start:
                    elapsed = time.time() - self.respawn_timer_start
                    remaining = self.respawn_duration - elapsed

                    # 倒计时即将结束（提前2秒切回）
                    if remaining <= 2 and remaining > 0:
                        self.switch_back_to_game()
                        self.is_waiting_respawn = False
                        self.respawn_timer_start = None
                        self.respawn_duration = None
                        # 重置冷却，允许下次检测
                        self.cooldown.trigger()
                    elif remaining <= 0:
                        # 倒计时已结束但还未切回（容错处理）
                        self.logger.warning("倒计时已结束但未切回，立即执行切回")
                        self.switch_back_to_game()
                        self.is_waiting_respawn = False
                        self.respawn_timer_start = None
                        self.respawn_duration = None
                        self.cooldown.trigger()

                # 处理检测结果
                if state == "dead":
                    # 检查是否正在等待复活
                    if self.is_waiting_respawn:
                        # 正在等待复活，不要重复触发
                        if loop_count % 30 == 0:
                            self.logger.debug(f"已在倒计时中，等待复活...")
                    # 检查冷却时间
                    elif self.cooldown.can_trigger():
                        self.handle_dead_state(respawn_timer)
                    else:
                        remaining = self.cooldown.remaining()
                        if loop_count % 10 == 0:  # 每10帧打印一次
                            self.logger.info(f"检测到阵亡，但在冷却中（剩余 {remaining:.1f}秒）")

                # 定期打印状态
                loop_count += 1
                if loop_count % 30 == 0:  # 每30帧打印一次统计
                    stats = self.detector.get_stats()
                    runtime = format_time(time.time() - start_time)
                    status_info = f"运行时间: {runtime} | FPS: {stats['fps']:.1f} | 状态: {state}"

                    # 如果正在等待复活，显示剩余时间
                    if self.is_waiting_respawn and self.respawn_timer_start:
                        elapsed = time.time() - self.respawn_timer_start
                        remaining = max(0, self.respawn_duration - elapsed)
                        status_info += f" | 复活倒计时: {remaining:.0f}秒"

                    status_info += f" | CPU: {stats['cpu_usage']:.1f}%"
                    self.logger.info(status_info)

                # 检查看门狗
                if self.watchdog and self.watchdog.is_timeout():
                    self.logger.error("看门狗超时！检测循环可能卡死")
                    self.watchdog.reset()

                # 控制帧率
                elapsed = time.time() - loop_start
                sleep_time = max(0, frame_delay - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.logger.info("\n收到中断信号，正在停止...")
        except Exception as e:
            self.logger.error(f"检测循环异常: {e}", exc_info=True)
        finally:
            self.stop()

    def start(self):
        """启动控制器"""
        if self.is_running:
            self.logger.warning("控制器已在运行中")
            return

        # 检查前提条件
        if not self.check_prerequisites():
            self.logger.error("前提条件检查失败，无法启动")
            return

        self.is_running = True
        self.run_detection_loop()

    def stop(self):
        """停止控制器"""
        if not self.is_running:
            return

        self.logger.info("正在停止控制器...")
        self.is_running = False

        # 关闭检测器
        self.detector.close()

        self.logger.info("控制器已停止")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def signal_handler(signum, frame):
    """信号处理器"""
    print("\n收到停止信号，正在退出...")
    sys.exit(0)


def main():
    """主入口函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 打印欢迎信息
    print("=" * 60)
    print("LOL游戏状态检测 + 自动浏览器切换播放系统")
    print("=" * 60)
    print()

    # 验证配置
    try:
        Config.validate()
        Config.print_config()
    except ValueError as e:
        print(f"配置错误: {e}")
        return

    # 询问用户选择配置模式
    print("\n请选择运行模式：")
    print("1. 平衡模式（推荐）")
    print("2. 高性能模式（低延迟）")
    print("3. 稳定模式（低误判）")
    print("4. 调试模式")
    print("5. 使用当前配置")

    try:
        choice = input("\n请输入选项 (1-5, 默认为1): ").strip() or "1"

        if choice == "1":
            PresetConfigs.balanced()
            print("✓ 已切换到平衡模式")
        elif choice == "2":
            PresetConfigs.high_performance()
            print("✓ 已切换到高性能模式")
        elif choice == "3":
            PresetConfigs.stable()
            print("✓ 已切换到稳定模式")
        elif choice == "4":
            PresetConfigs.debug()
            print("✓ 已切换到调试模式")
        elif choice == "5":
            print("✓ 使用当前配置")
        else:
            print("无效选项，使用平衡模式")
            PresetConfigs.balanced()

    except (EOFError, KeyboardInterrupt):
        print("\n用户取消")
        return

    print("\n按 Ctrl+C 停止程序\n")
    time.sleep(1)

    # 创建并启动控制器
    with AutoSwitchController(Config) as controller:
        controller.start()


if __name__ == "__main__":
    main()
