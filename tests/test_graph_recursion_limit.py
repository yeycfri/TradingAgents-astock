from __future__ import annotations

from unittest.mock import MagicMock, patch

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


def test_trading_graph_uses_configured_recursion_limit(tmp_path):
    config = DEFAULT_CONFIG.copy()
    config.update(
        {
            "data_cache_dir": str(tmp_path / "cache"),
            "results_dir": str(tmp_path / "logs"),
            "memory_log_path": str(tmp_path / "memory" / "trading_memory.md"),
            "max_recur_limit": 250,
        }
    )

    fake_llm_client = MagicMock()
    fake_llm_client.get_llm.return_value = MagicMock()

    fake_workflow = MagicMock()
    fake_workflow.compile.return_value = MagicMock()

    with (
        patch("tradingagents.graph.trading_graph.create_llm_client", return_value=fake_llm_client),
        patch("tradingagents.graph.trading_graph.GraphSetup") as graph_setup_cls,
    ):
        graph_setup_cls.return_value.setup_graph.return_value = fake_workflow

        graph = TradingAgentsGraph(config=config)

    assert graph.propagator.max_recur_limit == 250


def test_default_recursion_limit_allows_full_astock_workflow():
    assert DEFAULT_CONFIG["max_recur_limit"] >= 250
