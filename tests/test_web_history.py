from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from web import history
from web.components.sidebar import _history_label


def _write_log(root: Path, ticker: str, trade_date: str) -> Path:
    path = root / ticker / "TradingAgentsStrategy_logs" / f"full_states_log_{trade_date}.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"company_of_interest": ticker}), encoding="utf-8")
    return path


def test_get_history_includes_stock_name(monkeypatch, tmp_path):
    _write_log(tmp_path, "600519", "2026-06-08")

    monkeypatch.setattr(history, "_results_dir", lambda: tmp_path)
    monkeypatch.setattr(history, "_stock_name_for", lambda ticker: {"600519": "贵州茅台"}.get(ticker))

    assert history.get_history() == [
        {
            "ticker": "600519",
            "stock_name": "贵州茅台",
            "date": "2026-06-08",
            "path": str(
                tmp_path
                / "600519"
                / "TradingAgentsStrategy_logs"
                / "full_states_log_2026-06-08.json"
            ),
        }
    ]


def test_history_label_uses_code_name_date():
    assert (
        _history_label({"ticker": "600519", "stock_name": "贵州茅台", "date": "2026-06-08"})
        == "600519-贵州茅台-2026.06.08"
    )


def test_history_label_falls_back_without_name():
    assert _history_label({"ticker": "600519", "date": "2026-06-08"}) == "600519-2026.06.08"


def test_stock_name_falls_back_to_eastmoney_when_mootdx_map_fails(monkeypatch):
    history._stock_name_for.cache_clear()

    response = MagicMock()
    response.json.return_value = {
        "rc": 0,
        "data": {
            "f57": "600519",
            "f58": "贵州茅台",
        },
    }

    def fail_build_name_code_map():
        raise ValueError("not enough values to unpack (expected 2, got 0)")

    monkeypatch.setattr(
        "tradingagents.dataflows.a_stock._build_name_code_map",
        fail_build_name_code_map,
    )
    monkeypatch.setattr("tradingagents.dataflows.a_stock._em_get", lambda *args, **kwargs: response)

    assert history._stock_name_for("600519") == "贵州茅台"
    history._stock_name_for.cache_clear()


def test_stock_name_falls_back_to_eastmoney_search_when_quote_request_fails(monkeypatch):
    history._stock_name_for.cache_clear()

    search_response = MagicMock()
    search_response.json.return_value = {
        "QuotationCodeTable": {
            "Data": [
                {
                    "Code": "600519",
                    "Name": "贵州茅台",
                    "Classify": "AStock",
                }
            ]
        }
    }

    def fail_build_name_code_map():
        raise ValueError("not enough values to unpack (expected 2, got 0)")

    def fake_em_get(url, *args, **kwargs):
        if "qt/stock/get" in url:
            raise ConnectionError("remote disconnected")
        return search_response

    monkeypatch.setattr(
        "tradingagents.dataflows.a_stock._build_name_code_map",
        fail_build_name_code_map,
    )
    monkeypatch.setattr("tradingagents.dataflows.a_stock._em_get", fake_em_get)

    assert history._stock_name_for("600519") == "贵州茅台"
    history._stock_name_for.cache_clear()
