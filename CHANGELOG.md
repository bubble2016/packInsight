# 更新日志

## v9.0.0 (2026-02-19)

本版本基于远端最新 `origin/main@f24d05a`（README 文案更新）继续演进。

### 1. 与远端最新版本对比（origin/main -> 当前工作区）

- 新增文件
  - `refresh_dashboard_html.py`
- 变更文件
  - `gui/app.py`
  - `main.py`
  - `report/dashboard_builder.py`
  - `report/dashboard_styles.py`
  - `report/html_builder.py`
  - `report/scripts.py`
  - `report/styles.py`
  - `README.md`

### 2. 进度窗口（桌面 GUI）改进

- `gui/app.py`
  - 统一主题色与字体（引入 `THEME` 配置集中管理）。
  - 进度窗口从无边框模式切换为可控窗口行为。
  - 关闭按钮行为改为“最小化到后台继续执行”，避免误终止任务。
  - 新增“最小化”按钮与后台执行提示文案。
  - 修复窗口高度不足导致底部内容被裁切：窗口改为 `560x320` 并设置最小尺寸。

### 3. 仪表板视觉与动效优化（柔和化）

- `report/dashboard_styles.py`
  - 降低霓虹脉冲强度，减少高亮半径与亮度波动。
  - 标题发光改为更长周期、低强度呼吸效果。
  - KPI 发光由强 `drop-shadow` 调整为轻量阴影，避免刺眼“白闪”。
  - 增补移动端布局与按钮响应式样式。
  - 补充 `focus-visible` 焦点态与 `prefers-reduced-motion` 支持。

- `report/scripts.py`
  - KPI 数字滚动阶段透明度波动收窄（减少闪烁感）。
  - 滚动完成后的瞬时高亮改为轻提亮（`brightness(1.08)`），避免强闪。
  - 图表 KPI 文本动效节奏放缓，发光半径降低。
  - 加载遮罩改为 `DOMContentLoaded` 优先移除，并增加超时兜底，避免卡“系统加载中”。
  - 回到顶部与粒子/计数动画均尊重 `prefers-reduced-motion`。

### 4. HTML 报告与仪表板生成器重构

- `report/dashboard_builder.py`
  - 抽离样式/脚本组合函数：`get_dashboard_style_bundle()`、`get_dashboard_script_bundle()`。
  - 抽离长图导出脚本：`get_save_long_image_script()`。
  - 在生成 HTML 中加入动态区块标记：
    - `DASHBOARD_DYNAMIC_STYLES_START/END`
    - `DASHBOARD_DYNAMIC_SCRIPTS_START/END`
  - 提升按钮可访问性（`type`、`aria-label`、`title`）。

- `report/html_builder.py`
  - 拆分复用函数：表格、指标条、建议卡、预警块渲染函数。
  - 移除大量内联样式写法，改为数据属性驱动（如 `data-color`）。
  - 补充页面元信息与交互按钮无障碍属性。

- `report/styles.py`
  - 增加响应式断点适配（1200/900/600）。
  - 新增日报峰值、成本透视、预警建议模块样式。
  - 数据条动画改为类触发模式（`.data-bar.animate`）并区分条形渐变主题。

### 5. 开发体验与运维效率提升

- 新增 `refresh_dashboard_html.py`
  - 支持在“已生成的仪表板 HTML”上快速热更新样式/脚本，无需重跑数据分析。
  - 支持两种模式：
    - 指定文件路径刷新
    - 自动刷新最近修改的仪表板 HTML

- `main.py`
  - 新增 `setup_console_utf8()`，统一 Windows 控制台 UTF-8 输出，降低中文乱码风险。

### 6. 版本升级

- 全局版本标识升级为 `v9.0`：
  - `README.md`
  - `main.py`
  - `report/html_builder.py`
  - `report/dashboard_builder.py`

