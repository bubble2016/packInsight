# -*- coding: utf-8 -*-
"""仪表盘专属样式（CSS）。"""


def get_dashboard_base_styles():
    """获取仪表盘基础样式。"""
    return """
        :root { --safe-bottom: env(safe-area-inset-bottom, 0px); }
        /* 全局赛博风格 */
        body {
            background: radial-gradient(circle at center, #1e1e2f 0%, #0f0f1a 100%) !important;
            color: #e0e0e0 !important;
            font-family: 'MSGothic', 'Roboto', 'Microsoft YaHei', sans-serif;
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

        /* Plotly 容器：性能优化版（移除高成本模糊） */
        .plotly-graph-div {
            margin-top: 20px;
            animation: zoomInEntry 1s ease-out;
            /* export-ignore: 用 box-shadow 替代 drop-shadow */
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            background: rgba(30, 32, 40, 0.7) !important;
            border-radius: 12px;
            /* backdrop-filter: blur(2px); */
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        @keyframes zoomInEntry { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

        /* Header 样式 */
        #dashboard-header {
            text-align: center; padding: 25px;
            background: rgba(20, 20, 25, 0.95);
            /* backdrop-filter: blur(10px); */
            border-bottom: 1px solid rgba(0, 255, 204, 0.3);
            box-shadow: 0 5px 20px rgba(0,0,0,0.5);
            position: relative; overflow: hidden;
        }
        #dashboard-header::after {
            content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, #00FF99, #00CCFF, transparent);
            animation: scanline 3s linear infinite;
        }
        @keyframes scanline { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

        h1.cyber-title {
            font-size: 2.8em; margin: 0; color: #fff; text-transform: uppercase; letter-spacing: 4px;
            text-shadow: 2px 2px 0px #FF00CC, -2px -2px 0px #00CCFF;
        }

        /* 滚动条 */
        ::-webkit-scrollbar { width: 10px; background: #0f0c29; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; border: 1px solid #444; }
        ::-webkit-scrollbar-thumb:hover { background: #00FF99; }

        /* 实时时钟 */
        #real-time-clock {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 1.1em;
            color: #00CCFF;
            text-shadow: 0 0 10px rgba(0, 204, 255, 0.5);
            margin-top: 10px;
            letter-spacing: 2px;
            opacity: 0.9;
        }

        /* 页脚 */
        .dashboard-footer {
            text-align: center;
            padding: 40px 0 60px 0;
            color: rgba(255,255,255,0.55);
            font-size: 0.85em;
            letter-spacing: 1px;
            text-shadow: 0 0 5px rgba(0,0,0,0.5);
            margin-top: 50px;
            border-top: 1px solid rgba(255,255,255,0.05);
            background: linear-gradient(to top, rgba(0,0,0,0.5), transparent);
        }
        .footer-info { margin-bottom: 8px; font-family: 'MSGothic', 'Roboto', 'Microsoft YaHei', sans-serif; letter-spacing: 1px; }
        .footer-tech { font-family: 'MSGothic', 'Roboto', 'Microsoft YaHei', sans-serif; color: rgba(0, 255, 153, 0.75); font-weight: bold; letter-spacing: 1px; }

        @media (max-width: 900px) {
            h1.cyber-title { font-size: 1.5em; letter-spacing: 1px; }
            #dashboard-header { padding: 18px 12px; }
            #real-time-clock { font-size: 0.95em; letter-spacing: 1px; }
            .dashboard-container { padding: 12px; }
            .plotly-graph-div { margin-top: 12px; border-radius: 8px; }
            .dashboard-footer { padding: 24px 12px 92px 12px; }
        }"""


def get_dashboard_button_styles():
    """获取仪表盘侧边按钮样式。"""
    return """
        /* 侧边栏按钮组 */
        .btn-group {
            position: fixed; top: 50%; right: 0; transform: translateY(-50%); z-index: 10000;
            display: flex; flex-direction: column; gap: 20px;
        }
        .btn {
            width: 36px;
            height: 100px;
            border: none;
            border-radius: 10px 0 0 10px;
            cursor: pointer;
            font-weight: bold;
            margin: 0;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            writing-mode: vertical-rl;
            text-orientation: upright;
            letter-spacing: 2px;
            font-size: 12px;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: -3px 3px 10px rgba(0,0,0,0.3);
            font-family: "Microsoft YaHei", sans-serif;
            text-shadow: 0 1px 1px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }

        /* 悬停效果 */
        .btn:hover {
            width: 46px;
            padding-right: 3px;
            filter: brightness(1.1);
        }

        /* 光泽层 */
        .btn::after {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(90deg, rgba(255,255,255,0.1), transparent);
            pointer-events: none;
        }

        /* 保存按钮：深蓝渐变 */
        .btn-shot {
            background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
            box-shadow: 0 4px 15px rgba(0, 114, 255, 0.4);
        }
        .btn-shot:hover { box-shadow: -6px 6px 20px rgba(0, 198, 255, 0.6); }

        /* 隐私按钮：紫粉渐变 */
        .btn-privacy {
            background: linear-gradient(135deg, #FF00CC 0%, #333399 100%);
            box-shadow: 0 4px 15px rgba(255, 0, 204, 0.4);
        }
        .btn-privacy:hover { box-shadow: -6px 6px 20px rgba(255, 0, 204, 0.6); }

        /* 顶部按钮：黄绿渐变 */
        .btn-top {
            background: linear-gradient(135deg, #FFE000 0%, #799F0C 100%);
            color: #000;
            text-shadow: none;
            box-shadow: 0 4px 15px rgba(255, 224, 0, 0.4);
        }
        .btn-top:hover { box-shadow: -6px 6px 20px rgba(255, 224, 0, 0.6); }
        .btn:focus-visible {
            outline: 3px solid #ffffff;
            outline-offset: 2px;
            box-shadow: 0 0 0 3px rgba(0, 204, 255, 0.45);
        }

        @media (max-width: 900px) {
            .btn-group {
                top: auto;
                right: 12px;
                left: 12px;
                bottom: calc(12px + var(--safe-bottom));
                transform: none;
                z-index: 10001;
                flex-direction: row;
                gap: 8px;
            }
            .btn {
                width: auto;
                height: auto;
                min-height: 44px;
                flex: 1;
                border-radius: 10px;
                writing-mode: horizontal-tb;
                text-orientation: mixed;
                letter-spacing: 0;
                padding: 8px 10px;
                font-size: 13px;
            }
            .btn:hover { width: auto; padding-right: 10px; filter: brightness(1.05); }
        }

        .blurred-sensitive { filter: blur(15px) !important; transition: filter 0.5s ease; }
        .privacy-active .sensitive-data, .privacy-active .blurred-sensitive { filter: blur(15px) !important; pointer-events: none; user-select: none; }
        text { transition: filter 0.5s ease; }
    """


def get_dashboard_animation_styles():
    """获取仪表盘动画样式。"""
    return """
        /* 渐入级联动画 */
        .stagger-animate {
            animation: staggerFadeIn 0.8s ease-out forwards !important;
            opacity: 1 !important;
        }
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

        /* 霓虹脉冲 */
        .neon-pulse {
            animation: neonPulse 3.2s ease-in-out infinite;
        }
        @keyframes neonPulse {
            0%, 100% {
                text-shadow:
                    0 0 2px rgba(255, 255, 255, 0.12),
                    0 0 6px currentColor;
                filter: brightness(1);
                opacity: 0.95;
            }
            50% {
                text-shadow:
                    0 0 3px rgba(255, 255, 255, 0.16),
                    0 0 9px currentColor;
                filter: brightness(1.05);
                opacity: 1;
            }
        }

        /* 标题专属霓虹效果 */
        h1.cyber-title {
            animation: titleNeonPulse 4.5s ease-in-out infinite;
        }
        @keyframes titleNeonPulse {
            0%, 100% {
                text-shadow:
                    2px 2px 0px #FF00CC,
                    -2px -2px 0px #00CCFF,
                    0 0 6px rgba(255, 0, 204, 0.45),
                    0 0 10px rgba(0, 204, 255, 0.4);
            }
            50% {
                text-shadow:
                    2px 2px 0px #FF00CC,
                    -2px -2px 0px #00CCFF,
                    0 0 9px rgba(255, 0, 204, 0.55),
                    0 0 15px rgba(0, 204, 255, 0.5);
            }
        }

        /* KPI 霓虹脉冲 */
        .kpi-neon {
            animation: kpiNeonPulse 2.8s ease-in-out infinite;
        }
        @keyframes kpiNeonPulse {
            0%, 100% { filter: drop-shadow(0 0 2px currentColor); }
            50% { filter: drop-shadow(0 0 6px currentColor); }
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
        .loading-text {
            color: #00FF99;
            font-family: 'Consolas', monospace;
            font-size: 1.2em;
            letter-spacing: 3px;
            animation: textBlink 1.5s infinite alternate;
        }
        @keyframes textBlink { 0% { opacity: 0.5; } 100% { opacity: 1; text-shadow: 0 0 10px #00FF99; } }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        /* 截图清理模式：去除影响清晰度的滤镜和动画 */
        .snapshot-mode, .snapshot-mode * {
            animation: none !important;
            transition: none !important;
            filter: none !important;
        }
        .snapshot-mode body {
            -webkit-font-smoothing: antialiased;
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
            body > canvas {
                display: none !important;
            }
        }
    """


def get_all_dashboard_styles():
    """获取全部仪表盘样式。"""
    return (
        get_dashboard_base_styles()
        + get_dashboard_button_styles()
        + get_dashboard_animation_styles()
    )
