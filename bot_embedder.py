#!/usr/bin/env python3
"""
Система для встраивания ботов во вкладки основного интерфейса
"""

import subprocess
import sys
import os
import threading
import time
from pathlib import Path
from typing import Dict, Optional

class BotManager:
    """Менеджер для управления ботами во вкладках."""
    
    def __init__(self):
        self.bots: Dict[str, Optional[subprocess.Popen]] = {
            "parser": None,
            "smc": None
        }
        self.bot_status: Dict[str, str] = {
            "parser": "Остановлен",
            "smc": "Остановлен"
        }
        self.bot_logs: Dict[str, list] = {
            "parser": [],
            "smc": []
        }
        
    def start_parser_bot(self) -> bool:
        """Запускает парсер бота."""
        try:
            if self.bots["parser"] is not None:
                return False  # Бот уже запущен
                
            parser_path = Path("CombineTradeBotRabochiyBOT/main.py")
            if not parser_path.exists():
                self.add_log("parser", "❌ Файл парсер бота не найден")
                return False
                
            # Запускаем бота в отдельном процессе
            self.bots["parser"] = subprocess.Popen([
                sys.executable, str(parser_path)
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            
            self.bot_status["parser"] = "Работает"
            self.add_log("parser", "✅ Парсер бот запущен")
            return True
            
        except Exception as e:
            self.add_log("parser", f"❌ Ошибка запуска: {e}")
            return False
    
    def stop_parser_bot(self) -> bool:
        """Останавливает парсер бота."""
        try:
            if self.bots["parser"] is None:
                return False
                
            self.bots["parser"].terminate()
            self.bots["parser"] = None
            self.bot_status["parser"] = "Остановлен"
            self.add_log("parser", "⏹️ Парсер бот остановлен")
            return True
            
        except Exception as e:
            self.add_log("parser", f"❌ Ошибка остановки: {e}")
            return False
    
    def start_smc_bot(self) -> bool:
        """Запускает смартмани бота."""
        try:
            if self.bots["smc"] is not None:
                return False  # Бот уже запущен
                
            smc_path = Path("sms_bot/smc_bot.py")
            if not smc_path.exists():
                self.add_log("smc", "❌ Файл смартмани бота не найден")
                return False
                
            # Запускаем бота в отдельном процессе
            self.bots["smc"] = subprocess.Popen([
                sys.executable, str(smc_path)
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            
            self.bot_status["smc"] = "Работает"
            self.add_log("smc", "✅ Смартмани бот запущен")
            return True
            
        except Exception as e:
            self.add_log("smc", f"❌ Ошибка запуска: {e}")
            return False
    
    def stop_smc_bot(self) -> bool:
        """Останавливает смартмани бота."""
        try:
            if self.bots["smc"] is None:
                return False
                
            self.bots["smc"].terminate()
            self.bots["smc"] = None
            self.bot_status["smc"] = "Остановлен"
            self.add_log("smc", "⏹️ Смартмани бот остановлен")
            return True
            
        except Exception as e:
            self.add_log("smc", f"❌ Ошибка остановки: {e}")
            return False
    
    def add_log(self, bot_name: str, message: str):
        """Добавляет сообщение в лог бота."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.bot_logs[bot_name].append(log_entry)
        
        # Ограничиваем размер лога
        if len(self.bot_logs[bot_name]) > 50:
            self.bot_logs[bot_name] = self.bot_logs[bot_name][-50:]
    
    def get_logs(self, bot_name: str) -> str:
        """Возвращает логи бота в виде строки."""
        return "\n".join(self.bot_logs[bot_name])
    
    def get_status(self, bot_name: str) -> str:
        """Возвращает статус бота."""
        return self.bot_status[bot_name]
    
    def check_bot_health(self):
        """Проверяет состояние ботов."""
        for bot_name, process in self.bots.items():
            if process is not None:
                if process.poll() is not None:
                    # Процесс завершился
                    self.bots[bot_name] = None
                    self.bot_status[bot_name] = "Остановлен"
                    self.add_log(bot_name, "⚠️ Бот неожиданно остановился")
    
    def stop_all_bots(self):
        """Останавливает всех ботов."""
        self.stop_parser_bot()
        self.stop_smc_bot()

# Глобальный экземпляр менеджера ботов
bot_manager = BotManager()

def get_bot_manager() -> BotManager:
    """Возвращает глобальный менеджер ботов."""
    return bot_manager 