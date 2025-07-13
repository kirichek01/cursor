
CONFIG = {
    "sessions": {
        "Asia":     {"start": "00:00", "end": "06:00", "enabled": False},
        "London":   {"start": "07:00", "end": "11:00", "enabled": True},
        "NewYork":  {"start": "13:30", "end": "17:30", "enabled": True}
    },

    "risk": {
        "risk_per_trade": 0.01,
        "max_daily_loss_pct": 0.05,
        "max_total_drawdown_pct": 0.10
    },

    "strategy": {
        "use_buy": True,
        "use_sell": True,
        "require_bos": True,
        "require_ob": True,
        "require_fvg": True,
        "trend_filter": True,
        "trend_ema_period": 50,
        "tp1_ratio": 0.006,
        "tp2_ratio": 0.009,
        "tp3_ratio": 0.012,
        "sl_ratio": 0.003,
        "trail_stop_enabled": False
    },

    "execution": {
        "commission_pct": 0.0001,
        "slippage_pct": 0.0002
    },

    "mode": {
        "paper_trading": True  # True = на бумаге, False = вживую через API
    },

    "symbols": ["XAUUSD", "GER40", "EURUSD"],
    "timeframe": "M15"  # Можно выбрать: "M1", "M5", "M15", "H1", "H4"
}
