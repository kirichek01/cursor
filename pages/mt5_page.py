import flet as ft

# ----- КОНСТАНТЫ -----
BLOCK_BG_COLOR = "#272a44"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a0a3b1"
SUCCESS_COLOR = "#4CAF50"
ERROR_COLOR = "#f44336"
WARNING_COLOR = "#ff9800"

def create_mt5_view():
    """Создает страницу MT5 Connection."""
    
    # ----- СОСТОЯНИЕ -----
    connection_status = ft.Text("Отключен", color=ERROR_COLOR, size=16, weight=ft.FontWeight.BOLD)
    balance_text = ft.Text("$0.00", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    equity_text = ft.Text("$0.00", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    margin_text = ft.Text("$0.00", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    
    # ----- ФУНКЦИИ ОБРАБОТКИ -----
    def update_connection_status(status: str, color: str):
        connection_status.value = status
        connection_status.color = color
        connection_status.update()
    
    def connect_mt5(e):
        try:
            # Проверяем заполнение полей
            if not login_input.value or not password_input.value or not server_input.value:
                add_log("❌ Заполните все поля подключения")
                return
            
            update_connection_status("Подключен", SUCCESS_COLOR)
            add_log("✅ Подключение к MT5 установлено")
            
            # Обновляем баланс (демо данные)
            balance_text.value = "$10,000.00"
            equity_text.value = "$10,245.50"
            margin_text.value = "$1,200.00"
            balance_text.update()
            equity_text.update()
            margin_text.update()
            
        except Exception as ex:
            add_log(f"❌ Ошибка подключения: {ex}")
    
    def disconnect_mt5(e):
        try:
            update_connection_status("Отключен", ERROR_COLOR)
            add_log("🛑 Отключение от MT5")
            
            # Сбрасываем баланс
            balance_text.value = "$0.00"
            equity_text.value = "$0.00"
            margin_text.value = "$0.00"
            balance_text.update()
            equity_text.update()
            margin_text.update()
            
        except Exception as ex:
            add_log(f"❌ Ошибка отключения: {ex}")
    
    def add_log(message: str):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        current_logs = logs_area.value or ""
        logs_area.value = f"[{timestamp}] {message}\n{current_logs}"
        logs_area.update()
    
    def test_connection(e):
        add_log("🔍 Тестирование подключения к MT5...")
        # Здесь будет логика тестирования
    
    def load_history(e):
        add_log("📊 Загрузка истории сделок...")
        # Здесь будет логика загрузки истории
    
    # ----- ЭЛЕМЕНТЫ ИНТЕРФЕЙСА -----
    login_input = ft.TextField(
        label="Логин",
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        width=200
    )
    
    password_input = ft.TextField(
        label="Пароль",
        password=True,
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        width=200
    )
    
    server_input = ft.TextField(
        label="Сервер",
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        width=200
    )
    
    path_input = ft.TextField(
        label="Путь к MT5",
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        width=300
    )
    
    connect_button = ft.ElevatedButton(
        "Подключиться",
        bgcolor=SUCCESS_COLOR,
        color="white",
        on_click=connect_mt5
    )
    
    disconnect_button = ft.ElevatedButton(
        "Отключиться",
        bgcolor=ERROR_COLOR,
        color="white",
        on_click=disconnect_mt5
    )
    
    test_button = ft.ElevatedButton(
        "Тест подключения",
        bgcolor=WARNING_COLOR,
        color="white",
        on_click=test_connection
    )
    
    history_button = ft.ElevatedButton(
        "Загрузить историю",
        bgcolor=WARNING_COLOR,
        color="white",
        on_click=load_history
    )
    
    logs_area = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=8,
        max_lines=15,
        border_color="transparent",
        bgcolor=BLOCK_BG_COLOR,
        color=TEXT_COLOR,
        text_size=12
    )
    
    # ----- ФОРМА ПОДКЛЮЧЕНИЯ -----
    connection_form = ft.Container(
        bgcolor=BLOCK_BG_COLOR,
        border_radius=12,
        padding=20,
        content=ft.Column([
            ft.Text("Подключение к MT5", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(color=SUBTEXT_COLOR),
            
            ft.Row([
                ft.Column([
                    login_input,
                    ft.Container(height=10),
                    password_input
                ], expand=True),
                ft.Container(width=20),
                ft.Column([
                    server_input,
                    ft.Container(height=10),
                    path_input
                ], expand=True)
            ]),
            
            ft.Container(height=20),
            
            ft.Row([
                connect_button,
                ft.Container(width=10),
                disconnect_button,
                ft.Container(width=20),
                test_button,
                ft.Container(width=10),
                history_button
            ])
        ], spacing=10)
    )
    
    # ----- СТАТУС ПОДКЛЮЧЕНИЯ -----
    status_container = ft.Container(
        bgcolor=BLOCK_BG_COLOR,
        border_radius=12,
        padding=20,
        content=ft.Column([
            ft.Text("Статус подключения", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(color=SUBTEXT_COLOR),
            
            ft.Row([
                ft.Text("Статус:", color=SUBTEXT_COLOR, size=14),
                connection_status
            ]),
            
            ft.Container(height=20),
            
            ft.Row([
                ft.Column([
                    ft.Text("Баланс", color=SUBTEXT_COLOR, size=12),
                    balance_text
                ], expand=True),
                ft.Column([
                    ft.Text("Собственный капитал", color=SUBTEXT_COLOR, size=12),
                    equity_text
                ], expand=True),
                ft.Column([
                    ft.Text("Маржа", color=SUBTEXT_COLOR, size=12),
                    margin_text
                ], expand=True)
            ], spacing=20)
        ], spacing=10)
    )
    
    # ----- СИМВОЛЫ -----
    symbols_container = ft.Container(
        bgcolor=BLOCK_BG_COLOR,
        border_radius=12,
        padding=20,
        content=ft.Column([
            ft.Text("Доступные символы", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(color=SUBTEXT_COLOR),
            
            ft.Row([
                ft.Text("EURUSD", color=TEXT_COLOR, size=14),
                ft.Container(expand=True),
                ft.Text("1.0850", color=SUBTEXT_COLOR, size=12),
                ft.Container(width=20),
                ft.Text("+0.12%", color=SUCCESS_COLOR, size=12)
            ]),
            
            ft.Row([
                ft.Text("GBPUSD", color=TEXT_COLOR, size=14),
                ft.Container(expand=True),
                ft.Text("1.2650", color=SUBTEXT_COLOR, size=12),
                ft.Container(width=20),
                ft.Text("-0.08%", color=ERROR_COLOR, size=12)
            ]),
            
            ft.Row([
                ft.Text("XAUUSD", color=TEXT_COLOR, size=14),
                ft.Container(expand=True),
                ft.Text("2050.00", color=SUBTEXT_COLOR, size=12),
                ft.Container(width=20),
                ft.Text("+0.25%", color=SUCCESS_COLOR, size=12)
            ]),
            
            ft.Row([
                ft.Text("USDJPY", color=TEXT_COLOR, size=14),
                ft.Container(expand=True),
                ft.Text("148.50", color=SUBTEXT_COLOR, size=12),
                ft.Container(width=20),
                ft.Text("+0.05%", color=SUCCESS_COLOR, size=12)
            ])
        ], spacing=10)
    )
    
    # ----- ОСНОВНОЙ КОНТЕНТ -----
    content = ft.Column([
        # Заголовок
        ft.Text("MT5 Connection", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(height=24),
        
        # Основные секции
        ft.Row([
            # Левая колонка - форма подключения и статус
            ft.Column([
                connection_form,
                ft.Container(height=20),
                status_container
            ], expand=True),
            
            ft.Container(width=20),
            
            # Правая колонка - символы и логи
            ft.Column([
                symbols_container,
                ft.Container(height=20),
                ft.Container(
                    expand=True,
                    bgcolor=BLOCK_BG_COLOR,
                    border_radius=12,
                    padding=20,
                    content=ft.Column([
                        ft.Text("Логи MT5", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(color=SUBTEXT_COLOR),
                        logs_area
                    ], spacing=10)
                )
            ], expand=True)
        ], spacing=0)
    ], spacing=0)
    
    return content 