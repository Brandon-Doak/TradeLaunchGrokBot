"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _parse_tickers(raw: str) -> list[str]:
    return [t.strip().upper() for t in raw.split(",") if t.strip()]


@dataclass
class Settings:
    """All tunable settings for a bot run.

    Values default to a fully offline configuration so the bot runs
    end-to-end without any credentials. Supplying ``GROK_API_KEY`` switches
    the strategy over to the real xAI API.
    """

    grok_api_key: str = ""
    grok_base_url: str = "https://api.x.ai/v1"
    grok_model: str = "grok-2-latest"
    tickers: list[str] = field(default_factory=lambda: ["BTC-USD", "ETH-USD", "SOL-USD"])
    starting_cash: float = 10_000.0

    @property
    def use_real_grok(self) -> bool:
        return bool(self.grok_api_key.strip())

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "Settings":
        env = os.environ if environ is None else environ
        tickers_raw = env.get("TRADELAUNCH_TICKERS", "").strip()
        cash_raw = env.get("TRADELAUNCH_STARTING_CASH", "").strip()

        settings = cls()
        settings.grok_api_key = env.get("GROK_API_KEY", "").strip()
        settings.grok_base_url = env.get("GROK_BASE_URL", settings.grok_base_url).strip()
        settings.grok_model = env.get("GROK_MODEL", settings.grok_model).strip()
        if tickers_raw:
            settings.tickers = _parse_tickers(tickers_raw)
        if cash_raw:
            settings.starting_cash = float(cash_raw)
        return settings
