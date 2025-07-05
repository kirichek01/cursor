from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QScrollArea, QCheckBox, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

class SettingsView(QWidget):
    def __init__(self, settings_data, parent=None):
        super().__init__(parent)
        self.settings = settings_data
        self._setup_ui()
        self._load_settings_to_ui()

    def _apply_shadow(self, widget):
        """Вспомогательная функция для добавления эффекта тени к виджету."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 100))
        widget.setGraphicsEffect(shadow)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("ScrollArea")
        main_layout.addWidget(scroll_area)
        
        container = QWidget()
        scroll_area.setWidget(container)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 20, 25, 20)
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        container_layout.addWidget(self._create_telegram_card())
        container_layout.addWidget(self._create_gpt_card())
        container_layout.addWidget(self._create_mt5_card())
        container_layout.addWidget(self._create_trading_card())
        container_layout.addWidget(self._create_breakeven_card())
        container_layout.addWidget(self._create_ai_trader_card())

    def _create_telegram_card(self):
        card = QFrame()
        card.setObjectName("InfoCard")
        self._apply_shadow(card)
        layout = QGridLayout(card)
        layout.addWidget(QLabel("Telegram Settings", objectName="CardTitle"), 0, 0, 1, 2)
        self.api_id_input = QLineEdit()
        self.api_hash_input = QLineEdit()
        self.session_file_input = QLineEdit()
        self.import_session_btn = QPushButton("Import Session File")
        self.import_session_btn.setObjectName("SecondaryButton")
        self._apply_shadow(self.import_session_btn)
        layout.addWidget(QLabel("API ID:"), 1, 0)
        layout.addWidget(self.api_id_input, 1, 1)
        layout.addWidget(QLabel("API Hash:"), 2, 0)
        layout.addWidget(self.api_hash_input, 2, 1)
        layout.addWidget(QLabel("Session File Name:"), 3, 0)
        layout.addWidget(self.session_file_input, 3, 1)
        layout.addWidget(self.import_session_btn, 4, 1)
        return card

    def _create_gpt_card(self):
        card = QFrame()
        card.setObjectName("InfoCard")
        self._apply_shadow(card)
        layout = QGridLayout(card)
        layout.addWidget(QLabel("GPT (Gemini) Settings", objectName="CardTitle"), 0, 0, 1, 2)
        self.gpt_api_key_input = QLineEdit()
        self.gpt_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.test_gpt_key_btn = QPushButton("Test Key")
        self.test_gpt_key_btn.setObjectName("SecondaryButton")
        self._apply_shadow(self.test_gpt_key_btn)
        layout.addWidget(QLabel("API Key:"), 1, 0)
        layout.addWidget(self.gpt_api_key_input, 1, 1)
        layout.addWidget(self.test_gpt_key_btn, 2, 1)
        return card

    def _create_mt5_card(self):
        card = QFrame()
        card.setObjectName("InfoCard")
        self._apply_shadow(card)
        layout = QGridLayout(card)
        layout.addWidget(QLabel("MetaTrader 5 Settings", objectName="CardTitle"), 0, 0, 1, 2)
        self.mt5_path_input = QLineEdit()
        self.mt5_login_input = QLineEdit()
        self.mt5_password_input = QLineEdit()
        self.mt5_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.mt5_server_input = QLineEdit()
        layout.addWidget(QLabel("Terminal Path:"), 1, 0)
        layout.addWidget(self.mt5_path_input, 1, 1)
        layout.addWidget(QLabel("Login:"), 2, 0)
        layout.addWidget(self.mt5_login_input, 2, 1)
        layout.addWidget(QLabel("Password:"), 3, 0)
        layout.addWidget(self.mt5_password_input, 3, 1)
        layout.addWidget(QLabel("Server:"), 4, 0)
        layout.addWidget(self.mt5_server_input, 4, 1)
        return card
        
    def _create_trading_card(self):
        card = QFrame()
        card.setObjectName("InfoCard")
        self._apply_shadow(card)
        layout = QGridLayout(card)
        layout.addWidget(QLabel("Signal Trading Settings", objectName="CardTitle"), 0, 0, 1, 2)
        self.lot_per_tp_input = QLineEdit()
        layout.addWidget(QLabel("Lot Size per Take Profit:"), 1, 0)
        layout.addWidget(self.lot_per_tp_input, 1, 1)
        return card

    def _create_breakeven_card(self):
        card = QFrame()
        card.setObjectName("InfoCard")
        self._apply_shadow(card)
        layout = QGridLayout(card)
        layout.addWidget(QLabel("Risk Management (for Signals)", objectName="CardTitle"), 0, 0, 1, 2)
        self.enable_breakeven_checkbox = QCheckBox("Enable Move to Breakeven after TP1")
        self.pips_for_breakeven_input = QLineEdit()
        layout.addWidget(self.enable_breakeven_checkbox, 1, 0, 1, 2)
        layout.addWidget(QLabel("Pips from entry for new SL:"), 2, 0)
        layout.addWidget(self.pips_for_breakeven_input, 2, 1)
        return card

    def _create_ai_trader_card(self):
        card = QFrame()
        card.setObjectName("InfoCard")
        self._apply_shadow(card)
        layout = QGridLayout(card)
        layout.addWidget(QLabel("AI Assistant Trader", objectName="CardTitle"), 0, 0, 1, 2)
        self.enable_signal_parser_checkbox = QCheckBox("Enable Telegram Signal Parser Module")
        self.enable_ai_trader_checkbox = QCheckBox("Enable AI Assistant Trader Module")
        self.ai_lot_size_input = QLineEdit()
        layout.addWidget(self.enable_signal_parser_checkbox, 1, 0, 1, 2)
        layout.addWidget(self.enable_ai_trader_checkbox, 2, 0, 1, 2)
        layout.addWidget(QLabel("Lot Size for AI Trades:"), 3, 0)
        layout.addWidget(self.ai_lot_size_input, 3, 1)
        return card

    def _load_settings_to_ui(self):
        tg_settings = self.settings.get('telegram', {})
        self.api_id_input.setText(str(tg_settings.get('api_id', '')))
        self.api_hash_input.setText(tg_settings.get('api_hash', ''))
        self.session_file_input.setText(tg_settings.get('session_file', 'userbot.session'))
        
        gpt_settings = self.settings.get('gpt', {})
        self.gpt_api_key_input.setText(gpt_settings.get('api_key', ''))

        mt5_settings = self.settings.get('mt5', {})
        self.mt5_path_input.setText(mt5_settings.get('path', ''))
        self.mt5_login_input.setText(str(mt5_settings.get('login', '')))
        self.mt5_password_input.setText(mt5_settings.get('password', ''))
        self.mt5_server_input.setText(mt5_settings.get('server', ''))
        
        trading_settings = self.settings.get('trading', {})
        self.lot_per_tp_input.setText(str(trading_settings.get('lot_per_tp', 0.01)))
        
        be_settings = self.settings.get('breakeven', {})
        self.enable_breakeven_checkbox.setChecked(be_settings.get('enabled', True))
        self.pips_for_breakeven_input.setText(str(be_settings.get('pips', 5)))

        parser_settings = self.settings.get('signal_parser', {})
        self.enable_signal_parser_checkbox.setChecked(parser_settings.get('enabled', True))
        
        ai_settings = self.settings.get('ai_trader', {})
        self.enable_ai_trader_checkbox.setChecked(ai_settings.get('enabled', False))
        self.ai_lot_size_input.setText(str(ai_settings.get('lot_size', 0.01)))

    def collect_settings_from_ui(self):
        def to_int(text): return int(text) if text.strip().isdigit() else 0
        def to_float(text, default=0.01):
            try: return float(text.strip().replace(',', '.'))
            except (ValueError, TypeError): return default

        # Сохраняем последнее состояние переключателя live_trading
        live_trading_state = self.settings.get('ai_trader', {}).get('live_trading', False)

        return {
            'telegram': {'api_id': to_int(self.api_id_input.text()), 'api_hash': self.api_hash_input.text(), 'session_file': self.session_file_input.text()},
            'gpt': {'api_key': self.gpt_api_key_input.text()},
            'mt5': {'path': self.mt5_path_input.text(), 'login': to_int(self.mt5_login_input.text()), 'password': self.mt5_password_input.text(), 'server': self.mt5_server_input.text()},
            'trading': {'lot_per_tp': to_float(self.lot_per_tp_input.text())},
            'breakeven': {'enabled': self.enable_breakeven_checkbox.isChecked(), 'pips': to_int(self.pips_for_breakeven_input.text())},
            'signal_parser': {'enabled': self.enable_signal_parser_checkbox.isChecked()},
            'ai_trader': {'enabled': self.enable_ai_trader_checkbox.isChecked(), 'lot_size': to_float(self.ai_lot_size_input.text()), 'live_trading': live_trading_state}
        }