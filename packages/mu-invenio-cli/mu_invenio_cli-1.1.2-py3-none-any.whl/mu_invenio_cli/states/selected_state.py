#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Selected state for the MU Invenio CLI application.
This state handles the actions when the draft is selected.
"""

from .base_state import BaseState


class SelectedState(BaseState):
    def handle(self):
        print("Selected State")
