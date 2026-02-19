# -*- coding: utf-8 -*-
"""仪表盘 HTML 构建器。"""

import plotly.io as pio

from .dashboard_styles import get_all_dashboard_styles
from .scripts import (
    get_base_scripts,
    get_particle_animation_js,
    get_counter_animation_js,
    get_stagger_animation_js,
)


def get_dashboard_extra_styles():
    """获取仪表盘专属样式（霓虹边框等）。"""
    return """
        /* 霓虹边框效果 */
        .neon-border {
            box-shadow: 0 0 20px rgba(0, 255, 153, 0.3),
                        0 0 40px rgba(0, 204, 255, 0.2),
                        0 0 60px rgba(255, 0, 204, 0.1);
            border: 1px solid rgba(0, 255, 153, 0.2);
        }

        /* 仪表盘容器样式 */
        .dashboard-container {
            padding: 20px;
            min-height: 100vh;
        }

        /* 仪表盘标题 */
        .dashboard-header {
            text-align: center;
            padding: 30px 0;
            margin-bottom: 20px;
        }

        .dashboard-header h1 {
            font-size: 2.5em;
            color: #00FF99;
            text-shadow: 0 0 20px rgba(0, 255, 153, 0.5),
                         0 0 40px rgba(0, 255, 153, 0.3);
            letter-spacing: 4px;
            margin: 0;
        }

        .dashboard-header .subtitle {
            color: #888;
            font-size: 1em;
            margin-top: 10px;
            letter-spacing: 2px;
        }
    """


def get_save_long_image_script():
    """获取保存长图脚本。"""
    return """
        // 保存长图功能（使用 dom-to-image 替代 html2canvas）
        function saveLongImage() {
            const saveBtn = document.getElementById('saveBtn');
            const originalText = saveBtn.innerHTML;

            saveBtn.innerHTML = '⏳ 生成中...';
            saveBtn.style.background = '#666';

            // 滚动到顶部防止截图错位
            window.scrollTo(0, 0);

            const filterNode = (node) => {
                if (node.classList && node.classList.contains('btn-group')) return false;
                if (node.id === 'loading-overlay') return false;
                if (node.tagName === 'CANVAS' && node.style.position === 'fixed') return false;
                return true;
            };

            setTimeout(() => {
                const scale = window.devicePixelRatio || 1;

                domtoimage.toPng(document.body, {
                    filter: filterNode,
                    bgcolor: '#1e1e2f',
                    quality: 1.0,
                    width: document.body.scrollWidth * scale,
                    height: document.body.scrollHeight * scale,
                    style: {
                        transform: 'scale(' + scale + ')',
                        transformOrigin: 'top left',
                        width: document.body.scrollWidth + 'px',
                        height: document.body.scrollHeight + 'px'
                    }
                })
                .then(function (dataUrl) {
                    const link = document.createElement('a');
                    const cleanTitle = document.title.replace(/[\\/:*?"<>|]/g, '_');
                    link.download = cleanTitle + '_长图.png';
                    link.href = dataUrl;
                    link.click();

                    saveBtn.innerHTML = '✅ 已保存';
                    saveBtn.style.background = '#00FF99';
                    saveBtn.style.color = '#000';

                    setTimeout(() => {
                        saveBtn.innerHTML = originalText;
                        saveBtn.style.background = '';
                        saveBtn.style.color = '';
                    }, 2000);
                })
                .catch(function (error) {
                    console.error('DOM-to-Image Error:', error);
                    saveBtn.innerHTML = '❌ 失败';
                    alert('保存失败: ' + error.message + '\\n如果图片不完整，可能是页面过长或内存不足。');

                    setTimeout(() => {
                        saveBtn.innerHTML = originalText;
                        saveBtn.style.background = '';
                        saveBtn.style.color = '';
                    }, 3000);
                });
            }, 500);
        }
    """


def get_dashboard_style_bundle():
    """获取仪表盘样式合集。"""
    return f"""
        {get_all_dashboard_styles()}
        {get_dashboard_extra_styles()}
    """


def get_dashboard_script_bundle():
    """获取仪表盘脚本合集。"""
    return f"""
        {get_base_scripts()}
        {get_particle_animation_js()}
        {get_counter_animation_js()}
        {get_stagger_animation_js()}
        {get_save_long_image_script()}
    """


def build_dashboard_html(fig, title, dest_list=None, generate_time=None):
    """构建完整的仪表盘 HTML。"""

    plot_html = pio.to_html(
        fig,
        include_plotlyjs="cdn",
        full_html=False,
        config={
            "displayModeBar": False,
            "displaylogo": False,
            "locale": "zh-CN",
            "staticPlot": False,
            "scrollZoom": False,
            "responsive": True,
        },
    )

    styles = get_dashboard_style_bundle()
    scripts = get_dashboard_script_bundle()

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>西关打包站 - {title} 运营仪表盘</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dom-to-image/2.6.0/dom-to-image.min.js"></script>
    <style>
        /* DASHBOARD_DYNAMIC_STYLES_START */
        {styles}
        /* DASHBOARD_DYNAMIC_STYLES_END */
    </style>
</head>
<body>
    <div id="loading-overlay" class="active">
        <div class="spinner"></div>
        <div class="loading-text">系统加载中...</div>
    </div>

    <div class="btn-group" data-html2canvas-ignore="true">
        <button type="button" id="saveBtn" class="btn btn-shot" onclick="saveLongImage()" aria-label="保存长图" title="保存长图">📷 保存长图</button>
        <button type="button" id="profitBtn" class="btn btn-privacy" onclick="togglePrivacy()" aria-label="切换利润显示" title="切换利润显示">🙈 隐藏利润</button>
        <button type="button" id="topBtn" class="btn btn-top" onclick="scrollToTop()" aria-label="回到顶部" title="回到顶部">⬆️ 回到顶部</button>
    </div>

    <div id="dashboard-header">
        <h1 class="cyber-title">西关打包站 {title} 实时运营仪表盘</h1>
        <div id="real-time-clock">--:--:--</div>
    </div>

    <div class="dashboard-container">
        {plot_html}
    </div>

    <div class="dashboard-footer">
        <div class="footer-info">系统生成: <b>PackInsight 智能分析系统</b> v9.0 | 数据更新: <span class="footer-tech">{generate_time}</span></div>
        <div class="footer-tech">核心驱动: PANDAS & PLOTLY | 专为西关打包站定制开发</div>
    </div>

    <script>
        /* DASHBOARD_DYNAMIC_SCRIPTS_START */
        {scripts}
        /* DASHBOARD_DYNAMIC_SCRIPTS_END */
    </script>
</body>
</html>"""

    return html

