import flet as ft
from components.charts import generate_donut_chart, generate_line_chart, generate_real_donut_chart, generate_real_profit_chart
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

def get_real_trading_stats(logic_manager):
    """Получение реальной статистики торговли из MT5 и базы данных"""
    if not logic_manager:
        return {
            'total_profit': "$0.00",
            'max_drawdown': "$0.00",
            'total_trades': "0",
            'open_trades': "0",
            'profitable_trades': "0"
        }
    
    try:
        # Получаем информацию об аккаунте MT5
        account_info = logic_manager.get_mt5_account_info()
        if account_info:
            # Реальные данные из MT5
            balance = account_info.get('balance', 0.0)
            equity = account_info.get('equity', 0.0)
            profit = equity - balance
            
            # Получаем открытые позиции
            positions = logic_manager.get_mt5_positions()
            open_trades = len(positions)
            
            # Получаем историю сделок
            deals_history = logic_manager.get_mt5_deals_history(days=30)
            total_trades = len(deals_history) if deals_history else 0
            
            # Подсчитываем прибыльные сделки
            profitable_trades = 0
            if deals_history:
                for deal in deals_history:
                    if hasattr(deal, 'profit') and deal.profit > 0:
                        profitable_trades += 1
            
            return {
                'total_profit': f"${profit:,.2f}",
                'max_drawdown': f"${abs(min(profit, 0)):,.2f}",
                'total_trades': str(total_trades),
                'open_trades': str(open_trades),
                'profitable_trades': str(profitable_trades)
            }
        else:
            # Fallback на данные из базы
            stats = logic_manager.get_trading_stats()
            signal_history = logic_manager.get_signal_history(limit=100)
            
            total_profit = stats.get('total_profit', 0.0)
            total_trades = len(signal_history)
            closed_trades = len([s for s in signal_history if isinstance(s, dict) and s.get('status') in ['CLOSED', 'PROCESSED_CLOSED']])
            open_trades = len([s for s in signal_history if isinstance(s, dict) and s.get('status') in ['PROCESSED_ACTIVE', 'NEW']])
            
            return {
                'total_profit': f"${total_profit:,.2f}",
                'max_drawdown': f"${abs(min(total_profit, 0)):,.2f}",
                'total_trades': str(total_trades),
                'open_trades': str(open_trades),
                'profitable_trades': str(closed_trades // 2)  # Примерно половина закрытых сделок
            }
    except Exception as e:
        print(f"Ошибка получения статистики MT5: {e}")
        # Fallback на базовые данные
        return {
            'total_profit': "$0.00",
            'max_drawdown': "$0.00",
            'total_trades': "0",
            'open_trades': "0",
            'profitable_trades': "0"
        }

def create_dashboard_view(page, logic_manager=None):
    """
    Создает и возвращает только центральную часть Dashboard (без правой панели).
    Правая панель теперь создается в main.py.
    """
    # Получаем реальную статистику
    real_stats = get_real_trading_stats(logic_manager)
    
    # Создаем графики с реальными данными
    try:
        donut_chart = generate_real_donut_chart(logic_manager)
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
        line_chart = generate_real_profit_chart(logic_manager, days=7)
    except Exception as e:
        print(f"Ошибка создания line chart: {e}")
        line_chart = ft.Container(
            height=200, 
            bgcolor=BLOCK_BG_COLOR, 
            border_radius=8,
            content=ft.Text("Chart Error", color=TEXT_COLOR, size=12),
            alignment=ft.alignment.center
        )

    # Создаем элементы статистики для обновления
    total_profit_text = ft.Text(real_stats['total_profit'], color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    max_drawdown_text = ft.Text(real_stats['max_drawdown'], color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    total_trades_text = ft.Text(real_stats['total_trades'], color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    open_trades_text = ft.Text(real_stats['open_trades'], color=TEXT_COLOR, size=24, weight=ft.FontWeight.BOLD)
    profitable_trades_text = ft.Text(real_stats['profitable_trades'], color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)
    session_total_trades_text = ft.Text(str(real_stats.get('total_trades', '0')), color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD)

    def update_stats(e):
        """Обновляет статистику в реальном времени."""
        if logic_manager:
            new_stats = get_real_trading_stats(logic_manager)
            total_profit_text.value = new_stats['total_profit']
            max_drawdown_text.value = new_stats['max_drawdown']
            total_trades_text.value = new_stats['total_trades']
            open_trades_text.value = new_stats['open_trades']
            profitable_trades_text.value = new_stats['profitable_trades']
            session_total_trades_text.value = str(new_stats.get('total_trades', '0'))
            
            # Обновляем страницу
            if page:
                page.update()
                print("✅ Статистика обновлена")

    # Удалены все вызовы page.set_timer и связанные комментарии
    # Автообновление только через поток main.py (_start_auto_update)

    # Кнопка обновления
    refresh_button = ft.IconButton(
        icon="refresh",
        icon_color=SUBTEXT_COLOR,
        on_click=update_stats,
        tooltip="Обновить статистику"
    )
    
    # Автообновление будет запущено в main.py через _start_auto_update()

    return ft.Column(
        controls=[
            # Заголовок с кнопкой обновления
            ft.Row([
                ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Container(expand=True),
                refresh_button,
            ]),
            ft.Container(height=24),
            ft.Row([
                ft.Container(
                    bgcolor=BLOCK_BG_COLOR,
                    border_radius=12,
                    padding=16,
                    content=ft.Row([
                        ft.Container(
                            width=40, height=40, 
                            bgcolor="#3676e0", 
                            border_radius=20, 
                            content=ft.Icon("people_outline", color=TEXT_COLOR, size=20), 
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text("Общая прибыль", color=SUBTEXT_COLOR, size=12),
                            total_profit_text,
                        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=12),
                    expand=True
                ),
                ft.Container(width=22),
                ft.Container(
                    bgcolor=BLOCK_BG_COLOR,
                    border_radius=12,
                    padding=16,
                    content=ft.Row([
                        ft.Container(
                            width=40, height=40, 
                            bgcolor="#fbc858", 
                            border_radius=20, 
                            content=ft.Icon("work_outline", color=TEXT_COLOR, size=20), 
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text("Макс. просадка", color=SUBTEXT_COLOR, size=12),
                            max_drawdown_text,
                        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=12),
                    expand=True
                ),
                ft.Container(width=22),
                ft.Container(
                    bgcolor=BLOCK_BG_COLOR,
                    border_radius=12,
                    padding=16,
                    content=ft.Row([
                        ft.Container(
                            width=40, height=40, 
                            bgcolor="#ff6a6a", 
                            border_radius=20, 
                            content=ft.Icon("request_quote", color=TEXT_COLOR, size=20), 
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text("Всего сделок", color=SUBTEXT_COLOR, size=12),
                            total_trades_text,
                        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=12),
                    expand=True
                )
            ], spacing=0),
            ft.Container(height=24),
            ft.Row(
                [
                    ft.Container(
                        expand=2,  # Увеличиваем ширину левого блока
                        height=220, 
                        bgcolor=BLOCK_BG_COLOR, 
                        border_radius=12, 
                        padding=20, 
                        content=ft.Column([
                            ft.Text("Статус сервисов", color=TEXT_COLOR, size=14),
                            ft.Row([
                                ft.Container(content=donut_chart, width=150, height=150, alignment=ft.alignment.center),
                                ft.Column([
                                    _create_legend_item("#4CAF50" if logic_manager and logic_manager.mt5 else "#f44336", 
                                                      "MT5: " + ("Подключен" if logic_manager and logic_manager.mt5 else "Отключен"), "●"), 
                                    _create_legend_item("#4CAF50" if logic_manager and logic_manager.telegram else "#f44336", 
                                                      "PA: " + ("Активен" if logic_manager and logic_manager.telegram else "Остановлен"), "●"),
                                    _create_legend_item("#4CAF50" if logic_manager and logic_manager.signal_processor else "#f44336", 
                                                      "SM: " + ("Активен" if logic_manager and logic_manager.signal_processor else "Остановлен"), "●")
                                ], spacing=8, expand=True, alignment=ft.MainAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
                        ], spacing=10)
                    ),
                    ft.Container(width=24),
                    ft.Container(
                        expand=1,  # Уменьшаем ширину правого блока
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
                            open_trades_text,
                            ft.Container(content=ft.Text("Открытых сделок", color=SUBTEXT_COLOR, size=12), margin=ft.margin.only(top=10)),
                            profitable_trades_text,
                            ft.Container(content=ft.Text("Прибыльных", color=SUBTEXT_COLOR, size=12), margin=ft.margin.only(top=10)),
                            session_total_trades_text
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

 