import threading
import json
import os

# Предполагается, что все сервисы будут перемещены и адаптированы
# from core.database_service import DatabaseService
# from core.gpt_service import GptService
# from core.mt5_service import MT5Service
# from core.telegram_service import TelegramService
# ... и так далее

class LogicManager:
    """
    Управляет всеми фоновыми сервисами, их инициализацией и жизненным циклом.
    Это замена логики, которая была в MainWindow.
    """
    def __init__(self, page):
        self.page = page # Для отправки обновлений в UI через pubsub
        self.settings = self._load_config_file("data/config.json")
        self.channels = self._load_config_file("data/channels.json", is_channels=True)
        self.is_bot_running = False
        self.backend_services = {}
        self.threads = {}

    def _load_config_file(self, path, is_channels=False):
        # ... (код загрузки конфига, адаптированный без QMessageBox)
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
            print(f"ERROR: Не удалось загрузить {path}: {e}")
            return {}

    def start_all_services(self):
        """
        Инициализирует и запускает все необходимые сервисы в отдельных потоках.
        """
        if self.is_bot_running:
            print("INFO: Сервисы уже запущены.")
            return

        print("INFO: Запуск всех сервисов...")
        # Здесь будет логика из _initialize_and_start_services
        # Например:
        # db = DatabaseService()
        # tg = TelegramService(...)
        # tg_thread = threading.Thread(target=tg.start, daemon=True)
        # tg_thread.start()
        # self.threads['tg_thread'] = tg_thread
        
        self.is_bot_running = True
        self.page.pubsub.send_all({"type": "status", "service": "main", "data": "STARTED"})
        print("INFO: Все сервисы запущены.")

    def stop_all_services(self):
        """
        Останавливает все запущенные сервисы и потоки.
        """
        if not self.is_bot_running:
            return
            
        print("INFO: Остановка всех сервисов...")
        # Здесь будет логика из _stop_services
        # Например, вызов service.stop() для каждого сервиса
        
        self.is_bot_running = False
        self.page.pubsub.send_all({"type": "status", "service": "main", "data": "STOPPED"})
        print("INFO: Все сервисы остановлены.")

    def save_settings(self, new_settings):
        """Сохраняет новые настройки в config.json"""
        self.settings = new_settings
        try:
            with open("data/config.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            print("INFO: Настройки сохранены.")
            return True
        except Exception as e:
            print(f"ERROR: Не удалось сохранить настройки: {e}")
            return False 