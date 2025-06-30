# main_pyqt.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QLineEdit, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import Qt, QSize

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt6agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import FuncFormatter

# --- Цветовая палитра ---
BACKGROUND_COLOR = "#242734"
WIDGET_COLOR = "#2B2D3C"
ACCENT_COLOR = "#8A3FFC"
TEXT_COLOR = "#FFFFFF"
SECONDARY_TEXT_COLOR = "#A0A0A0"
CHART_PURPLE = "#6936F5"
CHART_PINK = "#F536A7"


class CombineTradeBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Combine Trade Bot")
        self.setGeometry(100, 100, 1440, 810)

        # --- Основной виджет и разметка ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Создание элементов интерфейса ---
        sidebar = self.create_sidebar()
        main_content = self.create_main_content()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(main_content)
        
        self.apply_styles()

    def create_sidebar(self):
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Логотип
        logo_label = QLabel("Combine Trade Bot")
        logo_label.setObjectName("logo")
        logo_label.setFixedHeight(40)
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(20)

        # Кнопки навигации
        nav_buttons_data = ["Dashboard", "Strategies", "Markets", "Trades", "Signals", "Portfolio", "Performance", "Reports"]
        for i, text in enumerate(nav_buttons_data):
            button = QPushButton(text)
            button.setObjectName("navButton")
            button.setFixedHeight(40)
            if text == "Dashboard":
                button.setProperty("active", True)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch() # Заполнитель, чтобы прижать нижний элемент

        # Статус AI Core
        ai_status_label = QLabel("AI Core: Active\nWB Bersinar")
        ai_status_label.setObjectName("aiStatus")
        sidebar_layout.addWidget(ai_status_label)
        
        return sidebar_frame

    def create_main_content(self):
        main_frame = QFrame()
        main_frame.setObjectName("mainContent")
        
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # --- Верхняя панель (Header) ---
        header = self.create_header()
        main_layout.addWidget(header)

        # --- Сетка с виджетами ---
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0,0,0,0)
        grid_layout.setSpacing(15)

        # Карточки статистики
        stats_data = [("Active Bots", "1,300"), ("Strategies", "42"), ("Open Orders", "128")]
        for i, (title, value) in enumerate(stats_data):
            grid_layout.addWidget(self.create_stat_card(title, value), 0, i)
        
        # Карточка PnL
        grid_layout.addWidget(self.create_pnl_card(), 0, 3)

        # Графики
        grid_layout.addWidget(self.create_portfolio_chart(), 1, 0, 1, 2)
        grid_layout.addWidget(self.create_summary_card(), 1, 2)
        grid_layout.addWidget(self.create_volume_chart(), 2, 0, 1, 3)
        
        # Список недавних транзакций
        grid_layout.addWidget(self.create_recent_trades_list(), 1, 3, 2, 1)

        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 2)
        grid_layout.setColumnStretch(2, 2)
        grid_layout.setColumnStretch(3, 3)
        grid_layout.setRowStretch(1, 2)
        grid_layout.setRowStretch(2, 3)
        
        main_layout.addWidget(grid_widget)
        
        return main_frame

    def create_header(self):
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0,0,0,0)
        
        overview_label = QLabel("Overview")
        overview_label.setObjectName("overviewTitle")
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search 'asset'...")
        search_input.setFixedSize(300, 40)
        
        user_profile = QWidget()
        user_layout = QHBoxLayout(user_profile)
        user_name = QLabel("Ceptari Tyas")
        user_avatar = QLabel("CT")
        user_avatar.setFixedSize(40, 40)
        user_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_avatar.setObjectName("userAvatar")
        user_layout.addWidget(user_name)
        user_layout.addSpacing(10)
        user_layout.addWidget(user_avatar)

        header_layout.addWidget(overview_label)
        header_layout.addStretch()
        header_layout.addWidget(search_input)
        header_layout.addSpacing(20)
        header_layout.addWidget(user_profile)
        return header_frame

    def create_stat_card(self, title, value):
        card = QFrame()
        card.setObjectName("infoCard")
        layout = QHBoxLayout(card)
        icon = QFrame()
        icon.setFixedSize(40, 40)
        icon.setObjectName("statIcon")
        layout.addWidget(icon)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        layout.addLayout(text_layout)
        return card

    def create_pnl_card(self):
        card = QFrame()
        card.setObjectName("pnlCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        id_label = QLabel("ID 123 887 552")
        id_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        title_label = QLabel("Total PnL")
        value_label = QLabel("$2,920")
        value_label.setObjectName("pnlValue")
        
        layout.addWidget(id_label)
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card
    
    def create_chart_frame(self, title_text):
        frame = QFrame()
        frame.setObjectName("infoCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20,20,20,20)
        title = QLabel(title_text)
        title.setObjectName("chartTitle")
        layout.addWidget(title)
        return frame, layout

    def create_portfolio_chart(self):
        frame, layout = self.create_chart_frame("Portfolio Distribution")
        
        content_layout = QHBoxLayout()
        fig = Figure(figsize=(2.5, 2.5), dpi=100, facecolor=WIDGET_COLOR)
        ax = fig.add_subplot(111)
        ax.pie([45, 25, 20, 10], wedgeprops=dict(width=0.45), startangle=90, colors=[CHART_PURPLE, CHART_PINK, "#4D4DA6", "#A64D8D"])
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        canvas = FigureCanvas(fig)
        canvas.setFixedSize(150, 150)
        
        legend_layout = QVBoxLayout()
        legend_layout.addStretch()
        legend_data = [("BTC", CHART_PURPLE), ("ETH", CHART_PINK), ("SOL", "#4D4DA6"), ("ADA", "#A64D8D")]
        for asset, color in legend_data:
            item_layout = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 20px;")
            item_layout.addWidget(dot)
            item_layout.addWidget(QLabel(asset))
            item_layout.addStretch()
            legend_layout.addLayout(item_layout)
        legend_layout.addStretch()
        
        content_layout.addWidget(canvas)
        content_layout.addLayout(legend_layout)
        layout.addLayout(content_layout)
        return frame

    def create_summary_card(self):
        frame, layout = self.create_chart_frame("Trade Summary")
        layout.addStretch()
        layout.addWidget(QLabel("Total Buys"))
        layout.addWidget(QLabel("564"))
        layout.addSpacing(10)
        layout.addWidget(QLabel("Total Sells"))
        layout.addWidget(QLabel("1205"))
        layout.addStretch()
        return frame
    
    def create_volume_chart(self):
        frame, layout = self.create_chart_frame("Trading Volume (In/Out)")
        
        fig = Figure(figsize=(10, 3), dpi=100, facecolor=WIDGET_COLOR)
        ax = fig.add_subplot(111)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        vol_in = [500, 600, 750, 800, 650, 700, 900]
        vol_out = [400, 500, 600, 550, 700, 650, 800]
        ax.plot(days, vol_in, color=CHART_PURPLE, linewidth=2.5)
        ax.fill_between(days, vol_in, color=CHART_PURPLE, alpha=0.1)
        ax.plot(days, vol_out, color=CHART_PINK, linewidth=2.5)
        ax.fill_between(days, vol_out, color=CHART_PINK, alpha=0.1)

        ax.set_facecolor(WIDGET_COLOR)
        for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']: ax.spines[spine].set_color(SECONDARY_TEXT_COLOR)
        ax.tick_params(axis='x', colors=SECONDARY_TEXT_COLOR, pad=10)
        ax.tick_params(axis='y', colors=SECONDARY_TEXT_COLOR, pad=10)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x)}'))
        ax.set_ylim(bottom=0)
        fig.tight_layout(pad=0)
        
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        return frame

    def create_recent_trades_list(self):
        frame, layout = self.create_chart_frame("Recent Trades")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        trades_data = [("BUY","BTC/USDT","$291","13 Jan 2025",CHART_PURPLE), ("BUY","ETH/USDT","$691","13 Jan 2025",CHART_PURPLE),
                       ("SELL","SOL/USDT","$80","13 Jan 2025",CHART_PINK), ("BUY","ADA/USDT","$256","13 Jan 2025",CHART_PURPLE),
                       ("SELL","LINK/USDT","$144","13 Jan 2025",CHART_PINK),("BUY","DOT/USDT","$308","13 Jan 2025",CHART_PURPLE)]

        for trade_type, pair, amount, date, color in trades_data:
            item = QFrame()
            item_layout = QHBoxLayout(item)
            icon = QLabel(trade_type[0])
            icon.setFixedSize(40,40)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet(f"background-color: {color}; border-radius: 10px; font-weight: bold;")

            text_layout = QVBoxLayout()
            text_layout.setSpacing(0)
            text_layout.addWidget(QLabel(f"{trade_type} {pair}"))
            text_layout.addWidget(QLabel(date))
            
            item_layout.addWidget(icon)
            item_layout.addLayout(text_layout)
            item_layout.addStretch()
            item_layout.addWidget(QLabel(amount))
            scroll_layout.addWidget(item)
            
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        return frame


    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QFrame#mainContent {{
                background-color: {BACKGROUND_COLOR};
            }}
            QFrame#sidebar {{
                background-color: {WIDGET_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-family: Arial;
                font-size: 14px;
            }}
            QLabel#logo {{
                font-size: 20px;
                font-weight: bold;
            }}
            QLabel#aiStatus {{
                color: {SECONDARY_TEXT_COLOR};
                font-size: 12px;
            }}
            QLabel#aiStatus::first-line {{
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QPushButton#navButton {{
                background-color: transparent;
                color: {TEXT_COLOR};
                border: none;
                text-align: left;
                padding: 0 15px;
                font-size: 14px;
                font-weight: normal;
                border-radius: 8px;
            }}
            QPushButton#navButton:hover {{
                background-color: #3A3C4C;
            }}
            QPushButton#navButton[active="true"] {{
                background-color: {ACCENT_COLOR};
                font-weight: bold;
            }}
            QLabel#overviewTitle {{
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {WIDGET_COLOR};
                color: {TEXT_COLOR};
                border: none;
                border-radius: 10px;
                padding: 0 15px;
            }}
            QLabel#userAvatar {{
                background-color: {ACCENT_COLOR};
                border-radius: 20px;
                font-weight: bold;
            }}
            QFrame#infoCard, QFrame#pnlCard {{
                background-color: {WIDGET_COLOR};
                border-radius: 15px;
            }}
            QFrame#pnlCard {{
                background-color: {ACCENT_COLOR};
                border-radius: 20px;
            }}
            QFrame#pnlCard QLabel {{
                font-size: 16px;
            }}
            QFrame#pnlCard QLabel#pnlValue {{
                font-size: 36px;
                font-weight: bold;
            }}
            QFrame#statIcon {{
                background-color: #4E4095;
                border-radius: 10px;
            }}
            QLabel#cardTitle {{
                color: {SECONDARY_TEXT_COLOR};
            }}
            QLabel#cardValue {{
                font-size: 28px;
                font-weight: bold;
            }}
            QLabel#chartTitle {{
                font-size: 16px;
                font-weight: bold;
            }}
            QScrollArea#scrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea#scrollArea QWidget {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {WIDGET_COLOR};
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {SECONDARY_TEXT_COLOR};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CombineTradeBotApp()
    window.show()
    sys.exit(app.exec())