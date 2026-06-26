"""Browser title helpers for the Streamlit web UI."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit.components.v1 as components

from web.history import _stock_name_for

DEFAULT_PAGE_TITLE = "TradingAgents-Astock A股分析"


def analysis_page_title(ticker: str, trade_date: str) -> str:
    """Return the browser title for an active or completed analysis."""

    stock_name = _stock_name_for(ticker) or ticker
    display_date = trade_date.replace("-", ".")
    return f"{stock_name}-{display_date}"


def title_script(title: str) -> str:
    """Return JavaScript that sets the parent Streamlit document title."""

    encoded = json.dumps(title, ensure_ascii=False)
    return f"<script>window.parent.document.title = {encoded};</script>"


def page_config_title(session_state) -> str:
    """Return the title to pass to st.set_page_config for the current UI state."""

    viewing_history = session_state.get("viewing_history")
    if viewing_history:
        try:
            path = Path(viewing_history)
            ticker = path.parent.parent.name
            trade_date = path.stem.replace("full_states_log_", "")
            return analysis_page_title(ticker, trade_date)
        except Exception:
            return DEFAULT_PAGE_TITLE

    start_req = session_state.get("start_analysis")
    if start_req:
        return analysis_page_title(start_req["ticker"], start_req["trade_date"])

    tracker = session_state.get("tracker")
    if tracker and (tracker.is_running or tracker.is_complete):
        return analysis_page_title(tracker.ticker, tracker.trade_date)

    return DEFAULT_PAGE_TITLE


def render_browser_title(title: str) -> None:
    """Update the browser tab title from inside Streamlit."""

    components.html(title_script(title), height=0, width=0)
