import random
from typing import Tuple, Optional
import numpy as np

from .geometry import Board, PIECE_SHAPES, PIECE_IDS
from .exceptions import GameOver, InvalidMove
from ..sculptor.generators import PieceGenerator, generate_target_curve
from ..sculptor.metrics import get_height_profile, calculate_approximation_error


class TetrisEngine:
    """Игровой движок. Управляет логикой, состоянием поля и фигурами"""

    def __init__(self, width: int, height: int, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        self.board = Board(width, height)
        self.piece_generator = PieceGenerator(seed)
        self.seed = seed
        self.target_curve = generate_target_curve(
            self.seed, self.board.width, self.board.height
        )

        self.game_over = False
        self.current_piece_type: Optional[str] = None
        self.next_piece_type: Optional[str] = None
        self.score = 0
        self.combo_counter = -1  # -1 означает отсутствие активного комбо

        self._approximation_error_cache: Optional[float] = None

        self._spawn_next_piece()
        self._spawn_next_piece()

    def _spawn_next_piece(self):
        """Берет следующую фигуру из генератора"""
        self.current_piece_type = self.next_piece_type
        self.next_piece_type = next(self.piece_generator)

        if self.current_piece_type is None:
            return

        start_x = self.board.width // 2
        start_y = 1

        initial_shape = PIECE_SHAPES[self.current_piece_type][0]
        if not self.board.is_valid_position(initial_shape, start_x, start_y):
            self.game_over = True
            raise GameOver(
                f"Невозможно разместить новую фигуру '{self.current_piece_type}'. Игра окончена."
            )
        self._approximation_error_cache = None

    def _find_drop_y(self, piece_shape: Tuple[Tuple[int, int], ...], x: int) -> int:
        """Находит конечную Y для фигуры при 'мгновенном сбросе'"""
        y = 0
        while self.board.is_valid_position(piece_shape, x, y + 1):
            y += 1
        return y

    def _is_t_spin(self, x: int, y: int) -> bool:
        """Проверяет, был ли выполнен T-spin по правилу 3 углов."""
        if self.current_piece_type != "T":
            return False

        # Центр T-фигуры находится в локальных координатах (1, 1)
        center_x, center_y = x + 1, y + 1

        # Координаты 4 угловых клеток вокруг центра
        corners = [
            (center_x - 1, center_y - 1),  # Верхний-левый
            (center_x + 1, center_y - 1),  # Верхний-правый
            (center_x - 1, center_y + 1),  # Нижний-левый
            (center_x + 1, center_y + 1),  # Нижний-правый
        ]

        occupied_corners = 0
        for cx, cy in corners:
            # Если угол за пределами доски или занят, считаем его "занятым"
            if not (0 <= cx < self.board.width and 0 <= cy < self.board.height) or self.board.grid[cy, cx] != 0:
                occupied_corners += 1
        
        return occupied_corners >= 3

    def place_piece(self, x: int, rotation_index: int) -> int:
        """Размещает текущую фигуру, начисляет очки за T-spins и комбо."""
        if self.game_over:
            raise GameOver("Игра уже окончена.")

        piece_shapes = PIECE_SHAPES[self.current_piece_type]
        if not (0 <= rotation_index < len(piece_shapes)):
            raise InvalidMove(f"Некорректный индекс поворота: {rotation_index}")

        shape_to_place = piece_shapes[rotation_index]
        final_y = self._find_drop_y(shape_to_place, x)

        if not self.board.is_valid_position(shape_to_place, x, final_y):
            raise InvalidMove(
                f"Недопустимое конечное положение для x={x}, rotation={rotation_index}"
            )

        # Проверяем на T-spin *перед* установкой фигуры
        is_tspin = self._is_t_spin(x, final_y)

        piece_id = PIECE_IDS[self.current_piece_type]
        lines_cleared = self.board.place_piece(shape_to_place, x, final_y, piece_id)

        score_to_add = 0
        if is_tspin:
            if lines_cleared == 1:
                score_to_add = 800  # T-Spin Single
            elif lines_cleared == 2:
                score_to_add = 1200  # T-Spin Double
            elif lines_cleared == 3:
                score_to_add = 1600  # T-Spin Triple
            else: # 0 линий
                score_to_add = 400 # T-Spin
        else:
            if lines_cleared == 1:
                score_to_add = 100  # Single
            elif lines_cleared == 2:
                score_to_add = 300  # Double
            elif lines_cleared == 3:
                score_to_add = 500  # Triple
            elif lines_cleared == 4:
                score_to_add = 800  # Tetris

        self.score += score_to_add

        if lines_cleared > 0:
            self.combo_counter += 1
            if self.combo_counter > 0:
                self.score += 50 * self.combo_counter
        else:
            self.combo_counter = -1 # Сброс комбо

        self._approximation_error_cache = None
        self._spawn_next_piece()
        return lines_cleared

    def simulate_placement(self, x: int, rotation_index: int) -> Tuple[np.ndarray, int]:
        """Симулирует размещение фигуры без изменения состояния игры."""
        if self.game_over:
            raise GameOver("Нельзя симулировать ход, игра окончена.")

        piece_shapes = PIECE_SHAPES[self.current_piece_type]
        if not (0 <= rotation_index < len(piece_shapes)):
            raise InvalidMove(f"Некорректный индекс поворота: {rotation_index}")

        shape_to_place = piece_shapes[rotation_index]
        temp_grid = self.board.grid.copy()

        y = 0
        while True:
            can_move_down = True
            for px, py in shape_to_place:
                abs_x, abs_y = x + px, y + 1 + py
                if not (
                    0 <= abs_x < self.board.width
                    and 0 <= abs_y < self.board.height
                    and temp_grid[abs_y, abs_x] == 0
                ):
                    can_move_down = False
                    break
            if can_move_down:
                y += 1
            else:
                break

        for px, py in shape_to_place:
            abs_x, abs_y = x + px, y + py
            if not (
                0 <= abs_x < self.board.width
                and 0 <= abs_y < self.board.height
                and temp_grid[abs_y, abs_x] == 0
            ):
                raise InvalidMove(
                    f"Недопустимое конечное положение для симуляции x={x}, rotation={rotation_index}"
                )

        piece_id = PIECE_IDS[self.current_piece_type]
        for px, py in shape_to_place:
            abs_x, abs_y = x + px, y + py
            temp_grid[abs_y, abs_x] = piece_id

        lines_to_clear_mask = np.all(temp_grid != 0, axis=1)
        lines_cleared = int(np.sum(lines_to_clear_mask))

        if lines_cleared > 0:
            non_cleared_rows = temp_grid[~lines_to_clear_mask]
            new_grid = np.zeros_like(temp_grid)
            new_grid[lines_cleared:, :] = non_cleared_rows
            temp_grid = new_grid

        return temp_grid, lines_cleared

    def get_game_state(self):
        """Возвращает информацию о состоянии игры для бота"""
        return {
            "board": self.board.get_state(),
            "current_piece_type": self.current_piece_type,
            "next_piece_type": self.next_piece_type,
            "score": self.score,
            "is_game_over": self.game_over,
            "target_curve": self.target_curve,
        }

    def _calculate_and_cache_approximation_error(self):
        """Рассчитывает и кэширует ошибку аппроксимации"""
        height_profile = get_height_profile(
            self.board.grid, self.board.width, self.board.height
        )
        self._approximation_error_cache = calculate_approximation_error(
            height_profile, self.target_curve
        )

    def get_approximation_error(self) -> float:
        """Возвращает кэшированную ошибку аппроксимации"""
        if self._approximation_error_cache is None:
            self._calculate_and_cache_approximation_error()
        return self._approximation_error_cache

