import time
import json
from PySide6.QtCore import QObject, QThread, Signal
import MetaTrader5 as mt5

class TradeManagerService(QObject):
    """
    A background service that actively manages open trades.
    Its primary responsibility is to monitor active signals and move the
    Stop Loss to breakeven only after a real Take Profit event.
    """
    log_signal = Signal(str, str)

    def __init__(self, db_service, mt5_service, settings, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.mt5 = mt5_service
        self.settings = settings
        self.is_running = False

    def update_settings(self, new_settings):
        """Applies new settings to the running service."""
        print("--- [TRADE MANAGER] Settings updated. ---")
        self.settings = new_settings

    def start_monitoring(self):
        """Starts the trade monitoring loop."""
        self.is_running = True
        print("--- [TRADE MANAGER] Starting trade monitoring... ---")
        
        while self.is_running:
            try:
                be_settings = self.settings.get('breakeven', {})
                if not be_settings.get('enabled', False):
                    time.sleep(30)
                    continue

                active_signals = self.db.get_active_signals_for_management()

                if active_signals:
                    # Получаем историю сделок за последний день для анализа
                    deals = self.mt5.get_deals_in_history(days=1)
                    if deals is not None:
                        self._check_signals_for_breakeven(active_signals, deals)

            except Exception as e:
                log_msg = f"--- [TRADE MANAGER] Error in monitoring loop: {e} ---"
                print(log_msg)
                self.log_signal.emit(log_msg, "ERROR")

            time.sleep(15) # Check every 15 seconds

        print("--- [TRADE MANAGER] Trade monitoring stopped. ---")

    def _check_signals_for_breakeven(self, signals, deals):
        """
        Processes active signals to check for breakeven conditions based on actual deal history.
        """
        pips_offset = self.settings.get('breakeven', {}).get('pips', 5)
        
        # Преобразуем историю сделок в словарь для быстрого доступа
        # Ключ - ID позиции, значение - сама сделка
        closed_positions = {d.position_id: d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT}

        for signal in signals:
            signal_id = signal['id']
            symbol = signal['symbol']
            tickets_json = signal['mt5_tickets']
            
            try:
                if not tickets_json: continue
                original_tickets = json.loads(tickets_json)
                if not original_tickets: continue
                
                # Проверяем, был ли какой-то из наших ордеров закрыт с прибылью
                tp_hit = False
                for ticket in original_tickets:
                    # Если тикет есть в словаре закрытых позиций и его прибыль > 0
                    if ticket in closed_positions and closed_positions[ticket].profit > 0:
                        tp_hit = True
                        print(f"--- [TRADE MANAGER] Detected that ticket {ticket} for signal {signal_id} was closed with profit.")
                        break # Нашли закрытие по TP, можно выходить из цикла
                
                if tp_hit:
                    log_msg = f"--- [TRADE MANAGER] Confirmed TP hit for signal ID {signal_id} ({symbol}). Moving SL to breakeven... ---"
                    print(log_msg)
                    self.log_signal.emit(log_msg, "INFO")

                    # Получаем оставшиеся открытые позиции по этому сигналу
                    open_positions = self.mt5.get_open_positions_by_ticket(tuple(original_tickets))
                    for position in open_positions:
                        success, message = self.mt5.move_sl_to_breakeven(position, pips_offset)
                        if success:
                            self.log_signal.emit(f"Breakeven set for ticket {position.ticket}.", "SUCCESS")
                        else:
                            self.log_signal.emit(f"Failed to set breakeven for ticket {position.ticket}: {message}", "ERROR")
                    
                    self.db.update_signal_status(signal_id, 'BREAKEVEN_SET')
            
            except json.JSONDecodeError:
                log_msg = f"--- [TRADE MANAGER] Could not parse tickets for signal ID {signal_id}. ---"
                print(log_msg)
                self.log_signal.emit(log_msg, "ERROR")
                self.db.update_signal_status(signal_id, "ERROR_TICKET_PARSE")

    def stop(self):
        """Stops the monitoring loop."""
        self.is_running = False