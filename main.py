import asyncio
import random
from pathlib import Path

import pygame


async def main():
    from boss import Boss
    from cupcake import spawn_cupcakes
    from markov_predictor import MarkovPredictor
    from mazev2 import maze2
    from monster import Monster
    from player import Player

    WIDTH = HEIGHT = 800
    GRID_SIZE = 25
    CELL_SIZE = 40
    CAMERA_ZOOM = 3
    CAMERA_WIDTH = WIDTH // CAMERA_ZOOM
    CAMERA_HEIGHT = HEIGHT // CAMERA_ZOOM
    MONSTER_COUNT = 3
    CUPCAKE_COUNT = 5
    MONSTER_MOVE_INTERVAL = 0.45

    def create_wall_sprite():
        wall = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        wall.fill((24, 14, 24, 235))
        pygame.draw.rect(wall, (83, 43, 58, 255), wall.get_rect(), 2)
        return wall

    def camera_offset_for_player(player, world_width, world_height):
        x = player.x * CELL_SIZE + CELL_SIZE // 2 - CAMERA_WIDTH // 2
        y = player.y * CELL_SIZE + CELL_SIZE // 2 - CAMERA_HEIGHT // 2
        x = max(0, min(x, world_width - CAMERA_WIDTH))
        y = max(0, min(y, world_height - CAMERA_HEIGHT))
        return x, y

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Best Maze Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    end_image_path = Path(__file__).resolve().with_name("end.png")
    end_image = pygame.image.load(str(end_image_path)).convert()
    end_image = pygame.transform.smoothscale(end_image, (WIDTH, HEIGHT))

    maze_generator = maze2(GRID_SIZE, 0.3)
    maze_grid = maze_generator.generate_maze()
    maze_grid = maze_generator.remove_walls(maze_grid)
    boss_exit = (1, 1)
    boss_start = (GRID_SIZE // 2, GRID_SIZE // 2)
    player = Player(*boss_exit, maze_grid)

    open_cells = [
        (x, y)
        for y, row in enumerate(maze_grid)
        for x, cell in enumerate(row)
        if cell != 1 and (x, y) not in (boss_exit, boss_start)
    ]
    monster_starts = random.sample(open_cells, MONSTER_COUNT)
    monsters = [
        Monster(x, y, GRID_SIZE, maze_grid)
        for x, y in monster_starts
    ]
    cupcakes = spawn_cupcakes(
        maze_grid,
        CUPCAKE_COUNT,
        {boss_exit, boss_start, *monster_starts},
    )

    predictor = MarkovPredictor()
    boss = None
    phase = "maze"

    background = pygame.image.load(
        str(Path(__file__).resolve().with_name("maze_background.png"))
    ).convert()
    assets = {"background": background, "wall": [create_wall_sprite()]}
    world_width = len(maze_grid[0]) * CELL_SIZE
    world_height = len(maze_grid) * CELL_SIZE
    maze_surface = pygame.Surface((world_width, world_height))
    boss_surface = pygame.Surface((world_width, world_height), pygame.SRCALPHA)

    def draw_map(exit_cell=None, color=None):
        maze_generator.draw(maze_surface, maze_grid, assets, CELL_SIZE)
        if exit_cell is not None and color is not None:
            exit_box = pygame.Rect(
                exit_cell[0] * CELL_SIZE + CELL_SIZE // 4,
                exit_cell[1] * CELL_SIZE + CELL_SIZE // 4,
                CELL_SIZE // 2,
                CELL_SIZE // 2,
            )
            pygame.draw.rect(maze_surface, color, exit_box, 3)

    draw_map()

    keys = {
        pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
        pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
        pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
        pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    }

    monster_move_elapsed = 0
    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and phase in ("maze", "boss"):
                movement = keys.get(event.key)
                if movement and player.move(*movement):
                    predictor.record(*movement)
                    player_cell = (player.x, player.y)

                    if phase == "maze":
                        if any((monster.x, monster.y) == player_cell for monster in monsters):
                            phase = "caught"
                        else:
                            cupcakes = [
                                cupcake for cupcake in cupcakes
                                if (cupcake.x, cupcake.y) != player_cell
                            ]

                        if phase == "maze" and not cupcakes:
                            for row in maze_grid:
                                for x in range(len(row)):
                                    row[x] = 0
                            draw_map(boss_exit, (80, 255, 120))
                            boss = Boss(*boss_start, GRID_SIZE)
                            phase = "boss"

                    elif boss.collides_with(player_cell):
                        phase = "caught"
                    elif player_cell == boss_exit:
                        phase = "escaped"

        if phase == "maze":
            monster_move_elapsed += dt
            if monster_move_elapsed >= MONSTER_MOVE_INTERVAL:
                monster_move_elapsed = 0
                for monster in monsters:
                    if monster.player_in_range(player.x, player.y):
                        monster.update((player.x, player.y))
                    else:
                        monster.update()
                    if (monster.x, monster.y) == (player.x, player.y):
                        phase = "caught"

        if phase == "boss":
            boss.update(dt, (player.x, player.y), predictor)
            if boss.collides_with((player.x, player.y)):
                phase = "caught"

        camera_x, camera_y = camera_offset_for_player(player, world_width, world_height)
        camera_rect = pygame.Rect(camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT)
        camera_view = maze_surface.subsurface(camera_rect)
        pygame.transform.scale(camera_view, (WIDTH, HEIGHT), screen)
        zoomed_offset = (camera_x * CAMERA_ZOOM, camera_y * CAMERA_ZOOM)

        if phase == "maze":
            for monster in monsters:
                monster.draw(screen, CELL_SIZE * CAMERA_ZOOM, zoomed_offset)
            for cupcake in cupcakes:
                cupcake.draw(screen, CELL_SIZE * CAMERA_ZOOM, zoomed_offset)
        elif boss is not None:
            boss_surface.fill((0, 0, 0, 0))
            boss.draw(boss_surface, CELL_SIZE)
            boss_view = boss_surface.subsurface(camera_rect)
            screen.blit(pygame.transform.scale(boss_view, (WIDTH, HEIGHT)), (0, 0))

        player.draw(screen, CELL_SIZE * CAMERA_ZOOM, zoomed_offset)

        hud = pygame.Surface((WIDTH, 32), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 170))
        screen.blit(hud, (0, 0))
        message = (
            f"Magical Wand: {CUPCAKE_COUNT - len(cupcakes)}/{CUPCAKE_COUNT} "
            "Collect all magical wands to gain your power"
            if phase == "maze" else
            "Reach the exit and dodge red circles"
        )
        screen.blit(font.render(message, True, (255, 255, 255)), (10, 8))

        if phase in ("escaped", "caught"):
            screen.blit(end_image, (0, 0))

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
