# -*- coding: utf-8 -*-
"""
HTML 报告交互脚本 (JavaScript)
"""

def get_base_scripts():
    """获取基础交互脚本（打印、截图、隐私）"""
    return """
        function printReport() { window.print(); }
        
        function scrollToTop() {
            const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
        }

        function initDynamicStyles() {
            // KPI 动态颜色：通过 data-color 注入，避免模板内联样式
            document.querySelectorAll('.kpi-val[data-color]').forEach(el => {
                const color = el.getAttribute('data-color');
                if (color) {
                    el.style.setProperty('--kpi-color', color);
                }
            });

            // 数据条宽度：通过 data-width 注入并触发动画
            document.querySelectorAll('.data-bar[data-width]').forEach((el, index) => {
                const width = parseFloat(el.getAttribute('data-width'));
                const safeWidth = Number.isFinite(width) ? Math.max(0, Math.min(100, width)) : 0;
                el.style.setProperty('--width', safeWidth + '%');
                setTimeout(() => el.classList.add('animate'), Math.min(index * 25, 400));
            });
        }

        
        function captureScreenshot() {
            const saveBtn = document.querySelector('.btn-shot');
            const originalText = saveBtn.innerHTML;
            
            // 优化体验：仅修改按钮状态，不隐藏界面防止闪烁
            saveBtn.innerHTML = '⏳ 保存中...';
            saveBtn.style.cursor = 'wait';
            
            html2canvas(document.body, {
                backgroundColor: "#1e1e1e",
                scale: 2, 
                useCORS: true,
                onclone: function(clonedDoc) {
                    // 在克隆的文档中隐藏按钮，这样真实屏幕不会闪烁
                    const clonedBtnGroup = clonedDoc.querySelector('.btn-group');
                    if(clonedBtnGroup) clonedBtnGroup.style.display = 'none'; 
                    // 在克隆文档中冻结动画
                    clonedDoc.body.classList.add('no-anim');
                }
            }).then(canvas => {
                let link = document.createElement('a');
                link.download = document.title + '.png';
                link.href = canvas.toDataURL();
                link.click();
                
                // 恢复按钮与状态
                saveBtn.innerHTML = '✅ 已保存';
                saveBtn.style.cursor = 'default';
                setTimeout(() => { saveBtn.innerHTML = originalText; }, 2000);
            }).catch(err => {
                console.error(err);
                saveBtn.innerHTML = '❌ 失败';
                setTimeout(() => { saveBtn.innerHTML = originalText; }, 2000);
            });
        }
        
        // 统一的隐私模式切换函数
        function togglePrivacy() {
            const body = document.body;
            const btn = document.getElementById('privacyBtn') || document.getElementById('profitBtn');
            
            // 切换 Body 类（这将自动触发 CSS 模糊效果）
            body.classList.toggle('privacy-active');
            const isHidden = body.classList.contains('privacy-active');
            
            // 更新按钮文字
            if (btn) {
                if (isHidden) {
                    btn.innerHTML = btn.id === 'profitBtn' ? '👁️ 显示利润' : '🔓 显示利润';
                    btn.classList.add('active');
                } else {
                    btn.innerHTML = btn.id === 'profitBtn' ? '🙈 隐藏利润' : '👁️ 隐藏利润';
                    btn.classList.remove('active');
                }
            }
            
            // --- 针对 Plotly 图表的特殊处理 (SVG/Canvas 无法被 simple CSS class 覆盖) ---
            // 只有当存在 Plotly 图表时才执行
            if (document.querySelector('.plotly-graph-div')) {
                 handlePlotlyPrivacy(isHidden);
            }
        }
        
        // 专门处理 Plotly 图表的隐私保护
        function handlePlotlyPrivacy(isHidden) {
             // 1. 查找所有可能包含敏感数据的 SVG 文本元素
             const allTexts = document.querySelectorAll('.plotly-graph-div text, .plotly-graph-div tspan');
             
             // 利润相关的关键词
             const profitKeywords = ['总预估利润', '平均吨利润', '每吨利润', '利润率', '总利润'];
             
             // 收集标题位置
             const titlePositions = [];
             allTexts.forEach(el => {
                 const content = (el.textContent || '').trim();
                 if (profitKeywords.some(kw => content.includes(kw))) {
                     const rect = el.getBoundingClientRect();
                     titlePositions.push({
                         x: rect.x + rect.width / 2,
                         y: rect.y,
                         width: rect.width,
                         height: rect.height
                     });
                 }
             });
             
             // 遍历所有文本以查找附近的数值
             allTexts.forEach(el => {
                 const content = (el.textContent || '').trim();
                 
                 // 简单的启发式：如果是数字且带有金额单位，或者纯数字（并在标题附近）
                 // 匹配格式：xx.x 万, xx.x 元, xx%, 纯数字
                 // 使用 raw string 避免 python 转义警告
                 const isMoneyLike = /^[0-9,\\.]+\\s*(万|元)$/.test(content);
                 const isPercent = /^[0-9,\\.]+%$/.test(content);
                 const isNumber = /^[0-9,\\.]+$/.test(content);
                 
                 if (isMoneyLike || isPercent || isNumber) {
                     const rect = el.getBoundingClientRect();
                     const elX = rect.x + rect.width / 2;
                     const elY = rect.y;
                     
                     // 检查是否在任意利润标题下方/附近
                     let isSensitive = false;
                     for (const pos of titlePositions) {
                         // 垂直方向：标题下方 0~150px
                         // 水平方向：中心对齐偏差 < 100px
                         if (elY >= pos.y && (elY - pos.y) < 180 && Math.abs(elX - pos.x) < 120) {
                             isSensitive = true;
                             break;
                         }
                         // 特殊情况：左右布局（如气泡图 Legend）
                         if (Math.abs(elY - pos.y) < 50 && Math.abs(elX - pos.x) < 200) {
                            // 可能是旁边的数值
                         }
                     }
                     
                     if (isSensitive) {
                         if (isHidden) {
                             el.classList.add('blurred-sensitive');
                             el.style.filter = 'blur(10px)'; // 强制内联样式以确保生效
                         } else {
                             el.classList.remove('blurred-sensitive');
                             el.style.filter = '';
                         }
                     }
                 }
             });
        }

        // 实时时钟
        function startClock() {
            function update() {
                const now = new Date();
                const datePart = now.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\\//g, '-');
                const timePart = now.toLocaleTimeString('zh-CN', { hour12: false });
                const clockEl = document.getElementById('real-time-clock');
                if (clockEl) {
                    clockEl.innerHTML = `📅 ${datePart} <span style="margin-left:15px">⏰ ${timePart}</span>`;
                }
            }
            setInterval(update, 1000);
            update();
        }
        window.addEventListener('load', () => {
            initDynamicStyles();
            startClock();
        });
    """

def get_particle_animation_js():
    """获取粒子背景动画脚本"""
    return """
        (function initParticles() {
            if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                return;
            }
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.style.position = 'fixed';
            canvas.style.top = '0';
            canvas.style.left = '0';
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            canvas.style.zIndex = '-1';
            canvas.style.pointerEvents = 'none';
            document.body.prepend(canvas);

            let particles = [];
            const PARTICLE_COUNT = 80;

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            resize();

            class Particle {
                constructor() {
                    this.reset();
                }
                reset() {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.vx = (Math.random() - 0.5) * 0.5;
                    this.vy = (Math.random() - 0.5) * 0.5;
                    this.radius = Math.random() * 2;
                    this.alpha = Math.random() * 0.5 + 0.1;
                    this.color = Math.random() > 0.5 ? '#00FF99' : '#00CCFF';
                    this.twinkleSpeed = Math.random() * 0.03 + 0.01;
                    this.twinklePhase = Math.random() * Math.PI * 2;
                }
                update() {
                    this.x += this.vx;
                    this.y += this.vy;
                    if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
                        this.reset();
                    }
                    this.twinklePhase += this.twinkleSpeed;
                    this.alpha = 0.3 + Math.sin(this.twinklePhase) * 0.4;
                }
                draw() {
                    ctx.save();
                    ctx.globalAlpha = this.alpha;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.fill();
                    ctx.restore();
                }
            }

            for (let i = 0; i < PARTICLE_COUNT; i++) {
                particles.push(new Particle());
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                particles.forEach(p => { p.update(); p.draw(); });
                requestAnimationFrame(animate);
            }
            animate();
        })();
    """

def get_counter_animation_js():
    """获取抽奖式数字滚动动画脚本（老虎机效果）"""
    return """
        (function initSlotMachineAnimation() {
            if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                return;
            }
            /**
             * 抽奖机式数字滚动动画
             * @param {Element} element - 要动画的文本元素
             * @param {number} targetValue - 目标数值
             * @param {string} suffix - 后缀（如 " 吨"、" 万"）
             * @param {number} decimals - 小数位数
             */
            function animateSlotMachine(element, targetValue, suffix = '', decimals = 1) {
                const totalDuration = 2500;  // 总动画时长
                const spinPhase = 1500;      // 快速滚动阶段时长
                const slowDownPhase = 1000;  // 减速阶段时长
                const startTime = performance.now();
                
                // 计算随机数范围（目标值的 50% ~ 150%）
                const minRandom = targetValue * 0.3;
                const maxRandom = targetValue * 1.7;
                
                function formatNumber(num) {
                    return num.toFixed(decimals);
                }
                
                function getRandomValue() {
                    return minRandom + Math.random() * (maxRandom - minRandom);
                }
                
                function easeOutExpo(t) {
                    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
                }
                
                function update(currentTime) {
                    const elapsed = currentTime - startTime;
                    
                    if (elapsed < spinPhase) {
                        // === 快速随机滚动阶段 ===
                        // 滚动速度：开始快，逐渐变慢
                        const spinProgress = elapsed / spinPhase;
                        const intervalMs = 30 + spinProgress * 100; // 30ms -> 130ms
                        
                        // 每隔一定时间切换随机数
                        const randomValue = getRandomValue();
                        element.textContent = formatNumber(randomValue) + suffix;
                        
                        // 添加闪烁效果
                        element.style.opacity = 0.9 + Math.random() * 0.1;
                        
                        requestAnimationFrame(update);
                    } else if (elapsed < totalDuration) {
                        // === 减速收敛阶段 ===
                        const slowProgress = (elapsed - spinPhase) / slowDownPhase;
                        const easedProgress = easeOutExpo(slowProgress);
                        
                        // 从最后一个随机值渐变到目标值
                        const lastRandomBase = targetValue * (0.8 + Math.random() * 0.4);
                        const currentValue = lastRandomBase + (targetValue - lastRandomBase) * easedProgress;
                        
                        element.textContent = formatNumber(currentValue) + suffix;
                        element.style.opacity = 0.9 + easedProgress * 0.1;
                        
                        requestAnimationFrame(update);
                    } else {
                        // === 最终定格 ===
                        element.textContent = formatNumber(targetValue) + suffix;
                        element.style.opacity = '1';
                        
                        // 添加完成后的高亮闪烁效果
                        element.style.transition = 'filter 0.45s ease-out';
                        element.style.filter = 'brightness(1.08) drop-shadow(0 0 4px currentColor)';
                        setTimeout(() => {
                            element.style.filter = '';
                        }, 420);
                    }
                }
                
                requestAnimationFrame(update);
            }
            
            /**
             * 查找并动画化仪表板中的 KPI 数字
             */
            function initDashboardKPIAnimation() {
                // 等待 Plotly 渲染完成
                setTimeout(() => {
                    // 查找所有 Plotly Indicator 数字
                    const allTexts = document.querySelectorAll('text');
                    
                    // KPI 标题关键词（用于定位附近的数值）
                    const kpiTitles = ['总发货量', '总预估利润', '平均吨利润', '总运输车次', '日均发货量'];
                    const titlePositions = [];
                    
                    // 第一步：收集标题位置
                    allTexts.forEach(el => {
                        const content = (el.textContent || '').trim();
                        if (kpiTitles.some(title => content.includes(title))) {
                            const rect = el.getBoundingClientRect();
                            titlePositions.push({
                                title: content,
                                x: rect.x + rect.width / 2,
                                y: rect.y,
                                element: el
                            });
                        }
                    });
                    
                    // 第二步：查找每个标题下方的数值并动画化
                    const animatedElements = new Set();
                    
                    allTexts.forEach(el => {
                        if (animatedElements.has(el)) return;
                        
                        const content = (el.textContent || '').trim();
                        
                        // 匹配数字+单位格式（如 "667.5 吨"、"5.05 万"）
                        const numMatch = content.match(/^([\\d,\\.]+)\\s*(吨|万|元|车)$/);
                        if (!numMatch) return;
                        
                        const rect = el.getBoundingClientRect();
                        const elX = rect.x + rect.width / 2;
                        const elY = rect.y;
                        
                        // 检查是否在某个 KPI 标题下方
                        for (const pos of titlePositions) {
                            if (Math.abs(elX - pos.x) < 120 && elY > pos.y && (elY - pos.y) < 100) {
                                // 找到匹配的 KPI 数值！
                                const numValue = parseFloat(numMatch[1].replace(/,/g, ''));
                                const unit = ' ' + numMatch[2];
                                
                                // 确定小数位数
                                let decimals = 1;
                                if (numMatch[1].includes('.')) {
                                    decimals = numMatch[1].split('.')[1].length;
                                } else {
                                    decimals = 0;
                                }
                                
                                // 立即隐藏真实值，显示初始随机状态
                                const initialRandom = numValue * 0.5 + Math.random() * numValue;
                                // 立即设置初始文本，避免露馅
                                el.textContent = initialRandom.toFixed(decimals) + unit;
                                el.style.opacity = '0.5';

                                // 启动抽奖式动画（错开时间）
                                const delay = titlePositions.indexOf(pos) * 300;
                                setTimeout(() => {
                                    animateSlotMachine(el, numValue, unit, decimals);
                                }, delay);
                                
                                animatedElements.add(el);
                                break;
                            }
                        }
                    });
                    
                    console.log('🎰 抽奖式 KPI 动画已启动，共 ' + animatedElements.size + ' 个元素');
                    
                }, 800); // 等待 Plotly 渲染
            }
            
            // 页面加载完成后启动
            window.addEventListener('load', initDashboardKPIAnimation);
        })();
    """


def get_stagger_animation_js():
    """获取级联渐入动画及霓虹脉冲脚本"""
    return """
        (function initStaggeredAnimation() {
            let hasStarted = false;

            function hideLoader(force = false) {
                const loader = document.getElementById('loading-overlay');
                if (!loader) return;
                if (force) {
                    loader.style.display = 'none';
                    return;
                }
                loader.style.opacity = '0';
                setTimeout(() => { loader.style.display = 'none'; }, 500);
            }

            function start() {
                if (hasStarted) return;
                hasStarted = true;

                const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                // 优先移除加载遮罩，避免因外链资源导致 window.load 延迟
                if (reduceMotion) hideLoader(true);
                else setTimeout(() => hideLoader(false), 300);
                if (reduceMotion) return;

                setTimeout(() => {
                    // Plotly图表级联动画
                    const plotlyContainers = document.querySelectorAll('.plotly-graph-div');
                    plotlyContainers.forEach((container, index) => {
                        container.style.opacity = '0';
                        container.style.transform = 'translateY(30px)';
                        container.style.transition = 'all 0.8s cubic-bezier(0.2, 0.8, 0.2, 1)';
                        
                        setTimeout(() => {
                            container.style.opacity = '1';
                            container.style.transform = 'translateY(0)';
                            // container.classList.add('neon-border'); // 已移除霓虹边框
                        }, index * 150);
                    });
                    
                    // 霓虹文字效果
                    setTimeout(() => {
                        const textElements = document.querySelectorAll('text');
                        const kpiColors = ['rgb(0, 255, 153)', 'rgb(255, 0, 204)', 'rgb(0, 204, 255)', 'rgb(255, 255, 51)'];
                        
                        textElements.forEach(el => {
                            const fill = el.style.fill || el.getAttribute('fill');
                            if (!fill) return;
                            
                            const isKPI = kpiColors.some(c => fill.includes(c)) || 
                                          (el.getAttribute('class') && el.getAttribute('class').includes('number'));
                            
                            if (isKPI) {
                                el.style.filter = 'drop-shadow(0 0 3px ' + fill + ')';
                                el.style.animation = 'neonPulse 3.2s ease-in-out infinite';
                            }
                        });
                    }, 1000);
                    
                }, 300);
            }

            // DOM 就绪即可启动，避免卡在“系统加载中...”
            document.addEventListener('DOMContentLoaded', start, { once: true });
            // 双保险：部分环境 DOMContentLoaded 触发异常时仍可在 load 启动
            window.addEventListener('load', start, { once: true });
            // 最终兜底：4 秒后强制移除遮罩
            setTimeout(() => hideLoader(true), 4000);
        })();
    """
