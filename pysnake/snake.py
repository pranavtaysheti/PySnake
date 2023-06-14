from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from random import randint

from grid import (
    Block,
    CollisionError,
    Coordinates,
    EntityType,
    Grid,
    GridRepresentation,
)

Snake = list[Block]


class SnakeEntityType(EntityType):
    APPLE = auto()
    SNAKE = auto()
    OBSTACLE = auto()


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


delta_map: dict[Direction, tuple[int, int]] = {
    Direction.UP: (0, +1),
    Direction.DOWN: (0, -1),
    Direction.LEFT: (+1, 0),
    Direction.RIGHT: (-1, 0),
}

@dataclass
class SnakeBlock(Block):
    position: int

@dataclass
class SnakeGrid(Grid):
    snake_direction: Direction = Direction.RIGHT
    snake: Snake = field(init=False, default_factory=list)

    representation_map = {
        None: "X",
        SnakeEntityType.APPLE: "A",
        SnakeEntityType.SNAKE: "S",
        SnakeEntityType.OBSTACLE: "O",
    }

    def add_apple(self, coordinate: Optional[Coordinates] = None) -> None:
        rand_pos: Callable[[int], int] = lambda high: randint(1, high - 1)

        while True:
            try:
                apple = Block(
                    SnakeEntityType.APPLE, (rand_pos(self.width), rand_pos(self.height))
                )
                self.add_block(apple)
            except CollisionError:
                continue
            else:
                break

    def add_snake(self, coordinates: Coordinates) -> None:
        if self.snake:
            raise Exception("Snake alrealy exists on grid.")
        snake_block = SnakeBlock(SnakeEntityType.SNAKE, coordinates, 0)
        self.snake.append(snake_block)
        self.add_block(snake_block)

    def extend_snake(self):
        snake = self.snake

        last_x, last_y = snake[-1].coordinates
        delta_x, delta_y = delta_map[self.snake_direction]
        new_coord = last_x + delta_x, last_y + delta_y

        new_block = SnakeBlock(SnakeEntityType.SNAKE, new_coord, len(snake))
        self.add_block(new_block)
        snake.append(new_block)

    def move_snake(self):
        snake = self.snake
        prev_coordinates: Coordinates = snake[0].coordinates

        delta_x, delta_y = delta_map[self.snake_direction]
        first_x, first_y = snake[0].coordinates
        new_coordinates = first_x - delta_x, first_y - delta_y

        try:
            self.move_block(snake[0], new_coordinates)

        except CollisionError as e:
            if not e.existing.entity_type == SnakeEntityType.APPLE:
                raise

            self.remove_block(e.existing)
            self.move_block(snake[0], new_coordinates)
            self.extend_snake()

        for i in range(1, len(snake)):
            temp = snake[i].coordinates
            self.move_block(snake[i], prev_coordinates)
            prev_coordinates = temp


if __name__ == "__main__":
    gr = SnakeGrid(10, 12, Direction.DOWN)
    gr.add_snake((5, 5))
    gr.get_updates()
    for _ in range(3):
        gr.extend_snake()
    print(gr.get_updates())
    gr.snake_direction = Direction.RIGHT
    for _ in range(2):
        gr.move_snake()
    # print(gr.get_updates())
    for _ in range(1):
        gr.add_apple()
    # print(gr.get_updates())
    print(str(GridRepresentation(gr)))
