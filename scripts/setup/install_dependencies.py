#!/usr/bin/env python3
"""
Combine Trade Bot - Установка зависимостей
Автор: Kirichek
"""

import subprocess
import sys
import os

def install_package(package):
    """Устанавливает пакет."""
    try:
        print(f"📦 Установка {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} установлен")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки {package}: {e}")
        return False

def main():
    """Главная функция установки."""
    print("=" * 50)
    print("🔧 Combine Trade Bot - Установка зависимостей")
    print("Автор: Kirichek")
    print("=" * 50)
    
    # Список необходимых пакетов
    packages = [
        "flet>=0.21.0",
        "requests>=2.31.0",
        "openai>=1.0.0",
        "telethon>=1.32.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "python-dotenv>=1.0.0"
    ]
    
    print("📋 Устанавливаемые пакеты:")
    for package in packages:
        print(f"   • {package}")
    
    print("\n🚀 Начинаем установку...")
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Результат установки: {success_count}/{total_count} пакетов")
    
    if success_count == total_count:
        print("✅ Все зависимости установлены успешно!")
        print("\n🎉 Система готова к работе!")
        print("💡 Запустите: python main.py")
    else:
        print("⚠️  Некоторые пакеты не установлены.")
        print("💡 Попробуйте установить их вручную:")
        failed_packages = [pkg for pkg in packages if not install_package(pkg)]
        for package in failed_packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main() 