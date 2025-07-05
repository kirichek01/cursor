#!/usr/bin/env python3
"""
Смартмани бот - торговля по SMC стратегии с анализом 
order blocks, FVG и индусментов
"""

import os
import sys
import subprocess
from pathlib import Path

def launch_smc_bot():
    """Запускает смартмани бота."""
    try:
        # Путь к смартмани боту
        smc_bot_path = Path("sms_bot/smc_bot.py")
        
        if smc_bot_path.exists():
            print("🚀 Запуск смартмани бота...")
            print("📊 Функции:")
            print("   • Анализ order blocks")
            print("   • Поиск Fair Value Gaps (FVG)")
            print("   • Индусменты")
            print("   • Break of Structure (BOS)")
            print("   • Автоматическая торговля по SMC")
            print("   • Управление позициями")
            print()
            
            # Запускаем бота в отдельном процессе
            process = subprocess.Popen([
                sys.executable, 
                str(smc_bot_path)
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            
            print(f"✅ Смартмани бот запущен (PID: {process.pid})")
            print("📱 Откроется GUI интерфейс смартмани бота")
            
            return process
            
        else:
            print("❌ Файл смартмани бота не найден")
            print(f"   Ожидаемый путь: {smc_bot_path.absolute()}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска смартмани бота: {e}")
        return None

if __name__ == "__main__":
    launch_smc_bot() 