"""Command-line entry point for TradeLaunchGrokBot."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from . import __version__
from .bot import RunResult, TradingBot
from .config import Settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tradelaunch",
        description="TradeLaunchGrokBot - a paper-trading bot driven by Grok (xAI).",
    )
    parser.add_argument("--version", action="version", version=f"tradelaunch {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a paper-trading session.")
    run.add_argument("--ticks", type=int, default=10, help="Number of market ticks to simulate.")
    run.add_argument("--seed", type=int, default=42, help="Market data random seed.")
    run.add_argument("--json", action="store_true", help="Emit a JSON summary instead of text.")
    run.add_argument("--verbose", action="store_true", help="Log every per-ticker decision.")
    return parser


def _summary_dict(result: RunResult, settings: Settings) -> dict:
    return {
        "model": result.model,
        "using_real_grok": settings.use_real_grok,
        "tickers": settings.tickers,
        "ticks": len(result.ticks),
        "starting_equity": round(result.starting_equity, 2),
        "ending_equity": round(result.ending_equity, 2),
        "pnl": round(result.pnl, 2),
        "pnl_pct": round(result.pnl_pct, 3),
    }


def _print_text(summary: dict) -> None:
    mode = "Grok (xAI)" if summary["using_real_grok"] else "offline mock model"
    print("TradeLaunchGrokBot paper-trading run")
    print(f"  model         : {summary['model']} ({mode})")
    print(f"  tickers       : {', '.join(summary['tickers'])}")
    print(f"  ticks         : {summary['ticks']}")
    print(f"  start equity  : ${summary['starting_equity']:,.2f}")
    print(f"  end equity    : ${summary['ending_equity']:,.2f}")
    print(f"  pnl           : ${summary['pnl']:,.2f} ({summary['pnl_pct']:+.3f}%)")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "run":
        logging.basicConfig(
            level=logging.INFO if args.verbose else logging.WARNING,
            format="%(message)s",
        )
        settings = Settings.from_env()
        bot = TradingBot(settings, seed=args.seed)
        result = bot.run(ticks=args.ticks)
        summary = _summary_dict(result, settings)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            _print_text(summary)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
