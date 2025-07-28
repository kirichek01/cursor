import flet as ft
import json
import os
import subprocess
import sys

def create_settings_view(page: ft.Page, settings: dict, logic_manager=None):
    # 'page' is already passed as an argument to create_settings_view.
    # We will use 'page' directly for all Flet UI operations within this function.

    # --- Функции-обработчики для модальных окон и удаления сессии (определяются до диалогов) ---
    def on_code_submit(code):
        print(f"Код введен: {code}")
        if page:
            page.close_dialog()
            page.update() # Обновить страницу после закрытия диалога
        if logic_manager and hasattr(logic_manager, 'submit_telegram_code'):
            logic_manager.submit_telegram_code(code)

    def on_password_submit(password):
        print(f"Пароль введен: {password}")
        if page:
            page.close_dialog()
            page.update() # Обновить страницу после закрытия диалога
        if logic_manager and hasattr(logic_manager, 'submit_telegram_password'):
            logic_manager.submit_telegram_password(password)

    def on_delete_session(e):
        print("Удаление сессии Telegram...")
        # Обновляем логику удаления сессии, чтобы она вызывалась через logic_manager
        if logic_manager and hasattr(logic_manager, 'delete_telegram_session'):
            logic_manager.delete_telegram_session()
            session_log.value = "Сессия Telegram удалена."
            session_log.color = "#4CAF50"
            session_log.update()
            update_statuses()
        else:
            # На случай, если logic_manager еще не готов, удаляем файл напрямую
            session_file = session_file_input.value or "userbot.session"
            session_path = os.path.join("data", session_file)
            if os.path.exists(session_path):
                os.remove(session_path)
                session_log.value = "✅ Сессия Telegram удалена (файл)."
                session_log.color = "#4CAF50"
            else:
                session_log.value = "❌ Файл сессии не найден."
                session_log.color = "#f44336"
            session_log.update()
            update_statuses()


    # --- Модальные окна для кода и пароля ---
    code_input = ft.TextField(label="Введите код из Telegram", autofocus=True)
    password_input = ft.TextField(label="Облачный пароль Telegram", password=True, autofocus=True)

    code_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Подтверждение Telegram"),
        content=code_input,
        actions=[
            ft.TextButton("OK", on_click=lambda e: on_code_submit(code_input.value))
        ],
        open=False
    )
    password_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Облачный пароль Telegram"),
        content=password_input,
        actions=[
            ft.TextButton("OK", on_click=lambda e: on_password_submit(password_input.value))
        ],
        open=False
    )

    # --- Функции для показа модальных окон ---
    def show_code_dialog():
        print("Вызов show_code_dialog!")
        code_input.value = "" # Очищаем поле ввода
        if page:
            page.open_dialog(code_dialog)
            page.update()

    def show_password_dialog():
        print("Вызов show_password_dialog!")
        password_input.value = "" # Очищаем поле ввода
        if page:
            page.open_dialog(password_dialog)
            page.update()

    # --- Подписка на события Telegram через pubsub ---
    page.pubsub.subscribe_topic("telegram_code_required", lambda _: show_code_dialog())
    page.pubsub.subscribe_topic("telegram_password_required", lambda _: show_password_dialog())
    print("Подписка на события Telegram pubsub создана в settings_page.")

    # Определяем режим работы MT5
    mt5_mode = "flask"  # По умолчанию Flask API для macOS
    if logic_manager and logic_manager.mt5:
        mt5_mode = logic_manager.mt5.mode

    # ----- ЭЛЕМЕНТЫ УПРАВЛЕНИЯ -----
    # Telegram
    api_id_input = ft.TextField(label="Telegram API ID", value=settings.get("telegram", {}).get("api_id", ""), password=True)
    api_hash_input = ft.TextField(label="Telegram API Hash", value=settings.get("telegram", {}).get("api_hash", ""), password=True)
    phone_input = ft.TextField(label="Номер телефона", value=settings.get("telegram", {}).get("phone", ""), hint_text="+79001234567")
    session_file_input = ft.TextField(label="Session File Name", value=settings.get("telegram", {}).get("session_file", "userbot.session"))
    delete_session_button = ft.ElevatedButton(
        text="Удалить сессию Telegram", icon="delete", bgcolor="#f44336", color="white"
    )
    delete_session_button.on_click = on_delete_session # Привязываем обработчик для кнопки удаления сессии

    # MT5 - Локальный режим (только для Windows)
    mt5_login_input = ft.TextField(label="MT5 Login", value=settings.get("mt5", {}).get("login", ""))
    mt5_password_input = ft.TextField(label="MT5 Password", value=settings.get("mt5", {}).get("password", ""), password=True)
    mt5_server_input = ft.TextField(label="MT5 Server", value=settings.get("mt5", {}).get("server", ""))
    mt5_path_input = ft.TextField(label="MT5 Path (for Windows)", value=settings.get("mt5", {}).get("path", ""))

    # MT5 - Flask API режим (для macOS/Linux)
    mt5_flask_url_input = ft.TextField(label="MT5 Server URL", value=settings.get("mt5_server", {}).get("url", "http://10.211.55.3:5000"))

    # Переключатель режима MT5
    mt5_mode_switch = ft.Switch(label="Локальный MT5 (Windows)", value=mt5_mode == "local")

    # Показываем/скрываем поля в зависимости от режима
    def on_mt5_mode_change(e):
        is_local = mt5_mode_switch.value
        mt5_login_input.visible = is_local
        mt5_password_input.visible = is_local
        mt5_server_input.visible = is_local
        mt5_path_input.visible = is_local
        mt5_flask_url_input.visible = not is_local
        
        # Обновляем страницу
        if page:
            page.update()
    
    mt5_mode_switch.on_change = on_mt5_mode_change
    
    # Инициализируем видимость полей
    is_local_mode = mt5_mode == "local"
    mt5_login_input.visible = is_local_mode
    mt5_password_input.visible = is_local_mode
    mt5_server_input.visible = is_local_mode
    mt5_path_input.visible = is_local_mode
    mt5_flask_url_input.visible = not is_local_mode

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
    create_session_button = ft.ElevatedButton(text="Создать сессию Telegram", icon="telegram", bgcolor="#0088cc", color="white")
    
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
    
    # Лог создания сессии
    session_log = ft.Text("", size=12, color="#888888")
    
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
            
            if page:
                page.update()
    
    def on_create_telegram_session(e):
        """Инициирует создание новой Telegram сессии через LogicManager."""
        try:
            api_id = (api_id_input.value or "").strip()
            api_hash = (api_hash_input.value or "").strip()
            phone = (phone_input.value or "").strip()
            session_file = (session_file_input.value or "userbot.session").strip()

            if not api_id or not api_hash or not phone:
                session_log.value = "❌ Заполните API ID, API Hash и номер телефона!"
                session_log.color = "#f44336"
                session_log.update()
                return

            on_save_settings(None) # Сначала сохраняем настройки

            session_log.value = "🔐 Запуск создания Telegram сессии..."
            session_log.color = "#2196F3"
            session_log.update()

            if logic_manager and hasattr(logic_manager, 'start_telegram_authentication'):
                logic_manager.start_telegram_authentication(api_id, api_hash, phone, session_file)
                session_log.value = "✅ Процесс авторизации Telegram запущен."
                session_log.color = "#4CAF50"
            else:
                session_log.value = "❌ LogicManager или метод start_telegram_authentication недоступен."
                session_log.color = "#f44336"
            session_log.update()

        except Exception as e:
            session_log.value = f"❌ Ошибка при инициализации авторизации: {str(e)} "
            session_log.color = "#f44336"
            session_log.update()

    def on_save_settings(e):
        """Сохраняет настройки."""
        try:
            # Определяем режим MT5
            is_local_mode = mt5_mode_switch.value
            
            new_settings = {
                "telegram": {
                    "api_id": api_id_input.value,
                    "api_hash": api_hash_input.value,
                    "phone": phone_input.value,
                    "session_file": session_file_input.value
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
            
            # Добавляем настройки MT5 в зависимости от режима
            if is_local_mode:
                new_settings["mt5"] = {
                    "login": mt5_login_input.value,
                    "password": mt5_password_input.value,
                    "server": mt5_server_input.value,
                    "path": mt5_path_input.value
                }
            else:
                new_settings["mt5_server"] = {
                    "url": mt5_flask_url_input.value
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
                gpt_status.value = "GPT: ПОДКЛЮЧЕН"
                gpt_status.color = "#4CAF50"
            else:
                gpt_status.value = "GPT: ОШИБКА"
                gpt_status.color = "#f44336"
            gpt_status.update()
    
    def on_test_mt5(e):
        """Тестирует подключение к MT5."""
        if logic_manager:
            account_info = logic_manager.get_mt5_account_info()
            if account_info:
                mt5_status.value = "MT5: ПОДКЛЮЧЕН"
                mt5_status.color = "#4CAF50"
            else:
                mt5_status.value = "MT5: ОШИБКА"
                mt5_status.color = "#f44336"
            mt5_status.update()
    
    def on_start_bot(e):
        """Запускает бота."""
        if logic_manager:
            logic_manager.start_services()
            update_statuses()
    
    def on_stop_bot(e):
        """Останавливает бота."""
        if logic_manager:
            logic_manager.stop_services()
            update_statuses()
    
    def on_start_ai(e):
        """Запускает AI Trader."""
        # Реализация запуска AI Trader
        pass
    
    def on_stop_ai(e):
        """Останавливает AI Trader."""
        # Реализация остановки AI Trader
        pass
    
    # Привязываем обработчики событий
    save_button.on_click = on_save_settings
    test_gpt_button.on_click = on_test_gpt
    test_mt5_button.on_click = on_test_mt5
    create_session_button.on_click = on_create_telegram_session
    start_bot_button.on_click = on_start_bot
    stop_bot_button.on_click = on_stop_bot
    start_ai_button.on_click = on_start_ai
    stop_ai_button.on_click = on_stop_ai
    
    # Создаем интерфейс
    settings_view = ft.Container(
        bgcolor="#1a1a1a",
        padding=24,
        content=ft.Column([
            ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD, color="#ffffff"),
            ft.Container(height=24),
            
            # Секция MT5
            ft.Container(
                bgcolor="#2a2a2a",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("Настройки MetaTrader 5", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(height=16),
                    mt5_mode_switch,
                    ft.Container(height=12),
                    mt5_login_input,
                    mt5_password_input,
                    mt5_server_input,
                    mt5_path_input,
                    mt5_flask_url_input,
                ], spacing=12)
            ),
            
            ft.Container(height=16),
            
            # Кнопка удаления сессии Telegram
            delete_session_button,
            
            # Секция Telegram
            ft.Container(
                bgcolor="#2a2a2a",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("Настройки Telegram", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(height=16),
                    api_id_input,
                    api_hash_input,
                    phone_input,
                    session_file_input,
                    create_session_button,
                    session_log,
                ], spacing=12)
            ),
            
            ft.Container(height=16),
            
            # Секция GPT
            ft.Container(
                bgcolor="#2a2a2a",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("Настройки GPT", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(height=16),
                    gpt_key_input,
                    test_gpt_button,
                ], spacing=12)
            ),
            
            ft.Container(height=16),
            
            # Секция торговли
            ft.Container(
                bgcolor="#2a2a2a",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("Настройки торговли", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(height=16),
                    trading_lot_size,
                    trading_max_risk,
                    breakeven_enabled,
                    breakeven_pips,
                ], spacing=12)
            ),
            
            ft.Container(height=16),
            
            # Секция AI Trader
            ft.Container(
                bgcolor="#2a2a2a",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("AI Trader", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(height=16),
                    ai_trader_enabled,
                    ai_lot_size,
                    ai_live_trading,
                ], spacing=12)
            ),
            
            ft.Container(height=16),
            
            # Секция управления
            ft.Container(
                bgcolor="#2a2a2a",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("Управление", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(height=16),
                    ft.Row([save_button, test_mt5_button], spacing=12),
                    ft.Container(height=12),
                    ft.Row([start_bot_button, stop_bot_button], spacing=12),
                    ft.Container(height=12),
                    ft.Row([start_ai_button, stop_ai_button], spacing=12),
                ], spacing=12)
            ),
            
            ft.Container(height=16),
            
            # Секция статусов
            ft.Container(
                bgcolor="#2a2a2a",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("Статус сервисов", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(height=16),
                    telegram_status,
                    mt5_status,
                    gpt_status,
                    db_status,
                    ft.Container(height=12),
                    stats_text,
                ], spacing=12)
            ),
            
        ], spacing=0, scroll=ft.ScrollMode.AUTO)
    )
    
    # Обновляем статусы при создании
    update_statuses()

    # Инициализация модальных окон, чтобы они были привязаны к странице
    # Это должно быть в самом конце функции create_settings_view
    page.overlay.append(code_dialog)
    page.overlay.append(password_dialog)

    return settings_view # Return the main view content 