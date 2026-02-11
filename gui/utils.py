# -*- coding: utf-8 -*-
"""
Windows 原生 API 工具模块
用于窗口控制、图标设置等底层操作
"""
import ctypes
from ctypes import wintypes
import os

# 定义 Windows API 常量
WM_SETICON = 0x80
ICON_SMALL = 0
ICON_BIG = 1
LR_LOADFROMFILE = 0x00000010
IMAGE_ICON = 1

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]

def get_console_window():
    """获取当前控制台窗口句柄"""
    try:
        return ctypes.windll.kernel32.GetConsoleWindow()
    except:
        return None

def set_console_icon(icon_path):
    """设置控制台窗口图标 (标题栏和任务栏)"""
    hwnd = get_console_window()
    if not hwnd or not os.path.exists(icon_path):
        return False
    
    try:
        # 加载图标资源
        h_icon = ctypes.windll.user32.LoadImageW(
            None, 
            os.path.abspath(icon_path), 
            IMAGE_ICON, 
            0, 0, 
            LR_LOADFROMFILE
        )
        
        if h_icon:
            # 设置窗口小图标 (标题栏)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon)
            # 设置窗口大图标 (任务栏)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon)
            return True
    except Exception as e:
        print(f"Set icon failed: {e}")
    return False

def center_window_on_console(tk_window, width=None, height=None):
    """
    将 Tkinter 窗口居中显示在控制台窗口之上
    如果无法获取控制台位置，则居中于屏幕
    """
    hwnd_console = get_console_window()
    
    # 获取窗口期望的尺寸
    tk_window.update_idletasks() # 确保尺寸计算正确
    w = width if width else tk_window.winfo_width()
    h = height if height else tk_window.winfo_height()
    
    # 默认屏幕居中
    screen_w = tk_window.winfo_screenwidth()
    screen_h = tk_window.winfo_screenheight()
    x = (screen_w - w) // 2
    y = (screen_h - h) // 2

    # 如果能获取控制台窗口，基于控制台计算居中
    if hwnd_console:
        rect = RECT()
        if ctypes.windll.user32.GetWindowRect(hwnd_console, ctypes.byref(rect)):
            console_w = rect.right - rect.left
            console_h = rect.bottom - rect.top
            
            # 计算相对坐标
            center_x = rect.left + (console_w // 2)
            center_y = rect.top + (console_h // 2)
            
            x = center_x - (w // 2)
            y = center_y - (h // 2)
            
            # 确保不超出屏幕边界 (可选)
            # x = max(0, min(x, screen_w - w))
            # y = max(0, min(y, screen_h - h))

    tk_window.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
