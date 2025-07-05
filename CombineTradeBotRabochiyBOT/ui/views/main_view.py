from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QLinearGradient, QBrush
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np

class MainView(QWidget):
    """
    The main dashboard view. This version includes the final, corrected chart creation logic.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.equity_data = []
        self._setup_ui()

    def _apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 120))
        widget.setGraphicsEffect(shadow)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        top_controls_layout = QHBoxLayout()
        self.start_stop_button = QPushButton("🚀 START BOT")
        self.start_stop_button.setObjectName("PrimaryButton")
        self.start_stop_button.setFixedHeight(45)
        self._apply_shadow(self.start_stop_button)

        self.save_button = QPushButton("💾 SAVE ALL SETTINGS")
        # --- aliases for alternative names (btn) ---
        self.start_stop_btn = self.start_stop_button  # alias
        self.save_btn       = self.save_button        # alias
        # -------------------------------------------
        self.save_button.setObjectName("SecondaryButton")
        self.save_button.setFixedHeight(45)
        self._apply_shadow(self.save_button)
        
        top_controls_layout.addWidget(self.start_stop_button)
        top_controls_layout.addStretch()
        top_controls_layout.addWidget(self.save_button)
        main_layout.addLayout(top_controls_layout)

        status_grid_layout = QGridLayout()
        status_grid_layout.setSpacing(20)
        self.telegram_card = self._create_status_card("Telegram Service")
        self.gpt_card = self._create_status_card("GPT Parser")
        self.mt5_card = self._create_status_card("MetaTrader 5")
        status_grid_layout.addWidget(self.telegram_card, 0, 0)
        status_grid_layout.addWidget(self.gpt_card, 0, 1)
        status_grid_layout.addWidget(self.mt5_card, 0, 2)
        main_layout.addLayout(status_grid_layout)

        self.chart_card = self._create_chart_card()
        main_layout.addWidget(self.chart_card)
        main_layout.setStretch(main_layout.count() - 1, 1)

    def _create_status_card(self, title):
        shadow_container = QWidget()
        shadow_container.setAttribute(Qt.WA_TranslucentBackground)
        self._apply_shadow(shadow_container)
        
        card = QFrame(shadow_container)
        card.setObjectName("InfoCard")
        container_layout = QVBoxLayout(shadow_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.addWidget(card)
        
        card_layout = QHBoxLayout(card)
        title_label = QLabel(title)
        title_label.setObjectName("CardContent")
        status_label = QLabel("OFFLINE")
        status_label.setObjectName("CardStatusDisconnected")
        card.status_label = status_label
        card_layout.addWidget(title_label)
        card_layout.addStretch()
        card_layout.addWidget(status_label)
        return shadow_container
        
    def _create_chart_card(self):
        shadow_container = QWidget()
        shadow_container.setAttribute(Qt.WA_TranslucentBackground)
        self._apply_shadow(shadow_container)
        
        card = QFrame(shadow_container)
        card.setObjectName("InfoCard")
        container_layout = QVBoxLayout(shadow_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.addWidget(card)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(QLabel("AI Simulation Equity Curve", objectName="CardTitle"))
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#44475a")
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='#bd93f9'))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#6272a4'))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.plot_widget.getPlotItem().hideAxis('bottom')
        
        # --- ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        # 1. Создаем объект для линии графика
        self.equity_curve_item = self.plot_widget.plot(pen=pg.mkPen(color='#50fa7b', width=2))
        
        # 2. Создаем вторую, невидимую линию на уровне земли (для заливки)
        self.fill_line = self.plot_widget.plot(pen=None)
        
        # 3. Создаем объект заливки между двумя линиями
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0.3, QColor(80, 250, 123, 100))
        gradient.setColorAt(1.0, QColor(80, 250, 123, 0))
        
        # Правильно создаем кисть и применяем ее к объекту заливки
        fill_brush = QBrush(gradient)
        self.fill_item = pg.FillBetweenItem(self.equity_curve_item, self.fill_line, brush=fill_brush)
        self.plot_widget.addItem(self.fill_item)
        
        layout.addWidget(self.plot_widget)
        return shadow_container

    def update_equity_curve(self, history_data):
        """Updates the chart with a full list of balance points."""
        self.equity_data = history_data
        if self.equity_data and len(self.equity_data) > 1:
            self.equity_curve_item.setData(y=self.equity_data, x=list(range(len(self.equity_data))))
            min_y = min(self.equity_data) * 0.99
            ground_data = np.full(len(self.equity_data), min_y)
            self.fill_line.setData(y=ground_data, x=list(range(len(self.equity_data))))
            self.plot_widget.getPlotItem().setYRange(min_y, max(self.equity_data))
        elif self.equity_data:
             self.equity_curve_item.setData(y=self.equity_data, x=list(range(len(self.equity_data))))

    def add_point_to_equity_curve(self, new_balance_point):
        """Adds a single new point to the chart."""
        self.equity_data.append(new_balance_point)
        if len(self.equity_data) > 1:
            min_y = min(self.equity_data) * 0.99
            self.equity_curve_item.setData(y=self.equity_data, x=list(range(len(self.equity_data))))
            ground_data = np.full(len(self.equity_data), min_y)
            self.fill_line.setData(y=ground_data, x=list(range(len(self.equity_data))))
            self.plot_widget.getPlotItem().setYRange(min_y, max(self.equity_data))
        else:
             self.equity_curve_item.setData(y=self.equity_data, x=list(range(len(self.equity_data))))

    def update_service_status(self, service_name, status):
        card_map = {'telegram': self.telegram_card, 'gpt': self.gpt_card, 'mt5': self.mt5_card}
        card_widget = card_map.get(service_name)
        if not card_widget: return
        
        card = card_widget.findChild(QFrame)
        if hasattr(card, 'status_label'):
            card.status_label.setText(status.upper())
            object_name = "CardStatusDisconnected"
            if status == 'CONNECTED': object_name = "CardStatusConnected"
            elif status == 'ERROR': object_name = "CardStatusError"
            card.status_label.setObjectName(object_name)
            card.status_label.style().unpolish(card.status_label)
            card.status_label.style().polish(card.status_label)