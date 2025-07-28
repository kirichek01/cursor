# MT5 Server - Руководство по настройке и использованию

## Обзор

Профессиональный сервер для подключения к MetaTrader 5 с поддержкой только реальных торговых данных. Предназначен для работы с MT5 на виртуальных машинах и удаленных системах.

## ⚠️ ВАЖНО: Только реальные данные

Этот сервер работает **исключительно с реальными торговыми данными**. Все демо-режимы удалены для обеспечения достоверности торговой информации.

## Системные требования

- **Windows 10/11** (для MT5)
- **Python 3.8+**
- **MetaTrader 5** (установлен и настроен)
- **Реальный торговый счет** (демо-счета не поддерживаются)
- **Сетевое подключение** (для работы с VM)

## Быстрый старт

### 1. Запуск сервера

```bash
# Для обычного сервера
start_mt5_server.bat

# Для расширенного сервера (рекомендуется)
start_mt5_server_enhanced.bat
```

### 2. Настройка конфигурации

Создайте файл `mt5_config.json` на основе `mt5_config.example.json`:

```json
{
    "mt5_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
    "login": 1234567890,
    "password": "ваш_реальный_пароль",
    "server": "YourBroker-Live",
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "auto_initialize": true
}
```

### 3. Инициализация через API

```bash
curl -X POST http://localhost:5000/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
    "login": 1234567890,
    "password": "ваш_пароль",
    "server": "YourBroker-Live"
  }'
```

## API Endpoints

### Статус сервера
```
GET /health
```
Возвращает информацию о состоянии сервера и подключении к MT5.

**Ответ:**
```json
{
    "status": "ok",
    "mt5_initialized": true,
    "mt5_connected": true,
    "connection_message": "Подключение активно",
    "real_data_only": true,
    "timestamp": "2024-01-15T14:30:00.000Z",
    "config_loaded": true
}
```

### Инициализация MT5
```
POST /initialize
```
**Тело запроса:**
```json
{
    "path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
    "login": 1234567890,
    "password": "пароль",
    "server": "сервер_брокера"
}
```

### Информация о счете
```
GET /account_info
```
**Ответ:**
```json
{
    "success": true,
    "login": 1234567890,
    "balance": 10000.0,
    "equity": 10150.25,
    "profit": 150.25,
    "currency": "USD",
    "leverage": 100,
    "margin": 500.0,
    "margin_free": 9650.25,
    "margin_level": 2030.05,
    "server": "YourBroker-Live",
    "real_account": true
}
```

### Открытые позиции
```
GET /positions
```
**Ответ:**
```json
{
    "success": true,
    "positions": [
        {
            "ticket": 123456789,
            "symbol": "EURUSD",
            "type": "BUY",
            "volume": 0.1,
            "price_open": 1.2050,
            "price_current": 1.2080,
            "sl": 1.2000,
            "tp": 1.2150,
            "profit": 30.0,
            "comment": "Smart Money Bot",
            "time": "2024-01-15T14:00:00.000Z"
        }
    ],
    "count": 1
}
```

### Котировки
```
GET /rates?symbol=EURUSD&timeframe=M15&count=100
```
**Параметры:**
- `symbol` - торговый инструмент (EURUSD, GBPUSD, XAUUSD и т.д.)
- `timeframe` - таймфрейм (M1, M5, M15, M30, H1, H4, D1)
- `count` - количество свечей (по умолчанию 10)

### Конфигурация
```
GET /config
```
Возвращает текущую конфигурацию сервера (без паролей).

### Отключение
```
POST /shutdown
```
Корректно закрывает соединение с MT5.

## Настройка для виртуальной машины

### 1. Конфигурация сети VM

#### VirtualBox:
```
Настройки VM → Сеть → Адаптер 1 → Тип подключения: "Сетевой мост"
```

#### VMware:
```
VM Settings → Network Adapter → Network connection: "Bridged"
```

### 2. Настройка брандмауэра Windows

```powershell
# Разрешить входящие подключения на порт 5000
netsh advfirewall firewall add rule name="MT5 Server" dir=in action=allow protocol=TCP localport=5000

# Проверить правило
netsh advfirewall firewall show rule name="MT5 Server"
```

### 3. Получение IP-адреса

```bash
# В основной системе
ipconfig

# Найти IP-адрес (например: 192.168.1.100)
# Тогда сервер будет доступен по адресу: http://192.168.1.100:5000
```

## Безопасность

### Рекомендации по паролям
- Никогда не сохраняйте пароли в git-репозитории
- Используйте переменные окружения для чувствительных данных
- Регулярно меняйте пароли торговых счетов

### Сетевая безопасность
- Ограничьте доступ к серверу только доверенным IP
- Используйте VPN для удаленного доступа
- Регулярно обновляйте MT5 и зависимости Python

## Диагностика проблем

### Проверка подключения
```bash
# Тест доступности сервера
curl http://localhost:5000/health

# Проверка порта
netstat -an | find "5000"

# Проверка подключения к VM
ping IP_ВИРТУАЛЬНОЙ_МАШИНЫ
```

### Логи
Сервер создает детальные логи в файле `mt5_server.log`:

```bash
# Просмотр логов в реальном времени (Windows)
type mt5_server.log

# Последние записи
powershell "Get-Content mt5_server.log -Tail 50"
```

### Типичные ошибки

#### "MetaTrader5 library is not installed"
```bash
# Решение: установить библиотеку MT5
pip install MetaTrader5
```

#### "Path to MT5 terminal is required"
- Убедитесь, что указан правильный путь к MT5
- Проверьте, что MT5 установлен и запущен

#### "MT5 login failed"
- Проверьте правильность логина, пароля и сервера
- Убедитесь, что счет активен и не заблокирован

#### "Connection refused" при подключении к VM
- Проверьте настройки сети VM
- Убедитесь, что брандмауэр не блокирует порт 5000
- Проверьте IP-адрес основной системы

## Интеграция с торговым ботом

### Подключение в Python коде
```python
import requests

# Базовый URL сервера
MT5_SERVER_URL = "http://192.168.1.100:5000"

def get_account_info():
    response = requests.get(f"{MT5_SERVER_URL}/account_info")
    return response.json()

def get_rates(symbol, timeframe="M15", count=100):
    params = {
        "symbol": symbol,
        "timeframe": timeframe,
        "count": count
    }
    response = requests.get(f"{MT5_SERVER_URL}/rates", params=params)
    return response.json()
```

### Настройка в торговом боте
```python
# В файле настроек
USE_MT5_SERVER = True
MT5_SERVER_URL = "http://192.168.1.100:5000"

# В коде бота
if USE_MT5_SERVER:
    # Использовать сервер MT5
    data = load_mt5_data_from_server(symbol, timeframe, date_from, date_to)
else:
    # Использовать локальный MT5 (если доступен)
    data = load_mt5_data_local(symbol, timeframe, date_from, date_to)
```

## Мониторинг и обслуживание

### Автоматический перезапуск
Создайте службу Windows или используйте планировщик задач для автоматического перезапуска сервера.

### Мониторинг состояния
```python
import requests
import time

def monitor_mt5_server():
    while True:
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            data = response.json()
            
            if data.get("mt5_connected"):
                print("✅ MT5 сервер работает нормально")
            else:
                print("⚠️ MT5 сервер потерял соединение")
                
        except Exception as e:
            print(f"❌ Ошибка подключения к серверу: {e}")
            
        time.sleep(60)  # Проверка каждую минуту
```

## Поддержка

При возникновении проблем:
1. Проверьте логи в `mt5_server.log`
2. Убедитесь в правильности конфигурации
3. Проверьте сетевые настройки
4. Убедитесь, что используется реальный торговый счет

---

**Важно**: Этот сервер предназначен только для реальной торговли. Убедитесь, что понимаете риски, связанные с автоматической торговлей на реальных счетах.