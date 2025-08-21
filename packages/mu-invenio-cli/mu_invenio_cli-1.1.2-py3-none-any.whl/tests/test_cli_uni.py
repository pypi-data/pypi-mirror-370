#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Unit tests for the MU Invenio CLI application states and context management."""

import unittest
from mu_invenio_cli.cli_context import CLIContext
from mu_invenio_cli.states.configuration_state import ConfigurationState
from mu_invenio_cli.states.not_selected_state import NotSelectedState


class TestCLIContext(unittest.TestCase):
    def test_initial_state(self):
        ctx = CLIContext()
        self.assertEqual(ctx.state.name, "CONFIGURATION")
        self.assertEqual(ctx.last_state.name, "CONFIGURATION")
        self.assertIsInstance(ctx.config, dict)


class TestConfigurationState(unittest.TestCase):
    def setUp(self):
        self.ctx = CLIContext()
        self.state = ConfigurationState(self.ctx)

    def test_is_config_complete_false(self):
        self.ctx.config = {"BASE_API_URL": None, "API_TOKEN": None, "MODEL": None}
        self.assertFalse(self.state.is_config_complete())

    def test_is_config_complete_true(self):
        self.ctx.config = {"BASE_API_URL": "url", "API_TOKEN": "token", "MODEL": "model"}
        self.assertTrue(self.state.is_config_complete())


class TestNotSelectedState(unittest.TestCase):
    def setUp(self):
        self.ctx = CLIContext()
        self.state = NotSelectedState(self.ctx)

    def test_clear_state(self):
        self.ctx.selected_id = "123"
        self.ctx.json_body = {"a": 1}
        self.ctx.selected_data = {"b": 2}
        self.state.clear_state()
        self.assertIsNone(self.ctx.selected_id)
        self.assertIsNone(self.ctx.json_body)
        self.assertIsNone(self.ctx.selected_data)

if __name__ == "__main__":
    unittest.main()
