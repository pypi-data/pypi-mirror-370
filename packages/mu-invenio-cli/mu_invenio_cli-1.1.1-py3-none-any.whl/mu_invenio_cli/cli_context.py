from mu_invenio_cli.states.state import State


class CLIContext:
    def __init__(self):
        self.config = {}
        self.selected_id = None
        self.json_body = None
        self.selected_data = None
        self.state = State.CONFIGURATION
        self.last_state = State.CONFIGURATION
