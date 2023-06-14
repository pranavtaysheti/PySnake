from __future__ import annotations
import os
from typing import Callable
from enum import Enum, auto
from math import floor

import pygame as pg

from pysnake.snake import SnakeGrid, Direction, SnakeEntityType, SnakeBlock


class AssetType(Enum):
    BACKGROUND = auto()
    SNAKE_HEAD_UP = auto()
    SNAKE_HEAD_DOWN = auto()
    SNAKE_HEAD_RIGHT = auto()
    SNAKE_HEAD_LEFT = auto()
    SNAKE_BODY = auto()
    CHERRY = auto()


direction_image_map: dict[Direction, AssetType] = {
    Direction.UP: AssetType.SNAKE_HEAD_UP,
    Direction.DOWN: AssetType.SNAKE_HEAD_DOWN,
    Direction.LEFT: AssetType.SNAKE_HEAD_LEFT,
    Direction.RIGHT: AssetType.SNAKE_HEAD_RIGHT,
}

key_direction_map: dict[int, Direction] = {
    pg.K_UP: Direction.UP,
    pg.K_RIGHT: Direction.RIGHT,
    pg.K_DOWN: Direction.DOWN,
    pg.K_LEFT: Direction.LEFT,
}


def main():
    """Main function"""

    CAPTION = "Snake Game"
    BLOCKS_X = 32
    BLOCKS_Y = 18
    BLOCK_DIM = 40
    FPS = 30

    def process_updates():
        updates = grid.get_updates()
        for update in updates:
            block, (x, y) = update
            set_update: Callable[[AssetType], None] = lambda name: set_asset(
                name, x * BLOCK_DIM, y * BLOCK_DIM
            )

            if not block:
                set_update(AssetType.BACKGROUND)

            elif block.entity_type == SnakeEntityType.APPLE:
                set_update(AssetType.CHERRY)

            elif (
                type(block) == SnakeBlock and block.entity_type == SnakeEntityType.SNAKE
            ):
                if block.position != 0:
                    set_update(AssetType.SNAKE_BODY)
                else:
                    set_update(direction_image_map[grid.snake_direction])

    def load_asset(x: int, y: int) -> pg.Surface:
        unscaled_surface = asset.subsurface(pg.Rect(x, y, 8, 8)).convert()
        return pg.transform.scale(unscaled_surface, (BLOCK_DIM, BLOCK_DIM)).convert()

    def set_asset(name: AssetType, x: int, y: int):
        background.blit(image_map[name], (x, y))

    if not pg.get_init():
        pg.init()

    screen = pg.display.set_mode((BLOCKS_X * BLOCK_DIM, BLOCKS_Y * BLOCK_DIM))
    pg.display.set_caption(CAPTION)
    background = pg.Surface(screen.get_size()).convert()
    background.fill((0, 0, 0))

    asset = pg.image.load(os.path.relpath("assets/snake.png")).convert()

    image_map: dict[AssetType, pg.Surface] = {
        AssetType.BACKGROUND: load_asset(0, 8),
        AssetType.SNAKE_HEAD_UP: load_asset(8, 24),
        AssetType.SNAKE_HEAD_LEFT: load_asset(16, 24),
        AssetType.SNAKE_HEAD_DOWN: load_asset(24, 24),
        AssetType.SNAKE_HEAD_RIGHT: load_asset(32, 24),
        AssetType.SNAKE_BODY: load_asset(40, 24),
        AssetType.CHERRY: load_asset(48, 24),
    }

    grid = SnakeGrid(BLOCKS_X, BLOCKS_Y)
    grid.add_snake((BLOCKS_X // 2, BLOCKS_Y // 2))

    snake_speed = 10
    apple_frames = 0
    snake_steps = 0

    def place_apple():
        nonlocal apple_frames
        if apple_frames > FPS*5:
            apple_frames = 0
            grid.add_apple()
    
    def get_snake_steps():
        nonlocal snake_steps
        if snake_steps > FPS:
            snake_steps = 0
            return True


    for _ in range(3):
        grid.extend_snake()
    
    grid.add_apple()

    clock = pg.time.Clock()

    screen.blit(background, (0, 0))
    pg.display.flip()

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                continue

            if event.type == pg.KEYDOWN:
                try:
                    direction = key_direction_map[event.key]
                    grid.snake_direction = direction

                except KeyError:
                    ...
        
        if get_snake_steps():
            grid.move_snake()
        process_updates()
        if grid.get_apple_eaten():
            snake_speed = floor(snake_speed*1.1)
        
        place_apple()

        screen.blit(background, (0, 0))
        pg.display.flip()
        
        apple_frames += 1
        snake_steps += snake_speed
        clock.tick(FPS)
