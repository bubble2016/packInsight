# -*- coding: utf-8 -*-
"""
数据清洗与转换逻辑
"""
from datetime import datetime

import numpy as np
import pandas as pd

from config import WEEK_MAP, DATE_COL, REQUIRED_BASE_COLS
from core.logger import print_log


def find_col_name(df_columns, keywords):
    """在列名中模糊查找包含 keyword 的列"""
    for col in df_columns:
        for kw in keywords:
            if kw in col:
                return col
    return None


def convert_to_chinese_date(val):
    """将日期值转换为中文格式 (如 "1月15日")"""
    try:
        if pd.isna(val):
            return pd.NaT, ""
        if isinstance(val, (pd.Timestamp, datetime)):
            dt = val
        elif isinstance(val, (int, float)):
            dt = pd.to_datetime('1899-12-30') + pd.to_timedelta(val, unit='D')
        else:
            dt = pd.to_datetime(val, errors='coerce')
        
        if pd.isna(dt):
            return pd.NaT, ""
        return dt, f"{dt.month}月{dt.day}日"
    except Exception:
        return pd.NaT, ""


def clean_dataframe(df):
    """执行智能数据清洗
    
    Args:
        df: 原始 DataFrame
    
    Returns:
        tuple: (清洗后的 df, 列名信息 dict)
    """
    # 自动去除列名中的空格
    df.columns = df.columns.str.strip()
    print_log("已自动清理表头空格", "CLEAN")
    
    # === 智能列名识别 ===
    col_deduction = find_col_name(df.columns, ['扣点'])
    col_price = find_col_name(df.columns, ['卖出价', '单价'])
    col_weight = find_col_name(df.columns, ['重量']) or '重量（吨）'
    
    print_log(f"智能识别关键列: 扣点->[{col_deduction}], 卖出价->[{col_price}]", "INFO")
    
    col_info = {
        'deduction': col_deduction,
        'price': col_price,
        'weight': col_weight
    }
    
    # === 脏数据终结者逻辑 ===
    rows_before = len(df)
    
    # 1. 转换数值类型 (防止Excel里存成文本)
    numeric_cols = [col for col in [col_deduction, col_price, col_weight, '运费', '预估利润'] if col]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 2. 严格过滤逻辑
    # A. 必须有发货日期
    if DATE_COL in df.columns:
        df = df.dropna(subset=[DATE_COL])
    
    # B. 剔除"扣点"还没出来的 (数据为空)
    if col_deduction and col_deduction in df.columns:
        df = df.dropna(subset=[col_deduction])
    
    # C. 剔除"卖出价"为空 或 价格<=1 (防止0元/1元导致利润计算错误)
    if col_price and col_price in df.columns:
        df = df.dropna(subset=[col_price])
        df = df[df[col_price] > 1]
    
    # D. 剔除基础信息不全的
    required_base = REQUIRED_BASE_COLS + [col_weight]
    existing_base = [c for c in required_base if c in df.columns]
    df = df.dropna(subset=existing_base)
    if col_weight in df.columns:
        df = df[df[col_weight] > 0]
    
    rows_after = len(df)
    dropped_count = rows_before - rows_after
    
    if dropped_count > 0:
        print_log(f"🧹 自动清除了 {dropped_count} 条无效/未结算记录", "CLEAN")
    else:
        print_log("✨ 数据质量完美，无未结算记录", "CLEAN")
    
    # === 日期处理 ===
    if DATE_COL in df.columns:
        date_results = df[DATE_COL].apply(convert_to_chinese_date)
        df['Date'] = [x[0] for x in date_results]
        df['中文日期'] = [x[1] for x in date_results]
        
        # 再次清洗无效日期
        df = df.dropna(subset=['Date'])
        df = df.sort_values('Date')
        
        # 星期分析
        df['星期数字'] = df['Date'].dt.dayofweek
        df['星期'] = df['星期数字'].map(WEEK_MAP)
        df['周'] = df['Date'].dt.isocalendar().week
        df['周标签'] = '第' + df['周'].astype(str) + '周'
    
    # === 财务计算 ===
    # 确保列名统一
    if col_weight != '重量（吨）' and col_weight in df.columns:
        df['重量（吨）'] = df[col_weight]
    
    cols_to_fillna = ['运费', '预估利润']
    for col in cols_to_fillna:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # 处理除以零
    if '重量（吨）' in df.columns and '预估利润' in df.columns:
        df['吨利润'] = np.where(df['重量（吨）'] > 0, df['预估利润'] / df['重量（吨）'], 0)
    
    if '重量（吨）' in df.columns and '运费' in df.columns:
        df['运费单价'] = np.where(df['重量（吨）'] > 0, df['运费'] / df['重量（吨）'], 0)
        df['利润率'] = np.where(df['运费'] > 0, (df['预估利润'] / df['运费']) * 100, 0)
        
        # 异常数据检测 (Z-Score)
        mean_freight = df['运费单价'].mean()
        std_freight = df['运费单价'].std()
        if std_freight == 0:
            std_freight = 1
        df['运费异常'] = df['运费单价'] > (mean_freight + 2 * std_freight)
    
    print_log(f"数据准备就绪，有效记录: {len(df)} 条", "DATA")
    
    return df, col_info
