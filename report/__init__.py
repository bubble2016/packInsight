# -*- coding: utf-8 -*-
"""
报告生成模块
"""
from .html_builder import build_analysis_report
from .dashboard_builder import build_dashboard_html

__all__ = ['build_analysis_report', 'build_dashboard_html']
