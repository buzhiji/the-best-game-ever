import pygame
import math
from pathlib import Path
from markov_predictor import DIRECTIONS

class Boss:
    def __init__(self, x, y, grid_size):
        self.x, self.y = x + 0.5, y + 0.5
        self.grid_size = grid_size
        self.state = "ready"
        self.timer = 0
        self.target = (x, y)
        self.predicted_cell = (x, y)
        self.attack_count = 0

        path = Path(__file__).with_name("boss.png")
        self.image = pygame.image.load(str(path)).convert_alpha() if path.exists() else None

    def choose_target(self, player, predictor):
        # Not enough movement data yet
        if predictor.transitions_seen < 8:
            return player

        chances = predictor.probabilities(predictor.last_direction)
        best_score = -float("inf")
        best_cell = player

        for direction, (dx, dy) in DIRECTIONS.items():
            # Predict 2 cells ahead
            x = max(0, min(self.grid_size - 1, player[0] + 2 * dx))
            y = max(0, min(self.grid_size - 1, player[1] + 2 * dy))

            distance = math.hypot(x + 0.5 - self.x, y + 0.5 - self.y)
            score = 10 * chances[direction] - 0.1 * distance

            if score > best_score:
                best_score = score
                best_cell = (x, y)

        return best_cell

    def update(self, dt, player_cell, predictor):
        if self.state == "ready":
            self.target = self.choose_target(player_cell, predictor)
            self.predicted_cell = self.target
            self.state = "warning"
            self.timer = 0.4

        elif self.state == "warning":
            self.timer -= dt
            if self.timer <= 0:
                # Instantly dash to the circle
                self.x = self.target[0] + 0.5
                self.y = self.target[1] + 0.5
                self.attack_count += 1
                self.state = "cooldown"
                self.timer = 0.8

        elif self.state == "cooldown":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "ready"

    def collides_with(self, player_cell):
        px = player_cell[0] + 0.5
        py = player_cell[1] + 0.5
        return math.hypot(self.x - px, self.y - py) < 0.7

    def draw(self, surface, cell_size):
        # Show predicted location
        if self.state == "warning":
            center = (
                self.target[0] * cell_size + cell_size // 2,
                self.target[1] * cell_size + cell_size // 2
            )
            pygame.draw.circle(surface, (255, 70, 90),
                               center, cell_size // 2, 3)

        # Draw the boss
        center = (round(self.x * cell_size), round(self.y * cell_size))
        if self.image:
            w, h = self.image.get_size()
            scale = cell_size / max(w, h)
            sprite = pygame.transform.smoothscale(
                self.image,
                (max(1, round(w * scale)), max(1, round(h * scale)))
            )
            surface.blit(sprite, sprite.get_rect(center=center))
