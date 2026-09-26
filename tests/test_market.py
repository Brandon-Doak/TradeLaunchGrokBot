from tradelaunch.market import MarketFeed


def test_feed_is_deterministic_for_a_seed():
    a = MarketFeed(["BTC-USD", "ETH-USD"], seed=7)
    b = MarketFeed(["BTC-USD", "ETH-USD"], seed=7)
    for _ in range(5):
        qa = a.advance()
        qb = b.advance()
        assert {t: q.price for t, q in qa.items()} == {t: q.price for t, q in qb.items()}


def test_advance_increments_tick_and_tracks_prev_price():
    feed = MarketFeed(["BTC-USD"], seed=1)
    first = feed.advance()
    assert feed.tick == 1
    second = feed.advance()
    assert feed.tick == 2
    assert second["BTC-USD"].prev_price == first["BTC-USD"].price


def test_prices_stay_positive():
    feed = MarketFeed(["BTC-USD", "ETH-USD", "SOL-USD"], seed=99)
    for _ in range(50):
        for quote in feed.advance().values():
            assert quote.price > 0
