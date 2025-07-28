import threading
import time
from datetime import datetime
import json

# Импорты сервисов
try:
    from ..services.mt5_service import MT5Service
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MT5Service недоступен")

try:
    from ..services.telegram_service import TelegramService
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ TelegramService недоступен")

try:
    from ..services.gpt_service import GPTService
    GPT_AVAILABLE = True
except ImportError:
    GPT_AVAILABLE = False
    print("⚠️ GPTService недоступен")

try:
    from ..services.signal_processor import SignalProcessor
    SIGNAL_PROCESSOR_AVAILABLE = True
except ImportError:
    SIGNAL_PROCESSOR_AVAILABLE = False
    print("⚠️ SignalProcessor недоступен")

try:
    from ..services.trade_manager_service import TradeManagerService
    TRADE_MANAGER_AVAILABLE = True
except ImportError:
    TRADE_MANAGER_AVAILABLE = False
    print("⚠️ TradeManagerService недоступен")

try:
    from ..services.database_service import DatabaseService
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️ DatabaseService недоступен")

try:
    from .smc_logic import SMCStrategy
    SMC_AVAILABLE = True
except ImportError:
    SMC_AVAILABLE = False
    print("⚠️ SMCStrategy недоступен")

class LogicManager:
    """
    Центральный менеджер логики торговой системы
    Интегрирует все сервисы и управляет их взаимодействием
    """
    
    def __init__(self):
        # Инициализация сервисов
        self.mt5 = None
        self.telegram = None
        self.gpt = None
        self.signal_processor = None
        self.trade_manager = None
        self.database = None
        self.smc_strategy = None
        
        # Состояние системы
        self.is_running = False
        self.auto_update_thread = None
        
        # Настройки (загружаем из базы или создаём пустой словарь)
        self.settings = self._load_settings()
        
        # Инициализация сервисов
        self._initialize_services()

    def _load_settings(self):
        # Пример: загрузка настроек из базы, если есть
        if self.database:
            try:
                return self.database.get_all_settings()
            except Exception:
                return {}
        return {}

    def update_settings(self, new_settings):
        # Сохраняет настройки в базу и обновляет self.settings
        try:
            if self.database:
                for category, values in new_settings.items():
                    for key, value in values.items():
                        self.database.save_setting(category, key, value)
                self.settings = self.database.get_all_settings()
                return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
        return False

    def get_bot_status(self):
        # Возвращает структуру статусов сервисов и статистики для интерфейса
        system_status = self.get_system_status()
        stats = self.get_trading_stats()
        return {
            'services': {
                'telegram': system_status['telegram']['connected'],
                'mt5': system_status['mt5']['connected'],
                'gpt': system_status['gpt']['connected'],
                'database': system_status['database']['connected'],
            },
            'bot_running': self.is_running,
            'ai_trader_running': False,  # если есть AI Trader, добавить логику
            'stats': {
                'total_signals': stats.get('total_trades', 0),
                'successful_trades': stats.get('winning_trades', 0),
                'total_profit': stats.get('total_profit', 0.0)
            }
        }
    
    def _initialize_services(self):
        """Инициализация всех сервисов"""
        try:
            # База данных (всегда доступна)
            if DATABASE_AVAILABLE:
                self.database = DatabaseService()
                print("✅ DatabaseService инициализирован")
            
            # MT5 сервис - универсальный режим
            if MT5_AVAILABLE or True:  # Всегда инициализируем MT5Service
                # Загружаем настройки MT5 из базы данных
                mt5_settings = self.settings.get('mt5', {})
                flask_settings = self.settings.get('mt5_server', {})
                
                self.mt5 = MT5Service(
                    path=mt5_settings.get('path', "C:\\Program Files\\MetaTrader 5\\terminal64.exe"),
                    login=mt5_settings.get('login', ""),
                    password=mt5_settings.get('password', ""),
                    server=mt5_settings.get('server', ""),
                    flask_url=flask_settings.get('url', "http://10.211.55.3:5000")
                )
                print("✅ MT5Service инициализирован")
                
                # Автоматически инициализируем MT5 при запуске
                try:
                    success, message = self.mt5.initialize()
                    if success:
                        print(f"✅ MT5 автоматически подключен: {message}")
                    else:
                        print(f"⚠️ MT5 не подключен: {message}")
                except Exception as e:
                    print(f"⚠️ Ошибка автоматического подключения к MT5: {e}")
            
            # Telegram сервис (требует аргументы, инициализируем позже)
            if TELEGRAM_AVAILABLE:
                self.telegram = None  # Инициализируем позже с нужными аргументами
                print("⚠️ TelegramService требует настройки")
            
            # GPT сервис
            if GPT_AVAILABLE:
                self.gpt = GPTService()
                print("✅ GPTService инициализирован")
            
            # Менеджер торговли (инициализируем первым)
            if TRADE_MANAGER_AVAILABLE:
                self.trade_manager = TradeManagerService(
                    mt5_service=self.mt5,
                    database_service=self.database
                )
                print("✅ TradeManagerService инициализирован")
            
            # Обработчик сигналов (инициализируем после trade_manager)
            if SIGNAL_PROCESSOR_AVAILABLE:
                self.signal_processor = SignalProcessor(
                    db_service=self.database,
                    gpt_service=self.gpt,
                    mt5_service=self.mt5,
                    settings={},  # Пустые настройки по умолчанию
                    channels={},  # Пустые каналы по умолчанию
                    page=None  # Страница не нужна для LogicManager
                )
                print("✅ SignalProcessor инициализирован")
            
            # SMC стратегия
            if SMC_AVAILABLE:
                self.smc_strategy = SMCStrategy(mt5_service=self.mt5)
                print("✅ SMCStrategy инициализирован")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации сервисов: {e}")
    
    def start_services(self):
        """Запуск всех сервисов"""
        try:
            # Запуск MT5
            if self.mt5:
                success, message = self.mt5.initialize()
                if success:
                    print(f"✅ MT5 запущен: {message}")
                else:
                    print(f"⚠️ MT5 не запущен: {message}")
            
            # Запуск Telegram
            if self.telegram:
                success, message = self.telegram.initialize()
                if success:
                    print(f"✅ Telegram запущен: {message}")
                else:
                    print(f"⚠️ Telegram не запущен: {message}")
            
            # Запуск GPT
            if self.gpt:
                success, message = self.gpt.initialize()
                if success:
                    print(f"✅ GPT запущен: {message}")
                else:
                    print(f"⚠️ GPT не запущен: {message}")
            
            # Запуск SMC стратегии
            if self.smc_strategy:
                success, message = self.smc_strategy.initialize()
                if success:
                    print(f"✅ SMC стратегия запущена: {message}")
                else:
                    print(f"⚠️ SMC стратегия не запущена: {message}")
            
            # Запуск автообновления
            self._start_auto_update()
            
            self.is_running = True
            print("✅ Все сервисы запущены")
            
        except Exception as e:
            print(f"❌ Ошибка запуска сервисов: {e}")
    
    def stop_services(self):
        """Остановка всех сервисов"""
        try:
            # Остановка SMC стратегии
            if self.smc_strategy:
                self.smc_strategy.stop()
                print("🛑 SMC стратегия остановлена")
            
            # Остановка Telegram
            if self.telegram:
                self.telegram.shutdown()
                print("🛑 Telegram остановлен")
            
            # Остановка MT5
            if self.mt5:
                self.mt5.shutdown()
                print("🛑 MT5 остановлен")
            
            # Остановка автообновления
            self._stop_auto_update()
            
            self.is_running = False
            print("🛑 Все сервисы остановлены")
            
        except Exception as e:
            print(f"❌ Ошибка остановки сервисов: {e}")
    
    def _start_auto_update(self):
        """Запуск автообновления данных"""
        if self.auto_update_thread and self.auto_update_thread.is_alive():
            return
        
        self.auto_update_thread = threading.Thread(target=self._auto_update_loop, daemon=True)
        self.auto_update_thread.start()
        print("✅ Автообновление запущено")
    
    def _stop_auto_update(self):
        """Остановка автообновления"""
        self.is_running = False
        if self.auto_update_thread:
            self.auto_update_thread.join(timeout=5)
        print("🛑 Автообновление остановлено")
    
    def _auto_update_loop(self):
        """Цикл автообновления данных"""
        while self.is_running:
            try:
                # Обновление статистики торговли
                if self.database:
                    stats = self.database.get_trading_stats()
                    # Здесь можно добавить логику обновления UI
                
                # Генерация SMC сигналов
                if self.smc_strategy and self.smc_strategy.is_running:
                    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
                    for symbol in symbols:
                        signals = self.smc_strategy.generate_signals(symbol)
                        for signal in signals:
                            # Сохраняем сигнал в базу
                            if self.database:
                                self.database.add_signal({
                                    'signal_id': f"SMC_{int(time.time())}",
                                    'symbol': signal['symbol'],
                                    'type': signal['type'],
                                    'direction': signal['direction'],
                                    'entry_price': signal['entry_price'],
                                    'stop_loss': signal['stop_loss'],
                                    'take_profit': signal['take_profit'],
                                    'volume': signal['volume'],
                                    'status': 'PENDING',
                                    'timestamp': signal['timestamp'],
                                    'source': 'SMC',
                                    'channel': 'SMC_BOT',
                                    'message_text': f"{signal['direction']} {signal['symbol']} at {signal['entry_price']}"
                                })
                
                # Пауза между обновлениями
                time.sleep(30)  # 30 секунд
                
            except Exception as e:
                print(f"❌ Ошибка автообновления: {e}")
                time.sleep(60)  # Увеличиваем паузу при ошибке
    
    def get_system_status(self):
        """Получение статуса всей системы"""
        return {
            'mt5': {
                'available': MT5_AVAILABLE,
                'connected': self.mt5.is_initialized if self.mt5 else False
            },
            'telegram': {
                'available': TELEGRAM_AVAILABLE,
                'connected': self.telegram.is_connected if self.telegram else False
            },
            'gpt': {
                'available': GPT_AVAILABLE,
                'connected': self.gpt.is_initialized if self.gpt else False
            },
            'signal_processor': {
                'available': SIGNAL_PROCESSOR_AVAILABLE,
                'running': False  # убрано обращение к несуществующему атрибуту
            },
            'trade_manager': {
                'available': TRADE_MANAGER_AVAILABLE,
                'running': self.trade_manager.is_running if self.trade_manager else False
            },
            'database': {
                'available': DATABASE_AVAILABLE,
                'connected': self.database is not None
            },
            'smc_strategy': {
                'available': SMC_AVAILABLE,
                'running': self.smc_strategy.is_running if self.smc_strategy else False
            },
            'system': {
                'running': self.is_running,
                'auto_update': self.auto_update_thread.is_alive() if self.auto_update_thread else False
            }
        }
    
    def get_trading_stats(self):
        """Получение торговой статистики"""
        if self.database:
            return self.database.get_trading_stats()
        return {}
    
    def get_recent_trades(self, limit=10):
        """Получение последних сделок"""
        if self.database:
            return self.database.get_trades(limit=limit)
        return []
    
    def get_recent_signals(self, limit=10):
        """Получение последних сигналов"""
        if self.database:
            return self.database.get_signals(limit=limit)
        return []
    
    def get_signal_history(self, limit=10):
        """Получение истории сигналов (алиас для get_recent_signals)"""
        return self.get_recent_signals(limit)
    
    def get_mt5_positions(self):
        """Получение открытых позиций из MT5"""
        if self.mt5 and self.mt5.is_initialized:
            try:
                # Используем методы MT5Service
                if hasattr(self.mt5, 'get_positions'):
                    return self.mt5.get_positions()
                else:
                    # Демо-режим или метод не реализован
                    return []
            except Exception as e:
                print(f"Ошибка получения позиций MT5: {e}")
                return []
        return []
    
    def get_mt5_account_info(self):
        """Получение информации об аккаунте MT5"""
        if self.mt5 and self.mt5.is_initialized:
            try:
                return self.mt5.get_account_info()
            except Exception as e:
                print(f"Ошибка получения информации об аккаунте MT5: {e}")
                return None
        return None
    
    def get_mt5_deals_history(self, days=7):
        """Получение истории сделок из MT5"""
        if self.mt5 and self.mt5.is_initialized:
            try:
                return self.mt5.get_deals_in_history(days)
            except Exception as e:
                print(f"Ошибка получения истории сделок MT5: {e}")
                return []
        return []
    
    def get_mt5_rates(self, symbol, timeframe, count=100):
        """Получение котировок из MT5"""
        if self.mt5 and self.mt5.is_initialized:
            try:
                return self.mt5.get_rates(symbol, timeframe, count)
            except Exception as e:
                print(f"Ошибка получения котировок MT5: {e}")
                return None
        return None
    
    def update_smc_settings(self, settings):
        """Обновление настроек SMC стратегии"""
        if self.smc_strategy:
            self.smc_strategy.update_settings(settings)
            return True, "Настройки SMC обновлены"
        return False, "SMC стратегия недоступна"
    
    def get_smc_status(self):
        """Получение статуса SMC стратегии"""
        if self.smc_strategy:
            return self.smc_strategy.get_status()
        return {'running': False, 'mt5_available': MT5_AVAILABLE, 'mode': 'Paper', 'active_positions': 0}
    
    def execute_smc_signal(self, signal):
        """Выполнение SMC сигнала"""
        if self.smc_strategy:
            return self.smc_strategy.execute_signal(signal)
        return False, "SMC стратегия недоступна"
    
    def add_channel(self, channel_data):
        """Добавление нового канала"""
        if self.database:
            self.database.add_channel(channel_data)
            return True, "Канал добавлен"
        return False, "База данных недоступна"
    
    def get_channels(self):
        """Получение списка каналов"""
        if self.database:
            return self.database.get_channels()
        return []
    
    def add_log(self, level, source, message):
        """Добавление лога"""
        if self.database:
            self.database.add_log(level, source, message)
    
    def get_logs(self, limit=50):
        """Получение логов"""
        if self.database:
            return self.database.get_logs(limit=limit)
        return [] 