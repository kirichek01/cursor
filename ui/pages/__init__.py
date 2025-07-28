"""
UI Pages Module

Страницы пользовательского интерфейса:
- Dashboard: главная панель управления
- SettingsPage: настройки системы
- HistoryPage: история сделок
- ParserBotPage: управление Telegram парсером
- SmartMoneyBotPage: управление SmartMoney ботом
- MT5Page: управление MT5 подключением
"""

from .dashboard import create_dashboard_view
from .settings_page import create_settings_view
from .history_page import create_history_view
from .parser_bot_page import create_parser_bot_view
from .smartmoney_bot_page import create_smartmoney_bot_view
from .mt5_page import create_mt5_view

__all__ = [
    'create_dashboard_view',
    'create_settings_view',
    'create_history_view',
    'create_parser_bot_view',
    'create_smartmoney_bot_view',
    'create_mt5_view'
]