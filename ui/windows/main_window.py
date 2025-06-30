import sys
import os
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QMessageBox
)
from PySide6.QtCore import QThread, Slot, Qt
from PySide6.QtGui import QIcon

from ui.theme import STYLESHEET, ACCENT_COLOR, TEXT_COLOR
from ui.views.dashboard_view import DashboardView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView
from ui.views.smartmoney_view import SmartMoneyView
from ui.views.parser_view import ParserView
from ui.views.mt5_view import MT5View
from core.database_service import DatabaseService
from core.gpt_service import GptService
from core.telegram_service import TelegramService
from core.signal_processor import SignalProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Combine Trade Bot")
        self.setGeometry(100, 100, 1440, 810)

        icon_path = "assets/app_icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.settings = self._load_config_file("data/config.json")
        self.channels = self._load_config_file("data/channels.json", is_channels=True)
        self.all_dialogs = []
        self.is_bot_running = False
        self.backend_services = {}
        
        self._setup_new_ui()
        self.apply_styles()
        self._connect_ui_signals()

        if not self.settings.get('telegram', {}).get('api_id'):
            self.switch_page('settings')
            QMessageBox.information(self, "Добро пожаловать!", "Пожалуйста, заполните все настройки.")

    def _load_config_file(self, path, is_channels=False):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                default = {"telegram":{},"gpt":{},"mt5":{},"trading":{},"breakeven":{},"signal_parser":{"enabled":True},"sm_bot":{"enabled":True}}
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=4)
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить {path}: {e}")
            return {}
            
    def _setup_new_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        self.main_content = QFrame()
        self.main_content.setObjectName("mainContent")
        main_content_layout = QVBoxLayout(self.main_content)
        
        self.stacked_widget = QStackedWidget()
        main_content_layout.addWidget(self.stacked_widget)

        self.dashboard_page = DashboardView()
        self.smartmoney_page = SmartMoneyView() 
        self.parser_page = ParserView()
        self.mt5_page = MT5View()
        self.history_page = HistoryView()
        self.settings_page = SettingsView()

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.smartmoney_page)
        self.stacked_widget.addWidget(self.parser_page)
        self.stacked_widget.addWidget(self.mt5_page)
        self.stacked_widget.addWidget(self.history_page)
        self.stacked_widget.addWidget(self.settings_page)
        
    def _create_sidebar(self):
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(220)
        
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo_label = QLabel("Combine BOT")
        logo_label.setObjectName("logo")
        logo_label.setFixedHeight(40)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(20)

        self.nav_buttons = {}
        nav_buttons_data = [
            ("dashboard", "Dashboard"), ("smartmoney", "SmartMoney"), 
            ("parser", "Parser"), ("mt5", "MT5"), ("history", "History"), ("settings", "Settings")
        ]
        
        for key, text in nav_buttons_data:
            button = QPushButton(text)
            button.setObjectName("navButton")
            button.setFixedHeight(45)
            button.clicked.connect(lambda checked, k=key: self.switch_page(k))
            sidebar_layout.addWidget(button)
            self.nav_buttons[key] = button

        sidebar_layout.addStretch()

        self.start_stop_button = QPushButton("🚀 START BOT")
        self.start_stop_button.setFixedHeight(45)
        self.start_stop_button.setStyleSheet(f"QPushButton{{background-color:{ACCENT_COLOR};color:{TEXT_COLOR};font-weight:bold;border-radius:8px;}}QPushButton:hover{{background-color:#5A4CAD;}}")
        sidebar_layout.addWidget(self.start_stop_button)
        
        self.nav_buttons["dashboard"].setProperty("active", True)
        return sidebar_frame
        
    def _connect_ui_signals(self):
        self.start_stop_button.clicked.connect(self.toggle_bot_state)
        self.history_page.refresh_button.clicked.connect(self.refresh_history_tab)
        self.settings_page.save_button.clicked.connect(self.save_settings)

    def _initialize_and_start_services(self):
        self.settings = self._load_config_file("data/config.json")
        
        db = DatabaseService()
        self.backend_services['db'] = db
        self.dashboard_page.update_status('database', True)
        
        gpt = GptService(api_key=self.settings.get('gpt', {}).get('api_key'))
        self.backend_services['gpt'] = gpt
        self.dashboard_page.update_status('parser', self.settings.get('signal_parser', {}).get('enabled'))

        self.dashboard_page.update_status('mt5', False)

        if self.settings.get('signal_parser', {}).get('enabled', True):
            processor = SignalProcessor(db, gpt, None, self.settings, self.channels)
            tg_cfg = self.settings.get('telegram', {})
            tg = TelegramService(f"data/{tg_cfg.get('session_file', 'userbot.session')}", tg_cfg.get('api_id'), tg_cfg.get('api_hash'))
            
            self.backend_services.update({'processor': processor, 'tg': tg})
            
            tg.new_message_signal.connect(processor.process_new_message)
            tg.status_signal.connect(lambda s: self.dashboard_page.update_status('telegram', s == 'CONNECTED'))
            
            tg_thread = QThread(); tg.moveToThread(tg_thread); tg_thread.started.connect(tg.start); tg_thread.start()
            self.backend_services.update({'tg_thread': tg_thread})
        
        self.dashboard_page.update_status('smartmoney', self.settings.get('sm_bot', {}).get('enabled'))
        self.is_bot_running = True
        self.start_stop_button.setText("🛑 STOP BOT")

    def _stop_services(self):
        for thr_name in ['tg_thread']:
            if thr_name in self.backend_services and self.backend_services[thr_name]:
                self.backend_services[thr_name].quit()
                self.backend_services[thr_name].wait(2000)

        for srv_name in ['tg', 'db']:
            if srv_name in self.backend_services and self.backend_services[srv_name]:
                service = self.backend_services[srv_name]
                if hasattr(service, 'stop'): service.stop()
                if hasattr(service, 'shutdown'): service.shutdown()
                if hasattr(service, 'close_connection'): service.close_connection()
        
        self.backend_services = {}
        self.is_bot_running = False
        self.start_stop_button.setText("🚀 START BOT")
        
        for status in ['mt5', 'parser', 'telegram', 'database', 'smartmoney']:
            self.dashboard_page.update_status(status, False)
        print("All services stopped.")

    def closeEvent(self, event):
        self._stop_services()
        event.accept()

    def switch_page(self, key):
        page_map = {"dashboard": 0, "smartmoney": 1, "parser": 2, "mt5": 3, "history": 4, "settings": 5}
        self.stacked_widget.setCurrentIndex(page_map[key])
        for btn_key, button in self.nav_buttons.items():
            is_active = btn_key == key
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

        if key == "history":
            self.refresh_history_tab()
        elif key == "settings":
            self.settings_page.load_settings(self.settings)

    def apply_styles(self):
        self.setStyleSheet(STYLESHEET)
        
    def toggle_bot_state(self):
        if self.is_bot_running:
            self._stop_services()
        else:
            self._initialize_and_start_services()

    @Slot()
    def refresh_history_tab(self):
        """Refreshes the trade history table."""
        db = None
        try:
            # Use an active DB service if bot is running, otherwise create a temporary one
            db = self.backend_services.get('db') if self.is_bot_running else DatabaseService()
            if db:
                history_data = db.get_signal_history(limit=200)
                self.history_page.update_table(history_data)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not fetch history: {e}")
        finally:
            # Close the connection only if it was a temporary instance
            if not self.is_bot_running and db and hasattr(db, 'close_connection'):
                db.close_connection()

    @Slot()
    def save_settings(self):
        """Saves all settings from the UI to the config file."""
        try:
            new_settings = self.settings_page.collect_settings()
            # It's better to merge with existing settings to not lose any unexposed config
            for section, values in new_settings.items():
                if section not in self.settings:
                    self.settings[section] = {}
                self.settings[section].update(values)
            
            with open("data/config.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            
            QMessageBox.information(self, "Success", "Settings have been saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())