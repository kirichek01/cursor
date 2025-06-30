from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, 
    QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, QPushButton, QCheckBox
)
from PySide6.QtGui import QColor
import qtawesome as qta
ACCENT_COLOR = "#6C5ECF"

# Reusing the card class concept
class ParserCard(QFrame):
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

class ParserView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("parserView")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # --- Top section with title and buttons ---
        top_layout = QHBoxLayout()
        title = QLabel("Signal Parser"); title.setStyleSheet("font-size: 28px; font-weight: bold;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        self.add_channel_button = QPushButton("➕ Add Channel")
        self.remove_channel_button = QPushButton("➖ Remove Channel")
        top_layout.addWidget(self.add_channel_button)
        top_layout.addWidget(self.remove_channel_button)
        main_layout.addLayout(top_layout)

        # --- Stats Cards ---
        cards_layout = QHBoxLayout()
        cards_layout.addWidget(ParserCard("Signals Today", "12", "fa5s.bell"))
        cards_layout.addWidget(ParserCard("Active Channels", "5", "fa5s.broadcast-tower"))
        cards_layout.addStretch()
        main_layout.addLayout(cards_layout)

        # --- Channels Table ---
        table_label = QLabel("Monitored Channels")
        main_layout.addWidget(table_label)
        
        self.channels_table = QTableWidget()
        self.channels_table.setObjectName("channelsTable")
        self.channels_table.setColumnCount(3)
        self.channels_table.setHorizontalHeaderLabels(["Active", "Channel Name", "Default Symbol"])
        header = self.channels_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.channels_table.setShowGrid(False)
        main_layout.addWidget(self.channels_table, 1)

    def update_channels_table(self, channels_data):
        self.channels_table.setRowCount(len(channels_data))
        for row, (channel_id, data) in enumerate(channels_data.items()):
            active_checkbox = QCheckBox()
            active_checkbox.setChecked(data.get('active', True))
            active_checkbox.setProperty("channel_id", channel_id)
            # We would connect its stateChanged signal here or in main window
            
            self.channels_table.setCellWidget(row, 0, active_checkbox)
            self.channels_table.setItem(row, 1, QTableWidgetItem(data.get('name')))
            self.channels_table.setItem(row, 2, QTableWidgetItem(data.get('default_symbol')))

    def get_selected_channel_id(self):
        current_row = self.channels_table.currentRow()
        if current_row < 0:
            return None
        # Assuming channel ID is stored in the checkbox property of the first column
        checkbox_widget = self.channels_table.cellWidget(current_row, 0)
        if checkbox_widget:
            return checkbox_widget.property("channel_id")
        return None 