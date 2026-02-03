# -*- coding: utf-8 -*-
"""
文件选择与权限检查对话框
"""
import os
from tkinter import filedialog, messagebox

from core.logger import print_log, error_logger


def show_file_dialog():
    """显示文件选择对话框"""
    print_log("等待用户选择 Excel 文件...", "WAIT")
    
    file_path = filedialog.askopenfilename(
        title="请选择 '发货详单' 文件",
        filetypes=[("Excel files", "*.xlsx *.xlsm *.xls")]
    )
    
    if file_path:
        print_log(f"已捕获文件目标: {os.path.basename(file_path)}", "FILE")
    else:
        print_log("用户取消了文件选择", "WARN")
    
    return file_path


def check_file_access(path):
    """检查文件是否可访问（未被占用）"""
    print_log("正在进行文件占用检测...", "CHECK")
    max_retries = 3
    retry_count = 0
    
    while True:
        try:
            with open(path, 'a'):
                pass
            print_log("文件状态正常，权限已获取。", "OK")
            return True
        except PermissionError:
            retry_count += 1
            print_log(f"⚠️ 警告：文件被占用（可能正在Excel中打开） - 尝试 {retry_count}/{max_retries}", "WARN")
            error_logger.log_error(
                "文件被占用",
                f"文件正在被其他程序使用: {os.path.basename(path)}",
                suggestion="请关闭Excel或其他正在使用该文件的程序"
            )
            is_retry = messagebox.askretrycancel(
                "文件被占用", 
                f"检测到 Excel 文件正在被打开！\n\n请先【关闭】Excel 文件，然后点击【重试】。\n({os.path.basename(path)})\n\n尝试次数: {retry_count}/{max_retries}"
            )
            if not is_retry:
                return False
        except Exception as e:
            error_logger.log_error(
                "文件访问错误",
                f"无法访问文件: {e}",
                exception=e,
                suggestion="请检查文件是否存在、是否有读取权限"
            )
            error_logger.show_error_dialog(
                "📛 文件访问错误",
                f"无法访问文件:\n{e}",
                suggestion="请检查:\n1. 文件是否存在\n2. 是否有读取权限\n3. 文件路径是否正确"
            )
            return False
