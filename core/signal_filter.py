import pandas as pd
import numpy as np

class SignalFilter:
    """
    Анализирует историю свечей для нахождения торговых сигналов
    на основе концепции Smart Money (BOS + OB).
    Эта версия включает улучшенную логику поиска BOS и подробное логирование.
    """
    def __init__(self, settings):
        self.settings = settings
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.min_risk_reward = self.settings.get('ai_trader', {}).get('min_risk_reward', 1.5)

    def analyze_candles(self, candles_df: pd.DataFrame) -> dict | None:
        """
        Основной метод, который принимает DataFrame со свечами и ищет сигнал.
        """
        if len(candles_df) < 20:
            print("--- [SMC FILTER] Not enough candles for analysis.")
            return None

        self._add_indicators(candles_df)

        print("--- [SMC FILTER] Searching for Break of Structure (BOS)...")
        bos_index, bos_type = self._find_last_bos(candles_df)
        if bos_index is None:
            print("--- [SMC FILTER] No clear BOS found in recent candles.")
            return None

        print(f"--- [SMC FILTER] BOS found! Type: {bos_type}. Searching for Order Block...")
        order_block = self._find_order_block(candles_df, bos_index, bos_type)
        if order_block is None:
            print("--- [SMC FILTER] No valid Order Block found before BOS.")
            return None

        print(f"--- [SMC FILTER] Order Block found at price: {order_block['price']}. Generating signal...")
        signal = self._generate_signal(order_block, bos_type)
        
        if not self._validate_signal(signal):
            return None

        print(f"--- [SMC FILTER] Valid signal generated: {signal} ---")
        return signal

    def _add_indicators(self, df: pd.DataFrame):
        """Расчет и добавление RSI."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

    def _find_last_bos(self, df: pd.DataFrame, lookback=20, swing_n=3) -> tuple[int, str] | tuple[None, None]:
        """
        Улучшенный поиск слома структуры (BOS) с использованием свингов.
        """
        recent_df = df.iloc[-lookback:]
        
        # Находим точки свингов (максимумы и минимумы)
        highs = recent_df['high']
        lows = recent_df['low']
        
        swing_highs = highs[(highs.shift(1) < highs) & (highs.shift(-1) < highs)]
        swing_lows = lows[(lows.shift(1) > lows) & (lows.shift(-1) > lows)]

        if swing_highs.empty or swing_lows.empty:
            print("--- [SMC FILTER] Not enough swing points found.")
            return None, None

        last_swing_high_idx = swing_highs.index[-1]
        last_swing_low_idx = swing_lows.index[-1]
        
        # Последнее событие - новый максимум
        if last_swing_high_idx > last_swing_low_idx:
            # Ищем предыдущий максимум до этого минимума
            prev_swing_highs = swing_highs[swing_highs.index < last_swing_low_idx]
            if not prev_swing_highs.empty and swing_highs.loc[last_swing_high_idx] > prev_swing_highs.max():
                return last_swing_high_idx, 'BUY' # Бычий слом

        # Последнее событие - новый минимум
        if last_swing_low_idx > last_swing_high_idx:
            # Ищем предыдущий минимум до этого максимума
            prev_swing_lows = swing_lows[swing_lows.index < last_swing_high_idx]
            if not prev_swing_lows.empty and swing_lows.loc[last_swing_low_idx] < prev_swing_lows.min():
                return last_swing_low_idx, 'SELL' # Медвежий слом

        return None, None

    def _find_order_block(self, df: pd.DataFrame, bos_index: int, bos_type: str) -> dict | None:
        """Находит ордер-блок, предшествующий слому структуры."""
        search_range = df.loc[:bos_index].iloc[-10:]

        if bos_type == 'SELL': # Ищем последнюю бычью свечу перед падением
            bullish_candles = search_range[search_range['close'] > search_range['open']]
            if not bullish_candles.empty:
                ob_candle = bullish_candles.iloc[-1]
                return {'price': ob_candle['high'], 'low': ob_candle['low'], 'high': ob_candle['high']}

        if bos_type == 'BUY': # Ищем последнюю медвежью свечу перед ростом
            bearish_candles = search_range[search_range['close'] < search_range['open']]
            if not bearish_candles.empty:
                ob_candle = bearish_candles.iloc[-1]
                return {'price': ob_candle['low'], 'low': ob_candle['low'], 'high': ob_candle['high']}
        
        return None

    def _generate_signal(self, order_block: dict, side: str) -> dict:
        """Формирует торговый сигнал на основе ордер-блока."""
        entry_price = order_block['price']
        
        if side == 'SELL':
            sl = order_block['high'] + (order_block['high'] - order_block['low']) * 0.1
            tp = entry_price - (sl - entry_price) * self.min_risk_reward
            order_type = 'SELL_LIMIT'
        else: # BUY
            sl = order_block['low'] - (order_block['high'] - order_block['low']) * 0.1
            tp = entry_price + (entry_price - sl) * self.min_risk_reward
            order_type = 'BUY_LIMIT'

        return {"side": side, "order_type": order_type, "entry_price": round(entry_price, 2), "sl": round(sl, 2), "tp": round(tp, 2)}

    def _validate_signal(self, signal: dict) -> bool:
        """Проверяет сигнал на соответствие дополнительным фильтрам."""
        if signal['sl'] == signal['entry_price']: return False
        
        risk = abs(signal['entry_price'] - signal['sl'])
        reward = abs(signal['tp'] - signal['entry_price'])
        
        if reward / risk < self.min_risk_reward:
            print(f"--- [SMC FILTER] Signal rejected due to low R:R ({reward/risk:.2f}) ---")
            return False
            
        # Здесь можно добавить другие фильтры, например, по RSI
        # last_rsi = ...
        # if signal['side'] == 'BUY' and last_rsi > self.rsi_oversold: return False
        
        return True