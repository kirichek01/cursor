import flet as ft
import threading
from components import smc_logic
from datetime import datetime

# ----- ГЛОБАЛЬНОЕ ХРАНИЛИЩЕ ДАННЫХ -----
# Это простой способ для обмена данными между потоками и UI.
class AppState:
    def __init__(self):
        self.smc_trades = []
        self.active_trades = []

    def add_smc_trades(self, new_trades_df):
        new_trades = new_trades_df.to_dict('records')
        self.smc_trades.extend(new_trades)

# Создаем один экземпляр хранилища для всего приложения
app_state = AppState()

def create_smartmoney_view(page: ft.Page):
    """Создает и возвращает весь контент для страницы SmartMoney."""

    # ----- ЭЛЕМЕНТЫ УПРАВЛЕНИЯ -----
    symbol_input = ft.TextField(label="Символ", value="XAUUSD", width=150)
    timeframe_input = ft.Dropdown(
        label="Таймфрейм",
        width=150,
        options=[
            ft.dropdown.Option("M1"),
            ft.dropdown.Option("M5"),
            ft.dropdown.Option("M15"),
            ft.dropdown.Option("M30"),
            ft.dropdown.Option("H1"),
            ft.dropdown.Option("H4"),
            ft.dropdown.Option("D1"),
        ],
        value="M15",
    )
    date_from_input = ft.TextField(label="Дата начала (гггг-мм-дд)", value="2025-01-01", width=250)
    date_to_input = ft.TextField(label="Дата конца (гггг-мм-дд)", value="2025-06-01", width=250)
    start_button = ft.ElevatedButton(text="Запустить стратегию", icon="play_arrow_rounded")
    status_text = ft.Text("Ожидание запуска...", italic=True)
    progress_bar = ft.ProgressBar(width=400, visible=False)
    
    # ----- ТАБЛИЦА ДЛЯ РЕЗУЛЬТАТОВ -----
    results_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Время")),
            ft.DataColumn(ft.Text("Тип")),
            ft.DataColumn(ft.Text("Вход")),
            ft.DataColumn(ft.Text("SL")),
            ft.DataColumn(ft.Text("TP1")),
            ft.DataColumn(ft.Text("Лот")),
            ft.DataColumn(ft.Text("PnL ($)")),
            ft.DataColumn(ft.Text("Баланс")),
        ],
        rows=[],
    )

    # ----- ЛОГИКА ЗАПУСКА -----
    def run_strategy_in_thread():
        try:
            # 1. Показываем прогресс
            status_text.value = "Загрузка данных из MT5..."
            progress_bar.visible = True
            page.update()

            # Проверяем, что значения не None
            symbol = symbol_input.value or ""
            timeframe = timeframe_input.value or "M15"
            date_from = date_from_input.value or ""
            date_to = date_to_input.value or ""

            df_raw = smc_logic.load_mt5_data(
                symbol=symbol,
                timeframe=timeframe,
                date_from=date_from,
                date_to=date_to
            )
            if df_raw is None:
                status_text.value = "Ошибка: не удалось загрузить данные из MT5."
                progress_bar.visible = False
                page.update()
                return

            status_text.value = "Генерация признаков SMC..."
            page.update()
            df_features = smc_logic.generate_smc_features(df_raw)

            status_text.value = "Выполнение стратегии..."
            page.update()
            trades_df = smc_logic.run_strategy(df_features)

            # Обновляем глобальное состояние
            app_state.add_smc_trades(trades_df)
            
            # Отправляем сообщение об обновлении
            page.pubsub.send_all("update_logs")

            # 4. Обновляем таблицу в UI
            if results_table.rows is not None:
                results_table.rows.clear()
            else:
                results_table.rows = [] # Инициализируем, если None
            
            for _, row in trades_df.iterrows():
                if results_table.rows is not None:
                    results_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(row['time'].strftime('%Y-%m-%d %H:%M'))),
                            ft.DataCell(ft.Text(row['type'], color="green" if row['type'] == 'buy' else "red")),
                            ft.DataCell(ft.Text(f"{row['entry']:.2f}")),
                            ft.DataCell(ft.Text(f"{row['sl']:.2f}")),
                            ft.DataCell(ft.Text(f"{row['tp1']:.2f}")),
                            ft.DataCell(ft.Text(f"{row['lot']:.2f}")),
                            ft.DataCell(ft.Text(f"{row['pnl_usd']:.2f}", color="green" if row['pnl_usd'] > 0 else "red")),
                            ft.DataCell(ft.Text(f"{row['balance']:.2f}")),
                        ])
                    )
            
            status_text.value = f"Готово! Найдено {len(trades_df)} сделок."

        except Exception as e:
            status_text.value = f"Произошла ошибка: {e}"
        finally:
            # 5. Скрываем прогресс
            progress_bar.visible = False
            page.update()

    def run_strategy_clicked(e):
        thread = threading.Thread(target=run_strategy_in_thread, daemon=True)
        thread.start()

    start_button.on_click = run_strategy_clicked

    # ----- СБОРКА СТРАНИЦЫ -----
    return ft.Column(
        [
            ft.Text("Настройки SmartMoney Bot", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([symbol_input, timeframe_input]),
            ft.Row([date_from_input, date_to_input]),
            ft.Container(height=20),
            start_button,
            ft.Row([status_text, progress_bar]),
            ft.Container(height=20),
            ft.Text("Результаты торговли", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=results_table,
                expand=True, # Чтобы таблица растягивалась
                border=ft.border.all(1, "#44475a"),
                border_radius=8,
            )
        ],
        expand=True,
        spacing=10,
        scroll=ft.ScrollMode.ADAPTIVE,
    ) 