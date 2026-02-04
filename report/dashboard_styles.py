# -*- coding: utf-8 -*-
"""
仪表板专属样式 (CSS)
从原始文件恢复完整的赛博朋克风格样式和动画效果
"""


def get_dashboard_base_styles():
    """获取仪表板基础样式"""
    return """
        /* --- 全局酷炫样式 --- */
        body {
            background: radial-gradient(circle at center, #1e1e2f 0%, #0f0f1a 100%) !important;
            color: #e0e0e0 !important;
            font-family: 'MSGothic', 'Microsoft YaHei', sans-serif;
            margin: 0; overflow-x: hidden;
        }
        
        /* 背景网格线 */
        body::before {
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            background-size: 100% 2px, 3px 100%;
            pointer-events: none; z-index: -1;
        }
        
        /* 粒子背景 Canvas */
        #particle-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }
        .plotly-graph-div, #dashboard-header, .btn-group, #loading-overlay {
            position: relative;
            z-index: 1;
        }
        
        /* Plotly 容器特效：添加隐形式 Glassmorphism 背景 */
        .plotly-graph-div {
            margin-top: 20px;
            animation: zoomInEntry 1s ease-out;
            filter: drop-shadow(0 0 20px rgba(0,0,0,0.5));
            background: rgba(255, 255, 255, 0.05) !important; /* 5% 透明度的隐形背景块 */
            border-radius: 12px;
            backdrop-filter: blur(2px);
            border: 1px solid rgba(255, 255, 255, 0.08); /* 极细微的边框 */
        }
        @keyframes zoomInEntry { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

        /* 注入的 Header 样式 */
        #dashboard-header {
            text-align: center; padding: 25px;
            background: rgba(30, 30, 35, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0, 255, 204, 0.3);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            position: relative; overflow: hidden;
        }
        #dashboard-header::after {
            content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, #00FF99, #00CCFF, transparent);
            animation: scanline 3s linear infinite;
        }
        @keyframes scanline { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
        
        h1.cyber-title { 
            font-size: 2.8em; margin: 0; color: #fff; text-transform: uppercase; letter-spacing: 4px;
            text-shadow: 2px 2px 0px #FF00CC, -2px -2px 0px #00CCFF; 
        }
        
        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 10px; background: #0f0c29; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; border: 1px solid #444; }
        ::-webkit-scrollbar-thumb:hover { background: #00FF99; }
    """


def get_dashboard_button_styles():
    """获取仪表板侧边栏按钮样式"""
    return """
        /* --- 侧边栏按钮组 (复用报告页风格) --- */
        .btn-group { 
            position: fixed; top: 50%; right: 0; transform: translateY(-50%); z-index: 10000;
            display: flex; flex-direction: column; gap: 15px;
        }
        .btn { 
            padding: 15px 5px; border: none; border-radius: 12px 0 0 12px; 
            cursor: pointer; font-weight: bold; margin: 0; 
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55); 
            writing-mode: vertical-rl; text-orientation: upright; 
            letter-spacing: 2px; font-size: 13px; color: #000;
            display: flex; align-items: center; justify-content: center;
            min-width: 35px; box-shadow: -4px 5px 15px rgba(0,0,0,0.5);
            font-family: "Microsoft YaHei", sans-serif;
        }
        .btn:hover { transform: translateX(-5px); min-width: 45px; }
        
        .btn-shot { background: rgba(0, 204, 255, 0.95); color: #000; box-shadow: 0 0 15px rgba(0, 204, 255, 0.4); }
        .btn-shot:hover { box-shadow: -6px 6px 20px #00CCFF; }
        
        .btn-privacy { background: rgba(255, 0, 204, 0.95); color: #fff; box-shadow: 0 0 15px rgba(255, 0, 204, 0.4); }
        .btn-privacy:hover { box-shadow: -6px 6px 20px #FF00CC; }
        
        .blurred-sensitive { filter: blur(15px) !important; transition: filter 0.5s ease; }
        text { transition: filter 0.5s ease; }
    """


def get_dashboard_animation_styles():
    """获取仪表板动画样式"""
    return """
        /* ========== 🎬 渐入级联动画 (Staggered Fade-in) ========== */
        /* 动画类 - 只在JS添加后才生效，避免内容不显示 */
        .stagger-animate {
            animation: staggerFadeIn 0.8s ease-out forwards !important;
            opacity: 1 !important; /* 确保动画结束后可见 */
        }
        /* 动画完成后的最终状态 */
        .stagger-complete {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        @keyframes staggerFadeIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        

        /* ========== 💡 霓虹灯辉光脉冲 (Neon Pulse) ========== */
        .neon-pulse {
            animation: neonPulse 2.5s ease-in-out infinite alternate;
        }
        @keyframes neonPulse {
            0% {
                text-shadow: 
                    0 0 5px currentColor,
                    0 0 10px currentColor,
                    0 0 20px currentColor;
                filter: brightness(1);
            }
            50% {
                text-shadow: 
                    0 0 10px currentColor,
                    0 0 25px currentColor,
                    0 0 40px currentColor,
                    0 0 60px currentColor;
                filter: brightness(1.3);
            }
            100% {
                text-shadow: 
                    0 0 5px currentColor,
                    0 0 15px currentColor,
                    0 0 25px currentColor;
                filter: brightness(1.1);
            }
        }
        
        /* 标题专属霓虹效果（双色呼吸） */
        h1.cyber-title {
            animation: titleNeonPulse 3s ease-in-out infinite;
        }
        @keyframes titleNeonPulse {
            0%, 100% {
                text-shadow: 
                    2px 2px 0px #FF00CC, 
                    -2px -2px 0px #00CCFF,
                    0 0 10px #FF00CC,
                    0 0 20px #00CCFF;
            }
            50% {
                text-shadow: 
                    2px 2px 0px #FF00CC, 
                    -2px -2px 0px #00CCFF,
                    0 0 25px #FF00CC,
                    0 0 50px #00CCFF,
                    0 0 80px rgba(255,0,204,0.4),
                    0 0 100px rgba(0,204,255,0.3);
            }
        }
        
        /* KPI 数值霓虹呼吸灯 */
        .kpi-neon {
            animation: kpiNeonPulse 2s ease-in-out infinite alternate;
        }
        @keyframes kpiNeonPulse {
            0% {
                filter: drop-shadow(0 0 5px currentColor);
            }
            100% {
                filter: drop-shadow(0 0 15px currentColor) drop-shadow(0 0 30px currentColor);
            }
        }
        
        /* 边框霓虹效果 */
        .neon-border {
            box-shadow: 
                0 0 5px rgba(0, 255, 153, 0.3),
                inset 0 0 5px rgba(0, 255, 153, 0.1);
            animation: borderNeonPulse 3s ease-in-out infinite;
        }
        @keyframes borderNeonPulse {
            0%, 100% {
                box-shadow: 
                    0 0 5px rgba(0, 255, 153, 0.3),
                    inset 0 0 5px rgba(0, 255, 153, 0.1);
            }
            50% {
                box-shadow: 
                    0 0 15px rgba(0, 255, 153, 0.5),
                    0 0 30px rgba(0, 204, 255, 0.3),
                    inset 0 0 10px rgba(0, 255, 153, 0.2);
            }
        }
        
        /* Loading 遮罩层 */
        #loading-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); z-index: 20000;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            backdrop-filter: blur(5px);
            opacity: 0; transition: opacity 0.3s; pointer-events: none;
        }
        #loading-overlay.active { opacity: 1; pointer-events: all; }
        
        .spinner {
            width: 60px; height: 60px; 
            border: 6px solid #333; border-top: 6px solid #00FF99; 
            border-radius: 50%; animation: spin 1s linear infinite; 
            margin-bottom: 20px;
            box-shadow: 0 0 15px #00FF99;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        
        /* 截图专用清理模式：去除所有导致模糊的滤镜和动画 */
        .snapshot-mode, .snapshot-mode * {
            animation: none !important;
            transition: none !important;
            filter: none !important; /* 关键：去除 drop-shadow 滤镜 */
        }
        /* 保持文字清晰度 */
        .snapshot-mode body {
            -webkit-font-smoothing: antialiased;
        }
    """


def get_all_dashboard_styles():
    """获取所有仪表板样式"""
    return (
        get_dashboard_base_styles() +
        get_dashboard_button_styles() +
        get_dashboard_animation_styles()
    )
