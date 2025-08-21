#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

"""Helper state for the MU Invenio CLI application.
This state provides help options for the user.
"""

from mu_invenio_cli.help_messages import help_config_state
from mu_invenio_cli.states.base_state import BaseState


class HelperState(BaseState):

    def handle(self):
        print("\nHelp:")
        while True:
            print("\nOptions:")
            print("  1. Configuration help")
            print("  9. Back")
            print("  0. Exit")

            choice = input("Select option: ").strip()
            if choice == '1':
                help_config_state()
            elif choice == '9':
                self.context.state = self.context.last_state
                break
            elif choice == '0':
                exit(0)
            else:
                print("Invalid option. Please try again.")
