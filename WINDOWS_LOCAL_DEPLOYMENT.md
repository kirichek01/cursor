# 🖥️ ЛОКАЛЬНОЕ РАЗВЕРТЫВАНИЕ НА WINDOWS

## ✅ **ВЫ ПРАВЫ! Web-версия не подходит для полного функционала.**

**Нужно:** Локальный запуск на Windows с виртуальным сервером для полной функциональности

---

## 🎯 **ПЛАН ЛОКАЛЬНОГО РАЗВЕРТЫВАНИЯ:**

### **💻 Система требований:**
- **OS:** Windows 10/11 (для MT5)
- **Python:** 3.8+ 
- **MT5:** MetaTrader 5 установлен
- **RAM:** 4GB+ рекомендуется
- **Место:** 2GB свободного места

### **✅ Что будет ПОЛНОСТЬЮ работать локально:**
- ✅ **Создание Telegram сессий** (SMS коды)
- ✅ **Прямое подключение к MT5** (без API)
- ✅ **Полный парсинг каналов** в реальном времени
- ✅ **Размещение ордеров** через MT5
- ✅ **Все торговые боты** (SmartMoney + Parser)
- ✅ **Flet интерфейс** (desktop mode)
- ✅ **Доступ к файловой системе**

---

## 📦 **ЭТАПЫ РАЗВЕРТЫВАНИЯ:**

### **1. Скачивание проекта:**
```bash
# Клонируем чистую версию
git clone https://github.com/kirichek01/cursor.git trading_system_local
cd trading_system_local
git checkout cursor/bc-38e1de7a-1d0f-421b-91a6-76a49547c1fb-c202
```

### **2. Создание виртуального окружения:**
```bash
# Создаем изолированное окружение
python -m venv trading_venv

# Активируем (Windows)
trading_venv\Scripts\activate

# Устанавливаем зависимости
pip install -r requirements.txt
pip install MetaTrader5  # Для Windows
```

### **3. Настройка MT5:**
```bash
# Запускаем MT5 сервер локально
scripts\windows\start_mt5_server_enhanced.bat
```

### **4. Настройка Telegram:**
```bash
# Создаем сессию локально (интерактивно)
python scripts\setup\create_telegram_session.py
```

### **5. Запуск системы:**
```bash
# Главное приложение
python main.py
```

---

## 🔧 **АВТОМАТИЧЕСКИЕ СКРИПТЫ SETUP:**

### **Windows Batch для полного развертывания:**
```