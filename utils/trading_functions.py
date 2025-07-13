import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Импорт функции send_order
try:
    from utils.cursor_send_order_improved import send_order, test_connection, get_account_info
    CURSOR_MT5_AVAILABLE = True
except ImportError:
    CURSOR_MT5_AVAILABLE = False
    print("⚠️ Функция send_order недоступна")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def place_trade(symbol: str, volume: float, order_type: str, 
                price: Optional[float] = None, sl: Optional[float] = None, 
                tp: Optional[float] = None, comment: str = "Cursor Bot") -> Dict[str, Any]:
    """
    Автоматическое размещение торгового ордера
    
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
    """
    
    if not CURSOR_MT5_AVAILABLE:
        return {
            'success': False, 
            'error': 'Интеграция с MT5 через Flask недоступна. Проверьте файл cursor_send_order_improved.py'
        }
    
    # Проверяем подключение к MT5 серверу
    if not test_connection():
        return {
            'success': False, 
            'error': 'Нет подключения к MT5 серверу. Проверьте, что Flask сервер запущен на Windows VM'
        }
    
    try:
        logger.info(f"Отправка ордера: {symbol}, объем: {volume}, тип: {order_type}")
        
        # Отправляем ордер через Flask сервер
        result = send_order(symbol, volume, order_type, price, sl, tp, comment)
        
        if result.get('success'):
            logger.info(f"✅ Ордер успешно отправлен и исполнен: {result}")
            
            # Дополнительная логика после успешного выполнения ордера
            _log_trade_success(symbol, volume, order_type, result)
            
            return result
        else:
            logger.error(f"❌ Ошибка отправки ордера: {result.get('error')}")
            return result
            
    except Exception as e:
        error_msg = f"Неожиданная ошибка при отправке ордера: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}

def _log_trade_success(symbol: str, volume: float, order_type: str, result: Dict[str, Any]):
    """Логирование успешной сделки"""
    try:
        # Получаем информацию об аккаунте для статистики
        account_info = get_account_info()
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'volume': volume,
            'order_type': order_type,
            'ticket': result.get('ticket'),
            'price': result.get('price'),
            'account_balance': account_info.get('balance') if account_info.get('success') else 'N/A',
            'account_equity': account_info.get('equity') if account_info.get('success') else 'N/A'
        }
        
        logger.info(f"📊 Статистика сделки: {log_data}")
        
        # Здесь можно добавить сохранение в базу данных или отправку уведомлений
        
    except Exception as e:
        logger.error(f"Ошибка логирования сделки: {e}")

def place_multiple_trades(trades_list: list) -> Dict[str, Any]:
    """
    Размещение нескольких ордеров одновременно
    
    Args:
        trades_list: Список словарей с параметрами ордеров
        [
            {'symbol': 'EURUSD', 'volume': 0.1, 'order_type': 'buy', 'sl': 1.2000, 'tp': 1.2100},
            {'symbol': 'GBPUSD', 'volume': 0.05, 'order_type': 'sell', 'sl': 1.3000, 'tp': 1.2900}
        ]
    
    Returns:
        Dict с результатами выполнения всех ордеров
    """
    
    if not CURSOR_MT5_AVAILABLE:
        return {
            'success': False,
            'error': 'Интеграция с MT5 через Flask недоступна'
        }
    
    results = {
        'success': True,
        'total_orders': len(trades_list),
        'successful_orders': 0,
        'failed_orders': 0,
        'orders': []
    }
    
    for i, trade in enumerate(trades_list):
        try:
            logger.info(f"Отправка ордера {i+1}/{len(trades_list)}: {trade}")
            
            result = place_trade(
                symbol=trade['symbol'],
                volume=trade['volume'],
                order_type=trade['order_type'],
                price=trade.get('price'),
                sl=trade.get('sl'),
                tp=trade.get('tp'),
                comment=trade.get('comment', f'Batch order {i+1}')
            )
            
            results['orders'].append({
                'order_index': i+1,
                'trade_params': trade,
                'result': result
            })
            
            if result.get('success'):
                results['successful_orders'] += 1
            else:
                results['failed_orders'] += 1
                
            # Пауза между ордерами
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Ошибка отправки ордера {i+1}: {e}")
            results['orders'].append({
                'order_index': i+1,
                'trade_params': trade,
                'result': {'success': False, 'error': str(e)}
            })
            results['failed_orders'] += 1
    
    if results['failed_orders'] > 0:
        results['success'] = False
    
    logger.info(f"Результаты пакетной отправки: {results['successful_orders']} успешно, {results['failed_orders']} неудачно")
    return results

def test_mt5_connection() -> Dict[str, Any]:
    """Тестирование подключения к MT5 серверу"""
    if not CURSOR_MT5_AVAILABLE:
        return {
            'success': False,
            'error': 'Интеграция с MT5 через Flask недоступна'
        }
    
    try:
        # Проверяем подключение
        if test_connection():
            # Получаем информацию об аккаунте
            account_info = get_account_info()
            
            return {
                'success': True,
                'connection': 'OK',
                'account_info': account_info if account_info.get('success') else None,
                'message': 'Подключение к MT5 серверу установлено'
            }
        else:
            return {
                'success': False,
                'error': 'Нет подключения к MT5 серверу',
                'message': 'Проверьте, что Flask сервер запущен на Windows VM'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Ошибка тестирования подключения'
        }

def get_trading_status() -> Dict[str, Any]:
    """Получение статуса торговой системы"""
    return {
        'cursor_mt5_available': CURSOR_MT5_AVAILABLE,
        'connection_test': test_mt5_connection(),
        'timestamp': datetime.now().isoformat()
    }

# Примеры использования
if __name__ == "__main__":
    # Тест подключения
    print("🔍 Тестирование подключения к MT5...")
    connection_test = test_mt5_connection()
    print(f"Результат: {connection_test}")
    
    if connection_test['success']:
        print("✅ Подключение установлено, тестируем отправку ордера...")
        
        # Тестовый ордер
        result = place_trade("EURUSD", 0.01, "buy", comment="Test from Cursor")
        print(f"Результат отправки: {result}")
        
        # Пакетная отправка
        trades = [
            {'symbol': 'EURUSD', 'volume': 0.01, 'order_type': 'buy', 'sl': 1.2000, 'tp': 1.2100},
            {'symbol': 'GBPUSD', 'volume': 0.01, 'order_type': 'sell', 'sl': 1.3000, 'tp': 1.2900}
        ]
        
        batch_result = place_multiple_trades(trades)
        print(f"Результат пакетной отправки: {batch_result}")
    else:
        print("❌ Нет подключения к MT5 серверу")
        print("Убедитесь, что:")
        print("1. Flask сервер запущен на Windows VM")
        print("2. IP адрес настроен правильно в cursor_send_order_improved.py")
        print("3. Сетевые порты открыты") 