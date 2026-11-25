import pygame
import random
import heapq
import sys
from pathlib import Path

def load_maze_assets(cell_size, asset_dir=None):
    if asset_dir is None:
        asset_dir = Path(__file__).resolve().parent / "assets"
    else:
        asset_dir = Path(asset_dir)
        if not asset_dir.is_absolute():
            asset_dir = Path(__file__).resolve().parent / asset_dir


    background_path = Path(__file__).resolve().parent / "maze_background.png"
    if not background_path.is_file():
        raise FileNotFoundError(f"Maze background image not found: {background_path}")


    assets = {
        "wall": [],
        "floor": [],
        "background": pygame.image.load(str(background_path)).convert(),
    }


    for category in ("wall", "floor"):
        for image_path in sorted(asset_dir.glob(f"{category}*.png")):
            image = pygame.image.load(str(image_path)).convert_alpha()
            scaled = pygame.transform.scale(image, (cell_size, cell_size))
            assets[category].append(scaled)


        if not assets[category]:
            raise FileNotFoundError(f"No {category}*.png sprites found in: {asset_dir}")


    return assets

class maze2:
    def __init__(self, size, open_prob):
        self.size = size

        self.open_prob = open_prob


    def generate_maze(self, size=None):
        if size is None:
            size = self.size


        maze = [[1] * size for _ in range(size)]
        stack = [(1, 1)]
        maze[1][1] = 0


        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < size - 1 and 0 < ny < size - 1 and maze[ny][nx] == 1:
                    neighbors.append((nx, ny))


            if neighbors:
                nx, ny = random.choice(neighbors)
                maze[cy + (ny - cy) // 2][cx + (nx - cx) // 2] = 0
                maze[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        return maze


    def generate_open_maze(self, prob=None, size=None):
        maze = self.generate_maze(size)
        return self.remove_walls(maze, prob)


    def remove_walls(self, maze, prob=None):
        if prob is None:
            prob = self.open_prob


        height = len(maze)
        width = len(maze[0])


        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if random.random() < prob:
                    maze[y][x] = 0
        return maze


    def draw(self, surface, maze, assets, cell_size):
        background = pygame.transform.scale(assets["background"], surface.get_size())
        surface.blit(background, (0, 0))


        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 1:
                    sprite = random.choice(assets["wall"])
                    surface.blit(sprite, (x * cell_size, y * cell_size))
