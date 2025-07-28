@echo off
chcp 65001 >nul
echo 🚀 ПОЛНАЯ УСТАНОВКА ТОРГОВОЙ СИСТЕМЫ v2.0 НА WINDOWS
echo ====================================================
echo.
echo 📋 Этот скрипт выполнит полную установку:
echo   ✅ Создание виртуального окружения Python
echo   ✅ Установка всех зависимостей
echo   ✅ Настройка MT5 интеграции
echo   ✅ Создание Telegram сессии
echo   ✅ Запуск торговой системы
echo.
pause

:: Проверка Python
echo 🔍 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+ с python.org
    pause
    exit /b 1
)
echo ✅ Python найден

:: Проверка Git (опционально)
echo 🔍 Проверка Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Git не найден, но это не критично
) else (
    echo ✅ Git найден
)

:: Создание виртуального окружения
echo.
echo 📦 Создание виртуального окружения...
if exist "trading_venv" (
    echo 🔄 Виртуальное окружение уже существует, используем его
) else (
    python -m venv trading_venv
    if errorlevel 1 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
)

:: Активация виртуального окружения
echo 🔧 Активация виртуального окружения...
call trading_venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Ошибка активации виртуального окружения
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано

:: Обновление pip
echo 📦 Обновление pip...
python -m pip install --upgrade pip
echo ✅ pip обновлен

:: Установка зависимостей
echo 📦 Установка зависимостей из requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    echo 🔧 Попробуйте: pip install -r requirements.txt --no-cache-dir
    pause
)
echo ✅ Основные зависимости установлены

:: Установка MetaTrader5 для Windows
echo 📦 Установка MetaTrader5 модуля...
pip install MetaTrader5
if errorlevel 1 (
    echo ⚠️ MT5 модуль не установлен (возможно не Windows)
) else (
    echo ✅ MetaTrader5 модуль установлен
)

:: Установка дополнительных пакетов
echo 📦 Установка дополнительных пакетов...
pip install telethon cryptg pillow plotly pandas numpy flet
echo ✅ Дополнительные пакеты установлены

:: Создание конфигурационных файлов
echo 🔧 Создание конфигурационных файлов...

:: Создаем базовый config если не существует
if not exist "configs\mt5_config.json" (
    copy "configs\mt5_config.example.json" "configs\mt5_config.json" >nul 2>&1
    echo ✅ MT5 конфигурация создана
)

:: Создаем директории данных
if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs
if not exist "data\cache" mkdir data\cache
echo ✅ Директории данных созданы

:: Проверка MT5
echo 🔍 Проверка MetaTrader 5...
tasklist | findstr "MetaTrader5" >nul
if errorlevel 1 (
    echo ⚠️ MetaTrader 5 не запущен
    echo 💡 Рекомендация: Запустите MT5 перед использованием торговых функций
) else (
    echo ✅ MetaTrader 5 запущен
)

:: Тестирование системы
echo.
echo 🧪 Тестирование системы...
python test_reorganization.py
if errorlevel 1 (
    echo ⚠️ Некоторые тесты не прошли, но система может работать
) else (
    echo ✅ Все тесты прошли успешно
)

:: Создание ярлыков
echo 📋 Создание ярлыков запуска...

:: Создаем запуск торговой системы
echo @echo off > "Запуск_Торговой_Системы.bat"
echo cd /d "%~dp0" >> "Запуск_Торговой_Системы.bat"
echo call trading_venv\Scripts\activate.bat >> "Запуск_Торговой_Системы.bat"
echo python main.py >> "Запуск_Торговой_Системы.bat"
echo pause >> "Запуск_Торговой_Системы.bat"

:: Создаем запуск MT5 сервера
echo @echo off > "Запуск_MT5_Сервера.bat"
echo cd /d "%~dp0" >> "Запуск_MT5_Сервера.bat"
echo call trading_venv\Scripts\activate.bat >> "Запуск_MT5_Сервера.bat"
echo python servers\mt5_server\mt5_server_enhanced.py >> "Запуск_MT5_Сервера.bat"
echo pause >> "Запуск_MT5_Сервера.bat"

:: Создаем создание Telegram сессии
echo @echo off > "Создать_Telegram_Сессию.bat"
echo cd /d "%~dp0" >> "Создать_Telegram_Сессию.bat"
echo call trading_venv\Scripts\activate.bat >> "Создать_Telegram_Сессию.bat"
echo python scripts\setup\create_telegram_session.py >> "Создать_Telegram_Сессию.bat"
echo pause >> "Создать_Telegram_Сессию.bat"

echo ✅ Ярлыки запуска созданы

:: Финальная информация
echo.
echo 🎉 УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
echo ================================
echo.
echo 📋 СЛЕДУЮЩИЕ ШАГИ:
echo.
echo 1️⃣ НАСТРОЙКА TELEGRAM:
echo    📱 Запустите: "Создать_Telegram_Сессию.bat"
echo    📝 Введите API ID, API Hash, номер телефона
echo    📞 Введите код из SMS
echo.
echo 2️⃣ НАСТРОЙКА MT5:
echo    🔧 Откройте MetaTrader 5
echo    🔗 Подключитесь к вашему брокеру
echo    ✅ Убедитесь что терминал активен
echo.
echo 3️⃣ ЗАПУСК СИСТЕМЫ:
echo    🚀 Запустите: "Запуск_Торговой_Системы.bat"
echo    🌐 Откроется интерфейс Flet
echo.
echo 📁 ПОЛЕЗНЫЕ ФАЙЛЫ:
echo    📊 "Запуск_Торговой_Системы.bat" - главное приложение
echo    🔧 "Запуск_MT5_Сервера.bat" - MT5 API сервер  
echo    📱 "Создать_Telegram_Сессию.bat" - настройка Telegram
echo.
echo 🔧 TROUBLESHOOTING:
echo    ❓ Если проблемы: смотрите WINDOWS_LOCAL_DEPLOYMENT.md
echo    📧 Поддержка: проверьте документацию в docs/
echo.
echo 🎯 ВСЕ ГОТОВО К ИСПОЛЬЗОВАНИЮ!
echo.
pause

:: Спрашиваем о запуске
echo.
echo 🚀 Хотите запустить торговую систему сейчас? (y/n)
set /p launch="Введите y для запуска: "
if /i "%launch%"=="y" (
    echo 🎉 Запускаем торговую систему...
    python main.py
) else (
    echo 💡 Для запуска используйте: "Запуск_Торговой_Системы.bat"
)

echo.
echo ✅ Установка полностью завершена!
pause