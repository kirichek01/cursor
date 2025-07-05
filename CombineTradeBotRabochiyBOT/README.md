# Combine Trade Bot

Автоматический бот для чтения Telegram‑сигналов, анализа GPT и отправки в MT5.

## Запуск

```bash
git clone ...
cd CombineTradeBot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Windows**: используйте `run.bat`.

## Сборка в .exe

```bash
pyinstaller --noconfirm --onefile main.py --hidden-import PySide6.QtWebEngineWidgets
```

Требуется Python 3.10‑3.11.
