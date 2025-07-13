#!/usr/bin/env python3
"""
Скрипт для проверки подключения к Flask серверу MT5
"""

import requests
import json

def test_flask_connection():
    """Проверяет подключение к Flask серверу"""
    url = "http://10.211.55.3:5000/health"
    
    print(f"🔍 Проверяем подключение к Flask серверу...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Flask сервер доступен!")
            return True
        else:
            print(f"⚠️ Flask сервер недоступен: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения: сервер недоступен")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Таймаут подключения")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_mt5_endpoints():
    """Тестирует основные эндпоинты MT5"""
    base_url = "http://10.211.55.3:5000"
    
    endpoints = [
        "/health",
        "/account_info", 
        "/positions",
        "/rates?symbol=EURUSD&timeframe=M1&count=10"
    ]
    
    print(f"\n🔍 Тестируем эндпоинты MT5...")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 {endpoint}:")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ OK")
            else:
                print(f"   ❌ Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Тест подключения к MT5 Flask серверу")
    print("=" * 50)
    
    # Проверяем базовое подключение
    if test_flask_connection():
        # Если сервер доступен, тестируем эндпоинты
        test_mt5_endpoints()
    else:
        print("\n💡 Рекомендации:")
        print("1. Убедитесь, что Flask сервер запущен на Windows машине")
        print("2. Проверьте IP адрес: 10.211.55.3")
        print("3. Проверьте порт: 5000")
        print("4. Убедитесь, что файрвол не блокирует подключение") 