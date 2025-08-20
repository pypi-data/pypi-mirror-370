from typing import Tuple, List, Optional
import numpy as np

from .base_bot import BaseBot
from tttarena.engine.core.engine import TetrisEngine
from tttarena.engine.core.geometry import PIECE_SHAPES
from tttarena.engine.core.exceptions import InvalidMove, NoValidMovesError
from tttarena.engine.sculptor.metrics import get_height_profile


class SimpleBot(BaseBot):
    """Простой бот, принимающий решения на основе эвристики с инкрементальной оценкой."""

    def find_best_move(self, engine: TetrisEngine) -> Tuple[int, int]:
        """Ищет лучший ход для текущей фигуры, используя быструю инкрементальную оценку."""

        # target_curve = engine.target_curve
        
        best_move: Optional[Tuple[int, int]] = None
        best_score = float("inf")

        current_piece_type = engine.current_piece_type
        if not current_piece_type:
            raise RuntimeError("Попытка найти ход без текущей фигуры.")

        possible_rotations = PIECE_SHAPES[current_piece_type]
        original_height_profile = get_height_profile(engine.board.grid, engine.board.width, engine.board.height)

        for rot_idx, shape in enumerate(possible_rotations):
            for x in range(engine.board.width):
                try:
                    final_y = engine._find_drop_y(shape, x)

                    score, lines_cleared = self._calculate_incremental_score(
                        engine, original_height_profile, shape, x, final_y
                    )

                    score -= lines_cleared * 1000

                    if score < best_score:
                        best_score = score
                        best_move = (x, rot_idx)

                except InvalidMove:
                    continue

        if best_move is None:
            # Если ни один ход не найден (например, все приводят к немедленному проигрышу),
            # пытаемся найти хоть какой-то валидный ход, даже если он плохой.
            # Это запасной вариант, чтобы избежать NoValidMovesError.
            for rot_idx in range(len(possible_rotations)):
                for x in range(engine.board.width):
                    try:
                        # Просто проверим, можно ли вообще сбросить фигуру
                        engine._find_drop_y(possible_rotations[rot_idx], x)
                        return (x, rot_idx) # Возвращаем первый же валидный ход
                    except InvalidMove:
                        continue
            
            raise NoValidMovesError(
                "Не найдено ни одного валидного хода для текущей фигуры."
            )

        return best_move

    def _calculate_incremental_score(
        self, engine: TetrisEngine, original_height_profile: List[int],
        shape: Tuple[Tuple[int, int], ...], x: int, y: int
    ) -> Tuple[float, int]:
        """
        Вычисляет "штраф" для хода, не создавая новую доску.
        Возвращает (оценка, количество очищенных линий).
        """
        board = engine.board
        temp_height_profile = list(original_height_profile)
        
        piece_coords = set()
        for px, py in shape:
            abs_x, abs_y = x + px, y + py
            if not (0 <= abs_x < board.width and 0 <= abs_y < board.height):
                raise InvalidMove("Фигура выходит за границы доски")
            if board.grid[abs_y, abs_x] != 0:
                raise InvalidMove("Столкновение с существующим блоком")
            
            piece_coords.add((abs_x, abs_y))
            new_height = board.height - abs_y
            if new_height > temp_height_profile[abs_x]:
                temp_height_profile[abs_x] = new_height

        lines_cleared = 0
        cleared_rows = set()
        unique_y_coords = sorted(list(set(abs_y for _, abs_y in piece_coords)))
        
        for row_y in unique_y_coords:
            is_line_full = True
            for col_x in range(board.width):
                if board.grid[row_y, col_x] == 0 and (col_x, row_y) not in piece_coords:
                    is_line_full = False
                    break
            if is_line_full:
                lines_cleared += 1
                cleared_rows.add(row_y)

        holes = 0
        for abs_x, col_height in enumerate(temp_height_profile):
            start_y = board.height - col_height
            for row_y in range(start_y, board.height):
                if board.grid[row_y, abs_x] == 0 and (abs_x, row_y) not in piece_coords:
                    if row_y not in cleared_rows:
                        holes += 1

        bumpiness = np.sum(np.abs(np.diff(temp_height_profile)))
        aggregate_height = np.sum(temp_height_profile)

        # Веса из оригинальной статьи Pierre Dellacherie
        # https://github.com/JiangkaiWu/AI-Tetris/blob/master/ai.cpp
        score = aggregate_height * 0.51 + holes * 0.76 + bumpiness * 0.18

        return score, lines_cleared
