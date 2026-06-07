import unittest
from unittest.mock import patch

from tradingagents.llm_clients.factory import create_llm_client
from tradingagents.llm_clients.model_catalog import get_model_options
from tradingagents.llm_clients.openai_client import OpenAIClient


class XiaomiMiMoProviderTests(unittest.TestCase):
    def test_factory_routes_xiaomi_to_openai_compatible_client(self):
        client = create_llm_client("xiaomi", "mimo-v2.5")

        self.assertIsInstance(client, OpenAIClient)
        self.assertEqual(client.provider, "xiaomi")

    def test_xiaomi_client_uses_official_base_url_and_api_key_env(self):
        with patch.dict("os.environ", {"XIAOMI_API_KEY": "mimo-key"}, clear=True):
            with patch("tradingagents.llm_clients.openai_client.NormalizedChatOpenAI") as chat_cls:
                OpenAIClient("mimo-v2.5", provider="xiaomi").get_llm()

        chat_cls.assert_called_once()
        kwargs = chat_cls.call_args.kwargs
        self.assertEqual(kwargs["model"], "mimo-v2.5")
        self.assertEqual(kwargs["base_url"], "https://api.xiaomimimo.com/v1")
        self.assertEqual(kwargs["api_key"], "mimo-key")
        self.assertFalse(kwargs["http_client"].trust_env)
        self.assertFalse(kwargs["http_async_client"].trust_env)
        self.assertNotIn("use_responses_api", kwargs)

    def test_overseas_openai_provider_keeps_default_proxy_behavior(self):
        with patch("tradingagents.llm_clients.openai_client.NormalizedChatOpenAI") as chat_cls:
            OpenAIClient("gpt-5.4-mini", provider="openai").get_llm()

        kwargs = chat_cls.call_args.kwargs
        self.assertNotIn("http_client", kwargs)
        self.assertNotIn("http_async_client", kwargs)

    def test_qwen_uses_domestic_endpoint_and_no_proxy_clients(self):
        with patch.dict("os.environ", {"DASHSCOPE_API_KEY": "qwen-key"}, clear=True):
            with patch("tradingagents.llm_clients.openai_client.NormalizedChatOpenAI") as chat_cls:
                OpenAIClient("qwen-plus", provider="qwen").get_llm()

        kwargs = chat_cls.call_args.kwargs
        self.assertEqual(kwargs["base_url"], "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.assertFalse(kwargs["http_client"].trust_env)
        self.assertFalse(kwargs["http_async_client"].trust_env)

    def test_xiaomi_missing_api_key_names_required_env_var(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError) as raised:
                OpenAIClient("mimo-v2.5", provider="xiaomi").get_llm()

        self.assertIn("XIAOMI_API_KEY", str(raised.exception))
        self.assertIn("xiaomi", str(raised.exception))

    def test_xiaomi_catalog_defaults_match_requested_models(self):
        self.assertEqual(get_model_options("xiaomi", "quick")[0][1], "mimo-v2.5")
        self.assertEqual(get_model_options("xiaomi", "deep")[0][1], "mimo-v2.5-pro")
