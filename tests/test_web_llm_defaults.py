from __future__ import annotations

from tradingagents.llm_clients.model_catalog import get_model_options
from web.components import sidebar
from web.llm_defaults import DEFAULT_DEEP_MODEL, DEFAULT_LLM_PROVIDER, DEFAULT_QUICK_MODEL


def test_web_defaults_to_xiaomi_mimo_provider_and_models():
    assert DEFAULT_LLM_PROVIDER == "xiaomi"
    assert DEFAULT_QUICK_MODEL == "mimo-v2.5"
    assert DEFAULT_DEEP_MODEL == "mimo-v2.5-pro"


def test_sidebar_provider_order_starts_with_xiaomi():
    assert sidebar._PROVIDER_KEYS[0] == DEFAULT_LLM_PROVIDER


def test_web_default_models_match_xiaomi_catalog_first_options():
    assert get_model_options(DEFAULT_LLM_PROVIDER, "quick")[0][1] == DEFAULT_QUICK_MODEL
    assert get_model_options(DEFAULT_LLM_PROVIDER, "deep")[0][1] == DEFAULT_DEEP_MODEL
