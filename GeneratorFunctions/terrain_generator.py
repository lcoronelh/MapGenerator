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

    # Generar fallas
    for _ in range(num_faults):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Creamos una malla de coordenadas
        xs, ys = np.meshgrid(np.arange(width), np.arange(height))

        # Evaluamos qué puntos están de qué lado de la falla
        side = (xs - x1) * dy - (ys - y1) * dx

        # Modificamos toda la matriz de una vez
        heightmap += (side > 0) * 1
        heightmap -= (side <= 0) * 1
    
    perlin = generate_cyclic_perlin_noise(width, height, scale=2.5)
    heightmap += perlin * 10

    return heightmap

def normalize_heightmap(heightmap, out_min=0, out_max=255): # Normalización del mapa de alturas
    h_min = np.min(heightmap)
    h_max = np.max(heightmap)

    if h_max - h_min == 0:
        return np.full_like(heightmap, out_min)

    norm = (heightmap - h_min) / (h_max - h_min)
    return (norm * (out_max - out_min) + out_min).astype(np.uint8)