# -*- coding: utf-8 -*-
"""
成本与亏损预警分析模块
"""
import numpy as np

from core.logger import print_log


def create_cost_analysis(df):
    """创建成本分析数据
    
    Args:
        df: 清洗后的 DataFrame
    
    Returns:
        dict: 包含各类成本分析结果的字典
    """
    # 1. 运费成本占比分析
    total_revenue = df['预估利润'].sum() + df['运费'].sum()  # 简化：利润+运费≈收入
    total_freight = df['运费'].sum()
    freight_ratio = (total_freight / total_revenue * 100) if total_revenue > 0 else 0
    
    # 按目的地计算运费占比
    dest_cost = df.groupby('发往地').agg({
        '运费': 'sum',
        '预估利润': 'sum',
        '重量（吨）': 'sum'
    }).round(2)
    dest_cost['运费占比'] = np.where(
        (dest_cost['运费'] + dest_cost['预估利润']) > 0,
        dest_cost['运费'] / (dest_cost['运费'] + dest_cost['预估利润']) * 100,
        0
    ).round(1)
    dest_cost['利润率'] = np.where(
        dest_cost['运费'] > 0,
        dest_cost['预估利润'] / dest_cost['运费'] * 100,
        0
    ).round(1)
    dest_cost = dest_cost.sort_values('利润率', ascending=False)
    
    # 2. 亏损预警分析
    # A. 品类亏损
    category_profit = df.groupby('类别').agg({
        '吨利润': 'mean',
        '预估利润': 'sum',
        '重量（吨）': 'sum'
    }).round(2)
    loss_categories = category_profit[category_profit['吨利润'] < 0].sort_values('吨利润')
    
    # B. 路线亏损（品类+目的地组合）
    route_profit = df.groupby(['类别', '发往地']).agg({
        '吨利润': 'mean',
        '预估利润': 'sum',
        '重量（吨）': 'sum',
        '中文日期': 'count'
    }).round(2)
    route_profit.columns = ['平均吨利润', '总利润', '总重量', '车次']
    # 筛选亏损路线（吨利润<0且有一定发货量）
    loss_routes = route_profit[
        (route_profit['平均吨利润'] < 0) & 
        (route_profit['总重量'] > 1)  # 至少发了1吨
    ].sort_values('平均吨利润')
    
    # 3. 低利润预警（吨利润低于平均值50%的）
    avg_profit = df['吨利润'].mean()
    low_threshold = avg_profit * 0.5
    low_profit_routes = route_profit[
        (route_profit['平均吨利润'] > 0) & 
        (route_profit['平均吨利润'] < low_threshold) &
        (route_profit['总重量'] > 1)
    ].sort_values('平均吨利润')
    
    cost_summary = {
        'total_freight_ratio': freight_ratio,
        'dest_cost': dest_cost,
        'loss_categories': loss_categories,
        'loss_routes': loss_routes,
        'low_profit_routes': low_profit_routes,
        'avg_profit': avg_profit,
        'low_threshold': low_threshold
    }
    
    print_log(f"💰 成本分析完成: 运费占比 {freight_ratio:.1f}%", "COST")
    if len(loss_categories) > 0:
        print_log(f"⚠️ 发现 {len(loss_categories)} 个亏损品类!", "WARN")
    if len(loss_routes) > 0:
        print_log(f"⚠️ 发现 {len(loss_routes)} 条亏损路线!", "WARN")
    
    return cost_summary
