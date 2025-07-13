from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTextEdit, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
import qtawesome as qta
ACCENT_COLOR = "#6C5ECF"

class MT5Card(QFrame):
    def __init__(self, title, value, icon_name, parent=None):
        super().__init__(parent)
        self.setObjectName("infoCard")
        layout = QHBoxLayout(self)
        icon = QLabel(); icon.setPixmap(qta.icon(icon_name, color=ACCENT_COLOR).pixmap(32, 32))
        text_layout = QVBoxLayout()
        title_label = QLabel(title); title_label.setObjectName("cardTitle")
        self.value_label = QLabel(value); self.value_label.setObjectName("cardValue")
        text_layout.addWidget(title_label); text_layout.addWidget(self.value_label)
        layout.addWidget(icon); layout.addLayout(text_layout)
        shadow = QGraphicsDropShadowEffect(self); shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(4); shadow.setColor(QColor(0,0,0,60)); self.setGraphicsEffect(shadow)

class MT5View(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mt5View")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        title = QLabel("MetaTrader 5 Account")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        main_layout.addWidget(title)

        # --- Account Info Cards ---
        cards_layout = QHBoxLayout()
        self.balance_card = MT5Card("Balance", "$10,580.50", "fa5s.dollar-sign")
        self.equity_card = MT5Card("Equity", "$10,580.50", "fa5s.chart-area")
        self.margin_card = MT5Card("Free Margin", "$8,230.00", "fa5s.file-invoice-dollar")
        cards_layout.addWidget(self.balance_card)
        cards_layout.addWidget(self.equity_card)
        cards_layout.addWidget(self.margin_card)
        cards_layout.addStretch()
        main_layout.addLayout(cards_layout)

        # --- Open Positions Table ---
        table_label = QLabel("Open Positions")
        table_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(table_label)

        self.positions_table = QTableWidget()
        self.positions_table.setObjectName("historyTable") # Reuse history style
        self.positions_table.setColumnCount(6)
        self.positions_table.setHorizontalHeaderLabels(["Ticket", "Symbol", "Type", "Volume", "Open Price", "Profit"])
        self.positions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.positions_table, 1)

        # Dummy data for positions
        self.update_positions_table([
            ("12345", "EURUSD", "BUY", "0.10", "1.07500", "+$25.50"),
            ("12346", "XAUUSD", "SELL", "0.05", "2350.00", "-$10.20"),
        ])

        # --- Connection Log ---
        log_label = QLabel("Connection Log")
        log_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setObjectName("logOutput")
        self.log_output.setStyleSheet("background-color: #1A1826; border-radius: 8px; color: white; padding: 10px;")
        self.log_output.setFixedHeight(150)
        main_layout.addWidget(self.log_output)
        
        # Add initial notice
        self.log_output.setPlainText("NOTE: MetaTrader5 connection is disabled on this operating system (macOS/Linux). This view is for demonstration purposes.")

    def update_account_info(self, info):
        """Updates the account info cards. Expects an object with .balance, .equity, etc."""
        self.balance_card.value_label.setText(f"${info.balance:,.2f}")
        self.equity_card.value_label.setText(f"${info.equity:,.2f}")
        self.margin_card.value_label.setText(f"${info.margin_free:,.2f}")

    def update_positions_table(self, positions):
        """Updates the open positions table."""
        self.positions_table.setRowCount(len(positions))
        for row, pos in enumerate(positions):
            for col, data in enumerate(pos):
                self.positions_table.setItem(row, col, QTableWidgetItem(str(data)))

    def add_log_message(self, message, level):
        """Appends a message to the log."""
        # You can add color coding here based on level
        self.log_output.append(message) 