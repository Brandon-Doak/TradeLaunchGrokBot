from tradelaunch.portfolio import Portfolio


def test_buy_spends_cash_and_adds_position():
    p = Portfolio(cash=1000.0)
    fill = p.buy("BTC-USD", price=100.0, cash_fraction=0.5)
    assert fill is not None
    assert p.cash == 500.0
    assert p.position("BTC-USD") == 5.0
    assert fill.notional == 500.0


def test_sell_reduces_position_and_returns_cash():
    p = Portfolio(cash=0.0, positions={"ETH-USD": 4.0})
    fill = p.sell("ETH-USD", price=50.0, position_fraction=0.5)
    assert fill is not None
    assert p.position("ETH-USD") == 2.0
    assert p.cash == 100.0


def test_buy_without_cash_is_noop():
    p = Portfolio(cash=0.0)
    assert p.buy("BTC-USD", price=100.0, cash_fraction=1.0) is None


def test_sell_without_position_is_noop():
    p = Portfolio(cash=0.0)
    assert p.sell("BTC-USD", price=100.0, position_fraction=1.0) is None


def test_market_value_marks_positions_to_market():
    p = Portfolio(cash=100.0, positions={"BTC-USD": 2.0})
    assert p.market_value({"BTC-USD": 150.0}) == 400.0
