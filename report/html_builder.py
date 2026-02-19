# -*- coding: utf-8 -*-
"""HTML 报告构建器"""

from .styles import (
    get_base_styles,
    get_button_styles,
    get_card_styles,
    get_table_styles,
    get_animation_styles,
    get_print_styles,
)
from .scripts import (
    get_base_scripts,
    get_particle_animation_js,
    get_counter_animation_js,
    get_stagger_animation_js,
)


def _table_open(headers):
    """构建表格表头片段。"""
    th_html = "".join(f"<th>{header}</th>" for header in headers)
    return f"<table><tr>{th_html}</tr>"


def _metric_bar(value_text, width, bar_class, bg_class=""):
    """构建带进度条的指标片段。"""
    bg_extra = f" {bg_class}" if bg_class else ""
    return (
        '<div class="bar-container">'
        f"<span>{value_text}</span>"
        f'<div class="bar-bg{bg_extra}"><div class="data-bar {bar_class}" data-width="{width}"></div></div>'
        "</div>"
    )


def _render_suggestion_card(title, suggestions):
    """渲染建议卡片。"""
    items_html = "".join(
        f'<li class="suggestion-item">{suggestion}</li>' for suggestion in suggestions
    )
    return f"""
        <div class="card suggestion-card">
            <h3 class="suggestion-title">{title}</h3>
            <ul class="suggestion-list">
                {items_html}
            </ul>
        </div>
    """


def _render_warning_table(title_html, card_class, headers, rows_html):
    """渲染预警表格块。"""
    rows = "".join(rows_html)
    return (
        f"{title_html}"
        f'<div class="card {card_class}">'
        f"{_table_open(headers)}"
        f"{rows}"
        "</table></div>"
    )


def build_analysis_report(
    target_sheet,
    generate_time,
    kpi_data,
    category_summary,
    destination_summary,
    weekly_summary,
    top_vehicles,
    cost_analysis,
    kpi_title_prefix,
    daily_summary=None,
):
    """构建完整 HTML 分析报告。"""
    freight_ratio = cost_analysis["total_freight_ratio"]
    dest_cost = cost_analysis["dest_cost"]
    loss_categories = cost_analysis["loss_categories"]
    loss_routes = cost_analysis["loss_routes"]
    low_profit_routes = cost_analysis["low_profit_routes"]
    avg_profit = cost_analysis["avg_profit"]
    low_threshold = cost_analysis["low_threshold"]

    styles = (
        get_base_styles()
        + get_button_styles()
        + get_card_styles()
        + get_table_styles()
        + get_animation_styles()
        + get_print_styles()
    )

    scripts = (
        get_base_scripts()
        + get_particle_animation_js()
        + get_counter_animation_js()
        + get_stagger_animation_js()
    )

    header_html = build_header_section(target_sheet, generate_time)
    kpi_html = build_kpi_section(kpi_data)
    overview_html = build_overview_section(category_summary, destination_summary)
    daily_html = build_daily_section(daily_summary) if daily_summary is not None else ""
    insight_html = build_insight_section(weekly_summary, top_vehicles)
    cost_html = build_cost_analysis_section(
        freight_ratio, low_threshold, avg_profit, dest_cost
    )
    warning_html = build_warning_section(loss_categories, loss_routes)
    suggestion_html = build_suggestions_section(
        loss_routes,
        low_profit_routes,
        cost_analysis=cost_analysis,
        category_summary=category_summary,
        destination_summary=destination_summary,
        weekly_summary=weekly_summary,
        top_vehicles=top_vehicles,
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_sheet} - 深度运营分析报告</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        {styles}
    </style>
    <script>
        {scripts}
    </script>
</head>
<body>
    <div class="container">
        {header_html}

        <div class="btn-group">
            <button type="button" class="btn btn-print" onclick="printReport()" aria-label="打印 PDF 报告" title="打印 PDF 报告">🖨️ 打印PDF</button>
            <button type="button" class="btn btn-shot" onclick="captureScreenshot()" aria-label="导出长图" title="导出长图">📷 导出长图</button>
            <button type="button" class="btn btn-privacy" id="privacyBtn" onclick="togglePrivacy()" aria-label="切换利润显示" title="切换利润显示">👁️ 隐藏利润</button>
        </div>

        {kpi_html}
        {overview_html}

        {daily_html}

        <h2 class="section-title">🚀 深度洞察</h2>
        {insight_html}

        <h2 class="section-title">💰 成本与利润透视</h2>
        {cost_html}

        {warning_html}
        {suggestion_html}

        <div class="footer">
            <p>POWERED BY 李小泡智能分析系统 v9.0 | 核心算法支持：Pandas + Plotly + Scipy</p>
        </div>
    </div>
</body>
</html>
    """
    return html


def build_header_section(target_sheet, generate_time):
    """构建头部区域 HTML。"""
    return f"""
        <div class="header">
            <h1 class="glitch" data-text="西关打包站深度运营分析报告">📊 西关打包站深度运营分析报告</h1>
            <p>分析对象: {target_sheet} | 生成时间: {generate_time} | 李小泡专属系统</p>
        </div>
    """


def build_kpi_section(kpi_data):
    """构建 KPI 区域 HTML。"""
    kpi_html = '<div class="kpi-container">'
    for kpi in kpi_data:
        title = kpi["title"]
        fmt = kpi.get("valueformat", ".1f")
        value_fmt = (
            f"{kpi['value']:{fmt}}" if isinstance(kpi["value"], float) else f"{kpi['value']}"
        )
        suffix = kpi["suffix"]
        color = kpi["color"]

        sensitive_class = "sensitive-data" if "利润" in title else ""

        kpi_html += f"""
            <div class="kpi-box">
                <div class="kpi-lbl">{title}</div>
                <div class="kpi-val {sensitive_class}" data-color="{color}">{value_fmt}{suffix}</div>
            </div>
        """
    kpi_html += "</div>"
    return kpi_html


def build_daily_section(daily_summary):
    """构建日度峰值分析区域。"""
    if daily_summary.empty:
        return ""

    max_day = daily_summary["总重量"].idxmax()
    min_day = daily_summary["总重量"].idxmin()
    max_val = daily_summary.loc[max_day, "总重量"]
    min_val = daily_summary.loc[min_day, "总重量"]

    max_profit_day = daily_summary["总利润"].idxmax()
    max_profit_val = daily_summary.loc[max_profit_day, "总利润"]

    avg_val = daily_summary["总重量"].mean()

    return f"""
    <h2 class="section-title daily-section-title">📅 每日峰值透视 (High/Low)</h2>
    <div class="card">
        <div class="daily-highlow-row">
             <div class="daily-col daily-col-hot">
                <div class="daily-label">🔥 巅峰爆单日</div>
                <div class="daily-day">{max_day}</div>
                <div class="daily-value">{max_val:.1f} <span class="daily-unit">吨</span></div>
                <div class="daily-note">是平均水平的 {(max_val / avg_val):.1f} 倍</div>
            </div>

             <div class="daily-divider"></div>

             <div class="daily-col daily-col-profit">
                <div class="daily-label">💰 利润最高日</div>
                <div class="daily-day">{max_profit_day}</div>
                <div class="daily-value sensitive-data">{max_profit_val / 10000:.2f} <span class="daily-unit">万</span></div>
                <div class="daily-note">单日利润之王</div>
            </div>

            <div class="daily-divider"></div>

            <div class="daily-col daily-col-cool">
                <div class="daily-label">🧊 运营低谷日</div>
                <div class="daily-day">{min_day}</div>
                <div class="daily-value">{min_val:.1f} <span class="daily-unit">吨</span></div>
                <div class="daily-note">需关注原因</div>
            </div>
        </div>
    </div>
    """


def build_overview_section(category_summary, destination_summary):
    """构建数据总览区域 HTML。"""
    max_cat_weight = category_summary["总重量"].max() if not category_summary.empty else 1
    max_cat_profit = category_summary["总利润"].max() if not category_summary.empty else 1

    max_dest_weight = destination_summary["总重量"].max() if not destination_summary.empty else 1
    max_dest_count = destination_summary["车次"].max() if not destination_summary.empty else 1

    html = """<div class="grid-2">
            <div class="card">
                <h3>🏷️ 品类综合表现</h3>
                """
    html += _table_open(["品类", "总量(吨)", "总利润(万)", "吨利润"])

    for idx, row in category_summary.sort_values("总重量", ascending=False).head(8).iterrows():
        weight = row["总重量"]
        profit = row["总利润"]

        weight_width = (weight / max_cat_weight) * 100
        profit_width = (profit / max_cat_profit) * 100
        if profit_width < 0:
            profit_width = 0

        html += f"""<tr>
            <td>{idx}</td>
            <td>{_metric_bar(f"{weight:.1f}", weight_width, "bar-cat-weight")}</td>
            <td class='sensitive-data'>
                {_metric_bar(f"{(profit / 10000):.3f}", profit_width, "bar-cat-profit", "bar-bg-sm")}
            </td>
            <td class='sensitive-data'>{row['吨利润']:.1f}</td>
        </tr>"""
    html += "</table></div>"

    html += """<div class="card">
                <h3>📍 热门目的地 Top 8</h3>
                """
    html += _table_open(["目的地", "总量(吨)", "车次", "吨均运费"])

    for idx, row in destination_summary.sort_values("总重量", ascending=False).head(8).iterrows():
        weight = row["总重量"]
        count = row["车次"]

        weight_width = (weight / max_dest_weight) * 100
        count_width = (count / max_dest_count) * 100

        html += f"""<tr>
            <td class='sensitive-data'>{idx}</td>
            <td>{_metric_bar(f"{weight:.1f}", weight_width, "bar-dest-weight")}</td>
            <td>{_metric_bar(f"{int(count)}", count_width, "bar-dest-count", "bar-bg-xs")}</td>
            <td>{row['吨均运费']:.1f}</td>
        </tr>"""
    html += "</table></div></div>"

    return html


def build_insight_section(weekly_summary, top_vehicles):
    """构建深度洞察区域 HTML。"""
    max_week_weight = weekly_summary["总重量"].max() if not weekly_summary.empty else 1
    max_vehicle_weight = top_vehicles["重量（吨）"].max() if not top_vehicles.empty else 1

    html = """<div class="grid-2">
            <div class="card">
                <h3>📅 周度趋势雷达</h3>
                """
    html += _table_open(["周次", "总重量(吨)", "总利润(元)", "车次"])

    for idx, row in weekly_summary.iterrows():
        weight = row["总重量"]
        bar_width = (weight / max_week_weight) * 100
        html += f"""<tr>
            <td>{idx}</td>
            <td>{_metric_bar(f"{weight:.1f}", bar_width, "bar-week-weight")}</td>
            <td class='sensitive-data'>{row['总利润']:.0f}</td>
            <td>{int(row['运输次数'])}</td>
        </tr>"""
    html += "</table></div>"

    html += """<div class="card">
                <h3>🚛 荣耀车队榜 (Top 8)</h3>
                """
    html += _table_open(["车牌号", "总重量", "车次", "综合评分"])

    for idx, row in top_vehicles.iterrows():
        score = row["综合评分"]
        badge = '<span class="badge badge-hot">金牌</span>' if score >= 90 else ""
        weight = row["重量（吨）"]
        bar_width = (weight / max_vehicle_weight) * 100

        html += f"""<tr>
            <td>{idx} {badge}</td>
            <td>{_metric_bar(f"{weight:.1f}", bar_width, "bar-vehicle-weight")}</td>
            <td>{int(row['运输次数'])}</td>
            <td>{score:.1f}</td>
        </tr>"""
    html += "</table></div></div>"

    return html


def build_cost_analysis_section(freight_ratio, low_threshold, avg_profit, dest_cost):
    """构建成本分析区域 HTML。"""
    ratio_status_class = (
        "cost-metric-value-good"
        if freight_ratio < 40
        else "cost-metric-value-mid" if freight_ratio < 60 else "cost-metric-value-high"
    )

    html = f"""
        <div class="grid-2 cost-grid">
            <div class="card">
                <h3>💰 吨利润红黑榜</h3>
                <div class="cost-metric-grid">
                    <div class="cost-metric-card cost-metric-card-danger">
                        <strong class="cost-metric-title-danger">总运费占比</strong>
                        <p class="cost-metric-text">
                            <span class="cost-metric-value {ratio_status_class}">{freight_ratio:.1f}%</span><br>
                            <small>占总收入比例</small>
                        </p>
                    </div>
                    <div class="cost-metric-card cost-metric-card-warn">
                        <strong class="cost-metric-title-warn">低利润警戒线</strong>
                        <p class="cost-metric-text">
                            <span class="cost-metric-value cost-metric-title-warn">{low_threshold:.1f}</span> 元<br>
                            = 平均吨利润 × 50%<br>
                            <small>低于此值的路线需重点关注</small>
                        </p>
                    </div>
                    <div class="cost-metric-card cost-metric-card-success">
                        <strong class="cost-metric-title-success">全站平均吨利润</strong>
                        <p class="cost-metric-text">
                            <span class="cost-metric-value cost-metric-title-success">{avg_profit:.1f}</span> 元<br>
                            <small>作为整体盈利基准</small>
                        </p>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🏆 目的地利润率排名 Top 8</h3>
                """
    html += _table_open(["目的地", "利润率(%)", "运费占比(%)", "总重量(吨)"])

    for idx, row in dest_cost.head(8).iterrows():
        profit_rate = row["利润率"]
        badge_class = "badge-hot" if profit_rate > 50 else "badge-cool" if profit_rate < 20 else "badge-warn"
        html += f"""<tr>
            <td class='sensitive-data'>{idx} <span class="badge {badge_class}">{profit_rate:.0f}%</span></td>
            <td>{profit_rate:.1f}%</td>
            <td>{row['运费占比']:.1f}%</td>
            <td>{row['重量（吨）']:.1f}</td>
        </tr>"""
    html += "</table></div></div>"

    return html


def build_warning_section(loss_categories, loss_routes):
    """构建亏损预警区域 HTML。"""
    html = ""

    if len(loss_categories) > 0:
        rows_html = []
        for idx, row in loss_categories.iterrows():
            rows_html.append(
                f"<tr><td>{idx}</td><td class='warning-loss-value'>{row['吨利润']:.1f}</td><td class='sensitive-data'>{row['预估利润']:.1f}</td><td>{row['重量（吨）']:.1f}</td></tr>"
            )
        html += _render_warning_table(
            '<h4 class="warning-title">🔴 严重亏损预警 - 这些品类在赔钱!</h4>',
            "warning-card-strong",
            ["品类", "平均吨利润", "总亏损", "涉及重量"],
            rows_html,
        )
    else:
        html += "<p class='warning-ok'>✅ 暂无亏损品类，运营状态良好！</p>"

    if len(loss_routes) > 0:
        rows_html = []
        for idx, row in loss_routes.iterrows():
            cat, dest = idx
            rows_html.append(
                f"<tr><td>{cat}</td><td class='sensitive-data'>{dest}</td><td class='warning-loss-value'>{row['平均吨利润']:.1f}</td><td>{int(row['车次'])}</td></tr>"
            )
        html += _render_warning_table(
            '<h4 class="warning-subtitle">🔴 亏损路线 (品类→目的地)</h4>',
            "warning-card",
            ["品类", "目的地", "吨利润", "车次"],
            rows_html,
        )

    return html


def build_suggestions_section(
    loss_routes,
    low_profit_routes,
    cost_analysis=None,
    category_summary=None,
    destination_summary=None,
    weekly_summary=None,
    top_vehicles=None,
):
    """构建智能建议区域 HTML（增强版）。"""
    suggestions = []

    if len(loss_routes) > 0:
        suggestions.append(
            f"⚠️ <strong>亏损预警：</strong>发现 {len(loss_routes)} 条亏损路线，建议重点关注并优化定价或暂停发货。"
        )

    if len(low_profit_routes) > 0:
        suggestions.append(
            f"💡 <strong>低利润提醒：</strong>{len(low_profit_routes)} 条路线利润低于平均水平 50%，建议评估是否继续发货。"
        )

    if cost_analysis and "dest_cost" in cost_analysis:
        dest_cost = cost_analysis["dest_cost"]
        high_profit_dests = dest_cost[dest_cost["利润率"] > 60]
        if len(high_profit_dests) > 0:
            top_dest = high_profit_dests.head(3).index.tolist()
            suggestions.append(
                f"🌟 <strong>高利润路线：</strong>{', '.join(top_dest)} 利润率超过 60%，建议优先发货、扩大合作。"
            )

    if cost_analysis and "total_freight_ratio" in cost_analysis:
        freight_ratio = cost_analysis["total_freight_ratio"]
        if freight_ratio > 60:
            suggestions.append(
                f"🚚 <strong>运费优化：</strong>总运费占比达 {freight_ratio:.1f}%，偏高。建议与运输方谈判降低运费，或选择更优运输路线。"
            )
        elif freight_ratio > 45:
            suggestions.append(
                f"🚚 <strong>运费关注：</strong>总运费占比 {freight_ratio:.1f}%，处于中等水平，建议持续关注运输成本变化。"
            )

    if category_summary is not None and len(category_summary) > 0:
        sorted_cats = category_summary.sort_values("吨利润", ascending=False)
        if len(sorted_cats) >= 2:
            best_cat = sorted_cats.index[0]
            best_profit = sorted_cats.iloc[0]["吨利润"]
            worst_cat = sorted_cats.index[-1]
            worst_profit = sorted_cats.iloc[-1]["吨利润"]

            if best_profit > 0:
                suggestions.append(
                    f"📦 <strong>品类优化：</strong>“{best_cat}”吨利润最高({best_profit:.1f}元)，建议增加采购；"
                    f"“{worst_cat}”利润较低({worst_profit:.1f}元)，建议调整定价策略。"
                )

    if destination_summary is not None and len(destination_summary) > 0:
        total_weight = destination_summary["总重量"].sum()
        top1_weight = destination_summary.sort_values("总重量", ascending=False).iloc[0]["总重量"]
        top1_name = destination_summary.sort_values("总重量", ascending=False).index[0]
        concentration = top1_weight / total_weight * 100 if total_weight > 0 else 0

        if concentration > 50:
            suggestions.append(
                f"📍 <strong>客户集中度：</strong>“{top1_name}”占总发货量 {concentration:.1f}%，风险较高，建议开拓新客户分散风险。"
            )

    if top_vehicles is not None and len(top_vehicles) > 0:
        top_vehicle = top_vehicles.index[0]
        top_score = top_vehicles.iloc[0]["综合评分"]
        if top_score >= 90:
            suggestions.append(
                f"🏆 <strong>骨干车辆：</strong>“{top_vehicle}”综合评分 {top_score:.1f}，表现优异，建议长期合作并给予优惠锁定。"
            )

    if weekly_summary is not None and len(weekly_summary) > 0:
        best_week = weekly_summary["总重量"].idxmax()
        worst_week = weekly_summary["总重量"].idxmin()
        best_weight = weekly_summary.loc[best_week, "总重量"]
        worst_weight = weekly_summary.loc[worst_week, "总重量"]

        if best_weight > worst_weight * 2:
            suggestions.append(
                f"📅 <strong>周度均衡：</strong>“{best_week}”发货最多({best_weight:.1f}吨)，“{worst_week}”最少({worst_weight:.1f}吨)，建议平衡发货节奏。"
            )

    if len(suggestions) == 0:
        suggestions.append("✨ <strong>运营状态良好：</strong>各项指标健康，暂无明显风险，继续保持。")

    return _render_suggestion_card("💡 智能运营建议", suggestions)

