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
    """主 GUI 应用程序"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        self.start_time = None
        self.total_records = 0
        self.processed_records = 0
        self.win = None
        self.icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logo.ico') # Path relative to project root
        self._set_app_icon(self.root)
        
        # 将不可见的主窗口也居中于控制台，方便后续作为父窗口
        center_window_on_console(self.root, 1, 1)

    def _set_app_icon(self, window):
        """设置窗口图标"""
        if os.path.exists(self.icon_path):
            try:
                window.iconbitmap(self.icon_path)
            except Exception as e:
                print_log(f"图标加载失败: {e}", "WARN")

    def show_progress_window(self, title="正在处理"):
        """创建增强版进度条窗口"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("550x220")
        self._set_app_icon(win)
        
        # 居中显示于控制台
        center_window_on_console(win, 550, 220)
        
        win.attributes("-topmost", True)
        win.overrideredirect(True)  # 无边框风格
        
        frame = tk.Frame(win, bg='#1e1e1e', relief='raised', bd=2)
        frame.pack(fill='both', expand=True)
        
        lbl_title = tk.Label(frame, text="⚡ 李小泡专属·智能分析系统 ⚡", 
                           font=("微软雅黑", 14, "bold"), fg="#00FF99", bg='#1e1e1e')
        lbl_title.pack(pady=(15, 5))
        
        self.lbl_status = tk.Label(frame, text="准备就绪...", 
                                 font=("微软雅黑", 10), fg="white", bg='#1e1e1e')
        self.lbl_status.pack(pady=3)
        
        # 进度条样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar", 
                       troughcolor='#333', background='#00FF99', 
                       darkcolor='#00CC77', lightcolor='#00FF99')
        
        self.progress = ttk.Progressbar(frame, length=450, mode='determinate',
                                        style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10)
        
        # 详细信息行
        info_frame = tk.Frame(frame, bg='#1e1e1e')
        info_frame.pack(fill='x', padx=30)
        
        self.lbl_records = tk.Label(info_frame, text="记录数: --", 
                                   font=("微软雅黑", 9), fg="#888", bg='#1e1e1e')
        self.lbl_records.pack(side='left')
        
        self.lbl_time = tk.Label(info_frame, text="预计剩余: --", 
                                font=("微软雅黑", 9), fg="#888", bg='#1e1e1e')
        self.lbl_time.pack(side='right')
        
        # 进度百分比
        self.lbl_percent = tk.Label(frame, text="0%", 
                                   font=("微软雅黑", 12, "bold"), fg="#00CCFF", bg='#1e1e1e')
        self.lbl_percent.pack(pady=5)
        
        self.win = win
        self.start_time = time.time()
        self.root.update()

    def update_progress(self, value, text, records_info=None):
        """更新进度条和文字，支持记录数和剩余时间显示"""
        if hasattr(self, 'progress') and self.progress:
            self.progress['value'] = value
            self.lbl_status.config(text=text)
            self.lbl_percent.config(text=f"{value}%")
            
            # 更新记录数信息
            if records_info:
                self.lbl_records.config(text=f"记录数: {records_info}")
            
            # 计算预计剩余时间
            if self.start_time and value > 0:
                elapsed = time.time() - self.start_time
                if value < 100:
                    estimated_total = elapsed / (value / 100)
                    remaining = estimated_total - elapsed
                    if remaining > 60:
                        time_str = f"{int(remaining/60)}分{int(remaining%60)}秒"
                    elif remaining > 0:
                        time_str = f"{int(remaining)}秒"
                    else:
                        time_str = "即将完成"
                    self.lbl_time.config(text=f"预计剩余: {time_str}")
                else:
                    self.lbl_time.config(text=f"已完成! 用时: {elapsed:.1f}秒")
            
            self.root.update()  # 强制刷新界面
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
        if hasattr(self, 'lbl_records'):
            self.lbl_records.config(text=f"记录数: {current}/{self.total_records}")
            self.root.update()

    def close_progress(self):
        """关闭进度条窗口"""
        if hasattr(self, 'win') and self.win:
            self.win.destroy()
            self.win = None

    def ask_sheet_name(self, sheet_names, file_name):
        """弹出窗口让用户选择工作表（支持多选对比）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("请选择工作表")
        dialog.geometry("450x420")
        self._set_app_icon(dialog)
        
        # 居中显示于控制台
        center_window_on_console(dialog, 450, 420)
        dialog.attributes("-topmost", True)
        dialog.configure(bg='#1e1e1e')
        dialog.grab_set()  # 模态对话框，确保焦点
        
        # 标题
        label = tk.Label(dialog, text=f"📂 文件：{os.path.basename(file_name)}", 
                        font=("微软雅黑", 11, "bold"), fg="#00FF99", bg='#1e1e1e', pady=10)
        label.pack()
        
        tip_label = tk.Label(dialog, text="💡 按住 Ctrl 可多选月份 | 双击或按Enter确认", 
                            font=("微软雅黑", 9), fg="#888", bg='#1e1e1e')
        tip_label.pack()
        
        # 多选列表框架
        list_frame = tk.Frame(dialog, bg='#1e1e1e')
        list_frame.pack(pady=15, padx=20, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(list_frame, selectmode='extended', font=("微软雅黑", 11),
                            height=10, bg='#2d2d2d', fg='white', 
                            selectbackground='#007ACC', selectforeground='white',
                            yscrollcommand=scrollbar.set, relief='flat', bd=0,
                            activestyle='dotbox')
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        for name in sheet_names:
            listbox.insert('end', name)
        
        # === 智能月份锁定逻辑 ===
        default_index = 0
        if sheet_names:
            try:
                current_month = datetime.now().month 
                target_keyword = f"{current_month}月"
                print_log(f"正在寻找本月数据: [{target_keyword}...] ", "AUTO")
                for i, name in enumerate(sheet_names):
                    if str(name).startswith(target_keyword) or str(name) == str(current_month):
                        default_index = i
                        print_log(f"⚡ 已自动锁定当前月份: {name}", "AUTO")
                        break 
            except Exception as e:
                print_log(f"智能匹配出错，回退到默认: {e}", "WARN")
            listbox.selection_set(default_index)
            listbox.see(default_index)
            listbox.activate(default_index)
        
        self.selected_sheets = []
        
        def on_confirm(event=None):
            """确认选择"""
            indices = listbox.curselection()
            if not indices:
                # 如果没有选择，使用激活的项目
                active = listbox.index('active')
                if active >= 0:
                    indices = (active,)
            self.selected_sheets = [listbox.get(i) for i in indices]
            if self.selected_sheets:
                print_log(f"用户选择了: {', '.join(self.selected_sheets)}", "SELECT")
                dialog.destroy()
            else:
                # 显示提示
                tip_label.config(text="⚠️ 请先选择至少一个月份！", fg="#FF3333")
        
        def on_double_click(event):
            """双击确认"""
            on_confirm()
        
        def on_cancel():
            """取消选择"""
            self.selected_sheets = []
            dialog.destroy()
        
        # 绑定事件
        listbox.bind('<Double-Button-1>', on_double_click)
        listbox.bind('<Return>', on_confirm)
        dialog.bind('<Return>', on_confirm)
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # 按钮区域
        btn_frame = tk.Frame(dialog, bg='#1e1e1e')
        btn_frame.pack(pady=15)
        
        btn_confirm = tk.Button(btn_frame, text="✅ 确认分析", command=on_confirm, 
                               bg="#007ACC", fg="white", font=("微软雅黑", 11, "bold"), 
                               width=14, height=1, cursor="hand2",
                               activebackground="#005A9E", activeforeground="white")
        btn_confirm.pack(side='left', padx=8)
        
        btn_cancel = tk.Button(btn_frame, text="❌ 取消", command=on_cancel, 
                              bg="#444", fg="white", font=("微软雅黑", 10), 
                              width=10, cursor="hand2",
                              activebackground="#666", activeforeground="white")
        btn_cancel.pack(side='left', padx=8)
        
        # 设置焦点到列表框
        listbox.focus_set()
        
        dialog.wait_window() 
        return self.selected_sheets
