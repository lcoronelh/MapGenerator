import numpy as np
import random
import math
import pygame
from noise import pnoise3


def generate_cyclic_perlin_noise(width, height, scale=1.0, octaves=4, persistence=0.5, lacunarity=2.0): # Generación de ruido Perlin cicliclo para el mapa envolvente

    result = np.zeros((height, width), dtype=np.float32)
    for y in range(height):
        for x in range(width):
            # Coordenadas cíclicas
            nx = scale * np.cos(2 * np.pi * x / width)
            ny = scale * np.sin(2 * np.pi * x / width)
            nz = scale * y / height

            result[y, x] = pnoise3(nx, ny, nz, octaves=octaves, persistence=persistence, lacunarity=lacunarity)

    return result

def generate_base_heightmap(config): # Generación de mapa de alturas por sistema de fallas

    width = config["Ancho del mapa"]
    height = config["Alto del mapa"]
    num_faults = config["Iteraciones de fallas"]

    # Altura inicial: array de ceros
    heightmap = np.zeros((height, width), dtype=np.float32)
    # Crear la malla de coordenadas
    xs, ys = np.meshgrid(np.arange(width), np.arange(height))

    # Generar fallas
    for _ in range(num_faults):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Evaluamos qué puntos están de qué lado de la falla
        side = (xs - x1) * dy - (ys - y1) * dx

        # Modificamos toda la matriz de una vez
        heightmap += (side > 0) * 1
        heightmap -= (side <= 0) * 1
    
    perlin = generate_cyclic_perlin_noise(width, height, scale=2.5)
    heightmap += perlin * 10

    return heightmap

def apply_radial_fade(heightmap, base_strength=1.8, random_offset=True):
    h, w = heightmap.shape

    if random_offset:
        offset_x = int(w * random.uniform(-0.15, 0.15))
        offset_y = int(h * random.uniform(-0.15, 0.15))
    else:
        offset_x = 0
        offset_y = 0

    cx, cy = w // 2 + offset_x, h // 2 + offset_y

    ys, xs = np.ogrid[:h, :w]
    dx = (xs - cx) / (w // 2)
    dy = (ys - cy) / (h // 2)
    distance = np.sqrt(dx**2 + dy**2)

    strength = base_strength * random.uniform(0.85, 1.15)

    fade = np.clip(distance, 0, 1) ** strength

    # Reducción proporcional al máximo del mapa (esto es clave)
    return heightmap - fade * np.max(heightmap) * 0.9

def normalize_heightmap(heightmap, out_min=0, out_max=255): # Normalización del mapa de alturas
    h_min = np.min(heightmap)
    h_max = np.max(heightmap)

    if h_max - h_min == 0:
        return np.full_like(heightmap, out_min)

    norm = (heightmap - h_min) / (h_max - h_min)
    return (norm * (out_max - out_min) + out_min).astype(np.uint8)

def classify_terrain(heightmap, water_percent, mountain_percent):
    """
    Clasifica el terreno en 3 tipos:
    0 = Agua, 1 = Llanura, 2 = Montaña
    """

    flat = heightmap.flatten()
    water_thresh = np.percentile(flat, water_percent)
    mountain_thresh = np.percentile(flat, 100 - mountain_percent)

    terrain_map = np.zeros_like(heightmap, dtype=np.uint8)
    terrain_map[heightmap > water_thresh] = 1        # Llanura por defecto
    terrain_map[heightmap > mountain_thresh] = 2      # Montaña sobrescribe llanura

    return terrain_map

def thermal_erosion(heightmap, threshold=0.5, erosion_factor=0.05, iterations=10):
    h, w = heightmap.shape
    for _ in range(iterations):
        new_map = heightmap.copy()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            shifted = np.roll(heightmap, shift=dy, axis=0)
            shifted = np.roll(shifted, shift=dx, axis=1)
            delta = heightmap - shifted

            mask = delta > threshold
            amount = delta * erosion_factor * mask

            new_map -= amount
            new_map += np.roll(np.roll(amount, -dy, axis=0), -dx, axis=1)
        heightmap = new_map
    return heightmap