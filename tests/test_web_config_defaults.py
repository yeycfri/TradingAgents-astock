from __future__ import annotations

from web.config_defaults import WEB_MAX_DEBATE_ROUNDS, WEB_MAX_RISK_DISCUSS_ROUNDS


def test_web_risk_debate_rounds_defaults_to_one():
    assert WEB_MAX_RISK_DISCUSS_ROUNDS == 1


def test_web_debate_rounds_remains_three():
    assert WEB_MAX_DEBATE_ROUNDS == 3
