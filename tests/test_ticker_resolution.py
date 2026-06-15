"""Tests for Chinese A-stock ticker resolution fallbacks."""

import unittest
from unittest.mock import MagicMock, patch

import tradingagents.dataflows.a_stock as a_stock


class TestTickerResolution(unittest.TestCase):
    def setUp(self):
        a_stock._name_to_code = None
        a_stock._code_to_name = None

    def tearDown(self):
        a_stock._name_to_code = None
        a_stock._code_to_name = None
        a_stock._mootdx_client = None

    def test_mootdx_client_retries_with_default_server_when_bestip_is_empty(self):
        client = object()
        calls = []

        def factory(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise ValueError("not enough values to unpack (expected 2, got 0)")
            return client

        with patch("mootdx.quotes.Quotes.factory", side_effect=factory):
            self.assertIs(a_stock._get_mootdx_client(), client)

        self.assertEqual(calls[0], {"market": "std"})
        self.assertEqual(calls[1]["market"], "std")
        self.assertEqual(calls[1]["server"], ("110.41.147.114", 7709))

    def test_resolves_name_via_eastmoney_when_mootdx_has_no_server(self):
        response = MagicMock()
        response.json.return_value = {
            "QuotationCodeTable": {
                "Data": [
                    {
                        "Code": "300750",
                        "Name": "宁德时代",
                        "Classify": "AStock",
                    }
                ]
            }
        }

        with (
            patch("mootdx.quotes.Quotes.factory", side_effect=ValueError(
                "not enough values to unpack (expected 2, got 0)"
            )),
            patch.object(a_stock, "_em_get", return_value=response),
        ):
            self.assertEqual(a_stock.resolve_ticker("宁德时代"), "300750")


if __name__ == "__main__":
    unittest.main()
