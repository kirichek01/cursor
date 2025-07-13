# 🖥️ Запуск проекта в Windows VM с MT5

## Способ 1: Автоматический запуск

1. **Откройте Windows VM** в Parallels Desktop
2. **Скопируйте проект** в Windows:
   ```bash
   # В macOS терминале
   cp -r . "/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized/макет"
   ```
3. **Запустите bat-файл** в Windows:
   - Откройте командную строку Windows
   - Перейдите в папку проекта
   - Запустите: `start_windows.bat`

## Способ 2: Ручной запуск

### Шаг 1: Подготовка Windows VM
1. Откройте **Parallels Desktop**
2. Запустите **Windows 11 VM**
3. Убедитесь, что **MetaTrader 5** установлен в Windows

### Шаг 2: Копирование проекта
```bash
# В macOS терминале
cp -r . "/Users/vladislavkirichek/Applications (Parallels)/{64a44e8b-2a77-4379-9821-4cb170697000} Applications.localized/макет"
```

### Шаг 3: Установка зависимостей в Windows
```cmd
# В Windows командной строке
cd "C:\Users\vladislavkirichek\Desktop\макет"
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 4: Проверка MT5
```cmd
python -c "import MetaTrader5 as mt5; print('MT5 доступен')"
```

### Шаг 5: Запуск приложения
```cmd
python main.py
```

## 🔧 Настройка MT5 в Windows

1. **Установите MetaTrader 5** в Windows VM
2. **Настройте подключение** к брокеру
3. **Войдите в аккаунт** MT5
4. **Убедитесь, что терминал работает**

## 📁 Структура проекта в Windows

```
C:\Users\vladislavkirichek\Desktop\макет\
├── main.py                 # Главный файл
├── requirements.txt        # Зависимости
├── start_windows.bat      # Скрипт запуска
├── services\              # Сервисы
├── pages\                 # Страницы
├── components\            # Компоненты
└── data\                  # Данные
```

## 🚀 Полная функциональность

В Windows VM с MT5 доступны:
- ✅ **Реальная торговля** через MT5
- ✅ **Анализ Smart Money**
- ✅ **Парсинг сигналов**
- ✅ **Управление позициями**
- ✅ **История сделок**
- ✅ **Настройки брокера**

## 🔍 Проверка работы

1. **Откройте браузер** в Windows VM
2. **Перейдите** на `http://localhost:8550`
3. **Проверьте** все функции приложения
4. **Подключитесь** к MT5 через интерфейс

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте, что MT5 запущен в Windows
2. Убедитесь, что все зависимости установлены
3. Проверьте логи в консоли Windows 