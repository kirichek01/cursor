from flask import Flask, request, jsonify
import MetaTrader5 as mt5
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class MT5ServerEnhanced:
    """Расширенный сервер для работы с MT5 - только реальные данные"""
    
    def __init__(self, config_file='mt5_config.json'):
        self.initialized = False
        self.account_info = None
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Загрузка конфигурации из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"✅ Конфигурация загружена из {self.config_file}")
                return config
            else:
                logger.warning(f"⚠️ Файл конфигурации {self.config_file} не найден")
                return {}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            return {}
    
    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                # Убираем комментарии при сохранении
                config_to_save = {k: v for k, v in self.config.items() if k != 'comments'}
                json.dump(config_to_save, f, ensure_ascii=False, indent=4)
            logger.info(f"✅ Конфигурация сохранена в {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения конфигурации: {e}")
        
    def initialize(self, path: str = None, login: int = None, password: str = None, server: str = None):
        """Инициализация подключения к MT5"""
        try:
            # Используем параметры из конфигурации если не переданы
            path = path or self.config.get('mt5_path')
            login = login or self.config.get('login')
            password = password or self.config.get('password')
            server = server or self.config.get('server')
            
            # Путь к MT5 обязателен для реального подключения
            if not path:
                error_msg = "❌ Path to MT5 terminal is required for real connection"
                logger.error(error_msg)
                return False, error_msg
                
            logger.info(f"🔌 Инициализация MT5 по пути: {path}")
            
            if not mt5.initialize(path=path):
                error = mt5.last_error()
                logger.error(f"MT5 initialize() failed: {error}")
                return False, f"Ошибка инициализации MT5: {error}"
            
            # Если указаны данные для входа
            if login and password and server:
                logger.info(f"🔐 Вход в аккаунт {login} на сервере {server}")
                if not mt5.login(login, password, server):
                    error = mt5.last_error()
                    logger.error(f"MT5 login() failed: {error}")
                    return False, f"Ошибка входа в MT5: {error}"
            
            # Получаем информацию об аккаунте
            self.account_info = mt5.account_info()
            if self.account_info:
                logger.info(f"✅ Подключен к реальному аккаунту: {self.account_info.login}")
                logger.info(f"💰 Баланс: {self.account_info.balance} {self.account_info.currency}")
                logger.info(f"🏦 Сервер: {self.account_info.server}")
            else:
                return False, "Не удалось получить информацию о реальном аккаунте"
            
            self.initialized = True
            
            # Сохраняем успешную конфигурацию
            if path: self.config['mt5_path'] = path
            if login: self.config['login'] = login
            if server: self.config['server'] = server
            # Пароль не сохраняем в конфиг для безопасности
            self.save_config()
            
            return True, f"MT5 успешно инициализирован с реальными данными (Аккаунт: {self.account_info.login})"
            
        except Exception as e:
            logger.error(f"Ошибка инициализации MT5: {e}")
            return False, str(e)
    
    def shutdown(self):
        """Закрытие подключения к MT5"""
        if self.initialized:
            mt5.shutdown()
            self.initialized = False
            logger.info("🔌 MT5 соединение закрыто")
    
    def validate_connection(self):
        """Проверка состояния подключения"""
        if not self.initialized:
            return False, "MT5 не инициализирован"
        
        # Проверяем, что подключение все еще активно
        try:
            account_info = mt5.account_info()
            if account_info:
                return True, "Подключение активно"
            else:
                self.initialized = False
                return False, "Подключение потеряно"
        except Exception as e:
            self.initialized = False
            return False, f"Ошибка проверки подключения: {e}"
    
    def get_account_info(self) -> Dict[str, Any]:
        """Получение информации об аккаунте"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Проверяем подключение
        connected, message = self.validate_connection()
        if not connected:
            return {"success": False, "error": message}
        
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
                    "margin_level": account_info.margin_level,
                    "server": account_info.server,
                    "real_account": True
                }
            else:
                return {"success": False, "error": "Не удалось получить информацию об аккаунте"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_positions(self) -> Dict[str, Any]:
        """Получение открытых позиций"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Проверяем подключение
        connected, message = self.validate_connection()
        if not connected:
            return {"success": False, "error": message}
        
        try:
            positions = mt5.positions_get()
            if positions is not None:
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
                        "comment": pos.comment,
                        "time": datetime.fromtimestamp(pos.time).isoformat()
                    })
                return {"success": True, "positions": positions_data, "count": len(positions_data)}
            else:
                return {"success": True, "positions": [], "count": 0}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_rates(self, symbol: str, timeframe: str, count: int = 10) -> Dict[str, Any]:
        """Получение котировок"""
        if not self.initialized:
            return {"success": False, "error": "MT5 не инициализирован"}
        
        # Проверяем подключение
        connected, message = self.validate_connection()
        if not connected:
            return {"success": False, "error": message}
        
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
                    "open": float(rate['open']),
                    "high": float(rate['high']),
                    "low": float(rate['low']),
                    "close": float(rate['close']),
                    "tick_volume": int(rate['tick_volume'])
                })
            
            return {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "rates": rates_data,
                "count": len(rates_data)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Создаем экземпляр сервера
mt5_server = MT5ServerEnhanced()

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния сервера"""
    connected, message = mt5_server.validate_connection() if mt5_server.initialized else (False, "Not initialized")
    
    return jsonify({
        "status": "ok",
        "mt5_initialized": mt5_server.initialized,
        "mt5_connected": connected,
        "connection_message": message,
        "real_data_only": True,
        "timestamp": datetime.now().isoformat(),
        "config_loaded": bool(mt5_server.config)
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

@app.route('/shutdown', methods=['POST'])
def shutdown_mt5():
    """Закрытие соединения с MT5"""
    mt5_server.shutdown()
    return jsonify({"success": True, "message": "MT5 соединение закрыто"})

@app.route('/config', methods=['GET'])
def get_config():
    """Получение текущей конфигурации (без паролей)"""
    safe_config = {k: v for k, v in mt5_server.config.items() if k not in ['password', 'comments']}
    return jsonify({
        "success": True,
        "config": safe_config,
        "config_file": mt5_server.config_file
    })

if __name__ == '__main__':
    logger.info("🚀 Расширенный MT5 сервер запущен. Только реальные данные!")
    logger.info("📋 Используйте /initialize endpoint для подключения к MT5")
    logger.info("🔧 Используйте /config endpoint для проверки конфигурации")
    
    # Автоинициализация если настроена
    if mt5_server.config.get('auto_initialize', False):
        logger.info("🔄 Автоматическая инициализация...")
        success, message = mt5_server.initialize()
        if success:
            logger.info(f"✅ {message}")
        else:
            logger.warning(f"⚠️ {message}")
    
    # Запуск Flask сервера с настройками из конфигурации
    host = mt5_server.config.get('host', '0.0.0.0')
    port = mt5_server.config.get('port', 5000)
    debug = mt5_server.config.get('debug', False)
    
    app.run(host=host, port=port, debug=debug)