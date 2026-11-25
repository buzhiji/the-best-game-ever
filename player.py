
from pathlib import Path
import pygame


class Player:
    def __init__(self, x, y, maze):
        self.x, self.y, self.maze = x, y, maze
        image_path = Path(__file__).resolve().with_name("player.png")
        self.image = pygame.image.load(str(image_path)).convert_alpha() if image_path.exists() else None
        if not self._walkable(x, y):
            raise ValueError("Player must start on a walkable cell")

    def _walkable(self, x, y):
        return (0 <= y < len(self.maze) and 0 <= x < len(self.maze[y])
                and self.maze[y][x] != 1)

    def move(self, dx, dy):
        if (dx, dy) not in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            return False
        if not self._walkable(self.x + dx, self.y + dy):
            return False
        self.x += dx
        self.y += dy
        return True

    def draw(self, surface, cell_size, camera_offset=(0, 0)):
        center = (int((self.x + 0.5)*cell_size - camera_offset[0]),
                  int((self.y + 0.5)*cell_size - camera_offset[1]))
        if self.image:
            w, h = self.image.get_size()
            scale = min(cell_size * 0.9 / w, cell_size * 0.9 / h)
            sprite = pygame.transform.smoothscale(self.image, (max(1, int(w*scale)), max(1, int(h*scale))))
            surface.blit(sprite, sprite.get_rect(center=center))

