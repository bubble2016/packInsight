# -*- coding: utf-8 -*-
"""
磁盘持久化缓存系统
"""
import os
import time
import hashlib
import pickle
import json

from config import CACHE_MAX_AGE_DAYS
from .logger import print_log


class DataCache:
    """数据缓存管理器 - 磁盘持久化，避免重复计算"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cache()
        return cls._instance
    
    def _init_cache(self):
        """初始化缓存目录和索引"""
        # 缓存目录放在用户文档目录下
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.packing_station_cache')
        self.index_file = os.path.join(self.cache_dir, 'cache_index.json')
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # 加载缓存索引
        self.index = self._load_index()
        
        # 自动清理过期缓存
        self._cleanup_old_cache()
    
    def _load_index(self):
        """加载缓存索引"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_index(self):
        """保存缓存索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"\033[1;33m[CACHE] 无法保存缓存索引: {e}\033[0m")
    
    def _cleanup_old_cache(self, max_age_days=None):
        """清理超过指定天数的旧缓存"""
        if max_age_days is None:
            max_age_days = CACHE_MAX_AGE_DAYS
        
        now = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        keys_to_remove = []
        
        for key, info in self.index.items():
            cache_time = info.get('created', 0)
            if now - cache_time > max_age_seconds:
                keys_to_remove.append(key)
                cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
                if os.path.exists(cache_file):
                    try:
                        os.remove(cache_file)
                    except Exception:
                        pass
        
        for key in keys_to_remove:
            del self.index[key]
        
        if keys_to_remove:
            self._save_index()
            print_log(f"已清理 {len(keys_to_remove)} 个过期缓存", "CACHE")
    
    def _get_cache_key(self, file_path, sheet_names):
        """生成缓存键：基于文件路径 + 修改时间 + 选中的工作表"""
        try:
            mtime = os.path.getmtime(file_path)
            key_str = f"{file_path}:{mtime}:{','.join(sorted(sheet_names))}"
            return hashlib.md5(key_str.encode()).hexdigest()
        except Exception:
            return None
    
    def get(self, file_path, sheet_names, key_name):
        """获取缓存数据"""
        cache_key = self._get_cache_key(file_path, sheet_names)
        if not cache_key:
            return None
        
        full_key = f"{cache_key}_{key_name}"
        
        # 检查索引中是否存在
        if full_key not in self.index:
            return None
        
        # 检查文件修改时间是否匹配
        cached_mtime = self.index[full_key].get('file_mtime', 0)
        try:
            current_mtime = os.path.getmtime(file_path)
            if abs(cached_mtime - current_mtime) > 1:  # 允许1秒误差
                return None
        except Exception:
            return None
        
        # 读取缓存文件
        cache_file = os.path.join(self.cache_dir, f"{full_key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return None
        return None
    
    def set(self, file_path, sheet_names, key_name, value):
        """设置缓存数据（持久化到磁盘）"""
        cache_key = self._get_cache_key(file_path, sheet_names)
        if not cache_key:
            return
        
        full_key = f"{cache_key}_{key_name}"
        cache_file = os.path.join(self.cache_dir, f"{full_key}.pkl")
        
        try:
            # 写入缓存文件
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
            
            # 更新索引
            self.index[full_key] = {
                'created': time.time(),
                'file_path': file_path,
                'file_mtime': os.path.getmtime(file_path),
                'sheets': sheet_names,
                'key_name': key_name
            }
            self._save_index()
            print_log(f"💾 已缓存: {key_name}", "CACHE")
        except Exception as e:
            print(f"\033[1;33m[CACHE] 缓存写入失败: {e}\033[0m")
    
    def is_valid(self, file_path, sheet_names):
        """检查缓存是否有效（文件未被修改）"""
        return self.get(file_path, sheet_names, 'df') is not None


# 初始化全局缓存管理器
data_cache = DataCache()
