# -*- coding: utf-8 -*-
"""
图表布局与样式配置
"""

# 模板样式
TEMPLATE_STYLE = "plotly_dark"

# 霓虹色彩调色板
NEON_COLORS = [
    '#00FF99', '#FF00CC', '#00CCFF', '#FFFF33',
    '#FF3333', '#CC00FF', '#00FF00', '#FF0099'
]

# 星期顺序
WEEK_ORDER = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


def get_subplot_specs():
    """获取子图规格配置"""
    return [
        [{"type": "domain", "colspan": 2}, None],
        [{"type": "sankey"}, {"type": "xy"}],
        [{"type": "domain"}, {"type": "bar"}],
        [{"type": "bar"}, {"type": "scatter"}],
        [{"type": "heatmap"}, {"type": "polar"}]
    ]


def get_subplot_titles():
    """获取子图标题配置"""
    return (
        "",
        "🚛 货物流向脉络 (桑基图)",
        "📈 每日发货趋势 & AI预测 (线性回归)",
        "🍩 各品种发货流向 (占比分析)",
        "🏆 运输车辆 Top 8 (柱状动画)",
        "💰 各品种吨利润 (增长动画)",
        "💠 利润与运费分布 (气泡动画)",
        "🔥 品类-目的地热力图",
        "📅 星期运输效率雷达 (Weekly Rhythm)"
    )


def update_figure_layout(fig, week_stats_max):
    """更新图表整体布局
    
    Args:
        fig: Plotly Figure 对象
        week_stats_max: 周度统计最大值（用于雷达图范围）
    """
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template=TEMPLATE_STYLE,
        height=2300,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=50, r=100, t=80, b=50),
        hovermode='closest',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, week_stats_max * 1.2]
            )
        )
    )
    
    fig.update_annotations(yshift=30)
    fig.update_xaxes(title_text="", tickangle=-45, row=2, col=2)
    fig.update_yaxes(title_text="累计重量 (吨)", secondary_y=True, row=2, col=2)
