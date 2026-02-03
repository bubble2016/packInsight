# -*- coding: utf-8 -*-
"""
核心图表生成逻辑
"""
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats

from core.logger import print_log
from .layout import (
    NEON_COLORS, WEEK_ORDER, 
    get_subplot_specs, get_subplot_titles, update_figure_layout
)


def create_dashboard_figure(df, kpi_data, cost_analysis, weekly_summary):
    """创建完整的仪表板图表
    
    Args:
        df: 清洗后的 DataFrame
        kpi_data: KPI指标数据列表
        cost_analysis: 成本分析结果字典
        weekly_summary: 周度汇总数据
    
    Returns:
        plotly.graph_objects.Figure: 完整的Plotly图形对象
    """
    # 创建子图布局
    fig = make_subplots(
        rows=5, cols=2,
        specs=get_subplot_specs(),
        subplot_titles=get_subplot_titles(),
        vertical_spacing=0.12,
        row_heights=[0.10, 0.20, 0.20, 0.25, 0.25]
    )
    
    # 1. 添加 KPI 指标
    add_kpi_indicators(fig, kpi_data)
    
    # 2. 添加 Sankey 图 (Row 2, Col 1)
    add_sankey_diagram(fig, df)
    
    # 3. 添加每日趋势图 (Row 2, Col 2)
    add_daily_trend_chart(fig, df)
    
    # 4. 添加 Sunburst/饼图 (Row 3, Col 1)
    add_sunburst_chart(fig, df)
    
    # 5. 添加车辆排名 (Row 3, Col 2)
    add_vehicle_ranking(fig, df)
    
    # 6. 添加品类利润图 (Row 4, Col 1)
    add_category_profit_chart(fig, df)
    
    # 7. 添加气泡图 (Row 4, Col 2)
    add_bubble_chart(fig, df)
    
    # 8. 添加热力图 (Row 5, Col 1)
    add_heatmap(fig, df)
    
    # 9. 添加周度雷达图 (Row 5, Col 2)
    week_stats_max = add_week_radar(fig, df)
    
    # 更新整体布局
    update_figure_layout(fig, week_stats_max)
    
    return fig


def add_kpi_indicators(fig, kpi_data):
    """添加 KPI 指标卡"""
    for i, kpi in enumerate(kpi_data):
        x_pos = 0.05 + i * 0.19
        
        # 获取数值格式化参数（默认不格式化）
        value_format = kpi.get('valueformat', '')
        
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=kpi["value"],
            delta={'reference': kpi["value"] * 0.9, 'relative': False, 'increasing': {'color': kpi["color"]}},
            title={"text": kpi["title"], "font": {"size": 16, "color": "silver"}},
            number={'prefix': kpi.get('prefix', ''), 'suffix': kpi.get('suffix', ''), 
                    'font': {'size': 36, 'color': kpi["color"]},
                    'valueformat': value_format},
            domain={'x': [x_pos, x_pos + 0.17], 'y': [0.85, 1]}
        ))


def add_sankey_diagram(fig, df):
    """添加桑基图：货物流向脉络"""
    try:
        cats = df['类别'].unique()
        dests = df['发往地'].unique()
        labels = list(cats) + list(dests)
        label_map = {label: i for i, label in enumerate(labels)}
        sankey_data = df.groupby(['类别', '发往地'])['重量（吨）'].sum().reset_index()
        
        current_colors = (NEON_COLORS * (len(labels) // len(NEON_COLORS) + 1))[:len(labels)]
        
        fig.add_trace(go.Sankey(
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), 
                     label=labels, color=current_colors),
            link=dict(source=sankey_data['类别'].map(label_map), 
                     target=sankey_data['发往地'].map(label_map), 
                     value=sankey_data['重量（吨）'],
                     color='rgba(0, 204, 255, 0.4)') 
        ), row=2, col=1)
    except Exception as e:
        print_log(f"桑基图生成失败: {e}", "WARN")


def add_daily_trend_chart(fig, df):
    """添加每日发货趋势 & AI预测"""
    daily_trend = df.groupby(['Date', '中文日期'])['重量（吨）'].sum().reset_index().sort_values('Date')
    
    if daily_trend.empty:
        return

    daily_trend['运输次数'] = df.groupby(['Date', '中文日期']).size().values
    
    # 实际趋势线
    fig.add_trace(go.Scatter(
        x=daily_trend['中文日期'], y=daily_trend['重量（吨）'],
        mode='lines+markers', name='每日发货量',
        line=dict(color='#00CCFF', width=3, shape='spline'),
        marker=dict(size=8, color='#FFFFFF', symbol='diamond'),
        text=daily_trend['重量（吨）'].round(1), 
        hovertemplate='日期: %{x}<br>发货量: %{y:.2f}吨<br>运输车次: %{customdata}车<extra></extra>',
        customdata=daily_trend['运输次数'], fill='tozeroy', fillcolor='rgba(0, 204, 255, 0.1)'
    ), row=2, col=2)
    
    # AI 预测线
    if len(daily_trend) > 1:
        x_numeric = np.arange(len(daily_trend))
        slope, intercept, _, _, _ = stats.linregress(x_numeric, daily_trend['重量（吨）'])
        trend_line = slope * x_numeric + intercept
        trend_text = "📈 趋势向上" if slope > 0 else "📉 趋势向下"
        
        fig.add_trace(go.Scatter(
            x=daily_trend['中文日期'], y=trend_line,
            mode='lines', name=f'智能趋势 ({trend_text})',
            line=dict(color='#FFFF33', width=2, dash='dash'),
            hoverinfo='skip'
        ), row=2, col=2)


def add_sunburst_chart(fig, df):
    """添加各品种发货流向 (Sunburst 或 Pie)"""
    try:
        sb_fig = px.sunburst(df, path=['类别', '发往地'], values='重量（吨）', color='类别', color_discrete_sequence=NEON_COLORS)
        sb_trace = sb_fig.data[0]
        sb_trace.textinfo = 'label+percent entry'
        sb_trace.hovertemplate = '<b>%{label}</b><br>重量: %{value:.2f}吨<br>占比: %{percentEntry:.1%}<extra></extra>'
        sb_trace.marker.line.width = 1
        sb_trace.marker.line.color = 'white'
        fig.add_trace(sb_trace, row=3, col=1)
    except Exception:
        # 降级为饼图
        cat_sum = df.groupby('类别')['重量（吨）'].sum().reset_index()
        fig.add_trace(go.Pie(
            labels=cat_sum['类别'], values=cat_sum['重量（吨）'], hole=0.5,
            marker=dict(colors=NEON_COLORS, line=dict(color='white', width=2)),
            textinfo='label+percent',
            hovertemplate='类别: %{label}<br>重量: %{value:.2f}吨<br>占比: %{percent}<extra></extra>'
        ), row=3, col=1)


def add_vehicle_ranking(fig, df):
    """添加运输车辆 Top 8"""
    vehicle_stats = df.groupby('车牌号').agg({
        '重量（吨）': 'sum',
        '中文日期': 'count'
    }).rename(columns={'中文日期': '运输次数'})
    
    max_weight = vehicle_stats['重量（吨）'].max()
    max_count = vehicle_stats['运输次数'].max()
    if max_weight == 0: max_weight = 1
    if max_count == 0: max_count = 1
    
    vehicle_stats['综合评分'] = (vehicle_stats['重量（吨）'] / max_weight * 0.7 + 
                              vehicle_stats['运输次数'] / max_count * 0.3) * 100
    top_vehicles = vehicle_stats.sort_values('综合评分', ascending=False).head(8)
    
    fig.add_trace(go.Bar(
        y=top_vehicles.index, x=top_vehicles['重量（吨）'], orientation='h',
        marker=dict(color=top_vehicles['综合评分'], colorscale='Viridis', line=dict(color='white', width=1)),
        name='车辆运输量',
        text=[f"{w:.1f}吨 ({c}车)" for w, c in zip(top_vehicles['重量（吨）'], top_vehicles['运输次数'])],
        textposition='auto',
        hovertemplate='车牌: %{y}<br>总重量: %{x:.1f}吨<br>运输车次: %{customdata}车<extra></extra>',
        customdata=top_vehicles['运输次数']
    ), row=3, col=2)


def add_category_profit_chart(fig, df):
    """添加各品种吨利润"""
    profit_rank = df.groupby('类别')['吨利润'].agg(['mean', 'std']).reset_index().sort_values('mean')
    fig.add_trace(go.Bar(
        y=profit_rank['类别'], x=profit_rank['mean'], orientation='h',
        error_x=dict(type='data', array=profit_rank['std'], visible=True),
        marker=dict(color=profit_rank['mean'], colorscale='RdYlGn', line=dict(color='white', width=1)),
        name='每吨利润', text=profit_rank['mean'].round(1), textposition='outside',
        hovertemplate='类别: %{y}<br>平均利润: %{x:.2f}元/吨<extra></extra>'
    ), row=4, col=1)


def add_bubble_chart(fig, df):
    """添加气泡图: 利润与运费分布"""
    max_weight_val = df['重量（吨）'].max() if not df.empty else 10
    
    fig.add_trace(go.Scatter(
        x=df['运费单价'], y=df['吨利润'], mode='markers',
        marker=dict(
            size=df['重量（吨）'], 
            sizemode='area', 
            sizeref=2.*max_weight_val/(40.**2),
            color=df['利润率'], colorscale='Rainbow', showscale=True,
            colorbar=dict(title="利润率%", x=1.02, y=0.5, len=0.4), line=dict(width=1, color='White')
        ),
        text=df['车牌号'] + "<br>" + df['中文日期'] + "<br>品类:" + df['类别'],
        hovertemplate='<b>%{text}</b><br>运费单价: %{x:.1f}元<br>吨利润: %{y:.1f}元<extra></extra>',
        name='运输批次'
    ), row=4, col=2)


def add_heatmap(fig, df):
    """添加品类-目的地热力图"""
    heatmap_data = df.pivot_table(values='重量（吨）', index='类别', columns='发往地', aggfunc='sum', fill_value=0).round(1)
    if not heatmap_data.empty:
        fig.add_trace(go.Heatmap(
            z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index,
            colorscale='Viridis', colorbar=dict(title="发货量(吨)", x=1.02, y=0.15, len=0.3),
            text=heatmap_data.values, texttemplate='%{text}',
            hovertemplate='品类: %{y}<br>目的地: %{x}<br>发货量: %{z}吨<extra></extra>'
        ), row=5, col=1)


def add_week_radar(fig, df):
    """添加星期运输效率雷达
    
    Returns:
        float: 周统计数据中的最大值，用于设置雷达图范围
    """
    week_stats = df.groupby('星期')['重量（吨）'].sum().reindex(WEEK_ORDER, fill_value=0)
    fig.add_trace(go.Scatterpolar(
        r=week_stats.values, theta=week_stats.index, fill='toself',
        name='周度发货分布', line_color='#FF00CC', opacity=0.8
    ), row=5, col=2)
    
    return week_stats.max()
