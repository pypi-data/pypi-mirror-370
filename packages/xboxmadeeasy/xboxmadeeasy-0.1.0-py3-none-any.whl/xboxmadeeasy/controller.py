import pygame
from .state import controller_state

class XboxController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def update(self):
        pygame.event.pump()
        # Buttons
        for i in range(self.joystick.get_numbuttons()):
            controller_state.buttons[i] = self.joystick.get_button(i)
        # Axes (sticks and triggers)
        for i in range(self.joystick.get_numaxes()):
            controller_state.axes[i] = round(self.joystick.get_axis(i), 3)