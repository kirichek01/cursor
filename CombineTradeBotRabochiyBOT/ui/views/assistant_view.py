from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QDialog, QLineEdit, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt

class ChannelSelectionDialog(QDialog):
    """
    A dialog window with a search bar to find and select a channel
    from a large list of user's dialogs.
    """
    def __init__(self, all_dialogs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Channel for Parsing")
        self.setMinimumWidth(500)
        self.all_dialogs = all_dialogs
        self.selected_channel = None

        layout = QVBoxLayout(self)
        
        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search for a channel...")
        self.search_input.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_input)

        # List of channels
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Selected")
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.clicked.connect(self.accept_selection)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        layout.addLayout(button_layout)
        
        self.populate_list(self.all_dialogs)

    def populate_list(self, dialogs):
        """Fills the list widget with dialogs."""
        self.list_widget.clear()
        for dialog in dialogs:
            # We store the full dialog dict in the item itself
            item = QListWidgetItem(f"{dialog['name']} (ID: {dialog['id']})")
            item.setData(Qt.ItemDataRole.UserRole, dialog)
            self.list_widget.addItem(item)

    def filter_list(self, text):
        """Filters the list based on the search input text."""
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_text = item.text().lower()
            # Hide or show item based on whether it contains the search text
            item.setHidden(text not in item_text)

    def accept_selection(self):
        """Sets the selected channel and closes the dialog."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items: return
        self.selected_channel = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.accept()


class AssistantView(QWidget):
    """
    Redesigned view for the 'Assistant' tab.
    Displays only the configured channels and provides a user-friendly
    dialog with search to add new channels.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        controls_card = QFrame()
        controls_card.setObjectName("InfoCard")
        controls_layout = QHBoxLayout(controls_card)
        
        self.add_channel_button = QPushButton("➕ Add Channel...")
        self.add_channel_button.setObjectName("PrimaryButton")
        
        self.remove_channel_button = QPushButton("❌ Remove Selected")
        self.remove_channel_button.setObjectName("SecondaryButton")

        controls_layout.addWidget(QLabel("Manage channels for parsing:"))
        controls_layout.addStretch()
        controls_layout.addWidget(self.add_channel_button)
        controls_layout.addWidget(self.remove_channel_button)
        main_layout.addWidget(controls_card)

        self.channels_table = QTableWidget()
        self.channels_table.setColumnCount(3)
        self.channels_table.setHorizontalHeaderLabels(["Parse", "Channel Name", "Channel ID"])
        
        header = self.channels_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.channels_table.verticalHeader().setVisible(False)
        self.channels_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.channels_table)

    def update_channels_table(self, configured_channels):
        """
        Populates the table with ONLY the channels configured for parsing.
        """
        for row in range(self.channels_table.rowCount()):
            cell_widget = self.channels_table.cellWidget(row, 0)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox:
                    try: checkbox.stateChanged.disconnect()
                    except RuntimeError: pass

        self.channels_table.setRowCount(0)
        if not configured_channels: return
        self.channels_table.setRowCount(len(configured_channels))
        
        for row, (channel_id, info) in enumerate(configured_channels.items()):
            checkbox = QCheckBox()
            checkbox.setChecked(info.get("active", True))
            checkbox.setProperty("channel_id", channel_id)
            checkbox.setProperty("channel_name", info.get("name", "N/A"))
            cell_widget = QWidget()
            chk_layout = QHBoxLayout(cell_widget); chk_layout.addWidget(checkbox)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter); chk_layout.setContentsMargins(0, 0, 0, 0)
            self.channels_table.setCellWidget(row, 0, cell_widget)
            self.channels_table.setItem(row, 1, QTableWidgetItem(info.get("name", "N/A")))
            self.channels_table.setItem(row, 2, QTableWidgetItem(str(channel_id)))

    def get_selected_channel_id(self):
        selected_rows = self.channels_table.selectionModel().selectedRows()
        if not selected_rows: return None
        id_item = self.channels_table.item(selected_rows[0].row(), 2)
        return id_item.text() if id_item else None
