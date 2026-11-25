
import pygame
import random


class Cupcake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load("cupcake.png").convert_alpha()

    def draw(self, screen, cell_size, camera_offset=(0, 0)):
        # Make the cupcake smaller than one maze cell
        image = pygame.transform.scale(
            self.image, (cell_size * 3 // 4, cell_size * 3 // 4)
        )

        # Calculate the position on the screen
        x = self.x * cell_size - camera_offset[0] + cell_size // 8
        y = self.y * cell_size - camera_offset[1] + cell_size // 8

        screen.blit(image, (x, y))


def spawn_cupcakes(maze, count, occupied=()):
    empty_cells = []

    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 0 and (x, y) not in occupied:
                empty_cells.append((x, y))

    positions = random.sample(empty_cells, count)

    return [Cupcake(x, y) for x, y in positions]
