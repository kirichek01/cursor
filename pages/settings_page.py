import flet as ft

def create_settings_view(settings: dict, logic_manager=None):
    """
    Создает и возвращает view для страницы настроек с полной интеграцией логики ботов.
    """
    
    # ----- ЭЛЕМЕНТЫ УПРАВЛЕНИЯ -----
    
    # Telegram
    api_id_input = ft.TextField(label="Telegram API ID", value=settings.get("telegram", {}).get("api_id", ""), password=True)
    api_hash_input = ft.TextField(label="Telegram API Hash", value=settings.get("telegram", {}).get("api_hash", ""), password=True)
    session_file_input = ft.TextField(label="Session File Name", value=settings.get("telegram", {}).get("session_file", "userbot.session"))
    
    # MT5
    mt5_login_input = ft.TextField(label="MT5 Login", value=settings.get("mt5", {}).get("login", ""))
    mt5_password_input = ft.TextField(label="MT5 Password", value=settings.get("mt5", {}).get("password", ""), password=True)
    mt5_server_input = ft.TextField(label="MT5 Server", value=settings.get("mt5", {}).get("server", ""))
    mt5_path_input = ft.TextField(label="MT5 Path (for Windows)", value=settings.get("mt5", {}).get("path", ""))

    # GPT
    gpt_key_input = ft.TextField(label="OpenAI API Key", value=settings.get("gpt", {}).get("api_key", ""), password=True)
    
    # Signal Parser
    signal_parser_enabled = ft.Checkbox(label="Enable Signal Parser", value=settings.get("signal_parser", {}).get("enabled", True))
    
    # AI Trader
    ai_trader_enabled = ft.Checkbox(label="Enable AI Trader", value=settings.get("ai_trader", {}).get("enabled", False))
    ai_lot_size = ft.TextField(label="AI Lot Size", value=str(settings.get("ai_trader", {}).get("lot_size", 0.01)))
    ai_live_trading = ft.Checkbox(label="Live Trading", value=settings.get("ai_trader", {}).get("live_trading", False))
    
    # Trading Settings
    trading_lot_size = ft.TextField(label="Default Lot Size", value=str(settings.get("trading", {}).get("lot_size", 0.01)))
    trading_max_risk = ft.TextField(label="Max Risk %", value=str(settings.get("trading", {}).get("max_risk", 2)))
    
    # Breakeven Settings
    breakeven_enabled = ft.Checkbox(label="Enable Breakeven", value=settings.get("breakeven", {}).get("enabled", False))
    breakeven_pips = ft.TextField(label="Breakeven Pips", value=str(settings.get("breakeven", {}).get("pips", 20)))
    
    # Кнопки управления
    save_button = ft.ElevatedButton(text="Сохранить настройки", icon="save")
    test_gpt_button = ft.ElevatedButton(text="Тест GPT", icon="psychology")
    test_mt5_button = ft.ElevatedButton(text="Тест MT5", icon="account_balance")
    
    # Статусы сервисов
    telegram_status = ft.Text("Telegram: ОФФЛАЙН", color="#ff6a6a", size=12)
    mt5_status = ft.Text("MT5: ОФФЛАЙН", color="#ff6a6a", size=12)
    gpt_status = ft.Text("GPT: ОФФЛАЙН", color="#ff6a6a", size=12)
    db_status = ft.Text("Database: ОФФЛАЙН", color="#ff6a6a", size=12)
    
    # Кнопки управления ботом
    start_bot_button = ft.ElevatedButton(text="Запустить бота", icon="play_arrow", bgcolor="#4CAF50")
    stop_bot_button = ft.ElevatedButton(text="Остановить бота", icon="stop", bgcolor="#f44336")
    start_ai_button = ft.ElevatedButton(text="Запустить AI Trader", icon="smart_toy", bgcolor="#2196F3")
    stop_ai_button = ft.ElevatedButton(text="Остановить AI Trader", icon="smart_toy", bgcolor="#FF9800")
    
    # Статистика
    stats_text = ft.Text("Статистика загружается...", size=14)
    
    def update_statuses():
        """Обновляет статусы сервисов."""
        if logic_manager:
            status = logic_manager.get_bot_status()
            
            # Обновляем статусы сервисов
            telegram_status.value = f"Telegram: {'ПОДКЛЮЧЕН' if status['services']['telegram'] else 'ОФФЛАЙН'}"
            telegram_status.color = "#4CAF50" if status['services']['telegram'] else "#ff6a6a"
            
            mt5_status.value = f"MT5: {'ПОДКЛЮЧЕН' if status['services']['mt5'] else 'ОФФЛАЙН'}"
            mt5_status.color = "#4CAF50" if status['services']['mt5'] else "#ff6a6a"
            
            gpt_status.value = f"GPT: {'ПОДКЛЮЧЕН' if status['services']['gpt'] else 'ОФФЛАЙН'}"
            gpt_status.color = "#4CAF50" if status['services']['gpt'] else "#ff6a6a"
            
            db_status.value = f"Database: {'ПОДКЛЮЧЕН' if status['services']['database'] else 'ОФФЛАЙН'}"
            db_status.color = "#4CAF50" if status['services']['database'] else "#ff6a6a"
            
            # Обновляем статистику
            stats = status.get('stats', {})
            stats_text.value = f"Сигналов: {stats.get('total_signals', 0)} | Успешных сделок: {stats.get('successful_trades', 0)} | Прибыль: ${stats.get('total_profit', 0):.2f}"
            
            # Обновляем кнопки
            start_bot_button.disabled = status['bot_running']
            stop_bot_button.disabled = not status['bot_running']
            start_ai_button.disabled = not status['bot_running'] or status['ai_trader_running']
            stop_ai_button.disabled = not status['ai_trader_running']
            
            if hasattr(settings_view, 'page') and settings_view.page:
                settings_view.page.update()
    
    def on_save_settings(e):
        """Сохраняет настройки."""
        try:
            new_settings = {
                "telegram": {
                    "api_id": api_id_input.value,
                    "api_hash": api_hash_input.value,
                    "session_file": session_file_input.value
                },
                "mt5": {
                    "login": mt5_login_input.value,
                    "password": mt5_password_input.value,
                    "server": mt5_server_input.value,
                    "path": mt5_path_input.value
                },
                "gpt": {
                    "api_key": gpt_key_input.value
                },
                "signal_parser": {
                    "enabled": signal_parser_enabled.value
                },
                "ai_trader": {
                    "enabled": ai_trader_enabled.value,
                    "lot_size": float(ai_lot_size.value) if ai_lot_size.value else 0.01,
                    "live_trading": ai_live_trading.value
                },
                "trading": {
                    "lot_size": float(trading_lot_size.value) if trading_lot_size.value else 0.01,
                    "max_risk": float(trading_max_risk.value) if trading_max_risk.value else 2
                },
                "breakeven": {
                    "enabled": breakeven_enabled.value,
                    "pips": int(breakeven_pips.value) if breakeven_pips.value else 20
                }
            }
            
            if logic_manager:
                success = logic_manager.update_settings(new_settings)
                if success:
                    print("Настройки сохранены!")
                else:
                    print("Ошибка сохранения настроек!")
            
            update_statuses()
            
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def on_test_gpt(e):
        """Тестирует GPT API ключ."""
        if logic_manager and gpt_key_input.value:
            success = logic_manager.test_gpt_key(gpt_key_input.value)
            if success:
                print("GPT API ключ работает!")
            else:
                print("GPT API ключ не работает!")
        else:
            print("Введите GPT API ключ!")
    
    def on_test_mt5(e):
        """Тестирует подключение к MT5."""
        if logic_manager:
            account_info = logic_manager.get_account_info()
            if account_info:
                balance = account_info.get('balance', 0)
                print(f"MT5 подключен! Баланс: ${balance:.2f}")
            else:
                print("MT5 не подключен!")
        else:
            print("LogicManager не доступен!")
    
    def on_start_bot(e):
        """Запускает бота."""
        if logic_manager:
            logic_manager.start_bot()
            update_statuses()
            print("Бот запущен!")
    
    def on_stop_bot(e):
        """Останавливает бота."""
        if logic_manager:
            logic_manager.stop_bot()
            update_statuses()
            print("Бот остановлен!")
    
    def on_start_ai(e):
        """Запускает AI Trader."""
        if logic_manager:
            logic_manager.start_ai_trader()
            update_statuses()
            print("AI Trader запущен!")
    
    def on_stop_ai(e):
        """Останавливает AI Trader."""
        if logic_manager:
            logic_manager.stop_ai_trader()
            update_statuses()
            print("AI Trader остановлен!")
    
    # Привязываем обработчики событий
    save_button.on_click = on_save_settings
    test_gpt_button.on_click = on_test_gpt
    test_mt5_button.on_click = on_test_mt5
    start_bot_button.on_click = on_start_bot
    stop_bot_button.on_click = on_stop_bot
    start_ai_button.on_click = on_start_ai
    stop_ai_button.on_click = on_stop_ai

    # ----- СБОРКА СТРАНИЦЫ -----
    settings_content = ft.Column(
        [
            ft.Text("Настройки бота", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Статусы сервисов
            ft.Text("Статус сервисов", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([telegram_status, mt5_status], spacing=20),
            ft.Row([gpt_status, db_status], spacing=20),
            ft.Divider(),
            
            # Статистика
            ft.Text("Статистика", size=18, weight=ft.FontWeight.BOLD),
            stats_text,
            ft.Divider(),
            
            # Управление ботом
            ft.Text("Управление ботом", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([start_bot_button, stop_bot_button], spacing=10),
            ft.Row([start_ai_button, stop_ai_button], spacing=10),
            ft.Divider(),
            
            # Telegram настройки
            ft.Text("Telegram", size=18, weight=ft.FontWeight.BOLD),
            api_id_input,
            api_hash_input,
            session_file_input,
            ft.Divider(),

            # MT5 настройки
            ft.Text("MetaTrader 5", size=18, weight=ft.FontWeight.BOLD),
            mt5_login_input,
            mt5_password_input,
            mt5_server_input,
            mt5_path_input,
            ft.Row([test_mt5_button], spacing=10),
            ft.Divider(),

            # GPT настройки
            ft.Text("GPT (OpenAI)", size=18, weight=ft.FontWeight.BOLD),
            gpt_key_input,
            ft.Row([test_gpt_button], spacing=10),
            ft.Divider(),
            
            # Signal Parser настройки
            ft.Text("Signal Parser", size=18, weight=ft.FontWeight.BOLD),
            signal_parser_enabled,
            ft.Divider(),
            
            # AI Trader настройки
            ft.Text("AI Trader", size=18, weight=ft.FontWeight.BOLD),
            ai_trader_enabled,
            ai_lot_size,
            ai_live_trading,
            ft.Divider(),
            
            # Trading настройки
            ft.Text("Trading Settings", size=18, weight=ft.FontWeight.BOLD),
            trading_lot_size,
            trading_max_risk,
            ft.Divider(),
            
            # Breakeven настройки
            ft.Text("Breakeven Settings", size=18, weight=ft.FontWeight.BOLD),
            breakeven_enabled,
            breakeven_pips,
            ft.Divider(),

            # Кнопка сохранения
            ft.Row([save_button], spacing=10),
            ft.Container(height=20)
        ],
        spacing=10,
        scroll=ft.ScrollMode.ADAPTIVE
    )
    
    # Оборачиваем в контейнер с прокруткой
    settings_view = ft.Container(
        content=settings_content,
        expand=True,
        padding=ft.padding.all(24)
    )
    
    # Инициализируем статусы
    update_statuses()
    
    # Возвращаем и layout, и словарь с контролами
    controls = {
        "api_id": api_id_input,
        "api_hash": api_hash_input,
        "session_file": session_file_input,
        "mt5_login": mt5_login_input,
        "mt5_password": mt5_password_input,
        "mt5_server": mt5_server_input,
        "mt5_path": mt5_path_input,
        "gpt_key": gpt_key_input,
        "signal_parser_enabled": signal_parser_enabled,
        "ai_trader_enabled": ai_trader_enabled,
        "ai_lot_size": ai_lot_size,
        "ai_live_trading": ai_live_trading,
        "trading_lot_size": trading_lot_size,
        "trading_max_risk": trading_max_risk,
        "breakeven_enabled": breakeven_enabled,
        "breakeven_pips": breakeven_pips,
        "save_button": save_button,
        "update_statuses": update_statuses
    }
    
    return settings_view, controls 