from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QFrame, QGridLayout, QLineEdit, QCheckBox, QRadioButton, QTabWidget,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Slot
import mplfinance as mpf
import pandas as pd
import qtawesome as qta

from ..widgets import MplCanvas

ACCENT_COLOR = "#6C5ECF"

# We can reuse the InfoCard from the Dashboard view if we move it to a common widgets directory
# For now, let's create a similar card here for simplicity.

class SMCard(QFrame):
    def __init__(self, title, value, icon_name, parent=None):
        super().__init__(parent)
        self.setObjectName("infoCard")
        layout = QHBoxLayout(self)
        
        icon = QLabel()
        icon.setPixmap(qta.icon(icon_name, color=ACCENT_COLOR).pixmap(32, 32))
        
        text_layout = QVBoxLayout()
        title_label = QLabel(title); title_label.setObjectName("cardTitle")
        self.value_label = QLabel(value); self.value_label.setObjectName("cardValue")
        text_layout.addWidget(title_label); text_layout.addWidget(self.value_label)
        
        layout.addWidget(icon); layout.addLayout(text_layout)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(4); shadow.setColor(QColor(0,0,0,60))
        self.setGraphicsEffect(shadow)

class SmartMoneyView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Main Layout ---
        main_layout = QHBoxLayout(self)
        
        # --- Left Panel (Charts) ---
        left_panel = QVBoxLayout()
        self.symbol_tabs = QTabWidget()
        self.charts = {} # To hold canvas for each symbol
        
        symbols = ["XAUUSD", "NAS100", "GER40", "EURUSD", "BTCUSD"]
        for symbol in symbols:
            chart_widget = QWidget()
            chart_layout = QVBoxLayout(chart_widget)
            canvas = MplCanvas(self)
            chart_layout.addWidget(canvas)
            self.charts[symbol] = canvas
            self.symbol_tabs.addTab(chart_widget, symbol)
            
        left_panel.addWidget(self.symbol_tabs)
        main_layout.addLayout(left_panel, 3) # Give more space

        # --- Right Panel (Controls & Log) ---
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 0, 10, 0)
        
        # Control Buttons
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("🚀 Run Backtest")
        self.stop_button = QPushButton("🛑 Stop")
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        right_panel.addLayout(control_layout)
        
        # Settings
        right_panel.addWidget(self._create_settings_panel())
        
        # Log
        log_label = QLabel("Event Log")
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True)
        right_panel.addWidget(log_label)
        right_panel.addWidget(self.log_output)
        
        main_layout.addLayout(right_panel, 1)

    def _create_settings_panel(self):
        settings_frame = QFrame(); settings_frame.setObjectName("settingsGroup")
        layout = QGridLayout(settings_frame)
        
        # Mode
        self.paper_mode_rb = QRadioButton("Paper Trading (Backtest)"); self.paper_mode_rb.setChecked(True)
        self.live_mode_rb = QRadioButton("Live Trading")
        layout.addWidget(self.paper_mode_rb, 0, 0); layout.addWidget(self.live_mode_rb, 0, 1)

        # Inputs
        self.inputs = {}
        settings = [("Risk (%)", "risk", "1.0"), ("SL (pips)", "sl_pips", "30"), 
                    ("TP Ratio", "tp_ratio", "2.0"), ("Timeframe", "timeframe", "M15")]
        for i, (label, key, default) in enumerate(settings):
            layout.addWidget(QLabel(label), i + 1, 0)
            line_edit = QLineEdit(); line_edit.setPlaceholderText(default)
            self.inputs[key] = line_edit
            layout.addWidget(line_edit, i + 1, 1)
            
        # Checkbox
        self.auto_learn_cb = QCheckBox("Train Smart AI (Auto-Learn)")
        layout.addWidget(self.auto_learn_cb, len(settings) + 1, 0, 1, 2)
        
        return settings_frame

    @Slot(str)
    def add_log_message(self, message):
        self.log_output.append(message)

    @Slot(str, pd.DataFrame)
    def plot_chart(self, symbol, df):
        canvas = self.charts.get(symbol)
        if not canvas: return
        canvas.axes.clear()
        
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.set_index('datetime')
            
        mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', inherit=True)
        s  = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='nightclouds', gridstyle='-')
        
        # You would add plots for OB, BOS etc. here using mpf.make_addplot
        mpf.plot(df, type='candle', ax=canvas.axes, style=s, volume=False)
        
        canvas.draw()
        
    def get_current_settings(self):
        settings = {key: widget.text() or widget.placeholderText() for key, widget in self.inputs.items()}
        settings["mode"] = "live" if self.live_mode_rb.isChecked() else "paper"
        settings["auto_learn"] = self.auto_learn_cb.isChecked()
        settings["symbol"] = self.symbol_tabs.tabText(self.symbol_tabs.currentIndex())
        return settings 