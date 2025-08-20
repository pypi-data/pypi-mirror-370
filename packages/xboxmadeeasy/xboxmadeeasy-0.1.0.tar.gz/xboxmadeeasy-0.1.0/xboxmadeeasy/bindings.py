from .state import controller_state

class BindingManager:
    def __init__(self):
        self.bindings = {}  # e.g. {"A": self.jump}

    def bind(self, button_name, function):
        self.bindings[button_name] = function

    def check_and_execute(self):
        for name, func in self.bindings.items():
            if controller_state.get_button(name):
                func()

# Example usage:
# binder = BindingManager()
# binder.bind("A", jump)
# binder.check_and_execute()