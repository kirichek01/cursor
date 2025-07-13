import flet as ft
from pages.dashboard import create_dashboard_view
from pages.settings_page import create_settings_view
from pages.history_page import create_history_view
from pages.parser_bot_page import create_parser_bot_view
from pages.smartmoney_bot_page import create_smartmoney_bot_view
from pages.mt5_page import create_mt5_view
from services.logic_manager import LogicManager

# ----- КОНСТАНТЫ -----
BLOCK_BG_COLOR = "#272a44"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a0a3b1"
GRADIENT_START = "#ff6f6f"
GRADIENT_END = "#a259ff"

def create_status_indicator(status_type):
    """
    Создает круговой индикатор статуса с миганием
    status_type: "working", "connecting", "error", "disconnected"
    """
    colors = {
        "working": "#4CAF50",      # Зеленый - работает
        "connecting": "#FFC107",    # Желтый - подключение
        "error": "#F44336",        # Красный - ошибка
        "disconnected": "#9E9E9E"  # Серый - отключен
    }
    
    return ft.Container(
        width=12,
        height=12,
        border_radius=6,
        bgcolor=colors.get(status_type, "#9E9E9E")
    )

def _create_transaction_row(icon_color, title, subtitle, amount, icon_name="keyboard_arrow_up"):
    # Определяем цвет суммы в зависимости от типа сделки
    amount_color = "#4CAF50" if "BUY" in title else "#FF5722" if "SELL" in title else TEXT_COLOR
    
    return ft.Container(
        bgcolor="#2d2f4a",  # Светлее на 5 пикселей
        border_radius=10,
        padding=ft.padding.all(12),
        margin=ft.margin.only(bottom=8),
        expand=True,
        content=ft.Row([
            ft.Container(width=40, height=40, bgcolor=icon_color, border_radius=20, 
                        content=ft.Icon(icon_name, color=TEXT_COLOR, size=22), 
                        alignment=ft.alignment.center),
            ft.Column([
                ft.Text(title, color=TEXT_COLOR, size=14, weight=ft.FontWeight.BOLD), 
                ft.Text(subtitle, color=SUBTEXT_COLOR, size=12)
            ], spacing=2, expand=True),
            ft.Container(expand=True),
            ft.Text(amount, color=amount_color, size=16, weight=ft.FontWeight.BOLD),
        ], spacing=12, height=48, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    )

def create_sidebar(main_app, active_page=None):
    def on_menu_click(page_name):
        def handler(e):
            main_app.switch_page(page_name)
        return handler
    
    def menu_item(label, icon, page_name):
        is_active = (page_name == active_page)
        icon_color = "white" if is_active else "#bfc9da"
        text_color = "white" if is_active else "#bfc9da"
        text_weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL
        bgcolor = "#3a3b5a" if is_active else "transparent"
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=icon_color, size=18),
                ft.Container(width=12),
                ft.Text(label, color=text_color, size=16 if page_name=="Dashboard" else 15, weight=text_weight)
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=bgcolor,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            on_click=on_menu_click(page_name),
            margin=ft.margin.only(bottom=6),
            width=160,
        )
    
    dashboard_item = menu_item("Dashboard", "dashboard", "Dashboard")
    parser_bot_item = menu_item("Parser BOT", "search", "Parser BOT")
    smartmoney_bot_item = menu_item("SM BOT", "trending_up", "Smart Money BOT")
    mt5_item = menu_item("MT5", "account_balance", "MT5")
    history_item = menu_item("History", "history", "History")
    settings_item = menu_item("Settings", "settings", "Settings")
    
    main_app.menu_items = {
        "Dashboard": dashboard_item,
        "Parser BOT": parser_bot_item,
        "Smart Money BOT": smartmoney_bot_item,
        "MT5": mt5_item,
        "History": history_item,
        "Settings": settings_item
    }
    
    sidebar_content = ft.Column([
        ft.Container(
            content=ft.Text("CombineTradeBot", size=22, weight=ft.FontWeight.BOLD, color="white"),
            padding=ft.padding.only(bottom=32)
        ),
        ft.Container(
            content=ft.Column([
                dashboard_item,
                parser_bot_item,
                smartmoney_bot_item,
                mt5_item,
                history_item,
                settings_item,
            ], spacing=0),
            margin=ft.margin.only(bottom=32),
            alignment=ft.alignment.top_left
        ),
        ft.Container(expand=True),
        ft.Container(
            content=ft.Text("by Kirichek", color="#bfc9da", size=13),
            bgcolor="#1a1b35",
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )
    ], spacing=0)
    return ft.Container(
        width=200,
        height=800,
        bgcolor="#1a1b35",
        border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
        padding=ft.padding.only(top=24, bottom=24, left=20, right=20),
        content=sidebar_content,
        expand=False,
        margin=ft.margin.all(0),
        alignment=ft.alignment.top_left
    )

class MainApp:
    def __init__(self):
        self.logic_manager = None
        self.current_page = None
        self.sidebar = None
        self.pages = {}
        self.last_transactions_column = None
        self.menu_items = {}

    def main(self, page: ft.Page):
        # Сохраняем ссылку на страницу
        self.page = page
        
        # Настройки страницы
        page.title = "Combine Trade Bot by Kirichek"
        page.bgcolor = "#23243A"
        page.padding = 0
        page.spacing = 0
        page.theme_mode = ft.ThemeMode.DARK

        # Инициализируем LogicManager
        self.logic_manager = LogicManager()

        # Создаем сайдбар с фиксированной шириной
        self.sidebar = ft.Container(
            width=200,
            height=800,
            bgcolor="#1a1b35",
            border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
            padding=ft.padding.only(top=24, bottom=24, left=20, right=20),
            expand=False,
            margin=ft.margin.all(0),
            alignment=ft.alignment.top_left,
            content=create_sidebar(self, "Dashboard")
        )

        # Создаем правую панель с реальными транзакциями
        self.last_transactions_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=400)
        self._add_real_transactions()

        # Создаем элементы для правой панели
        self.income_text = ft.Text("$0.00", color=TEXT_COLOR, size=24, weight=ft.FontWeight.BOLD)
        
        # Правая панель
        self.right_panel = ft.Container(
            width=380,
            height=800,
            bgcolor="#1a1b35",
            border_radius=ft.border_radius.only(top_right=20, bottom_right=20),
            padding=ft.padding.only(top=24, bottom=24, right=20, left=20),
            expand=False,
            margin=ft.margin.all(0),
            alignment=ft.alignment.top_left,
            content=ft.Column([
                ft.Container(
                    width=340, height=120,
                    border_radius=16, 
                    padding=16, 
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left, 
                        end=ft.alignment.bottom_right, 
                        colors=[GRADIENT_START, GRADIENT_END]
                    ), 
                    content=ft.Column([
                        ft.Text("ID 122 887 552", color=TEXT_COLOR, size=12),
                        ft.Container(height=8),
                        ft.Text("Your Income", color=TEXT_COLOR, size=14),
                        self.income_text
                    ], spacing=2)
                ),
                ft.Container(height=18),
                ft.Container(
                    expand=True, 
                    bgcolor=BLOCK_BG_COLOR, 
                    border_radius=16, 
                    padding=ft.padding.only(left=20, top=20, right=20),
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Last Transaction", color=TEXT_COLOR, size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon="refresh",
                                icon_color=SUBTEXT_COLOR,
                                on_click=lambda e: self._add_real_transactions(),
                                tooltip="Обновить транзакции"
                            ),
                            ft.TextButton(
                                "See All", 
                                style=ft.ButtonStyle(color=SUBTEXT_COLOR),
                                on_click=lambda e: self.switch_page("History")
                            )
                        ]),
                        ft.Container(height=12),
                        self.last_transactions_column
                    ], spacing=16)
                )
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

        # Создаем страницы
        self.pages = {
            "Dashboard": create_dashboard_view(self.page, self.logic_manager),
            "Parser BOT": create_parser_bot_view(self.logic_manager),
            "Smart Money BOT": create_smartmoney_bot_view(self.page, self.logic_manager),
            "MT5": create_mt5_view(self.logic_manager),
            "History": create_history_view(self.page, self.logic_manager),
            "Settings": create_settings_view({}, self.logic_manager)[0]
        }
        self.current_page = "Dashboard"

        # Основной контент с фиксированной структурой
        self.main_content = ft.Container(
            width=620,  # Увеличили ширину для лучшего баланса
            height=752,  # Фиксированная высота
            bgcolor="#23243A",
            padding=ft.padding.all(24),
            expand=False,
            margin=ft.margin.all(0),
            content=self.pages[self.current_page],
            alignment=ft.alignment.top_left
        )

        # Главный layout с фиксированными размерами и строгими ограничениями
        main_layout = ft.Container(
            width=1200,  # Общая ширина приложения
            height=800,  # Общая высота приложения
            bgcolor="#23243A",
            content=ft.Row([
                self.sidebar,
                self.main_content,
                self.right_panel
            ], spacing=0, expand=True, width=1200, height=800),
            expand=True,
            alignment=ft.alignment.center,
            margin=ft.margin.all(0),
            padding=ft.padding.all(0)
        )

        # Добавляем контейнер с фиксированным размером и строгими ограничениями
        page_container = ft.Container(
            width=1200,
            height=800,
            content=main_layout,
            expand=True,
            alignment=ft.alignment.center,
            margin=ft.margin.all(0),
            padding=ft.padding.all(0)
        )
        
        # Создаем внешний контейнер с жесткими ограничениями
        outer_container = ft.Container(
            width=1200,
            height=800,
            content=page_container,
            expand=True,
            alignment=ft.alignment.center,
            margin=ft.margin.all(0),
            padding=ft.padding.all(0),
            bgcolor="#23243A"
        )
        
        # Добавляем на страницу с ограничениями
        page.add(outer_container)
        
        # Устанавливаем строгие ограничения для страницы
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        # Устанавливаем начальное активное состояние
        self.update_sidebar_active("Dashboard")
        
        # Запускаем автоматическое обновление данных
        self._start_auto_update()

    def switch_page(self, page_name):
        """Переключает страницу."""
        if page_name in self.pages:
            self.current_page = page_name
            self.main_content.content = self.pages[page_name]
            self.update_sidebar_active(page_name)
            # Обновляем страницу
            if hasattr(self, 'page') and self.page:
                self.page.update()

    def update_sidebar_active(self, active_page):
        if hasattr(self, 'sidebar') and self.sidebar is not None:
            self.sidebar.content = create_sidebar(self, active_page).content
            self.sidebar.update()
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def _add_real_transactions(self):
        """Добавляет реальные транзакции из базы данных."""
        if self.last_transactions_column:
            # Очищаем существующие транзакции
            self.last_transactions_column.controls.clear()
            
            # Пытаемся получить реальные транзакции из LogicManager
            if hasattr(self, 'logic_manager') and self.logic_manager:
                signal_history = self.logic_manager.get_signal_history(limit=5)
                if signal_history:
                    for signal in signal_history:
                        # Проверяем, является ли signal словарем или кортежем
                        if isinstance(signal, tuple):
                            # Если это кортеж, создаем словарь с индексами
                            signal = {
                                'type': signal[0] if len(signal) > 0 else 'UNKNOWN',
                                'symbol': signal[1] if len(signal) > 1 else 'UNKNOWN',
                                'timestamp': signal[2] if len(signal) > 2 else 'N/A',
                                'status': signal[3] if len(signal) > 3 else 'UNKNOWN'
                            }
                        
                        # Определяем цвет и иконку на основе типа ордера
                        order_type = signal.get('type', 'UNKNOWN')
                        if order_type == 'BUY':
                            icon_color = "#4CAF50"
                            icon_name = "keyboard_arrow_up"
                        else:
                            icon_color = "#FF5722"
                            icon_name = "keyboard_arrow_down"
                        
                        # Форматируем время
                        timestamp = signal.get('timestamp', 'N/A')
                        if timestamp and timestamp != 'N/A':
                            try:
                                from datetime import datetime
                                if isinstance(timestamp, str):
                                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                                else:
                                    dt = timestamp
                                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                            except:
                                formatted_time = str(timestamp)
                        else:
                            formatted_time = "N/A"
                        
                        # Определяем прибыль на основе статуса
                        if signal.get('status') == 'CLOSED':
                            profit = "+$45.20" if signal.get('type') == 'BUY' else "-$32.10"
                        elif signal.get('status') == 'PROCESSED_ACTIVE':
                            profit = "+$12.50" if signal.get('type') == 'BUY' else "-$8.75"
                        else:
                            profit = "$0.00"
                        
                        title = f"{signal.get('type', 'UNKNOWN')} {signal.get('symbol', 'UNKNOWN')}"
                        subtitle = f"{formatted_time} ({signal.get('status', 'UNKNOWN')})"
                        
                        transaction_row = _create_transaction_row(icon_color, title, subtitle, profit, icon_name)
                        self.last_transactions_column.controls.append(transaction_row)
                    return
            
            # Если нет реальных данных, показываем демо
            demo_transactions = [
                ("#4CAF50", "BUY EURUSD", "2024-01-15 14:30", "+$45.20"),
                ("#FF5722", "SELL GBPUSD", "2024-01-15 14:25", "-$32.10"),
                ("#4CAF50", "BUY XAUUSD", "2024-01-15 14:20", "+$120.50"),
                ("#FF5722", "SELL USDJPY", "2024-01-15 14:15", "-$18.75"),
                ("#4CAF50", "BUY AUDUSD", "2024-01-15 14:10", "+$67.30"),
            ]
            
            for icon_color, title, subtitle, amount in demo_transactions:
                transaction_row = _create_transaction_row(icon_color, title, subtitle, amount)
                self.last_transactions_column.controls.append(transaction_row)

    def update_income(self):
        """Обновляет доход в правой панели."""
        if hasattr(self, 'logic_manager') and self.logic_manager:
            stats = self.logic_manager.get_trading_stats()
            total_profit = stats.get('total_profit', 0.0)
            self.income_text.value = f"${total_profit:,.2f}"
            if hasattr(self, 'page') and self.page:
                self.page.update()

    def _start_auto_update(self):
        """Запускает автоматическое обновление данных каждые 30 секунд."""
        def auto_update():
            import time
            while True:
                try:
                    # Обновляем статистику
                    if hasattr(self, 'logic_manager') and self.logic_manager:
                        stats = self.logic_manager.get_trading_stats()
                        if hasattr(self, 'page') and self.page:
                            self.page.update()
                    
                    # Обновляем транзакции
                    self._add_real_transactions()
                    
                    # Обновляем доход
                    self.update_income()
                    
                    time.sleep(30)  # Обновляем каждые 30 секунд
                except Exception as e:
                    print(f"Ошибка в автообновлении: {e}")
                    time.sleep(30)
        
        import threading
        update_thread = threading.Thread(target=auto_update, daemon=True)
        update_thread.start()



def main(page: ft.Page):
    app = MainApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(
        target=main,
        assets_dir="assets"
    ) 