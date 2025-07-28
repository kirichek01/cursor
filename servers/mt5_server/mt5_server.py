from flask import Flask, request, jsonify
import MetaTrader5 as mt5
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class MT5Server:
    """Сервер для работы с MT5 - только реальные данные"""
    
    def __init__(self):
        self.initialized = False
        self.account_info = None
        
    def initialize(self, path: str = None, login: int = None, password: str = None, server: str = None):
        """Инициализация подключения к MT5"""
        try:
            # Путь к MT5 обязателен для реального подключения
            if not path:
                error_msg = "❌ Path to MT5 terminal is required for real connection"
                logger.error(error_msg)
                return False, error_msg
                
            if not mt5.initialize(path=path):
                logger.error(f"MT5 initialize() failed: {mt5.last_error()}")
                return False, f"Ошибка инициализации MT5: {mt5.last_error()}"
            
            # Если указаны данные для входа
            if login and password and server:
                if not mt5.login(login, password, server):
                    logger.error(f"MT5 login() failed: {mt5.last_error()}")
                    return False, f"Ошибка входа в MT5: {mt5.last_error()}"
            
            # Получаем информацию об аккаунте
            self.account_info = mt5.account_info()
            if self.account_info:
                logger.info(f"Подключен к реальному аккаунту: {self.account_info.login}")
            else:
                return False, "Не удалось получить информацию о реальном аккаунте"
            
            self.initialized = True
            return True, "MT5 успешно инициализирован с реальными данными"
            
        except Exception as e:
            logger.error(f"Ошибка инициализации MT5: {e}")
            return False, str(e)
    
    def shutdown(self):
        """Закрытие подключения к MT5"""
        if self.initialized:
            mt5.shutdown()
            self.initialized = False
            logger.info("MT5 соединение закрыто")
    
    # Demo methods removed - only real MT5 data supported
    
    def send_order(self, symbol: str, volume: float, order_type: str, 
                   price: Optional[float] = None, sl: Optional[float] = None, 
                   tp: Optional[float] = None, comment: str = "Cursor Bot") -> Dict[str, Any]:
        """Отправка ордера в MT5"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Only real orders supported
        
        try:
            # Выбираем символ
            if not mt5.symbol_select(symbol, True):
                return {"success": False, "error": f"Не удалось выбрать символ {symbol}"}
            
            # Получаем информацию о символе
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return {"success": False, "error": f"Не удалось получить информацию о символе {symbol}"}
            
            # Определяем тип ордера
            if order_type == "buy":
                action = mt5.TRADE_ACTION_DEAL
                order_type_mt5 = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
            elif order_type == "sell":
                action = mt5.TRADE_ACTION_DEAL
                order_type_mt5 = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
            elif order_type == "buy_limit":
                action = mt5.TRADE_ACTION_PENDING
                order_type_mt5 = mt5.ORDER_TYPE_BUY_LIMIT
            elif order_type == "sell_limit":
                action = mt5.TRADE_ACTION_PENDING
                order_type_mt5 = mt5.ORDER_TYPE_SELL_LIMIT
            elif order_type == "buy_stop":
                action = mt5.TRADE_ACTION_PENDING
                order_type_mt5 = mt5.ORDER_TYPE_BUY_STOP
            elif order_type == "sell_stop":
                action = mt5.TRADE_ACTION_PENDING
                order_type_mt5 = mt5.ORDER_TYPE_SELL_STOP
            else:
                return {"success": False, "error": f"Неизвестный тип ордера: {order_type}"}
            
            # Нормализация цены
            point = symbol_info.point
            digits = symbol_info.digits
            price = round(price, digits)
            if sl:
                sl = round(sl, digits)
            if tp:
                tp = round(tp, digits)
            
            # Формируем запрос
            request_data = {
                "action": action,
                "symbol": symbol,
                "volume": volume,
                "type": order_type_mt5,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            if sl:
                request_data["sl"] = sl
            if tp:
                request_data["tp"] = tp
            
            # Отправляем ордер
            result = mt5.order_send(request_data)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Ордер успешно отправлен: {result}")
                return {
                    "success": True,
                    "ticket": result.order,
                    "volume": result.volume,
                    "price": result.price,
                    "comment": result.comment,
                    "retcode": result.retcode
                }
            else:
                error_msg = f"Ошибка отправки ордера: {result.comment} (код: {result.retcode})"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Ошибка отправки ордера: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_account_info(self) -> Dict[str, Any]:
        """Получение информации об аккаунте"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Only real account info supported
        
        try:
            account_info = mt5.account_info()
            if account_info:
                return {
                    "success": True,
                    "login": account_info.login,
                    "balance": account_info.balance,
                    "equity": account_info.equity,
                    "profit": account_info.profit,
                    "currency": account_info.currency,
                    "leverage": account_info.leverage,
                    "margin": account_info.margin,
                    "margin_free": account_info.margin_free,
                    "margin_level": account_info.margin_level
                }
            else:
                return {"success": False, "error": "Не удалось получить информацию об аккаунте"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_positions(self) -> Dict[str, Any]:
        """Получение открытых позиций"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Only real positions supported
        
        try:
            positions = mt5.positions_get()
            if positions:
                positions_data = []
                for pos in positions:
                    positions_data.append({
                        "ticket": pos.ticket,
                        "symbol": pos.symbol,
                        "type": "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
                        "volume": pos.volume,
                        "price_open": pos.price_open,
                        "price_current": pos.price_current,
                        "sl": pos.sl,
                        "tp": pos.tp,
                        "profit": pos.profit,
                        "comment": pos.comment
                    })
                return {"success": True, "positions": positions_data}
            else:
                return {"success": True, "positions": []}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_rates(self, symbol: str, timeframe: str, count: int = 10) -> Dict[str, Any]:
        """Получение котировок"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Only real rates supported
        
        try:
            # Преобразуем timeframe в формат MT5
            tf_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_M1)
            
            # Получаем котировки
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if rates is None:
                return {"success": False, "error": f"Не удалось получить котировки для {symbol}"}
            
            # Преобразуем в JSON-совместимый формат
            rates_data = []
            for rate in rates:
                rates_data.append({
                    "time": datetime.fromtimestamp(rate['time']).isoformat(),
                    "open": rate['open'],
                    "high": rate['high'],
                    "low": rate['low'],
                    "close": rate['close'],
                    "tick_volume": rate['tick_volume']
                })
            
            return {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "rates": rates_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_position(self, ticket: int) -> Dict[str, Any]:
        """Закрытие позиции по тикету"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Only real position closing supported
        
        try:
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                return {"success": False, "error": f"Позиция с тикетом {ticket} не найдена"}
            
            position = positions[0]
            symbol = position.symbol
            volume = position.volume
            order_type = position.type
            
            # Определяем тип закрытия
            close_action_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "symbol": symbol,
                "volume": volume,
                "type": close_action_type,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "Closed by Cursor Bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return {"success": True, "message": f"Позиция {ticket} успешно закрыта"}
            else:
                return {"success": False, "error": f"Ошибка закрытия позиции: {result.comment}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def modify_position(self, ticket: int, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict[str, Any]:
        """Модификация позиции (SL/TP)"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Only real position modification supported
        
        try:
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                return {"success": False, "error": f"Позиция с тикетом {ticket} не найдена"}
            
            position = positions[0]
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info:
                return {"success": False, "error": f"Не удалось получить информацию о символе {position.symbol}"}
            
            # Нормализация цен
            digits = symbol_info.digits
            sl_to_set = round(sl, digits) if sl is not None else position.sl
            tp_to_set = round(tp, digits) if tp is not None else position.tp
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "sl": sl_to_set,
                "tp": tp_to_set
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return {"success": True, "message": f"Позиция {ticket} успешно модифицирована"}
            else:
                return {"success": False, "error": f"Ошибка модификации позиции: {result.comment}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# Создаем экземпляр сервера
mt5_server = MT5Server()

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния сервера"""
    return jsonify({
        "status": "ok",
        "mt5_initialized": mt5_server.initialized,
        "real_data_only": True,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/initialize', methods=['POST'])
def initialize_mt5():
    """Инициализация MT5"""
    data = request.get_json() or {}
    path = data.get('path')
    login = data.get('login')
    password = data.get('password')
    server = data.get('server')
    
    success, message = mt5_server.initialize(path, login, password, server)
    return jsonify({"success": success, "message": message})

@app.route('/send_order', methods=['POST'])
def send_order():
    """Отправка ордера"""
    data = request.get_json()
    
    symbol = data.get('symbol')
    volume = data.get('volume')
    order_type = data.get('order_type')
    price = data.get('price')
    sl = data.get('sl')
    tp = data.get('tp')
    comment = data.get('comment', 'Cursor Bot')
    
    result = mt5_server.send_order(symbol, volume, order_type, price, sl, tp, comment)
    return jsonify(result)

@app.route('/account_info', methods=['GET'])
def get_account_info():
    """Получение информации об аккаунте"""
    result = mt5_server.get_account_info()
    return jsonify(result)

@app.route('/positions', methods=['GET'])
def get_positions():
    """Получение открытых позиций"""
    result = mt5_server.get_positions()
    return jsonify(result)

@app.route('/rates', methods=['GET'])
def get_rates():
    """Получение котировок"""
    symbol = request.args.get('symbol', 'EURUSD')
    timeframe = request.args.get('timeframe', 'M1')
    count = int(request.args.get('count', 10))
    
    result = mt5_server.get_rates(symbol, timeframe, count)
    return jsonify(result)

@app.route('/close_position', methods=['POST'])
def close_position():
    """Закрытие позиции"""
    data = request.get_json()
    ticket = data.get('ticket')
    
    result = mt5_server.close_position(ticket)
    return jsonify(result)

@app.route('/modify_position', methods=['POST'])
def modify_position():
    """Модификация позиции"""
    data = request.get_json()
    ticket = data.get('ticket')
    sl = data.get('sl')
    tp = data.get('tp')
    
    result = mt5_server.modify_position(ticket, sl, tp)
    return jsonify(result)

@app.route('/shutdown', methods=['POST'])
def shutdown_mt5():
    """Закрытие соединения с MT5"""
    mt5_server.shutdown()
    return jsonify({"success": True, "message": "MT5 соединение закрыто"})

if __name__ == '__main__':
    logger.info("🚀 MT5 сервер запущен. Ожидание подключения к реальному MT5...")
    logger.info("📋 Используйте /initialize endpoint для подключения к MT5")
    
    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=5000, debug=False) 