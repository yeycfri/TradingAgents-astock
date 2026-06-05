"""Tests for default checkpoint configuration across entry points."""

import inspect
import unittest

from cli.main import analyze, run_analysis
from tradingagents.default_config import DEFAULT_CONFIG


class TestCheckpointDefaults(unittest.TestCase):
    def test_checkpointing_is_enabled_by_default(self):
        self.assertTrue(DEFAULT_CONFIG["checkpoint_enabled"])
        self.assertTrue(inspect.signature(run_analysis).parameters["checkpoint"].default)
        option = inspect.signature(analyze).parameters["checkpoint"].default
        self.assertTrue(option.default)
        self.assertEqual(option.param_decls, ("--checkpoint/--no-checkpoint",))


if __name__ == "__main__":
    unittest.main()
