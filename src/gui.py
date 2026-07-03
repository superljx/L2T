"""
LOL 自动切换系统 GUI界面
提供现代化的图形界面控制程序
"""

import customtkinter as ctk
from tkinter import scrolledtext
import threading
import sys
import time
from datetime import datetime
from config import Config
from main import AutoSwitchController

# 设置主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LogRedirector:
    """日志重定向到GUI"""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if message.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.text_widget.configure(state='normal')
            self.text_widget.insert('end', f"[{timestamp}] {message}\n")
            self.text_widget.see('end')
            self.text_widget.configure(state='disabled')

    def flush(self):
        pass


class LOLAutoSwitchGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("LOL 自动切换系统 v1.3.4")
        self.window.geometry("900x700")

        # 防止窗口被调整得太小
        self.window.minsize(800, 600)

        # 控制器
        self.controller = None
        self.is_running = False
        self.monitor_thread = None

        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        # 主容器
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== 标题区域 =====
        title_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🎮 LOL 自动切换系统",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="阵亡时自动切换到抖音，复活时自动切回游戏",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack()

        # ===== 状态指示器 =====
        status_frame = ctk.CTkFrame(main_container)
        status_frame.pack(fill="x", pady=(0, 20))

        status_label = ctk.CTkLabel(
            status_frame,
            text="状态:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_label.pack(side="left", padx=10)

        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="● 未运行",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.status_indicator.pack(side="left", padx=5)

        # ===== 控制按钮区域 =====
        control_frame = ctk.CTkFrame(main_container)
        control_frame.pack(fill="x", pady=(0, 20))

        # 启动/停止按钮
        self.start_button = ctk.CTkButton(
            control_frame,
            text="▶ 启动检测",
            command=self.start_detection,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.start_button.pack(side="left", expand=True, fill="x", padx=5)

        self.stop_button = ctk.CTkButton(
            control_frame,
            text="⏸ 停止检测",
            command=self.stop_detection,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            state="disabled"
        )
        self.stop_button.pack(side="left", expand=True, fill="x", padx=5)

        # ===== 快捷操作按钮 =====
        quick_actions_frame = ctk.CTkFrame(main_container)
        quick_actions_frame.pack(fill="x", pady=(0, 20))

        quick_label = ctk.CTkLabel(
            quick_actions_frame,
            text="快捷操作",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quick_label.pack(anchor="w", padx=10, pady=(10, 5))

        buttons_frame = ctk.CTkFrame(quick_actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 测试OCR
        test_ocr_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍 测试OCR",
            command=self.test_ocr,
            height=35
        )
        test_ocr_btn.pack(side="left", expand=True, fill="x", padx=2)

        # 测试倒计时
        test_timer_btn = ctk.CTkButton(
            buttons_frame,
            text="⏱ 测试倒计时",
            command=self.test_timer,
            height=35
        )
        test_timer_btn.pack(side="left", expand=True, fill="x", padx=2)

        # 系统诊断
        diagnose_btn = ctk.CTkButton(
            buttons_frame,
            text="🔧 系统诊断",
            command=self.run_diagnostics,
            height=35
        )
        diagnose_btn.pack(side="left", expand=True, fill="x", padx=2)

        # 清空日志
        clear_log_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑 清空日志",
            command=self.clear_log,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_log_btn.pack(side="left", expand=True, fill="x", padx=2)

        # ===== 配置选项 =====
        config_frame = ctk.CTkFrame(main_container)
        config_frame.pack(fill="x", pady=(0, 20))

        config_label = ctk.CTkLabel(
            config_frame,
            text="配置选项",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 配置项网格
        config_grid = ctk.CTkFrame(config_frame, fg_color="transparent")
        config_grid.pack(fill="x", padx=10, pady=(0, 10))

        # OCR开关
        self.ocr_switch = ctk.CTkSwitch(
            config_grid,
            text="使用OCR识别",
            font=ctk.CTkFont(size=13)
        )
        self.ocr_switch.pack(side="left", padx=10)
        self.ocr_switch.select() if Config.USE_OCR else self.ocr_switch.deselect()

        # 调试模式
        self.debug_switch = ctk.CTkSwitch(
            config_grid,
            text="调试模式",
            font=ctk.CTkFont(size=13)
        )
        self.debug_switch.pack(side="left", padx=10)
        self.debug_switch.select() if Config.DEBUG_MODE else self.debug_switch.deselect()

        # ===== 日志区域 =====
        log_frame = ctk.CTkFrame(main_container)
        log_frame.pack(fill="both", expand=True)

        log_label = ctk.CTkLabel(
            log_frame,
            text="运行日志",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 使用CTkTextbox替代scrolledtext
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 重定向日志
        self.log_redirector = LogRedirector(self.log_text)

        # 底部信息栏
        footer_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        footer_frame.pack(fill="x")

        footer_label = ctk.CTkLabel(
            footer_frame,
            text="版本 v1.3.4 | © 2026 LOL Auto Switch",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        footer_label.pack()

    def log(self, message):
        """添加日志"""
        self.log_redirector.write(message)

    def update_status(self, text, color):
        """更新状态指示器"""
        self.status_indicator.configure(text=f"● {text}", text_color=color)

    def start_detection(self):
        """启动检测"""
        if self.is_running:
            self.log("检测已在运行中")
            return

        self.log("正在启动检测系统...")

        # 更新配置
        Config.USE_OCR = self.ocr_switch.get()
        Config.DEBUG_MODE = self.debug_switch.get()

        # 禁用启动按钮，启用停止按钮
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        # 更新状态
        self.update_status("运行中", "#2ecc71")

        # 在新线程中启动控制器
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.run_controller, daemon=True)
        self.monitor_thread.start()

        self.log("✓ 检测系统已启动")

    def run_controller(self):
        """运行控制器（在独立线程中）"""
        try:
            # 创建控制器实例
            self.controller = AutoSwitchController(Config)

            # 重定向日志
            import logging
            handler = logging.StreamHandler(self.log_redirector)
            handler.setFormatter(logging.Formatter('%(name)s: %(message)s'))
            logging.getLogger().addHandler(handler)

            # 启动
            self.controller.start()

        except Exception as e:
            self.log(f"错误: {e}")
            self.is_running = False
            self.window.after(0, self.reset_buttons)

    def stop_detection(self):
        """停止检测"""
        if not self.is_running:
            return

        self.log("正在停止检测系统...")

        self.is_running = False

        if self.controller:
            self.controller.stop()

        # 重置按钮状态
        self.reset_buttons()

        # 更新状态
        self.update_status("已停止", "gray")

        self.log("✓ 检测系统已停止")

    def reset_buttons(self):
        """重置按钮状态"""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def test_ocr(self):
        """测试OCR功能"""
        self.log("运行OCR测试...")
        threading.Thread(target=self._test_ocr_thread, daemon=True).start()

    def _test_ocr_thread(self):
        import subprocess
        try:
            result = subprocess.run(
                ["python", "test_ocr.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            # 清理输出中的特殊字符
            output = output.replace('✗', 'X').replace('✓', 'V')
            self.log(output)
        except Exception as e:
            self.log(f"OCR测试失败: {e}")

    def test_timer(self):
        """测试倒计时识别"""
        self.log("运行倒计时测试...")
        threading.Thread(target=self._test_timer_thread, daemon=True).start()

    def _test_timer_thread(self):
        import subprocess
        try:
            result = subprocess.run(
                ["python", "test_timer.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            # 清理输出中的特殊字符
            output = output.replace('✗', 'X').replace('✓', 'V')
            self.log(output)
        except Exception as e:
            self.log(f"倒计时测试失败: {e}")

    def run_diagnostics(self):
        """运行系统诊断"""
        self.log("运行系统诊断...")
        threading.Thread(target=self._diagnostics_thread, daemon=True).start()

    def _diagnostics_thread(self):
        import subprocess
        try:
            result = subprocess.run(
                ["python", "diagnostics.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            # 清理输出中的特殊字符
            output = output.replace('✗', 'X').replace('✓', 'V')
            self.log(output)
        except Exception as e:
            self.log(f"诊断失败: {e}")

    def clear_log(self):
        """清空日志"""
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')
        self.log("日志已清空")

    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            self.stop_detection()
        self.window.destroy()

    def run(self):
        """运行GUI"""
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 显示欢迎信息
        self.log("=" * 60)
        self.log("欢迎使用 LOL 自动切换系统 v1.3.4")
        self.log("=" * 60)
        self.log("功能说明:")
        self.log("• 自动检测英雄联盟阵亡状态")
        self.log("• 自动切换到抖音页面")
        self.log("• 倒计时结束自动切回游戏")
        self.log("=" * 60)
        self.log("点击 [启动检测] 开始使用")
        self.log("")

        self.window.mainloop()


if __name__ == "__main__":
    app = LOLAutoSwitchGUI()
    app.run()
