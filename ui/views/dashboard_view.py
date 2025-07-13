import matplotlib
matplotlib.use('QtAgg') # Set the backend before importing pyplot
import pandas as pd
from scipy.interpolate import make_interp_spline
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPalette, QFont, QPixmap
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import qtawesome as qta

from ..widgets import StyledCard, MplCanvas

# Hardcoding colors instead of importing from theme
CHART_PINK = "#F536A7"
CHART_PURPLE = "#6C5ECF"
SECONDARY_TEXT_COLOR = "#8E8E93"
SUCCESS_COLOR = "#00B16A"
DANGER_COLOR = "#F44336"
TEXT_COLOR = "#FFFFFF"

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardView")
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(20,20,20,20); main_layout.setSpacing(15)
        
        # --- Top Grid (2 rows, 3 columns) ---
        top_grid = QGridLayout(); top_grid.setSpacing(15)
        self.cards = {
            "balance": StyledCard("MT5 Balance", "$0.00", "assets/icons/wallet.svg"),
            "parser": StyledCard("Parser Profit", "$0.00", "assets/icons/chart-pie.svg"),
            "smartmoney": StyledCard("SM Profit", "$0.00", "assets/icons/coin-stack.svg"),
            "status": StyledCard("System Status", "Offline", "assets/icons/battery.svg"),
            "total": StyledCard("Total Profit", "$0.00", "assets/icons/usd-circle.svg")
        }
        top_grid.addWidget(self.cards["balance"], 0, 0); top_grid.addWidget(self.cards["parser"], 0, 1); top_grid.addWidget(self.cards["smartmoney"], 0, 2)
        top_grid.addWidget(self.cards["status"], 1, 0); top_grid.addWidget(self.cards["total"], 1, 1, 1, 2)
        main_layout.addLayout(top_grid)

        # --- Middle Block (Charts) ---
        charts_layout = QHBoxLayout(); charts_layout.setSpacing(15)
        charts_layout.addWidget(self._create_pie_chart_card())
        charts_layout.addWidget(self._create_line_chart_card())
        main_layout.addLayout(charts_layout)
        
        main_layout.addStretch()

    def _create_pie_chart_card(self):
        card = QFrame(); card.setProperty("class", "CardWidget")
        layout = QHBoxLayout(card)
        
        canvas = MplCanvas(self, width=3, height=3)
        self.pie_ax = canvas.axes
        profits = [1230.10, 850.75]; colors = [CHART_PURPLE, CHART_PINK]
        self.pie_ax.pie(profits, colors=colors, wedgeprops=dict(width=0.45), startangle=90)
        self.pie_ax.text(0., 0., '89%', ha='center', va='center', fontsize=28, color='white', weight='bold')
        layout.addWidget(canvas)
        
        # Legend
        legend_layout = QVBoxLayout(); legend_layout.addStretch()
        for label, color in [("Parser", CHART_PURPLE), ("SmartMoney", CHART_PINK)]:
            row = QHBoxLayout()
            dot = QLabel("●"); dot.setStyleSheet(f"color: {color};")
            row.addWidget(dot); row.addWidget(QLabel(label)); row.addStretch()
            legend_layout.addLayout(row)
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        return card

    def _create_line_chart_card(self):
        card = QFrame(); card.setProperty("class", "CardWidget")
        layout = QVBoxLayout(card)
        layout.addWidget(QLabel("7-Day Profit"))
        canvas = MplCanvas(self)
        self.line_ax = canvas.axes
        
        days = np.array([0, 1, 2, 3, 4, 5, 6])
        profit1 = np.array([100, 150, 120, 200, 180, 250, 230])
        profit2 = np.array([80, 100, 110, 130, 150, 140, 160])
        
        spline1 = make_interp_spline(days, profit1); days_smooth = np.linspace(days.min(), days.max(), 300)
        profit1_smooth = spline1(days_smooth)
        spline2 = make_interp_spline(days, profit2)
        profit2_smooth = spline2(days_smooth)
        
        canvas.axes.plot(days_smooth, profit1_smooth, color=CHART_PURPLE, linewidth=3)
        canvas.axes.plot(days_smooth, profit2_smooth, color=CHART_PINK, linewidth=3)
        canvas.axes.fill_between(days_smooth, profit1_smooth, color=CHART_PURPLE, alpha=0.1)
        canvas.axes.fill_between(days_smooth, profit2_smooth, color=CHART_PINK, alpha=0.1)
        canvas.axes.set_xticks(days, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        
        layout.addWidget(canvas)
        return card

    def _create_status_card(self):
        card = QFrame()
        card.setObjectName("statusCard") # Use new ID for specific styling
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 20)
        
        title = QLabel("System Status")
        title.setObjectName("chartTitle")
        layout.addWidget(title)
        layout.addSpacing(10)

        self.mt5_status_indicator = self._add_status_row(layout, "MT5", True)
        self.parser_status_indicator = self._add_status_row(layout, "Parser", True)
        self.sm_bot_status_indicator = self._add_status_row(layout, "SmartMoney Bot", True)
        self.telegram_status_indicator = self._add_status_row(layout, "Telegram", False)
        
        layout.addStretch()
        return card

    def _add_status_row(self, parent_layout, name, is_online):
        row_layout = QHBoxLayout()
        label = QLabel(name)
        
        indicator = QLabel()
        indicator.setFixedSize(12, 12)
        indicator.setStyleSheet(f"color: {SUCCESS_COLOR if is_online else DANGER_COLOR}; border-radius: 6px;")
        
        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(indicator)
        parent_layout.addLayout(row_layout)
        
        return indicator
        
    def update_data(self, balance_data, profit_data, status_text):
        self.cards["balance"].value_label.setText(f"${balance_data:,.2f}")
        self.cards["parser"].value_label.setText(f"${profit_data.get('parser', 0):,.2f}")
        self.cards["smartmoney"].value_label.setText(f"${profit_data.get('smartmoney', 0):,.2f}")
        self.cards["status"].value_label.setText(status_text)
        total = sum(profit_data.values()) + balance_data
        self.cards["total"].value_label.setText(f"${total:,.2f}")
        
    def update_pie_chart(self, mt5_profit, parser_profit, sm_profit):
        self.pie_ax.clear()
        profits = [p for p in [mt5_profit, parser_profit, sm_profit] if p > 0]
        labels = ["MT5", "Parser", "SM"]
        colors = [CHART_PURPLE, CHART_PINK, "#4CAF50"]
        # Filter out zero-profit slices to avoid visual clutter
        non_zero_profits = [p for p in profits if p > 0]
        non_zero_labels = [l for i, l in enumerate(labels) if profits[i] > 0]
        non_zero_colors = [c for i, c in enumerate(colors) if profits[i] > 0]

        if not non_zero_profits: # If all are zero or negative
             non_zero_profits = [1]
             non_zero_labels = ["No Profit"]
             non_zero_colors = [SECONDARY_TEXT_COLOR]

        self.pie_ax.pie(non_zero_profits, labels=non_zero_labels, colors=non_zero_colors,
                        autopct='%1.1f%%', textprops={'color': TEXT_COLOR})
        self.pie_ax.figure.canvas.draw()

    def update_line_chart(self, dates, parser_profits, sm_profits):
        self.line_ax.clear()
        self.line_ax.plot(dates, parser_profits, color=CHART_PURPLE)
        self.line_ax.plot(dates, sm_profits, color=CHART_PINK)
        self.line_ax.figure.canvas.draw() 