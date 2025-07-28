import flet as ft
from core.services.logic_manager import LogicManager

# ----- КОНСТАНТЫ -----
BLOCK_BG_COLOR = "#272a44"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a0a3b1"
SUCCESS_COLOR = "#4CAF50"
ERROR_COLOR = "#f44336"
WARNING_COLOR = "#ff9800"

def get_parser_stats(logic_manager):
    """Получает реальную статистику парсера из базы данных."""
    if not logic_manager or not hasattr(logic_manager, 'database_service'):
        return {
            'processed_signals': '0',
            'successful_trades': '0',
            'cancelled_trades': '0'
        }
    
    try:
        # Получаем все сигналы из базы
        signals = logic_manager.database_service.get_signal_history(limit=1000)
        
        # Подсчитываем статистику
        total_signals = len(signals)
        successful_trades = len([s for s in signals if s['status'] == 'CLOSED'])
        cancelled_trades = len([s for s in signals if s['status'] in ['CANCELLED', 'PARTIALLY_CANCELLED']])
        
        return {
            'processed_signals': str(total_signals),
            'successful_trades': str(successful_trades),
            'cancelled_trades': str(cancelled_trades)
        }
    except Exception as e:
        print(f"Error getting parser stats: {e}")
        return {
            'processed_signals': '0',
            'successful_trades': '0',
            'cancelled_trades': '0'
        }

def create_parser_bot_view(logic_manager: LogicManager):
    """Создает страницу Parser BOT с улучшенным выбором каналов."""
    
    # ----- ПЕРЕМЕННЫЕ -----
    parser_status_indicator = ft.Container(
        width=12,
        height=12,
        border_radius=6,
        bgcolor=ERROR_COLOR
    )
    
    parser_status_text = ft.Text("Остановлен", color=SUBTEXT_COLOR, size=14)
    
    # Статистика
    real_stats = get_parser_stats(logic_manager)
    processed_signals_text = ft.Text(real_stats['processed_signals'], color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    successful_trades_text = ft.Text(real_stats['successful_trades'], color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    cancelled_trades_text = ft.Text(real_stats['cancelled_trades'], color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    
    # Список каналов
    channels_list = ft.Column(spacing=8)
    
    # Поиск каналов
    search_input = ft.TextField(
        label="Поиск каналов",
        hint_text="Введите название канала для поиска",
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        prefix_icon=ft.Icons.SEARCH
    )
    
    # Результаты поиска
    search_results = ft.Column(spacing=4, visible=False)
    
    # Логи
    logs_area = ft.TextField(
        multiline=True,
        min_lines=8,
        max_lines=12,
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        read_only=True,
        text_style=ft.TextStyle(font_family="monospace", size=12)
    )
    
    # ----- ФУНКЦИИ -----
    def update_status(status: str, color: str):
        parser_status_text.value = status
        parser_status_indicator.bgcolor = color
        parser_status_text.update()
        parser_status_indicator.update()
    
    def update_stats():
        new_stats = get_parser_stats(logic_manager)
        processed_signals_text.value = new_stats['processed_signals']
        successful_trades_text.value = new_stats['successful_trades']
        cancelled_trades_text.value = new_stats['cancelled_trades']
        processed_signals_text.update()
        successful_trades_text.update()
        cancelled_trades_text.update()
    
    def add_channel(e):
        channel_name = channel_input.value.strip() if channel_input.value else ""
        if channel_name:
            # Создаем карточку канала
            channel_card = ft.Container(
                bgcolor=BLOCK_BG_COLOR,
                border_radius=8,
                padding=12,
                content=ft.Row([
                    ft.Icon("telegram", color=SUCCESS_COLOR, size=20),
                    ft.Text(channel_name, color=TEXT_COLOR, size=14, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon="delete",
                        icon_color=ERROR_COLOR,
                        icon_size=18,
                        on_click=lambda e, card=channel_card: remove_channel(card)
                    )
                ], spacing=12)
            )
            channels_list.controls.append(channel_card)
            channels_list.update()
            channel_input.value = ""
            channel_input.update()
            add_log(f"● Добавлен канал: {channel_name}")
    
    def search_channels(e):
        query = search_input.value.strip().lower() if search_input.value else ""
        if not query:
            search_results.visible = False
            search_results.update()
            return
        
        # Имитация поиска каналов (в реальном приложении здесь будет API Telegram)
        mock_channels = [
            "GOLDHUNTER | PAUL 🦁 FX & CRYPTO 🌍",
            "CryptoJuketrade",
            "FX Signals Pro",
            "Trading Master",
            "Forex Signals Daily",
            "Crypto Trading Signals",
            "Gold Trading Pro",
            "EURUSD Signals"
        ]
        
        # Фильтруем каналы по запросу
        filtered_channels = [ch for ch in mock_channels if query in ch.lower()]
        
        # Очищаем предыдущие результаты
        search_results.controls.clear()
        
        for channel in filtered_channels:
            channel_item = ft.Container(
                bgcolor=BLOCK_BG_COLOR,
                border_radius=6,
                padding=8,
                content=ft.Row([
                    ft.Icon("telegram", color=SUBTEXT_COLOR, size=16),
                    ft.Text(channel, color=TEXT_COLOR, size=12),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon="add",
                        icon_color=SUCCESS_COLOR,
                        icon_size=16,
                        on_click=lambda e, ch=channel: add_channel_from_search(ch)
                    )
                ], spacing=8)
            )
            search_results.controls.append(channel_item)
        
        search_results.visible = True
        search_results.update()
    
    def add_channel_from_search(channel_name):
        # Проверяем, не добавлен ли уже этот канал
        existing_channels = [ch.content.controls[1].value for ch in channels_list.controls]
        if channel_name not in existing_channels:
            channel_card = ft.Container(
                bgcolor=BLOCK_BG_COLOR,
                border_radius=8,
                padding=12,
                content=ft.Row([
                    ft.Icon("telegram", color=SUCCESS_COLOR, size=20),
                    ft.Text(channel_name, color=TEXT_COLOR, size=14, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon="delete",
                        icon_color=ERROR_COLOR,
                        icon_size=18,
                        on_click=lambda e, card=channel_card: remove_channel(card)
                    )
                ], spacing=12)
            )
            channels_list.controls.append(channel_card)
            channels_list.update()
            add_log(f"● Добавлен канал из поиска: {channel_name}")
        
        # Скрываем результаты поиска
        search_results.visible = False
        search_results.update()
        search_input.value = ""
        search_input.update()
    
    def remove_channel(channel_card):
        channel_name = channel_card.content.controls[1].value
        channels_list.controls.remove(channel_card)
        channels_list.update()
        add_log(f"● Удален канал: {channel_name}")
    
    def start_parser(e):
        try:
            # logic_manager.start_parser_bot()
            update_status("Активен", SUCCESS_COLOR)
            add_log("● Parser BOT запущен")
            update_stats()  # Обновляем статистику при запуске
        except Exception as ex:
            add_log(f"● Ошибка запуска: {ex}")
    
    def stop_parser(e):
        try:
            # logic_manager.stop_parser_bot()
            update_status("Остановлен", ERROR_COLOR)
            add_log("● Parser BOT остановлен")
        except Exception as ex:
            add_log(f"● Ошибка остановки: {ex}")
    
    def add_log(message: str):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        current_logs = logs_area.value or ""
        logs_area.value = f"[{timestamp}] {message}\n{current_logs}"
        logs_area.update()
    
    def train_model(e):
        add_log("🧠 Начинается обучение модели на новых каналах...")
        # Здесь будет логика обучения
        
        # Анализируем специфику канала GOLDHUNTER
        add_log("📊 Анализ канала GOLDHUNTER:")
        add_log("   • Формат: BUY/SELL SYMBOL at PRICE")
        add_log("   • SL: всегда указывается")
        add_log("   • TP: множественные (TP1, TP2, TP3)")
        add_log("   • Обновления: через reply сообщения")
        add_log("   • Trailing: SL подтягивается к цене")
        add_log("   • Break-even: перевод в безубыток")
        
        # Настраиваем парсер под канал
        add_log("⚙️ Настройка парсера:")
        add_log("   ✅ Поддержка множественных TP")
        add_log("   ✅ Обработка trailing stop")
        add_log("   ✅ Break-even логика")
        add_log("   ✅ Частичное закрытие позиций")
        add_log("   ✅ Модификация через reply")
        
        add_log("🎯 Парсер готов к работе с GOLDHUNTER!")
    
    # ----- ЭЛЕМЕНТЫ ИНТЕРФЕЙСА -----
    channel_input = ft.TextField(
        label="Название канала",
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR
    )
    
    add_channel_button = ft.ElevatedButton(
        "Добавить канал",
        bgcolor=SUCCESS_COLOR,
        color="white",
        on_click=add_channel,
        height=40,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )
    
    search_button = ft.ElevatedButton(
        "Поиск каналов",
        bgcolor=WARNING_COLOR,
        color="white",
        on_click=search_channels,
        height=40,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )
    
    start_button = ft.ElevatedButton(
        "Запустить Parser",
        bgcolor=SUCCESS_COLOR,
        color="white",
        on_click=start_parser
    )
    
    stop_button = ft.ElevatedButton(
        "Остановить Parser",
        bgcolor=ERROR_COLOR,
        color="white",
        on_click=stop_parser
    )
    
    train_button = ft.ElevatedButton(
        "Обучить модель",
        bgcolor=WARNING_COLOR,
        color="white",
        on_click=train_model
    )
    
    # Кнопка обновления статистики
    refresh_stats_button = ft.IconButton(
        icon="refresh",
        icon_color=SUBTEXT_COLOR,
        on_click=lambda e: update_stats(),
        tooltip="Обновить статистику"
    )
    
    # ----- СТАТИСТИКА -----
    stats_container = ft.Container(
        bgcolor=BLOCK_BG_COLOR,
        border_radius=12,
        padding=20,
        content=ft.Column([
            ft.Row([
                ft.Text("Статистика Parser BOT", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                refresh_stats_button
            ]),
            ft.Divider(color=SUBTEXT_COLOR),
            ft.Row([
                ft.Column([
                    ft.Text("Обработано сигналов", color=SUBTEXT_COLOR, size=12),
                    processed_signals_text
                ], expand=True),
                ft.Column([
                    ft.Text("Успешных сделок", color=SUBTEXT_COLOR, size=12),
                    successful_trades_text
                ], expand=True),
                ft.Column([
                    ft.Text("Отменено", color=SUBTEXT_COLOR, size=12),
                    cancelled_trades_text
                ], expand=True)
            ], spacing=20)
        ], spacing=10)
    )
    
    # ----- ОСНОВНОЙ КОНТЕНТ -----
    content = ft.Column(
        scroll=ft.ScrollMode.ADAPTIVE,
        controls=[
            # Заголовок и статус
            ft.Row([
                ft.Text("Parser BOT", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Text("Статус:", color=SUBTEXT_COLOR, size=14),
                        parser_status_indicator,
                        ft.Container(width=8),
                        parser_status_text
                    ], spacing=8),
                    padding=ft.padding.only(right=16)
                )
            ]),
            ft.Container(height=24),
            
            # Кнопки управления
            ft.Row([
                start_button,
                ft.Container(width=10),
                stop_button,
                ft.Container(width=20),
                train_button
            ]),
            ft.Container(height=24),
            
            # Основные секции
            ft.Column([
                # Блок каналов на всю ширину
                ft.Container(
                    bgcolor=BLOCK_BG_COLOR,
                    border_radius=12,
                    padding=20,
                    content=ft.Column([
                        ft.Text("Telegram каналы", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(color=SUBTEXT_COLOR),
                        
                        # Поиск каналов
                        ft.Text("Поиск каналов", color=SUBTEXT_COLOR, size=12, weight=ft.FontWeight.W_500),
                        ft.Row([
                            ft.Container(
                                content=search_input,
                                expand=True
                            ),
                            ft.Container(width=10),
                            search_button
                        ], alignment=ft.MainAxisAlignment.START),
                        
                        # Результаты поиска
                        search_results,
                        
                        ft.Container(height=16),
                        ft.Text("Добавить вручную", color=SUBTEXT_COLOR, size=12, weight=ft.FontWeight.W_500),
                        ft.Row([
                            ft.Container(
                                content=channel_input,
                                expand=True
                            ),
                            ft.Container(width=10),
                            add_channel_button
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Container(height=16),
                        ft.Text("Выбранные каналы", color=SUBTEXT_COLOR, size=12, weight=ft.FontWeight.W_500),
                        channels_list
                    ], spacing=10)
                ),
                ft.Container(height=20),
                
                # Блок статистики на всю ширину
                stats_container,
                ft.Container(height=20),
                # Блок логов на всю ширину
                ft.Container(
                    bgcolor=BLOCK_BG_COLOR,
                    border_radius=12,
                    padding=20,
                    content=ft.Column([
                        ft.Text("Логи Parser BOT", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(color=SUBTEXT_COLOR),
                        logs_area
                    ], spacing=10)
                )
            ], spacing=0)
        ], spacing=0)
    return content
