import numpy as np

def generate_rivers(heightmap, terrain_map, num_rivers=50, max_steps=500):
    
    h, w = heightmap.shape
    river_map = np.zeros((h, w), dtype=np.uint8)

    # Buscar posibles puntos altos
    flat_indices = np.dstack(np.unravel_index(np.argsort(heightmap.ravel())[::-1], heightmap.shape))[0]

    rivers_placed = 0
    attempts = 0
    i = 0

    while rivers_placed < num_rivers and i < len(flat_indices):
        y, x = flat_indices[i]
        i += 1

        if terrain_map[y, x] == 0 or river_map[y, x] == 1:
            continue  # ya es agua o ya hay río

        path = []
        cy, cx = y, x
        steps = 0

        while steps < max_steps:
            path.append((cy, cx))

            neighbors = [
                (cy - 1, cx), (cy + 1, cx),
                (cy, cx - 1), (cy, cx + 1),
                (cy - 1, cx - 1), (cy - 1, cx + 1),
                (cy + 1, cx - 1), (cy + 1, cx + 1)
            ]
            neighbors = [(ny, nx) for ny, nx in neighbors if 0 <= ny < h and 0 <= nx < w]

            min_h = heightmap[cy, cx]
            next_pos = None

            for ny, nx in neighbors:
                if heightmap[ny, nx] < min_h:
                    min_h = heightmap[ny, nx]
                    next_pos = (ny, nx)

            if next_pos is None:
                break  # no hay descenso
            if terrain_map[next_pos] == 0:
                for py, px in path:
                    river_map[py, px] = 1
                rivers_placed += 1
                break

            cy, cx = next_pos
            steps += 1

    return river_map
