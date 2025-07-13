#!/usr/bin/env python3
"""
Скрипт для поиска Flask сервера MT5 в сети
"""

import requests
import socket
import threading
import time

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Ошибка получения локального IP: {e}")
        return None

def check_flask_server(ip, port=5000):
    """Проверяет доступность Flask сервера на указанном IP"""
    url = f"http://{ip}:{port}/health"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"Status: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def scan_network(base_ip="10.211.55", port=5000):
    """Сканирует сеть в поисках Flask сервера"""
    print(f"🔍 Сканируем сеть {base_ip}.0/24 на порту {port}...")
    
    found_servers = []
    
    def check_ip(ip):
        success, message = check_flask_server(ip, port)
        if success:
            found_servers.append((ip, message))
            print(f"✅ Найден Flask сервер на {ip}:{port}")
            print(f"   Response: {message}")
    
    # Создаем потоки для параллельного сканирования
    threads = []
    for i in range(1, 255):
        ip = f"{base_ip}.{i}"
        thread = threading.Thread(target=check_ip, args=(ip,))
        threads.append(thread)
        thread.start()
        
        # Ограничиваем количество одновременных потоков
        if len(threads) >= 50:
            for t in threads:
                t.join()
            threads = []
    
    # Ждем завершения оставшихся потоков
    for t in threads:
        t.join()
    
    return found_servers

def main():
    print("🚀 Поиск Flask сервера MT5 в сети")
    print("=" * 50)
    
    # Получаем локальный IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"📍 Локальный IP: {local_ip}")
        
        # Определяем базовый IP для сканирования
        base_ip = ".".join(local_ip.split(".")[:3])
        print(f"🌐 Сканируем сеть: {base_ip}.0/24")
    else:
        base_ip = "10.211.55"
        print(f"🌐 Используем стандартную сеть: {base_ip}.0/24")
    
    # Сканируем сеть
    start_time = time.time()
    found_servers = scan_network(base_ip)
    end_time = time.time()
    
    print(f"\n⏱️ Сканирование завершено за {end_time - start_time:.2f} секунд")
    
    if found_servers:
        print(f"\n✅ Найдено {len(found_servers)} Flask серверов:")
        for ip, response in found_servers:
            print(f"   • {ip}:5000")
            print(f"     Response: {response}")
        
        print(f"\n💡 Обновите настройки в data/config.json:")
        print(f"   {{\"mt5_server\": {{\"url\": \"http://{found_servers[0][0]}:5000\"}}}}")
    else:
        print("\n❌ Flask серверы не найдены")
        print("\n💡 Рекомендации:")
        print("1. Убедитесь, что Flask сервер запущен на Windows машине")
        print("2. Проверьте, что порт 5000 открыт")
        print("3. Убедитесь, что машины находятся в одной сети")
        print("4. Попробуйте другие IP диапазоны (10.211.55.x)")

if __name__ == "__main__":
    main() 