import time
import pandas as pd
import MetaTrader5 as mt5
from PySide6.QtCore import QObject, Signal, QTimer

# Импортируем наши новые модули
from .signal_filter import SignalFilter
from .gpt_confidence import GptConfidence
from .prop_guard import PropRiskGuard

class AITraderService(QObject):
    """
    Главный сервис AI-трейдера. Управляет всем процессом:
    1. Получает данные из MT5.
    2. Вызывает SignalFilter для поиска SMC-паттернов.
    3. Вызывает GptConfidence для оценки сигнала.
    4. Принимает решение о сделке или симуляции.
    """
    log_signal = Signal(str, str)
    stats_updated_signal = Signal(dict)

    def __init__(self, mt5_service, settings, parent=None):
        super().__init__(parent)
        self.mt5 = mt5_service
        self.settings = settings
        self.is_running = False
        
        # --- Параметры из ТЗ ---
        self.SYMBOL = settings.get('ai_trader', {}).get('symbol', 'XAUUSD')
        self.TIMEFRAME_ENUM = mt5.TIMEFRAME_M15 # Жестко задано в ТЗ
        self.MIN_CONFIDENCE = settings.get('ai_trader', {}).get('min_confidence', 0.65)
        self.TRADE_LOT_SIZE = settings.get('ai_trader', {}).get('lot_size', 0.01)

        # --- Инициализация модулей ---
        self.signal_filter = SignalFilter(self.settings)
        self.gpt_confidence = GptConfidence(self.settings.get('gpt', {}).get('api_key'))
        self.risk_guard = None # Будет создан при запуске
        
        self.last_candle_time = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_tick)
        
        # Для симуляции
        self.simulated_balance = 10000 # Начальный симулированный баланс
        self.simulated_pnl = 0
        self.simulated_trades = 0

    @property
    def is_live_trading_enabled(self):
        """Проверяет, включена ли реальная торговля."""
        return self.settings.get('ai_trader', {}).get('live_trading', False)

    def start_trading(self):
        """Инициализация и запуск основного цикла."""
        try:
            account_info = self.mt5.get_account_info()
            start_balance = account_info.get('equity') if account_info else 10000
            self.simulated_balance = start_balance
            
            self.risk_guard = PropRiskGuard(balance=start_balance)
            
            self.is_running = True
            self.timer.start(10000) # Проверяем наличие новой свечи каждые 10 секунд
            self.log_signal.emit(f"AI Trader (SMC+GPT) started. Monitoring {self.SYMBOL} on M15.", "SUCCESS")
        except Exception as e:
            self.log_signal.emit(f"AI Initialization failed: {e}", "ERROR")

    def stop(self):
        self.is_running = False
        self.timer.stop()
        self.log_signal.emit("AI Trader stopped.", "INFO")

    def main_tick(self):
        """Основной цикл, который запускается по таймеру."""
        if not self.is_running:
            self.timer.stop()
            return

        try:
            # 1. Получаем исторические данные (последние 50 свечей)
            candles_df = self.mt5.get_rates(self.SYMBOL, self.TIMEFRAME_ENUM, count=50)
            if candles_df is None or candles_df.empty:
                self.log_signal.emit("Waiting for market data...", "INFO")
                return

            # Проверяем, появилась ли новая свеча
            latest_candle_time = candles_df.iloc[-1]['time']
            if self.last_candle_time and latest_candle_time <= self.last_candle_time:
                return # Новой свечи нет, ждем следующего тика
            
            self.last_candle_time = latest_candle_time
            self.log_signal.emit(f"New M15 candle detected for {self.last_candle_time}. Analyzing...", "INFO")

            # 2. Этап 1: Фильтр Smart Money
            smc_signal = self.signal_filter.analyze_candles(candles_df.copy())
            if not smc_signal:
                return # Нет сигнала от SMC, выходим

            self.log_signal.emit(f"SMC Signal Found: {smc_signal}", "SUCCESS")
            
            # 3. Этап 2: Фильтр GPT Confidence
            confidence_check = self.gpt_confidence.get_confidence_for_signal(smc_signal)
            if not confidence_check:
                self.log_signal.emit("GPT confidence check failed.", "ERROR")
                return
            
            self.log_signal.emit(f"GPT Confidence: {confidence_check}", "SUCCESS")
            
            # 4. Принятие решения
            prob = confidence_check.get('prob', 0)
            if prob >= self.MIN_CONFIDENCE:
                self.log_signal.emit(f"Confidence threshold passed ({prob:.2f} >= {self.MIN_CONFIDENCE}). Executing trade.", "SUCCESS")
                self.execute_trade(smc_signal, confidence_check)
            else:
                self.log_signal.emit(f"Confidence threshold NOT passed ({prob:.2f} < {self.MIN_CONFIDENCE}). Skipping trade.", "WARNING")

        except Exception as e:
            self.log_signal.emit(f"Error in AI main_tick: {e}", "ERROR")

    def execute_trade(self, signal: dict, confidence: dict):
        """Выполняет сделку в реальном или тестовом режиме."""
        # Обновляем симуляцию
        pnl = confidence.get('expected_pnl', 0)
        self.simulated_balance += pnl
        self.simulated_pnl += pnl
        self.simulated_trades += 1
        self.emit_stats() # Отправляем обновленную статистику в GUI

        # Проверяем, включена ли реальная торговля
        if self.is_live_trading_enabled:
            trade_data = {
                'symbol': self.SYMBOL,
                'order_type': signal['order_type'],
                'entry_price': signal['entry_price'],
                'stop_loss': signal['sl'],
                'take_profits': [signal['tp']],
            }
            success, message = self.mt5.place_order(trade_data, self.TRADE_LOT_SIZE, "AI_SMC_GPT_Bot")
            if success:
                self.log_signal.emit(f"LIVE TRADE PLACED: {message}", "SUCCESS")
            else:
                self.log_signal.emit(f"LIVE TRADE FAILED: {message}", "ERROR")
        else:
            self.log_signal.emit("TEST MODE: Real trade was not sent.", "INFO")

    def emit_stats(self):
        """Отправляет статистику в GUI."""
        stats_data = {
            'balance': self.simulated_balance,
            'total_profit': self.simulated_pnl,
            'total_trades': self.simulated_trades
        }
        self.stats_updated_signal.emit(stats_data)