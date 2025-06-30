import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import qtawesome as qta

# Import views and theme - we'll create/update these later
from ui.theme import STYLESHEET
from ui.views.dashboard_view import DashboardView
from ui.views.smartmoney_view import SmartMoneyView
from ui.views.parser_view import ParserView
from ui.views.mt5_view import MT5View
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView


class NavButton(QPushButton):
    """Custom button for the sidebar with an active state indicator."""
    def __init__(self, text, icon_name, parent=None):
        super().__init__(text, parent)
        self.icon_name = icon_name
        self.setIcon(qta.icon(self.icon_name, color='#8E8E93'))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setFixedHeight(45)

class RedesignedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Combine Trade Bot (Redesigned)")
        self.setGeometry(100, 100, 1440, 810)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(DashboardView())
        self.stacked_widget.addWidget(SmartMoneyView())
        self.stacked_widget.addWidget(ParserView())
        self.stacked_widget.addWidget(MT5View())
        self.stacked_widget.addWidget(HistoryView())
        self.stacked_widget.addWidget(SettingsView())
        
        main_layout.addWidget(self.stacked_widget)
        
        self.apply_styles()
        self.nav_buttons[0].setChecked(True) # Set Dashboard as active by default

    def _create_sidebar(self):
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(240)
        
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo_label = QLabel("Combine BOT")
        logo_label.setObjectName("logo")
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(30)
        
        self.nav_buttons = []
        nav_data = [
            ("Dashboard", "fa5s.home"),
            ("SmartMoney", "fa5s.brain"),
            ("Parser", "fa5s.rss"),
            ("MT5", "fa5s.chart-line"),
            ("History", "fa5s.history"),
            ("Settings", "fa5s.cog")
        ]

        for i, (text, icon) in enumerate(nav_data):
            btn = NavButton(text, icon)
            btn.clicked.connect(lambda checked, index=i: self._on_nav_button_clicked(index))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        
        # Start button placeholder
        self.start_button = QPushButton("🚀 START BOT")
        self.start_button.setObjectName("startButton") # For styling
        self.start_button.setFixedHeight(50)
        sidebar_layout.addWidget(self.start_button)
        
        return sidebar_frame

    def _on_nav_button_clicked(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            if i == index:
                btn.setIcon(qta.icon(btn.icon_name, color='white'))
            else:
                btn.setIcon(qta.icon(btn.icon_name, color='#8E8E93'))


    def apply_styles(self):
        # We will need to update theme.py for the new styles
        # For now, let's use the existing one and add some specific styles here
        self.setStyleSheet(STYLESHEET + """
            QFrame#sidebar {
                background-color: #252836;
            }
            QPushButton#navButton {
                background-color: transparent;
                color: #8E8E93;
                border: none;
                text-align: left;
                padding: 10px;
                font-size: 15px;
                border-radius: 8px;
            }
            QPushButton#navButton:hover {
                background-color: #3A3C4C;
                color: white;
            }
            QPushButton#navButton:checked {
                background-color: #2B2A3D;
                color: white;
                font-weight: bold;
                border-left: 3px solid #6C5ECF;
            }
            QLabel#logo {
                font-size: 22px;
                font-weight: bold;
                color: white;
                padding-bottom: 10px;
            }
            QPushButton#startButton {
                background-color: #6C5ECF;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 10px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedesignedMainWindow()
    window.show()
    sys.exit(app.exec()) 