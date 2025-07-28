# План реорганизации проекта

## Новая структура папок

```
trading_system/
├── app/                          # Основное приложение
│   ├── __init__.py
│   ├── main.py                   # Главный файл приложения
│   └── config.py                 # Конфигурация приложения
│
├── core/                         # Основная бизнес-логика
│   ├── __init__.py
│   ├── services/                 # Основные сервисы
│   │   ├── __init__.py
│   │   ├── database_service.py
│   │   ├── mt5_service.py
│   │   ├── telegram_service.py
│   │   ├── trade_manager_service.py
│   │   ├── signal_processor.py
│   │   └── gpt_service.py
│   ├── logic/                    # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── logic_manager.py
│   │   └── smc_logic.py
│   └── models/                   # Модели данных
│       ├── __init__.py
│       ├── trade.py
│       ├── signal.py
│       └── account.py
│
├── bots/                         # Торговые боты
│   ├── __init__.py
│   ├── smart_money/              # SmartMoney бот
│   │   ├── __init__.py
│   │   ├── smc_bot.py
│   │   ├── smc_bot_core.py
│   │   ├── smc_runner.py
│   │   ├── ai_agent.py
│   │   └── config.py
│   └── parser/                   # Telegram парсер
│       ├── __init__.py
│       └── parser_logic.py
│
├── ui/                          # Пользовательский интерфейс
│   ├── __init__.py
│   ├── pages/                   # Страницы приложения
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── parser_bot_page.py
│   │   ├── smartmoney_bot_page.py
│   │   ├── mt5_page.py
│   │   ├── settings_page.py
│   │   └── history_page.py
│   ├── components/              # UI компоненты
│   │   ├── __init__.py
│   │   ├── charts.py
│   │   ├── header.py
│   │   ├── sidebar.py
│   │   └── right_panel.py
│   ├── widgets/                 # Виджеты
│   │   ├── __init__.py
│   │   └── widgets.py
│   └── theme.py                 # Тема оформления
│
├── servers/                     # Серверные компоненты
│   ├── __init__.py
│   ├── mt5_server/              # MT5 сервер
│   │   ├── __init__.py
│   │   ├── mt5_server.py
│   │   ├── mt5_server_enhanced.py
│   │   └── config.py
│   └── api/                     # API endpoints
│       ├── __init__.py
│       └── routes.py
│
├── utils/                       # Утилиты
│   ├── __init__.py
│   ├── helpers.py
│   ├── constants.py
│   └── validators.py
│
├── data/                        # Данные
│   ├── __init__.py
│   ├── database/               # База данных
│   │   └── trading_data.db
│   ├── logs/                   # Логи
│   └── cache/                  # Кэш
│
├── configs/                     # Конфигурационные файлы
│   ├── __init__.py
│   ├── mt5_config.example.json
│   ├── app_config.json
│   └── settings.json
│
├── scripts/                     # Скрипты запуска и установки
│   ├── windows/                # Windows скрипты
│   │   ├── start_mt5_server.bat
│   │   ├── start_mt5_server_enhanced.bat
│   │   ├── start_windows.bat
│   │   └── install_dependencies.bat
│   ├── linux/                  # Linux скрипты
│   │   └── start.sh
│   └── setup/                  # Установка
│       ├── install_dependencies.py
│       └── setup.py
│
├── tests/                       # Тесты
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                        # Документация
│   ├── README.md
│   ├── API.md
│   ├── SETUP.md
│   ├── MT5_SERVER.md
│   └── TROUBLESHOOTING.md
│
├── requirements.txt             # Зависимости Python
├── .gitignore
└── .env.example                # Пример переменных окружения
```

## Этапы реорганизации

### Этап 1: Создание новой структуры папок
### Этап 2: Перемещение файлов
### Этап 3: Обновление импортов
### Этап 4: Тестирование связей
### Этап 5: Очистка дублирующихся файлов