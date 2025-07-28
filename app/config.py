#!/usr/bin/env python3
"""
Конфигурация торговой системы
"""

import os
from pathlib import Path

class AppConfig:
    """Конфигурация приложения"""
    
    # Основные настройки
    APP_NAME = "Trading System"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Professional Trading System with Real Data Only"
    
    # Пути
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    CONFIGS_DIR = BASE_DIR / "configs"
    LOGS_DIR = DATA_DIR / "logs"
    
    # MT5 настройки
    MT5_CONFIG = {
        "login": os.getenv("MT5_LOGIN", ""),
        "password": os.getenv("MT5_PASSWORD", ""),
        "server": os.getenv("MT5_SERVER", ""),
        "symbols": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"],
        "timeframes": ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
    }
    
    # База данных
    DATABASE_CONFIG = {
        "path": DATA_DIR / "database" / "trading_data.db",
        "backup_interval": 3600,  # секунды
        "max_backups": 10
    }
    
    # UI настройки
    UI_CONFIG = {
        "theme": "dark",
        "window_width": 1200,
        "window_height": 800,
        "auto_update_interval": 30  # секунды
    }

# Совместимость со старым кодом
PARSER_BOT_PATH = Path("bots/parser/parser_logic.py")
SMC_BOT_PATH = Path("bots/smart_money/smc_bot_core.py")
MT5_CONFIG = AppConfig.MT5_CONFIG

# Telegram настройки для парсер бота
TELEGRAM_CONFIG = {
    "api_id": os.getenv("TELEGRAM_API_ID", ""),
    "api_hash": os.getenv("TELEGRAM_API_HASH", ""),
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "channels": [
        # Добавьте сюда каналы для парсинга
        # "channel_name_1",
        # "channel_name_2"
    ]
}

# Настройки риска
RISK_CONFIG = {
    "max_risk_per_trade": 0.02,  # 2% от баланса
    "max_daily_loss": 0.05,      # 5% от баланса
    "max_open_trades": 3,        # Максимум открытых сделок
    "stop_loss_pips": 50,        # Stop Loss в пипсах
    "take_profit_pips": 100,     # Take Profit в пипсах
}

# SMC настройки
SMC_CONFIG = {
    "symbols": ["XAUUSD"],
    "timeframe": "M15",
    "order_block_threshold": 0.6,
    "fvg_threshold": 0.3,
    "atr_period": 14,
    "ema_period": 50,
}

# Настройки интерфейса
UI_CONFIG = {
    "theme": "dark",
    "refresh_interval": 5000,  # 5 секунд
    "max_history_items": 100,
    "chart_update_interval": 1000,  # 1 секунда
}

# Пути к данным
DATA_PATHS = {
    "database": "data/trading_bots.db",
    "logs": "logs/",
    "backups": "backups/",
    "configs": "configs/",
}

# Создание необходимых директорий
def create_directories():
    """Создает необходимые директории."""
    for path in DATA_PATHS.values():
        if path.endswith("/"):
            Path(path).mkdir(parents=True, exist_ok=True)
        else:
            Path(path).parent.mkdir(parents=True, exist_ok=True)

# Проверка конфигурации
def validate_config():
    """Проверяет корректность конфигурации."""
    errors = []
    
    # Проверка путей к ботам
    if not PARSER_BOT_PATH.exists():
        errors.append(f"Парсер бот не найден: {PARSER_BOT_PATH}")
    
    if not SMC_BOT_PATH.exists():
        errors.append(f"Смартмани бот не найден: {SMC_BOT_PATH}")
    
    # Проверка MT5 настроек
    if not MT5_CONFIG["login"]:
        errors.append("MT5_LOGIN не настроен")
    
    # Проверка Telegram настроек
    if not TELEGRAM_CONFIG["api_id"]:
        errors.append("TELEGRAM_API_ID не настроен")
    
    return errors

if __name__ == "__main__":
    print("🔧 Проверка конфигурации...")
    create_directories()
    
    errors = validate_config()
    if errors:
        print("❌ Найдены ошибки в конфигурации:")
        for error in errors:
            print(f"   • {error}")
        print("\n📝 Создайте файл .env с необходимыми переменными:")
        print("MT5_LOGIN=your_login")
        print("MT5_PASSWORD=your_password")
        print("TELEGRAM_API_ID=your_api_id")
        print("TELEGRAM_API_HASH=your_api_hash")
    else:
        print("✅ Конфигурация корректна")
