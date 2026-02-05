# -*- coding: utf-8 -*-
"""
HTML 报告构建器
"""
from datetime import datetime

from .styles import (
    get_base_styles, get_button_styles, get_card_styles, 
    get_table_styles, get_animation_styles, get_print_styles
)
from .scripts import (
    get_base_scripts, get_particle_animation_js, 
    get_counter_animation_js, get_stagger_animation_js
)


def build_analysis_report(target_sheet, generate_time, kpi_data, 
                         category_summary, destination_summary, weekly_summary,
                         top_vehicles, cost_analysis, kpi_title_prefix, 
                         daily_summary=None):
    """构建完整 HTML 分析报告"""
    
    # 提取成本分析数据
    freight_ratio = cost_analysis['total_freight_ratio']
    dest_cost = cost_analysis['dest_cost']
    loss_categories = cost_analysis['loss_categories']
    loss_routes = cost_analysis['loss_routes']
    low_profit_routes = cost_analysis['low_profit_routes']
    avg_profit = cost_analysis['avg_profit']
    low_threshold = cost_analysis['low_threshold']
    
    # 构建各个HTML部分
    styles = (
        get_base_styles() + get_button_styles() + 
        get_card_styles() + get_table_styles() + 
        get_animation_styles() + get_print_styles()
    )
    
    scripts = (
        get_base_scripts() + get_particle_animation_js() + 
        get_counter_animation_js() + get_stagger_animation_js()
    )
    
    # 头部区域
    header_html = build_header_section(target_sheet, generate_time)
    
    # KPI 区域
    kpi_html = build_kpi_section(kpi_data)
    
    # 数据总览区域 (品类+目的地)
    overview_html = build_overview_section(category_summary, destination_summary)
    
    # 每日峰值分析 (新增)
    daily_html = build_daily_section(daily_summary) if daily_summary is not None else ""
    
    # 深度洞察区域 (周度+车辆)
    insight_html = build_insight_section(weekly_summary, top_vehicles)
    
    # 成本与利润分析区域
    cost_html = build_cost_analysis_section(freight_ratio, low_threshold, avg_profit, dest_cost)
    
    # 亏损预警区域
    warning_html = build_warning_section(loss_categories, loss_routes)
    
    # 智能建议区域（增强版 - 传入更多数据）
    suggestion_html = build_suggestions_section(
        loss_routes, low_profit_routes, 
        cost_analysis=cost_analysis,
        category_summary=category_summary,
        destination_summary=destination_summary,
        weekly_summary=weekly_summary,
        top_vehicles=top_vehicles
    )
    
    # 组装完整HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
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
            <button class="btn btn-print" onclick="printReport()">🖨️ 打印PDF</button>
            <button class="btn btn-shot" onclick="captureScreenshot()">📸 导出长图</button>
            <button class="btn btn-privacy" id="privacyBtn" onclick="togglePrivacy()">👁️ 隐藏利润</button>
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
            <p>POWERED BY 李小泡智能分析系统 v8.1 | 核心算法支持：Pandas + Plotly + Scipy</p>
        </div>
    </div>
</body>
</html>
    """
    return html


def build_header_section(target_sheet, generate_time):
    """构建头部区域 HTML"""
    return f"""
        <div class="header">
            <h1 class="glitch" data-text="西关打包站深度运营分析报告">📊 西关打包站深度运营分析报告</h1>
            <p>分析对象: {target_sheet} | 生成时间: {generate_time} | 李小泡专属系统</p>
        </div>
    """


def build_kpi_section(kpi_data):
    """构建 KPI 区域 HTML"""
    kpi_html = '<div class="kpi-container">'
    for kpi in kpi_data:
        title = kpi['title']
        value_fmt = f"{kpi['value']:.1f}" if isinstance(kpi['value'], float) else f"{kpi['value']}"
        suffix = kpi['suffix']
        color = kpi['color']
        
        # 添加敏感数据标记 (利润相关)
        sensitive_class = "sensitive-data" if "利润" in title else ""
        
        kpi_html += f"""
            <div class="kpi-box">
                <div class="kpi-lbl">{title}</div>
                <div class="kpi-val {sensitive_class}" style="color:{color}">{value_fmt}{suffix}</div>
            </div>
        """
    kpi_html += '</div>'
    return kpi_html


def build_daily_section(daily_summary):
    """构建日度峰值分析区域"""
    if daily_summary.empty:
        return ""
        
    # 找到极值
    max_day = daily_summary['总重量'].idxmax()
    min_day = daily_summary['总重量'].idxmin()
    max_val = daily_summary.loc[max_day, '总重量']
    min_val = daily_summary.loc[min_day, '总重量']
    
    max_profit_day = daily_summary['总利润'].idxmax()
    max_profit_val = daily_summary.loc[max_profit_day, '总利润']
    
    # 计算均值作为基准
    avg_val = daily_summary['总重量'].mean()

    return f'''
    <h2 class="section-title" style="margin-top: 30px;">📅 每日峰值透视 (High/Low)</h2>
    <div class="card">
        <div style="display: flex; gap: 30px; justify-content: space-around;">
             <div style="text-align: center; color: #ff5e62;">
                <div style="font-size: 12px; color: #aaa; margin-bottom: 5px;">🔥 巅峰爆单日</div>
                <div style="font-size: 20px; font-weight: bold; margin-bottom: 5px;">{max_day}</div>
                <div style="font-size: 28px; color: #ff5e62; font-weight: 800;">{max_val:.1f} <span style="font-size:14px">吨</span></div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">是平均水平的 {(max_val/avg_val):.1f} 倍</div>
            </div>
            
             <div style="width: 1px; background: rgba(255,255,255,0.1);"></div>
            
             <div style="text-align: center; color: #00FF99;">
                <div style="font-size: 12px; color: #aaa; margin-bottom: 5px;">💰 利润最高日</div>
                <div style="font-size: 20px; font-weight: bold; margin-bottom: 5px;">{max_profit_day}</div>
                <div class="sensitive-data" style="font-size: 28px; color: #00FF99; font-weight: 800;">{max_profit_val/10000:.2f} <span style="font-size:14px">万</span></div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">单日利润之王</div>
            </div>

            <div style="width: 1px; background: rgba(255,255,255,0.1);"></div>

            <div style="text-align: center; color: #00CCFF;">
                <div style="font-size: 12px; color: #aaa; margin-bottom: 5px;">🧊 运营低谷日</div>
                <div style="font-size: 20px; font-weight: bold; margin-bottom: 5px;">{min_day}</div>
                <div style="font-size: 28px; color: #00CCFF; font-weight: 800;">{min_val:.1f} <span style="font-size:14px">吨</span></div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">需关注原因</div>
            </div>
        </div>
    </div>
    '''


def build_overview_section(category_summary, destination_summary):
    """构建数据总览区域 HTML"""
    # 计算最大值用于进度条归一化
    max_cat_weight = category_summary['总重量'].max() if not category_summary.empty else 1
    max_dest_weight = destination_summary['总重量'].max() if not destination_summary.empty else 1
    
    html = """<div class="grid-2">
            <div class="card">
                <h3>🏷️ 品类综合表现</h3>
                <table><tr><th>品类</th><th>总量(吨)</th><th>总利润(万)</th><th>吨利润</th></tr>"""
    
    for idx, row in category_summary.sort_values('总重量', ascending=False).head(8).iterrows():
        weight = row['总重量']
        bar_width = (weight / max_cat_weight) * 100
        html += f"""<tr>
            <td>{idx}</td>
            <td>
                <div class="bar-container">
                    <span>{weight:.1f}</span>
                    <div class="bar-bg"><div class="data-bar" style="width: {bar_width}%; --width: {bar_width}%; background: linear-gradient(90deg, #00C9FF, #92FE9D);"></div></div>
                </div>
            </td>
            <td class='sensitive-data'>{(row['总利润']/10000):.3f}</td>
            <td class='sensitive-data'>{row['吨利润']:.1f}</td>
        </tr>"""
    html += "</table></div>"
    
    html += """<div class="card">
                <h3>📍 热门目的地 Top 8</h3>
                <table><tr><th>目的地</th><th>总量(吨)</th><th>车次</th><th>吨均运费</th></tr>"""
    
    for idx, row in destination_summary.sort_values('总重量', ascending=False).head(8).iterrows():
        weight = row['总重量']
        bar_width = (weight / max_dest_weight) * 100
        html += f"""<tr>
            <td class='sensitive-data'>{idx}</td>
            <td>
                <div class="bar-container">
                    <span>{weight:.1f}</span>
                    <div class="bar-bg"><div class="data-bar" style="width: {bar_width}%; --width: {bar_width}%; background: linear-gradient(90deg, #F9D423, #FF4E50);"></div></div>
                </div>
            </td>
            <td>{int(row['车次'])}</td>
            <td>{row['吨均运费']:.1f}</td>
        </tr>"""
    html += "</table></div></div>"
    
    return html


def build_insight_section(weekly_summary, top_vehicles):
    """构建深度洞察区域 HTML"""
    # 计算最大值
    max_week_weight = weekly_summary['总重量'].max() if not weekly_summary.empty else 1
    max_vehicle_weight = top_vehicles['重量（吨）'].max() if not top_vehicles.empty else 1
    
    html = """<div class="grid-2">
            <div class="card">
                <h3>📅 周度趋势雷达</h3>
                <table><tr><th>周次</th><th>总重量(吨)</th><th>总利润(元)</th><th>车次</th></tr>"""
    
    for idx, row in weekly_summary.iterrows():
        weight = row['总重量']
        bar_width = (weight / max_week_weight) * 100
        html += f"""<tr>
            <td>{idx}</td>
            <td>
                <div class="bar-container">
                    <span>{weight:.1f}</span>
                    <div class="bar-bg"><div class="data-bar" style="width: {bar_width}%; --width: {bar_width}%; background: linear-gradient(90deg, #A8CABA, #5D4157);"></div></div>
                </div>
            </td>
            <td class='sensitive-data'>{row['总利润']:.0f}</td>
            <td>{int(row['运输次数'])}</td>
        </tr>"""
    html += "</table></div>"
    
    html += """<div class="card">
                <h3>🚛 荣耀车队榜 (Top 8)</h3>
                <table><tr><th>车牌号</th><th>总重量</th><th>车次</th><th>综合评分</th></tr>"""
    
    for idx, row in top_vehicles.iterrows():
        score = row['综合评分']
        badge = '<span class="badge badge-hot">金牌</span>' if score >= 90 else ''
        weight = row['重量（吨）']
        bar_width = (weight / max_vehicle_weight) * 100
        
        html += f"""<tr>
            <td>{idx} {badge}</td>
            <td>
                <div class="bar-container">
                    <span>{weight:.1f}</span>
                    <div class="bar-bg"><div class="data-bar" style="width: {bar_width}%; --width: {bar_width}%; background: linear-gradient(90deg, #ff9966, #ff5e62);"></div></div>
                </div>
            </td>
            <td>{int(row['运输次数'])}</td>
            <td>{score:.1f}</td>
        </tr>"""
    html += "</table></div></div>"
    
    return html


def build_cost_analysis_section(freight_ratio, low_threshold, avg_profit, dest_cost):
    """构建成本分析区域 HTML"""
    # 运费占比颜色
    ratio_color = "#00FF99" if freight_ratio < 40 else "#FFFF33" if freight_ratio < 60 else "#FF3333"
    
    html = f"""
        <div class="grid-2" style="margin-top: 25px;">
            <div class="card">
                <h3>💰 吨利润红黑榜</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; font-size: 13px;">
                    <div style="padding: 15px; background: rgba(255,51,51,0.1); border-radius: 8px;">
                        <strong style="color:#FF3333;">总运费占比</strong>
                        <p style="margin: 8px 0 0 0; color: #aaa; line-height: 1.5;">
                            <span style="font-size: 24px; color:{ratio_color}; font-weight:bold;">{freight_ratio:.1f}%</span><br>
                            <small>占总收入比例</small>
                        </p>
                    </div>
                    <div style="padding: 15px; background: rgba(255,255,51,0.1); border-radius: 8px;">
                        <strong style="color:#FFFF33;">低利润警戒线</strong>
                        <p style="margin: 8px 0 0 0; color: #aaa; line-height: 1.5;">
                            <span style="font-size: 24px; color:#FFFF33; font-weight:bold;">{low_threshold:.1f}</span> 元<br>
                            = 平均吨利润 × 50%<br>
                            <small>低于此值的路线需重点关注</small>
                        </p>
                    </div>
                    <div style="padding: 15px; background: rgba(0,255,153,0.1); border-radius: 8px;">
                        <strong style="color:#00FF99;">全站平均吨利润</strong>
                        <p style="margin: 8px 0 0 0; color: #aaa; line-height: 1.5;">
                            <span style="font-size: 24px; color:#00FF99; font-weight:bold;">{avg_profit:.1f}</span> 元<br>
                            <small>作为整体盈利基准</small>
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🏆 目的地利润率排名 Top 8</h3>
                <table><tr><th>目的地</th><th>利润率(%)</th><th>运费占比(%)</th><th>总重量(吨)</th></tr>"""
    
    for idx, row in dest_cost.head(8).iterrows():
        profit_rate = row['利润率']
        badge_class = 'badge-hot' if profit_rate > 50 else 'badge-cool' if profit_rate < 20 else 'badge-warn'
        html += f"""<tr>
            <td class='sensitive-data'>{idx} <span class="badge {badge_class}">{profit_rate:.0f}%</span></td>
            <td>{profit_rate:.1f}%</td>
            <td>{row['运费占比']:.1f}%</td>
            <td>{row['重量（吨）']:.1f}</td>
        </tr>"""
    html += "</table></div></div>"
    
    return html


def build_warning_section(loss_categories, loss_routes):
    """构建亏损预警区域 HTML"""
    html = ""
    # 亏损品类
    if len(loss_categories) > 0:
        html += """<h4 style="color:#FF3333; margin-top:30px;">🔴 严重亏损预警 - 这些品类在赔钱!</h4>
                    <div class="card" style="border: 1px solid #FF3333; box-shadow: 0 0 20px rgba(255, 51, 51, 0.2);">
                    <table><tr><th>品类</th><th>平均吨利润</th><th>总亏损</th><th>涉及重量</th></tr>"""
        for idx, row in loss_categories.iterrows():
            html += f"<tr><td>{idx}</td><td style='color:#FF3333; font-weight:bold;'>{row['吨利润']:.1f}</td><td class='sensitive-data'>{row['预估利润']:.1f}</td><td>{row['重量（吨）']:.1f}</td></tr>"
        html += "</table></div>"
    else:
        html += "<p style='color:#00FF99; margin-top:20px;'>✅ 暂无亏损品类，运营状态良好！</p>"
    
    # 亏损路线
    if len(loss_routes) > 0:
        html += """<h4 style="color:#FF3333; margin-top:20px;">🔴 亏损路线 (品类→目的地)</h4>
                    <div class="card" style="border: 1px solid #FF3333;">
                    <table><tr><th>品类</th><th>目的地</th><th>吨利润</th><th>车次</th></tr>"""
        for idx, row in loss_routes.iterrows():
            cat, dest = idx
            html += f"<tr><td>{cat}</td><td class='sensitive-data'>{dest}</td><td style='color:#FF3333;'>{row['平均吨利润']:.1f}</td><td>{int(row['车次'])}</td></tr>"
        html += "</table></div>"
        
    return html


def build_suggestions_section(loss_routes, low_profit_routes, cost_analysis=None, 
                               category_summary=None, destination_summary=None, 
                               weekly_summary=None, top_vehicles=None):
    """构建智能建议区域 HTML（增强版 - 更多分析维度）"""
    html = f"""
        <div class="card" style="margin-top: 30px; background: linear-gradient(to right, #2d2d2d, #3d3d3d);">
            <h3 style="color:#FF00CC">💡 智能运营建议</h3>
            <ul style="line-height: 2.0; color: #ddd;">
    """
    
    suggestions = []
    
    # 1. 亏损预警
    if len(loss_routes) > 0:
        suggestions.append(f"""⚠️ <strong>亏损预警：</strong> 发现 {len(loss_routes)} 条亏损路线，建议重点关注并优化定价或暂停发货。""")
    
    # 2. 低利润提醒
    if len(low_profit_routes) > 0:
        suggestions.append(f"""💡 <strong>低利润提醒：</strong> {len(low_profit_routes)} 条路线利润低于平均水平50%，建议评估是否继续发货。""")
    
    # 3. 高利润路线推荐（如果有成本分析数据）
    if cost_analysis and 'dest_cost' in cost_analysis:
        dest_cost = cost_analysis['dest_cost']
        high_profit_dests = dest_cost[dest_cost['利润率'] > 60]
        if len(high_profit_dests) > 0:
            top_dest = high_profit_dests.head(3).index.tolist()
            suggestions.append(f"""🌟 <strong>高利润路线：</strong> {', '.join(top_dest)} 利润率超过60%，建议优先发货、扩大合作。""")
    
    # 4. 运费占比优化
    if cost_analysis and 'total_freight_ratio' in cost_analysis:
        freight_ratio = cost_analysis['total_freight_ratio']
        if freight_ratio > 60:
            suggestions.append(f"""🚚 <strong>运费优化：</strong> 总运费占比达 {freight_ratio:.1f}%，偏高。建议与运输方谈判降低运费，或选择更优运输路线。""")
        elif freight_ratio > 45:
            suggestions.append(f"""🚚 <strong>运费关注：</strong> 总运费占比 {freight_ratio:.1f}%，处于中等水平，持续关注运输成本变化。""")
    
    # 5. 品类分析建议
    if category_summary is not None and len(category_summary) > 0:
        # 找出最赚钱和最不赚钱的品类
        sorted_cats = category_summary.sort_values('吨利润', ascending=False)
        if len(sorted_cats) >= 2:
            best_cat = sorted_cats.index[0]
            best_profit = sorted_cats.iloc[0]['吨利润']
            worst_cat = sorted_cats.index[-1]
            worst_profit = sorted_cats.iloc[-1]['吨利润']
            
            if best_profit > 0:
                suggestions.append(f"""📦 <strong>品类优化：</strong> 「{best_cat}」吨利润最高({best_profit:.1f}元)，建议增加采购；「{worst_cat}」利润较低({worst_profit:.1f}元)，建议调整定价策略。""")
    
    # 6. 目的地集中度分析
    if destination_summary is not None and len(destination_summary) > 0:
        total_weight = destination_summary['总重量'].sum()
        top1_weight = destination_summary.sort_values('总重量', ascending=False).iloc[0]['总重量']
        top1_name = destination_summary.sort_values('总重量', ascending=False).index[0]
        concentration = top1_weight / total_weight * 100 if total_weight > 0 else 0
        
        if concentration > 50:
            suggestions.append(f"""📍 <strong>客户集中度：</strong> 「{top1_name}」占总发货量 {concentration:.1f}%，风险较高。建议开拓新客户分散风险。""")
    
    # 7. 车辆激励建议
    if top_vehicles is not None and len(top_vehicles) > 0:
        top_vehicle = top_vehicles.index[0]
        top_score = top_vehicles.iloc[0]['综合评分']
        if top_score >= 90:
            suggestions.append(f"""🏆 <strong>骨干车辆：</strong> 「{top_vehicle}」综合评分 {top_score:.1f}，表现优异！建议长期合作，给予运费优惠锁定。""")
    
    # 8. 周度运营建议
    if weekly_summary is not None and len(weekly_summary) > 0:
        best_week = weekly_summary['总重量'].idxmax()
        worst_week = weekly_summary['总重量'].idxmin()
        best_weight = weekly_summary.loc[best_week, '总重量']
        worst_weight = weekly_summary.loc[worst_week, '总重量']
        
        if best_weight > worst_weight * 2:
            suggestions.append(f"""📅 <strong>周度均衡：</strong> 「{best_week}」发货最多({best_weight:.1f}吨)，「{worst_week}」最少({worst_weight:.1f}吨)，差异较大。建议平衡各日发货量，降低仓储压力。""")
    
    # 无建议时显示正面信息
    if len(suggestions) == 0:
        suggestions.append("""✨ <strong>完美运营：</strong> 各项指标健康，暂无明显风险。继续保持！""")
    
    # 组装HTML
    for suggestion in suggestions:
        html += f"""<li style="margin-bottom: 12px;">{suggestion}</li>"""
        
    html += """
            </ul>
        </div>
    """
    return html

