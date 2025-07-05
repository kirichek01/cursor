# prop_guard.py
# Spice Prop‑style risk guard for Combine Trade Bot
# Author: Kirichek Crypto  –  2025‑06‑15

"""Usage example:

from core.prop_guard import PropRiskGuard
guard = PropRiskGuard(daily_dd=0.055, max_dd=0.11, balance=10_000)

# inside on_new_candle loop:
if not guard.can_trade(bot.balance + bot.profit_day, bot.balance):
    return None  # trading blocked for this candle

# after each closed trade:
guard.update(real_pnl)
"""

class PropRiskGuard:
    """Simple day / overall drawdown limiter.

    Args:
        daily_dd (float): 0.055 means 5.5 % max daily loss
        max_dd   (float): 0.11  means 11 % total loss allowed
        balance  (float): initial account balance
    """

    def __init__(self, daily_dd: float = 0.055,
                 max_dd: float = 0.11,
                 balance: float = 10_000.0):
        self.start_balance = balance
        self.daily_limit   = balance * daily_dd
        self.max_limit     = balance * max_dd
        self.day_pl        = 0.0  # resets every new trading day

    # ----------------------------------------------------------
    def can_trade(self, equity_today: float, equity_total: float) -> bool:
        """Return False if any prop limit already violated."""
        if self.day_pl <= -self.daily_limit:
            return False
        if equity_total <= self.start_balance - self.max_limit:
            return False
        return True

    def update(self, pnl: float):
        """Call after each closed position (pnl in USD)."""
        self.day_pl += pnl

    def reset_day(self):
        """Call at the start of a new trading day."""
        self.day_pl = 0.0