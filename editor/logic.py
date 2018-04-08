from random import randint


def get_tile(x, y, tiles):
    """Gets the tile at the specified coords,
    returns None if it doesn't exist."""
    width = len(tiles)
    height = len(tiles[0])

    if x >= width or y >= height or x < 0 or y < 0:
        return None

    return tiles[x][y]


def get_rand_from_list(list):
    return list[randint(0, len(list) - 1)]


def hex_to_rgb(hex: str):
    hex = hex.lstrip('#')
    return [int(hex[i:i+2], 16) for i in (0, 2, 4)]


class Rect:
    def __init__(self, x, y, w=8, h=8):
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h

    def scale(self, scale=(1, 1)):
        return Rect(self.x, self.y, self.w * scale[0], self.h * scale[1])

    def to_tuple(self):
        return self.x, self.y, self.w, self.h


class Tile:
    def __init__(self, name, color, file_name="", coords=[], visible=True):
        self.visible = visible
        self.name = name
        self.file_name = file_name.rstrip(".png")
        self.color = hex_to_rgb(color)
        self.coords = coords
        self.rect: Rect = None
        self.tile_surface = None

    def get_rect(self, tile_pos, tiles) -> Rect:
        if self.rect is None:
            self.rect = get_rand_from_list(self.coords)
        return self.rect


class Sky(Tile):
    def __init__(self):
        super().__init__("Sky", "#A5BDC8", visible=False)


class Dirt(Tile):
    def __init__(self):
        super().__init__("Dirt", "#844715", "world.png")

        self.grass_dirt = [
            Rect(8 * 8, 8),
            Rect(9 * 8, 8)
        ]

        self.dirt = [
            Rect(14 * 8, 8),
            Rect(15 * 8, 8),
            Rect(16 * 8, 8)
        ]

    def get_rect(self, tile_pos, tiles) -> Rect:
        if self.rect is None:
            x, y = tile_pos
            upper_tile = get_tile(x, y-1, tiles)
            if upper_tile and upper_tile.name == "Grass":
                self.rect = get_rand_from_list(self.grass_dirt)
            else:
                self.rect = get_rand_from_list(self.dirt)
        return self.rect


class DirtBackground(Tile):
    def __init__(self):
        super().__init__("Dirt Background", "#3B1406", "world.png", [
            Rect(0, 0),
            Rect(8, 0),
            Rect(2 * 8, 0),
            Rect(3 * 8, 0)
        ])


def get_tile_by_name(name):
    if name == "Sky":
        return Sky()
    elif name == "Dirt":
        return Dirt()
    elif name == "Dirt Background":
        return DirtBackground()
    else:
        return None
