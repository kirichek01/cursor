import sys
import os
import time
import pandas as pd
from datetime import datetime, timedelta

# Попытка импортировать MetaTrader5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

IS_WINDOWS = sys.platform.startswith('win')

class DummyMT5Service:
    """
    Dummy-реализация MT5Service для macOS/Linux или если MetaTrader5 не установлен.
    Возвращает тестовые данные из dummy_data.csv или фиксированные значения.
    """
    def __init__(self, path, login, password, server):
        self.is_initialized = True
        self.dummy_data_path = os.path.join(os.path.dirname(__file__), '..', 'dummy_data.csv')

    def initialize(self):
        return True, "Dummy MT5 initialized."

    def shutdown(self):
        pass

    def get_account_info(self):
        return {
            'login': 123456,
            'balance': 10000.0,
            'equity': 10000.0,
            'currency': 'USD',
            'leverage': 100,
        }

    def get_open_positions_by_ticket(self, tickets):
        return []

    def get_rates(self, symbol, timeframe, count=10):
        # Пробуем загрузить dummy_data.csv
        try:
            df = pd.read_csv(self.dummy_data_path)
            if len(df) > count:
                df = df.tail(count)
            df['time'] = pd.to_datetime(df['time'])
            return df
        except Exception:
            # Возвращаем фиктивные данные
            now = datetime.now()
            data = {
                'time': [now - timedelta(minutes=15*i) for i in range(count)][::-1],
                'open': [1900.0]*count,
                'high': [1910.0]*count,
                'low': [1890.0]*count,
                'close': [1905.0]*count,
                'tick_volume': [100]*count,
            }
            return pd.DataFrame(data)

    def get_deals_in_history(self, days=1):
        return []

    def close_position_by_ticket(self, ticket):
        return True, f"Dummy: closed position {ticket}"

    def cancel_pending_order(self, ticket):
        return True, f"Dummy: cancelled order {ticket}"

    def move_sl_to_breakeven(self, position, pips_offset=5):
        return True, f"Dummy: moved SL to breakeven for {getattr(position, 'ticket', 0)}"

    def modify_position_sltp(self, ticket, new_sl=None, new_tp=None):
        return True, f"Dummy: modified SL/TP for {ticket}"

    def place_order(self, signal_data, volume_per_tp, source_comment="CombineTradeBot"):
        return True, f"Dummy: order placed for {signal_data.get('symbol', 'XAUUSD')}"

# Основной класс MT5Service
if MT5_AVAILABLE and IS_WINDOWS:
    class MT5Service:
        """
        Реальная реализация MT5Service для Windows с установленным MetaTrader5.
        """
        def __init__(self, path, login, password, server):
            self.path = path
            self.login = login
            self.password = password
            self.server = server
            self.is_initialized = False

        def _log_error(self, message):
            """Helper to print errors."""
            print(f"--- [MT5] ERROR: {message} ---")

        def _normalize_price(self, price, symbol_info):
            """A more robust price normalization function."""
            if price is None or price == 0.0:
                return 0.0
            
            point = symbol_info.point
            if point == 0:
                return round(price, symbol_info.digits)

            price_in_points = int(round(price / point))
            normalized_price = price_in_points * point
            
            return round(normalized_price, symbol_info.digits)

        def _format_symbol(self, symbol):
            if not isinstance(symbol, str):
                return None
            return symbol.replace("/", "").replace("-", "").replace("#", "").upper()

        def initialize(self):
            try:
                if not mt5.initialize(path=self.path):
                    return False, f"MT5 initialize() failed: {mt5.last_error()}"
                account_info = mt5.account_info()
                if account_info and account_info.login == int(self.login):
                    self.is_initialized = True
                    return True, "MT5 connected (already logged in)."
                if not self.login:
                    return False, "Not logged in. Provide login details in Settings."
                if not mt5.login(int(self.login), self.password, self.server):
                    return False, f"MT5 login() failed: {mt5.last_error()}"
                self.is_initialized = True
                return True, "MT5 connected and logged in successfully."
            except Exception as e:
                return False, f"An error occurred during MT5 initialization: {e}"

        def shutdown(self):
            if self.is_initialized:
                mt5.shutdown()

        def get_account_info(self):
            if not self.is_initialized:
                return None
            info = mt5.account_info()
            return info._asdict() if info else None
        
        def get_open_positions_by_ticket(self, tickets):
            if not self.is_initialized or not tickets:
                return []
            try:
                return mt5.positions_get(tickets=tickets)
            except Exception:
                return []

        def get_rates(self, symbol, timeframe, count=10):
            if not self.is_initialized:
                return None
            try:
                if not mt5.symbol_select(symbol, True):
                    self._log_error(f"Could not select {symbol}, trying to get rates anyway.")
                rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
                if rates is None or len(rates) == 0:
                    return None
                rates_df = pd.DataFrame(rates)
                rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
                return rates_df
            except Exception as e:
                self._log_error(f"Error getting rates for {symbol}: {e}")
                return None

        def get_deals_in_history(self, days=1):
            """Gets closed deals from the specified number of days ago."""
            if not self.is_initialized:
                return None
            date_from = datetime.now() - timedelta(days=days)
            date_to = datetime.now()
            try:
                return mt5.history_deals_get(date_from, date_to)
            except Exception as e:
                self._log_error(f"Could not get history deals: {e}")
                return None

        def close_position_by_ticket(self, ticket):
            if not self.is_initialized:
                return False, "MT5 not initialized."
            try:
                positions = mt5.positions_get(ticket=ticket)
                if not positions:
                    return False, f"No open position found for ticket {ticket}."
                
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
                    return True, f"Successfully closed position for ticket {ticket}."
                else:
                    return False, f"Failed to close position for ticket {ticket}: {result.comment}"
            except Exception as e:
                return False, f"Error closing position for ticket {ticket}: {e}"

        def cancel_pending_order(self, ticket):
            if not self.is_initialized:
                return False, "MT5 not initialized."
            request = {"action": mt5.TRADE_ACTION_REMOVE, "order": int(ticket)}
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return True, f"Successfully cancelled pending order {ticket}."
            else:
                return False, f"Failed to cancel order {ticket}: {result.comment}"
            
        def move_sl_to_breakeven(self, position, pips_offset=5):
            if not self.is_initialized or not position:
                return False, "Position not found"
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info:
                return False, f"Could not get info for {position.symbol}"
            if position.type == mt5.ORDER_TYPE_BUY:
                new_sl_price = position.price_open + (pips_offset * symbol_info.point)
            elif position.type == mt5.ORDER_TYPE_SELL:
                new_sl_price = position.price_open - (pips_offset * symbol_info.point)
            else:
                return False, "Unsupported position type for breakeven."
            normalized_sl = self._normalize_price(new_sl_price, symbol_info)
            request = {"action": mt5.TRADE_ACTION_SLTP, "position": position.ticket, "sl": normalized_sl, "tp": position.tp}
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return True, f"Successfully moved SL for ticket {position.ticket}."
            else:
                return False, f"Failed to modify SL for ticket {position.ticket}: {result.comment}"

        def modify_position_sltp(self, ticket, new_sl=None, new_tp=None):
            if not self.is_initialized:
                return False, "MT5 not initialized."
            if new_sl is None and new_tp is None:
                return False, "No new SL or TP provided."
            try:
                positions = mt5.positions_get(ticket=ticket)
                if not positions:
                    return False, f"No open position found for ticket {ticket}."
                position = positions[0]
                symbol_info = mt5.symbol_info(position.symbol)
                if not symbol_info:
                    return False, f"Could not get info for {position.symbol}"
                sl_to_set = new_sl if new_sl is not None else position.sl
                tp_to_set = new_tp if new_tp is not None else position.tp
                normalized_sl = self._normalize_price(sl_to_set, symbol_info)
                normalized_tp = self._normalize_price(tp_to_set, symbol_info)
                request = {"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": normalized_sl, "tp": normalized_tp}
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    return True, f"Successfully modified position for ticket {ticket}."
                else:
                    return False, f"Failed to modify position for ticket {ticket}: {result.comment}"
            except Exception as e:
                return False, f"Error modifying position for ticket {ticket}: {e}"

        def place_order(self, signal_data, volume_per_tp, source_comment="CombineTradeBot"):
            if not self.is_initialized:
                msg = "MT5 not initialized."
                self._log_error(msg)
                return False, msg
            
            raw_symbol = signal_data.get('symbol')
            symbol = self._format_symbol(raw_symbol)
            if not symbol:
                msg = "Signal is missing a symbol."
                self._log_error(msg)
                return False, msg
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                msg = f"Symbol '{symbol}' not found in MarketWatch."
                self._log_error(msg)
                return False, msg
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    msg = f"Failed to select/enable symbol '{symbol}'."
                    self._log_error(msg)
                    return False, msg
                time.sleep(0.1)
                symbol_info = mt5.symbol_info(symbol)
            
            order_type_str = signal_data.get('order_type', '').upper()
            entry_price = signal_data.get('entry_price')
            sl = signal_data.get('stop_loss')
            tps = signal_data.get('take_profits', [])
            
            if not tps and not sl:
                 msg = "Signal has no Take Profit or Stop Loss levels."
                 self._log_error(msg)
                 return False, msg
            if not tps:
                tps = [] # Ensure tps is a list even if it's missing, for market orders with only SL

            order_map = {
                "BUY": (mt5.ORDER_TYPE_BUY, mt5.TRADE_ACTION_DEAL),
                "SELL": (mt5.ORDER_TYPE_SELL, mt5.TRADE_ACTION_DEAL),
                "BUY_LIMIT": (mt5.ORDER_TYPE_BUY_LIMIT, mt5.TRADE_ACTION_PENDING),
                "SELL_LIMIT": (mt5.ORDER_TYPE_SELL_LIMIT, mt5.TRADE_ACTION_PENDING),
                "BUY_STOP": (mt5.ORDER_TYPE_BUY_STOP, mt5.TRADE_ACTION_PENDING),
                "SELL_STOP": (mt5.ORDER_TYPE_SELL_STOP, mt5.TRADE_ACTION_PENDING)
            }
            
            if order_type_str not in order_map:
                msg = f"Unsupported order type: {order_type_str}"
                self._log_error(msg)
                return False, msg
            
            order_type, action_type = order_map[order_type_str]
            
            # Get current market price for market orders
            if action_type == mt5.TRADE_ACTION_DEAL:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    msg = f"Could not get tick data for {symbol}"
                    self._log_error(msg)
                    return False, msg
                entry_price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
            
            if not entry_price:
                msg = f"No entry price provided for {order_type_str} order"
                self._log_error(msg)
                return False, msg

            # Normalize prices
            normalized_entry = self._normalize_price(entry_price, symbol_info)
            normalized_sl = self._normalize_price(sl, symbol_info) if sl else 0.0
            
            # Place orders for each TP level
            tickets = []
            for i, tp in enumerate(tps):
                normalized_tp = self._normalize_price(tp, symbol_info)
                
                request = {
                    "action": action_type,
                    "symbol": symbol,
                    "volume": volume_per_tp,
                    "type": order_type,
                    "price": normalized_entry,
                    "sl": normalized_sl,
                    "tp": normalized_tp,
                    "deviation": 20,
                    "magic": 234000,
                    "comment": f"{source_comment}_TP{i+1}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    tickets.append(result.order)
                else:
                    msg = f"Failed to place order for TP {tp}: {result.comment}"
                    self._log_error(msg)
                    return False, msg
            
            if tickets:
                return True, f"Orders placed successfully. Tickets: [{', '.join(map(str, tickets))}]"
            else:
                return False, "No orders were placed."
else:
    MT5Service = DummyMT5Service 