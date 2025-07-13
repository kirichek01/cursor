#!/usr/bin/env python3
"""
Скрипт для запуска проекта в Windows VM через Parallels Desktop
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_command_in_windows(command):
    """Выполняет команду в Windows VM через Parallels"""
    try:
        # Путь к Windows VM
        windows_path = "/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized"
        
        # Команда для запуска в Windows
        full_command = f'"{windows_path}/Терминал.app/Contents/MacOS/WinAppHelper" --ivmid 5 --command "{command}"'
        
        print(f"🚀 Выполняю команду в Windows VM: {command}")
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Команда выполнена успешно")
            return result.stdout
        else:
            print(f"❌ Ошибка выполнения команды: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Windows VM: {e}")
        return None

def setup_project_in_windows():
    """Настраивает проект в Windows VM"""
    print("🔧 Настройка проекта в Windows VM...")
    
    # Копируем проект в Windows
    project_path = os.getcwd()
    windows_project_path = "/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized/макет"
    
    # Создаем директорию в Windows
    os.makedirs(windows_project_path, exist_ok=True)
    
    # Копируем файлы
    subprocess.run(f"cp -r {project_path}/* {windows_project_path}/", shell=True)
    
    print("📁 Проект скопирован в Windows VM")
    
    # Устанавливаем зависимости в Windows
    commands = [
        "cd /Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized/макет",
        "python -m pip install --upgrade pip",
        "pip install -r requirements.txt",
        "python main.py"
    ]
    
    for cmd in commands:
        result = run_command_in_windows(cmd)
        if result is None:
            print("❌ Не удалось выполнить команду в Windows VM")
            return False
    
    return True

def main():
    print("🖥️  Запуск проекта в Windows VM с MT5...")
    
    # Проверяем, что Windows VM запущена
    if not os.path.exists("/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized"):
        print("❌ Windows VM не найдена. Запустите Parallels Desktop и Windows VM")
        return
    
    # Настраиваем и запускаем проект
    if setup_project_in_windows():
        print("✅ Проект успешно запущен в Windows VM с MT5!")
        print("🌐 Интерфейс должен открыться в браузере Windows VM")
    else:
        print("❌ Не удалось запустить проект в Windows VM")

if __name__ == "__main__":
    main() 