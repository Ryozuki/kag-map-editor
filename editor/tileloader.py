import json
import pygame
import os
from random import randint

TILES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiles.json")
MAPS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps/")
TILE_SIZE = 32

def hex_to_rgb(hex: str):
    hex = hex.lstrip('#')
    return [int(hex[i:i+2], 16) for i in (0, 2, 4)]

class Rect:
    def __init__(self, x, y, w, h):
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h

class Tile:
    def __init__(self, name, color, file_name, coords, visible=True):
        self.visible = visible
        self.name = name
        self.file_name = file_name.rstrip(".png")
        self.color = hex_to_rgb(color)
        self.coords = []
        self.index = None
        self.tile_surface = None

        for x in coords:
            self.coords.append(Rect(x[0], x[1], x[2], x[3]))

    def get_rect(self) -> Rect:
        if self.index is None:
            self.index = randint(0, len(self.coords) - 1)
        return self.coords[self.index]



class TileMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []
        self.tile_info = {}
        with open(TILES_PATH, 'r') as file:
            self.tile_info = json.loads(file.read())
        self.fill_sky()
        self.tile_size = TILE_SIZE
        self.surface = None

    def set_zoom(self, is_more: bool):
        if is_more:
            self.tile_size += 8
        else:
            self.tile_size -= 8

        if self.tile_size < 16:
            self.tile_size = 16

    def get_tile_info(self, name: str) -> Tile:
        for x in self.tile_info:
            if x["name"] == name:
                tile = Tile(x["name"], x["color"], x.get("file_name", ""), x.get("coords", []), visible=x.get("visible", True))
                return tile

    def set_tile(self, x, y, tile_name):
        info: Tile = self.get_tile_info(tile_name)
        if self.tiles and self.tiles[x][y]:
            self.tiles[x][y] = info

    def fill_sky(self):
        sky_info = self.get_tile_info("sky")
        self.tiles = []
        for x in range(self.width):
            self.tiles.append([])
            for y in range(self.height):
                self.tiles[x].append(sky_info)

    def get_map_coords_from_mouse(self, mouse_pos, offset=(0, 0)):
        offset_x, offset_y = offset
        tile_x = (mouse_pos[0] + -offset_x) // self.tile_size
        tile_y = (mouse_pos[1] + -offset_y) // self.tile_size
        return tile_x, tile_y

    def draw(self, display, sprites, offset=(0, 0)):
        for x in range(self.width):
            for y in range(self.height):
                tile: Tile = self.tiles[x][y]
                if tile.name not in ["sky"]:
                    if list(map(lambda x: x*4, sprites[tile.file_name].get_scale_factor()))[0] * 2 != self.tile_size:
                        sprites[tile.file_name].scale_by(self.tile_size // 8, self.tile_size // 8)
                    sprite: KagImage = sprites[tile.file_name]
                    scale = sprite.get_scale_factor()
                    rect = tile.get_rect()
                    sprite.draw(display, (scale[0] * rect.w  * x + offset[0], scale[1] * rect.h * y + offset[1]), tile)

    def save_map(self):
        arr = pygame.PixelArray(pygame.Surface((self.width, self.height)))
        for x in range(self.width):
            for y in range(self.height):
                tile: Tile = self.tiles[x][y]
                arr[x, y] = pygame.Color(tile.color[0], tile.color[1], tile.color[2])
        surface = arr.make_surface()
        if not os.path.exists(MAPS_PATH):
            os.makedirs(MAPS_PATH)
        pygame.image.save(surface, os.path.join(MAPS_PATH, "map.png"))
        print("Map saved")

class KagImage:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.size = self.image.get_size()

        # Make the tile 8x8 be 32x32
        self.scaled_image = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))
        self.scaled_size = self.scaled_image.get_size()

    def scale_by(self, x, y):
        self.scaled_image = pygame.transform.scale(self.image, (int(self.size[0]*x), int(self.size[1]*y)))
        self.scaled_size = self.scaled_image.get_size()

    def get_scale_factor(self):
        return [self.scaled_size[0] // self.size[0], self.scaled_size[1] // self.size[1]]

    def draw_bg(self, display, position=(0, 0)):
        display.blit(self.image, position)

    def draw_scaled_bg(self, display, position=(0, 0)):
        display.blit(self.scaled_image, position)

    def draw(self, surface, position, tile: Tile):
        x, y = position
        scale = self.get_scale_factor()
        rect = tile.get_rect()
        surface.blit(self.scaled_image, (x, y), area=(rect.x, rect.y, rect.w * scale[0], rect.h * scale[1]))
