#!/usr/bin/env python3
"""
Автоматический запуск проекта в Windows VM с MT5
"""

import os
import subprocess
import time
import sys
import shutil

def check_windows_vm():
    """Проверяет, запущена ли Windows VM"""
    windows_path = "/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized"
    return os.path.exists(windows_path)

def copy_project_to_windows():
    """Копирует проект в Windows VM"""
    print("📁 Копирую проект в Windows VM...")
    
    source = os.getcwd()
    destination = "/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized/макет"
    
    try:
        # Создаем директорию
        os.makedirs(destination, exist_ok=True)
        
        # Копируем файлы с помощью shutil
        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(destination, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
        print("✅ Проект скопирован в Windows VM")
        return True
    except Exception as e:
        print(f"❌ Ошибка копирования: {e}")
        return False

def open_windows_terminal():
    """Открывает терминал Windows VM"""
    print("🖥️  Открываю терминал Windows VM...")
    
    terminal_path = "/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized/Терминал.app"
    
    if os.path.exists(terminal_path):
        subprocess.run(["open", terminal_path])
        print("✅ Терминал Windows VM открыт")
        return True
    else:
        print("❌ Терминал Windows VM не найден")
        return False

def main():
    print("🚀 Запуск проекта в Windows VM с MT5...")
    print("=" * 50)
    
    # Проверяем Windows VM
    if not check_windows_vm():
        print("❌ Windows VM не найдена!")
        print("💡 Запустите Parallels Desktop и Windows VM")
        return
    
    print("✅ Windows VM найдена")
    
    # Копируем проект
    if not copy_project_to_windows():
        print("❌ Не удалось скопировать проект")
        return
    
    # Открываем терминал Windows
    if not open_windows_terminal():
        print("❌ Не удалось открыть терминал Windows")
        return
    
    print("\n" + "=" * 50)
    print("📋 Инструкции для Windows VM:")
    print("1. В открывшемся терминале Windows выполните:")
    print("   cd /Users/vladislavkirichek/Applications\ \(Parallels\)/{64a44e8b-2a77-4379-9821-4cb170697000}\ Applications.localized/макет")
    print("2. Установите зависимости:")
    print("   python -m pip install --upgrade pip")
    print("   pip install -r requirements.txt")
    print("3. Проверьте MT5:")
    print("   python -c \"import MetaTrader5 as mt5; print('MT5 доступен')\"")
    print("4. Запустите приложение:")
    print("   python main.py")
    print("=" * 50)
    
    print("\n🎯 Альтернативно, используйте готовый bat-файл:")
    print("   start_windows.bat")
    
    print("\n🌐 После запуска откройте браузер в Windows VM:")
    print("   http://localhost:8550")

if __name__ == "__main__":
    main() 