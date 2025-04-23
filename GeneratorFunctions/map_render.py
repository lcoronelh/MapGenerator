import pygame
import numpy as np

def render_map_surface(data_array, mode="grayscale", river_map=None):
    if mode == "grayscale":
        rgb_array = np.stack([data_array]*3, axis=-1)
    elif mode == "biomes":
        rgb_array = biomes_to_rgb(data_array)
    else:
        raise ValueError(f"Modo de renderizado no soportado: {mode}")
    if river_map is not None:
        river_color = np.array([0, 0, 255], dtype=np.uint8)
        rgb_array[river_map == 1] = river_color

    return pygame.surfarray.make_surface(rgb_array)
    

def biomes_to_rgb(terrain_map):
    """
    Convierte el mapa de biomas a colores:
    0 = azul (agua), 1 = verde (llanura), 2 = marrón (montaña)
    """
    color_map = {
        0: (50, 100, 200),   # Agua
        1: (34, 139, 34),    # Llanura
        2: (139, 69, 19),    # Montaña
    }
    h, w = terrain_map.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    for val, color in color_map.items():
        rgb[terrain_map == val] = color
    return rgb