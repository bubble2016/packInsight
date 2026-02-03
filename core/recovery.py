# -*- coding: utf-8 -*-
"""
错误恢复模块 - 自动保存中间结果，防止数据丢失
"""
import os
import json
import pickle
import shutil
from datetime import datetime
from core.logger import print_log, error_logger


class RecoveryManager:
    """恢复管理器 - 自动保存检查点，支持断点恢复"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance
    
    def _init_manager(self):
        """初始化恢复管理器"""
        # 恢复目录放在用户目录下
        self.recovery_dir = os.path.join(os.path.expanduser('~'), '.packing_station_recovery')
        self.checkpoint_file = os.path.join(self.recovery_dir, 'checkpoint.json')
        self.data_file = os.path.join(self.recovery_dir, 'checkpoint_data.pkl')
        
        # 确保目录存在
        if not os.path.exists(self.recovery_dir):
            os.makedirs(self.recovery_dir)
        
        # 会话信息
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.checkpoints = {}  # 存储检查点信息
        self.current_stage = None
    
    def save_checkpoint(self, stage_name, data=None, metadata=None):
        """保存检查点
        
        Args:
            stage_name: 阶段名称（如 'data_loaded', 'analysis_complete'）
            data: 要保存的数据（DataFrame 或其他可序列化对象）
            metadata: 额外的元数据信息
        """
        try:
            checkpoint_info = {
                'session_id': self.session_id,
                'stage': stage_name,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self.checkpoints[stage_name] = checkpoint_info
            self.current_stage = stage_name
            
            # 保存检查点索引
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'latest_checkpoint': checkpoint_info,
                    'all_checkpoints': self.checkpoints
                }, f, ensure_ascii=False, indent=2)
            
            # 如果有数据，保存到单独文件
            if data is not None:
                data_backup = {
                    'stage': stage_name,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
                with open(self.data_file, 'wb') as f:
                    pickle.dump(data_backup, f)
                
                print_log(f"💾 检查点已保存: {stage_name}", "SAVE")
            
            return True
            
        except Exception as e:
            print_log(f"⚠️ 检查点保存失败: {e}", "WARN")
            return False
    
    def has_recovery_data(self):
        """检查是否有可恢复的数据"""
        return os.path.exists(self.checkpoint_file) and os.path.exists(self.data_file)
    
    def get_recovery_info(self):
        """获取恢复信息"""
        if not self.has_recovery_data():
            return None
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            return info.get('latest_checkpoint')
        except Exception:
            return None
    
    def load_recovery_data(self):
        """加载恢复数据
        
        Returns:
            tuple: (stage_name, data, metadata) 或 None
        """
        if not self.has_recovery_data():
            return None
        
        try:
            # 读取检查点信息
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            # 读取数据
            with open(self.data_file, 'rb') as f:
                data_backup = pickle.load(f)
            
            checkpoint = info.get('latest_checkpoint', {})
            
            print_log(f"🔄 已加载恢复数据: {checkpoint.get('stage')}", "RECOVER")
            
            return (
                data_backup.get('stage'),
                data_backup.get('data'),
                checkpoint.get('metadata', {})
            )
            
        except Exception as e:
            print_log(f"⚠️ 恢复数据加载失败: {e}", "WARN")
            return None
    
    def clear_recovery_data(self):
        """清除恢复数据（正常完成后调用）"""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            self.checkpoints = {}
            print_log("🗑️ 恢复数据已清理", "CLEAN")
            return True
        except Exception as e:
            print_log(f"⚠️ 清理恢复数据失败: {e}", "WARN")
            return False
    
    def get_checkpoint_age_hours(self):
        """获取检查点的年龄（小时）"""
        info = self.get_recovery_info()
        if not info:
            return None
        
        try:
            checkpoint_time = datetime.fromisoformat(info['timestamp'])
            age = datetime.now() - checkpoint_time
            return age.total_seconds() / 3600
        except Exception:
            return None
    
    def should_offer_recovery(self):
        """判断是否应该提供恢复选项
        
        Returns:
            bool: 如果有有效的恢复数据（24小时内）则返回 True
        """
        if not self.has_recovery_data():
            return False
        
        age = self.get_checkpoint_age_hours()
        if age is None:
            return False
        
        # 超过24小时的恢复数据不再有效
        return age < 24
    
    def backup_output_files(self, file_paths, backup_name=None):
        """备份输出文件
        
        Args:
            file_paths: 文件路径列表
            backup_name: 备份名称（可选）
        """
        backup_dir = os.path.join(
            self.recovery_dir, 
            'backups', 
            backup_name or datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    dest = os.path.join(backup_dir, os.path.basename(file_path))
                    shutil.copy2(file_path, dest)
            
            print_log(f"📂 文件已备份到: {backup_dir}", "BACKUP")
            return backup_dir
            
        except Exception as e:
            print_log(f"⚠️ 文件备份失败: {e}", "WARN")
            return None


class AutoSaveContext:
    """自动保存上下文管理器 - 用于 with 语句"""
    
    def __init__(self, stage_name, recovery_manager=None):
        self.stage_name = stage_name
        self.manager = recovery_manager or recovery_manager_instance
        self.data = None
    
    def __enter__(self):
        print_log(f"▶️ 开始阶段: {self.stage_name}", "STAGE")
        return self
    
    def set_data(self, data, metadata=None):
        """设置要保存的数据"""
        self.data = data
        self.metadata = metadata
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 发生异常，保存当前数据用于恢复
            if self.data is not None:
                self.manager.save_checkpoint(
                    f"{self.stage_name}_error",
                    self.data,
                    {'error': str(exc_val)}
                )
            error_logger.log_error(
                f"阶段异常: {self.stage_name}",
                str(exc_val),
                exception=exc_val,
                suggestion="程序已保存中间数据，下次启动可恢复"
            )
            return False  # 不抑制异常
        else:
            # 正常完成，保存检查点
            if self.data is not None:
                self.manager.save_checkpoint(
                    self.stage_name,
                    self.data,
                    getattr(self, 'metadata', None)
                )
            print_log(f"✅ 完成阶段: {self.stage_name}", "STAGE")
            return True


# 全局恢复管理器实例
recovery_manager_instance = RecoveryManager()


def offer_recovery_dialog():
    """显示恢复对话框
    
    Returns:
        bool: 用户是否选择恢复
    """
    manager = recovery_manager_instance
    
    if not manager.should_offer_recovery():
        return False
    
    info = manager.get_recovery_info()
    if not info:
        return False
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        timestamp = info.get('timestamp', '未知时间')
        stage = info.get('stage', '未知阶段')
        
        result = messagebox.askyesno(
            "发现未完成的任务",
            f"检测到上次处理未完成：\n\n"
            f"📍 阶段: {stage}\n"
            f"⏰ 时间: {timestamp[:19]}\n\n"
            f"是否恢复上次的数据继续处理？\n"
            f"（选择「否」将重新开始）"
        )
        
        root.destroy()
        return result
        
    except Exception:
        return False
