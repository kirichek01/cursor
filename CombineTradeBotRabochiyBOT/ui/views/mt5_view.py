from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTextEdit
)
from PySide6.QtGui import QColor

class MT5View(QWidget):
    """
    The view for the "MT5" tab.
    Displays connection status, account information, and a log of MT5 events.
    This fulfills the UI requirements for MT5 monitoring from the technical specification.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the layout and widgets for the MT5 view."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # --- Top controls and status ---
        main_layout.addLayout(self._create_status_layout())
        
        # --- Account Info Card ---
        main_layout.addWidget(self._create_info_card())
        
        # --- Log Area ---
        main_layout.addWidget(self._create_log_card())
        
        main_layout.addStretch()

    def _create_status_layout(self):
        """Creates the top layout with the status label and connect button."""
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("DISCONNECTED")
        self.status_label.setObjectName("CardStatusDisconnected") # Default status style
        
        self.connect_button = QPushButton("CONNECT TO MT5")
        self.connect_button.setObjectName("PrimaryButton")
        
        status_layout.addWidget(QLabel("Connection Status:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.connect_button)
        
        return status_layout

    def _create_info_card(self):
        """Creates the card for displaying account information."""
        card = QFrame()
        card.setObjectName("InfoCard")
        layout = QGridLayout(card)
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("Account Information", objectName="CardTitle"), 0, 0, 1, 2)
        
        # Create labels for each piece of info
        self.login_label = QLabel("N/A")
        self.server_label = QLabel("N/A")
        self.balance_label = QLabel("N/A")
        self.equity_label = QLabel("N/A")
        self.margin_label = QLabel("N/A")

        layout.addWidget(QLabel("Login:"), 1, 0)
        layout.addWidget(self.login_label, 1, 1)
        layout.addWidget(QLabel("Server:"), 2, 0)
        layout.addWidget(self.server_label, 2, 1)
        layout.addWidget(QLabel("Balance:"), 3, 0)
        layout.addWidget(self.balance_label, 3, 1)
        layout.addWidget(QLabel("Equity:"), 4, 0)
        layout.addWidget(self.equity_label, 4, 1)
        layout.addWidget(QLabel("Margin:"), 5, 0)
        layout.addWidget(self.margin_label, 5, 1)
        
        return card

    def _create_log_card(self):
        """Creates the card for displaying logs."""
        card = QFrame()
        card.setObjectName("InfoCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("MT5 Event Log", objectName="CardTitle"))
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setObjectName("LogArea") # For specific styling if needed
        layout.addWidget(self.log_area)
        
        return card

    def update_status(self, status_text, is_connected):
        """Updates the status label text and style."""
        self.status_label.setText(status_text.upper())
        if is_connected:
            self.status_label.setObjectName("CardStatusConnected")
            self.connect_button.setText("REFRESH INFO")
            self.connect_button.setObjectName("SecondaryButton")
        else:
            self.status_label.setObjectName("CardStatusDisconnected")
            self.connect_button.setText("CONNECT TO MT5")
            self.connect_button.setObjectName("PrimaryButton")
            
        # Re-apply stylesheet to update the objectName change
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.connect_button.style().unpolish(self.connect_button)
        self.connect_button.style().polish(self.connect_button)

    def update_account_info(self, info_dict):
        """Populates the info card with data from the MT5 account."""
        if info_dict:
            self.login_label.setText(str(info_dict.get('login', 'N/A')))
            self.server_label.setText(str(info_dict.get('server', 'N/A')))
            self.balance_label.setText(f"{info_dict.get('balance', 0.0):.2f} {info_dict.get('currency', '')}")
            self.equity_label.setText(f"{info_dict.get('equity', 0.0):.2f}")
            self.margin_label.setText(f"{info_dict.get('margin', 0.0):.2f}")
        else:
            # Clear fields if info is not available
            self.login_label.setText("N/A")
            self.server_label.setText("N/A")
            self.balance_label.setText("N/A")
            self.equity_label.setText("N/A")
            self.margin_label.setText("N/A")

    def add_log_message(self, message, level="INFO"):
        """Adds a new message to the log area with appropriate color."""
        color = "white"
        if level == "ERROR":
            color = "#ff5555" # Red
        elif level == "SUCCESS":
            color = "#50fa7b" # Green
        
        log_entry = f'<p style="color:{color}; margin:0;">{message}</p>'
        self.log_area.append(log_entry)
