#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
"""Main entry point for the MU Invenio CLI application."""

from mu_invenio_cli.cli_context import CLIContext
from mu_invenio_cli.states.not_selected_state import NotSelectedState
from mu_invenio_cli.states.selected_state import SelectedState
from mu_invenio_cli.states.configuration_state import ConfigurationState
from mu_invenio_cli.states.state import State
from mu_invenio_cli.states.helper_state import HelperState


def main():
    try:
        run()
    except KeyboardInterrupt:
        print("\nExiting the CLI application.")
        exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


def run():
    context = CLIContext()
    state = ConfigurationState(context)
    while True:
        state.handle()
        match context.state:
            case State.CONFIGURATION:
                state = ConfigurationState(context)
            case State.NOT_SELECTED:
                state = NotSelectedState(context)
            case State.SELECTED:
                state = SelectedState(context)
            case State.HELP:
                state = HelperState(context)
            case _:
                state = ConfigurationState(context)


if __name__ == "__main__":
    main()
