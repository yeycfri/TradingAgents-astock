from __future__ import annotations

from types import SimpleNamespace

from web import page_title


def test_analysis_page_title_uses_stock_name_and_date(monkeypatch):
    monkeypatch.setattr(page_title, "_stock_name_for", lambda ticker: {"600519": "贵州茅台"}.get(ticker))

    assert page_title.analysis_page_title("600519", "2026-06-08") == "贵州茅台-2026.06.08"


def test_analysis_page_title_falls_back_to_ticker_when_name_unknown(monkeypatch):
    monkeypatch.setattr(page_title, "_stock_name_for", lambda ticker: None)

    assert page_title.analysis_page_title("600519", "2026-06-08") == "600519-2026.06.08"


def test_title_script_json_escapes_title():
    script = page_title.title_script('贵州"茅台-2026-06-08')

    assert 'document.title = "贵州\\"茅台-2026-06-08";' in script


def test_page_config_title_uses_running_tracker(monkeypatch):
    monkeypatch.setattr(page_title, "_stock_name_for", lambda ticker: {"600519": "贵州茅台"}.get(ticker))
    tracker = SimpleNamespace(ticker="600519", trade_date="2026-06-08", is_running=True, is_complete=False)

    assert page_title.page_config_title({"tracker": tracker}) == "贵州茅台-2026.06.08"


def test_page_config_title_uses_pending_start_request(monkeypatch):
    monkeypatch.setattr(page_title, "_stock_name_for", lambda ticker: {"600519": "贵州茅台"}.get(ticker))

    assert (
        page_title.page_config_title(
            {"start_analysis": {"ticker": "600519", "trade_date": "2026-06-08"}}
        )
        == "贵州茅台-2026.06.08"
    )


def test_page_config_title_uses_viewing_history_path(monkeypatch, tmp_path):
    monkeypatch.setattr(page_title, "_stock_name_for", lambda ticker: {"600519": "贵州茅台"}.get(ticker))
    history_path = (
        tmp_path
        / "600519"
        / "TradingAgentsStrategy_logs"
        / "full_states_log_2026-06-08.json"
    )

    assert page_title.page_config_title({"viewing_history": str(history_path)}) == "贵州茅台-2026.06.08"
