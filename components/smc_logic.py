import pandas as pd
import numpy as np
from datetime import datetime
import telegram
import asyncio

# ----- ПОПЫТКА ИМПОРТА MT5 -----
try:
    import MetaTrader5 as mt5
    MT5_INITIALIZED = True
except ImportError:
    print("⚠️ MetaTrader5 не найден. Используется dummy_data.csv")
    MT5_INITIALIZED = False

# ======== MT5 Data Load ============
def load_mt5_data(symbol="XAUUSD", timeframe="M15", date_from="2025-01-01", date_to="2025-06-01"):
    if MT5_INITIALIZED:
        tf_map = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
                  "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
                  "D1": mt5.TIMEFRAME_D1}

        if not mt5.initialize():
            print("❌ MT5 initialize() failed")
            return None

        rates = mt5.copy_rates_range(symbol, tf_map[timeframe],
                                     datetime.strptime(date_from, "%Y-%m-%d"),
                                     datetime.strptime(date_to, "%Y-%m-%d"))
        mt5.shutdown()
        
        if rates is None:
            return None
        
        df = pd.DataFrame(rates)
    else:
        # Загрузка данных из CSV, если MT5 недоступен
        try:
            df = pd.read_csv("dummy_data.csv")
        except FileNotFoundError:
            print("❌ dummy_data.csv не найден!")
            return None

    df["datetime"] = pd.to_datetime(df["time"], unit="s")
    df = df[["datetime", "open", "high", "low", "close"]]
    df = df.sort_values(by=["datetime"]).reset_index(drop=True)
    return df

# ======== SMC Feature Generation ============
def generate_smc_features(df):
    # ... (код функции без изменений)
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
    # ... (код функции без изменений)
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
            "time": row["datetime"], "type": direction, "entry": round(entry, 2),
            "sl": round(sl, 2), "tp1": round(tp1, 2), "tp2": round(tp2, 2),
            "tp3": round(tp3, 2), "lot": round(lot_size, 2),
            "pnl_usd": round(pnl, 2), "balance": round(balance, 2)
        })

    return pd.DataFrame(trades)

# ======== Telegram Notification ============
async def send_telegram_message(message, token, chat_id):
    try:
        bot = telegram.Bot(token=token)
        await bot.sendMessage(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")
        return False 