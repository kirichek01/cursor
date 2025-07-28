"""
UI Components Module

UI компоненты и виджеты:
- Charts: графики и диаграммы
- Header: заголовок приложения
- Sidebar: боковая панель навигации
- RightPanel: правая информационная панель
"""

from .charts import (
    generate_donut_chart, 
    generate_line_chart, 
    generate_real_donut_chart, 
    generate_real_profit_chart
)
from .header import create_header
from .sidebar import create_sidebar
from .right_panel import create_right_panel

__all__ = [
    'generate_donut_chart',
    'generate_line_chart', 
    'generate_real_donut_chart',
    'generate_real_profit_chart',
    'create_header',
    'create_sidebar',
    'create_right_panel'
]