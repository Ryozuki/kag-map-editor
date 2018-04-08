import pygame

class Input:
    def __init__(self):
        self.mouse_left = False
        self.mouse_right = False
        self.mouse_wheel = 0
        self.prev_mouse_status = None
        self.mouse_status = None
        self.prev_keyboard_status = None
        self.keyboard_status = None

    def update(self):
        self.prev_mouse_status = self.mouse_status
        self.mouse_status = pygame.mouse.get_pressed()
        self.prev_keyboard_status = self.keyboard_status
        self.keyboard_status = pygame.key.get_pressed()

    def is_pressed(self, key):
        if self.mouse_status is None:
            return False
        return self.keyboard_status[key] == 1

    def is_click(self, key):
        if self.prev_keyboard_status is None or self.keyboard_status is None:
            return False
        return self.prev_keyboard_status[key] == 1 and self.keyboard_status[key] == 0

    def is_mouse_pressed(self, button):
        if self.mouse_status is None:
            return False
        return self.mouse_status[button] == 1

    def is_mouse_click(self, button):
        if self.prev_mouse_status is None or self.mouse_status is None:
            return False
        return self.prev_mouse_status[button] == 1 and self.mouse_status[button] == 0

    def mouse_pos(self):
        return pygame.mouse.get_pos()
