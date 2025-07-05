import flet as ft
from services.logic_manager import LogicManager

# ----- КОНСТАНТЫ -----
BLOCK_BG_COLOR = "#272a44"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a0a3b1"
SUCCESS_COLOR = "#4CAF50"
ERROR_COLOR = "#f44336"
WARNING_COLOR = "#ff9800"

def create_parser_bot_view(logic_manager: LogicManager):
    """Создает страницу Parser BOT."""
    
    # ----- СОСТОЯНИЕ -----
    parser_status_indicator = ft.Container(
        width=12,
        height=12,
        border_radius=6,
        bgcolor=ERROR_COLOR  # Красный - остановлен
    )
    parser_status_text = ft.Text("Остановлен", color=ERROR_COLOR, size=16, weight=ft.FontWeight.BOLD)
    channels_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
    logs_area = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=20,
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        text_size=12
    )
    
    # ----- ФУНКЦИИ ОБРАБОТКИ -----
    def update_status(status: str, color: str):
        parser_status_text.value = status
        parser_status_text.color = color
        parser_status_indicator.bgcolor = color
        parser_status_text.update()
        parser_status_indicator.update()
    
    def add_channel(e):
        channel_name = channel_input.value
        if channel_name:
            channel_card = ft.Container(
                bgcolor=BLOCK_BG_COLOR,
                border_radius=8,
                padding=16,
                content=ft.Column([
                    ft.Row([
                        ft.Text(channel_name, color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon="delete",
                            icon_color=ERROR_COLOR,
                            on_click=lambda e: remove_channel(channel_card)
                        )
                    ]),
                    ft.Row([
                        ft.Text("Стиль обработки:", color=SUBTEXT_COLOR, size=12),
                        ft.Dropdown(
                            width=120,
                            options=[
                                ft.dropdown.Option("Агрессивный"),
                                ft.dropdown.Option("Консервативный"),
                                ft.dropdown.Option("Умеренный")
                            ],
                            value="Умеренный",
                            border_color="transparent",
                            color=SUBTEXT_COLOR,
                            bgcolor=BLOCK_BG_COLOR
                        )
                    ]),
                    ft.Row([
                        ft.Text("ИИ обработка:", color=SUBTEXT_COLOR, size=12),
                        ft.Switch(value=True, active_color=SUCCESS_COLOR)
                    ])
                ], spacing=8)
            )
            channels_list.controls.append(channel_card)
            channels_list.update()
            channel_input.value = ""
            channel_input.update()
    
    def remove_channel(channel_card):
        channels_list.controls.remove(channel_card)
        channels_list.update()
    
    def start_parser(e):
        try:
            # logic_manager.start_parser_bot()
            update_status("Активен", SUCCESS_COLOR)
            add_log("● Parser BOT запущен")
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
    
    # ----- СТАТИСТИКА -----
    stats_container = ft.Container(
        bgcolor=BLOCK_BG_COLOR,
        border_radius=12,
        padding=20,
        content=ft.Column([
            ft.Text("Статистика Parser BOT", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(color=SUBTEXT_COLOR),
            ft.Row([
                ft.Column([
                    ft.Text("Обработано сигналов", color=SUBTEXT_COLOR, size=12),
                    ft.Text("1,247", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Успешных сделок", color=SUBTEXT_COLOR, size=12),
                    ft.Text("892", color=SUCCESS_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Отменено", color=SUBTEXT_COLOR, size=12),
                    ft.Text("355", color=ERROR_COLOR, size=18, weight=ft.FontWeight.BOLD)
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
                        ft.Row([
                            ft.Container(
                                content=channel_input,
                                expand=True
                            ),
                            ft.Container(width=10),
                            add_channel_button
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Container(height=16),
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