import pandas as pd
import numpy as np
try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None
from datetime import datetime, timedelta

# ======== MT5 Data Load ============
def load_mt5_data(symbol="XAUUSD", timeframe="M15", date_from="2025-01-01", date_to="2025-06-01", use_server=False, server_url=None):
    """
    Загрузка данных MT5 с поддержкой как локального MT5, так и сервера Flask
    """
    if use_server and server_url:
        # Получение данных через Flask сервер
        try:
            import requests
            response = requests.get(f"{server_url}/get_rates", params={
                'symbol': symbol,
                'timeframe': timeframe,
                'count': 1000
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    rates = data.get('data', [])
                    df = pd.DataFrame(rates)
                    if not df.empty:
                        df["datetime"] = pd.to_datetime(df["time"], unit="s")
                        df = df[["datetime", "open", "high", "low", "close", "tick_volume"]]
                        df = df.sort_values(by="datetime").reset_index(drop=True)
                        return df
        except Exception as e:
            print(f"❌ Ошибка загрузки данных через сервер: {e}")
    
    # Локальная загрузка через MT5
    if not mt5:
        error_msg = "❌ MetaTrader5 library is not installed and no server configured. Cannot load real data."
        print(error_msg)
        raise Exception(error_msg)

    tf_map = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
              "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
              "D1": mt5.TIMEFRAME_D1}

    if not mt5.initialize():
        print("❌ MT5 initialize() failed")
        return pd.DataFrame()

    try:
        rates = mt5.copy_rates_range(symbol, tf_map[timeframe],
                                     datetime.strptime(date_from, "%Y-%m-%d"),
                                     datetime.strptime(date_to, "%Y-%m-%d"))
        
        if rates is None or len(rates) == 0:
            print(f"❌ Нет данных для {symbol}")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df["datetime"] = pd.to_datetime(df["time"], unit="s")
        df = df[["datetime", "open", "high", "low", "close", "tick_volume"]]
        df = df.sort_values(by="datetime").reset_index(drop=True)
        return df
        
    except Exception as e:
        print(f"❌ Ошибка получения данных MT5: {e}")
        return pd.DataFrame()
    finally:
        mt5.shutdown()

# ======== SMC Feature Generation ============
def generate_smc_features(df):
    """Генерация SMC индикаторов"""
    if df.empty:
        return df
        
    df = df.copy()
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
    wick = wick.replace(0, 0.0001)  # Избегаем деления на ноль
    df["order_block"] = (body / wick > 0.6).astype(int)
    df["fvg"] = ((df["high"] < df["low"].shift(-2)) | (df["low"] > df["high"].shift(-2))).astype(int)
    df["inducement"] = ((df["high"] > df["high"].shift(3)) & (df["close"] < df["open"])).astype(int)
    
    return df.dropna().reset_index(drop=True)

# ======== SMC Strategy Execution ============
def run_strategy(df, balance=10000, trade_signal=None, ai_agent=None, symbol="XAUUSD", account_currency="USD"):
    """
    Выполнение SMC стратегии с реалистичным учетом комиссий и спредов
    """
    trades = []
    current_balance = balance
    risk_pct = 0.01  # 1% риск на сделку
    
    # Реалистичные параметры для разных инструментов
    instrument_params = {
        "XAUUSD": {
            "spread": 0.30,         # Спред в долларах
            "commission": 0.50,     # Комиссия за лот в долларах
            "slippage": 0.20,       # Проскальзывание в долларах
            "point_value": 1.0,     # Стоимость пункта
            "contract_size": 100    # Размер контракта
        },
        "EURUSD": {
            "spread": 0.00015,      # Спред в пунктах
            "commission": 3.0,      # Комиссия за лот
            "slippage": 0.00010,
            "point_value": 10.0,
            "contract_size": 100000
        },
        "GBPUSD": {
            "spread": 0.00020,
            "commission": 3.0,
            "slippage": 0.00015,
            "point_value": 10.0,
            "contract_size": 100000
        }
    }
    
    params = instrument_params.get(symbol, instrument_params["XAUUSD"])
    
    for i in range(1, len(df)):
        if current_balance <= balance * 0.5:  # Стоп при просадке 50%
            print(f"⚠️ Торговля остановлена при балансе ${current_balance:.2f}")
            break
            
        row = df.iloc[i]
        
        # Используем AI для принятия решений, если доступен
        if ai_agent:
            state = df.iloc[max(0, i-10):i+1]  # Последние 10 свечей для контекста
            action = ai_agent.predict(state)  # 0:hold, 1:buy, 2:sell
            buy_cond = action == 1
            sell_cond = action == 2
        else:
            # Оригинальная логика SMC
            buy_cond = (row["bos_up"] and row["order_block"] and 
                       row["fvg"] and row["trend"] == 1)
            sell_cond = (row["bos_down"] and row["order_block"] and 
                        row["fvg"] and row["trend"] == 0)

        if not (buy_cond or sell_cond):
            continue

        direction = "buy" if buy_cond else "sell"
        
        # Расчет цены входа с учетом спреда и проскальзывания
        if direction == "buy":
            entry_price = row["close"] + params["spread"] + params["slippage"]
        else:
            entry_price = row["close"] - params["spread"] - params["slippage"]
        
        # Расчет стоп-лосса и тейк-профитов
        atr_value = row.get("atr", entry_price * 0.01)  # ATR или 1% от цены
        
        if direction == "buy":
            sl = entry_price - (atr_value * 2)  # 2 ATR стоп-лосс
            tp1 = entry_price + (atr_value * 1.5)  # 1.5 ATR первый тейк
            tp2 = entry_price + (atr_value * 3)    # 3 ATR второй тейк
            tp3 = entry_price + (atr_value * 4.5)  # 4.5 ATR третий тейк
        else:
            sl = entry_price + (atr_value * 2)
            tp1 = entry_price - (atr_value * 1.5)
            tp2 = entry_price - (atr_value * 3)
            tp3 = entry_price - (atr_value * 4.5)

        # Расчет размера позиции
        stop_distance = abs(entry_price - sl)
        dollar_risk = current_balance * risk_pct
        
        if symbol == "XAUUSD":
            # Для золота: каждый доллар движения = $100 на стандартном лоте
            lot_size = dollar_risk / (stop_distance * 100)
        else:
            # Для валютных пар
            pip_value = params["point_value"]
            stop_distance_pips = stop_distance * 10000  # Конвертируем в пипсы
            lot_size = dollar_risk / (stop_distance_pips * pip_value)
        
        # Ограничиваем размер лота
        lot_size = min(lot_size, 1.0)  # Максимум 1 лот
        lot_size = max(lot_size, 0.01) # Минимум 0.01 лота
        lot_size = round(lot_size, 2)

        # Симуляция исполнения сделки
        sl_hit = tp1_hit = tp2_hit = tp3_hit = False
        exit_price = entry_price
        exit_time = row["datetime"]
        
        # Ищем выход в следующих свечах (максимум 48 свечей = 12 часов для M15)
        for j in range(i+1, min(i+49, len(df))):
            future_row = df.iloc[j]
            
            # Проверка стоп-лосса
            if ((direction == "buy" and future_row["low"] <= sl) or 
                (direction == "sell" and future_row["high"] >= sl)):
                sl_hit = True
                exit_price = sl
                exit_time = future_row["datetime"]
                break
            
            # Проверка тейк-профитов
            if direction == "buy":
                if future_row["high"] >= tp1 and not tp1_hit:
                    tp1_hit = True
                    exit_price = tp1
                    exit_time = future_row["datetime"]
                if tp1_hit and future_row["high"] >= tp2 and not tp2_hit:
                    tp2_hit = True
                    exit_price = tp2
                    exit_time = future_row["datetime"]
                if tp2_hit and future_row["high"] >= tp3 and not tp3_hit:
                    tp3_hit = True
                    exit_price = tp3
                    exit_time = future_row["datetime"]
                    break
            else:
                if future_row["low"] <= tp1 and not tp1_hit:
                    tp1_hit = True
                    exit_price = tp1
                    exit_time = future_row["datetime"]
                if tp1_hit and future_row["low"] <= tp2 and not tp2_hit:
                    tp2_hit = True
                    exit_price = tp2
                    exit_time = future_row["datetime"]
                if tp2_hit and future_row["low"] <= tp3 and not tp3_hit:
                    tp3_hit = True
                    exit_price = tp3
                    exit_time = future_row["datetime"]
                    break

        # Расчет P&L с учетом комиссий
        price_movement = exit_price - entry_price
        if direction == "sell":
            price_movement = -price_movement
            
        if symbol == "XAUUSD":
            gross_pnl = price_movement * lot_size * 100  # $100 за пункт для золота
        else:
            # Для валютных пар
            pips_movement = price_movement * 10000
            gross_pnl = pips_movement * lot_size * params["point_value"]
        
        # Вычитаем комиссию
        commission_cost = params["commission"] * lot_size * 2  # Вход и выход
        net_pnl = gross_pnl - commission_cost
        
        # Обновляем баланс
        current_balance += net_pnl
        
        # Определяем результат сделки
        if sl_hit:
            result = "STOP_LOSS"
        elif tp3_hit:
            result = "TP3"
        elif tp2_hit:
            result = "TP2"
        elif tp1_hit:
            result = "TP1"
        else:
            result = "TIMEOUT"

        trade_result = {
            "time": row["datetime"],
            "exit_time": exit_time,
            "type": direction.upper(),
            "symbol": symbol,
            "entry": round(entry_price, 4),
            "exit": round(exit_price, 4),
            "sl": round(sl, 4),
            "tp1": round(tp1, 4),
            "tp2": round(tp2, 4),
            "tp3": round(tp3, 4),
            "lot": lot_size,
            "gross_pnl": round(gross_pnl, 2),
            "commission": round(commission_cost, 2),
            "net_pnl": round(net_pnl, 2),
            "balance": round(current_balance, 2),
            "result": result,
            "risk_pct": risk_pct * 100
        }
        trades.append(trade_result)
        
        # Отправляем сигнал о новой сделке
        if trade_signal:
            trade_signal.emit(trade_result)
        
        print(f"📊 {direction.upper()} {symbol} | Entry: {entry_price:.4f} | Exit: {exit_price:.4f} | P&L: ${net_pnl:.2f} | Balance: ${current_balance:.2f}")

    results_df = pd.DataFrame(trades)
    
    # Выводим итоговую статистику
    if not results_df.empty:
        total_trades = len(results_df)
        winning_trades = len(results_df[results_df['net_pnl'] > 0])
        total_pnl = results_df['net_pnl'].sum()
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   Общее количество сделок: {total_trades}")
        print(f"   Прибыльных сделок: {winning_trades}")
        print(f"   Процент прибыльности: {win_rate:.1f}%")
        print(f"   Общая прибыль: ${total_pnl:.2f}")
        print(f"   Итоговый баланс: ${current_balance:.2f}")
        print(f"   Доходность: {((current_balance - balance) / balance * 100):.2f}%")
    
    return results_df

# ======== Telegram Notification ============
def send_telegram_message(message, token, chat_id):
    """Отправка уведомления в Telegram"""
    try:
        import telegram
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"Ошибка отправки Telegram сообщения: {e}")
        return False