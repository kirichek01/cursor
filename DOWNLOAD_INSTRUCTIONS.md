# 📥 Инструкция по скачиванию проекта

## 🎯 У вас есть несколько способов получить проект на свой компьютер:

## **Способ 1: Git клонирование (рекомендуется) 🏆**

### Для Windows:
```bash
# Откройте Git Bash или PowerShell
git clone https://github.com/kirichek01/cursor.git trading_system
cd trading_system

# Переключитесь на ветку с реорганизацией
git checkout cursor/bc-38e1de7a-1d0f-421b-91a6-76a49547c1fb-c202

# Или слейте в main (рекомендуется)
git checkout main
git merge cursor/bc-38e1de7a-1d0f-421b-91a6-76a49547c1fb-c202
```

### Для Linux/Mac:
```bash
git clone https://github.com/kirichek01/cursor.git trading_system
cd trading_system
git checkout cursor/bc-38e1de7a-1d0f-421b-91a6-76a49547c1fb-c202
```

## **Способ 2: Скачать ZIP с GitHub 📦**

1. **Перейдите на GitHub:**
   https://github.com/kirichek01/cursor

2. **Нажмите зеленую кнопку "Code"**

3. **Выберите "Download ZIP"**

4. **Распакуйте архив** в папку `trading_system`

## **Способ 3: Скачать готовые архивы 💾**

В проекте созданы готовые архивы:

### ZIP архив (Git):
- **Файл:** `trading_system_v2.0_reorganized.zip` (1.3MB)
- **Содержит:** Полную Git историю + весь проект

### TAR.GZ архив (чистый):
- **Файл:** `trading_system_complete_20250728_1802.tar.gz` (157KB)
- **Содержит:** Только важные файлы проекта без Git

### Как скачать архивы:
```bash
# Если у вас есть доступ к серверу
scp user@server:/workspace/trading_system_v2.0_reorganized.zip .
scp user@server:/workspace/trading_system_complete_20250728_1802.tar.gz .
```

## **Способ 4: Использование GitHub CLI 🔧**

```bash
# Установите GitHub CLI, затем:
gh repo clone kirichek01/cursor trading_system
cd trading_system
gh checkout cursor/bc-38e1de7a-1d0f-421b-91a6-76a49547c1fb-c202
```

## **После скачивания:**

### 1. **Установите зависимости:**
```bash
cd trading_system
pip install -r requirements.txt
```

### 2. **Протестируйте систему:**
```bash
python test_reorganization.py
```

### 3. **Запустите приложение:**
```bash
python main.py
```

### 4. **Для Windows - запустите MT5 сервер:**
```bash
scripts/windows/start_mt5_server_enhanced.bat
```

## **Структура после скачивания:**

```
trading_system/
├── app/                    # Основное приложение
├── core/                   # Бизнес-логика  
├── bots/                   # Торговые боты
├── ui/                     # Интерфейс
├── servers/                # MT5 серверы
├── scripts/                # Скрипты запуска
├── configs/                # Конфигурации
├── docs/                   # Документация
├── main.py                 # 🚀 Главный launcher
├── requirements.txt        # Зависимости
└── README_NEW_STRUCTURE.md # Руководство
```

## **Содержимое архива `trading_system_complete_20250728_1802.tar.gz`:**

✅ **Основные модули:**
- `app/` - TradingApp, AppConfig
- `core/` - services, logic, models
- `bots/` - smart_money, parser
- `ui/` - pages, components, widgets

✅ **Серверы и скрипты:**
- `servers/` - MT5 серверы
- `scripts/` - Windows .bat файлы

✅ **Документация:**
- `README_NEW_STRUCTURE.md`
- `REORGANIZATION_COMPLETE.md`
- `test_reorganization.py`
- `SAVE_PROJECT_GUIDE.md`

✅ **Конфигурация:**
- `requirements.txt`
- `main.py`
- `configs/`

## **Проверка целостности:**

После скачивания выполните:

```bash
# Проверьте структуру
ls -la app/ core/ bots/ ui/ servers/

# Протестируйте импорты
python -c "from app import TradingApp, AppConfig; print('✅ App works')"
python -c "from core.services.database_service import DatabaseService; print('✅ Core works')"

# Полный тест
python test_reorganization.py
```

## **Troubleshooting:**

### Проблема: "No module named 'flet'"
```bash
pip install flet plotly pandas numpy
```

### Проблема: "MetaTrader5 not found"
```bash
# Это нормально в Linux/Mac, MT5 работает через сервер
# Используйте Windows для прямого подключения к MT5
```

### Проблема: Git ошибки
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## **🎉 Готово!**

После скачивания у вас будет полная рабочая торговая система с:
- ✅ Профессиональной структурой
- ✅ Реальными данными only
- ✅ MT5 интеграцией
- ✅ Telegram парсером
- ✅ SmartMoney ботом
- ✅ Полной документацией

**Система готова к использованию!** 🚀