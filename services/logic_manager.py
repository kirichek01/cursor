import json
import os
import threading
from datetime import datetime

from .database_service import DatabaseService
from .gpt_service import GptService
from .mt5_service import MT5Service
from .telegram_service import TelegramService
from .signal_processor import SignalProcessor
from .trade_manager_service import TradeManagerService

class LogicManager:
    """
    Главный менеджер логики бота. Управляет всеми сервисами и их жизненным циклом.
    Адаптирован для работы с Flet вместо Qt.
    """
    
    def __init__(self, page):
        self.page = page
        self.settings = self._load_config_file("data/config.json")
        self.channels = self._load_config_file("data/channels.json", is_channels=True)
        
        # Состояние сервисов
        self.is_bot_running = False
        self.is_ai_trader_running = False
        self.is_signal_parser_running = False
        
        # Сервисы
        self.db = None
        self.gpt = None
        self.mt5 = None
        self.telegram = None
        self.signal_processor = None
        self.trade_manager = None
        
        # Потоки
        self.telegram_thread = None
        self.trade_manager_thread = None
        self.ai_trader_thread = None
        
        # Статистика
        self.stats = {
            'total_signals': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'current_balance': 0.0
        }
        
        # Подписки на события
        self._setup_pubsub_subscriptions()

    def _load_config_file(self, path, is_channels=False):
        """Загружает конфигурационный файл."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                default = {} if is_channels else {
                    "telegram": {}, "gpt": {}, "mt5": {}, "trading": {}, "breakeven": {},
                    "signal_parser": {"enabled": True},
                    "ai_trader": {"enabled": False, "lot_size": 0.01, "live_trading": False}
                }
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=4)
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file {path}: {e}")
            return {}

    def _setup_pubsub_subscriptions(self):
        """Настраивает подписки на события pubsub."""
        try:
            self.page.pubsub.subscribe("new_telegram_message")(self._handle_telegram_message)
            self.page.pubsub.subscribe("telegram_status")(self._handle_telegram_status)
            self.page.pubsub.subscribe("dialogs_fetched")(self._handle_dialogs_fetched)
            self.page.pubsub.subscribe("trade_manager_log")(self._handle_trade_manager_log)
            self.page.pubsub.subscribe("signal_processed")(self._handle_signal_processed)
            self.page.pubsub.subscribe("trade_executed")(self._handle_trade_executed)
        except Exception as e:
            print(f"PubSub setup error: {e}")

    def _handle_telegram_message(self, message_data):
        """Обрабатывает новое сообщение из Telegram."""
        if self.signal_processor:
            self.signal_processor.process_new_message(message_data)

    def _handle_telegram_status(self, status):
        """Обрабатывает изменение статуса Telegram."""
        print(f"--- [LOGIC MANAGER] Telegram status: {status} ---")
        self._update_ui_status('telegram', status)

    def _handle_dialogs_fetched(self, dialogs_list):
        """Обрабатывает полученный список диалогов."""
        print(f"--- [LOGIC MANAGER] Fetched {len(dialogs_list)} dialogs ---")
        self._update_ui_status('dialogs_count', len(dialogs_list))

    def _handle_trade_manager_log(self, log_data):
        """Обрабатывает логи от Trade Manager."""
        print(f"--- [TRADE MANAGER] {log_data['level']}: {log_data['message']} ---")
        self._update_ui_status('trade_log', log_data)

    def _handle_signal_processed(self, signal_data):
        """Обрабатывает обработанный сигнал."""
        self.stats['total_signals'] += 1
        self._update_ui_status('signal_count', self.stats['total_signals'])

    def _handle_trade_executed(self, trade_data):
        """Обрабатывает выполненную сделку."""
        if trade_data.get('success'):
            self.stats['successful_trades'] += 1
            self.stats['total_profit'] += trade_data.get('profit', 0)
        else:
            self.stats['failed_trades'] += 1
        self._update_ui_status('trade_stats', self.stats)

    def _update_ui_status(self, status_type, data):
        """Обновляет UI статус."""
        try:
            if hasattr(self.page, 'main_app'):
                self.page.main_app.update_status(status_type, data)
        except Exception as e:
            print(f"UI update error: {e}")

    def start_bot(self):
        """Запускает все сервисы бота."""
        if self.is_bot_running:
            return
            
        print("--- [LOGIC MANAGER] Starting bot services... ---")
        
        # Перезагружаем настройки
        self.settings = self._load_config_file("data/config.json")
        
        # Инициализируем сервисы
        self.db = DatabaseService()
        self._update_service_status('database', 'CONNECTED')
        
        gpt_api_key = self.settings.get('gpt', {}).get('api_key')
        self.gpt = GptService(api_key=gpt_api_key)
        self._update_service_status('gpt', 'CONNECTED' if gpt_api_key else 'OFFLINE')
        
        mt5_cfg = self.settings.get('mt5', {})
        self.mt5 = MT5Service(
            path=mt5_cfg.get('path'),
            login=mt5_cfg.get('login'),
            password=mt5_cfg.get('password'),
            server=mt5_cfg.get('server')
        )
        
        # Инициализируем MT5
        success, message = self.mt5.initialize()
        if success:
            self._update_service_status('mt5', 'CONNECTED')
            # Получаем информацию об аккаунте
            account_info = self.mt5.get_account_info()
            if account_info:
                self.stats['current_balance'] = account_info.get('balance', 0)
        else:
            self._update_service_status('mt5', 'ERROR')
            print(f"MT5 initialization failed: {message}")
        
        # Запускаем парсер сигналов если включен
        if self.settings.get('signal_parser', {}).get('enabled', True):
            self.signal_processor = SignalProcessor(
                self.db, self.gpt, self.mt5, self.settings, self.channels, self.page
            )
            
            # Инициализируем Telegram сервис
            tg_cfg = self.settings.get('telegram', {})
            session_file = f"data/{tg_cfg.get('session_file', 'userbot.session')}"
            self.telegram = TelegramService(
                session_file,
                tg_cfg.get('api_id'),
                tg_cfg.get('api_hash'),
                self.page
            )
            
            # Запускаем Telegram в отдельном потоке
            self.telegram.start()
            self.is_signal_parser_running = True
            
            # Инициализируем Trade Manager
            self.trade_manager = TradeManagerService(
                self.db, self.mt5, self.settings, self.page
            )
            
            # Запускаем Trade Manager в отдельном потоке
            self.trade_manager.start_monitoring()
            
        else:
            self._update_service_status('telegram', 'DISABLED')
        
        # Проверяем AI Trader
        if self.settings.get('ai_trader', {}).get('enabled', False):
            print("--- [LOGIC MANAGER] AI Trader is enabled. Use start_ai_trader() to begin. ---")
        
        self.is_bot_running = True
        print("--- [LOGIC MANAGER] Bot services started successfully. ---")

    def stop_bot(self):
        """Останавливает все сервисы бота."""
        if not self.is_bot_running:
            return
            
        print("--- [LOGIC MANAGER] Stopping bot services... ---")
        
        # Останавливаем AI Trader если запущен
        if self.is_ai_trader_running:
            self.stop_ai_trader()
        
        # Останавливаем Trade Manager
        if self.trade_manager:
            self.trade_manager.stop()
        
        # Останавливаем Telegram
        if self.telegram:
            self.telegram.stop()
        
        # Закрываем MT5
        if self.mt5:
            self.mt5.shutdown()
        
        # Закрываем базу данных
        if self.db:
            self.db.close_connection()
        
        self.is_bot_running = False
        self.is_signal_parser_running = False
        print("--- [LOGIC MANAGER] Bot services stopped. ---")

    def start_ai_trader(self):
        """Запускает AI Trader."""
        if not self.is_bot_running:
            print("--- [LOGIC MANAGER] Bot must be running before starting AI Trader. ---")
            return
            
        if self.is_ai_trader_running:
            print("--- [LOGIC MANAGER] AI Trader is already running. ---")
            return
        
        # Здесь можно добавить импорт и инициализацию AI Trader
        # from .ai_trader_service import AITraderService
        # self.ai_trader = AITraderService(...)
        
        self.is_ai_trader_running = True
        print("--- [LOGIC MANAGER] AI Trader started. ---")

    def stop_ai_trader(self):
        """Останавливает AI Trader."""
        if not self.is_ai_trader_running:
            return
        
        # Останавливаем AI Trader
        # if self.ai_trader:
        #     self.ai_trader.stop()
        
        self.is_ai_trader_running = False
        print("--- [LOGIC MANAGER] AI Trader stopped. ---")

    def update_settings(self, new_settings):
        """Обновляет настройки и сохраняет в файл."""
        self.settings.update(new_settings)
        try:
            with open("data/config.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            print("--- [LOGIC MANAGER] Settings updated successfully. ---")
            return True
        except Exception as e:
            print(f"--- [LOGIC MANAGER] Error saving settings: {e} ---")
            return False

    def update_channels(self, new_channels):
        """Обновляет список каналов и сохраняет в файл."""
        self.channels = new_channels
        try:
            with open("data/channels.json", "w", encoding="utf-8") as f:
                json.dump(self.channels, f, indent=4)
            print("--- [LOGIC MANAGER] Channels updated successfully. ---")
            return True
        except Exception as e:
            print(f"--- [LOGIC MANAGER] Error saving channels: {e} ---")
            return False

    def _update_service_status(self, service_name, status):
        """Обновляет статус сервиса."""
        print(f"--- [LOGIC MANAGER] {service_name.upper()} status: {status} ---")
        self._update_ui_status(f'{service_name}_status', status)

    def get_account_info(self):
        """Получает информацию об аккаунте MT5."""
        if self.mt5:
            return self.mt5.get_account_info()
        return None

    def test_gpt_key(self, api_key):
        """Тестирует GPT API ключ."""
        if self.gpt:
            return self.gpt.test_api_key(api_key)
        return False

    def fetch_telegram_dialogs(self):
        """Получает список диалогов Telegram."""
        if self.telegram:
            return self.telegram.fetch_dialogs()
        return []

    def get_signal_history(self, limit=100):
        """Получает историю сигналов."""
        if self.db:
            return self.db.get_signal_history(limit=limit)
        return []

    def get_bot_status(self):
        """Получает общий статус бота."""
        return {
            'bot_running': self.is_bot_running,
            'ai_trader_running': self.is_ai_trader_running,
            'signal_parser_running': self.is_signal_parser_running,
            'stats': self.stats,
            'services': {
                'database': self.db is not None,
                'gpt': self.gpt is not None,
                'mt5': self.mt5 is not None,
                'telegram': self.telegram is not None,
                'signal_processor': self.signal_processor is not None,
                'trade_manager': self.trade_manager is not None
            }
        }

    def get_trading_stats(self):
        """Получает торговую статистику."""
        return self.stats

    def reset_stats(self):
        """Сбрасывает статистику."""
        self.stats = {
            'total_signals': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'current_balance': 0.0
        }
        print("--- [LOGIC MANAGER] Statistics reset. ---") 