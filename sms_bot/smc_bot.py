
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt
import sys
import telegram

# ======== MT5 Data Load ============
def load_mt5_data(symbol="XAUUSD", timeframe="M15", date_from="2025-01-01", date_to="2025-06-01"):
    tf_map = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
              "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
              "D1": mt5.TIMEFRAME_D1}

    if not mt5.initialize():
        print("❌ MT5 initialize() failed")
        quit()

    rates = mt5.copy_rates_range(symbol, tf_map[timeframe],
                                 datetime.strptime(date_from, "%Y-%m-%d"),
                                 datetime.strptime(date_to, "%Y-%m-%d"))

    mt5.shutdown()

    df = pd.DataFrame(rates)
    df["datetime"] = pd.to_datetime(df["time"], unit="s")
    df = df[["datetime", "open", "high", "low", "close"]]
    df = df.sort_values("datetime").reset_index(drop=True)
    return df

# ======== SMC Feature Generation ============
def generate_smc_features(df):
    df["hour"] = df["datetime"].dt.hour
    df["session"] = df["hour"].apply(lambda h: "London" if 7 <= h < 12 else ("New York" if 13 <= h < 18 else "Asia"))
    df["ema_50"] = df["close"].ewm(span=50).mean()
    df["trend"] = (df["close"] > df["ema_50"]).astype(int)

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(window=14).mean()

    df["bos_up"] = (df["high"] > df["high"].shift(1)) & (df["close"] > df["close"].shift(1))
    df["bos_down"] = (df["low"] < df["low"].shift(1)) & (df["close"] < df["close"].shift(1))

    body = abs(df["close"] - df["open"])
    wick = df["high"] - df["low"]
    df["order_block"] = (body / wick > 0.6).astype(int)
    df["fvg"] = ((df["high"] < df["low"].shift(-2)) | (df["low"] > df["high"].shift(-2))).astype(int)
    df["inducement"] = ((df["high"] > df["high"].shift(3)) & (df["close"] < df["open"])).astype(int)
    return df.dropna().reset_index(drop=True)

# ======== SMC Strategy Execution ============
def run_strategy(df, balance=10000):
    trades = []
    risk_pct = 0.01
    slippage = 0.0002
    commission = 0.0001

    for i in range(1, len(df)):
        row = df.iloc[i]
        buy_cond = row["bos_up"] and row["order_block"] and row["fvg"] and row["trend"] == 1
        sell_cond = row["bos_down"] and row["order_block"] and row["fvg"] and row["trend"] == 0

        if not (buy_cond or sell_cond):
            continue

        direction = "buy" if buy_cond else "sell"
        entry = row["close"] * (1 + commission + slippage) if direction == "buy" else row["close"] * (1 - commission - slippage)
        sl = entry - 0.003 * entry if direction == "buy" else entry + 0.003 * entry
        tp1 = entry + 0.006 * entry if direction == "buy" else entry - 0.006 * entry
        tp2 = entry + 0.009 * entry if direction == "buy" else entry - 0.009 * entry
        tp3 = entry + 0.012 * entry if direction == "buy" else entry - 0.012 * entry

        stop_size = abs(entry - sl)
        dollar_risk = balance * risk_pct
        lot_size = dollar_risk / stop_size

        sl_hit = tp1_hit = tp2_hit = tp3_hit = False
        for j in range(i+1, min(i+49, len(df))):
            future_price = df.iloc[j]["close"]
            if (direction == "buy" and future_price <= sl) or (direction == "sell" and future_price >= sl):
                sl_hit = True
                break
            if (direction == "buy" and future_price >= tp1) or (direction == "sell" and future_price <= tp1):
                tp1_hit = True
            if tp1_hit and ((direction == "buy" and future_price >= tp2) or (direction == "sell" and future_price <= tp2)):
                tp2_hit = True
            if tp2_hit and ((direction == "buy" and future_price >= tp3) or (direction == "sell" and future_price <= tp3)):
                tp3_hit = True

        if sl_hit:
            pnl = -dollar_risk
        elif tp3_hit:
            pnl = dollar_risk * ((abs(tp1 - entry)) * 0.2 + abs(tp2 - entry) * 0.4 + abs(tp3 - entry) * 0.4) / stop_size
        elif tp2_hit:
            pnl = dollar_risk * ((abs(tp1 - entry)) * 0.2 + abs(tp2 - entry) * 0.4) / stop_size
        elif tp1_hit:
            pnl = dollar_risk * ((abs(tp1 - entry)) * 0.2) / stop_size
        else:
            pnl = 0

        if direction == "sell":
            pnl = -pnl

        balance += pnl
        trades.append({
            "time": row["datetime"],
            "type": direction,
            "entry": round(entry, 2),
            "sl": round(sl, 2),
            "tp1": round(tp1, 2),
            "tp2": round(tp2, 2),
            "tp3": round(tp3, 2),
            "lot": round(lot_size, 2),
            "pnl_usd": round(pnl, 2),
            "balance": round(balance, 2)
        })

    results_df = pd.DataFrame(trades)
    results_df.to_csv("smc_results.csv", index=False)
    print("✔️ Trades saved to smc_results.csv")

# ======== Telegram Notification ============
def send_telegram_message(message, token, chat_id):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message)

# ======== GUI Setup ============
class SMCBotUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('SMC Trade Bot Interface')
        self.setGeometry(100, 100, 800, 600)

        # Основной Layout
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel('Combine Trade Bot by Kistech', self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(title_label)

        # Баланс
        balance_label = QLabel('Balance: $10,000', self)
        balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        balance_label.setStyleSheet("font-size: 18px; color: #00FF00;")
        layout.addWidget(balance_label)

        # График баланса (позже подключим)
        chart_label = QLabel('Balance Equity Curve (Placeholder)', self)
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(chart_label)

        # Настройки сигналов
        signals_label = QLabel('Signals', self)
        signals_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signals_label.setStyleSheet("font-size: 18px; color: white;")
        layout.addWidget(signals_label)

        # Таблица сигналов
        table = QTableWidget(self)
        table.setRowCount(5)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['Signal Type', 'Symbol', 'Price'])

        # Заполнение таблицы примерами
        data = [
            ['Buy', 'XAUUSD', '2670.00'],
            ['Sell', 'EURUSD', '1.2200'],
            ['Buy', 'GER40', '15000.50'],
            ['Buy', 'XAUUSD', '2675.30'],
            ['Sell', 'GBPUSD', '1.3600']
        ]

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                table.setItem(row_idx, col_idx, QTableWidgetItem(value))

        layout.addWidget(table)

        # Основной центральный виджет
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

# Создание приложения и окна
app = QApplication(sys.argv)
window = SMCBotUI()
window.setStyleSheet("background-color: #2E3B47; color: white;")
window.show()
sys.exit(app.exec())

# ======== Запуск торговли ============
if __name__ == "__main__":
    df_raw = load_mt5_data(symbol="XAUUSD", timeframe="M15", date_from="2025-01-01", date_to="2025-06-01")
    df_features = generate_smc_features(df_raw)
    run_strategy(df_features)
