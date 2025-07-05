#!/usr/bin/env python3
"""
Combine Trade Bot - Система запуска
Автор: Kirichek
"""

import sys
import os
import subprocess
import importlib.util

def check_python_version():
    """Проверяет версию Python."""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    print(f"✅ Python версия: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Проверяет установленные зависимости."""
    required_packages = [
        'flet',
        'requests',
        'sqlite3',
        'json',
        'threading',
        'datetime'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'json':
                import json
            elif package == 'threading':
                import threading
            elif package == 'datetime':
                import datetime
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Установите недостающие пакеты:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def install_dependencies():
    """Устанавливает зависимости."""
    print("\n🔧 Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def check_config_files():
    """Проверяет наличие конфигурационных файлов."""
    config_files = [
        "data/config.json",
        "data/channels.json"
    ]
    
    for file_path in config_files:
        if not os.path.exists(file_path):
            print(f"⚠️  Файл {file_path} не найден, будет создан автоматически")
    
    return True

def create_directories():
    """Создает необходимые директории."""
    directories = [
        "data",
        "logs",
        "backups"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Директория {directory} создана/проверена")

def start_application():
    """Запускает основное приложение."""
    print("\n🚀 Запуск Combine Trade Bot...")
    try:
        import main
        print("✅ Приложение запущено успешно")
    except Exception as e:
        print(f"❌ Ошибка запуска приложения: {e}")
        return False
    
    return True

def main():
    """Главная функция."""
    print("=" * 50)
    print("🤖 Combine Trade Bot - Система запуска")
    print("Автор: Kirichek")
    print("=" * 50)
    
    # Проверяем версию Python
    if not check_python_version():
        return
    
    # Создаем директории
    create_directories()
    
    # Проверяем конфигурационные файлы
    check_config_files()
    
    # Проверяем зависимости
    print("\n📋 Проверка зависимостей:")
    if not check_dependencies():
        print("\n❓ Установить зависимости автоматически? (y/n): ", end="")
        response = input().lower()
        if response in ['y', 'yes', 'да']:
            if not install_dependencies():
                return
        else:
            print("❌ Зависимости не установлены. Запуск невозможен.")
            return
    
    # Запускаем приложение
    if start_application():
        print("\n🎉 Система готова к работе!")
    else:
        print("\n❌ Ошибка запуска системы")

if __name__ == "__main__":
    main() 