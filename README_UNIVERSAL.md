# MT5 Trading Bot - Универсальная версия

## 🚀 Описание
Универсальное приложение для автоматической торговли через MetaTrader 5 с поддержкой различных операционных систем.

## 🌐 Универсальная поддержка платформ

### Windows (локальный режим)
- ✅ **Прямое подключение к MT5** через библиотеку MetaTrader5
- ✅ **Полный доступ** ко всем функциям торговли
- ✅ **Автономная работа** без дополнительных серверов

### macOS/Linux (Flask API режим)
- ✅ **Подключение через HTTP API** к MT5 серверу на Windows
- ✅ **Работа с удалённым MT5** через общую сеть
- ✅ **Демо-режим** для тестирования без реального MT5

## 🛠️ Установка и настройка

### Требования:
- Python 3.8+
- Flet и другие зависимости (см. requirements.txt)
- MetaTrader5 (для Windows или удалённого сервера)
- Telegram API ключи

### Установка:
```bash
pip install -r requirements.txt
```

### Настройка для Windows (локальный режим):
1. Установите MetaTrader 5 и войдите в аккаунт
2. Запустите приложение: `python main.py`
3. Перейдите в Settings → MT5
4. Включите переключатель "Локальный MT5 (Windows)"
5. Введите логин, пароль, сервер и путь к MT5
6. Сохраните настройки

### Настройка для macOS/Linux (Flask API режим):
1. **На Windows машине:**
   - Установите MT5 и войдите в аккаунт
   - Запустите MT5 сервер: `python mt5_server.py`
   - Убедитесь, что сервер доступен по сети

2. **На macOS/Linux:**
   - Запустите приложение: `python main.py`
   - Перейдите в Settings → MT5
   - Отключите переключатель "Локальный MT5 (Windows)"
   - Введите URL MT5 сервера (например, `http://10.211.55.3:5000`)
   - Сохраните настройки

### Запуск:
```bash
python main.py
```

## 🔧 Режимы работы MT5Service

### Локальный режим (Windows)
```python
# Автоматически определяется при наличии MT5 библиотеки
# и заполненных настройках логина/пароля/сервера
mt5_service = MT5Service(
    path="C:\\Program Files\\MetaTrader 5\\terminal64.exe",
    login="12345",
    password="password",
    server="MetaQuotes-Demo"
)
```

### Flask API режим (macOS/Linux)
```python
# Подключение через HTTP API к серверу на Windows
mt5_service = MT5Service(
    flask_url="http://10.211.55.3:5000"
)
```

### Демо режим
```python
# Генерация демо-данных для тестирования
mt5_service = MT5Service()  # Без параметров
```

## 🚀 Возможности

### Универсальная работа
- **Windows**: Полная функциональность с прямым доступом к MT5
- **macOS/Linux**: Работа через Flask API или демо-режим
- **Автоматическое определение** режима работы

### Торговые функции
- Открытие/закрытие позиций
- Модификация SL/TP
- Получение котировок
- История сделок
- Информация об аккаунте

### Интерфейс
- Современный дизайн с темной темой
- Адаптивные настройки для разных платформ
- Автообновление данных
- Статус сервисов в реальном времени

## 📊 Структура проекта

```
MT5_Project/
├── main.py                 # Главный файл приложения
├── mt5_server.py          # Flask сервер для MT5 (Windows)
├── pages/                  # Страницы интерфейса
│   ├── dashboard.py       # Главная страница
│   ├── parser_bot_page.py # Parser BOT
│   ├── smartmoney_bot_page.py # Smart Money BOT
│   ├── mt5_page.py        # MT5 подключение
│   ├── history_page.py    # История сделок
│   └── settings_page.py   # Настройки
├── services/              # Бизнес-логика
│   ├── mt5_service.py    # Универсальный MT5 сервис
│   ├── logic_manager.py  # Центральный менеджер
│   └── ...
├── components/            # Компоненты интерфейса
└── assets/               # Ресурсы
```

## 🔍 Устранение неполадок

### MT5 не подключается (Windows)
1. Проверьте правильность логина/пароля/сервера
2. Убедитесь, что MT5 терминал запущен
3. Проверьте путь к терминалу

### Flask API недоступен (macOS/Linux)
1. Убедитесь, что сервер запущен на Windows
2. Проверьте IP адрес и порт
3. Проверьте сетевое подключение

### Telegram не работает
1. Проверьте API ID и API Hash
2. Создайте сессию через кнопку "Создать сессию Telegram"
3. Проверьте номер телефона

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в папке `logs/`
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки в разделе Settings

## 📄 Лицензия

MIT License

---

**Примечание:** Торговля на финансовых рынках связана с рисками. Используйте приложение на свой страх и риск. 