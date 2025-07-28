@echo off
echo ========================================
echo    CombineTradeBot - Windows Setup
echo ========================================
echo.

echo [1/4] Переходим в директорию проекта...
cd /d "C:\Users\vladislavkirichek\Desktop\макет"

echo [2/4] Устанавливаем Python зависимости...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/4] Проверяем MT5...
python -c "import MetaTrader5 as mt5; print('✅ MT5 доступен')"

echo [4/4] Запускаем приложение...
python main.py

pause 