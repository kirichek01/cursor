#!/usr/bin/env python3
"""
Trading System Main Launcher

Главный файл запуска торговой системы.
Только реальные данные, профессиональная торговля.
"""

import sys
import os

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Главная функция запуска приложения"""
    try:
        # Импортируем и запускаем приложение
        from app.main import main as app_main
        
        print("🚀 Запуск торговой системы...")
        print("📊 Режим: Только реальные данные")
        print("=" * 50)
        
        # Запускаем основное приложение
        app_main()
        
    except KeyboardInterrupt:
        print("\n⏹️ Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска приложения: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
