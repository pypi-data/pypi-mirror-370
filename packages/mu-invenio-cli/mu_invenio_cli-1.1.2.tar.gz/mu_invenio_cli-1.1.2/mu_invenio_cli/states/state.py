#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
"""State management enum for the MU Invenio CLI application."""

from enum import Enum


class State(Enum):
    CONFIGURATION = 1
    NOT_SELECTED = 2
    SELECTED = 3
    HELP = 4
