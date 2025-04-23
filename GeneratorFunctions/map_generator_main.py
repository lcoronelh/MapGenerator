from ui_map import run_ui_config
from terrain_utils import seed_from_string
from terrain_generator import generate_base_heightmap
import random

def main():
    # Paso 1: Obtener configuración desde la interfaz
    config = run_ui_config()

    # Paso 2: Convertir semilla alfanumérica a número reproducible
    numeric_seed = seed_from_string(config["Semilla"])
    random.seed(numeric_seed)

    # Paso 3: Generar el heightmap base
    heightmap = generate_base_heightmap(config)

    # Paso 4: Por ahora solo mostramos tamaño o ejemplo
    print(f"Mapa generado con tamaño: {len(heightmap)}x{len(heightmap[0])} (alto x ancho)")

if __name__ == "__main__":
    main()