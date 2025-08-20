from typing import List
import math
import numpy as np
from numba import jit


@jit(nopython=True, cache=True)
def get_height_profile(board_grid: np.ndarray, board_width: int, board_height: int) -> List[int]:
    """Вычисляет профиль высоты h(x) для текущего состояния поля."""
    profile = [0] * board_width
    for x in range(board_width):
        column = board_grid[:, x]
        if np.any(column != 0):
            first_filled_row_idx = np.argmax(column != 0)
            profile[x] = board_height - first_filled_row_idx
    return profile


@jit(nopython=True, cache=True)
def calculate_holes(grid: np.ndarray, width: int, height: int, height_profile: List[int]) -> int:
    """Считает количество пустых клеток, над которыми есть хотя бы один блок."""
    holes = 0
    for x in range(width):
        for y in range(height - height_profile[x], height):
            if grid[y, x] == 0:
                holes += 1
    return holes


@jit(nopython=True, cache=True)
def calculate_approximation_error(height_profile: List[int], target_curve: List[float]) -> float:
    """Вычисляет ошибку аппроксимации (MSE) между профилем высоты и целевой кривой."""
    if len(height_profile) != len(target_curve):
        raise ValueError(
            "Длина профиля высоты должна совпадать с длиной целевой кривой. "
            f"({len(height_profile)} != {len(target_curve)})"
        )

    squared_errors = [(h - f) ** 2 for h, f in zip(height_profile, target_curve)]

    if not squared_errors:
        return 0.0

    mse = sum(squared_errors) / len(squared_errors)
    return mse


def calculate_final_metric(score_S: float, error_A: float, max_possible_score: float) -> float:
    """Вычисляет итоговую метрику на основе счета (S) и ошибки аппроксимации (A)."""
    if score_S < 0 or error_A < 0:
        raise ValueError("Счет и ошибка не могут быть отрицательными.")
    if max_possible_score <= 0:
        raise ValueError("Максимальный счет должен быть положительным.")

    s_norm = min(score_S / max_possible_score, 1.0)
    a_norm = 1.0 / (1.0 + math.sqrt(error_A))

    if s_norm == 0 or a_norm == 0:
        return 0.0

    harmonic_mean = 2 * (s_norm * a_norm) / (s_norm + a_norm)

    return harmonic_mean
