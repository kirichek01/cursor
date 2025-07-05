#!/usr/bin/env python3
"""
Парсер бот - автоматический парсинг сигналов с Telegram каналов
и торговля на их основе с AI анализом
"""

import os
import sys
import subprocess
from pathlib import Path

def launch_parser_bot():
    """Запускает парсер бота."""
    try:
        # Путь к парсер боту
        parser_bot_path = Path("CombineTradeBotRabochiyBOT/main.py")
        
        if parser_bot_path.exists():
            print("🚀 Запуск парсер бота...")
            print("📊 Функции:")
            print("   • Парсинг сигналов с Telegram каналов")
            print("   • AI анализ сигналов")
            print("   • Автоматическая торговля")
            print("   • Управление рисками")
            print("   • Мониторинг сделок")
            print()
            
            # Запускаем бота в отдельном процессе
            process = subprocess.Popen([
                sys.executable, 
                str(parser_bot_path)
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            
            print(f"✅ Парсер бот запущен (PID: {process.pid})")
            print("📱 Откроется GUI интерфейс парсер бота")
            
            return process
            
        else:
            print("❌ Файл парсер бота не найден")
            print(f"   Ожидаемый путь: {parser_bot_path.absolute()}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска парсер бота: {e}")
        return None

if __name__ == "__main__":
    launch_parser_bot() 