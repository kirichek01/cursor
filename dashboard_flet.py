import flet as ft
from components.charts import generate_donut_chart, generate_line_chart
from pages.smartmoney_page import app_state

# ----- КОНСТАНТЫ -----
BLOCK_BG_COLOR = "#272a44"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a0a3b1"
GRADIENT_START = "#ff6f6f"
GRADIENT_END = "#a259ff"

# ----- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ -----
def _create_stat_card(icon, label, value, color):
    return ft.Container(
        width=180, height=80, 
        bgcolor=BLOCK_BG_COLOR, 
        border_radius=12, 
        padding=16, 
        content=ft.Column([
            ft.Text(label, color=SUBTEXT_COLOR, size=12),
            ft.Text(value, color=color, size=18, weight=ft.FontWeight.BOLD),
        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER)
    )

def _create_legend_item(color, text, value):
    return ft.Row([
        ft.Container(width=10, height=10, bgcolor=color, border_radius=3),
        ft.Text(text, color=SUBTEXT_COLOR, size=12),
        ft.Container(expand=True),
        ft.Text(str(value), color=TEXT_COLOR, size=12, weight=ft.FontWeight.BOLD),
    ], spacing=8, height=20)

def _create_transaction_row(icon_color, title, subtitle, amount):
    return ft.Row([
        ft.Container(
            width=40, height=40, 
            bgcolor=icon_color, 
            border_radius=20, 
            content=ft.Icon("keyboard_arrow_up", color=TEXT_COLOR, size=20), 
            alignment=ft.alignment.center
        ),
        ft.Column([
            ft.Text(title, color=TEXT_COLOR, size=13, weight=ft.FontWeight.BOLD), 
            ft.Text(subtitle, color=SUBTEXT_COLOR, size=11)
        ], spacing=2),
        ft.Container(expand=True),
        ft.Text(amount, color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD),
    ], spacing=12, height=50, vertical_alignment=ft.CrossAxisAlignment.CENTER)

def create_dashboard_view(page):
    """
    Создает и возвращает только центральную часть Dashboard (без правой панели).
    Правая панель теперь создается в main.py.
    """
    # Создаем графики с обработкой ошибок
    try:
        donut_chart = generate_donut_chart()
    except Exception as e:
        print(f"Ошибка создания donut chart: {e}")
        donut_chart = ft.Container(
            width=150, height=150, 
            bgcolor=BLOCK_BG_COLOR, 
            border_radius=75,
            content=ft.Text("Chart Error", color=TEXT_COLOR, size=12),
            alignment=ft.alignment.center
        )
    
    try:
        line_chart = generate_line_chart()
    except Exception as e:
        print(f"Ошибка создания line chart: {e}")
        line_chart = ft.Container(
            height=200, 
            bgcolor=BLOCK_BG_COLOR, 
            border_radius=8,
            content=ft.Text("Chart Error", color=TEXT_COLOR, size=12),
            alignment=ft.alignment.center
        )

    # Кнопки управления ботом
    start_bot_button = ft.ElevatedButton(
        text="Запустить бота", 
        icon="play_arrow", 
        bgcolor="#4CAF50",
        color="white"
    )
    stop_bot_button = ft.ElevatedButton(
        text="Остановить бота", 
        icon="stop", 
        bgcolor="#f44336",
        color="white"
    )
    
    # Статус бота
    bot_status_text = ft.Text("Бот: ОСТАНОВЛЕН", color="#ff6a6a", size=14, weight=ft.FontWeight.BOLD)
    
    def update_bot_status():
        """Обновляет статус бота."""
        if hasattr(page, 'main_app') and page.main_app.logic_manager:
            status = page.main_app.logic_manager.get_bot_status()
            if status['bot_running']:
                bot_status_text.value = "Бот: ЗАПУЩЕН"
                bot_status_text.color = "#4CAF50"
                start_bot_button.disabled = True
                stop_bot_button.disabled = False
            else:
                bot_status_text.value = "Бот: ОСТАНОВЛЕН"
                bot_status_text.color = "#ff6a6a"
                start_bot_button.disabled = False
                stop_bot_button.disabled = True
            
            # Обновляем статистику
            stats = status.get('stats', {})
            total_signals = stats.get('total_signals', 0)
            successful_trades = stats.get('successful_trades', 0)
            total_profit = stats.get('total_profit', 0.0)
            
            # Обновляем карточки статистики
            if hasattr(page, 'main_app') and page.main_app.pages:
                # Обновляем значения в карточках
                pass  # Здесь можно добавить обновление карточек
    
    def on_start_bot(e):
        """Запускает бота."""
        if hasattr(page, 'main_app') and page.main_app.logic_manager:
            page.main_app.logic_manager.start_bot()
            update_bot_status()
            print("✅ Bot started successfully!")
        else:
            print("❌ LogicManager not available")
    
    def on_stop_bot(e):
        """Останавливает бота."""
        if hasattr(page, 'main_app') and page.main_app.logic_manager:
            page.main_app.logic_manager.stop_bot()
            update_bot_status()
            print("🛑 Bot stopped successfully!")
        else:
            print("❌ LogicManager not available")
    
    # Привязываем обработчики
    start_bot_button.on_click = on_start_bot
    stop_bot_button.on_click = on_stop_bot

    return ft.Column(
        controls=[
            # Верхняя панель (Overview, поиск, профиль) - как в оригинале
            ft.Row([
                ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Container(expand=True),
                # Поиск как в оригинале
                ft.Container(
                    content=ft.TextField(
                        hint_text="Search 'waste in'",
                        width=260,
                        border_color="#35365c",
                        bgcolor="#23243A",
                        color="#bfc9da",
                        border_radius=12,
                        content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    ),
                    padding=ft.padding.only(right=16)
                ),
                # Профиль справа как в оригинале
                ft.Container(
                    content=ft.Row([
                        ft.Text("Ceptari Tyas", size=15, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                        ft.Container(width=8),
                        ft.Container(
                            width=36, height=36, bgcolor="#3a3b5a", border_radius=18,
                            content=ft.Icon(name="person", color="#fff", size=20),
                            alignment=ft.alignment.center,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="#23243A",
                    border_radius=16,
                    padding=ft.padding.symmetric(horizontal=18, vertical=8),
                )
            ]),
            ft.Container(height=24),
            
            # Управление ботом
            ft.Row([
                bot_status_text,
                ft.Container(expand=True),
                start_bot_button,
                ft.Container(width=10),
                stop_bot_button,
            ]),
            ft.Container(height=24),
            
            # Карточки Overview (как в оригинале - 3 карточки без иконок)
            ft.Row([
                _create_stat_card(None, "Customer", "1,300", "#a259ff"),
                _create_stat_card(None, "Employees", "42", "#fbc858"),
                _create_stat_card(None, "Request", "128", "#ff6a6a"),
            ], spacing=22),
            ft.Container(height=24),
            ft.Row(
                [
                    ft.Container(
                        width=340, height=220, 
                        bgcolor=BLOCK_BG_COLOR, 
                        border_radius=12, 
                        padding=20, 
                        content=ft.Column([
                            ft.Text("Customer based region", color=TEXT_COLOR, size=14),
                            ft.Row([
                                ft.Container(content=donut_chart, width=150, height=150, alignment=ft.alignment.center),
                                ft.Column([
                                    _create_legend_item("#ff6a6a", "Bojongsoang", 854), 
                                    _create_legend_item("#a259ff", "Baleendah", 650)
                                ], spacing=8, expand=True, alignment=ft.MainAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
                        ], spacing=10)
                    ),
                    ft.Container(width=24),
                    ft.Container(
                        width=220, height=220, 
                        bgcolor=BLOCK_BG_COLOR, 
                        border_radius=12, 
                        padding=20, 
                        content=ft.Column([
                            ft.Text("Total category waste", color=SUBTEXT_COLOR, size=12),
                            ft.Text("20", color=TEXT_COLOR, size=24, weight=ft.FontWeight.BOLD),
                            ft.Container(content=ft.Text("Total waste in", color=SUBTEXT_COLOR, size=12), margin=ft.margin.only(top=10)),
                            ft.Text("564 kg", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(content=ft.Text("Total waste out", color=SUBTEXT_COLOR, size=12), margin=ft.margin.only(top=10)),
                            ft.Text("1205 kg", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
                        ], spacing=2)
                    ),
                ],
                spacing=0
            ),
            ft.Container(height=24),
            ft.Row([
                ft.Container(
                    width=540, height=220, 
                    bgcolor=BLOCK_BG_COLOR, 
                    border_radius=12, 
                    padding=20, 
                    content=ft.Column([
                        ft.Text("Waste In & Out", color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(content=line_chart, expand=True),
                    ])
                ),
                ft.Container(width=24),
                ft.Container(
                    width=320, height=220, 
                    bgcolor=BLOCK_BG_COLOR, 
                    border_radius=12, 
                    padding=20, 
                    content=ft.Column([
                        ft.Text("Last Transaction", color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        *[
                            ft.Text(f"Deposit Waste   ${291+i*50}", color="#bfc9da", size=14)
                            for i in range(5)
                        ]
                    ])
                ),
            ], spacing=0),
        ],
        spacing=0
    )

def _start_bot(page):
    """Запускает бота."""
    try:
        # Получаем LogicManager из main app
        if hasattr(page, 'main_app') and page.main_app.logic_manager:
            page.main_app.logic_manager.start_bot()
            print("✅ Bot started successfully!")
        else:
            print("❌ LogicManager not available")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

def _stop_bot(page):
    """Останавливает бота."""
    try:
        # Получаем LogicManager из main app
        if hasattr(page, 'main_app') and page.main_app.logic_manager:
            page.main_app.logic_manager.stop_bot()
            print("🛑 Bot stopped successfully!")
        else:
            print("❌ LogicManager not available")
    except Exception as e:
        print(f"❌ Error stopping bot: {e}")

def create_sidebar(active_page="Dashboard"):
    # Меню согласно оригинальному макету
    return ft.Container(
        width=220,
        height=800,  # фиксированная высота
        bgcolor="#1a1b35",  # темнее
        border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
        padding=ft.padding.only(left=24, right=24, top=0, bottom=0),  # убираем верхний padding
        content=ft.Column([
            ft.Text("CombineTradeBot", size=22, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=18),
            ft.Column([
                ft.Container(
                    content=ft.Text("Dashboard", color="white", size=16, weight=ft.FontWeight.BOLD),
                    bgcolor="#3a3b5a",
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                ),
                ft.Container(
                    content=ft.Text("Settings", color="#bfc9da", size=15),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                ),
                ft.Container(
                    content=ft.Text("History", color="#bfc9da", size=15),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                ),
            ], spacing=0),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Text("by Kirichek", color="#bfc9da", size=13),
                bgcolor="#1a1b35",  # темнее
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
            )
        ], spacing=0)
    )

def create_right_panel():
    # Правая панель с реальным контентом (фиксированная ширина)
    return ft.Container(
        width=260,
        height=800,
        bgcolor="#1a1b35",  # темнее
        border_radius=ft.border_radius.only(top_right=20, bottom_right=20),
        padding=ft.padding.only(top=24, bottom=24, right=16),  # убрал left padding
        content=ft.Column([
            ft.Container(
                width=220, height=140,  # уменьшил ширину и высоту карточки
                border_radius=16, 
                padding=16, 
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left, 
                    end=ft.alignment.bottom_right, 
                    colors=[GRADIENT_START, GRADIENT_END]
                ), 
                content=ft.Column([
                    ft.Text("ID 122 887 552", color=TEXT_COLOR, size=12),
                    ft.Container(height=12),
                    ft.Text("Your Income", color=TEXT_COLOR, size=14),
                    ft.Text("$2,920", color=TEXT_COLOR, size=26, weight=ft.FontWeight.BOLD)
                ], spacing=2)
            ),
            ft.Container(height=18),
            ft.Container(
                width=220,  # уменьшил ширину блока транзакций
                expand=True, 
                bgcolor=BLOCK_BG_COLOR, 
                border_radius=16, 
                padding=16, 
                content=ft.Column([
                    ft.Row([
                        ft.Text("Last Transaction", color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Text("See All", color=SUBTEXT_COLOR, size=12)
                    ]),
                    ft.Container(height=10),
                    ft.Column([
                        _create_transaction_row("#3676e0", "BUY EURUSD", "2024-01-15", "$1.0850"),
                        _create_transaction_row("#e03636", "SELL GBPUSD", "2024-01-15", "$1.2650"),
                        _create_transaction_row("#3676e0", "BUY XAUUSD", "2024-01-15", "$2050.00"),
                        _create_transaction_row("#e03636", "SELL USDJPY", "2024-01-15", "$148.50"),
                        _create_transaction_row("#3676e0", "BUY AUDUSD", "2024-01-15", "$0.6750"),
                    ], spacing=15)
                ], spacing=15)
            )
        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)  # выравнивание по центру
    )

def main(page: ft.Page):
    # Фиксированные размеры приложения
    page.title = "Combine Trade Bot by Kirichek"
    page.bgcolor = "#23243A"
    page.padding = 0
    page.spacing = 0

    # Создаем основной layout
    main_layout = ft.Row([
        create_sidebar(),
        ft.Container(
            expand=True,
            content=create_dashboard_view(page)
        ),
        create_right_panel()
    ], spacing=0)

    page.add(main_layout)

if __name__ == "__main__":
    ft.app(target=main) 