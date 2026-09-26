"""The main trading loop wiring the market feed, Grok, and the portfolio."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .config import Settings
from .grok import Decision, build_client
from .market import MarketFeed
from .portfolio import Portfolio

logger = logging.getLogger("tradelaunch")

# Fraction of buying power / position acted on, scaled by model confidence.
_MAX_BUY_FRACTION = 0.25
_MAX_SELL_FRACTION = 1.0


@dataclass
class TickReport:
    tick: int
    decisions: list[Decision]
    equity: float


@dataclass
class RunResult:
    starting_equity: float
    ending_equity: float
    ticks: list[TickReport] = field(default_factory=list)
    model: str = "mock"

    @property
    def pnl(self) -> float:
        return self.ending_equity - self.starting_equity

    @property
    def pnl_pct(self) -> float:
        if self.starting_equity == 0:
            return 0.0
        return self.pnl / self.starting_equity * 100.0


class TradingBot:
    def __init__(self, settings: Settings, seed: int = 42, client=None) -> None:
        self.settings = settings
        self.feed = MarketFeed(settings.tickers, seed=seed)
        self.portfolio = Portfolio(cash=settings.starting_cash)
        self.client = client if client is not None else build_client(settings)

    def run(self, ticks: int) -> RunResult:
        prices: dict[str, float] = {}
        starting_equity = self.portfolio.market_value(prices) or self.settings.starting_cash
        result = RunResult(
            starting_equity=starting_equity,
            ending_equity=starting_equity,
            model=getattr(self.client, "name", "unknown"),
        )

        for _ in range(ticks):
            quotes = self.feed.advance()
            prices = {t: q.price for t, q in quotes.items()}
            decisions: list[Decision] = []

            for ticker, quote in quotes.items():
                decision = self.client.decide(quote)
                decisions.append(decision)
                self._apply(decision, quote.price)
                logger.info(
                    "tick=%d %s %s conf=%.2f price=%.2f (%s)",
                    self.feed.tick,
                    decision.ticker,
                    decision.action,
                    decision.confidence,
                    quote.price,
                    decision.rationale,
                )

            equity = self.portfolio.market_value(prices)
            result.ticks.append(
                TickReport(tick=self.feed.tick, decisions=decisions, equity=equity)
            )

        result.ending_equity = self.portfolio.market_value(prices)
        return result

    def _apply(self, decision: Decision, price: float) -> None:
        if decision.action == "BUY":
            self.portfolio.buy(
                decision.ticker, price, _MAX_BUY_FRACTION * decision.confidence
            )
        elif decision.action == "SELL":
            self.portfolio.sell(
                decision.ticker, price, _MAX_SELL_FRACTION * decision.confidence
            )
