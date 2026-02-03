# -*- coding: utf-8 -*-
"""
性能监控模块 - 各阶段耗时统计
"""
import time
from datetime import datetime
from core.logger import print_log


class PerformanceMonitor:
    """性能监控器 - 追踪各阶段执行时间"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_monitor()
        return cls._instance
    
    def _init_monitor(self):
        """初始化监控器"""
        self.stages = {}  # 存储各阶段时间信息
        self.current_stage = None
        self.start_time = None  # 程序总开始时间
        self.stage_order = []  # 阶段执行顺序
    
    def start(self):
        """开始总计时"""
        self.start_time = time.time()
        self.stages = {}
        self.stage_order = []
        print_log("⏱️ 性能监控已启动", "PERF")
    
    def begin_stage(self, stage_name, description=None):
        """开始一个阶段计时
        
        Args:
            stage_name: 阶段名称（唯一标识）
            description: 阶段描述（可选）
        """
        now = time.time()
        
        # 结束上一个阶段
        if self.current_stage and self.current_stage in self.stages:
            self.stages[self.current_stage]['end_time'] = now
            self.stages[self.current_stage]['duration'] = now - self.stages[self.current_stage]['start_time']
        
        # 开始新阶段
        self.current_stage = stage_name
        self.stages[stage_name] = {
            'start_time': now,
            'end_time': None,
            'duration': None,
            'description': description or stage_name
        }
        self.stage_order.append(stage_name)
    
    def end_stage(self, stage_name=None):
        """结束一个阶段计时
        
        Args:
            stage_name: 阶段名称，默认为当前阶段
        """
        stage = stage_name or self.current_stage
        if stage and stage in self.stages:
            now = time.time()
            self.stages[stage]['end_time'] = now
            self.stages[stage]['duration'] = now - self.stages[stage]['start_time']
            
            duration = self.stages[stage]['duration']
            desc = self.stages[stage]['description']
            print_log(f"⏱️ [{desc}] 耗时: {self._format_duration(duration)}", "PERF")
    
    def _format_duration(self, seconds):
        """格式化时长显示"""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}秒"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}分{secs:.1f}秒"
    
    def get_total_time(self):
        """获取总耗时"""
        if self.start_time:
            return time.time() - self.start_time
        return 0
    
    def get_stage_stats(self):
        """获取各阶段统计信息"""
        stats = []
        for stage_name in self.stage_order:
            stage = self.stages.get(stage_name, {})
            if stage.get('duration') is not None:
                stats.append({
                    'name': stage_name,
                    'description': stage.get('description', stage_name),
                    'duration': stage['duration'],
                    'duration_formatted': self._format_duration(stage['duration'])
                })
        return stats
    
    def generate_report(self):
        """生成性能报告"""
        total = self.get_total_time()
        stats = self.get_stage_stats()
        
        report_lines = [
            "",
            "=" * 60,
            "  ⏱️ 性能统计报告",
            "=" * 60,
        ]
        
        if stats:
            # 计算最长描述长度用于对齐
            max_desc = max(len(s['description']) for s in stats)
            
            for stat in stats:
                desc = stat['description'].ljust(max_desc)
                duration = stat['duration_formatted'].rjust(10)
                # 计算占比
                pct = (stat['duration'] / total * 100) if total > 0 else 0
                bar_len = int(pct / 5)  # 每5%一个块
                bar = "█" * bar_len + "░" * (20 - bar_len)
                
                report_lines.append(f"  {desc}  {duration}  [{bar}] {pct:5.1f}%")
        
        report_lines.append("-" * 60)
        report_lines.append(f"  {'总耗时'.ljust(max_desc if stats else 10)}  {self._format_duration(total).rjust(10)}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        return "\n".join(report_lines)
    
    def print_report(self):
        """打印性能报告"""
        print(self.generate_report())
    
    def get_summary_html(self):
        """生成 HTML 格式的性能摘要（用于报告）"""
        total = self.get_total_time()
        stats = self.get_stage_stats()
        
        html = '<div class="perf-summary" style="margin-top:20px; padding:15px; background:rgba(0,255,153,0.1); border-radius:8px;">'
        html += '<h4 style="color:#00FF99; margin:0 0 10px 0;">⏱️ 处理性能统计</h4>'
        html += f'<p style="color:#888; margin:0;">总耗时: <strong style="color:#00CCFF;">{self._format_duration(total)}</strong></p>'
        
        if stats:
            html += '<div style="margin-top:10px; font-size:12px;">'
            for stat in stats:
                pct = (stat['duration'] / total * 100) if total > 0 else 0
                html += f'<div style="margin:3px 0; color:#aaa;">'
                html += f'{stat["description"]}: {stat["duration_formatted"]} ({pct:.1f}%)'
                html += '</div>'
            html += '</div>'
        
        html += '</div>'
        return html


# 全局性能监控器实例
perf_monitor = PerformanceMonitor()
