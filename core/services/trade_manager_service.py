import json
import sqlite3
from datetime import datetime
import threading
import time

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 не найден. TradeManagerService будет работать в демо-режиме.")

# Импорт функции send_order для интеграции с MT5 через Flask
try:
    from utils.cursor_send_order_improved import send_order, get_account_info, get_positions, close_position, modify_position, test_connection, update_server_config
    CURSOR_MT5_AVAILABLE = True
    print("✅ Интеграция с MT5 через Flask доступна")
except ImportError:
    CURSOR_MT5_AVAILABLE = False
    print("⚠️ Интеграция с MT5 через Flask недоступна")

class TradeManagerService:
    """
    Улучшенный сервис управления торговлей с интеграцией MT5 через Flask
    """
    
    def __init__(self, mt5_service=None, database_service=None):
        self.mt5_service = mt5_service
        self.database_service = database_service
        self.is_running = False
        self.trading_thread = None
        
        # Настройки торговли
        self.trading_settings = {
            'risk_per_trade': 2.0,  # % от баланса
            'max_positions': 5,
            'default_lot_size': 0.1,
            'use_cursor_mt5': True,  # Использовать интеграцию через Flask
            'mt5_server_ip': '10.211.55.3',  # IP виртуалки Windows
            'mt5_server_port': 5000
        }
        
        # Инициализация интеграции с MT5 через Flask
        if CURSOR_MT5_AVAILABLE:
            self._setup_cursor_mt5_integration()
    
    def _setup_cursor_mt5_integration(self):
        """Настройка интеграции с MT5 через Flask"""
        try:
            # Обновляем конфигурацию сервера
            server_config = {
                'base_url': f'http://{self.trading_settings["mt5_server_ip"]}:{self.trading_settings["mt5_server_port"]}'
            }
            update_server_config(server_config)
            
            # Тестируем подключение
            if test_connection():
                print("✅ Подключение к MT5 серверу установлено")
            else:
                print("⚠️ Нет подключения к MT5 серверу")
                
        except Exception as e:
            print(f"❌ Ошибка настройки интеграции с MT5: {e}")
    
    def _init_mt5(self):
        """Инициализация MT5 (локальная или через Flask)"""
        if CURSOR_MT5_AVAILABLE and self.trading_settings['use_cursor_mt5']:
            # Используем интеграцию через Flask
            if test_connection():
                return True, "MT5 подключен через Flask сервер"
            else:
                return False, "Нет подключения к MT5 серверу"
        elif MT5_AVAILABLE and self.mt5_service:
            # Используем локальное подключение
            return self.mt5_service.initialize()
        else:
            return False, "MT5 недоступен"
    
    def start_trading(self):
        """Запуск торговли"""
        if self.is_running:
            return False, "Торговля уже запущена"
        
        success, message = self._init_mt5()
        if not success:
            return False, f"Ошибка инициализации MT5: {message}"
        
        self.is_running = True
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        
        return True, "Торговля запущена"
    
    def stop_trading(self):
        """Остановка торговли"""
        self.is_running = False
        if self.trading_thread:
            self.trading_thread.join(timeout=5)
        return True, "Торговля остановлена"
    
    def _trading_loop(self):
        """Основной цикл торговли"""
        while self.is_running:
            try:
                # Проверяем новые сигналы
                if self.database_service:
                    signals = self.database_service.get_signals(status='PENDING', limit=10)
                    for signal in signals:
                        self._process_signal(signal)
                
                # Обновляем открытые позиции
                self._update_positions()
                
                time.sleep(5)  # Пауза между проверками
                
            except Exception as e:
                print(f"❌ Ошибка в торговом цикле: {e}")
                time.sleep(10)
    
    def _process_signal(self, signal_data):
        """Обработка торгового сигнала"""
        try:
            symbol = signal_data[2]  # symbol
            direction = signal_data[3]  # direction
            entry_price = signal_data[4]  # entry_price
            sl = signal_data[5]  # stop_loss
            tp = signal_data[6]  # take_profit
            volume = signal_data[7]  # volume
            
            # Определяем тип ордера
            order_type = "buy" if direction == "LONG" else "sell"
            
            # Отправляем ордер
            result = self._place_order(symbol, volume, order_type, entry_price, sl, tp)
            
            if result['success']:
                # Обновляем статус сигнала
                if self.database_service:
                    self.database_service.update_signal(signal_data[1], {'status': 'EXECUTED'})
                
                # Сохраняем сделку
                trade_data = {
                    'trade_id': f"TRADE_{int(time.time())}",
                    'symbol': symbol,
                    'type': 'SIGNAL',
                    'direction': direction,
                    'entry_price': entry_price,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'volume': volume,
                    'status': 'OPEN',
                    'timestamp': datetime.now(),
                    'source': 'TradeManager',
                    'comment': f"Signal: {signal_data[1]}"
                }
                
                if self.database_service:
                    self.database_service.add_trade(trade_data)
                
                print(f"✅ Ордер выполнен: {symbol} {direction} {volume}")
            else:
                print(f"❌ Ошибка выполнения ордера: {result['error']}")
                
        except Exception as e:
            print(f"❌ Ошибка обработки сигнала: {e}")
    
    def _place_order(self, symbol, volume, order_type, price=None, sl=None, tp=None):
        """Размещение ордера"""
        try:
            if CURSOR_MT5_AVAILABLE and self.trading_settings['use_cursor_mt5']:
                # Используем интеграцию через Flask
                return send_order(symbol, volume, order_type, price, sl, tp, "Cursor Bot")
            elif MT5_AVAILABLE and self.mt5_service:
                # Используем локальное подключение
                return self.mt5_service.place_order({
                    'symbol': symbol,
                    'volume': volume,
                    'order_type': order_type,
                    'price': price,
                    'sl': sl,
                    'tp': tp
                })
            else:
                return {'success': False, 'error': 'MT5 недоступен'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update_positions(self):
        """Обновление информации о позициях"""
        try:
            if CURSOR_MT5_AVAILABLE and self.trading_settings['use_cursor_mt5']:
                positions_result = get_positions()
                if positions_result['success']:
                    positions = positions_result['positions']
                    # Обновляем позиции в базе данных
                    for pos in positions:
                        self._update_position_in_db(pos)
            elif MT5_AVAILABLE and self.mt5_service:
                # Используем локальное подключение
                positions = self.mt5_service.get_open_positions()
                for pos in positions:
                    self._update_position_in_db(pos)
                    
        except Exception as e:
            print(f"❌ Ошибка обновления позиций: {e}")
    
    def _update_position_in_db(self, position_data):
        """Обновление позиции в базе данных"""
        if self.database_service:
            try:
                # Проверяем, есть ли уже такая позиция
                trades = self.database_service.get_trades(status='OPEN')
                position_exists = False
                
                for trade in trades:
                    if trade[1] == position_data.get('ticket'):  # trade_id
                        # Обновляем существующую позицию
                        updates = {
                            'exit_price': position_data.get('price_current'),
                            'profit_loss': position_data.get('profit')
                        }
                        self.database_service.update_trade(trade[1], updates)
                        position_exists = True
                        break
                
                if not position_exists:
                    # Добавляем новую позицию
                    trade_data = {
                        'trade_id': str(position_data.get('ticket')),
                        'symbol': position_data.get('symbol'),
                        'type': 'POSITION',
                        'direction': position_data.get('type'),
                        'entry_price': position_data.get('price_open'),
                        'exit_price': position_data.get('price_current'),
                        'stop_loss': position_data.get('sl'),
                        'take_profit': position_data.get('tp'),
                        'volume': position_data.get('volume'),
                        'status': 'OPEN',
                        'profit_loss': position_data.get('profit'),
                        'timestamp': datetime.now(),
                        'source': 'MT5',
                        'comment': position_data.get('comment', '')
                    }
                    self.database_service.add_trade(trade_data)
                    
            except Exception as e:
                print(f"❌ Ошибка обновления позиции в БД: {e}")
    
    def get_account_info(self):
        """Получение информации об аккаунте"""
        try:
            if CURSOR_MT5_AVAILABLE and self.trading_settings['use_cursor_mt5']:
                return get_account_info()
            elif MT5_AVAILABLE and self.mt5_service:
                return self.mt5_service.get_account_info()
            else:
                return {'success': False, 'error': 'MT5 недоступен'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def close_position_by_ticket(self, ticket):
        """Закрытие позиции по тикету"""
        try:
            if CURSOR_MT5_AVAILABLE and self.trading_settings['use_cursor_mt5']:
                return close_position(ticket)
            elif MT5_AVAILABLE and self.mt5_service:
                return self.mt5_service.close_position_by_ticket(ticket)
            else:
                return {'success': False, 'error': 'MT5 недоступен'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def modify_position_sltp(self, ticket, new_sl=None, new_tp=None):
        """Модификация SL/TP позиции"""
        try:
            if CURSOR_MT5_AVAILABLE and self.trading_settings['use_cursor_mt5']:
                return modify_position(ticket, new_sl, new_tp)
            elif MT5_AVAILABLE and self.mt5_service:
                return self.mt5_service.modify_position_sltp(ticket, new_sl, new_tp)
            else:
                return {'success': False, 'error': 'MT5 недоступен'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_settings(self, new_settings):
        """Обновление настроек торговли"""
        self.trading_settings.update(new_settings)
        
        # Обновляем конфигурацию MT5 сервера если изменились настройки
        if CURSOR_MT5_AVAILABLE and 'mt5_server_ip' in new_settings:
            self._setup_cursor_mt5_integration()
        
        return True, "Настройки обновлены"
    
    def get_status(self):
        """Получение статуса торгового менеджера"""
        return {
            'running': self.is_running,
            'mt5_available': MT5_AVAILABLE,
            'cursor_mt5_available': CURSOR_MT5_AVAILABLE,
            'use_cursor_mt5': self.trading_settings['use_cursor_mt5'],
            'server_ip': self.trading_settings['mt5_server_ip'],
            'server_port': self.trading_settings['mt5_server_port']
        } 