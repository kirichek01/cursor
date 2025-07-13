from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QGridLayout, QScrollArea, QFrame, QCheckBox
)
from PySide6.QtCore import Qt

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsView")

        # --- Main Layout with Scroll Area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(20)
        
        # --- Header ---
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title)

        # --- Settings Sections ---
        self.telegram_settings = self._create_group("Telegram API")
        self._add_setting(self.telegram_settings, "API ID", "telegram_api_id")
        self._add_setting(self.telegram_settings, "API Hash", "telegram_api_hash")
        self._add_setting(self.telegram_settings, "Session File", "telegram_session_file", is_file=True)
        layout.addWidget(self.telegram_settings)

        self.gpt_settings = self._create_group("GPT (for Parser)")
        self._add_setting(self.gpt_settings, "API Key", "gpt_api_key", is_password=True)
        layout.addWidget(self.gpt_settings)

        self.mt5_settings = self._create_group("MetaTrader 5")
        self._add_setting(self.mt5_settings, "Terminal Path", "mt5_path", is_file=True)
        self._add_setting(self.mt5_settings, "Login", "mt5_login")
        self._add_setting(self.mt5_settings, "Password", "mt5_password", is_password=True)
        self._add_setting(self.mt5_settings, "Server", "mt5_server")
        layout.addWidget(self.mt5_settings)
        
        self.trading_settings = self._create_group("Trading Parameters")
        self._add_setting(self.trading_settings, "Risk per Trade (%)", "trading_risk")
        self._add_setting(self.trading_settings, "Default Lot Size", "trading_lot_size")
        self._add_setting(self.trading_settings, "Breakeven Enabled", "breakeven_enabled", is_checkbox=True)
        layout.addWidget(self.trading_settings)

        # --- New SmartMoney Section ---
        self.sm_settings = self._create_group("SmartMoney Bot")
        self._add_setting(self.sm_settings, "Risk Percentage", "sm_risk_pct", default="0.01")
        self._add_setting(self.sm_settings, "Slippage", "sm_slippage", default="0.0002")
        self._add_setting(self.sm_settings, "Commission", "sm_commission", default="0.0001")
        self._add_setting(self.sm_settings, "Stop Loss (pips)", "sm_sl_pips", default="30")
        self._add_setting(self.sm_settings, "TP Ratio", "sm_tp_ratio", default="2.0")
        layout.addWidget(self.sm_settings)

        layout.addStretch()
        
        # --- Save Button ---
        self.save_button = QPushButton("💾 Save All Settings")
        self.save_button.setObjectName("saveButton")
        self.save_button.setFixedHeight(45)
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _create_group(self, title_text):
        group = QFrame()
        group.setObjectName("settingsGroup")
        group.setStyleSheet("QFrame#settingsGroup { background-color: #252836; border-radius: 15px; }")
        
        self.group_layout = QVBoxLayout(group)
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        self.group_layout.addWidget(title)
        return group

    def _add_setting(self, group_widget, label_text, setting_key, is_password=False, is_file=False, is_checkbox=False, default=None):
        layout = group_widget.layout()
        row = QHBoxLayout()
        row.setContentsMargins(10, 5, 10, 5)

        label = QLabel(label_text)
        label.setFixedWidth(150)
        
        if is_checkbox:
            widget = QCheckBox()
        else:
            widget = QLineEdit()
            if is_password:
                widget.setEchoMode(QLineEdit.EchoMode.Password)
            if default:
                widget.setPlaceholderText(str(default))

        # Store widget in a dictionary for easy access
        if not hasattr(self, 'inputs'):
            self.inputs = {}
        self.inputs[setting_key] = widget
        
        row.addWidget(label)
        row.addWidget(widget)
        
        if is_file:
            browse_button = QPushButton("Browse...")
            row.addWidget(browse_button)
            # You would connect this button to a file dialog
            
        layout.addLayout(row)

    def load_settings(self, settings_data):
        """Populates the input fields with data from the config."""
        for key, widget in self.inputs.items():
            path = key.split('_', 1)
            section = path[0]
            config_key = path[1]
            
            # Special handling for "sm" section
            if section == "sm":
                section_data = settings_data.get("smartmoney", {})
            else:
                section_data = settings_data.get(section, {})

            value = section_data.get(config_key)
            
            if isinstance(widget, QLineEdit):
                widget.setText(str(value) if value is not None else "")
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))

    def collect_settings(self):
        """Gathers all values from the input fields."""
        settings = {}
        for key, widget in self.inputs.items():
            path = key.split('_', 1)
            section = path[0]
            config_key = path[1]
            
            # Special handling for "sm" section
            if section == "sm":
                section = "smartmoney"

            if section not in settings:
                settings[section] = {}
            
            if isinstance(widget, QLineEdit):
                # Save only if there is text, otherwise default will be used from config
                if widget.text():
                    settings[section][config_key] = widget.text()
            elif isinstance(widget, QCheckBox):
                settings[section][config_key] = widget.isChecked()
        return settings 