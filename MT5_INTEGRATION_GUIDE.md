# 🧾 Интеграция Cursor с MT5 через Flask сервер

## 📋 Обзор

Данная интеграция позволяет Cursor (на macOS) автоматически отправлять торговые ордера в MetaTrader 5 (на Windows VM) через Flask сервер.

## 🏗️ Архитектура

```
Cursor (macOS) ←→ Flask Server (Windows VM) ←→ MetaTrader 5
```

### Компоненты:
- **`cursor_send_order_improved.py`** - Клиентская часть на macOS
- **`mt5_server.py`** - Flask сервер на Windows VM
- **`trading_functions.py`** - Функции для автоматической торговли

## 🚀 Настройка

### 1. Настройка Windows VM

#### Установка зависимостей:
```bash
pip install flask MetaTrader5 requests
```

#### Запуск Flask сервера:
```bash
python mt5_server.py
```

Сервер будет доступен по адресу: `http://0.0.0.0:5000`

### 2. Настройка macOS (Cursor)

#### Обновление IP адреса:
В файле `utils/cursor_send_order_improved.py` измените IP адрес на локальный IP вашей Windows VM:

```python
MT5_SERVER_CONFIG = {
    'base_url': 'http://10.211.55.3:5000',  # Замените на ваш IP
    'timeout': 10,
    'retry_attempts': 3,
    'retry_delay': 1
}
```

#### Тестирование подключения:
```bash
python utils/trading_functions.py
```

## 📊 Использование

### Базовое использование

```python
from utils.trading_functions import place_trade

# Отправка простого ордера
result = place_trade("EURUSD", 0.1, "buy")
if result['success']:
    print("✅ Ордер выполнен успешно")
else:
    print(f"❌ Ошибка: {result['error']}")
```

### Продвинутое использование

```python
from utils.trading_functions import place_trade, place_multiple_trades

# Ордер с SL/TP
result = place_trade(
    symbol="XAUUSD",
    volume=0.1,
    order_type="buy",
    sl=1950.0,
    tp=2000.0,
    comment="Gold trade"
)

# Пакетная отправка ордеров
trades = [
    {'symbol': 'EURUSD', 'volume': 0.1, 'order_type': 'buy', 'sl': 1.2000, 'tp': 1.2100},
    {'symbol': 'GBPUSD', 'volume': 0.05, 'order_type': 'sell', 'sl': 1.3000, 'tp': 1.2900}
]

batch_result = place_multiple_trades(trades)
```

### Интеграция в торговый бот

```python
from utils.trading_functions import place_trade
from services.signal_processor import SignalProcessor

class TradingBot:
    def __init__(self):
        self.signal_processor = SignalProcessor()
    
    def process_signal(self, signal_data):
        """Обработка торгового сигнала"""
        symbol = signal_data['symbol']
        direction = signal_data['direction']
        volume = signal_data['volume']
        
        # Определяем тип ордера
        order_type = "buy" if direction == "LONG" else "sell"
        
        # Отправляем ордер
        result = place_trade(symbol, volume, order_type)
        
        if result['success']:
            print(f"✅ Сигнал обработан: {symbol} {direction}")
            return result
        else:
            print(f"❌ Ошибка обработки сигнала: {result['error']}")
            return None
```

## 🔧 API Endpoints

### Flask сервер (Windows VM)

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/health` | GET | Проверка состояния сервера |
| `/send_order` | POST | Отправка ордера |
| `/account_info` | GET | Информация об аккаунте |
| `/positions` | GET | Открытые позиции |
| `/close_position` | POST | Закрытие позиции |
| `/modify_position` | POST | Модификация SL/TP |

### Примеры запросов

#### Отправка ордера:
```bash
curl -X POST http://10.211.55.3:5000/send_order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "EURUSD",
    "volume": 0.1,
    "order_type": "buy",
    "sl": 1.2000,
    "tp": 1.2100,
    "comment": "Test order"
  }'
```

#### Получение информации об аккаунте:
```bash
curl http://10.211.55.3:5000/account_info
```

## ⚠️ Обработка ошибок

### Типичные ошибки и решения:

1. **"Нет подключения к MT5 серверу"**
   - Проверьте, что Flask сервер запущен на Windows VM
   - Убедитесь, что IP адрес настроен правильно
   - Проверьте сетевые порты (5000)

2. **"MT5 не инициализирован"**
   - Убедитесь, что MetaTrader 5 запущен на Windows VM
   - Проверьте логи Flask сервера

3. **"Не удалось выбрать символ"**
   - Убедитесь, что символ доступен в MT5
   - Проверьте правильность написания символа

## 🔒 Безопасность

### Рекомендации:

1. **Сетевая безопасность:**
   - Используйте VPN для подключения между macOS и Windows VM
   - Ограничьте доступ к порту 5000 только с IP macOS

2. **Аутентификация:**
   - Добавьте API ключи для защиты Flask сервера
   - Используйте HTTPS для шифрования трафика

3. **Логирование:**
   - Все операции логируются автоматически
   - Проверяйте логи на предмет подозрительной активности

## 📈 Мониторинг

### Проверка статуса:

```python
from utils.trading_functions import test_mt5_connection, get_trading_status

# Тест подключения
connection_status = test_mt5_connection()
print(f"Статус подключения: {connection_status}")

# Полный статус системы
trading_status = get_trading_status()
print(f"Статус торговой системы: {trading_status}")
```

### Логирование:

Все операции автоматически логируются с уровнем INFO. Логи содержат:
- Время выполнения операции
- Параметры ордера
- Результат выполнения
- Ошибки и предупреждения

## 🚀 Автоматизация

### Интеграция с торговыми стратегиями:

```python
import time
from utils.trading_functions import place_trade

class AutomatedTrader:
    def __init__(self):
        self.is_running = False
    
    def start_trading(self):
        """Запуск автоматической торговли"""
        self.is_running = True
        while self.is_running:
            # Ваша торговая логика здесь
            if self.should_buy():
                place_trade("EURUSD", 0.1, "buy")
            elif self.should_sell():
                place_trade("EURUSD", 0.1, "sell")
            
            time.sleep(60)  # Проверка каждую минуту
    
    def should_buy(self):
        # Ваша логика для покупки
        pass
    
    def should_sell(self):
        # Ваша логика для продажи
        pass
```

## 📝 Примеры использования

### 1. Простая торговая стратегия

```python
def simple_strategy():
    """Простая стратегия: покупка при росте, продажа при падении"""
    from utils.trading_functions import place_trade
    
    # Получаем текущие цены (ваша логика)
    current_price = get_current_price("EURUSD")
    
    if current_price > previous_price:
        place_trade("EURUSD", 0.1, "buy", comment="Trend following")
    elif current_price < previous_price:
        place_trade("EURUSD", 0.1, "sell", comment="Trend following")
```

### 2. Управление рисками

```python
def risk_managed_trade(symbol, direction, risk_percent=2.0):
    """Торговля с управлением рисками"""
    from utils.trading_functions import place_trade, get_account_info
    
    # Получаем информацию об аккаунте
    account_info = get_account_info()
    if not account_info['success']:
        return {'success': False, 'error': 'Не удалось получить информацию об аккаунте'}
    
    balance = account_info['balance']
    risk_amount = balance * (risk_percent / 100)
    
    # Рассчитываем объем позиции (упрощенно)
    volume = risk_amount / 1000  # Примерный расчет
    
    # Отправляем ордер
    return place_trade(symbol, volume, direction)
```

## 🔧 Устранение неполадок

### Частые проблемы:

1. **Сервер не отвечает:**
   ```bash
   # Проверьте статус сервера
   curl http://10.211.55.3:5000/health
   ```

2. **Ошибки MT5:**
   - Проверьте логи Flask сервера
   - Убедитесь, что MT5 запущен и авторизован

3. **Сетевые проблемы:**
   ```bash
   # Проверьте доступность порта
   telnet 10.211.55.3 5000
   ```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи Flask сервера
2. Убедитесь в правильности настройки IP адресов
3. Проверьте сетевые настройки
4. Убедитесь, что MT5 запущен и работает

---

**Важно:** Всегда тестируйте на демо-счете перед использованием на реальном счете! 