# -*- coding: utf-8 -*-
"""
打包站智能分析系统 By 李小泡 v8.2 (模块化重构版)
核心逻辑主入口
"""
import os
import sys
import time
import webbrowser
import threading
from datetime import datetime
from tkinter import messagebox

# 导入自定义模块
from config import APP_NAME, APP_AUTHOR, VERSION, OUTPUT_FOLDER_NAME
from core.logger import print_log, error_logger
from core.cache import data_cache
from gui.app import AppGUI
from gui.dialogs import show_file_dialog, check_file_access
from data.loader import ThreadedDataLoader, load_and_clean_sheet
from data.cleaner import clean_dataframe
from analysis.summary import create_summary_table
from analysis.monthly import create_monthly_comparison
from analysis.cost import create_cost_analysis
from visualization.charts import create_dashboard_figure
from report.html_builder import build_analysis_report
from report.dashboard_builder import build_dashboard_html

# ==========================================
# 1. 程序启动区
# ==========================================



def get_desktop_path():
    """获取真实桌面路径"""
    return os.path.join(os.path.expanduser("~"), 'Desktop')

def main():
    # --- 程序入口 ---
    print("=" * 60)
    print(f"  {APP_NAME} v{VERSION}")
    print(f"  开发者: {APP_AUTHOR}  |  核心算法: Pandas + Plotly + Scipy")
    print("=" * 60)
    print_log("系统内核启动中...", "BOOT")
    print_log("正在验证管理员权限...", "AUTH")
    time.sleep(0.3) 
    print_log("权限验证通过！欢迎回来，指挥官。", "OK")
    print("-" * 60)

    # 导入重型库 (延迟加载以提升观感)
    try:
        print_log("正在初始化数据引擎 (Pandas)...", "LOAD")
        import pandas as pd
        
        print_log("正在预热绘图引擎 (Plotly)...", "LOAD")
        import plotly.io as pio
        # pio.renderers.default = "browser" 
        
        print_log("正在加载 AI 预测算法 (Scipy)...", "LOAD")
        from scipy import stats

        print_log("所有核心模块加载完毕！引擎就绪。", "OK")
        print("-" * 60)
        
    except ImportError as e:
        missing_lib = str(e).replace("No module named '", "").replace("'", "")
        error_logger.log_error(
            "模块缺失", 
            f"核心模块 [{missing_lib}] 未安装",
            exception=e,
            suggestion=f"请运行: pip install {missing_lib}"
        )
        sys.exit(1)

    # 解决高分屏模糊
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # 初始化 GUI 工具
    app = AppGUI()

    # ==========================================
    #      逻辑处理主流程
    # ==========================================

    # --- 3. 交互式选择文件 ---
    print_log("等待用户选择 Excel 文件...", "WAIT")
    file_path = show_file_dialog()
    
    if not file_path:
        print_log("用户取消了文件选择，系统下线。", "WARN")
        time.sleep(1)
        sys.exit()

    print_log(f"已捕获文件目标: {os.path.basename(file_path)}", "FILE")

    # --- 4. 文件占用检测 ---
    if not check_file_access(file_path):
        print_log("无法获取文件权限，程序退出。", "STOP")
        sys.exit()

    # --- 5. Sheet 选择与进度条启动 ---
    app.show_progress_window()
    app.update_progress(5, "正在扫描 Excel 结构...")

    try:
        # 使用 openpyxl 快速读取 sheet 名，不读取内容
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        sheet_names = xl.sheet_names
    except Exception as e:
        app.close_progress()
        error_logger.log_error("Excel读取失败", "无法识别 Excel 结构", exception=e)
        sys.exit()

    app.win.withdraw() # 暂时隐藏进度条，显示选择框
    selected_sheets = app.ask_sheet_name(sheet_names, file_path)

    if not selected_sheets:
        app.close_progress()
        print_log("未选择工作表，程序退出。", "STOP")
        sys.exit()

    # 判断是否为多月对比模式
    is_compare_mode = len(selected_sheets) > 1
    target_sheet = selected_sheets[0] if not is_compare_mode else "多月对比"

    app.win.deiconify() # 重新显示进度条
    
    if is_compare_mode:
        app.update_progress(10, f"正在加载 {len(selected_sheets)} 个月份数据进行对比...")
        print_log(f"🔄 启动多月对比模式: {', '.join(selected_sheets)}", "COMPARE")
    else:
        app.update_progress(10, f"正在锁定目标数据: [{target_sheet}]")
        print_log(f"开始分析工作表: {target_sheet}", "START")

    # --- 6. 数据读取与智能清洗 (升级版 - 支持多月份 + 磁盘缓存) ---
    data_loader = ThreadedDataLoader(app)
    
    # ============ 🚀 性能优化：检查磁盘缓存 + 异步加载 ============
    cached_df = data_cache.get(file_path, selected_sheets, 'df')
    if cached_df is not None:
        print_log("⚡ 命中磁盘缓存！跳过 Excel 读取", "CACHE")
        # 模拟加载过程动画
        for i in range(10, 31, 5):
            app.update_progress(i, "正在从高速缓存加载数据...", records_info=f"{len(cached_df)} 条")
            time.sleep(0.05)
        df = cached_df
    else:
        # 缓存未命中，启动多线程异步加载
        print_log("启动多线程异步加载引擎...", "ASYNC")
        data_loader.set_load_function(load_and_clean_sheet)
        
        # 用于等待异步加载完成的事件
        load_complete_event = threading.Event()
        load_result = {'status': None, 'data': None, 'extra': None, 'error': None}
        
        def on_load_complete(status, data, extra):
            """异步加载完成回调"""
            load_result['status'] = status
            load_result['data'] = data
            load_result['extra'] = extra
            load_complete_event.set()
        
        # 启动异步加载
        data_loader.load_sheets_async(file_path, selected_sheets, on_load_complete)
        
        # 使用事件循环等待，避免阻塞 GUI
        def wait_for_load():
            if not load_complete_event.is_set():
                app.root.update()
                app.root.after(50, wait_for_load)
        
        # 启动等待循环
        wait_for_load()
        
        # 使用 mainloop 等待异步操作完成
        _async_load_pending = True
        
        # 等待异步加载完成（使用 tkinter 事件循环）
        while _async_load_pending and not load_complete_event.is_set():
            app.root.update()
            time.sleep(0.01)
        
        # 最终确认 df 已加载
        if load_result['status'] == 'success':
            df = load_result['data']
            print_log(f"异步加载完成，共 {len(df)} 条记录", "OK")
            # 存入缓存
            data_cache.set(file_path, selected_sheets, 'df', df)
        else:
            app.close_progress()
            error_msg = "数据加载失败"
            if load_result['extra'] and 'message' in load_result['extra']:
                error_msg = load_result['extra']['message']
            
            error_logger.show_error_dialog("加载失败", error_msg)
            sys.exit()

    # --- 数据清洗与处理 ---
    app.update_progress(32, "正在执行智能数据清洗...", records_info=f"{len(df)} 条待处理")
    
    df, col_info = clean_dataframe(df)

    # 检查是否杀太狠了
    if df.empty:
        app.close_progress()
        msg = "所有数据都被过滤掉了！\n请检查：\n1. 是否所有数据都没填'扣点'或'卖出价'？\n2. '卖出价'是否都填的0？"
        messagebox.showerror("有效数据为空", msg)
        sys.exit()

    app.update_progress(45, "正在计算关键财务指标...")
    print_log(f"数据准备就绪，有效记录: {len(df)} 条", "DATA")

    # --- 7. 多维度分析汇总表 ---
    app.update_progress(55, "正在构建多维数据模型...")
    category_summary, destination_summary, weekly_summary = create_summary_table(df)

    # --- 多月份对比分析 ---
    app.update_progress(62, "正在进行多月份对比分析...")
    monthly_summary, monthly_category, monthly_dest = create_monthly_comparison(df, is_compare_mode)

    # --- 成本分析 ---
    app.update_progress(70, "正在进行成本与利润分析...")
    cost_analysis = create_cost_analysis(df)

    # --- 8. 创建可视化图表 ---
    app.update_progress(80, "正在渲染动画与可视化图表...")
    
    # 准备 KPI 数据
    total_weight = df['重量（吨）'].sum()
    total_profit = df['预估利润'].sum()
    avg_profit_per_ton = total_profit / total_weight if total_weight > 0 else 0
    total_shipments = len(df)
    avg_daily_weight = df.groupby('中文日期')['重量（吨）'].sum().mean() if not df.empty else 0
    total_profit_wan = total_profit / 10000
    
    kpi_title_prefix = f"[{', '.join(selected_sheets)}]" if is_compare_mode else f"[{target_sheet}]"
    kpi_data = [
        {"value": total_weight, "title": f"{kpi_title_prefix} 总发货量", "suffix": " 吨", "color": '#00FF99', "valueformat": ".1f"},
        {"value": total_profit_wan, "title": "总预估利润", "suffix": " 万", "color": '#FF00CC', "valueformat": ".2f"},
        {"value": avg_profit_per_ton, "title": "平均吨利润", "suffix": " 元", "color": '#FFFF33', "valueformat": ".1f"},
        {"value": total_shipments, "title": "总运输车次", "suffix": " 车", "color": '#00CCFF'},
        {"value": avg_daily_weight, "title": "日均发货量", "suffix": " 吨", "color": '#CC00FF', "valueformat": ".1f"}
    ]
    
    # 渲染图表
    fig = create_dashboard_figure(df, kpi_data, cost_analysis, weekly_summary)

    # --- 9. 生成深度分析报告 ---
    app.update_progress(88, "正在生成深度分析报告...")
    generate_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 计算 Top Vehicles (用于报告)
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

    analysis_report = build_analysis_report(
        target_sheet, generate_time, kpi_data, 
        category_summary, destination_summary, weekly_summary,
        top_vehicles, cost_analysis, kpi_title_prefix
    )

    # --- 10. 获取桌面路径并保存文件 ---
    app.update_progress(96, "正在生成最终文件...")
    print_log("正在写入文件到桌面...", "SAVE")

    desktop_path = get_desktop_path()
    folder_name = OUTPUT_FOLDER_NAME
    save_dir = os.path.join(desktop_path, folder_name)

    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            print_log(f"已创建输出目录: {save_dir}", "DIR")
        except Exception as e:
            print_log(f"无法创建目录，将保存到桌面: {e}", "WARN")
            save_dir = desktop_path

    # 生成文件名
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_prefix = f"多月对比" if is_compare_mode else f"{target_sheet}"
    
    # 生成文件路径
    dashboard_file = os.path.join(save_dir, f"{file_prefix}_仪表板_{timestamp_str}.html")
    report_file = os.path.join(save_dir, f"{file_prefix}_深度报告_{timestamp_str}.html")
    excel_file = os.path.join(save_dir, f"{file_prefix}_清洗后数据_{timestamp_str}.xlsx")

    # --- 生成独立的仪表板 HTML（含动画效果） ---
    dest_list = df['目的地'].unique().tolist() if '目的地' in df.columns else []
    dashboard_html = build_dashboard_html(fig, kpi_title_prefix, dest_list, generate_time)
    
    try:
        # 保存仪表板
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        print_log(f"仪表板已生成: {dashboard_file}", "SUCCESS")
        
        # 保存深度报告（静态内容，不含 Plotly 图表）
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(analysis_report)
        print_log(f"深度报告已生成: {report_file}", "SUCCESS")
        
        # 导出清洗后的数据
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='清洗后明细', index=False)
            category_summary.to_excel(writer, sheet_name='品类汇总')
            destination_summary.to_excel(writer, sheet_name='目的地汇总')
            cost_analysis['dest_cost'].to_excel(writer, sheet_name='成本分析')
        print_log(f"数据已备份: {excel_file}", "SUCCESS")
        
        app.update_progress(100, "🎉 分析完成！准备展示成果...")
        time.sleep(1)
        app.close_progress()

        # --- 11. 自动打开结果 ---
        print_log("正在唤醒默认浏览器...", "OPEN")
        
        # 先打开仪表板
        if os.path.exists(dashboard_file):
            webbrowser.open(f'file:///{dashboard_file}')
        
        # 再打开报告
        time.sleep(0.5)
        if os.path.exists(report_file):
            webbrowser.open(f'file:///{report_file}')
        
        # 打开文件夹
        os.startfile(save_dir)

    except Exception as e:
        app.close_progress()
        error_logger.log_error("保存失败", "无法写入报告文件", exception=e, suggestion="请检查文件是否被占用")
        sys.exit()

if __name__ == '__main__':
    main()
