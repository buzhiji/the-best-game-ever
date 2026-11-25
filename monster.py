
import random
from pathlib import Path
import heapq
import pygame


class Monster:
    def __init__(self, x, y, grid_size, maze):
        self.x, self.y = x, y
        self.grid_size = grid_size
        self.maze = maze
        self.path, self.target = [], None
        self.detection_range = 5
        image_path = Path(__file__).resolve().with_name("enemy.png")
        self.image = pygame.image.load(str(image_path)).convert_alpha() if image_path.exists() else None

    def heuristic(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def get_astar_path(self, maze, start, goal):
        queue = [(0, start)]
        parent = {start: None}
        costs = {start: 0}
        while queue:
            _, current = heapq.heappop(queue)
            if current == goal:
                break
            for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
                next_cell = (current[0]+dx, current[1]+dy)
                nx, ny = next_cell
                if not (0 <= ny < len(maze) and 0 <= nx < len(maze[ny])):
                    continue
                if maze[ny][nx] == 1:
                    continue
                cost = costs[current] + 1
                if cost < costs.get(next_cell, float('inf')):
                    costs[next_cell] = cost
                    parent[next_cell] = current
                    heapq.heappush(queue, (cost + self.heuristic(next_cell, goal), next_cell))
        if goal not in parent:
            return []
        path, cell = [], goal
        while cell is not None:
            path.append(cell)
            cell = parent[cell]
        return path[::-1]

    def player_in_range(self, x, y):
        return self.heuristic((self.x, self.y), (x, y)) <= self.detection_range

    def set_target(self, goal):
        self.target = goal
        self.path = self.get_astar_path(self.maze, (self.x, self.y), goal)

    def move(self):
        if len(self.path) < 2:
            return False
        self.x, self.y = self.path[1]
        self.path = self.path[1:]
        return True

    def move_randomly(self):
        neighbors = [
            (self.x + dx, self.y + dy)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if (
                0 <= self.y + dy < len(self.maze)
                and 0 <= self.x + dx < len(self.maze[self.y + dy])
                and self.maze[self.y + dy][self.x + dx] != 1
            )
        ]
        if not neighbors:
            return False

        self.x, self.y = random.choice(neighbors)
        self.target = None
        self.path = []
        return True

    def update(self, goal=None):
        if goal is None:
            self.move_randomly()
            return self.x, self.y

        if self.target != goal or not self.path:
            self.set_target(goal)
        self.move()
        return self.x, self.y

    def draw(self, surface, cell_size, camera_offset=(0, 0)):
        center = (int((self.x+0.5)*cell_size-camera_offset[0]),
                  int((self.y+0.5)*cell_size-camera_offset[1]))
        if self.image:
            w, h = self.image.get_size()
            scale = min(cell_size*.9/w, cell_size*.9/h)
            sprite = pygame.transform.smoothscale(self.image,(max(1,int(w*scale)),max(1,int(h*scale))))
            surface.blit(sprite, sprite.get_rect(center=center))
