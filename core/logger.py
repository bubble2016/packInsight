# -*- coding: utf-8 -*-
"""
错误日志系统
"""
import os
import traceback
from datetime import datetime

from config import OUTPUT_FOLDER_NAME, ERROR_LOG_FOLDER_NAME


class ErrorLogger:
    """错误日志管理器"""
    def __init__(self):
        self.errors = []
        self.log_file = None
        
    def init_log_file(self):
        """初始化日志文件"""
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        log_dir = os.path.join(desktop, OUTPUT_FOLDER_NAME, ERROR_LOG_FOLDER_NAME)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(log_dir, f"error_log_{timestamp}.txt")
        return self.log_file
    
    def log_error(self, error_type, message, exception=None, suggestion=None):
        """记录错误"""
        error_entry = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': error_type,
            'message': message,
            'traceback': traceback.format_exc() if exception else None,
            'suggestion': suggestion
        }
        self.errors.append(error_entry)
        
        # 打印错误
        print(f"\033[1;31m[ERROR] {error_type}: {message}\033[0m")
        if suggestion:
            print(f"\033[1;33m[建议] {suggestion}\033[0m")
        
        return error_entry
    
    def export_log(self):
        """导出错误日志"""
        if not self.errors:
            return None
        
        if not self.log_file:
            self.init_log_file()
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("  打包站智能分析系统 - 错误日志\n")
                f.write(f"  导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for i, err in enumerate(self.errors, 1):
                    f.write(f"--- 错误 #{i} ---\n")
                    f.write(f"时间: {err['time']}\n")
                    f.write(f"类型: {err['type']}\n")
                    f.write(f"描述: {err['message']}\n")
                    if err['suggestion']:
                        f.write(f"建议: {err['suggestion']}\n")
                    if err['traceback']:
                        f.write(f"堆栈:\n{err['traceback']}\n")
                    f.write("\n")
            
            return self.log_file
        except Exception as e:
            print(f"\033[1;31m无法导出错误日志: {e}\033[0m")
            return None
    
    def show_error_dialog(self, title, message, suggestion=None):
        """显示用户友好的错误对话框"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            
            full_message = f"{message}"
            if suggestion:
                full_message += f"\n\n💡 建议:\n{suggestion}"
            if self.errors:
                full_message += f"\n\n📁 错误日志已保存到:\n{self.export_log()}"
            
            messagebox.showerror(title, full_message)
            root.destroy()
        except Exception:
            print(f"\033[1;31m{title}: {message}\033[0m")
            if suggestion:
                print(f"\033[1;33m建议: {suggestion}\033[0m")


def print_log(message, tag="INFO"):
    """带时间戳的炫酷日志输出"""
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[1;36m[{current_time}]\033[0m \033[1;33m[{tag:<5}]\033[0m {message}")


# 初始化全局错误日志管理器
error_logger = ErrorLogger()
