import sys
import os
import json
import shutil
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QMessageBox, QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt, QSize, QThread, Slot, QObject, Signal
from PySide6.QtGui import QIcon, QPixmap
import qtawesome as qta

# Import all backend and UI components
from core.database_service import DatabaseService
from core.gpt_service import GptService
from core.telegram_service import TelegramService
from core.signal_processor import SignalProcessor
# MT5 and TradeManager are disabled on non-Windows platforms
try:
    from core.mt5_service import MT5Service
    from core.trade_manager_service import TradeManagerService
    IS_MACOS = False
except ImportError:
    IS_MACOS = True
    MT5Service = None
    TradeManagerService = None

from ui.views.dashboard_view import DashboardView
from ui.views.smartmoney_view import SmartMoneyView
from ui.views.parser_view import ParserView
from ui.views.mt5_view import MT5View
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView
from ui.dialogs.channel_selection_dialog import ChannelSelectionDialog
from ui.theme import STYLESHEET, ACCENT_COLOR
from ui.widgets import BalanceCard, RecentSignalsWidget

# Import smc_bot functions
from sm_bot.smc_bot import load_mt5_data, generate_smc_features, run_strategy
from sm_bot.smc_runner import SmartMoneyWorker

class NavButton(QPushButton):
    """Custom button for the sidebar."""
    def __init__(self, text, icon_name):
        super().__init__()
        self.icon_name = icon_name
        self.setCheckable(True)
        self.setObjectName("navButton")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        self.indicator = QFrame(self)
        self.indicator.setObjectName("navIndicator")
        self.indicator.setFixedSize(6, 20)
        self.indicator.setStyleSheet("background-color: #6C5ECF; border-radius: 3px;")
        self.indicator.hide()
        
        self.icon_label = QLabel()
        self.text_label = QLabel(text)
        
        layout.addWidget(self.indicator)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label, 1) # Stretch text label

        self.setChecked(False) # Set initial state

    def setChecked(self, checked):
        super().setChecked(checked)
        self.indicator.setVisible(checked)
        icon_color = "white" if checked else "#8E8E93"
        self.icon_label.setPixmap(qta.icon(self.icon_name, color=icon_color).pixmap(QSize(20, 20)))
        
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("AppWindow")
        self.setWindowTitle("Combine Trade Bot")
        self.setGeometry(100, 100, 1440, 810)

        # --- Load Configs & App State ---
        self._load_configs()
        self.all_dialogs = []
        self.is_bot_running = False
        self.backend_services = {}
        self.sm_bot_thread = None
        self.sm_bot_worker = None
        self.is_sm_bot_running = False

        # --- Setup UI ---
        self._setup_ui()
        self.apply_styles()
        self._connect_signals()
        
        # Set initial view
        self.nav_buttons[0].setChecked(True)
        self._on_nav_button_clicked(0) # Ensure first page is loaded and icon is colored

    def _load_configs(self):
        self.settings = self._load_config("data/config.json")
        self.channels = self._load_config("data/channels.json", is_channels=True)

    def _setup_ui(self):
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)
        
        main_layout.addWidget(self._create_sidebar())
        
        # --- Center content with StackedWidget ---
        self.stacked_widget = QStackedWidget()
        self.dashboard_view = DashboardView()
        self.smartmoney_view = SmartMoneyView()
        self.parser_view = ParserView()
        self.mt5_view = MT5View()
        self.history_view = HistoryView()
        self.settings_view = SettingsView()
        
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.smartmoney_view)
        self.stacked_widget.addWidget(self.parser_view)
        self.stacked_widget.addWidget(self.mt5_view)
        self.stacked_widget.addWidget(self.history_view)
        self.stacked_widget.addWidget(self.settings_view)
        main_layout.addWidget(self.stacked_widget, 1)

        main_layout.addWidget(self._create_right_column())

    def _create_sidebar(self):
        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(240)
        layout = QVBoxLayout(sidebar); layout.setContentsMargins(10, 20, 10, 20); layout.setSpacing(5)

        logo_label = QLabel("Combine BOT"); logo_label.setObjectName("logo"); layout.addWidget(logo_label); layout.addSpacing(30)
        
        self.nav_buttons = []
        nav_data = [
            ("Dashboard", "fa5s.home"), ("SmartMoney", "fa5s.brain"), 
            ("Parser", "fa5s.rss"), ("MT5", "fa5s.chart-line"), 
            ("History", "fa5s.history"), ("Settings", "fa5s.cog")
        ]

        for i, (text, icon) in enumerate(nav_data):
            btn = NavButton(text, icon)
            btn.clicked.connect(lambda checked, index=i: self._on_nav_button_clicked(index))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        self.start_button = QPushButton("🚀 START BOT"); self.start_button.setObjectName("startButton"); self.start_button.setFixedHeight(50)
        layout.addWidget(self.start_button)
        return sidebar

    def _create_right_column(self):
        right_col = QFrame(); right_col.setObjectName("rightColumn"); right_col.setFixedWidth(320)
        layout = QVBoxLayout(right_col); layout.setContentsMargins(15, 20, 15, 20); layout.setSpacing(20)
        
        self.balance_card = BalanceCard()
        self.recent_signals_widget = RecentSignalsWidget()
        
        layout.addWidget(self.balance_card)
        layout.addWidget(self.recent_signals_widget, 1) # Растягиваем список
        
        return right_col

    def _connect_signals(self):
        self.start_button.clicked.connect(self.toggle_bot_state)
        self.settings_view.save_button.clicked.connect(self.save_settings)
        self.history_view.refresh_button.clicked.connect(self.refresh_history_tab)
        
        # Connect SmartMoney view buttons
        self.smartmoney_view.start_button.clicked.connect(self.start_sm_bot)
        self.smartmoney_view.stop_button.clicked.connect(self.stop_sm_bot)
        
        self.parser_view.add_channel_button.clicked.connect(self.show_add_channel_dialog)
        self.parser_view.remove_channel_button.clicked.connect(self.remove_selected_channel)

    def _on_nav_button_clicked(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            btn.setIcon(qta.icon(btn.icon_name, color='white' if i == index else 'grey'))
        
        # Load data for the selected tab
        if self.nav_buttons[index].text() == "History":
            self.refresh_history_tab()
        elif self.nav_buttons[index].text() == "Settings":
            self.settings_view.load_settings(self.settings)
        elif self.nav_buttons[index].text() == "Parser":
            self.parser_view.update_channels_table(self.channels)

    @Slot()
    def toggle_bot_state(self):
        if self.is_bot_running:
            self._stop_services()
        else:
            self._initialize_and_start_services()
            
    def _initialize_and_start_services(self):
        self.settings = self._load_config("data/config.json")
        db = DatabaseService()
        self.backend_services['db'] = db
        # self.dashboard_view.update_status('database', True)
        
        gpt = GptService(api_key=self.settings.get('gpt', {}).get('api_key'))
        # self.dashboard_view.update_status('parser', bool(gpt.api_key))

        # --- MT5 Service ---
        mt5 = None
        if not IS_MACOS and MT5Service:
            mt5 = MT5Service(**self.settings.get('mt5', {}))
            success, msg = mt5.initialize()
            # self.dashboard_view.update_status('mt5', success)
            if success:
                account_info = mt5.get_account_info()
                if account_info:
                    self.mt5_view.update_account_info(account_info)
            else:
                self.mt5_view.add_log_message(f"MT5 Connection Failed: {msg}", "ERROR")
            self.backend_services['mt5'] = mt5
        else:
            # self.dashboard_view.update_status('mt5', False)
            self.backend_services['mt5'] = None
        
        # --- Telegram and other services ---
        tg_cfg = self.settings.get('telegram', {})
        tg = TelegramService(f"data/{tg_cfg.get('session_file', 'userbot.session')}", tg_cfg.get('api_id'), tg_cfg.get('api_hash'))
        # tg.status_signal.connect(lambda s: self.dashboard_view.update_status('telegram', s == 'CONNECTED'))
        tg.dialogs_fetched_signal.connect(self.on_channels_fetched)

        processor = SignalProcessor(db, gpt, self.backend_services['mt5'], self.settings, self.channels)
        self.backend_services.update({'processor': processor, 'tg': tg})
        tg.new_message_signal.connect(processor.process_new_message)

        tg_thread = QThread(); tg.moveToThread(tg_thread); tg_thread.started.connect(tg.start); tg_thread.start()
        self.backend_services['tg_thread'] = tg_thread

        if not IS_MACOS and TradeManagerService:
            manager = TradeManagerService(db, self.backend_services['mt5'], self.settings)
            manager.log_signal.connect(self.mt5_view.add_log_message)
            manager_thread = QThread(); manager.moveToThread(manager_thread); manager_thread.started.connect(manager.start_monitoring); manager_thread.start()
            self.backend_services['manager'] = manager
            self.backend_services['manager_thread'] = manager_thread

        self.is_bot_running = True
        self.start_button.setText("🛑 STOP BOT")
        print("Services Initialized.")
        if not self.all_dialogs: tg.fetch_dialogs()

    def _stop_services(self):
        self.stop_sm_bot() # Also stop SM bot if main bot is stopped
        for name, service in self.backend_services.items():
            if isinstance(service, QThread):
                service.quit()
                service.wait(2000)
            elif hasattr(service, 'stop'):
                service.stop()
        self.backend_services = {}
        
        self.is_bot_running = False
        self.start_button.setText("🚀 START BOT")
        # for s in ['database', 'parser', 'mt5', 'telegram', 'smartmoney']: self.dashboard_view.update_status(s, False)
        print("All services stopped.")

    @Slot()
    def save_settings(self):
        new_settings = self.settings_view.collect_settings()
        for section, values in new_settings.items():
            self.settings.setdefault(section, {}).update(values)
        with open("data/config.json", "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)
        QMessageBox.information(self, "Success", "Settings saved. Restart the bot to apply all changes.")

    @Slot()
    def refresh_history_tab(self):
        db = self.backend_services.get('db')
        if not db and not self.is_bot_running:
            db = DatabaseService()
        if db:
            self.history_view.update_table(db.get_signal_history(limit=100))
        if not self.is_bot_running and db:
            db.close_connection()

    def start_sm_bot(self):
        if IS_MACOS and self.smartmoney_view.get_current_settings()['mode'] == 'live':
            QMessageBox.warning(self, "Compatibility Warning", "Live trading requires MT5 and cannot be run on macOS.")
            return
            
        settings = self.smartmoney_view.get_current_settings()
        
        self.sm_bot_thread = QThread()
        self.sm_bot_worker = SmartMoneyWorker(settings)
        self.sm_bot_worker.moveToThread(self.sm_bot_thread)
        
        # Connect signals
        self.sm_bot_worker.log.connect(self.smartmoney_view.add_log_message)
        self.sm_bot_worker.chart_data.connect(self.smartmoney_view.plot_chart)
        # self.sm_bot_worker.new_trade.connect(self.smartmoney_view.add_trade_to_table) # Example
        
        self.sm_bot_thread.started.connect(self.sm_bot_worker.run)
        self.sm_bot_worker.finished.connect(self.stop_sm_bot)
        
        self.sm_bot_thread.start()
        
        mode_text = "Live" if settings['mode'] == 'live' else 'Backtest'
        self.is_sm_bot_running = True
        self.smartmoney_view.start_button.setText(f"🧠 {mode_text} Running...")
        self.smartmoney_view.start_button.setEnabled(False)
        self.smartmoney_view.stop_button.setEnabled(True)
        # self.dashboard_view.update_status('smartmoney', True)

    def stop_sm_bot(self):
        if self.sm_bot_worker:
            self.sm_bot_worker.stop()
        if self.sm_bot_thread and self.sm_bot_thread.isRunning():
            self.sm_bot_thread.quit()
            self.sm_bot_thread.wait(1000)
        
        self.is_sm_bot_running = False
        self.smartmoney_view.start_button.setText("🚀 Run")
        self.smartmoney_view.start_button.setEnabled(True)
        self.smartmoney_view.stop_button.setEnabled(False)
        # self.dashboard_view.update_status('smartmoney', False)
        # Clean up references
        self.sm_bot_thread = None
        self.sm_bot_worker = None
        self.smartmoney_view.add_log_message("Backtest stopped by user.")

    @Slot(list)
    def on_channels_fetched(self, dialogs):
        self.all_dialogs = dialogs
        QMessageBox.information(self, "Success", f"Found {len(dialogs)} channels/chats.")

    @Slot()
    def show_add_channel_dialog(self):
        if not self.is_bot_running:
            QMessageBox.warning(self, "Bot Offline", "Please start the bot first.")
            return
        if not self.all_dialogs:
            QMessageBox.warning(self, "No Channels", "Channel list not fetched yet. Please wait.")
            return
        dialog = ChannelSelectionDialog(self.all_dialogs, self)
        if dialog.exec() and dialog.selected_channel:
            ch = dialog.selected_channel
            cid = str(ch['id'])
            if cid not in self.channels:
                self.channels[cid] = {"name": ch['name'], "active": True, "default_symbol": ""}
                self.save_channels_to_file()
                self.parser_view.update_channels_table(self.channels)

    def save_channels_to_file(self):
        with open("data/channels.json", "w", encoding="utf-8") as f:
            json.dump(self.channels, f, indent=4)
        if 'processor' in self.backend_services:
            self.backend_services['processor'].update_channels(self.channels)

    @Slot()
    def remove_selected_channel(self):
        cid = self.parser_view.get_selected_channel_id()
        if not cid:
            QMessageBox.warning(self, "Error", "Please select a channel to remove.")
            return
        if cid in self.channels:
            del self.channels[cid]
            self.save_channels_to_file()
            self.parser_view.update_channels_table(self.channels)

    def _load_config(self, path, is_channels=False):
        try:
            if not os.path.exists(path):
                # Create default config if it doesn't exist
                return {}
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Config Error", f"Failed to load {path}: {e}")
            return {}

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow#AppWindow { background-color: #0F172A; }
            QFrame#sidebar { background-color: #131B2B; }
            /* ... ALL other styles hardcoded here ... */
            #RightBalanceCard {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #E91E63, stop:1 #9C27B0);
                border-radius: 16px;
            }
        """)

    def closeEvent(self, event):
        self.stop_sm_bot()
        self._stop_services()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec()) 