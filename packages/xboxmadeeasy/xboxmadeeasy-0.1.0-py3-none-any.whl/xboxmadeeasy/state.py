class ControllerState:
    def __init__(self):
        self.buttons = {}  # e.g. {0: True}
        self.axes = {}     # e.g. {0: -0.5, 1: 0.0}

    def get_button(self, name):
        mapping = {
            "A": 0, "B": 1, "X": 2, "Y": 3,
            "LB": 4, "RB": 5, "BACK": 6, "START": 7,
            "LS": 8, "RS": 9
        }
        return self.buttons.get(mapping.get(name), False)

    def get_axis(self, name):
        mapping = {
            "LX": 0, "LY": 1, "RX": 3, "RY": 4,
            "LT": 2, "RT": 5
        }
        return self.axes.get(mapping.get(name), 0.0)

controller_state = ControllerState()