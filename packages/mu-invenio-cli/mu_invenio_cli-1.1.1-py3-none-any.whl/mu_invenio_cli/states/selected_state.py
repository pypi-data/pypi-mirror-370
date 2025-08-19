from .base_state import BaseState


class SelectedState(BaseState):
    def handle(self):
        print("Selected State")
