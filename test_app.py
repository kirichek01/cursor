#!/usr/bin/env python3
"""
Простой тест для проверки работы приложения
"""

import flet as ft
from services.logic_manager import LogicManager

def test_logic_manager():
    """Тестирует LogicManager и загрузку данных."""
    try:
        # Создаем мок страницы
        class MockPage:
            def __init__(self):
                self.pubsub = None
            
            def update(self):
                pass
        
        page = MockPage()
        
        # Создаем LogicManager
        logic_manager = LogicManager(page)
        
        # Инициализируем базу данных
        from services.database_service import DatabaseService
        logic_manager.db = DatabaseService()
        
        # Тестируем загрузку истории сигналов
        signal_history = logic_manager.get_signal_history(limit=5)
        
        print("=== Тест LogicManager ===")
        print(f"Загружено сигналов: {len(signal_history)}")
        
        for signal in signal_history:
            print(f"ID: {signal['id']}")
            print(f"  Символ: {signal['symbol']}")
            print(f"  Тип: {signal['order_type']}")
            print(f"  Статус: {signal['status']}")
            print(f"  Время: {signal['timestamp']}")
            print()
        
        print("✅ LogicManager работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка в LogicManager: {e}")

if __name__ == "__main__":
    test_logic_manager() 