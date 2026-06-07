import unittest
from unittest.mock import Mock, patch

from tradingagents.dataflows import a_stock


class AStockFinancialReportTests(unittest.TestCase):
    def test_sina_financial_report_parses_current_report_list_schema(self):
        payload = {
            "result": {
                "data": {
                    "report_list": {
                        "20260331": {
                            "data": [
                                {
                                    "item_title": "资产总计",
                                    "item_value": "1000.000000",
                                    "item_display_type": 2,
                                },
                                {
                                    "item_title": "负债合计",
                                    "item_value": "450.000000",
                                    "item_display_type": 2,
                                },
                            ],
                        },
                        "20251231": {
                            "data": [
                                {
                                    "item_title": "资产总计",
                                    "item_value": "900.000000",
                                    "item_display_type": 2,
                                },
                                {
                                    "item_title": "负债合计",
                                    "item_value": "360.000000",
                                    "item_display_type": 2,
                                },
                            ],
                        },
                    },
                },
            },
        }
        response = Mock()
        response.json.return_value = payload

        with patch.object(a_stock._DIRECT_SESSION, "get", return_value=response):
            report = a_stock.get_balance_sheet("603308", "quarterly", "2026-06-05")

        self.assertIn("Balance Sheet for 603308", report)
        self.assertIn("报告日", report)
        self.assertIn("资产总计", report)
        self.assertIn("负债合计", report)
        self.assertIn("2026-03-31", report)
        self.assertIn("2025-12-31", report)

    def test_eastmoney_session_ignores_environment_proxies(self):
        self.assertFalse(a_stock._EM_SESSION.trust_env)

    def test_domestic_data_session_ignores_environment_proxies(self):
        self.assertFalse(a_stock._DIRECT_SESSION.trust_env)
