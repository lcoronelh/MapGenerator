import pygame
import sys
import random
from terrain_config import default_config
from terrain_utils import seed_from_string
from terrain_generator import (
    generate_base_heightmap,
    normalize_heightmap,
    apply_radial_fade,
    classify_terrain
)
import time
from map_render import render_map_surface

# ---------- Clase Slider ----------
class Slider:
    def __init__(self, x, y, width, min_val, max_val, default, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = default
        self.label = label
        self.handle_radius = 10
        self.active = False
        self.handle_x = self._value_to_pos(self.value)

    def _value_to_pos(self, value):
        return self.rect.x + int((value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)

    def _pos_to_value(self, pos):
        ratio = (pos - self.rect.x) / self.rect.width
        return round(self.min_val + ratio * (self.max_val - self.min_val))

    def draw(self, screen, font):
        pygame.draw.line(screen, (180, 180, 180), (self.rect.x, self.rect.centery),
                         (self.rect.right, self.rect.centery), 4)
        pygame.draw.circle(screen, (255, 100, 100), (self.handle_x, self.rect.centery), self.handle_radius)
        label_surf = font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False
        elif event.type == pygame.MOUSEMOTION and self.active:
            self.handle_x = max(self.rect.x, min(event.pos[0], self.rect.right))
            self.value = self._pos_to_value(self.handle_x)


# ---------- Interfaz principal ----------
def run_ui_config():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
    pygame.display.set_caption("Configuración del Mapa")
    font = pygame.font.SysFont("Arial", 20)

    slider_defs = [
        ("Ancho del mapa", 100, 1000, default_config["Ancho del mapa"]),
        ("Alto del mapa", 100, 1000, default_config["Alto del mapa"]),
        ("Porcentaje de agua", 0, 100, default_config["Porcentaje de agua"]),
        ("Porcentaje de hielo", 0, 100, default_config["Porcentaje de hielo"])
    ]

    sliders = []

    seed_text = default_config["Semilla"]
    seed_active = False
    seed_rect = pygame.Rect(0, 0, 300, 32)

    button_rect = pygame.Rect(0, 0, 200, 50)
    button_color = (100, 200, 100)

    clock = pygame.time.Clock()
    state = "menu"
    generated_surface = None

    while True:
        screen.fill((30, 30, 30))
        center_x = screen.get_width() // 2
        slider_width = 400
        spacing_y = 60
        total_height = len(slider_defs) * spacing_y + 32 + 50 + 60
        start_y = (screen.get_height() - total_height) // 2

        # Crear sliders una sola vez
        if state == "menu" and not sliders:
            for i, (label, min_val, max_val, default) in enumerate(slider_defs):
                x = center_x - slider_width // 2
                y = start_y + i * spacing_y
                slider = Slider(x, y, slider_width, min_val, max_val, default, label)
                sliders.append(slider)

        # Actualizar posición de elementos
        seed_rect.width = 300
        seed_rect.height = 32
        seed_rect.x = center_x - seed_rect.width // 2
        seed_rect.y = start_y + len(slider_defs) * spacing_y + 10

        button_rect.width = 200
        button_rect.height = 50
        button_rect.x = center_x - button_rect.width // 2
        button_rect.y = seed_rect.y + seed_rect.height + 40

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == "menu":
                for slider in sliders:
                    slider.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    seed_active = seed_rect.collidepoint(event.pos)
                    if button_rect.collidepoint(event.pos):
                        config = {slider.label: slider.value for slider in sliders}
                        config["Semilla"] = seed_text
                        config["Iteraciones de fallas"] = 15000

                        numeric_seed = seed_from_string(seed_text)
                        random.seed(numeric_seed)

                        start_t = time.time()
                        print("Generando el mapa")

                        heightmap = generate_base_heightmap(config)
                        heightmap = apply_radial_fade(heightmap, base_strength=1)
                        norm_map = normalize_heightmap(heightmap)

                        terrain_map = classify_terrain(norm_map,
                                config["Porcentaje de agua"],
                                mountain_percent=15)

                        generated_surface = render_map_surface(terrain_map, mode="biomes")
                        state = "map"

                        end_t = time.time()
                        print(f"Mapa generado en {end_t - start_t:.2f} segundos")

                if event.type == pygame.KEYDOWN and seed_active:
                    if event.key == pygame.K_BACKSPACE:
                        seed_text = seed_text[:-1]
                    elif len(seed_text) < 30:
                        seed_text += event.unicode

        if state == "menu":
            for slider in sliders:
                slider.draw(screen, font)

            pygame.draw.rect(screen, (255, 255, 255), seed_rect, 2)
            label_seed = font.render("Semilla:", True, (255, 255, 255))
            text_surface = font.render(seed_text, True, (255, 255, 255))
            screen.blit(label_seed, (seed_rect.x, seed_rect.y - 25))
            screen.blit(text_surface, (seed_rect.x + 5, seed_rect.y + 5))

            pygame.draw.rect(screen, button_color, button_rect)
            button_text = font.render("Generar mapa", True, (0, 0, 0))
            screen.blit(button_text, (button_rect.x + 30, button_rect.y + 15))

        elif state == "map" and generated_surface is not None:
            screen.blit(pygame.transform.scale(generated_surface, screen.get_size()), (0, 0))

        pygame.display.flip()
        clock.tick(60)

# ---------- Ejecutable ----------
if __name__ == "__main__":
    run_ui_config()