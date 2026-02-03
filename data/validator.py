# -*- coding: utf-8 -*-
"""
数据验证模块 - 数据质量检测与报告
"""
import numpy as np
from datetime import datetime
from core.logger import print_log


class DataValidator:
    """数据验证器 - 检测缺失值、异常值、重复记录"""
    
    def __init__(self, df):
        """初始化验证器
        
        Args:
            df: 待验证的 DataFrame
        """
        self.df = df
        self.issues = []  # 存储发现的问题
        self.stats = {}   # 存储统计信息
    
    def run_all_checks(self):
        """运行所有检查"""
        print_log("🔍 开始数据质量检查...", "VALID")
        
        self._check_missing_values()
        self._check_duplicates()
        self._check_outliers()
        self._check_data_types()
        self._check_logical_errors()
        
        self._generate_summary()
        return self.get_report()
    
    def _check_missing_values(self):
        """检查缺失值"""
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df) * 100).round(2)
        
        # 关键列缺失检查
        critical_cols = ['类别', '发往地', '重量（吨）', '卖出价', '扣点']
        
        for col in critical_cols:
            if col in self.df.columns:
                missing_count = missing.get(col, 0)
                if missing_count > 0:
                    self.issues.append({
                        'type': 'missing',
                        'severity': 'high' if missing_pct[col] > 10 else 'medium',
                        'column': col,
                        'count': int(missing_count),
                        'percentage': float(missing_pct[col]),
                        'message': f"关键列「{col}」有 {missing_count} 条缺失 ({missing_pct[col]:.1f}%)"
                    })
        
        # 非关键列缺失统计
        for col in self.df.columns:
            if col not in critical_cols and missing.get(col, 0) > 0:
                self.stats[f'missing_{col}'] = {
                    'count': int(missing[col]),
                    'percentage': float(missing_pct[col])
                }
        
        total_missing = missing.sum()
        if total_missing == 0:
            print_log("✅ 缺失值检查通过：无缺失数据", "VALID")
        else:
            print_log(f"⚠️ 发现 {total_missing} 处缺失值", "WARN")
    
    def _check_duplicates(self):
        """检查重复记录"""
        # 完全重复
        full_duplicates = self.df.duplicated().sum()
        
        # 关键字段重复（同一天、同一车、同一目的地）
        key_cols = ['中文日期', '车牌号', '发往地', '类别']
        available_keys = [c for c in key_cols if c in self.df.columns]
        
        if len(available_keys) >= 3:
            key_duplicates = self.df.duplicated(subset=available_keys, keep=False).sum()
        else:
            key_duplicates = 0
        
        self.stats['full_duplicates'] = int(full_duplicates)
        self.stats['key_duplicates'] = int(key_duplicates)
        
        if full_duplicates > 0:
            self.issues.append({
                'type': 'duplicate',
                'severity': 'medium',
                'count': int(full_duplicates),
                'message': f"发现 {full_duplicates} 条完全重复记录"
            })
            print_log(f"⚠️ 发现 {full_duplicates} 条重复记录", "WARN")
        else:
            print_log("✅ 重复检查通过：无完全重复记录", "VALID")
        
        if key_duplicates > 0 and key_duplicates != full_duplicates:
            self.issues.append({
                'type': 'duplicate',
                'severity': 'low',
                'count': int(key_duplicates),
                'message': f"发现 {key_duplicates} 条疑似重复（同日期、车牌、目的地、品类）"
            })
    
    def _check_outliers(self):
        """检查异常值（使用 IQR 方法）"""
        numeric_cols = ['重量（吨）', '卖出价', '运费', '预估利润', '吨利润']
        
        for col in numeric_cols:
            if col not in self.df.columns:
                continue
            
            data = self.df[col].dropna()
            if len(data) < 10:  # 数据太少不检测
                continue
            
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            outlier_count = len(outliers)
            
            if outlier_count > 0:
                self.stats[f'outliers_{col}'] = {
                    'count': outlier_count,
                    'min': float(outliers.min()),
                    'max': float(outliers.max()),
                    'normal_range': (float(lower_bound), float(upper_bound))
                }
                
                # 严重异常：超出正常范围3倍
                extreme_outliers = data[(data < Q1 - 3 * IQR) | (data > Q3 + 3 * IQR)]
                
                if len(extreme_outliers) > 0:
                    self.issues.append({
                        'type': 'outlier',
                        'severity': 'high',
                        'column': col,
                        'count': len(extreme_outliers),
                        'message': f"「{col}」有 {len(extreme_outliers)} 个极端异常值"
                    })
                elif outlier_count > len(data) * 0.05:  # 超过5%
                    self.issues.append({
                        'type': 'outlier',
                        'severity': 'medium',
                        'column': col,
                        'count': outlier_count,
                        'message': f"「{col}」有 {outlier_count} 个异常值 ({outlier_count/len(data)*100:.1f}%)"
                    })
        
        print_log("✅ 异常值检查完成", "VALID")
    
    def _check_data_types(self):
        """检查数据类型一致性"""
        # 检查数值列是否包含非数值
        numeric_cols = ['重量（吨）', '卖出价', '运费', '扣点']
        
        for col in numeric_cols:
            if col in self.df.columns:
                non_numeric = self.df[col].apply(lambda x: not isinstance(x, (int, float, np.number)) and x == x)
                non_numeric_count = non_numeric.sum()
                
                if non_numeric_count > 0:
                    self.issues.append({
                        'type': 'type_error',
                        'severity': 'medium',
                        'column': col,
                        'count': int(non_numeric_count),
                        'message': f"「{col}」有 {non_numeric_count} 个非数值数据"
                    })
    
    def _check_logical_errors(self):
        """检查逻辑错误"""
        # 1. 负重量
        if '重量（吨）' in self.df.columns:
            negative_weight = (self.df['重量（吨）'] < 0).sum()
            if negative_weight > 0:
                self.issues.append({
                    'type': 'logical',
                    'severity': 'high',
                    'column': '重量（吨）',
                    'count': int(negative_weight),
                    'message': f"发现 {negative_weight} 条负重量记录"
                })
        
        # 2. 零重量
        if '重量（吨）' in self.df.columns:
            zero_weight = (self.df['重量（吨）'] == 0).sum()
            if zero_weight > 0:
                self.issues.append({
                    'type': 'logical',
                    'severity': 'low',
                    'column': '重量（吨）',
                    'count': int(zero_weight),
                    'message': f"发现 {zero_weight} 条零重量记录"
                })
        
        # 3. 卖出价为0但有运费（可能漏填）
        if '卖出价' in self.df.columns and '运费' in self.df.columns:
            suspicious = ((self.df['卖出价'] == 0) | self.df['卖出价'].isna()) & (self.df['运费'] > 0)
            suspicious_count = suspicious.sum()
            if suspicious_count > 0:
                self.issues.append({
                    'type': 'logical',
                    'severity': 'medium',
                    'count': int(suspicious_count),
                    'message': f"发现 {suspicious_count} 条可能漏填卖出价（有运费但无卖出价）"
                })
    
    def _generate_summary(self):
        """生成摘要统计"""
        self.stats['total_records'] = len(self.df)
        self.stats['total_issues'] = len(self.issues)
        self.stats['high_severity'] = len([i for i in self.issues if i.get('severity') == 'high'])
        self.stats['medium_severity'] = len([i for i in self.issues if i.get('severity') == 'medium'])
        self.stats['low_severity'] = len([i for i in self.issues if i.get('severity') == 'low'])
        
        if self.stats['high_severity'] > 0:
            print_log(f"🔴 发现 {self.stats['high_severity']} 个高优先级问题!", "WARN")
        if self.stats['total_issues'] == 0:
            print_log("✅ 数据质量检查通过，未发现问题", "VALID")
    
    def get_report(self):
        """获取检查报告"""
        return {
            'stats': self.stats,
            'issues': self.issues,
            'is_healthy': self.stats.get('high_severity', 0) == 0
        }
    
    def get_quality_score(self):
        """计算数据质量评分 (0-100)"""
        base_score = 100
        
        # 高严重性问题扣10分
        base_score -= self.stats.get('high_severity', 0) * 10
        # 中等严重性扣5分
        base_score -= self.stats.get('medium_severity', 0) * 5
        # 低严重性扣2分
        base_score -= self.stats.get('low_severity', 0) * 2
        
        return max(0, min(100, base_score))
    
    def generate_html_report(self):
        """生成 HTML 格式的数据质量报告"""
        score = self.get_quality_score()
        score_color = "#00FF99" if score >= 80 else "#FFFF33" if score >= 60 else "#FF3333"
        
        html = f'''
        <div class="data-quality-card" style="margin-top:20px; padding:20px; background:linear-gradient(135deg, #1a1a2e, #16213e); border-radius:12px; border:1px solid #333;">
            <h3 style="color:#00CCFF; margin:0 0 15px 0;">📊 数据质量报告</h3>
            
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-bottom:20px;">
                <div style="text-align:center; padding:15px; background:rgba(255,255,255,0.05); border-radius:8px;">
                    <div style="font-size:28px; font-weight:bold; color:{score_color};">{score}</div>
                    <div style="color:#888; font-size:12px;">质量评分</div>
                </div>
                <div style="text-align:center; padding:15px; background:rgba(255,255,255,0.05); border-radius:8px;">
                    <div style="font-size:28px; font-weight:bold; color:#00FF99;">{self.stats.get('total_records', 0)}</div>
                    <div style="color:#888; font-size:12px;">总记录数</div>
                </div>
                <div style="text-align:center; padding:15px; background:rgba(255,255,255,0.05); border-radius:8px;">
                    <div style="font-size:28px; font-weight:bold; color:#FF3333;">{self.stats.get('high_severity', 0)}</div>
                    <div style="color:#888; font-size:12px;">严重问题</div>
                </div>
                <div style="text-align:center; padding:15px; background:rgba(255,255,255,0.05); border-radius:8px;">
                    <div style="font-size:28px; font-weight:bold; color:#FFFF33;">{self.stats.get('medium_severity', 0) + self.stats.get('low_severity', 0)}</div>
                    <div style="color:#888; font-size:12px;">一般问题</div>
                </div>
            </div>
        '''
        
        if self.issues:
            html += '<div style="margin-top:15px;"><h4 style="color:#FF00CC; margin:0 0 10px 0;">⚠️ 发现的问题</h4><ul style="margin:0; padding-left:20px; color:#ddd; line-height:1.8;">'
            for issue in self.issues[:10]:  # 最多显示10条
                severity_icon = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
                html += f'<li>{severity_icon} {issue["message"]}</li>'
            if len(self.issues) > 10:
                html += f'<li style="color:#888;">... 还有 {len(self.issues) - 10} 个问题</li>'
            html += '</ul></div>'
        else:
            html += '<div style="margin-top:15px; padding:15px; background:rgba(0,255,153,0.1); border-radius:8px; color:#00FF99;">✅ 数据质量良好，未发现问题！</div>'
        
        html += '</div>'
        return html


def validate_dataframe(df):
    """便捷函数：验证 DataFrame 并返回报告"""
    validator = DataValidator(df)
    return validator.run_all_checks()
