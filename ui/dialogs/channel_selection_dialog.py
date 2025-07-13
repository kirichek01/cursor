from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox

class ChannelSelectionDialog(QDialog):
    def __init__(self, channels, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Channel")
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        for channel in channels:
            self.list_widget.addItem(channel['name'])
        layout.addWidget(self.list_widget)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.channels = channels
        self.selected_channel = None

    def accept(self):
        if self.list_widget.currentItem():
            selected_index = self.list_widget.currentRow()
            self.selected_channel = self.channels[selected_index]
        super().accept() 