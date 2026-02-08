# -*- coding: utf-8 -*-
"""
仪表板 HTML 构建器
将 Plotly 图表包装成带有动画效果的完整仪表板 HTML
"""
import plotly.io as pio

# 使用专门的仪表板样式，而非通用报告样式
from .dashboard_styles import get_all_dashboard_styles
from .scripts import (
    get_base_scripts, get_particle_animation_js,
    get_counter_animation_js, get_stagger_animation_js
)


def get_dashboard_extra_styles():
    """获取仪表板专属样式（霓虹边框等）"""
    return """
        /* 霓虹边框效果 */
        .neon-border {
            box-shadow: 0 0 20px rgba(0, 255, 153, 0.3),
                        0 0 40px rgba(0, 204, 255, 0.2),
                        0 0 60px rgba(255, 0, 204, 0.1);
            border: 1px solid rgba(0, 255, 153, 0.2);
        }
        
        /* 仪表板容器样式 */
        .dashboard-container {
            padding: 20px;
            min-height: 100vh;
        }
        
        /* 仪表板标题 */
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


def build_dashboard_html(fig, title, dest_list=None, generate_time=None):
    """
    构建完整的仪表板 HTML
    
    Args:
        fig: Plotly Figure 对象
        title: 仪表板标题（如 "[1月]" 或 "[多月对比]"）
        dest_list: 目的地列表（用于隐私保护功能）
        generate_time: 生成时间字符串
    
    Returns:
        str: 完整的 HTML 字符串
    """

    # 生成 Plotly 图表 HTML（不含完整页面结构，隐藏工具栏）
    plot_html = pio.to_html(
        fig,
        include_plotlyjs='cdn',
        full_html=False,
        config={
            'displayModeBar': False,  # 隐藏工具栏
            'displaylogo': False,
            'locale': 'zh-CN',
            'staticPlot': False,  # 保持交互
            'scrollZoom': False   # 禁用滚轮缩放
        }
    )
    
    # 组装样式（使用仪表板专属样式）
    styles = f"""
        {get_all_dashboard_styles()}
        {get_dashboard_extra_styles()}
    """
    
    # 组装脚本
    scripts = f"""
        {get_base_scripts()}
        {get_particle_animation_js()}
        {get_counter_animation_js()}
        {get_stagger_animation_js()}
    """
    
    # 隐藏利润功能脚本 (使用 scripts.py 中的统一逻辑) + 保存长图功能
    # 注意：这里只保留保存长图的特定逻辑，隐私切换已统一
    hide_profit_script = """
        // 保存长图功能（使用 dom-to-image 替代 html2canvas）
        function saveLongImage() {
            const btnGroup = document.querySelector('.btn-group');
            const saveBtn = document.getElementById('saveBtn');
            const originalText = saveBtn.innerHTML;
            
            // 显示进度
            saveBtn.innerHTML = '⏳...';
            saveBtn.style.background = '#666';
            
            // 滚动到顶部防止错位
            window.scrollTo(0, 0);

            // 过滤函数
            const filterNode = (node) => {
                if (node.classList && node.classList.contains('btn-group')) return false;
                if (node.id === 'loading-overlay') return false;
                if (node.tagName === 'CANVAS' && node.style.position === 'fixed') return false;
                return true;
            };

            setTimeout(() => {
                // 获取设备像素比 (Retina 屏幕通常为 2 或更高)
                const scale = window.devicePixelRatio || 1;
                
                // dom-to-image 默认导出 CSS 像素尺寸，需要手动放大以匹配屏幕清晰度
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
                    const cleanTitle = document.title.replace(/[\\\\/:*?"<>|]/g, '_');
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
                    alert('保存失败: ' + error.message + '\\n如果图片不完整，可能因为内存不足。');
                    
                    setTimeout(() => {
                        saveBtn.innerHTML = originalText;
                        saveBtn.style.background = '';
                    }, 3000);
                });
            }, 500);
        }
    """
    
    # 构建完整 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>西关打包站 - {title} 运营仪表板</title>
    <!-- 更换为 dom-to-image 库，解决 html2canvas 的 canvas 报错问题 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dom-to-image/2.6.0/dom-to-image.min.js"></script>
    <style>
        {styles}
    </style>
</head>
<body>
    <!-- Loading Overlay -->
    <div id="loading-overlay" class="active">
        <div class="spinner"></div>
        <div class="loading-text">系统装载中...</div>
    </div>

    <!-- 粒子背景 Canvas (由 JS 动态创建) -->
    
    <!-- 侧边栏按钮 -->
    <div class="btn-group" data-html2canvas-ignore="true">
        <button id="saveBtn" class="btn btn-shot" onclick="saveLongImage()">📸 保存长图</button>
        <button id="profitBtn" class="btn btn-privacy" onclick="togglePrivacy()">🙈 隐藏利润</button>
        <button id="topBtn" class="btn btn-top" onclick="scrollToTop()">⬆️ 回到顶部</button>
    </div>
    
    <!-- 仪表板头部 (一行大字体标题) -->
    <div id="dashboard-header">
        <h1 class="cyber-title">西关打包站 {title} 实时运营仪表板</h1>
        <div id="real-time-clock">--:--:--</div>
    </div>
    
    <!-- Plotly 图表区域 -->
    <div class="dashboard-container">
        {plot_html}
    </div>
    
    <!-- 页脚 -->
    <div class="dashboard-footer">
        <div class="footer-info">系统生成: <b>PackInsight 智能分析系统</b> v8.1 | 数据更新: <span class="footer-tech">{generate_time}</span></div>
        <div class="footer-tech">核心驱动: PANDAS & PLOTLY | 专为西关打包站定制开发</div>
    </div>

    <script>
        {scripts}
        {hide_profit_script}
    </script>
</body>
</html>"""
    
    return html
