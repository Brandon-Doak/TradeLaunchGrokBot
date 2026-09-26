"""A deterministic synthetic market data feed.

The feed produces reproducible price series seeded by an integer so that
bot runs are fully repeatable in tests and demos without any network access.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Quote:
    ticker: str
    price: float
    prev_price: float

    @property
    def pct_change(self) -> float:
        if self.prev_price == 0:
            return 0.0
        return (self.price - self.prev_price) / self.prev_price * 100.0


class MarketFeed:
    """Generates synthetic but plausible price walks for a set of tickers."""

    def __init__(self, tickers: list[str], seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._tick = 0
        # Seed each ticker with a distinct, stable starting price.
        self._prices: dict[str, float] = {}
        self._prev: dict[str, float] = {}
        for i, ticker in enumerate(tickers):
            base = 100.0 * (i + 1) + self._rng.uniform(0, 50)
            self._prices[ticker] = round(base, 2)
            self._prev[ticker] = round(base, 2)

    @property
    def tick(self) -> int:
        return self._tick

    def advance(self) -> dict[str, Quote]:
        """Advance one time step and return the new quotes per ticker."""
        self._tick += 1
        quotes: dict[str, Quote] = {}
        for ticker, price in self._prices.items():
            drift = math.sin(self._tick / 3.0) * 0.4
            shock = self._rng.uniform(-2.0, 2.0)
            new_price = max(0.01, round(price * (1 + (drift + shock) / 100.0), 2))
            self._prev[ticker] = price
            self._prices[ticker] = new_price
            quotes[ticker] = Quote(ticker=ticker, price=new_price, prev_price=price)
        return quotes
