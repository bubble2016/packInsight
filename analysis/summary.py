# -*- coding: utf-8 -*-
"""
汇总表生成模块
"""
import numpy as np


def create_summary_table(df):
    """创建多维度分析汇总表
    
    Args:
        df: 清洗后的 DataFrame
    
    Returns:
        tuple: (category_summary, destination_summary, weekly_summary, daily_summary)
    """
    # 品类汇总
    category_summary = df.groupby('类别').agg({
        '重量（吨）': ['sum', 'mean', 'std'],
        '预估利润': ['sum', 'mean'],
        '吨利润': 'mean',
        '运费单价': 'mean',
        '利润率': 'mean'
    }).fillna(0).round(2)
    category_summary.columns = ['总重量', '平均重量', '重量标准差', '总利润', '平均利润', '吨利润', '运费单价', '利润率']
    
    # 目的地汇总
    destination_summary = df.groupby('发往地').agg({
        '重量（吨）': 'sum',
        '预估利润': ['sum', 'mean'],
        '吨利润': 'mean',
        '运费单价': 'mean',
        '中文日期': 'count'
    }).fillna(0).round(2)
    destination_summary.columns = ['总重量', '总利润', '平均利润', '平均吨利润', '平均运费单价', '车次']
    
    # 计算吨均运费
    destination_freight = df.groupby('发往地').agg({
        '运费': 'sum',
        '重量（吨）': 'sum'
    })
    destination_freight['吨均运费'] = np.where(
        destination_freight['重量（吨）'] > 0, 
        destination_freight['运费'] / destination_freight['重量（吨）'], 
        0
    )
    destination_summary['吨均运费'] = destination_freight['吨均运费'].round(2)
    
    # 周度汇总
    weekly_summary = df.groupby('周标签').agg({
        '重量（吨）': ['sum', 'mean'],
        '预估利润': ['sum', 'mean'],
        '中文日期': 'count'
    }).fillna(0).round(2)
    weekly_summary.columns = ['总重量', '平均重量', '总利润', '平均利润', '运输次数']
    
    # 日度汇总 (High/Low 分析用)
    daily_summary = df.groupby('中文日期').agg({
        '重量（吨）': 'sum',
        '预估利润': 'sum',
        '车牌号': 'count'
    }).fillna(0).round(2)
    daily_summary.columns = ['总重量', '总利润', '车次']
    
    return category_summary, destination_summary, weekly_summary, daily_summary
