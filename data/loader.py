# -*- coding: utf-8 -*-
"""
多线程数据加载器
"""
import threading
import traceback
from queue import Queue
import warnings

import pandas as pd

from config import STAGE_INIT, STAGE_READ, STAGE_CLEAN, STAGE_ANALYZE, STAGE_VISUALIZE, STAGE_SAVE
from core.logger import print_log, error_logger


class ThreadedDataLoader:
    """多线程数据加载器 - 避免 UI 阻塞，支持精确进度追踪"""
    
    def __init__(self, gui_app):
        self.gui = gui_app
        self.result_queue = Queue()
        self.progress_queue = Queue()
        self.error_queue = Queue()
        self.cancel_event = threading.Event()
        self.worker_thread = None
        self._load_func = None
        self._current_stage = 'init'
        self._sheet_count = 0
        self._loaded_count = 0
    
    def set_load_function(self, func):
        """设置数据加载函数"""
        self._load_func = func
    
    def _calc_progress(self, stage_name, sub_progress=0):
        """计算精确进度百分比
        
        Args:
            stage_name: 阶段名称 ('init', 'read', 'clean', 'analyze', 'visualize', 'save')
            sub_progress: 阶段内子进度 (0-100)
        Returns:
            总进度百分比 (0-100)
        """
        stages = {
            'init': STAGE_INIT,
            'read': STAGE_READ,
            'clean': STAGE_CLEAN,
            'analyze': STAGE_ANALYZE,
            'visualize': STAGE_VISUALIZE,
            'save': STAGE_SAVE
        }
        if stage_name not in stages:
            return 0
        
        start, end = stages[stage_name]
        return start + int((end - start) * sub_progress / 100)
    
    def load_sheets_async(self, file_path, sheet_names, callback):
        """异步加载多个工作表（非阻塞）"""
        self.cancel_event.clear()
        self._sheet_count = len(sheet_names)
        self._loaded_count = 0
        
        def worker():
            all_dfs = []
            total_records = 0
            
            for i, sheet in enumerate(sheet_names):
                if self.cancel_event.is_set():
                    self.result_queue.put(('cancelled', None, None))
                    return
                
                # 计算精确进度：读取阶段内的子进度
                sub_pct = int((i / len(sheet_names)) * 100)
                pct = self._calc_progress('read', sub_pct)
                self.progress_queue.put((pct, f"正在读取: {sheet} ({i+1}/{len(sheet_names)})", total_records))
                
                try:
                    if self._load_func:
                        df = self._load_func(file_path, sheet)
                    else:
                        warnings.filterwarnings("ignore", category=UserWarning)
                        df = pd.read_excel(file_path, sheet_name=sheet, header=1)
                        df.columns = df.columns.str.strip()
                        df['月份标签'] = sheet
                    
                    if df is not None and not df.empty:
                        all_dfs.append(df)
                        total_records += len(df)
                        self._loaded_count += 1
                        
                except Exception as e:
                    # 详细错误信息
                    error_info = {
                        'type': '工作表读取失败',
                        'sheet': sheet,
                        'message': str(e),
                        'traceback': traceback.format_exc()
                    }
                    self.error_queue.put(error_info)
                    self.result_queue.put(('error', f"读取工作表 [{sheet}] 失败: {e}", error_info))
                    return
            
            # 合并数据
            if all_dfs:
                try:
                    self.progress_queue.put((30, "正在合并数据...", total_records))
                    merged_df = pd.concat(all_dfs, ignore_index=True)
                    self.result_queue.put(('success', merged_df, {'total_records': total_records}))
                except Exception as e:
                    error_info = {
                        'type': '数据合并失败',
                        'message': str(e),
                        'traceback': traceback.format_exc()
                    }
                    self.error_queue.put(error_info)
                    self.result_queue.put(('error', f"数据合并失败: {e}", error_info))
            else:
                error_info = {'type': '无数据', 'message': '未能加载任何有效数据'}
                self.result_queue.put(('error', '未能加载任何数据', error_info))
        
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
        
        # 启动 GUI 轮询
        self._poll_progress(callback)
    
    def _poll_progress(self, callback):
        """轮询进度队列，更新 GUI（带错误处理）"""
        try:
            # 处理进度更新
            while not self.progress_queue.empty():
                try:
                    pct, text, records = self.progress_queue.get_nowait()
                    self.gui.update_progress(pct, text, records_info=f"已加载 {records} 条")
                except Exception as e:
                    print_log(f"进度更新失败: {e}", "WARN")
            
            # 检查结果
            if not self.result_queue.empty():
                try:
                    result = self.result_queue.get_nowait()
                    status = result[0]
                    data = result[1] if len(result) > 1 else None
                    extra = result[2] if len(result) > 2 else None
                    callback(status, data, extra)
                    return
                except Exception as e:
                    error_logger.log_error("结果处理失败", str(e), exception=e)
                    callback('error', f"结果处理异常: {e}", None)
                    return
            
            # 继续轮询
            if self.worker_thread and self.worker_thread.is_alive():
                self.gui.root.after(50, lambda: self._poll_progress(callback))  # 50ms 更流畅
            elif self.result_queue.empty():
                # 线程结束但没有结果
                error_logger.log_error("加载异常", "加载线程异常终止，未返回任何结果")
                callback('error', '加载线程异常终止', None)
        except Exception as e:
            error_logger.log_error("轮询异常", str(e), exception=e)
            callback('error', f"进度轮询异常: {e}", None)
    
    def cancel(self):
        """取消加载操作"""
        self.cancel_event.set()
        print_log("用户取消了加载操作", "CANCEL")


def load_and_clean_sheet(file_path, sheet_name, progress_callback=None):
    """加载并清洗单个工作表数据"""
    try:
        warnings.filterwarnings("ignore", category=UserWarning)
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        df.columns = df.columns.str.strip()
        df['月份标签'] = sheet_name  # 添加月份标识
        return df
    except Exception as e:
        error_logger.log_error(
            "工作表读取失败",
            f"无法读取工作表 [{sheet_name}]: {e}",
            exception=e,
            suggestion="检查工作表名称是否正确，或尝试用Excel打开查看"
        )
        return None
