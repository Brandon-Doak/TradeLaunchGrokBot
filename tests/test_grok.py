from tradelaunch.config import Settings
from tradelaunch.grok import MockGrokClient, RealGrokClient, build_client
from tradelaunch.market import Quote


def _quote(price, prev):
    return Quote(ticker="BTC-USD", price=price, prev_price=prev)


def test_mock_client_buys_on_up_move():
    d = MockGrokClient().decide(_quote(105.0, 100.0))
    assert d.action == "BUY"
    assert 0.0 <= d.confidence <= 1.0


def test_mock_client_sells_on_down_move():
    assert MockGrokClient().decide(_quote(95.0, 100.0)).action == "SELL"


def test_mock_client_holds_on_flat_move():
    assert MockGrokClient().decide(_quote(100.1, 100.0)).action == "HOLD"


def test_build_client_selects_mock_without_key():
    assert isinstance(build_client(Settings()), MockGrokClient)


def test_build_client_selects_real_with_key():
    settings = Settings(grok_api_key="test-key")
    assert isinstance(build_client(settings), RealGrokClient)


class _FakeResponse:
    def __init__(self, content):
        self._content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


class _FakeSession:
    def __init__(self, content):
        self._content = content
        self.calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "json": json})
        return _FakeResponse(self._content)


def test_real_client_parses_json_decision():
    session = _FakeSession('{"action": "BUY", "confidence": 0.8, "rationale": "trend up"}')
    client = RealGrokClient(Settings(grok_api_key="k"), session=session)
    d = client.decide(_quote(110.0, 100.0))
    assert d.action == "BUY"
    assert d.confidence == 0.8
    assert d.rationale == "trend up"
    assert session.calls[0]["url"].endswith("/chat/completions")
    assert session.calls[0]["headers"]["Authorization"] == "Bearer k"


def test_real_client_defaults_to_hold_on_bad_response():
    client = RealGrokClient(Settings(grok_api_key="k"), session=_FakeSession("not json"))
    assert client.decide(_quote(110.0, 100.0)).action == "HOLD"
