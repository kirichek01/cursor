from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QWidget
from PySide6.QtGui import QColor, QPixmap, QLinearGradient, QBrush, QPalette
from PySide6.QtCore import Qt
import qtawesome as qta
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os

# No longer importing from theme.py
ACCENT_COLOR = "#6C5ECF" 

class StyledCard(QFrame):
    """A reusable styled card with an icon, title, and value."""
    def __init__(self, title, value, icon_path=None, parent=None):
        super().__init__(parent)
        self.setObjectName("infoCard")
        self.setMinimumHeight(120) # Ensure a minimum height
        layout = QHBoxLayout(self)
        
        icon_label = QLabel()
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        elif icon_path: # If path provided but not found, use a placeholder
            icon_label.setPixmap(qta.icon("fa5s.question-circle", color=ACCENT_COLOR).pixmap(32, 32))
        
        text_layout = QVBoxLayout()
        title_label = QLabel(title); title_label.setObjectName("cardTitle")
        self.value_label = QLabel(value); self.value_label.setObjectName("cardValue")
        text_layout.addWidget(title_label); text_layout.addWidget(self.value_label)
        
        layout.addWidget(icon_label); layout.addLayout(text_layout)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30); shadow.setXOffset(0); shadow.setYOffset(8); shadow.setColor(QColor(0,0,0,100))
        self.setGraphicsEffect(shadow)

class MplCanvas(FigureCanvas):
    """A Matplotlib canvas widget to embed in a PyQt6 application."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#252836') # Match widget color
        fig.patch.set_alpha(0) # Transparent background
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#252836') # Match widget color
        # Style axes
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.spines['left'].set_color('white')
        self.axes.spines['bottom'].set_color('white')
        super(MplCanvas, self).__init__(fig) 

class BalanceCard(QFrame):
    """The gradient balance card for the right column."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RightBalanceCard")
        self.setFixedHeight(150)
        
        layout = QVBoxLayout(self)
        label = QLabel("SmartMoney Balance"); label.setStyleSheet("font-size: 14px;")
        self.value_label = QLabel("$0.00"); self.value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        
        layout.addWidget(label)
        layout.addWidget(self.value_label)

class RecentSignalsWidget(QFrame):
    """Widget to display a list of recent signals, styled like WasteBank."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecentSignalsList")
        self.setProperty("class", "CardWidget") # Use setProperty
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Recent Signals</b>"))
        header_layout.addStretch()
        header_layout.addWidget(QLabel("<a href='#'>See All</a>")) # Placeholder link
        self.main_layout.addLayout(header_layout)

        # This layout will hold the signal items
        self.signals_list_layout = QVBoxLayout()
        self.main_layout.addLayout(self.signals_list_layout)
        self.main_layout.addStretch()

    def add_signal(self, icon_path, symbol, source):
        item = QWidget()
        layout = QHBoxLayout(item)
        icon = QLabel(); icon.setPixmap(QPixmap(icon_path).scaled(32,32))
        text = QLabel(f"<b>{symbol}</b><br><span style='color:#A0A0B0;'>{source}</span>")
        layout.addWidget(icon); layout.addWidget(text); layout.addStretch()
        self.signals_list_layout.addWidget(item) 