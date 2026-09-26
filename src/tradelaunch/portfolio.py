"""A minimal paper-trading portfolio."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Fill:
    ticker: str
    side: str  # "BUY" or "SELL"
    quantity: float
    price: float

    @property
    def notional(self) -> float:
        return self.quantity * self.price


@dataclass
class Portfolio:
    cash: float
    positions: dict[str, float] = field(default_factory=dict)
    fills: list[Fill] = field(default_factory=list)

    def position(self, ticker: str) -> float:
        return self.positions.get(ticker, 0.0)

    def buy(self, ticker: str, price: float, cash_fraction: float) -> Fill | None:
        """Spend ``cash_fraction`` of available cash to buy ``ticker``."""
        cash_fraction = max(0.0, min(1.0, cash_fraction))
        spend = self.cash * cash_fraction
        if spend <= 0 or price <= 0:
            return None
        quantity = spend / price
        self.cash -= spend
        self.positions[ticker] = self.position(ticker) + quantity
        fill = Fill(ticker=ticker, side="BUY", quantity=quantity, price=price)
        self.fills.append(fill)
        return fill

    def sell(self, ticker: str, price: float, position_fraction: float) -> Fill | None:
        """Sell ``position_fraction`` of the held position in ``ticker``."""
        position_fraction = max(0.0, min(1.0, position_fraction))
        held = self.position(ticker)
        quantity = held * position_fraction
        if quantity <= 0 or price <= 0:
            return None
        self.cash += quantity * price
        self.positions[ticker] = held - quantity
        fill = Fill(ticker=ticker, side="SELL", quantity=quantity, price=price)
        self.fills.append(fill)
        return fill

    def market_value(self, prices: dict[str, float]) -> float:
        """Total account value: cash plus marked-to-market positions."""
        holdings = sum(qty * prices.get(t, 0.0) for t, qty in self.positions.items())
        return self.cash + holdings
