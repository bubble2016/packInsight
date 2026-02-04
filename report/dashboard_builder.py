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


def build_dashboard_html(fig, title, dest_list=None):
    """
    构建完整的仪表板 HTML
    
    Args:
        fig: Plotly Figure 对象
        title: 仪表板标题（如 "[1月]" 或 "[多月对比]"）
        dest_list: 目的地列表（用于隐私保护功能）
    
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
    
    # 隐藏利润功能脚本 (只隐藏利润相关数字) + 保存长图功能
    hide_profit_script = """
        // 隐藏利润功能：只隐藏利润相关的KPI数值
        let isProfitHidden = false;
        
        // 存储利润数据的标识（通过附近标题判断）
        function findProfitIndicators() {
            const allTexts = document.querySelectorAll('text, tspan');
            const profitElements = [];
            
            // 利润相关的标题关键词
            const profitTitleKeywords = ['总预估利润', '平均吨利润', '每吨利润'];
            
            // 先找到利润标题的位置
            const titlePositions = [];
            allTexts.forEach(el => {
                const content = (el.textContent || '').trim();
                if (profitTitleKeywords.some(kw => content.includes(kw))) {
                    // 获取标题元素的位置
                    const rect = el.getBoundingClientRect();
                    titlePositions.push({
                        title: content,
                        x: rect.x + rect.width / 2,
                        y: rect.y,
                        element: el
                    });
                }
            });
            
            // 找到标题下方最近的数值元素
            allTexts.forEach(el => {
                const content = (el.textContent || '').trim();
                
                // 检查是否是数字+单位（万或元），或者是趋势指标（▲▼）
                const isProfitValue = /^[0-9,\\.]+\\s*(万|元)$/.test(content);
                const isTrendDelta = /^[▲▼△▽][0-9\\.]+$/.test(content);
                
                if (isProfitValue || isTrendDelta) {
                    const rect = el.getBoundingClientRect();
                    const elX = rect.x + rect.width / 2;
                    const elY = rect.y;
                    
                    // 判断这个数值是否在某个利润标题的下方（垂直距离在150px内，水平距离在100px内）
                    for (const pos of titlePositions) {
                        if (Math.abs(elX - pos.x) < 100 && elY > pos.y && (elY - pos.y) < 150) {
                            profitElements.push(el);
                            break;
                        }
                    }
                }
            });
            
            return profitElements;
        }
        
        function toggleProfit() {
            const btn = document.getElementById('profitBtn');
            isProfitHidden = !isProfitHidden;
            
            // 找到利润相关的元素
            const profitElements = findProfitIndicators();
            
            profitElements.forEach(el => {
                if (isProfitHidden) {
                    el.classList.add('blurred-sensitive');
                } else {
                    el.classList.remove('blurred-sensitive');
                }
            });
            
            // 更新按钮文字
            btn.innerHTML = isProfitHidden ? '👁️ 显示利润' : '🙈 隐藏利润';
        }
        
        // 保存长图功能（带进度提示）
        function saveLongImage() {
            const btnGroup = document.querySelector('.btn-group');
            const saveBtn = document.getElementById('saveBtn');
            const originalText = saveBtn.innerHTML;
            
            // 显示进度
            saveBtn.innerHTML = '⏳ 保存中...';
            saveBtn.style.background = '#666';
            btnGroup.style.pointerEvents = 'none';
            
            // 准备截图
            
            setTimeout(() => {
                html2canvas(document.body, {
                    backgroundColor: '#1e1e2f',
                    scale: 2,
                    useCORS: true,
                    logging: false,
                    onclone: function(clonedDoc) {
                        const clonedBtnGroup = clonedDoc.querySelector('.btn-group');
                        if (clonedBtnGroup) clonedBtnGroup.style.display = 'none';
                        // 在克隆层添加截图模式类，不影响主界面
                        clonedDoc.body.classList.add('snapshot-mode');
                    }
                }).then(canvas => {
                    saveBtn.innerHTML = '✅ 已保存';
                    saveBtn.style.background = '#00FF99';
                    saveBtn.style.color = '#000';
                    
                    const link = document.createElement('a');
                    link.download = document.title + '_长图.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                    
                    setTimeout(() => {
                        saveBtn.innerHTML = originalText;
                        saveBtn.style.background = '';
                        saveBtn.style.color = '';
                        btnGroup.style.pointerEvents = '';
                        btnGroup.style.pointerEvents = '';
                    }, 1500);
                }).catch(err => {
                    saveBtn.innerHTML = '❌ 失败';
                    saveBtn.style.background = '#FF3333';
                    console.error('保存失败:', err);
                    
                    setTimeout(() => {
                        saveBtn.innerHTML = originalText;
                        saveBtn.style.background = '';
                        btnGroup.style.pointerEvents = '';
                        btnGroup.style.pointerEvents = '';
                    }, 2000);
                });
            }, 100);
        }
    """
    
    # 构建完整 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>西关打包站 - {title} 运营仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <style>
        {styles}
    </style>
</head>
<body>
    <!-- 粒子背景 Canvas (由 JS 动态创建) -->
    
    <!-- 侧边栏按钮 -->
    <div class="btn-group">
        <button id="saveBtn" class="btn btn-shot" onclick="saveLongImage()">📸 保存长图</button>
        <button id="profitBtn" class="btn btn-privacy" onclick="toggleProfit()">🙈 隐藏利润</button>
    </div>
    
    <!-- 仪表板头部 (一行大字体标题) -->
    <div id="dashboard-header">
        <h1 class="cyber-title">西关打包站 {title} 实时运营仪表板</h1>
    </div>
    
    <!-- Plotly 图表区域 -->
    <div class="dashboard-container">
        {plot_html}
    </div>
    
    <script>
        {scripts}
        {hide_profit_script}
    </script>
</body>
</html>"""
    
    return html
