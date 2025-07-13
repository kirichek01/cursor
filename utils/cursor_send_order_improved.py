import requests
import json
import time
from typing import Optional, Dict, Any
import logging
import traceback

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация Flask сервера MT5
MT5_SERVER_CONFIG = {
    'base_url': 'http://10.211.55.3:5000',  # IP Windows машины
    'timeout': 10,
    'retry_attempts': 3,
    'retry_delay': 1
}

print(f"[DEBUG] MT5_SERVER_CONFIG при импорте: {MT5_SERVER_CONFIG}")

class MT5OrderError(Exception):
    """Кастомное исключение для ошибок MT5"""
    pass

def send_order(
    symbol: str, 
    volume: float, 
    order_type: str, 
    price: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    comment: str = "Cursor Bot"
) -> Dict[str, Any]:
    """
    Отправляет ордер в MT5 через Flask сервер
    
    Args:
        symbol: Торговый символ (например, "EURUSD", "XAUUSD")
        volume: Объем позиции (например, 0.1)
        order_type: Тип ордера ("buy", "sell", "buy_limit", "sell_limit", "buy_stop", "sell_stop")
        price: Цена для отложенных ордеров
        sl: Stop Loss
        tp: Take Profit
        comment: Комментарий к ордеру
    
    Returns:
        Dict с результатом выполнения ордера
        
    Raises:
        MT5OrderError: При ошибке отправки или выполнения ордера
    """
    
    # Валидация параметров
    if not symbol or not isinstance(symbol, str):
        raise MT5OrderError("Неверный символ")
    
    if not volume or volume <= 0:
        raise MT5OrderError("Неверный объем")
    
    if order_type not in ["buy", "sell", "buy_limit", "sell_limit", "buy_stop", "sell_stop"]:
        raise MT5OrderError(f"Неверный тип ордера: {order_type}")
    
    # Подготовка данных для отправки
    order_data = {
        "symbol": symbol.upper(),
        "volume": float(volume),
        "order_type": order_type,
        "comment": comment
    }
    
    if price is not None:
        order_data["price"] = float(price)
    if sl is not None:
        order_data["sl"] = float(sl)
    if tp is not None:
        order_data["tp"] = float(tp)
    
    # Отправка запроса с повторными попытками
    for attempt in range(MT5_SERVER_CONFIG['retry_attempts']):
        try:
            logger.info(f"Отправка ордера (попытка {attempt + 1}): {order_data}")
            
            response = requests.post(
                f"{MT5_SERVER_CONFIG['base_url']}/send_order",
                json=order_data,
                timeout=MT5_SERVER_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Ордер успешно отправлен: {result}")
                return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Ошибка сервера: {error_msg}")
                raise MT5OrderError(error_msg)
                
        except requests.exceptions.ConnectionError:
            error_msg = f"Нет подключения к MT5 серверу: {MT5_SERVER_CONFIG['base_url']}"
            logger.error(error_msg)
            if attempt == MT5_SERVER_CONFIG['retry_attempts'] - 1:
                raise MT5OrderError(error_msg)
            time.sleep(MT5_SERVER_CONFIG['retry_delay'])
            
        except requests.exceptions.Timeout:
            error_msg = f"Таймаут подключения к MT5 серверу"
            logger.error(error_msg)
            if attempt == MT5_SERVER_CONFIG['retry_attempts'] - 1:
                raise MT5OrderError(error_msg)
            time.sleep(MT5_SERVER_CONFIG['retry_delay'])
            
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            logger.error(error_msg)
            if attempt == MT5_SERVER_CONFIG['retry_attempts'] - 1:
                raise MT5OrderError(error_msg)
            time.sleep(MT5_SERVER_CONFIG['retry_delay'])
    
    raise MT5OrderError("Все попытки отправки ордера исчерпаны")

def get_account_info() -> Dict[str, Any]:
    """Получает информацию об аккаунте MT5"""
    try:
        response = requests.get(
            f"{MT5_SERVER_CONFIG['base_url']}/account_info",
            timeout=MT5_SERVER_CONFIG['timeout']
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise MT5OrderError(f"Ошибка получения информации об аккаунте: {response.text}")
            
    except Exception as e:
        raise MT5OrderError(f"Ошибка подключения к MT5 серверу: {str(e)}")

def get_positions() -> Dict[str, Any]:
    """Получает открытые позиции"""
    try:
        response = requests.get(
            f"{MT5_SERVER_CONFIG['base_url']}/positions",
            timeout=MT5_SERVER_CONFIG['timeout']
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise MT5OrderError(f"Ошибка получения позиций: {response.text}")
            
    except Exception as e:
        raise MT5OrderError(f"Ошибка подключения к MT5 серверу: {str(e)}")

def close_position(ticket: int) -> Dict[str, Any]:
    """Закрывает позицию по тикету"""
    try:
        response = requests.post(
            f"{MT5_SERVER_CONFIG['base_url']}/close_position",
            json={"ticket": ticket},
            timeout=MT5_SERVER_CONFIG['timeout']
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise MT5OrderError(f"Ошибка закрытия позиции: {response.text}")
            
    except Exception as e:
        raise MT5OrderError(f"Ошибка подключения к MT5 серверу: {str(e)}")

def modify_position(ticket: int, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict[str, Any]:
    """Модифицирует позицию (SL/TP)"""
    try:
        data = {"ticket": ticket}
        if sl is not None:
            data["sl"] = float(sl)
        if tp is not None:
            data["tp"] = float(tp)
            
        response = requests.post(
            f"{MT5_SERVER_CONFIG['base_url']}/modify_position",
            json=data,
            timeout=MT5_SERVER_CONFIG['timeout']
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise MT5OrderError(f"Ошибка модификации позиции: {response.text}")
            
    except Exception as e:
        raise MT5OrderError(f"Ошибка подключения к MT5 серверу: {str(e)}")

def test_connection() -> bool:
    """Тестирует подключение к MT5 серверу"""
    try:
        response = requests.get(
            f"{MT5_SERVER_CONFIG['base_url']}/health",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def update_server_config(new_config: Dict[str, Any]):
    """Обновляет конфигурацию сервера"""
    global MT5_SERVER_CONFIG
    print(f"[DEBUG] update_server_config вызван с: {new_config}")
    print(f"[DEBUG] Стек вызова:\n{''.join(traceback.format_stack(limit=5))}")
    MT5_SERVER_CONFIG.update(new_config)
    logger.info(f"Конфигурация обновлена: {MT5_SERVER_CONFIG}")

# Примеры использования
if __name__ == "__main__":
    # Тест подключения
    if test_connection():
        print("✅ Подключение к MT5 серверу установлено")
        
        # Получение информации об аккаунте
        try:
            account_info = get_account_info()
            print(f"💰 Баланс: {account_info.get('balance', 'N/A')}")
        except MT5OrderError as e:
            print(f"❌ Ошибка получения информации об аккаунте: {e}")
        
        # Отправка тестового ордера
        try:
            result = send_order("EURUSD", 0.01, "buy", comment="Test from Cursor")
            print(f"✅ Тестовый ордер отправлен: {result}")
        except MT5OrderError as e:
            print(f"❌ Ошибка отправки ордера: {e}")
    else:
        print("❌ Нет подключения к MT5 серверу")
        print(f"Проверьте, что Flask сервер запущен на {MT5_SERVER_CONFIG['base_url']}") 