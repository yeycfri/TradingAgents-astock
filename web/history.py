"""Manage analysis history by scanning existing log files."""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _results_dir() -> Path:
    return Path.home() / ".tradingagents" / "logs"


@lru_cache(maxsize=512)
def _stock_name_for(ticker: str) -> str | None:
    """Return the Chinese stock name for a 6-digit code when available."""

    if not re.fullmatch(r"\d{6}", ticker):
        return None

    try:
        from tradingagents.dataflows.a_stock import _build_name_code_map

        _, code_to_name = _build_name_code_map()
        stock_name = code_to_name.get(ticker)
        if stock_name:
            return stock_name
    except Exception as exc:
        logger.debug("Unable to resolve stock name from mootdx for %s: %s", ticker, exc)

    try:
        from tradingagents.dataflows.a_stock import _em_get

        market_code = 1 if ticker.startswith("6") else 0
        response = _em_get(
            "https://push2.eastmoney.com/api/qt/stock/get",
            params={
                "fltt": "2",
                "invt": "2",
                "fields": "f57,f58",
                "secid": f"{market_code}.{ticker}",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json().get("data") or {}
        stock_name = str(data.get("f58") or "").strip()
        if stock_name:
            return stock_name
    except Exception as exc:
        logger.debug("Unable to resolve stock name from Eastmoney quote for %s: %s", ticker, exc)

    try:
        from tradingagents.dataflows.a_stock import _em_get

        response = _em_get(
            "https://searchapi.eastmoney.com/api/suggest/get",
            params={
                "input": ticker,
                "type": "14",
                "token": "D43BF722C8E33BDC906FB84D85E326E8",
            },
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("QuotationCodeTable", {}).get("Data", []) or []
        for item in items:
            code = str(item.get("Code", "")).strip()
            stock_name = str(item.get("Name", "")).strip()
            if code == ticker and item.get("Classify") == "AStock" and stock_name:
                return stock_name
    except Exception as exc:
        logger.debug("Unable to resolve stock name from Eastmoney search for %s: %s", ticker, exc)

    return None


def get_history() -> list[dict[str, str]]:
    """Scan saved analysis logs and return a sorted list (newest first).

    Each entry includes ticker, stock_name when known, date, and path.
    """
    root = _results_dir()
    if not root.exists():
        return []

    entries: list[dict[str, str]] = []
    for log_file in root.rglob("full_states_log_*.json"):
        match = re.search(r"full_states_log_(\d{4}-\d{2}-\d{2})\.json$", log_file.name)
        if not match:
            continue
        date = match.group(1)
        ticker = log_file.parent.parent.name
        entry = {"ticker": ticker, "date": date, "path": str(log_file)}
        stock_name = _stock_name_for(ticker)
        if stock_name:
            entry["stock_name"] = stock_name
        entries.append(entry)

    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def load_analysis(path: str) -> dict[str, Any]:
    """Load a saved analysis JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_signal(state: dict[str, Any]) -> str:
    """Extract the short signal (Buy/Sell/Hold) from a final state dict."""
    import re

    for field in (
        "investment_plan",
        "trader_investment_decision",
        "final_trade_decision",
    ):
        text = state.get(field, "")
        if not text:
            continue
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        for keyword in ("BUY", "SELL", "HOLD"):
            if keyword in cleaned.upper():
                return keyword.capitalize()
    return "N/A"
