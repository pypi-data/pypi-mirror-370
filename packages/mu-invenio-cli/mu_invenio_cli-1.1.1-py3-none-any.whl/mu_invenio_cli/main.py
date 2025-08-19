from mu_invenio_cli.cli_context import CLIContext
from mu_invenio_cli.states.not_selected_state import NotSelectedState
from mu_invenio_cli.states.selected_state import SelectedState
from mu_invenio_cli.states.configuration_state import ConfigurationState
from mu_invenio_cli.states.state import State
from mu_invenio_cli.states.helper_state import HelperState


def main():
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
