from tradelaunch.bot import TradingBot
from tradelaunch.config import Settings


def test_bot_runs_end_to_end_with_mock_client():
    settings = Settings(tickers=["BTC-USD", "ETH-USD"], starting_cash=10_000.0)
    bot = TradingBot(settings, seed=42)
    result = bot.run(ticks=10)

    assert result.model == "mock"
    assert len(result.ticks) == 10
    assert result.starting_equity == 10_000.0
    # Every tick makes a decision per ticker.
    assert all(len(t.decisions) == 2 for t in result.ticks)
    # Equity is finite and non-negative throughout.
    assert all(t.equity >= 0 for t in result.ticks)


def test_bot_run_is_reproducible():
    settings = Settings(tickers=["BTC-USD"], starting_cash=5_000.0)
    a = TradingBot(settings, seed=123).run(ticks=15)
    b = TradingBot(settings, seed=123).run(ticks=15)
    assert a.ending_equity == b.ending_equity


def test_bot_conserves_value_reasonably():
    # With a mock momentum model and no fees, equity should stay a positive number.
    settings = Settings(tickers=["BTC-USD", "ETH-USD", "SOL-USD"], starting_cash=10_000.0)
    result = TradingBot(settings, seed=7).run(ticks=20)
    assert result.ending_equity > 0
