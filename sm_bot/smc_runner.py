import time
from PySide6.QtCore import QObject, Signal, Slot
import pandas as pd

# We will import the logic from the refactored smc_bot file
from .smc_bot import generate_smc_features, run_strategy, load_mt5_data
from .ai_agent import AIAgent

class SmartMoneyWorker(QObject):
    """
    Worker to run the SmartMoney backtest strategy in a separate thread.
    """
    # Signals to communicate with the main thread
    log = Signal(str)
    finished = Signal()
    new_trade = Signal(dict)
    chart_data = Signal(pd.DataFrame)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self._is_running = True
        self.ai_agent = AIAgent(log_callback=self.log.emit)

    @Slot()
    def run(self):
        """Main execution loop for the worker."""
        self.log.emit("SmartMoney Worker started.")
        try:
            # 1. Load data
            df = load_mt5_data(symbol=self.settings.get('symbol', 'XAUUSD'), 
                               timeframe=self.settings.get('timeframe', 'M15'))
            if df.empty or not self._is_running:
                self.log.emit("No data loaded or task was stopped. Exiting.")
                self.finished.emit()
                return

            # 2. Train AI if requested
            if self.settings.get('auto_learn'):
                self.ai_agent.train(df)
            
            # 3. Generate features and plot chart
            df_features = generate_smc_features(df)
            self.chart_data.emit(self.settings['symbol'], df_features)
            
            # 4. Run strategy
            if self.settings.get('mode') == 'paper':
                self.log.emit("Running backtest...")
                run_strategy(df_features, 
                             trade_signal=self.new_trade, 
                             ai_agent=self.ai_agent) # Pass agent to strategy
            else: # Live mode
                self.run_live(df_features)

        except Exception as e:
            self.log.emit(f"Error in SM Worker: {e}")
        finally:
            self.finished.emit()
            
    def run_live(self, df):
        """Placeholder for live trading logic."""
        self.log.emit("Live trading mode started. (Simulation only)")
        # In a real scenario, this would loop and check for new data/signals
        for i in range(len(df)):
            if not self._is_running: break
            time.sleep(2) # Simulate real-time ticks
            current_state = df.iloc[i:i+1] # The current "tick"
            # Use AI to predict action
            action = self.ai_agent.predict(current_state) # 0:hold, 1:buy, 2:sell
            if action == 1:
                self.log.emit(f"LIVE SIGNAL: BUY {self.settings['symbol']}")
                # Here you would call mt5.order_send()
            elif action == 2:
                self.log.emit(f"LIVE SIGNAL: SELL {self.settings['symbol']}")
                # Here you would call mt5.order_send()

    def stop(self):
        """Stops the worker loop."""
        self.log.emit("Stopping SmartMoney Worker...")
        self._is_running = False 