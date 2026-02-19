# -*- coding: utf-8 -*-
"""
GUI 主界面类
"""
import os
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from core.logger import print_log
from gui.utils import center_window_on_console


class AppGUI:
    """GUI 应用程序"""

    THEME = {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_panel": "#1e1e2f",
        "bg_input": "#2d2d3f",
        "text_main": "#e0e0e0",
        "text_sub": "#9aa3ad",
        "accent_green": "#00FF99",
        "accent_blue": "#00CCFF",
        "accent_pink": "#FF00CC",
        "accent_warn": "#FF3333",
        "btn_blue": "#007ACC",
        "btn_blue_hover": "#005A9E",
        "btn_gray": "#444444",
        "btn_gray_hover": "#666666",
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.start_time = None
        self.total_records = 0
        self.processed_records = 0
        self.win = None
        self.lbl_hint = None

        self.icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.ico"
        )
        self._set_app_icon(self.root)
        center_window_on_console(self.root, 1, 1)

    def _set_app_icon(self, window):
        """设置窗口图标"""
        if os.path.exists(self.icon_path):
            try:
                window.iconbitmap(self.icon_path)
            except Exception as e:
                print_log(f"图标加载失败: {e}", "WARN")

    def _on_progress_close_request(self):
        """用户点击关闭时，不中断任务，只最小化窗口。"""
        if not self.win:
            return
        try:
            self.win.iconify()
            if self.lbl_hint:
                self.lbl_hint.config(text="窗口已最小化，分析仍在后台继续运行")
        except Exception:
            pass

    def show_progress_window(self, title="正在处理"):
        """创建增强版进度窗口"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("560x320")
        win.minsize(560, 320)
        win.resizable(False, False)
        self._set_app_icon(win)
        center_window_on_console(win, 560, 320)

        win.attributes("-topmost", True)
        win.configure(bg=self.THEME["bg_secondary"])
        win.protocol("WM_DELETE_WINDOW", self._on_progress_close_request)

        frame = tk.Frame(
            win,
            bg=self.THEME["bg_panel"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#26354f",
        )
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        title_row = tk.Frame(frame, bg=self.THEME["bg_panel"])
        title_row.pack(fill="x", padx=16, pady=(14, 6))

        lbl_title = tk.Label(
            title_row,
            text="西关打包站智能分析系统",
            font=("Microsoft YaHei UI", 13, "bold"),
            fg=self.THEME["accent_green"],
            bg=self.THEME["bg_panel"],
        )
        lbl_title.pack(side="left")

        lbl_tag = tk.Label(
            title_row,
            text="处理中",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg="#0e1b2d",
            bg=self.THEME["accent_blue"],
            padx=8,
            pady=2,
        )
        lbl_tag.pack(side="right")

        self.lbl_status = tk.Label(
            frame,
            text="准备就绪...",
            font=("Microsoft YaHei UI", 10),
            fg=self.THEME["text_main"],
            bg=self.THEME["bg_panel"],
        )
        self.lbl_status.pack(pady=(2, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor="#2a3348",
            background=self.THEME["accent_green"],
            darkcolor="#00D98A",
            lightcolor=self.THEME["accent_green"],
            bordercolor="#2a3348",
        )

        self.progress = ttk.Progressbar(
            frame,
            length=470,
            mode="determinate",
            style="Custom.Horizontal.TProgressbar",
        )
        self.progress.pack(pady=(0, 10))

        info_frame = tk.Frame(frame, bg=self.THEME["bg_panel"])
        info_frame.pack(fill="x", padx=30)

        self.lbl_records = tk.Label(
            info_frame,
            text="记录数: --",
            font=("Microsoft YaHei UI", 9),
            fg=self.THEME["text_sub"],
            bg=self.THEME["bg_panel"],
        )
        self.lbl_records.pack(side="left")

        self.lbl_time = tk.Label(
            info_frame,
            text="预计剩余: --",
            font=("Microsoft YaHei UI", 9),
            fg=self.THEME["text_sub"],
            bg=self.THEME["bg_panel"],
        )
        self.lbl_time.pack(side="right")

        self.lbl_percent = tk.Label(
            frame,
            text="0%",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg=self.THEME["accent_blue"],
            bg=self.THEME["bg_panel"],
        )
        self.lbl_percent.pack(pady=(4, 2))

        action_row = tk.Frame(frame, bg=self.THEME["bg_panel"])
        action_row.pack(fill="x", padx=16, pady=(2, 12))

        btn_min = tk.Button(
            action_row,
            text="最小化",
            command=self._on_progress_close_request,
            font=("Microsoft YaHei UI", 9),
            bg=self.THEME["btn_blue"],
            fg="white",
            activebackground=self.THEME["btn_blue_hover"],
            activeforeground="white",
            relief="flat",
            padx=10,
            cursor="hand2",
        )
        btn_min.pack(side="right")

        self.lbl_hint = tk.Label(
            action_row,
            text="可最小化窗口，任务会继续执行",
            font=("Microsoft YaHei UI", 9),
            fg=self.THEME["text_sub"],
            bg=self.THEME["bg_panel"],
        )
        self.lbl_hint.pack(side="left")

        self.win = win
        self.start_time = time.time()
        self.root.update()

    def update_progress(self, value, text, records_info=None):
        """更新进度条和文案，支持记录数与剩余时间"""
        if not (hasattr(self, "progress") and self.progress):
            return

        self.progress["value"] = value
        self.lbl_status.config(text=text)
        self.lbl_percent.config(text=f"{value}%")

        if records_info:
            self.lbl_records.config(text=f"记录数: {records_info}")

        if self.start_time and value > 0:
            elapsed = time.time() - self.start_time
            if value < 100:
                estimated_total = elapsed / (value / 100)
                remaining = estimated_total - elapsed
                if remaining > 60:
                    time_str = f"{int(remaining / 60)}分{int(remaining % 60)}秒"
                elif remaining > 0:
                    time_str = f"{int(remaining)}秒"
                else:
                    time_str = "即将完成"
                self.lbl_time.config(text=f"预计剩余: {time_str}")
            else:
                self.lbl_time.config(text=f"已完成 | 用时: {elapsed:.1f}秒")

        self.root.update()
        print_log(f"进度 {value}%: {text}", "WORK")

    def set_total_records(self, total):
        """设置总记录数"""
        self.total_records = total
        self.processed_records = 0

    def update_record_progress(self, current, total=None):
        """更新记录处理进度"""
        if total:
            self.total_records = total
        self.processed_records = current
        if hasattr(self, "lbl_records"):
            self.lbl_records.config(text=f"记录数: {current}/{self.total_records}")
            self.root.update()

    def close_progress(self):
        """关闭进度窗口"""
        if hasattr(self, "win") and self.win:
            self.win.destroy()
            self.win = None

    def ask_sheet_name(self, sheet_names, file_name):
        """弹窗让用户选择工作表（支持多选对比）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("请选择工作表")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        self._set_app_icon(dialog)
        center_window_on_console(dialog, 450, 420)
        dialog.attributes("-topmost", True)
        dialog.configure(bg=self.THEME["bg_panel"])
        dialog.grab_set()

        label = tk.Label(
            dialog,
            text=f"文件：{os.path.basename(file_name)}",
            font=("Microsoft YaHei UI", 11, "bold"),
            fg=self.THEME["accent_green"],
            bg=self.THEME["bg_panel"],
            pady=10,
        )
        label.pack()

        tip_label = tk.Label(
            dialog,
            text="按住 Ctrl 可多选月份 | 双击或按 Enter 确认",
            font=("Microsoft YaHei UI", 9),
            fg=self.THEME["text_sub"],
            bg=self.THEME["bg_panel"],
        )
        tip_label.pack()

        list_frame = tk.Frame(dialog, bg=self.THEME["bg_panel"])
        list_frame.pack(pady=15, padx=20, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(
            list_frame,
            selectmode="extended",
            font=("Microsoft YaHei UI", 11),
            height=10,
            bg=self.THEME["bg_input"],
            fg=self.THEME["text_main"],
            selectbackground=self.THEME["btn_blue"],
            selectforeground="white",
            yscrollcommand=scrollbar.set,
            relief="flat",
            bd=0,
            activestyle="dotbox",
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        for name in sheet_names:
            listbox.insert("end", name)

        default_index = 0
        if sheet_names:
            try:
                current_month = datetime.now().month
                target_keyword = f"{current_month}月"
                print_log(f"正在寻找本月数据: [{target_keyword}...]", "AUTO")
                for i, name in enumerate(sheet_names):
                    if str(name).startswith(target_keyword) or str(name) == str(current_month):
                        default_index = i
                        print_log(f"已自动锁定当前月份: {name}", "AUTO")
                        break
            except Exception as e:
                print_log(f"智能匹配失败，回退默认项: {e}", "WARN")

            listbox.selection_set(default_index)
            listbox.see(default_index)
            listbox.activate(default_index)

        self.selected_sheets = []

        def on_confirm(event=None):
            indices = listbox.curselection()
            if not indices:
                active = listbox.index("active")
                if active >= 0:
                    indices = (active,)

            self.selected_sheets = [listbox.get(i) for i in indices]
            if self.selected_sheets:
                print_log(f"用户选择了: {', '.join(self.selected_sheets)}", "SELECT")
                dialog.destroy()
            else:
                tip_label.config(text="请先选择至少一个月份", fg=self.THEME["accent_warn"])

        def on_double_click(event):
            on_confirm()

        def on_cancel():
            self.selected_sheets = []
            dialog.destroy()

        listbox.bind("<Double-Button-1>", on_double_click)
        listbox.bind("<Return>", on_confirm)
        dialog.bind("<Return>", on_confirm)
        dialog.bind("<Escape>", lambda e: on_cancel())

        btn_frame = tk.Frame(dialog, bg=self.THEME["bg_panel"])
        btn_frame.pack(pady=15)

        btn_confirm = tk.Button(
            btn_frame,
            text="确认分析",
            command=on_confirm,
            bg=self.THEME["btn_blue"],
            fg="white",
            font=("Microsoft YaHei UI", 11, "bold"),
            width=14,
            height=1,
            cursor="hand2",
            activebackground=self.THEME["btn_blue_hover"],
            activeforeground="white",
            relief="flat",
        )
        btn_confirm.pack(side="left", padx=8)

        btn_cancel = tk.Button(
            btn_frame,
            text="取消",
            command=on_cancel,
            bg=self.THEME["btn_gray"],
            fg="white",
            font=("Microsoft YaHei UI", 10),
            width=10,
            cursor="hand2",
            activebackground=self.THEME["btn_gray_hover"],
            activeforeground="white",
            relief="flat",
        )
        btn_cancel.pack(side="left", padx=8)

        listbox.focus_set()
        dialog.wait_window()
        return self.selected_sheets
