def render_map_surface(data_array, mode="grayscale"):
    
    import pygame
    import numpy as np

    if mode == "grayscale":
        rgb_array = np.stack([data_array]*3, axis=-1)
    else:
        raise ValueError(f"Modo de renderizado no soportado: {mode}")

    return pygame.surfarray.make_surface(rgb_array)