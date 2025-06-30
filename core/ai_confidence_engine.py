# ai_confidence_engine.py
# Kirichek Crypto – AI-Confidence Core (XAU/USD, M15)
# This version saves a history of the balance for equity curve plotting.

import json
import pathlib
import datetime as dt
from typing import Optional

import numpy as np
import pandas as pd
import lightgbm as lgb

MODEL_PATH = pathlib.Path('models/xau_m15_lgb.txt')
STATS_PATH = pathlib.Path('data/ai_stats_history.json') # Изменили путь и имя
RISK_PCT = 0.01
FEE_PER_TRADE = 7.0
CONF_TH = 0.65
_FEATS = ['rsi', 'ema_slope', 'atr', 'fibo_z', 'bos_dist', 'ob_width', 'vol_z', 'weekday', 'hour']

# --- ИЗМЕНЕННАЯ ЛОГИКА СОХРАНЕНИЯ/ЗАГРУЗКИ СТАТИСТИКИ ---
def _load_stats_history():
    """Loads the entire history of trades from the JSON file."""
    if STATS_PATH.exists():
        try:
            with open(STATS_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return [] # Если файл поврежден, начинаем с нуля
    return []

def _append_trade_to_history(trade_data):
    """Appends a new trade record to the history file."""
    history = _load_stats_history()
    history.append(trade_data)
    with open(STATS_PATH, 'w') as f:
        json.dump(history, f, indent=2)

class AIConfidenceBot:
    """Single‑symbol bot (XAUUSD M15) based on pre‑trained LightGBM."""

    def __init__(self, start_balance: float = 10_000):
        self.model = lgb.Booster(model_file=str(MODEL_PATH))
        self.start_balance = start_balance
        self.balance = start_balance
        self.trades_day, self.profit_day = 0, 0.0
        self.current_date = None
        
        # Инициализация статистики из истории
        self.history = _load_stats_history()
        if self.history:
            self.balance = self.history[-1]['balance'] # Начинаем с последнего записанного баланса

    def on_new_candle(self, o: float, h: float, l: float, c: float, v: float, ts: dt.datetime) -> Optional[dict]:
        """При новой свече возвращает dict‑сигнал или None."""
        if self.current_date != ts.date():
            self._roll_on_date_change(ts.date())

        row = self._compute_features(o, h, l, c, v, ts)
        prob = self.model.predict(row[_FEATS].values.reshape(1, -1))[0]

        if prob >= CONF_TH:
            return self._generate_trade_signal('BUY', prob, row, ts)
        if prob <= 1 - CONF_TH:
            return self._generate_trade_signal('SELL', prob, row, ts)
        return None

    @property
    def day_stats(self):
        return dict(trades=self.trades_day, profit=round(self.profit_day, 2))

    @property
    def total_stats(self):
        total_profit = self.balance - self.start_balance
        return dict(trades=len(self.history), profit=round(total_profit, 2))

    def _roll_on_date_change(self, new_date: dt.date):
        self.trades_day, self.profit_day = 0, 0.0
        self.current_date = new_date

    def _compute_features(self, o, h, l, c, v, ts) -> pd.Series:
        rsi = 50 + (np.arctan((c - o) * 10) * 20 / np.pi)
        ema_slope = (c - o) / o * 10_000
        atr = (h - l)
        fibo_z = 0.5
        bos_dist = abs(c - o)
        ob_width = h - l
        vol_z = 0
        return pd.Series(dict(rsi=rsi, ema_slope=ema_slope, atr=atr, fibo_z=fibo_z,
                              bos_dist=bos_dist, ob_width=ob_width, vol_z=vol_z,
                              weekday=ts.weekday(), hour=ts.hour, close=c))

    def _generate_trade_signal(self, side: str, prob: float, row: pd.Series, ts: dt.datetime) -> dict:
        size = 0.01 # Используем безопасный фиксированный лот
        tp_pips = 3 * row.atr
        sl_pips = 1.5 * row.atr
        
        # Этот PnL теперь используется только для симуляции и статистики
        exp_pnl = (tp_pips * 100 * size if prob > 0.5 else -sl_pips * 100 * size) - FEE_PER_TRADE

        return dict(timestamp=ts.isoformat(), side=side, prob=round(prob, 3),
                    size=round(size, 2), tp=round(tp_pips, 2), sl=round(sl_pips, 2),
                    exp_pnl=round(exp_pnl, 2), balance=self.balance, # Передаем текущий баланс
                    pnl_to_apply=exp_pnl) # Передаем PnL для обновления

    def update_balance_and_stats(self, pnl_to_apply: float):
        """Updates the balance and stats after a simulated trade."""
        self.balance += pnl_to_apply
        self.profit_day += pnl_to_apply
        
        new_record = {
            'timestamp': dt.datetime.now().isoformat(),
            'balance': round(self.balance, 2),
            'pnl': round(pnl_to_apply, 2)
        }
        _append_trade_to_history(new_record)