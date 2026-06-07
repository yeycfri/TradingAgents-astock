import unittest

from web.components.report_viewer import _ANALYST_SECTIONS


class WebReportViewerTests(unittest.TestCase):
    def test_analyst_sections_render_in_requested_display_order(self):
        self.assertEqual(
            [key for key, _ in _ANALYST_SECTIONS],
            [
                "fundamentals_report",
                "sentiment_report",
                "news_report",
                "market_report",
                "policy_report",
                "hot_money_report",
                "lockup_report",
            ],
        )

