"""
Trading Bots Module

Торговые боты и автоматизация:
- SmartMoney: бот для торговли по концепциям Smart Money
- Parser: парсер сигналов из Telegram каналов
"""

# Импортируем доступные компоненты
try:
    from .smart_money import load_mt5_data, generate_smc_features, run_strategy
    SMART_MONEY_CORE_AVAILABLE = True
except ImportError:
    SMART_MONEY_CORE_AVAILABLE = False

try:
    from .parser import ParserLogic
    PARSER_AVAILABLE = True
except ImportError:
    PARSER_AVAILABLE = False

__all__ = [
    'SMCBot',
    'SMCRunner', 
    'AIAgent',
    'ParserLogic'
]