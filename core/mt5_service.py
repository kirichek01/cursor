import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime, timedelta

class MT5Service:
    """
    Manages all interactions with the MetaTrader 5 terminal.
    This final version includes all safety checks, logging, and required functions.
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
        if not self.is_initialized: return False, "MT5 not initialized."
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
        if not self.is_initialized: return False, "MT5 not initialized."
        request = {"action": mt5.TRADE_ACTION_REMOVE, "order": int(ticket)}
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, f"Successfully cancelled pending order {ticket}."
        else:
            return False, f"Failed to cancel order {ticket}: {result.comment}"
            
    def move_sl_to_breakeven(self, position, pips_offset=5):
        if not self.is_initialized or not position: return False, "Position not found"
        symbol_info = mt5.symbol_info(position.symbol)
        if not symbol_info: return False, f"Could not get info for {position.symbol}"
        if position.type == mt5.ORDER_TYPE_BUY: new_sl_price = position.price_open + (pips_offset * symbol_info.point)
        elif position.type == mt5.ORDER_TYPE_SELL: new_sl_price = position.price_open - (pips_offset * symbol_info.point)
        else: return False, "Unsupported position type for breakeven."
        normalized_sl = self._normalize_price(new_sl_price, symbol_info)
        request = {"action": mt5.TRADE_ACTION_SLTP, "position": position.ticket, "sl": normalized_sl, "tp": position.tp}
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE: return True, f"Successfully moved SL for ticket {position.ticket}."
        else: return False, f"Failed to modify SL for ticket {position.ticket}: {result.comment}"

    def modify_position_sltp(self, ticket, new_sl=None, new_tp=None):
        if not self.is_initialized: return False, "MT5 not initialized."
        if new_sl is None and new_tp is None: return False, "No new SL or TP provided."
        try:
            positions = mt5.positions_get(ticket=ticket)
            if not positions: return False, f"No open position found for ticket {ticket}."
            position = positions[0]
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info: return False, f"Could not get info for {position.symbol}"
            sl_to_set = new_sl if new_sl is not None else position.sl
            tp_to_set = new_tp if new_tp is not None else position.tp
            normalized_sl = self._normalize_price(sl_to_set, symbol_info)
            normalized_tp = self._normalize_price(tp_to_set, symbol_info)
            request = {"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": normalized_sl, "tp": normalized_tp}
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE: return True, f"Successfully modified position for ticket {ticket}."
            else: return False, f"Failed to modify position for ticket {ticket}: {result.comment}"
        except Exception as e: return False, f"Error modifying position for ticket {ticket}: {e}"

    def place_order(self, signal_data, volume_per_tp, source_comment="CombineTradeBot"):
        if not self.is_initialized:
            msg = "MT5 not initialized."; self._log_error(msg); return False, msg
        
        raw_symbol = signal_data.get('symbol'); symbol = self._format_symbol(raw_symbol)
        if not symbol:
            msg = "Signal is missing a symbol."; self._log_error(msg); return False, msg
            
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            msg = f"Symbol '{symbol}' not found in MarketWatch."; self._log_error(msg); return False, msg
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                msg = f"Failed to select/enable symbol '{symbol}'."; self._log_error(msg); return False, msg
            time.sleep(0.1); symbol_info = mt5.symbol_info(symbol)
        
        order_type_str = signal_data.get('order_type', '').upper()
        entry_price = signal_data.get('entry_price')
        sl = signal_data.get('stop_loss')
        tps = signal_data.get('take_profits', [])
        
        if not tps and not sl:
             msg = "Signal has no Take Profit or Stop Loss levels."; self._log_error(msg); return False, msg
        if not tps: tps = [] # Ensure tps is a list even if it's missing, for market orders with only SL

        order_map = {"BUY": (mt5.ORDER_TYPE_BUY, mt5.TRADE_ACTION_DEAL), "SELL": (mt5.ORDER_TYPE_SELL, mt5.TRADE_ACTION_DEAL), "BUY_LIMIT": (mt5.ORDER_TYPE_BUY_LIMIT, mt5.TRADE_ACTION_PENDING), "SELL_LIMIT": (mt5.ORDER_TYPE_SELL_LIMIT, mt5.TRADE_ACTION_PENDING), "BUY_STOP": (mt5.ORDER_TYPE_BUY_STOP, mt5.TRADE_ACTION_PENDING), "SELL_STOP": (mt5.ORDER_TYPE_SELL_STOP, mt5.TRADE_ACTION_PENDING)}
        if order_type_str not in order_map:
            msg = f"Invalid order_type: '{order_type_str}'"; self._log_error(msg); return False, msg
        mt5_order_type, action = order_map[order_type_str]
        
        is_buy_order = "BUY" in order_type_str
        
        price = 0.0
        if action == mt5.TRADE_ACTION_DEAL:
            price = mt5.symbol_info_tick(symbol).ask if is_buy_order else mt5.symbol_info_tick(symbol).bid
            if not price or price == 0:
                msg = f"Invalid market price for {symbol} (is zero)."; self._log_error(msg); return False, msg
        else:
            if not entry_price:
                msg = f"Pending order '{order_type_str}' requires an entry_price."; self._log_error(msg); return False, msg
            price = entry_price
        
        if sl is not None and sl != 0:
            if is_buy_order and sl >= price:
                msg = f"Invalid Stop Loss for BUY order. SL ({sl}) must be below price ({price})."; self._log_error(msg); return False, msg
            if not is_buy_order and sl <= price:
                msg = f"Invalid Stop Loss for SELL order. SL ({sl}) must be above price ({price})."; self._log_error(msg); return False, msg

        tps_to_process = tps if tps else [0.0] # If no TPs, create one dummy entry to place one order with only SL
        
        successful_tickets = []
        for tp_level in tps_to_process:
            if tp_level != 0:
                if is_buy_order and tp_level <= price:
                    msg = f"Invalid Take Profit for BUY order. TP ({tp_level}) must be above price ({price})."; self._log_error(msg); return False, msg
                if not is_buy_order and tp_level >= price:
                    msg = f"Invalid Take Profit for SELL order. TP ({tp_level}) must be below price ({price})."; self._log_error(msg); return False, msg
            
            stops_level_dist = symbol_info.trade_stops_level * symbol_info.point
            if stops_level_dist > 0:
                if sl is not None and sl != 0 and abs(price - sl) < stops_level_dist:
                    msg = f"Stop Loss is too close to price. Minimum distance is {stops_level_dist}"; self._log_error(msg); return False, msg
                if tp_level != 0 and abs(price - tp_level) < stops_level_dist:
                    msg = f"Take Profit {tp_level} is too close to price. Minimum distance is {stops_level_dist}"; self._log_error(msg); return False, msg
        
        tick = mt5.symbol_info_tick(symbol)
        if tick: print(f"--- [MT5] DIAGNOSTIC: Current prices for {symbol}: Bid={tick.bid}, Ask={tick.ask}")
        else: print(f"--- [MT5] DIAGNOSTIC: Could not retrieve current tick for {symbol}.")

        for tp_level in tps_to_process:
            request = {
                "action": action, "symbol": symbol, "volume": float(volume_per_tp),
                "type": mt5_order_type, "price": self._normalize_price(price, symbol_info),
                "sl": self._normalize_price(sl, symbol_info), "tp": self._normalize_price(tp_level, symbol_info),
                "deviation": 20, "magic": 234000, "comment": source_comment,
                "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_message = f"Order failed for TP {tp_level}: {result.comment} (retcode: {result.retcode})"
                self._log_error(error_message); return False, error_message
            else:
                print(f"--- [MT5] Order successful for TP {tp_level}. Ticket: {result.order} ---")
                successful_tickets.append(result.order)
        
        if successful_tickets:
            return True, f"Successfully placed orders with tickets: {successful_tickets}"
        else:
            return False, "Failed to place any orders."