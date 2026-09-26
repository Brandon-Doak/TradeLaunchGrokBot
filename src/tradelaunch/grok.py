"""Grok (xAI) decision clients.

Two interchangeable clients implement the same interface:

* ``MockGrokClient`` - a deterministic, offline momentum heuristic used when
  no API key is configured. It lets the whole bot run end-to-end with no
  network access or credentials.
* ``RealGrokClient`` - calls the xAI OpenAI-compatible chat completions API
  and parses a structured JSON decision out of the model response.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from .config import Settings
from .market import Quote

Action = Literal["BUY", "SELL", "HOLD"]
VALID_ACTIONS = ("BUY", "SELL", "HOLD")


@dataclass(frozen=True)
class Decision:
    ticker: str
    action: Action
    confidence: float
    rationale: str


class MockGrokClient:
    """Offline momentum strategy standing in for the Grok model.

    Buys into positive momentum, sells on negative momentum, and holds when
    price movement is negligible. Deterministic given the same quotes.
    """

    name = "mock"

    def decide(self, quote: Quote) -> Decision:
        change = quote.pct_change
        if change > 0.5:
            action: Action = "BUY"
        elif change < -0.5:
            action = "SELL"
        else:
            action = "HOLD"
        confidence = min(1.0, abs(change) / 3.0)
        return Decision(
            ticker=quote.ticker,
            action=action,
            confidence=round(confidence, 3),
            rationale=f"momentum {change:+.2f}% over last tick",
        )


class RealGrokClient:
    """Calls the xAI chat completions endpoint for a trade decision."""

    name = "grok"

    _SYSTEM_PROMPT = (
        "You are a disciplined trading assistant. Given a ticker and its recent "
        "price move, respond ONLY with compact JSON of the form "
        '{"action": "BUY|SELL|HOLD", "confidence": 0.0-1.0, "rationale": "..."}. '
        "Be conservative and prefer HOLD when the signal is weak."
    )

    def __init__(self, settings: Settings, session=None) -> None:
        self._settings = settings
        if session is None:
            import requests  # imported lazily so offline runs need no dependency

            session = requests.Session()
        self._session = session

    def decide(self, quote: Quote) -> Decision:
        payload = {
            "model": self._settings.grok_model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": self._SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Ticker {quote.ticker} is at {quote.price:.2f}, "
                        f"a move of {quote.pct_change:+.2f}% since the last tick. "
                        "What should I do?"
                    ),
                },
            ],
        }
        resp = self._session.post(
            f"{self._settings.grok_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._settings.grok_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return self._parse(quote.ticker, content)

    @staticmethod
    def _parse(ticker: str, content: str) -> Decision:
        try:
            data = json.loads(content)
            action = str(data.get("action", "HOLD")).upper()
            if action not in VALID_ACTIONS:
                action = "HOLD"
            confidence = float(data.get("confidence", 0.0))
            rationale = str(data.get("rationale", "")).strip() or "grok decision"
        except (ValueError, KeyError, TypeError):
            action, confidence, rationale = "HOLD", 0.0, "unparseable grok response"
        return Decision(
            ticker=ticker,
            action=action,  # type: ignore[arg-type]
            confidence=max(0.0, min(1.0, confidence)),
            rationale=rationale,
        )


def build_client(settings: Settings):
    """Return the real client when an API key is present, else the mock."""
    if settings.use_real_grok:
        return RealGrokClient(settings)
    return MockGrokClient()
