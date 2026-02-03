# -*- coding: utf-8 -*-
"""
多月份对比分析模块
"""
from core.logger import print_log


def create_monthly_comparison(df, is_compare_mode):
    """创建月度对比分析数据
    
    Args:
        df: 清洗后的 DataFrame
        is_compare_mode: 是否为多月份对比模式
    
    Returns:
        tuple: (monthly_summary, monthly_category, monthly_dest) 或 (None, None, None)
    """
    if not is_compare_mode or '月份标签' not in df.columns:
        return None, None, None
    
    # 按月份汇总
    monthly_summary = df.groupby('月份标签').agg({
        '重量（吨）': 'sum',
        '预估利润': 'sum',
        '运费': 'sum',
        '吨利润': 'mean',
        '中文日期': 'count'
    }).round(2)
    monthly_summary.columns = ['总重量', '总利润', '总运费', '平均吨利润', '车次']
    
    # 计算环比增长率
    monthly_summary = monthly_summary.sort_index()
    monthly_summary['重量环比'] = monthly_summary['总重量'].pct_change() * 100
    monthly_summary['利润环比'] = monthly_summary['总利润'].pct_change() * 100
    monthly_summary['车次环比'] = monthly_summary['车次'].pct_change() * 100
    monthly_summary = monthly_summary.fillna(0).round(2)
    
    # 按月份+品类汇总（用于品类对比）
    monthly_category = df.groupby(['月份标签', '类别']).agg({
        '重量（吨）': 'sum',
        '预估利润': 'sum'
    }).round(2).reset_index()
    
    # 按月份+目的地汇总
    monthly_dest = df.groupby(['月份标签', '发往地']).agg({
        '重量（吨）': 'sum',
        '预估利润': 'sum',
        '运费': 'sum'
    }).round(2).reset_index()
    
    print_log(f"📊 月度对比分析完成: {len(monthly_summary)} 个月份", "COMPARE")
    return monthly_summary, monthly_category, monthly_dest
