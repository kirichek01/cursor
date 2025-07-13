import sys
import os
import json
import shutil
from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog, QCheckBox
from PySide6.QtCore import QThread, Slot, Qt
from PySide6.QtGui import QIcon

from core.database_service import DatabaseService
from core.gpt_service import GptService
from core.mt5_service import MT5Service
from core.telegram_service import TelegramService
from core.signal_processor import SignalProcessor
from core.trade_manager_service import TradeManagerService
from core.ai_trader_service import AITraderService
from .views.main_view import MainView
from .views.settings_view import SettingsView
from .views.history_view import HistoryView
from .views.mt5_view import MT5View
from .views.ai_bot_view import AIBotView
from .views.assistant_view import AssistantView, ChannelSelectionDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Combine Trade Bot by Kirichek")
        self.setGeometry(100, 100, 1100, 800)

        icon_path = "assets/app_icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.settings = self._load_config_file("data/config.json")
        self.channels = self._load_config_file("data/channels.json", is_channels=True)
        self.all_dialogs = []
        self.is_bot_running = False
        self.is_ai_trader_running = False
        self.backend_services = {}
        self.ai_trader_thread = None
        self.ai_log_history = [] # Хранилище для логов AI
        self._setup_ui()
        self._connect_ui_signals()
        self.apply_theme()
        self.refresh_history_tab()
        self.load_and_plot_equity_history()
        if not self.settings.get('telegram', {}).get('api_id'):
            self.tabs.setCurrentWidget(self.settings_view)
            QMessageBox.information(self, "Добро пожаловать!", "Пожалуйста, заполните все настройки и нажмите 'SAVE' на главной вкладке.")

    def _load_config_file(self, path, is_channels=False):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                default = {} if is_channels else {
                    "telegram": {}, "gpt": {}, "mt5": {}, "trading": {}, "breakeven": {},
                    "signal_parser": {"enabled": True},
                    "ai_trader": {"enabled": False, "lot_size": 0.01, "live_trading": False}
                }
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=4)
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить {path}: {e}")
            return {}

    def _setup_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.main_view = MainView()
        self.assistant_view = AssistantView()
        self.history_view = HistoryView()
        self.mt5_view = MT5View()
        self.ai_bot_view = AIBotView()
        self.settings_view = SettingsView(self.settings)
        self.tabs.addTab(self.main_view, "Main")
        self.tabs.addTab(self.ai_bot_view, "AI Assistant")
        self.tabs.addTab(self.history_view, "History")
        self.tabs.addTab(self.mt5_view, "MT5")
        self.tabs.addTab(self.assistant_view, "Channels")
        self.tabs.addTab(self.settings_view, "Settings")
        self.assistant_view.update_channels_table(self.channels)
        self._connect_channel_checkboxes()
        is_live = self.settings.get('ai_trader', {}).get('live_trading', False)
        self.ai_bot_view.live_trading_switch.setChecked(is_live)

    def _connect_ui_signals(self):
        self.main_view.start_stop_button.clicked.connect(self.toggle_bot_state)
        self.main_view.save_button.clicked.connect(self.save_all_settings)
        self.settings_view.test_gpt_key_btn.clicked.connect(self.test_gpt_key)
        self.settings_view.import_session_btn.clicked.connect(self.import_session_file)
        self.history_view.refresh_button.clicked.connect(self.refresh_history_tab)
        self.mt5_view.connect_button.clicked.connect(self.connect_or_refresh_mt5)
        self.assistant_view.add_channel_button.clicked.connect(self.show_add_channel_dialog)
        self.assistant_view.remove_channel_button.clicked.connect(self.remove_selected_channel)
        self.ai_bot_view.start_stop_button.clicked.connect(self.toggle_ai_trader_state)
        self.ai_bot_view.live_trading_switch.stateChanged.connect(self.on_live_trading_toggled)
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def apply_theme(self):
        try:
            with open("assets/style.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            print("Stylesheet 'assets/style.qss' not found.")

    def load_and_plot_equity_history(self):
        stats_path = "data/ai_stats_history.json"
        history_data = []
        if os.path.exists(stats_path):
            try:
                with open(stats_path, 'r') as f:
                    history_records = json.load(f)
                    history_data = [record['balance'] for record in history_records]
            except (json.JSONDecodeError, KeyError):
                history_data = []
        self.main_view.update_equity_curve(history_data)

    @Slot()
    def on_tab_changed(self, index):
        """Вызывается при переключении на другую вкладку для обновления лога."""
        if self.tabs.widget(index) == self.ai_bot_view:
            self.ai_bot_view.repopulate_log(self.ai_log_history)

    @Slot(str, str)
    def _handle_ai_log(self, message, level):
        """Сохраняет лог AI в историю и отправляет его в UI, если вкладка активна."""
        self.ai_log_history.append((message, level))
        if len(self.ai_log_history) > 500:
            self.ai_log_history.pop(0)
        
        if self.tabs.currentWidget() == self.ai_bot_view:
            self.ai_bot_view.add_log_message(message, level)

    @Slot()
    def on_live_trading_toggled(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        if 'ai_trader' not in self.settings: self.settings['ai_trader'] = {}
        self.settings['ai_trader']['live_trading'] = is_checked
        self.ai_bot_view.add_log_message(f"Live Trading has been {'ENABLED' if is_checked else 'DISABLED'}.", "SUCCESS" if is_checked else "ERROR")

    @Slot(dict)
    def on_ai_stats_updated(self, stats_data):
        self.ai_bot_view.update_statistics(stats_data)
        self.main_view.add_point_to_equity_curve(stats_data.get('balance'))

    @Slot()
    def toggle_bot_state(self):
        if self.is_bot_running:
            self._stop_services()
        else:
            self._initialize_and_start_services()

    def _initialize_and_start_services(self):
        self.settings = self._load_config_file("data/config.json")
        if not self.settings.get('gpt', {}).get('api_key'):
            QMessageBox.warning(self, "Внимание", "GPT API ключ не указан в настройках. Парсер сигналов не будет работать.")
        
        db = DatabaseService()
        self.main_view.update_service_status('database', 'CONNECTED')
        gpt = GptService(api_key=self.settings.get('gpt', {}).get('api_key'))
        self.main_view.update_service_status('gpt', 'CONNECTED' if gpt.api_key else 'OFFLINE')
        mt5_cfg = self.settings.get('mt5',{})
        mt5 = MT5Service(path=mt5_cfg.get('path'), login=mt5_cfg.get('login'), password=mt5_cfg.get('password'), server=mt5_cfg.get('server'))
        self.backend_services = {'db': db, 'gpt': gpt, 'mt5': mt5}

        if self.settings.get('signal_parser',{}).get('enabled',True):
            processor = SignalProcessor(db, gpt, mt5, self.settings, self.channels)
            tg_cfg = self.settings.get('telegram',{})
            tg = TelegramService(f"data/{tg_cfg.get('session_file','userbot.session')}", tg_cfg.get('api_id'), tg_cfg.get('api_hash'))
            manager = TradeManagerService(db, mt5, self.settings)
            self.backend_services.update({'processor': processor, 'tg': tg, 'manager': manager})
            tg.new_message_signal.connect(processor.process_new_message)
            tg.status_signal.connect(lambda s: self.main_view.update_service_status('telegram', s))
            tg.dialogs_fetched_signal.connect(self.on_channels_fetched)
            manager.log_signal.connect(self.mt5_view.add_log_message)
            tg_thread = QThread(); tg.moveToThread(tg_thread); tg_thread.started.connect(tg.start); tg_thread.start()
            manager_thread = QThread(); manager.moveToThread(manager_thread); manager_thread.started.connect(manager.start_monitoring); manager_thread.start()
            self.backend_services['tg_thread'] = tg_thread; self.backend_services['manager_thread'] = manager_thread
            if not self.all_dialogs: tg.fetch_dialogs()
        else:
            self.main_view.update_service_status('telegram','DISABLED')

        if self.settings.get('ai_trader',{}).get('enabled',False):
            self.ai_bot_view.start_stop_button.setEnabled(True)
            self.ai_bot_view.add_log_message("AI is enabled. Press START to begin.", "INFO")
        
        self.is_bot_running = True
        self.main_view.start_stop_button.setText("🛑 STOP BOT")
        self.connect_or_refresh_mt5()

    def _stop_services(self):
        if self.is_ai_trader_running:
            self.stop_ai_trader()
        for thr_name in ['tg_thread', 'manager_thread', 'ai_trader_thread']:
            thread = self.backend_services.get(thr_name)
            if thread and thread.isRunning():
                thread.quit()
                thread.wait(3000)
        for srv_name in ['tg','manager','mt5','db']:
            service = self.backend_services.get(srv_name)
            if service:
                if hasattr(service, 'stop'): service.stop()
                if hasattr(service, 'shutdown'): service.shutdown()
                if hasattr(service, 'close_connection'): service.close_connection()
        self.is_bot_running = False
        self.main_view.start_stop_button.setText("🚀 START BOT")
        self.ai_bot_view.start_stop_button.setEnabled(False)
        for srv_name in ['telegram', 'mt5', 'gpt', 'database']:
            self.main_view.update_service_status(srv_name, 'OFFLINE')
        print("All services stopped.")

    @Slot()
    def toggle_ai_trader_state(self):
        if not self.is_ai_trader_running:
            self.start_ai_trader()
        else:
            self.stop_ai_trader()

    def start_ai_trader(self):
        mt5_service = self.backend_services.get('mt5')
        if not self.is_bot_running or not mt5_service or not mt5_service.is_initialized:
            QMessageBox.warning(self, "Внимание", "Сначала запустите основного бота и убедитесь, что MT5 подключен.")
            return
        
        self.ai_log_history.clear()
        self.ai_bot_view.repopulate_log(self.ai_log_history)
            
        self.ai_trader_service = AITraderService(mt5_service, self.settings)
        self.ai_trader_service.log_signal.connect(self._handle_ai_log)
        self.ai_trader_service.stats_updated_signal.connect(self.on_ai_stats_updated)
        
        self.ai_trader_thread = QThread()
        self.ai_trader_service.moveToThread(self.ai_trader_thread)
        self.ai_trader_thread.finished.connect(self.ai_trader_service.deleteLater)
        self.ai_trader_thread.started.connect(self.ai_trader_service.start_trading)
        self.ai_trader_thread.start()
        self.backend_services['ai_trader_thread'] = self.ai_trader_thread
        
        self.is_ai_trader_running = True
        self.ai_bot_view.start_stop_button.setText("🛑 STOP SIMULATION")

    def stop_ai_trader(self):
        if self.ai_trader_thread and self.ai_trader_thread.isRunning():
            if self.ai_trader_service:
                self.ai_trader_service.stop()
            self.ai_trader_thread.quit()
            self.ai_trader_thread.wait(3000)
        self.is_ai_trader_running = False
        self.ai_bot_view.start_stop_button.setText("🤖 START SIMULATION")
        self.ai_trader_thread = None
        self.ai_trader_service = None

    @Slot()
    def save_all_settings(self):
        try:
            self.settings = self.settings_view.collect_settings_from_ui()
            with open("data/config.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            QMessageBox.information(self, "Успех", "Настройки сохранены. Некоторые изменения требуют перезапуска бота.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
    
    @Slot()
    def test_gpt_key(self):
        key = self.settings_view.gpt_api_key_input.text()
        if not key:
            QMessageBox.warning(self, "Проверка ключа", "Поле API ключа пустое.")
            return
        is_valid = GptService.test_api_key(key)
        if is_valid:
            QMessageBox.information(self, "Проверка ключа", "API ключ действителен!")
        else:
            QMessageBox.critical(self, "Проверка ключа", "Неверный API ключ.")

    @Slot()
    def refresh_history_tab(self):
        db = self.backend_services.get('db') if self.is_bot_running else DatabaseService()
        self.history_view.update_table(db.get_signal_history(limit=200))
        if not self.is_bot_running:
            db.close_connection()

    def connect_or_refresh_mt5(self):
        if not self.is_bot_running: return
        mt5 = self.backend_services.get('mt5')
        self.mt5_view.add_log_message("Connecting to MT5...", "INFO")
        success, message = mt5.initialize()
        if success:
            self.mt5_view.add_log_message("MT5 connection successful.", "SUCCESS")
            self.main_view.update_service_status('mt5', 'CONNECTED')
            self.mt5_view.update_account_info(mt5.get_account_info())
        else:
            self.mt5_view.add_log_message(f"MT5 connection failed: {message}", "ERROR")
            self.main_view.update_service_status('mt5', 'ERROR')

    @Slot(list)
    def on_channels_fetched(self, dialogs_list):
        self.all_dialogs = dialogs_list
        QMessageBox.information(self, "Успех", f"Получено {len(dialogs_list)} каналов. Теперь их можно добавлять на вкладке 'Channels'.")

    @Slot()
    def show_add_channel_dialog(self):
        if not self.is_bot_running: QMessageBox.warning(self, "Сервис выключен", "Сначала запустите бота."); return
        if not self.all_dialogs: QMessageBox.warning(self, "Нет данных", "Список каналов еще не получен. Пожалуйста, подождите."); return
        dialog = ChannelSelectionDialog(self.all_dialogs, self)
        if dialog.exec() and dialog.selected_channel:
            channel = dialog.selected_channel
            channel_id_str = str(channel['id'])
            if channel_id_str not in self.channels:
                self.channels[channel_id_str] = {"name": channel['name'], "active": True, "default_symbol": ""}
                self.save_channels_to_file()
                self.assistant_view.update_channels_table(self.channels)
                self._connect_channel_checkboxes()

    @Slot()
    def remove_selected_channel(self):
        channel_id = self.assistant_view.get_selected_channel_id()
        if not channel_id: QMessageBox.warning(self, "Ошибка", "Выберите канал для удаления."); return
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить канал {self.channels[channel_id]['name']}?")
        if reply == QMessageBox.StandardButton.Yes:
            if channel_id in self.channels:
                del self.channels[channel_id]
            self.save_channels_to_file()
            self.assistant_view.update_channels_table(self.channels)
            self._connect_channel_checkboxes()

    def _connect_channel_checkboxes(self):
        table = self.assistant_view.channels_table
        for row in range(table.rowCount()):
            checkbox_widget = table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    try: checkbox.stateChanged.disconnect()
                    except RuntimeError: pass
                    checkbox.stateChanged.connect(self.on_channel_selection_changed)

    @Slot(int)
    def on_channel_selection_changed(self, state):
        checkbox = self.sender()
        if not checkbox: return
        channel_id = checkbox.property("channel_id")
        if channel_id in self.channels:
            self.channels[channel_id]['active'] = bool(state == Qt.CheckState.Checked.value)
            self.save_channels_to_file()

    def save_channels_to_file(self):
        try:
            with open("data/channels.json", "w", encoding="utf-8") as f: json.dump(self.channels, f, indent=4)
            if self.is_bot_running and 'processor' in self.backend_services:
                self.backend_services['processor'].update_channels(self.channels)
        except Exception as e: QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить channels.json: {e}")

    @Slot()
    def import_session_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Session File", "", "Session Files (*.session)")
        if not path: return
        try:
            shutil.copy(path, "data/")
            filename = os.path.basename(path)
            self.settings_view.session_file_input.setText(filename)
            QMessageBox.information(self, "Успех", "Файл сессии импортирован.")
        except Exception as e: QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать файл: {e}")

    def closeEvent(self, event):
        self._stop_services()
        event.accept()