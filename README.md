# TradeLaunchGrokBot

A small, self-contained **paper-trading bot** that consults **Grok (xAI)** for
BUY / SELL / HOLD decisions on a set of tickers and simulates the resulting
trades against a synthetic market feed.

The bot is designed to run **end-to-end with no credentials**: when no
`GROK_API_KEY` is set it uses a deterministic offline "mock" model, so tests
and demos are fully reproducible and need no network access. Supplying a real
key switches the strategy over to the live xAI API.

## Quick start

```bash
# 1. Set up (creates .venv and installs the package with dev extras)
./.cursor/install.sh

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Run a paper-trading session (offline mock model)
tradelaunch run --ticks 12 --verbose

# JSON summary (handy for scripting / CI)
tradelaunch run --ticks 12 --json
```

You can also run it as a module without installing the console script:

```bash
python -m tradelaunch run --ticks 12
```

## Using the real Grok (xAI) API

Copy `.env.example` to `.env`, set `GROK_API_KEY`, and export the variables
(or use your own loader). The bot reads configuration from the environment:

```bash
export GROK_API_KEY="xai-..."          # enables the live model
export GROK_MODEL="grok-2-latest"
export TRADELAUNCH_TICKERS="BTC-USD,ETH-USD,SOL-USD"
export TRADELAUNCH_STARTING_CASH=10000
tradelaunch run --ticks 20 --verbose
```

When `GROK_API_KEY` is present the bot calls the xAI OpenAI-compatible
`/chat/completions` endpoint and parses a structured JSON decision from the
model's response. Trading is always simulated (paper only) — no real orders
are ever placed.

## Project layout

| Path | Purpose |
| --- | --- |
| `src/tradelaunch/config.py` | Environment-driven `Settings`. |
| `src/tradelaunch/market.py` | Deterministic synthetic market feed. |
| `src/tradelaunch/grok.py` | Mock and real Grok decision clients. |
| `src/tradelaunch/portfolio.py` | Paper-trading portfolio and fills. |
| `src/tradelaunch/bot.py` | Main trading loop. |
| `src/tradelaunch/cli.py` | `tradelaunch` command-line interface. |
| `tests/` | Pytest suite. |

## Development

```bash
source .venv/bin/activate
pytest            # run the test suite
```

## Cloud Agent environment

This repository ships a Cloud Agent environment under `.cursor/`:

- `.cursor/Dockerfile` installs the stable system toolchain (Python 3, pip, venv, git, curl).
- `.cursor/install.sh` creates `.venv` and installs the project with dev extras.
- `.cursor/environment.json` wires the two together.
