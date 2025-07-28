import time
from PySide6.QtCore import QObject, Signal, Slot
import pandas as pd

# We will import the logic from the refactored smc_bot_core file (without GUI)
from .smc_bot_core import generate_smc_features, run_strategy, load_mt5_data
from .ai_agent import AIAgent

class SmartMoneyWorker(QObject):
    """
    Worker to run the SmartMoney backtest strategy in a separate thread.
    """
    # Signals to communicate with the main thread
    log = Signal(str)
    finished = Signal()
    new_trade = Signal(dict)
    chart_data = Signal(str, pd.DataFrame)  # symbol, dataframe
    
    def __init__(self, settings, logic_manager=None):
        super().__init__()
        self.settings = settings
        self.logic_manager = logic_manager
        self._is_running = True
        self.ai_agent = AIAgent(log_callback=self.log.emit)

    @Slot()
    def run(self):
        """Main execution loop for the worker."""
        self.log.emit("✅ SmartMoney Worker started.")
        try:
            symbol = self.settings.get('symbol', 'XAUUSD')
            timeframe = self.settings.get('timeframe', 'M15')
            
            # 1. Load data from MT5 or server
            use_server = self.settings.get('use_mt5_server', False)
            server_url = self.settings.get('mt5_server_url', 'http://10.211.55.3:5000')
            
            self.log.emit(f"📊 Загрузка данных {symbol} {timeframe}...")
            df = load_mt5_data(
                symbol=symbol, 
                timeframe=timeframe,
                use_server=use_server,
                server_url=server_url
            )
            
            if df.empty or not self._is_running:
                self.log.emit("❌ Нет данных для анализа или задача остановлена.")
                self.finished.emit()
                return

            self.log.emit(f"✅ Загружено {len(df)} свечей для анализа")
            
            # 2. Train AI if requested
            if self.settings.get('auto_learn', False):
                self.log.emit("🤖 Запуск обучения AI...")
                self.ai_agent.train(df)
                self.log.emit("✅ Обучение AI завершено")
            
            # 3. Generate features and plot chart
            self.log.emit("⚙️ Генерация SMC индикаторов...")
            df_features = generate_smc_features(df)
            self.chart_data.emit(symbol, df_features)
            self.log.emit("✅ SMC индикаторы сгенерированы")
            
            # 4. Run strategy
            mode = self.settings.get('mode', 'paper')
            balance = self.settings.get('balance', 10000)
            
            if mode == 'paper':
                self.log.emit(f"📈 Запуск бэктеста с балансом ${balance:,.2f}...")
                results_df = run_strategy(
                    df_features, 
                    balance=balance,
                    trade_signal=self.new_trade, 
                    ai_agent=self.ai_agent if self.settings.get('use_ai', False) else None,
                    symbol=symbol
                )
                
                # Сохраняем результаты в базу данных
                if self.logic_manager and self.logic_manager.database and not results_df.empty:
                    self.log.emit("💾 Сохранение результатов в базу данных...")
                    self._save_results_to_database(results_df, symbol)
                    self.log.emit("✅ Результаты сохранены в базу данных")
                
                self.log.emit("🎯 Бэктест завершен")
            else:
                self.log.emit("🚀 Запуск режима живой торговли...")
                self.run_live(df_features, symbol)

        except Exception as e:
            self.log.emit(f"❌ Ошибка в SM Worker: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.finished.emit()
    
    def _save_results_to_database(self, results_df, symbol):
        """Сохранение результатов торговли в базу данных"""
        try:
            for _, trade in results_df.iterrows():
                trade_data = {
                    'trade_id': f"SMC_{symbol}_{trade['time'].strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'type': trade['type'],
                    'direction': 'LONG' if trade['type'] == 'BUY' else 'SHORT',
                    'entry_price': trade['entry'],
                    'exit_price': trade['exit'],
                    'stop_loss': trade['sl'],
                    'take_profit': trade['tp1'],  # Используем первый TP
                    'volume': trade['lot'],
                    'status': 'CLOSED',
                    'profit_loss': trade['net_pnl'],
                    'timestamp': trade['time'],
                    'close_timestamp': trade['exit_time'],
                    'source': 'SMC_BOT',
                    'comment': f"SMC Strategy - {trade['result']}"
                }
                
                self.logic_manager.database.add_trade(trade_data)
                
        except Exception as e:
            self.log.emit(f"❌ Ошибка сохранения в БД: {e}")
            
    def run_live(self, df, symbol):
        """Live trading mode with real-time data processing."""
        self.log.emit(f"🔴 LIVE режим запущен для {symbol}")
        
        # В реальном режиме мы бы получали данные в реальном времени
        # Здесь имитируем обработку последних данных
        for i in range(len(df) - 50, len(df)):  # Последние 50 свечей
            if not self._is_running: 
                break
                
            time.sleep(1)  # Имитация реального времени
            
            current_state = df.iloc[max(0, i-10):i+1]  # Последние 10 свечей для контекста
            
            # Используем AI для предсказания
            if self.settings.get('use_ai', False):
                action = self.ai_agent.predict(current_state)  # 0:hold, 1:buy, 2:sell
                
                if action == 1:
                    signal_text = f"🟢 LIVE BUY сигнал для {symbol} на цене {df.iloc[i]['close']:.4f}"
                    self.log.emit(signal_text)
                    
                    # В реальной торговле здесь был бы вызов MT5 API
                    if self.logic_manager and hasattr(self.logic_manager, 'execute_trade'):
                        trade_params = {
                            'symbol': symbol,
                            'action': 'BUY',
                            'volume': self.settings.get('lot_size', 0.01),
                            'price': df.iloc[i]['close']
                        }
                        # self.logic_manager.execute_trade(trade_params)
                        
                elif action == 2:
                    signal_text = f"🔴 LIVE SELL сигнал для {symbol} на цене {df.iloc[i]['close']:.4f}"
                    self.log.emit(signal_text)
                    
                    # В реальной торговле здесь был бы вызов MT5 API
                    if self.logic_manager and hasattr(self.logic_manager, 'execute_trade'):
                        trade_params = {
                            'symbol': symbol,
                            'action': 'SELL',
                            'volume': self.settings.get('lot_size', 0.01),
                            'price': df.iloc[i]['close']
                        }
                        # self.logic_manager.execute_trade(trade_params)

    def stop(self):
        """Stops the worker loop."""
        self.log.emit("⏹️ Остановка SmartMoney Worker...")
        self._is_running = False 