from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, QAbstractItemView
)

class HistoryView(QWidget):
    """
    The view for the "History" tab.
    This version includes a critical fix for the table update logic.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        controls_layout = QHBoxLayout()
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setObjectName("SecondaryButton")
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(12)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Timestamp", "Channel", "Original Message", "Symbol", "Order Type", 
            "Entry", "SL", "TPs", "Status", "MT5 Tickets", "Comment"
        ])
        
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.verticalHeader().setVisible(False)
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        main_layout.addWidget(self.history_table)

    def update_table(self, data):
        """
        Populates the history table with data from the database.
        This version uses a more robust method of populating cells by index.
        """
        self.history_table.setRowCount(0)
        if not data:
            return
            
        self.history_table.setRowCount(len(data))
        
        for row_index, row_data in enumerate(data):
            # A sqlite3.Row object can be iterated like a tuple, which is reliable.
            # We iterate through each piece of data in the row.
            for col_index, cell_data in enumerate(row_data):
                # Ensure we handle None values gracefully before converting to string
                item_text = str(cell_data) if cell_data is not None else ""
                item = QTableWidgetItem(item_text)
                self.history_table.setItem(row_index, col_index, item)
