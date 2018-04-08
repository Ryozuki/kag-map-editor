import json
import pygame
import os
from random import randint
import logic
from logic import Tile, Rect

TILES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiles.json")
MAPS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps/")
TILE_SIZE = 32


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

    def set_tile(self, x, y, tile_name):
        info: Tile = logic.get_tile_by_name(tile_name)
        if self.tiles and self.tiles[x][y]:
            self.tiles[x][y] = info

    def fill_sky(self):
        sky_tile: Tile = logic.get_tile_by_name("Sky")
        self.tiles = []
        for x in range(self.width):
            self.tiles.append([])
            for y in range(self.height):
                self.tiles[x].append(sky_tile)

    def get_map_coords_from_mouse(self, mouse_pos, offset=(0, 0)):
        offset_x, offset_y = offset
        tile_x = (mouse_pos[0] + -offset_x) // self.tile_size
        tile_y = (mouse_pos[1] + -offset_y) // self.tile_size
        return tile_x, tile_y

    def draw(self, display, sprites, offset=(0, 0)):
        for x in range(self.width):
            for y in range(self.height):
                tile: Tile = self.tiles[x][y]
                if tile.visible:
                    if list(map(lambda x: x*4, sprites[tile.file_name].get_scale_factor()))[0] * 2 != self.tile_size:
                        sprites[tile.file_name].scale_by(self.tile_size // 8, self.tile_size // 8)
                    sprite: KagImage = sprites[tile.file_name]
                    rect = tile.get_rect((x, y), self.tiles)
                    sprite.draw(display, (x, y), rect, offset)

    def save_map(self):
        arr = pygame.PixelArray(pygame.Surface((self.width, self.height)))
        for x in range(self.width):
            for y in range(self.height):
                tile: Tile = self.tiles[x][y]
                arr[x, y] = pygame.Color(tile.color[0], tile.color[1],
                                         tile.color[2])
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

    def draw(self, surface: pygame.Surface, position, rect: Rect, offset=(0, 0)):
        scale = self.get_scale_factor()
        x = scale[0] * rect.w * position[0] + offset[0]
        y = scale[1] * rect.h * position[1] + offset[1]
        surface.blit(self.scaled_image, (x, y), area=rect.scale(scale).to_tuple())
