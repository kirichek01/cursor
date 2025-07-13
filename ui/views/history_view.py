from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt

class HistoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyView")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # --- Header ---
        header_layout = QHBoxLayout()
        title = QLabel("Trade History")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setObjectName("refreshButton") # Can be styled via QSS
        self.refresh_button.setFixedHeight(35)
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(header_layout)

        # --- History Table ---
        self.history_table = QTableWidget()
        self.history_table.setObjectName("historyTable")
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["ID", "Timestamp", "Symbol", "Type", "Price", "Source"])
        
        # Style the header
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Style the table
        self.history_table.setShowGrid(False)
        self.history_table.setAlternatingRowColors(True) # For better readability
        
        main_layout.addWidget(self.history_table)

    def update_table(self, data):
        """Populates the table with signal history data."""
        self.history_table.setRowCount(len(data))
        for row, record in enumerate(data):
            # Assuming record is a tuple/list in the order of headers
            self.history_table.setItem(row, 0, QTableWidgetItem(str(record[0]))) # ID
            self.history_table.setItem(row, 1, QTableWidgetItem(record[1])) # Timestamp
            self.history_table.setItem(row, 2, QTableWidgetItem(record[2])) # Symbol
            self.history_table.setItem(row, 3, QTableWidgetItem(record[3])) # Type
            self.history_table.setItem(row, 4, QTableWidgetItem(str(record[5]))) # Price
            self.history_table.setItem(row, 5, QTableWidgetItem(record[6])) # Source

            # Center align all items for a cleaner look
            for col in range(self.history_table.columnCount()):
                item = self.history_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 