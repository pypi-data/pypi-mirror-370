from typing import List, Tuple, Dict, Final
import numpy as np

from ..sculptor.metrics import get_height_profile, calculate_holes

# Определяем формы фигур и их повороты. Координаты заданы относительно точки вращения (0,0).
# Структура: { 'ИмяФигуры': [ (форма_0), (форма_1), ... ], ... }
# форма_N = ( (x1,y1), (x2,y2), ... )
PIECE_SHAPES: Final[Dict[str, Tuple[Tuple[Tuple[int, int], ...], ...]]] = {
    "I": (((0, 0), (-1, 0), (1, 0), (2, 0)), ((0, 0), (0, -1), (0, 1), (0, 2))),
    "O": (((0, 0), (1, 0), (0, 1), (1, 1)),),
    "T": (
        ((0, 0), (-1, 0), (1, 0), (0, -1)),
        ((0, 0), (0, -1), (0, 1), (1, 0)),
        ((0, 0), (-1, 0), (1, 0), (0, 1)),
        ((0, 0), (0, -1), (0, 1), (-1, 0)),
    ),
    "S": (((0, 0), (-1, 0), (0, -1), (1, -1)), ((0, 0), (0, 1), (1, 0), (1, -1))),
    "Z": (((0, 0), (1, 0), (0, -1), (-1, -1)), ((0, 0), (0, -1), (1, 0), (1, 1))),
    "J": (
        ((0, 0), (-1, 0), (1, 0), (-1, -1)),
        ((0, 0), (0, -1), (0, 1), (1, -1)),
        ((0, 0), (-1, 0), (1, 0), (1, 1)),
        ((0, 0), (0, -1), (0, 1), (-1, 1)),
    ),
    "L": (
        ((0, 0), (-1, 0), (1, 0), (1, -1)),
        ((0, 0), (0, -1), (0, 1), (1, 1)),
        ((0, 0), (-1, 0), (1, 0), (-1, 1)),
        ((0, 0), (0, -1), (0, 1), (-1, -1)),
    ),
}

PIECE_IDS: Final[Dict[str, int]] = {
    name: i + 1 for i, name in enumerate(PIECE_SHAPES.keys())
}


class Board:
    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("Ширина и высота поля должны быть положительными.")
        self.width = width
        self.height = height
        # 0 - пустое место, >0 - занято блоком
        self.grid: np.ndarray = np.zeros((height, width), dtype=np.int32)
        self._height_profile: List[int] = [] # Cached height profile
        self._hole_count: int = 0 # Cached hole count
        self._update_metrics() # Initialize metrics

    def _update_metrics(self):
        self._height_profile = get_height_profile(self.grid, self.width, self.height)
        self._hole_count = calculate_holes(self.grid, self.width, self.height, self._height_profile)

    def get_height_profile_cached(self) -> List[int]:
        return self._height_profile

    def get_hole_count_cached(self) -> int:
        return self._hole_count

    def is_valid_position(self, piece_shape: Tuple[Tuple[int, int], ...], x: int, y: int) -> bool:
        """Проверяет, является ли позиция (x, y) для данной формы фигуры корректной."""
        for px, py in piece_shape:
            abs_x, abs_y = x + px, y + py

            if not (0 <= abs_x < self.width and 0 <= abs_y < self.height):
                return False

            if self.grid[abs_y, abs_x] != 0:
                return False
        return True

    def place_piece(self, piece_shape: Tuple[Tuple[int, int], ...], x: int, y: int, piece_id: int) -> int:
        for px, py in piece_shape:
            abs_x, abs_y = x + px, y + py

            if 0 <= abs_x < self.width and 0 <= abs_y < self.height:
                self.grid[abs_y, abs_x] = piece_id

        lines_cleared = self.clear_lines()
        self._update_metrics() 
        return lines_cleared

    def clear_lines(self) -> int:
        """
        Проверяет и удаляет заполненные линии, сдвигая верхние ряды вниз.
        Возвращает количество удаленных линий.
        """
        # Создаем маску для строк, которые НЕ являются полными
        # np.all(row != 0, axis=1) -> True для полных строк
        # ~ (тильда) инвертирует, чтобы получить НЕполные строки
        non_full_rows_mask = ~np.all(self.grid != 0, axis=1)
        non_full_rows = self.grid[non_full_rows_mask]
        lines_cleared = self.height - non_full_rows.shape[0]

        if lines_cleared > 0:
            new_grid = np.zeros_like(self.grid)
            new_grid[lines_cleared:, :] = non_full_rows
            self.grid = new_grid 
        
        return lines_cleared

    def get_state(self) -> np.ndarray:
        return self.grid.copy()
