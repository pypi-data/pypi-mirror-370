#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Test if the app can run without error."""

import unittest
from unittest.mock import patch
from mu_invenio_cli import main as cli_main
from mu_invenio_cli.cli_context import CLIContext

class TestMainEntryPoint(unittest.TestCase):
    @patch("builtins.input", side_effect=["0"])
    @patch("sys.exit", side_effect=SystemExit)
    def test_main_exits_from_configuration(self, mock_exit, mock_input):
        with patch("builtins.print"):
            with self.assertRaises(SystemExit) as cm:
                cli_main.main()
        self.assertEqual(cm.exception.code, 0)
        ctx = CLIContext()
        self.assertEqual(ctx.state.name, "CONFIGURATION")