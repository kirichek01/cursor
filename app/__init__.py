"""
Trading System Application

Главное приложение торговой системы с интеграцией MT5, Telegram парсера 
и SmartMoney бота. Работает исключительно с реальными торговыми данными.
"""

__version__ = "2.0.0"
__author__ = "Trading System Team"
__description__ = "Professional Trading System with Real Data Only"

# Основные компоненты приложения
from .main import TradingApp
from .config import AppConfig

__all__ = [
    'TradingApp',
    'AppConfig'
]