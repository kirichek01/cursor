#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации интеграции Cursor с MT5 через Flask сервер
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cursor_mt5_integration():
    """Тестирование интеграции с MT5"""
    print("🧾 Тестирование интеграции Cursor с MT5 через Flask сервер")
    print("=" * 60)
    
    # Проверяем доступность модулей
    print("\n1. Проверка доступности модулей:")
    
    try:
        from utils.cursor_send_order_improved import send_order, test_connection
        print("✅ Модуль cursor_send_order_improved доступен")
        cursor_available = True
    except ImportError as e:
        print(f"❌ Модуль cursor_send_order_improved недоступен: {e}")
        cursor_available = False
    
    try:
        from utils.trading_functions import place_trade, test_mt5_connection
        print("✅ Модуль trading_functions доступен")
        trading_available = True
    except ImportError as e:
        print(f"❌ Модуль trading_functions недоступен: {e}")
        trading_available = False
    
    # Тестируем подключение к MT5 серверу
    print("\n2. Тестирование подключения к MT5 серверу:")
    
    if cursor_available:
        try:
            connection_status = test_connection()
            if connection_status:
                print("✅ Подключение к MT5 серверу установлено")
                
                # Тестируем отправку ордера
                print("\n3. Тестирование отправки ордера:")
                try:
                    result = send_order("EURUSD", 0.01, "buy", comment="Test from Cursor")
                    if result.get('success'):
                        print(f"✅ Тестовый ордер отправлен успешно: {result}")
                    else:
                        print(f"❌ Ошибка отправки ордера: {result.get('error')}")
                except Exception as e:
                    print(f"❌ Ошибка при отправке ордера: {e}")
            else:
                print("❌ Нет подключения к MT5 серверу")
                print("Убедитесь, что:")
                print("  - Flask сервер запущен на Windows VM")
                print("  - IP адрес настроен правильно")
                print("  - Сетевые порты открыты")
        except Exception as e:
            print(f"❌ Ошибка тестирования подключения: {e}")
    
    # Демонстрация функций торговли
    print("\n4. Демонстрация функций торговли:")
    
    if trading_available:
        try:
            # Тест функции place_trade
            print("Тестирование функции place_trade...")
            trade_result = place_trade("XAUUSD", 0.01, "buy", comment="Demo trade")
            print(f"Результат: {trade_result}")
            
            # Тест пакетной отправки
            print("\nТестирование пакетной отправки...")
            from utils.trading_functions import place_multiple_trades
            
            trades = [
                {'symbol': 'EURUSD', 'volume': 0.01, 'order_type': 'buy', 'sl': 1.2000, 'tp': 1.2100},
                {'symbol': 'GBPUSD', 'volume': 0.01, 'order_type': 'sell', 'sl': 1.3000, 'tp': 1.2900}
            ]
            
            batch_result = place_multiple_trades(trades)
            print(f"Результат пакетной отправки: {batch_result}")
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании функций торговли: {e}")
    
    # Интеграция с TradeManagerService
    print("\n5. Интеграция с TradeManagerService:")
    
    try:
        from services.trade_manager_service import TradeManagerService
        print("✅ TradeManagerService доступен")
        
        # Создаем экземпляр торгового менеджера
        trade_manager = TradeManagerService()
        
        # Получаем статус
        status = trade_manager.get_status()
        print(f"Статус торгового менеджера: {status}")
        
        # Тестируем подключение
        account_info = trade_manager.get_account_info()
        print(f"Информация об аккаунте: {account_info}")
        
    except Exception as e:
        print(f"❌ Ошибка интеграции с TradeManagerService: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено")
    
    # Рекомендации
    print("\n📋 Рекомендации:")
    print("1. Для полной работы необходимо запустить Flask сервер на Windows VM")
    print("2. Обновите IP адрес в utils/cursor_send_order_improved.py")
    print("3. Убедитесь, что MT5 запущен и авторизован на Windows VM")
    print("4. Проверьте сетевые настройки между macOS и Windows VM")

def demonstrate_usage():
    """Демонстрация использования"""
    print("\n📚 Примеры использования:")
    print("-" * 40)
    
    print("\n1. Простая отправка ордера:")
    print("""
from utils.trading_functions import place_trade

result = place_trade("EURUSD", 0.1, "buy")
if result['success']:
    print("✅ Ордер выполнен")
else:
    print(f"❌ Ошибка: {result['error']}")
    """)
    
    print("\n2. Ордер с SL/TP:")
    print("""
result = place_trade(
    symbol="XAUUSD",
    volume=0.1,
    order_type="buy",
    sl=1950.0,
    tp=2000.0,
    comment="Gold trade"
)
    """)
    
    print("\n3. Пакетная отправка:")
    print("""
from utils.trading_functions import place_multiple_trades

trades = [
    {'symbol': 'EURUSD', 'volume': 0.1, 'order_type': 'buy'},
    {'symbol': 'GBPUSD', 'volume': 0.05, 'order_type': 'sell'}
]

batch_result = place_multiple_trades(trades)
    """)
    
    print("\n4. Интеграция в торговый бот:")
    print("""
from utils.trading_functions import place_trade

class TradingBot:
    def process_signal(self, signal):
        symbol = signal['symbol']
        direction = signal['direction']
        order_type = "buy" if direction == "LONG" else "sell"
        
        result = place_trade(symbol, 0.1, order_type)
        return result
    """)

if __name__ == "__main__":
    test_cursor_mt5_integration()
    demonstrate_usage() 