# 🧾 Интеграция Cursor с MT5 через Flask сервер

## ✅ Статус: Готово к использованию

Интеграция успешно создана и протестирована. Все компоненты работают корректно.

## 📁 Созданные файлы

### 1. Клиентская часть (macOS)
- **`utils/cursor_send_order_improved.py`** - Основная функция отправки ордеров
- **`utils/trading_functions.py`** - Функции для автоматической торговли
- **`test_mt5_integration.py`** - Тестовый скрипт

### 2. Серверная часть (Windows VM)
- **`mt5_server.py`** - Flask сервер для MT5

### 3. Документация
- **`MT5_INTEGRATION_GUIDE.md`** - Подробное руководство
- **`README_MT5_INTEGRATION.md`** - Эта документация

## 🚀 Быстрый старт

### Шаг 1: Настройка Windows VM

1. **Установите зависимости:**
```bash
pip install flask MetaTrader5 requests
```

2. **Запустите Flask сервер:**
```bash
python mt5_server.py
```

3. **Проверьте, что сервер работает:**
```bash
curl http://localhost:5000/health
```

### Шаг 2: Настройка macOS (Cursor)

1. **Обновите IP адрес в `utils/cursor_send_order_improved.py`:**
```python
MT5_SERVER_CONFIG = {
    'base_url': 'http://ВАШ_IP_ВИРТУАЛКИ:5000',  # Замените на ваш IP
    'timeout': 10,
    'retry_attempts': 3,
    'retry_delay': 1
}
```

2. **Протестируйте подключение:**
```bash
python test_mt5_integration.py
```

## 📊 Использование

### Простая отправка ордера:
```python
from utils.trading_functions import place_trade

result = place_trade("EURUSD", 0.1, "buy")
if result['success']:
    print("✅ Ордер выполнен")
else:
    print(f"❌ Ошибка: {result['error']}")
```

### Ордер с SL/TP:
```python
result = place_trade(
    symbol="XAUUSD",
    volume=0.1,
    order_type="buy",
    sl=1950.0,
    tp=2000.0,
    comment="Gold trade"
)
```

### Пакетная отправка:
```python
from utils.trading_functions import place_multiple_trades

trades = [
    {'symbol': 'EURUSD', 'volume': 0.1, 'order_type': 'buy'},
    {'symbol': 'GBPUSD', 'volume': 0.05, 'order_type': 'sell'}
]

batch_result = place_multiple_trades(trades)
```

## 🔧 Интеграция с проектом

### TradeManagerService
Интеграция уже подключена к `TradeManagerService`. При запуске торговли:

```python
from services.trade_manager_service import TradeManagerService

trade_manager = TradeManagerService()
success, message = trade_manager.start_trading()
```

### Автоматическая обработка сигналов
Система автоматически обрабатывает торговые сигналы и отправляет ордера в MT5.

## 📈 Возможности

### ✅ Реализовано:
- ✅ Отправка ордеров в MT5 через Flask
- ✅ Поддержка всех типов ордеров (buy, sell, limit, stop)
- ✅ Установка SL/TP
- ✅ Пакетная отправка ордеров
- ✅ Получение информации об аккаунте
- ✅ Получение открытых позиций
- ✅ Закрытие позиций
- ✅ Модификация SL/TP
- ✅ Обработка ошибок и повторные попытки
- ✅ Логирование всех операций
- ✅ Интеграция с TradeManagerService
- ✅ Автоматическая обработка сигналов

### 🔄 Автоматизация:
- Автоматическое выполнение сигналов
- Мониторинг позиций
- Обновление статусов в базе данных
- Логирование всех операций

## 🛡️ Безопасность

### Рекомендации:
1. **Сетевая безопасность:**
   - Используйте VPN между macOS и Windows VM
   - Ограничьте доступ к порту 5000

2. **Аутентификация:**
   - Добавьте API ключи в Flask сервер
   - Используйте HTTPS

3. **Мониторинг:**
   - Все операции логируются
   - Проверяйте логи регулярно

## 🔍 Тестирование

### Запуск тестов:
```bash
python test_mt5_integration.py
```

### Проверка статуса:
```python
from utils.trading_functions import test_mt5_connection

status = test_mt5_connection()
print(f"Статус: {status}")
```

## 📋 API Endpoints

### Flask сервер (Windows VM):

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/health` | GET | Проверка состояния |
| `/send_order` | POST | Отправка ордера |
| `/account_info` | GET | Информация об аккаунте |
| `/positions` | GET | Открытые позиции |
| `/close_position` | POST | Закрытие позиции |
| `/modify_position` | POST | Модификация SL/TP |

## ⚠️ Устранение неполадок

### Частые проблемы:

1. **"Нет подключения к MT5 серверу"**
   - Проверьте, что Flask сервер запущен
   - Убедитесь в правильности IP адреса
   - Проверьте сетевые порты

2. **"MT5 не инициализирован"**
   - Убедитесь, что MT5 запущен на Windows VM
   - Проверьте логи Flask сервера

3. **"Не удалось выбрать символ"**
   - Убедитесь, что символ доступен в MT5
   - Проверьте правильность написания

## 📞 Поддержка

### При возникновении проблем:

1. Проверьте логи Flask сервера
2. Убедитесь в правильности настройки IP адресов
3. Проверьте сетевые настройки
4. Убедитесь, что MT5 запущен и работает

### Логи:
- Все операции логируются автоматически
- Логи содержат время, параметры и результаты операций
- Ошибки логируются с подробным описанием

## 🎯 Результат

✅ **Интеграция полностью готова к использованию**

- Cursor (macOS) может отправлять ордера в MT5 (Windows VM)
- Автоматическая обработка торговых сигналов
- Полная интеграция с существующим проектом
- Надежная обработка ошибок
- Подробное логирование

**Важно:** Всегда тестируйте на демо-счете перед использованием на реальном счете! 