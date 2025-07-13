import sys
import os
import time
import pandas as pd
import requests
from datetime import datetime, timedelta

# Импорт MetaTrader5 с обработкой ошибки
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    print("⚠️ MetaTrader5 не найден. MT5Service будет работать через Flask API.")
    MT5_AVAILABLE = False
    mt5 = None

class MT5Service:
    """
    Универсальный MT5Service для работы с MetaTrader 5.
    Поддерживает два режима:
    1. Локальный (через библиотеку MetaTrader5) - для Windows
    2. Удалённый (через Flask API) - для macOS/Linux
    """
    def __init__(self, path="", login="", password="", server="", flask_url=""):
        self.path = path
        self.login = login
        self.password = password
        self.server = server
        self.flask_url = flask_url
        self.is_initialized = False
        self.mode = self._determine_mode()
        
    def _determine_mode(self):
        """Определяет режим работы: локальный или через Flask API"""
        if MT5_AVAILABLE:
            if self.login and self.password and self.server:
                return "local"  # Локальный режим с данными для входа
            else:
                return "auto"   # Автоматический режим (к уже открытому MT5)
        elif self.flask_url:
            return "flask"  # Flask API режим
        else:
            return "demo"   # Демо режим
    
    def _log_error(self, message):
        print(f"--- [MT5] ERROR: {message} ---")

    def initialize(self):
        """Инициализация MT5 в зависимости от режима"""
        try:
            if self.mode == "local":
                return self._initialize_local()
            elif self.mode == "auto":
                return self._initialize_auto()
            elif self.mode == "flask":
                return self._initialize_flask()
            else:
                return True, "MT5 работает в демо-режиме"
        except Exception as e:
            return False, f"Ошибка инициализации MT5: {e}"
    
    def _initialize_local(self):
        """Инициализация локального MT5 с данными для входа"""
        if not MT5_AVAILABLE:
            return False, "MetaTrader5 недоступен"
        
        try:
            if not mt5.initialize(path=self.path):
                return False, f"MT5 initialize() failed: {mt5.last_error()}"
            
            account_info = mt5.account_info()
            if account_info and account_info.login == int(self.login):
                self.is_initialized = True
                return True, "MT5 connected (already logged in)."
            
            if not mt5.login(int(self.login), self.password, self.server):
                return False, f"MT5 login() failed: {mt5.last_error()}"
            
            self.is_initialized = True
            return True, "MT5 connected and logged in successfully."
        except Exception as e:
            return False, f"Ошибка инициализации локального MT5: {e}"
    
    def _initialize_auto(self):
        """Автоматическое подключение к уже открытому MT5"""
        if not MT5_AVAILABLE:
            return False, "MetaTrader5 недоступен"
        
        try:
            # Пытаемся подключиться к уже запущенному MT5
            if not mt5.initialize():
                return False, f"MT5 initialize() failed: {mt5.last_error()}"
            
            # Проверяем, есть ли активный аккаунт
            account_info = mt5.account_info()
            if account_info:
                self.is_initialized = True
                return True, f"MT5 connected to account {account_info.login} ({account_info.server})"
            else:
                return False, "MT5 запущен, но нет активного аккаунта"
                
        except Exception as e:
            return False, f"Ошибка автоматического подключения к MT5: {e}"
    
    def _initialize_flask(self):
        """Инициализация через Flask API"""
        try:
            # Проверяем доступность Flask сервера
            print(f"[DEBUG] Проверяем Flask сервер: {self.flask_url}/health")
            response = requests.get(f"{self.flask_url}/health", timeout=5)
            print(f"[DEBUG] Ответ Flask сервера: {response.status_code} - {response.text}")
            if response.status_code == 200:
                self.is_initialized = True
                return True, "MT5 connected via Flask API"
            else:
                return False, f"Flask сервер недоступен: {response.status_code}"
        except Exception as e:
            return False, f"Ошибка подключения к Flask API: {e}"

    def shutdown(self):
        """Завершение работы MT5"""
        if self.mode == "local" and self.is_initialized and MT5_AVAILABLE:
            mt5.shutdown()
        self.is_initialized = False

    def get_account_info(self):
        """Получение информации об аккаунте"""
        if not self.is_initialized:
            return None
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    info = mt5.account_info()
                    return info._asdict() if info else None
            elif self.mode == "flask":
                print(f"[DEBUG] Запрашиваем информацию об аккаунте: {self.flask_url}/account_info")
                response = requests.get(f"{self.flask_url}/account_info", timeout=10)
                print(f"[DEBUG] Ответ account_info: {response.status_code} - {response.text}")
                if response.status_code == 200:
                    return response.json()
            else:
                # Демо режим
                return {"demo": True, "balance": 10000, "equity": 10000}
        except Exception as e:
            self._log_error(f"Ошибка получения информации об аккаунте: {e}")
            return None

    def get_positions(self):
        """Получение всех открытых позиций"""
        if not self.is_initialized:
            return []
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    positions = mt5.positions_get()
                    return [pos._asdict() for pos in positions] if positions else []
            elif self.mode == "flask":
                response = requests.get(f"{self.flask_url}/positions", timeout=10)
                if response.status_code == 200:
                    return response.json()
            else:
                return []  # Демо режим
        except Exception as e:
            self._log_error(f"Ошибка получения позиций: {e}")
            return []

    def get_open_positions_by_ticket(self, tickets):
        """Получение позиций по тикетам"""
        if not self.is_initialized or not tickets:
            return []
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    return mt5.positions_get(tickets=tickets)
            elif self.mode == "flask":
                response = requests.post(f"{self.flask_url}/positions_by_tickets", 
                                      json={"tickets": tickets}, timeout=10)
                if response.status_code == 200:
                    return response.json()
            else:
                return []
        except Exception as e:
            self._log_error(f"Ошибка получения позиций по тикетам: {e}")
            return []

    def get_historical_data(self, symbol, timeframe, start_date, end_date):
        """Получение исторических данных для бэктеста"""
        if not self.is_initialized:
            return None
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    # Преобразуем таймфрейм из строки в константу MT5
                    tf_map = {
                        "M1": mt5.TIMEFRAME_M1,
                        "M5": mt5.TIMEFRAME_M5,
                        "M15": mt5.TIMEFRAME_M15,
                        "M30": mt5.TIMEFRAME_M30,
                        "H1": mt5.TIMEFRAME_H1,
                        "H4": mt5.TIMEFRAME_H4,
                        "D1": mt5.TIMEFRAME_D1
                    }
                    mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
                    
                    # Выбираем символ
                    if not mt5.symbol_select(symbol, True):
                        self._log_error(f"Could not select {symbol}")
                        return None
                    
                    # Получаем исторические данные
                    rates = mt5.copy_rates_range(symbol, mt5_timeframe, start_date, end_date)
                    if rates is None or len(rates) == 0:
                        return None
                    
                    return rates
            elif self.mode == "flask":
                response = requests.get(f"{self.flask_url}/historical_data", 
                                     params={
                                         "symbol": symbol, 
                                         "timeframe": timeframe,
                                         "start_date": start_date.isoformat(),
                                         "end_date": end_date.isoformat()
                                     }, 
                                     timeout=30)
                if response.status_code == 200:
                    return response.json()
            else:
                # Демо режим - генерируем демо-данные
                return self._generate_demo_historical_data(symbol, timeframe, start_date, end_date)
        except Exception as e:
            self._log_error(f"Ошибка получения исторических данных для {symbol}: {e}")
            return None
    
    def _generate_demo_historical_data(self, symbol, timeframe, start_date, end_date):
        """Генерация демо исторических данных"""
        import numpy as np
        
        # Определяем количество баров в зависимости от таймфрейма
        tf_minutes = {
            "M1": 1, "M5": 5, "M15": 15, "M30": 30,
            "H1": 60, "H4": 240, "D1": 1440
        }
        minutes = tf_minutes.get(timeframe, 60)
        
        # Рассчитываем количество баров
        time_diff = end_date - start_date
        total_minutes = time_diff.total_seconds() / 60
        num_bars = int(total_minutes / minutes)
        
        # Базовая цена для разных символов
        base_prices = {
            "EURUSD": 1.1000, "GBPUSD": 1.3000, "USDJPY": 110.00,
            "AUDUSD": 0.7500, "USDCAD": 1.2500, "XAUUSD": 1800.00
        }
        base_price = base_prices.get(symbol, 1.0000)
        
        # Генерируем данные
        np.random.seed(42)
        rates = []
        current_time = start_date
        current_price = base_price
        
        for i in range(num_bars):
            # Генерируем изменение цены
            volatility = 0.0005 if symbol != "XAUUSD" else 0.005
            change = np.random.normal(0, volatility)
            current_price += change
            
            # OHLC
            open_price = current_price
            high_price = current_price + abs(np.random.normal(0, volatility/2))
            low_price = current_price - abs(np.random.normal(0, volatility/2))
            close_price = current_price + np.random.normal(0, volatility/3)
            
            rates.append({
                'time': int(current_time.timestamp()),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'tick_volume': np.random.randint(100, 1000),
                'spread': np.random.randint(1, 5),
                'real_volume': 0
            })
            
            current_time += timedelta(minutes=minutes)
            current_price = close_price
        
        return rates

    def get_rates(self, symbol, timeframe, count=10):
        """Получение котировок"""
        if not self.is_initialized:
            return None
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    if not mt5.symbol_select(symbol, True):
                        self._log_error(f"Could not select {symbol}")
                    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
                    if rates is None or len(rates) == 0:
                        return None
                    rates_df = pd.DataFrame(rates)
                    rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
                    return rates_df
            elif self.mode == "flask":
                response = requests.get(f"{self.flask_url}/rates", 
                                     params={"symbol": symbol, "timeframe": timeframe, "count": count}, 
                                     timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return pd.DataFrame(data)
            else:
                return self._get_demo_rates(symbol, count)
        except Exception as e:
            self._log_error(f"Ошибка получения котировок для {symbol}: {e}")
            return None

    def _get_demo_rates(self, symbol, count=10):
        """Демо-данные для macOS"""
        import numpy as np
        from datetime import datetime, timedelta
        
        base_price = 1.2000 if "EUR" in symbol else 1.3000 if "GBP" in symbol else 110.0
        dates = [datetime.now() - timedelta(minutes=i) for i in range(count, 0, -1)]
        
        # Генерируем демо-данные
        np.random.seed(42)
        prices = [base_price]
        for i in range(1, count):
            change = np.random.normal(0, 0.0005)
            prices.append(prices[-1] + change)
        
        data = {
            'time': dates,
            'open': prices,
            'high': [p + abs(np.random.normal(0, 0.0002)) for p in prices],
            'low': [p - abs(np.random.normal(0, 0.0002)) for p in prices],
            'close': prices,
            'tick_volume': [np.random.randint(100, 1000) for _ in range(count)]
        }
        
        return pd.DataFrame(data)

    def get_deals_in_history(self, days=1):
        """Получение истории сделок"""
        if not self.is_initialized:
            return []
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    date_from = datetime.now() - timedelta(days=days)
                    date_to = datetime.now()
                    return mt5.history_deals_get(date_from, date_to)
            elif self.mode == "flask":
                response = requests.get(f"{self.flask_url}/deals_history", 
                                     params={"days": days}, timeout=10)
                if response.status_code == 200:
                    return response.json()
            else:
                return []  # Демо режим
        except Exception as e:
            self._log_error(f"Ошибка получения истории сделок: {e}")
            return []

    def close_position_by_ticket(self, ticket):
        """Закрытие позиции по тикету"""
        if not self.is_initialized:
            return False, "MT5 не инициализирован"
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    positions = mt5.positions_get(ticket=ticket)
                    if not positions:
                        return False, f"Позиция с тикетом {ticket} не найдена"
                    
                    position = positions[0]
                    symbol = position.symbol
                    volume = position.volume
                    order_type = position.type
                    close_action_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                    price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
                    
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL, "position": ticket, "symbol": symbol,
                        "volume": volume, "type": close_action_type, "price": price, "deviation": 20,
                        "magic": 234000, "comment": "Closed by Bot", "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        return True, f"Позиция {ticket} успешно закрыта"
                    else:
                        return False, f"Ошибка закрытия позиции {ticket}: {result.comment}"
            elif self.mode == "flask":
                response = requests.post(f"{self.flask_url}/close_position", 
                                      json={"ticket": ticket}, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("success", False), result.get("message", "Неизвестная ошибка")
                else:
                    return False, f"Ошибка Flask API: {response.status_code}"
            else:
                return True, f"Демо: Позиция {ticket} закрыта"
        except Exception as e:
            return False, f"Ошибка закрытия позиции {ticket}: {e}"

    def cancel_pending_order(self, ticket):
        """Отмена отложенного ордера"""
        # Реализация отмены отложенного ордера
        pass

    def move_sl_to_breakeven(self, position, pips_offset=5):
        """Перенос SL в безубыток"""
        # Реализация переноса SL в безубыток
        pass

    def modify_position_sltp(self, ticket, new_sl=None, new_tp=None):
        """Модификация SL/TP позиции"""
        if not self.is_initialized:
            return False, "MT5 не инициализирован"
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    positions = mt5.positions_get(ticket=ticket)
                    if not positions:
                        return False, f"Позиция с тикетом {ticket} не найдена"
                    
                    position = positions[0]
                    symbol_info = mt5.symbol_info(position.symbol)
                    if not symbol_info:
                        return False, f"Не удалось получить информацию о {position.symbol}"
                    
                    sl_to_set = new_sl if new_sl is not None else position.sl
                    tp_to_set = new_tp if new_tp is not None else position.tp
                    
                    request = {"action": mt5.TRADE_ACTION_SLTP, "position": ticket, 
                             "sl": sl_to_set, "tp": tp_to_set}
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        return True, f"SL/TP позиции {ticket} успешно изменены"
                    else:
                        return False, f"Ошибка изменения SL/TP: {result.comment}"
            elif self.mode == "flask":
                response = requests.post(f"{self.flask_url}/modify_position", 
                                      json={"ticket": ticket, "sl": new_sl, "tp": new_tp}, 
                                      timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("success", False), result.get("message", "Неизвестная ошибка")
                else:
                    return False, f"Ошибка Flask API: {response.status_code}"
            else:
                return True, f"Демо: SL/TP позиции {ticket} изменены"
        except Exception as e:
            return False, f"Ошибка изменения SL/TP позиции {ticket}: {e}"

    def place_order(self, signal_data, volume_per_tp, source_comment="CombineTradeBot"):
        """Размещение ордера"""
        if not self.is_initialized:
            return False, "MT5 не инициализирован"
        
        try:
            if self.mode == "local":
                if MT5_AVAILABLE:
                    # Реализация размещения ордера через локальный MT5
                    pass
            elif self.mode == "flask":
                response = requests.post(f"{self.flask_url}/place_order", 
                                      json={"signal_data": signal_data, "volume": volume_per_tp, 
                                           "comment": source_comment}, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("success", False), result.get("message", "Неизвестная ошибка")
                else:
                    return False, f"Ошибка Flask API: {response.status_code}"
            else:
                return True, "Демо: Ордер размещён"
        except Exception as e:
            return False, f"Ошибка размещения ордера: {e}" 