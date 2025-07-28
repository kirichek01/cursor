@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    ПРОФЕССИОНАЛЬНЫЙ MT5 СЕРВЕР LAUNCHER
echo    для подключения к MT5 на виртуальной машине
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

:: Проверка существования файла сервера
if not exist "mt5_server.py" (
    echo ❌ ОШИБКА: Файл mt5_server.py не найден в текущей директории!
    echo Убедитесь, что вы запускаете bat-файл из правильной папки
    pause
    exit /b 1
)

:: Настройки сети
echo 🌐 Конфигурация сети:
echo    - Сервер будет доступен на: http://localhost:5000
echo    - Для доступа с других машин: http://[IP-адрес]:5000
echo    - Для виртуальной машины используйте IP хоста
echo.

:: Настройки брандмауэра
echo 🔒 ВАЖНО: Убедитесь, что:
echo    - Порт 5000 открыт в брандмауэре Windows
echo    - Сетевые настройки виртуальной машины позволяют подключение
echo    - MT5 запущен и настроен на виртуальной машине
echo.

:: Отображение конфигурации MT5
echo ⚙️ КОНФИГУРАЦИЯ MT5:
echo    Для подключения к серверу отправьте POST запрос на /initialize с параметрами:
echo    {
echo      "path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
echo      "login": ваш_логин,
echo      "password": "ваш_пароль", 
echo      "server": "имя_сервера"
echo    }
echo.

:: Запуск сервера
echo 🚀 Запуск MT5 Flask сервера...
echo 🔄 Для остановки сервера нажмите Ctrl+C
echo ========================================
echo.

python mt5_server.py

:: Обработка завершения
echo.
echo ========================================
echo 🛑 Сервер остановлен
echo.
if %errorlevel% neq 0 (
    echo ❌ Сервер завершился с ошибкой (код: %errorlevel%)
    echo 💡 Проверьте логи выше для диагностики
) else (
    echo ✅ Сервер завершен корректно
)

echo.
echo 💡 ПОЛЕЗНЫЕ КОМАНДЫ ДЛЯ ДИАГНОСТИКИ:
echo    - netstat -an ^| find "5000" (проверка порта)
echo    - ipconfig (получение IP-адреса)
echo    - ping [IP виртуальной машины] (проверка связи с VM)
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
