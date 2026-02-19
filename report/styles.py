# -*- coding: utf-8 -*-
"""
HTML 报告样式定义 (CSS)
"""

def get_base_styles():
    """获取基础页面样式"""
    return """
        :root { --safe-bottom: env(safe-area-inset-bottom, 0px); }
        body { font-family: 'Segoe UI', 'Roboto', 'Microsoft YaHei', sans-serif; margin: 40px; background:radial-gradient(circle at top left, #1a1a2e, #16213e); color: #e0e0e0; line-height: 1.6; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; animation: fadeIn 1s ease-out; }
        
        /* --- 滚动条完美样式 (与仪表板统一) --- */
        ::-webkit-scrollbar { width: 10px; background: #0f0c29; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; border: 1px solid #444; }
        ::-webkit-scrollbar-thumb:hover { background: #00FF99; }
        
        /* --- 赛博朋克头部 --- */
        .header { 
            text-align: center; padding: 40px; 
            background: rgba(30, 30, 30, 0.6); 
            backdrop-filter: blur(10px);
            border-radius: 20px; margin-bottom: 40px; 
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
            position: relative; overflow: hidden;
        }
        .header::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, #00FF99, #00CCFF, transparent);
            animation: scanline 3s linear infinite;
        }
        @keyframes scanline { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

        .header h1 { margin: 0; font-size: 3em; letter-spacing: 2px; text-transform: uppercase; position: relative; display: inline-block; }
        
        /* --- 故障文字特效 --- */
        .glitch {
            color: #fff;
            text-shadow: 2px 2px 0px #FF00CC, -2px -2px 0px #00CCFF;
            animation: glitch 1s infinite alternate-reverse;
        }
        @keyframes glitch {
            0% { text-shadow: 2px 2px 0px #FF00CC, -2px -2px 0px #00CCFF; transform: translate(0); }
            20% { text-shadow: -2px 2px 0px #FF00CC, 2px -2px 0px #00CCFF; transform: translate(-1px, 1px); }
            40% { text-shadow: 2px -2px 0px #FF00CC, -2px 2px 0px #00CCFF; transform: translate(1px, -1px); }
            60% { text-shadow: 0px 2px 0px #FF00CC, 0px -2px 0px #00CCFF; transform: translate(-1px, -1px); }
            80% { text-shadow: 2px 0px 0px #FF00CC, -2px 0px 0px #00CCFF; transform: translate(1px, 1px); }
            100% { text-shadow: 0px 0px 0px #FF00CC, 0px 0px 0px #00CCFF; transform: translate(0); }
        }
        
        .section-title { 
            color: #00FF99; border-left: 6px solid #00FF99; padding-left: 20px; margin: 50px 0 30px 0; font-size: 1.8em; 
            text-shadow: 0 0 10px rgba(0, 255, 153, 0.3);
            background: linear-gradient(90deg, rgba(0, 255, 153, 0.1), transparent);
        }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        
        .footer { text-align: center; margin-top: 60px; color: #9aa3ad; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; }

        @media (max-width: 1200px) {
            .kpi-container { grid-template-columns: repeat(3, 1fr); }
        }
        @media (max-width: 900px) {
            body { margin: 16px; }
            .header { padding: 24px 16px; margin-bottom: 24px; }
            .header h1 { font-size: 1.8em; letter-spacing: 1px; }
            .section-title { font-size: 1.2em; margin: 30px 0 16px 0; }
            .grid-2 { grid-template-columns: 1fr; gap: 16px; }
            .kpi-container { grid-template-columns: repeat(2, 1fr); gap: 12px; }
            .kpi-val { font-size: 24px; }
            .card { padding: 16px; }
            table { font-size: 12px; }
            th, td { padding: 10px; }
            .footer { margin-top: 36px; letter-spacing: 1px; }
        }
        @media (max-width: 600px) {
            .kpi-container { grid-template-columns: 1fr; }
        }
    """

def get_button_styles():
    """获取按钮样式"""
    return """
        .btn-group { 
            position: fixed; 
            top: 50%; 
            right: 0; 
            transform: translateY(-50%);
            z-index: 1000; 
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .btn { 
            padding: 12px 4px; 
            border: none; 
            border-radius: 12px 0 0 12px; 
            cursor: pointer; 
            font-weight: bold; 
            margin: 0; 
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55); 
            
            /* 竖排文字核心样式 */
            writing-mode: vertical-rl;
            text-orientation: upright;
            letter-spacing: 2px;
            font-size: 12px;
            
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 35px;
            box-shadow: -4px 5px 15px rgba(0,0,0,0.3);
        }
        .btn:hover { transform: translateX(-5px); min-width: 45px; }
        .btn-print { background: rgba(0, 255, 153, 0.9); color: #000; box-shadow: 0 5px 15px rgba(0, 255, 153, 0.3); }
        .btn-print:hover { box-shadow: -6px 6px 20px #00FF99; }
        
        .btn-shot { background: rgba(0, 204, 255, 0.9); color: #000; box-shadow: 0 5px 15px rgba(0, 204, 255, 0.3); }
        .btn-shot:hover { box-shadow: -6px 6px 20px #00CCFF; }
        
        .btn-privacy { background: rgba(255, 0, 204, 0.9); color: #fff; box-shadow: 0 5px 15px rgba(255, 0, 204, 0.3); }
        .btn-privacy:hover { box-shadow: -6px 6px 20px #FF00CC; }
        .btn:focus-visible {
            outline: 3px solid #ffffff;
            outline-offset: 2px;
            box-shadow: 0 0 0 3px rgba(0, 204, 255, 0.4);
        }

        @media (max-width: 900px) {
            .btn-group {
                top: auto;
                right: 12px;
                left: 12px;
                bottom: calc(12px + var(--safe-bottom));
                transform: none;
                z-index: 1100;
                flex-direction: row;
                gap: 8px;
            }
            .btn {
                min-width: 0;
                flex: 1;
                border-radius: 10px;
                padding: 10px 12px;
                writing-mode: horizontal-tb;
                text-orientation: mixed;
                letter-spacing: 0;
                font-size: 13px;
            }
            .btn:hover { transform: none; min-width: 0; }
        }

        /* 截图辅助：截图期间禁用动画 */
        .no-anim, .no-anim * { animation: none !important; transition: none !important; opacity: 1 !important; transform: none !important; }
    """

def get_card_styles():
    """获取卡片和KPI盒子样式"""
    return """
        /* --- 玻璃拟态卡片 --- */
        .card { 
            background: rgba(45, 45, 45, 0.4); 
            backdrop-filter: blur(10px);
            padding: 30px; border-radius: 16px; 
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
            opacity: 0; animation: slideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }
        .card:hover { 
            transform: translateY(-10px) scale(1.02); 
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
            border-color: rgba(0, 255, 153, 0.3);
            background: rgba(50, 50, 50, 0.6);
        }
        .card h3 { color: #00CCFF; margin-top: 0; border-bottom: 2px solid rgba(255,255,255,0.05); padding-bottom: 15px; font-size: 1.3em; }
        
        /* --- KPI 霓虹盒子 --- */
        .kpi-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; margin-bottom: 40px; }
        .kpi-box { 
            background: rgba(40, 40, 40, 0.6); padding: 25px; border-radius: 12px; text-align: center; 
            border: 1px solid rgba(255,255,255,0.05); position: relative; overflow: hidden;
            transition: 0.3s;
            opacity: 0; animation: slideUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }
        .kpi-box:hover { background: rgba(60, 60, 60, 0.8); transform: translateY(-5px); box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        .kpi-box::after {
            content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 3px;
            background: linear-gradient(90deg, #00FF99, #00CCFF, #FF00CC);
            transform: scaleX(0); transform-origin: left; transition: transform 0.4s ease;
        }
        .kpi-box:hover::after { transform: scaleX(1); }

        .kpi-val { font-size: 32px; font-weight: 800; margin: 10px 0; text-shadow: 0 0 10px rgba(0,0,0,0.3); color: var(--kpi-color, inherit); }
        .kpi-lbl { color: #aaa; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }

        /* --- 每日峰值模块 --- */
        .daily-section-title { margin-top: 30px; }
        .daily-highlow-row { display: flex; gap: 30px; justify-content: space-around; }
        .daily-col { text-align: center; }
        .daily-col-hot { color: #ff5e62; }
        .daily-col-profit { color: #00FF99; }
        .daily-col-cool { color: #00CCFF; }
        .daily-label { font-size: 12px; color: #aaa; margin-bottom: 5px; }
        .daily-day { font-size: 20px; font-weight: bold; margin-bottom: 5px; }
        .daily-value { font-size: 28px; font-weight: 800; }
        .daily-unit { font-size: 14px; }
        .daily-note { font-size: 12px; color: #888; margin-top: 5px; }
        .daily-divider { width: 1px; background: rgba(255,255,255,0.1); }

        /* --- 成本透视模块 --- */
        .cost-grid { margin-top: 25px; }
        .cost-metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; font-size: 13px; }
        .cost-metric-card { padding: 15px; border-radius: 8px; }
        .cost-metric-card-danger { background: rgba(255,51,51,0.1); }
        .cost-metric-card-warn { background: rgba(255,255,51,0.1); }
        .cost-metric-card-success { background: rgba(0,255,153,0.1); }
        .cost-metric-title-danger { color: #FF3333; }
        .cost-metric-title-warn { color: #FFFF33; }
        .cost-metric-title-success { color: #00FF99; }
        .cost-metric-text { margin: 8px 0 0 0; color: #aaa; line-height: 1.5; }
        .cost-metric-value { font-size: 24px; font-weight: bold; }
        .cost-metric-value-good { color: #00FF99; }
        .cost-metric-value-mid { color: #FFFF33; }
        .cost-metric-value-high { color: #FF3333; }

        /* --- 预警与建议模块 --- */
        .warning-title { color:#FF3333; margin-top:30px; }
        .warning-subtitle { color:#FF3333; margin-top:20px; }
        .warning-card { border: 1px solid #FF3333; }
        .warning-card-strong { border: 1px solid #FF3333; box-shadow: 0 0 20px rgba(255, 51, 51, 0.2); }
        .warning-loss-value { color:#FF3333; font-weight:bold; }
        .warning-ok { color:#00FF99; margin-top:20px; }
        .suggestion-card { margin-top: 30px; background: linear-gradient(to right, #2d2d2d, #3d3d3d); }
        .suggestion-title { color:#FF00CC; }
        .suggestion-list { line-height: 2.2; color: #ddd; list-style-type: none; padding: 0 20px; }
        .suggestion-item { margin-bottom: 12px; }

        @media (max-width: 900px) {
            .daily-highlow-row { flex-direction: column; gap: 14px; }
            .daily-divider { width: 100%; height: 1px; }
            .cost-metric-grid { grid-template-columns: 1fr; gap: 12px; }
        }
    """

def get_table_styles():
    """获取表格样式"""
    return """
        /* --- 表格样式 --- */
        table { width: 100%; border-collapse: separate; border-spacing: 0 8px; font-size: 14px; }
        th { color: #00FF99; padding: 15px; text-align: left; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.1); }
        td { padding: 15px; background: rgba(255,255,255,0.03); transition: 0.2s; }
        tr td:first-child { border-top-left-radius: 8px; border-bottom-left-radius: 8px; }
        tr td:last-child { border-top-right-radius: 8px; border-bottom-right-radius: 8px; }
        tr:hover td { background: rgba(0, 204, 255, 0.15); color: #fff; transform: scale(1.01); }
        
        .badge { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .badge-hot { background: linear-gradient(45deg, #ff4757, #ff6b81); color: white; }
        .badge-cool { background: linear-gradient(45deg, #2ed573, #7bed9f); color: black; }
        .badge-warn { background: linear-gradient(45deg, #ffa502, #ffc048); color: black; }
        
        .sensitive-data { transition: filter 0.5s ease; }
        .privacy-active .sensitive-data { filter: blur(12px) !important; pointer-events: none; user-select: none; }
        .blurred-text { filter: blur(12px); pointer-events: none; }
        
        /* 数据条样式 */
        .bar-container { display: flex; align-items: center; gap: 8px; }
        .bar-bg { flex-grow: 1; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden; min-width: 60px; }
        .bar-bg-sm { min-width: 40px; }
        .bar-bg-xs { min-width: 30px; }
        .data-bar {
            height: 100%;
            border-radius: 3px;
            width: 0;
            background: var(--bar-gradient, linear-gradient(90deg, #00C9FF, #92FE9D));
        }
        .data-bar.animate { animation: expandWidth 1s ease-out forwards; }
        .bar-cat-weight { --bar-gradient: linear-gradient(90deg, #00C9FF, #92FE9D); }
        .bar-cat-profit { --bar-gradient: linear-gradient(90deg, #ff9a9e, #fecfef); }
        .bar-dest-weight { --bar-gradient: linear-gradient(90deg, #F9D423, #FF4E50); }
        .bar-dest-count { --bar-gradient: linear-gradient(90deg, #89f7fe, #66a6ff); }
        .bar-week-weight { --bar-gradient: linear-gradient(90deg, #A8CABA, #5D4157); }
        .bar-vehicle-weight { --bar-gradient: linear-gradient(90deg, #ff9966, #ff5e62); }
        @keyframes expandWidth { from { width: 0; } to { width: var(--width); } }
    """

def get_animation_styles():
    """获取动画关键帧"""
    return """
        @keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        
        .kpi-box:nth-child(1) { animation-delay: 0.1s; }
        .kpi-box:nth-child(2) { animation-delay: 0.2s; }
        .kpi-box:nth-child(3) { animation-delay: 0.3s; }
        .kpi-box:nth-child(4) { animation-delay: 0.4s; }
        .kpi-box:nth-child(5) { animation-delay: 0.5s; }
        .card:nth-child(odd) { animation-delay: 0.6s; }
        .card:nth-child(even) { animation-delay: 0.7s; }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        }
    """

def get_print_styles():
    """获取打印样式"""
    return """
        @media print {
            body { background: white; color: black; margin: 0; }
            .card, .kpi-box { box-shadow: none; border: 1px solid #ddd; background: #fff; color: black; break-inside: avoid; }
            .header { background: #eee; color: black; box-shadow: none; border: none; }
            .header h1 { text-shadow: none; animation: none; color: #000; }
            .header::before { display: none; }
            .kpi-val, .card h3 { color: #000 !important; text-shadow: none; }
            th { color: #000; border-bottom: 2px solid #000; }
            td { background: #fff !important; border-bottom: 1px solid #eee; }
            .btn-group { display: none; }
        }
    """
