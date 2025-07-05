import flet as ft

# ----- КОНСТАНТЫ -----
BLOCK_BG_COLOR = "#272a44"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a0a3b1"
SUCCESS_COLOR = "#4CAF50"
ERROR_COLOR = "#f44336"
WARNING_COLOR = "#ff9800"

def create_history_view(page):
    """Создает страницу History с полной таблицей сделок."""
    
    # ----- ФИЛЬТРЫ -----
    def filter_trades(e):
        # Здесь будет логика фильтрации
        pass
    
    # ----- ДЕТАЛЬНАЯ ТАБЛИЦА СДЕЛОК -----
    trades_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Инструмент", color=TEXT_COLOR, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Направление", color=TEXT_COLOR, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Прибыль", color=TEXT_COLOR, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Комиссия", color=TEXT_COLOR, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Результат", color=TEXT_COLOR, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Статус", color=TEXT_COLOR, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Действия", color=TEXT_COLOR, weight=ft.FontWeight.BOLD)),
        ],
        rows=[
            # Parser BOT сделки
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("EURUSD", color=TEXT_COLOR)),
                ft.DataCell(ft.Text("BUY", color=SUCCESS_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("+$45.20", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Text("-$2.50", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("+$42.70", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Text("Закрыта", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Container(
                    content=ft.ElevatedButton("Лог", bgcolor=WARNING_COLOR, color="white"),
                    padding=ft.padding.only(left=8)
                ))
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("XAUUSD", color=TEXT_COLOR)),
                ft.DataCell(ft.Text("SELL", color=ERROR_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("-$12.80", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("-$1.20", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("-$14.00", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("Закрыта", color=ERROR_COLOR)),
                ft.DataCell(ft.Container(
                    content=ft.ElevatedButton("Лог", bgcolor=WARNING_COLOR, color="white"),
                    padding=ft.padding.only(left=8)
                ))
            ]),
            
            # Smart Money BOT сделки
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("GBPUSD", color=TEXT_COLOR)),
                ft.DataCell(ft.Text("BUY", color=SUCCESS_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("+$78.50", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Text("-$3.20", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("+$75.30", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Text("Закрыта", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Container(
                    content=ft.ElevatedButton("Лог", bgcolor=WARNING_COLOR, color="white"),
                    padding=ft.padding.only(left=8)
                ))
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("USDJPY", color=TEXT_COLOR)),
                ft.DataCell(ft.Text("SELL", color=ERROR_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("-$25.40", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("-$1.80", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("-$27.20", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("Закрыта", color=ERROR_COLOR)),
                ft.DataCell(ft.Container(
                    content=ft.ElevatedButton("Лог", bgcolor=WARNING_COLOR, color="white"),
                    padding=ft.padding.only(left=8)
                ))
            ]),
            
            # Открытые сделки
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("AUDUSD", color=TEXT_COLOR)),
                ft.DataCell(ft.Text("BUY", color=SUCCESS_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("+$15.60", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Text("-$1.50", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("+$14.10", color=SUCCESS_COLOR)),
                ft.DataCell(ft.Text("Открыта", color=WARNING_COLOR)),
                ft.DataCell(ft.Container(
                    content=ft.ElevatedButton("Лог", bgcolor=WARNING_COLOR, color="white"),
                    padding=ft.padding.only(left=8)
                ))
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("NZDUSD", color=TEXT_COLOR)),
                ft.DataCell(ft.Text("SELL", color=ERROR_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("-$8.90", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("-$1.20", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("-$10.10", color=ERROR_COLOR)),
                ft.DataCell(ft.Text("Открыта", color=WARNING_COLOR)),
                ft.DataCell(ft.Container(
                    content=ft.ElevatedButton("Лог", bgcolor=WARNING_COLOR, color="white"),
                    padding=ft.padding.only(left=8)
                ))
            ]),
            
            # Отмененные сделки
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("CADUSD", color=TEXT_COLOR)),
                ft.DataCell(ft.Text("BUY", color=SUBTEXT_COLOR)),
                ft.DataCell(ft.Text("$0.00", color=SUBTEXT_COLOR)),
                ft.DataCell(ft.Text("$0.00", color=SUBTEXT_COLOR)),
                ft.DataCell(ft.Text("$0.00", color=SUBTEXT_COLOR)),
                ft.DataCell(ft.Text("Отменена", color=SUBTEXT_COLOR)),
                ft.DataCell(ft.Container(
                    content=ft.ElevatedButton("Лог", bgcolor=WARNING_COLOR, color="white"),
                    padding=ft.padding.only(left=8)
                ))
            ])
        ]
    )
    
    # ----- ФИЛЬТРЫ -----
    filter_container = ft.Container(
        bgcolor=BLOCK_BG_COLOR,
        border_radius=12,
        padding=20,
        content=ft.Column([
            ft.Text("Фильтры", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(color=SUBTEXT_COLOR),
            
            ft.Row([
                ft.Text("Тип:", color=SUBTEXT_COLOR, size=14),
                ft.Dropdown(
                    width=120,
                    options=[
                        ft.dropdown.Option("Все"),
                        ft.dropdown.Option("Parser BOT"),
                        ft.dropdown.Option("Smart Money BOT")
                    ],
                    value="Все",
                    border_color="transparent",
                    color=SUBTEXT_COLOR,
                    bgcolor=BLOCK_BG_COLOR
                ),
                ft.Container(width=20),
                ft.Text("Статус:", color=SUBTEXT_COLOR, size=14),
                ft.Dropdown(
                    width=120,
                    options=[
                        ft.dropdown.Option("Все"),
                        ft.dropdown.Option("Открыта"),
                        ft.dropdown.Option("Закрыта"),
                        ft.dropdown.Option("Отменена")
                    ],
                    value="Все",
                    border_color="transparent",
                    color=SUBTEXT_COLOR,
                    bgcolor=BLOCK_BG_COLOR
                ),
                ft.Container(width=20),
                ft.Text("Инструмент:", color=SUBTEXT_COLOR, size=14),
                ft.Dropdown(
                    width=120,
                    options=[
                        ft.dropdown.Option("Все"),
                        ft.dropdown.Option("EURUSD"),
                        ft.dropdown.Option("GBPUSD"),
                        ft.dropdown.Option("XAUUSD"),
                        ft.dropdown.Option("USDJPY")
                    ],
                    value="Все",
                    border_color="transparent",
                    color=SUBTEXT_COLOR,
                    bgcolor=BLOCK_BG_COLOR
                )
            ]),
            
            ft.Container(height=10),
            
            ft.Row([
                ft.Text("Дата с:", color=SUBTEXT_COLOR, size=14),
                ft.TextField(
                    value="2024-01-01",
                    width=120,
                    border_color="transparent",
                    bgcolor=BLOCK_BG_COLOR,
                    color=TEXT_COLOR,
                    text_size=12
                ),
                ft.Container(width=20),
                ft.Text("Дата по:", color=SUBTEXT_COLOR, size=14),
                ft.TextField(
                    value="2024-12-31",
                    width=120,
                    border_color="transparent",
                    bgcolor=BLOCK_BG_COLOR,
                    color=TEXT_COLOR,
                    text_size=12
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Применить фильтр",
                    bgcolor=SUCCESS_COLOR,
                    color="white",
                    on_click=filter_trades
                )
            ])
        ], spacing=10)
    )
    
    # ----- СТАТИСТИКА -----
    stats_container = ft.Container(
        bgcolor=BLOCK_BG_COLOR,
        border_radius=12,
        padding=20,
        content=ft.Column([
            ft.Text("Общая статистика", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(color=SUBTEXT_COLOR),
            
            ft.Row([
                ft.Column([
                    ft.Text("Всего сделок", color=SUBTEXT_COLOR, size=12),
                    ft.Text("128", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Прибыльных", color=SUBTEXT_COLOR, size=12),
                    ft.Text("89", color=SUCCESS_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Убыточных", color=SUBTEXT_COLOR, size=12),
                    ft.Text("35", color=ERROR_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Отмененных", color=SUBTEXT_COLOR, size=12),
                    ft.Text("4", color=WARNING_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True)
            ], spacing=20),
            
            ft.Divider(color=SUBTEXT_COLOR),
            
            ft.Row([
                ft.Column([
                    ft.Text("Общая прибыль", color=SUBTEXT_COLOR, size=12),
                    ft.Text("$2,920.50", color=SUCCESS_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Макс. просадка", color=SUBTEXT_COLOR, size=12),
                    ft.Text("-$450.20", color=ERROR_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Винрейт", color=SUBTEXT_COLOR, size=12),
                    ft.Text("71.8%", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("Средний P&L", color=SUBTEXT_COLOR, size=12),
                    ft.Text("+$22.82", color=SUCCESS_COLOR, size=18, weight=ft.FontWeight.BOLD)
                ], expand=True)
            ], spacing=20)
        ], spacing=10)
    )
    
    # ----- ОСНОВНОЙ КОНТЕНТ -----
    content = ft.Column([
        # Заголовок
        ft.Text("История сделок", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(height=24),
        
        # Фильтры
        filter_container,
            ft.Container(height=20),

        # Статистика
        stats_container,
            ft.Container(height=20),

        # Таблица сделок
             ft.Container(
            bgcolor=BLOCK_BG_COLOR,
            border_radius=12,
            padding=20,
            content=ft.Column([
                ft.Text("Детальная таблица сделок", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(color=SUBTEXT_COLOR),
                trades_table
            ], spacing=10)
        )
    ], spacing=0, scroll=ft.ScrollMode.ADAPTIVE)
    
    return content 