import sys
import os
import pygame
from tileloader import KagImage, Tile, TileMap
from input import Input

__version__ = "0.0.1"

RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sprites")


HELP_TEXT = """Controls:
    - F1: Opens the help menu
    - F2: Enters mapping mode
    - ESC: Goes to the menu

While being in mapping mode:
    - Left mouse: Places the selected tile, you can hold it down and use it as a brush.
    - W A S D: Move the camera
    - K: To save the map"""


def get_path(file: str) -> str:
    """Gets the resource absolute path"""
    return os.path.join(RESOURCE_PATH, file)


class Editor:
    def __init__(self):
        self._running = True
        self.size = self.width, self.height = 1024, 768
        self.sprites = {}
        self.display = None
        self.map = TileMap(200, 100)
        self.input = Input()
        self.map_offset = [0, 0]
        self.last_coords = None
        self.font = None
        self.tip_label = None
        self.help_label = None
        self.version_label = None
        self.status = 0
        self.last_status = 0
        self.selected_tile_name = "Dirt Background"
        self.fps_label = None
        self.clock = None

    def set_status(self, n):
        if self.status == n: # Don't lose info if it's the same.
            return
        self.last_status = self.status
        self.status = n

    def on_load(self):
        self.sprites["world"] = KagImage(get_path("world.png"))
        self.sprites["background"] = KagImage(get_path("Back/BackgroundCastle.png"))
        self.sprites["background"].scale_by(2, 2)

    def on_init(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(get_path("font/uni0553.ttf"), 18)

        self.tip_label = self.font.render("Press F1 for help!", 0, (255, 255, 255))
        self.help_label = self.font.render(HELP_TEXT, 0, (255, 255, 255))
        self.version_label = self.font.render("Version: " + __version__, 0, (255, 255, 255))
        self.fps_label = self.font.render("FPS: 0", 0, (255, 255, 255))

        self.display = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        pygame.display.set_caption("King Arthur's Gold Map Editor by Ryozuki")

    def render_multiline_text(self, position, text: str, font: pygame.font.Font, color=(255, 255, 255), antialias=0):
        lines = text.splitlines()
        for x in lines:
            text = x.replace('\t', '    ')
            width, height = font.size(text)
            label = font.render(text, antialias, color)
            self.display.blit(label, position)
            position[1] += height

    def on_event(self, event: pygame.event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.on_mouse_wheel_up()
            elif event.button == 5:
                self.on_mouse_wheel_down()

    def on_mouse_wheel_down(self):
        self.map.set_zoom(False)

    def on_mouse_wheel_up(self):
        self.map.set_zoom(True)

    def add_offset(self, x=0, y=0):
        if x == 0 and y == 0:
            return
        self.map_offset[0] += x
        self.map_offset[1] += y

    def on_update(self):
        self.input.update()

        if self.status == 0: # Menu
            if self.input.is_click(pygame.K_F2):
                self.set_status(1)
            elif self.input.is_click(pygame.K_F1):
                self.set_status(2)
        elif self.status == 1: # Mapping:
            if self.input.is_click(pygame.K_ESCAPE):
                # TODO: Ask for save or something?
                self.set_status(0)
            elif self.input.is_click(pygame.K_F1):
                self.set_status(2)
            elif self.input.is_click(pygame.K_k):
                self.map.save_map()

            if self.input.is_pressed(pygame.K_a):
                self.add_offset(self.map.tile_size // 4)
            elif self.input.is_pressed(pygame.K_d):
                self.add_offset(-self.map.tile_size // 4)

            if self.input.is_pressed(pygame.K_w):
                self.add_offset(0, self.map.tile_size // 4)
            elif self.input.is_pressed(pygame.K_s):
                self.add_offset(0, -self.map.tile_size // 4)

            # Update tile if mouse pressed in a new coord and is another type of tile.
            if self.input.is_mouse_pressed(0):
                coords = self.map.get_map_coords_from_mouse(self.input.mouse_pos(), self.map_offset)
                if coords[0] < 0 or coords[1] < 0 or coords[0] >= self.map.width or coords[1] >= self.map.height:
                    print("Tried to add tile outside of bounds.")
                else:
                    if self.last_coords is None or (self.last_coords[0] != coords[0] or self.last_coords[1] != coords[1]):
                        # TODO: Add an "and selected_tile_name == old_tile_name"
                        self.last_coords = coords
                        x, y = coords
                        self.map.set_tile(x, y, self.selected_tile_name)
                        print("Put tile in:", coords)
        elif self.status == 2: # Help
            if self.input.is_click(pygame.K_ESCAPE):
                self.set_status(0)
            if self.input.is_click(pygame.K_F2):
                self.set_status(1)
            if self.input.is_click(pygame.K_F1):
                self.set_status(self.last_status)

    def on_render(self):
        self.display.fill((59, 112, 118))
        self.sprites["background"].draw_scaled_bg(self.display, (-100, -100))

        if self.status == 1: # Mapping
            self.map.draw(self.display, self.sprites, self.map_offset)

        if self.status == 2: # Help
            self.render_multiline_text([40, 40], HELP_TEXT, self.font)

        self.display.blit(self.tip_label, (20, self.height - self.font.get_height() - 20))
        self.fps_label = self.font.render("FPS: %.2f" % self.clock.get_fps(), 0, (255, 255, 255))
        self.display.blit(self.fps_label, (20, 20))
        self.display.blit(self.version_label, (self.width - self.version_label.get_size()[0] - 20, self.height - self.font.get_height() - 20))

        pygame.display.update()

    def on_execute(self):
        self.on_init()
        self.on_load()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update()
            self.on_render()
            self.clock.tick(144)

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    editor = Editor()
    editor.on_execute()
