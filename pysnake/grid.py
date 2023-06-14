from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Optional

Coordinates = tuple[int, int]


class CollisionError(Exception):
    """To be raised when 2 blocks claim same coordinate on grid"""

    def __init__(self, existing: Block, challenger: Block):
        self.existing = existing
        self.challenger = challenger


class EntityType(Enum):
    ...


@dataclass
class Block:
    entity_type: EntityType
    _coordinates: Coordinates
    _grid: Grid = field(init=False, repr=False)

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, grid: Grid):
        self._grid = grid
        self._correct_coordinates()

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates: Coordinates):
        self._coordinates = coordinates

        if self._grid:
            self._correct_coordinates()

    def _correct_coordinates(self) -> None:
        x, y = self.coordinates
        if not self.grid:
            raise Exception("Block not part of any grid")

        self._coordinates = x % self.grid.width, y % self.grid.height


BlockCoordinates = tuple[Block, Coordinates]
Collision = tuple[Block, Block]
Delta = tuple[Optional[Block], Coordinates]

@dataclass
class Grid:
    width: int
    height: int
    _blocks: list[Block] = field(init=False, default_factory=list)
    _build: list[list[Optional[Block]]] = field(init=False, default_factory=list)
    representation_map: ClassVar[dict[Optional[EntityType], str]]
    _deltas: list[Delta] = field(init = False, default_factory=list)

    def __post_init__(self):
        for _ in range(self.width):
            column: list[Optional[Block]] = []
            for _ in range(self.height):
                column.append(None)
            self._build.append(column)
    
    def _set_cell(self, block: Block):
        x, y = block.coordinates
        if existing_block := self._build[x][y]:
            raise CollisionError(existing_block, block)

        self._build[x][y] = block
        self._deltas.append((block, block.coordinates))

    
    def _clear_cell(self, coordinate: Coordinates):
        x, y = coordinate
        self._build[x][y] = None
        self._deltas.append((None, coordinate))
    
    def add_block(self, new_block: Block):
        new_block.grid = self
        self._set_cell(new_block)
        self._blocks.append(new_block)

    def remove_block(self, block: Block):

        if block in self._blocks:
            self._clear_cell(block.coordinates)
            self._blocks.remove(block)

    def move_block(self, block: Block, coordinates: Coordinates):
        if block not in self._blocks:
            raise ValueError("Block not in grid")
        
        self._clear_cell(block.coordinates)
        block.coordinates = coordinates
        self._set_cell(block)
    
    def get_updates(self):
        result = self._deltas
        self._deltas = []
        return result

    @property
    def build(self):
        return self._build


@dataclass
class GridRepresentation:
    grid: Grid
    _representation: list[list[Optional[EntityType]]] = field(
        init=False, default_factory=list
    )

    def _get_entity_type(self, coordinates: Coordinates):
        x, y = coordinates
        if block := self.grid.build[x][y]:
            return block.entity_type

    def __post_init__(self):
        for column_no in range(self.grid.width):
            k: list[Optional[EntityType]] = []
            for row_no in range(self.grid.height):
                k.append(self._get_entity_type((column_no, row_no)))
            self._representation.append(k)

    def __str__(self):
        return "\n".join(
            [
                " ".join(
                    [
                        self.grid.representation_map[
                            self._representation[column_no][row_no]
                        ]
                        for column_no in range(self.grid.width)
                    ]
                )
                for row_no in range(self.grid.height)
            ]
        )
    
    def update(self, delta: Delta):
        block, (x,y) = delta
        self._representation[x][y] = block.entity_type if block else None
