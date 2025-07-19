from enum import IntEnum
from textual.widgets import Button


class ToggleButton(Button):
    """Custom toggle button that changes between PUT and CALL"""

    def __init__(self, **kwargs):
        super().__init__("CALL", **kwargs)
        self.is_call = True
        self.add_class("toggle-call")

    def toggle(self):
        self.is_call = not self.is_call
        if self.is_call:
            self.label = "CALL"
            self.remove_class("toggle-put")
            self.add_class("toggle-call")
        else:
            self.label = "PUT"
            self.remove_class("toggle-call")
            self.add_class("toggle-put")

    def get_direction(self):
        if self.is_call:
            return "CALL"
        return "PUT"

    def on_button_pressed(self):
        self.toggle()


class DynamicButton(Button):
    class States(IntEnum):
        FETCH_DATES = 0
        FETCH_OPTION_CHAIN = 1
        RESET = 2

    STATE_LABELS = {
        States.FETCH_DATES: "Fetch Dates",
        States.FETCH_OPTION_CHAIN: "Fetch Options",
        States.RESET: "Reset Choices",
    }

    # all the same css for now
    STATE_CLASSES = {
        States.FETCH_DATES: "state-dates",
        States.FETCH_OPTION_CHAIN: "state-chain",
        States.RESET: "reset",
    }

    def __init__(self, **kwargs):
        self.states = DynamicButton.States
        self.state = self.states.FETCH_DATES
        super().__init__(
            label=DynamicButton.STATE_LABELS[self.state],
            classes=DynamicButton.STATE_CLASSES[self.state],
            **kwargs,
        )

    def on_button_pressed(self):
        if self.state == self.States.RESET:
            self.reset_state()
            return
        self.remove_class(DynamicButton.STATE_CLASSES[self.state])
        self.state = DynamicButton.States((self.state + 1) % len(DynamicButton.States))
        self.label = DynamicButton.STATE_LABELS[self.state]
        self.add_class(DynamicButton.STATE_CLASSES[self.state])

    def update_disabled_state(
        self, ticker: str = "", date: str = "", option_selected: bool = False
    ):
        if self.state == self.states.FETCH_DATES:
            self.disabled = not ticker.strip()
        elif self.state == self.states.FETCH_OPTION_CHAIN:
            self.disabled = not (ticker.strip() and date.strip())
        elif self.state == self.states.RESET:
            self.disabled = not option_selected

    def get_current_state(self):
        return self.state

    def reset_state(self):
        self.remove_class(DynamicButton.STATE_CLASSES[self.state])
        self.state = self.states.FETCH_DATES
        self.label = DynamicButton.STATE_LABELS[self.state]
        self.add_class(DynamicButton.STATE_CLASSES[self.state])
