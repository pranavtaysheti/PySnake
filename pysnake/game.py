from __future__ import annotations
import os
from typing import Callable

import pygame as pg

from snake import SnakeGrid, Direction, SnakeEntityType, SnakeBlock

CAPTION = "Snake Game"
BLOCKS_X = 32
BLOCKS_Y = 18
BLOCK_DIM = 40
asset: pg.Surface
screen: pg.Surface
background: pg.Surface


direction_image_map: dict[Direction, str] = {
    Direction.UP: "snake_head_up",
    Direction.DOWN: "snake_head_down",
    Direction.LEFT: "snake_head_left",
    Direction.RIGHT: "snake_head_right",
}

key_direction_map: dict[int, Direction] = {
    pg.K_w: Direction.UP,
    pg.K_d: Direction.RIGHT,
    pg.K_s: Direction.DOWN,
    pg.K_a: Direction.LEFT,
}

def to_display(num: int):
    return num * BLOCK_DIM


def load_asset(x: int, y: int) -> pg.Surface:
    unscaled_surface = asset.subsurface(pg.Rect(x, y, 8, 8)).convert()
    return pg.transform.scale(unscaled_surface, (BLOCK_DIM, BLOCK_DIM)).convert()


def set_asset(name: str, x: int, y: int):
    background.blit(image_map[name], (x, y))


def set_direction(grid: SnakeGrid, event: pg.event.Event):
    try:
        direction = key_direction_map[event.type]
        grid.snake_direction = direction

        print("set direction to", direction)
    
    except KeyError: ...

def process_updates(grid: SnakeGrid):
    updates = grid.get_updates()
    for update in updates:
        block, (x, y) = update
        set_update: Callable[[str], None] = lambda name: set_asset(
            name, to_display(x), to_display(y)
        )

        if not block:
            set_update("background")

        elif block.entity_type == SnakeEntityType.APPLE:
            set_update("cherry")

        elif type(block) == SnakeBlock and block.entity_type == SnakeEntityType.SNAKE:
            if block.position != 0:
                set_update("snake_body")
            else:
                set_update(direction_image_map[grid.snake_direction])

""" Main program """
if not pg.get_init():
    pg.init()
    screen = pg.display.set_mode((to_display(BLOCKS_X), to_display(BLOCKS_Y)))
    pg.display.set_caption(CAPTION)

asset = pg.image.load(os.path.relpath("images/snake.png")).convert()

image_map: dict[str, pg.Surface] = {
    "background": load_asset(0, 8),
    "snake_head_up": load_asset(8, 24),
    "snake_head_left": load_asset(16, 24),
    "snake_head_down": load_asset(24, 24),
    "snake_head_right": load_asset(32, 24),
    "snake_body": load_asset(40, 24),
    "cherry": load_asset(48, 24),
}


grid = SnakeGrid(BLOCKS_X, BLOCKS_Y)
grid.add_snake((BLOCKS_X // 2, BLOCKS_Y // 2))
for _ in range(3):
    grid.extend_snake()
for _ in range(6):
    grid.add_apple()
clock = pg.time.Clock()
background = pg.Surface(screen.get_size()).convert()
background.fill((0, 0, 0))
screen.blit(background, (0,0))

running = True

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            continue

        set_direction(grid, event)

    grid.move_snake()
    screen.blit(background, (0,0))
    process_updates(grid)
    pg.display.flip()
    clock.tick(10)
