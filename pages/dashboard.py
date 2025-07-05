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
        expand=True,
        height=80, 
        bgcolor=BLOCK_BG_COLOR, 
        border_radius=12, 
        padding=16, 
        content=ft.Row([
            ft.Container(
                width=40, height=40, 
                bgcolor=color, 
                border_radius=20, 
                content=ft.Icon(icon, color=TEXT_COLOR, size=20), 
                alignment=ft.alignment.center
            ),
            ft.Column([
                ft.Text(label, color=SUBTEXT_COLOR, size=12),
                ft.Text(value, color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD),
            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=12)
    )
def _create_legend_item(color, text, value):
    return ft.Row([ft.Container(width=10, height=10, bgcolor=color, border_radius=3),ft.Text(text, color=SUBTEXT_COLOR, size=12),ft.Container(expand=True),ft.Text(str(value), color=TEXT_COLOR, size=12, weight=ft.FontWeight.BOLD),], spacing=8, height=20)
def _create_transaction_row(icon_color, title, subtitle, amount):
    return ft.Row([ft.Container(width=40, height=40, bgcolor=icon_color, border_radius=20, content=ft.Icon("keyboard_arrow_up", color=TEXT_COLOR, size=20), alignment=ft.alignment.center),ft.Column([ft.Text(title, color=TEXT_COLOR, size=13, weight=ft.FontWeight.BOLD), ft.Text(subtitle, color=SUBTEXT_COLOR, size=11)], spacing=2),ft.Container(expand=True),ft.Text(amount, color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD),], spacing=12, height=50, vertical_alignment=ft.CrossAxisAlignment.CENTER)

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

    return ft.Column(
        controls=[
            # Заголовок
            ft.Row([
                ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Container(expand=True),
            ]),
            ft.Container(height=24),
            ft.Row([
                ft.Container(
                    content=_create_stat_card("people_outline", "Общая прибыль", "$2,920", "#3676e0"),
                    expand=True
                ),
                ft.Container(width=22),
                ft.Container(
                    content=_create_stat_card("work_outline", "Макс. просадка", "-$450", "#fbc858"),
                    expand=True
                ),
                ft.Container(width=22),
                ft.Container(
                    content=_create_stat_card("request_quote", "Всего сделок", "128", "#ff6a6a"),
                    expand=True
                )
            ], spacing=0),
            ft.Container(height=24),
            ft.Row(
                [
                    ft.Container(
                        expand=True,
                        height=220, 
                        bgcolor=BLOCK_BG_COLOR, 
                        border_radius=12, 
                        padding=20, 
                        content=ft.Column([
                            ft.Text("Статус сервисов", color=TEXT_COLOR, size=14),
                            ft.Row([
                                ft.Container(content=donut_chart, width=150, height=150, alignment=ft.alignment.center),
                                ft.Column([
                                    _create_legend_item("#4CAF50", "MT5: Подключен", "●"), 
                                    _create_legend_item("#4CAF50", "PA: Активен", "●"),
                                    _create_legend_item("#f44336", "SM: Остановлен", "●")
                                ], spacing=8, expand=True, alignment=ft.MainAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
                        ], spacing=10)
                    ),
                    ft.Container(width=24),
                    ft.Container(
                        expand=True,
                        height=220, 
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left, 
                            end=ft.alignment.bottom_right, 
                            colors=["#3676e0", "#272a44"]
                        ), 
                        border_radius=12, 
                        padding=20, 
                        content=ft.Column([
                            ft.Text("Текущая сессия", color=SUBTEXT_COLOR, size=12),
                            ft.Text("24", color=TEXT_COLOR, size=24, weight=ft.FontWeight.BOLD),
                            ft.Container(content=ft.Text("Открытых сделок", color=SUBTEXT_COLOR, size=12), margin=ft.margin.only(top=10)),
                            ft.Text("12", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(content=ft.Text("Прибыльных", color=SUBTEXT_COLOR, size=12), margin=ft.margin.only(top=10)),
                            ft.Text("8", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
                        ], spacing=2)
                    ),
                ],
                spacing=0
            ),
            ft.Container(height=24),
            ft.Container(
                height=300,  # Фиксированная высота
                bgcolor=BLOCK_BG_COLOR, 
                border_radius=12, 
                padding=20, 
                content=ft.Column([
                    ft.Row([
                        ft.Text("Прибыль по дням", color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Container(
                            height=35, 
                            content=ft.Dropdown(
                                width=100, 
                                options=[ft.dropdown.Option("7 Days")], 
                                value="7 Days", 
                                border_color="transparent", 
                                color=SUBTEXT_COLOR, 
                                bgcolor=BLOCK_BG_COLOR, 
                                content_padding=ft.padding.only(left=10, right=5), 
                                text_size=12
                            )
                        )
                    ]),
                    ft.Container(
                        content=line_chart, 
                        expand=True,
                        height=200  # Фиксированная высота для графика
                    ),
                ], expand=True)
            ),
        ],
        spacing=0
    )

 