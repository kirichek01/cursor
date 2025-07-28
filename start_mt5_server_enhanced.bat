@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    РАСШИРЕННЫЙ MT5 СЕРВЕР LAUNCHER
echo    Только реальные данные, никаких демо
echo ========================================
echo.

:: Установка кодировки UTF-8
chcp 65001 >nul

:: Проверка и переход в папку скрипта
cd /d "%~dp0"
echo 📁 Текущая директория: %CD%
echo.

:: Проверка наличия Python
echo 🔍 Проверка наличия Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Python не найден! Установите Python 3.8+ и добавьте в PATH
    pause
    exit /b 1
)
echo ✅ Python обнаружен
python --version
echo.

:: Проверка наличия pip
echo 🔍 Проверка pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: pip не найден!
    pause
    exit /b 1
)
echo ✅ pip обнаружен
echo.

:: Создание/активация виртуального окружения
if not exist "venv" (
    echo 🏗️ Создание виртуального окружения...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ ОШИБКА: Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
)

echo 🔌 Активация виртуального окружения...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано
echo.

:: Обновление pip в виртуальном окружении
echo 📦 Обновление pip...
python -m pip install --upgrade pip
echo.

:: Установка зависимостей
echo 📦 Установка основных зависимостей...
pip install flask MetaTrader5 requests pandas numpy plotly matplotlib
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Не удалось установить зависимости
    pause
    exit /b 1
)
echo ✅ Зависимости установлены
echo.

:: Проверка существования расширенного сервера
if exist "mt5_server_enhanced.py" (
    set SERVER_FILE=mt5_server_enhanced.py
    echo ✅ Найден расширенный сервер: mt5_server_enhanced.py
) else if exist "mt5_server.py" (
    set SERVER_FILE=mt5_server.py
    echo ⚠️ Используется стандартный сервер: mt5_server.py
) else (
    echo ❌ ОШИБКА: Файлы серверов не найдены!
    echo Убедитесь, что вы запускаете bat-файл из правильной папки
    pause
    exit /b 1
)
echo.

:: Проверка конфигурационного файла
if exist "mt5_config.json" (
    echo ✅ Найден файл конфигурации: mt5_config.json
) else if exist "mt5_config.example.json" (
    echo ⚠️ Найден только пример конфигурации
    echo 💡 Скопируйте mt5_config.example.json в mt5_config.json и настройте
    echo 📝 Или используйте /initialize endpoint для настройки
) else (
    echo ℹ️ Конфигурационный файл не найден - будет использована ручная настройка
)
echo.

:: Настройки сети
echo 🌐 КОНФИГУРАЦИЯ СЕТИ:
echo    - Локальный доступ: http://localhost:5000
echo    - Сетевой доступ: http://[IP-адрес]:5000
echo    - Для VM: используйте IP-адрес основной системы
echo.

:: Проверка порта
echo 🔍 Проверка порта 5000...
netstat -an | find "5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️ Порт 5000 уже используется! Возможен конфликт.
    echo 💡 Остановите другие сервисы или измените порт в конфигурации
) else (
    echo ✅ Порт 5000 свободен
)
echo.

:: Настройки брандмауэра
echo 🔒 ВАЖНЫЕ ТРЕБОВАНИЯ:
echo    ✓ Порт 5000 открыт в брандмауэре Windows
echo    ✓ Настроены сетевые адаптеры виртуальной машины
echo    ✓ MT5 запущен и доступен на виртуальной машине
echo    ✓ Используются только РЕАЛЬНЫЕ торговые счета
echo.

:: API endpoints
echo 📡 ДОСТУПНЫЕ API ENDPOINTS:
echo    GET  /health        - Статус сервера и соединения
echo    POST /initialize    - Подключение к MT5
echo    GET  /account_info  - Информация о торговом счете
echo    GET  /positions     - Открытые позиции
echo    GET  /rates         - Котировки инструментов
echo    GET  /config        - Текущая конфигурация
echo    POST /shutdown      - Отключение от MT5
echo.

:: Пример инициализации
echo ⚙️ ПРИМЕР ИНИЦИАЛИЗАЦИИ MT5:
echo    POST http://localhost:5000/initialize
echo    Content-Type: application/json
echo    {
echo      "path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
echo      "login": 1234567890,
echo      "password": "ваш_пароль",
echo      "server": "имя_сервера_брокера"
echo    }
echo.

:: Запуск сервера
echo 🚀 ЗАПУСК РАСШИРЕННОГО MT5 СЕРВЕРА...
echo 🔄 Для остановки нажмите Ctrl+C
echo 📊 РЕЖИМ: Только реальные данные
echo ========================================
echo.

python !SERVER_FILE!

:: Обработка завершения
echo.
echo ========================================
echo 🛑 Сервер остановлен
echo.
if %errorlevel% neq 0 (
    echo ❌ Сервер завершился с ошибкой (код: %errorlevel%)
    echo 💡 Проверьте mt5_server.log для диагностики
) else (
    echo ✅ Сервер завершен корректно
)

echo.
echo 📊 ФАЙЛЫ ЛОГОВ:
if exist "mt5_server.log" (
    echo    ✅ mt5_server.log - Логи сервера
) else (
    echo    ❌ Логи не созданы
)

echo.
echo 🛠️ ДИАГНОСТИЧЕСКИЕ КОМАНДЫ:
echo    netstat -an ^| find "5000"           - Проверка порта
echo    ipconfig                            - IP-адрес системы  
echo    ping [IP_виртуальной_машины]        - Связь с VM
echo    curl http://localhost:5000/health   - Тест API
echo.

echo 📖 ДОКУМЕНТАЦИЯ:
echo    Подробная документация доступна в README_MT5_SERVER.md
echo.

echo Нажмите любую клавишу для выхода...
pause >nul