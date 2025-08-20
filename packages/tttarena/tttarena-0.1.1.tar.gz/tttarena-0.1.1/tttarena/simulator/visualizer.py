# tools/visualizer.py

import os
import time
from typing import Dict, Any


def clear_console():
    """Очищает консоль в зависимости от ОС."""
    os.system("cls" if os.name == "nt" else "clear")


def print_game_state(state: Dict[str, Any]):
    """
    Отрисовывает текущее состояние игры в консоли.

    Args:
        state: Словарь с состоянием игры, обычно от `engine.get_game_state()`.
               Должен содержать `board`, `score`, `current_piece_type`, `target_curve`.
    """
    board_grid = state["board"]
    target_curve = state.get("target_curve")  # Может отсутствовать
    height = len(board_grid)
    width = len(board_grid[0])

    clear_console()

    print("-" * (width * 2 + 2))

    # Создаем буфер для отрисовки, чтобы наложить кривую
    display_buffer = [["." for _ in range(width)] for _ in range(height)]

    # 1. Заполняем буфер блоками
    for y in range(height):
        for x in range(width):
            if board_grid[y][x] != 0:
                display_buffer[y][x] = "■"

    # 2. Накладываем целевую кривую
    if target_curve and len(target_curve) == width:
        for x in range(width):
            target_h = round(target_curve[x])
            if 0 < target_h <= height:
                y = height - target_h
                if (
                    display_buffer[y][x] == "."
                ):  # Рисуем кривую, только если клетка пуста
                    display_buffer[y][x] = "*"

    # 3. Выводим буфер в консоль
    for y in range(height):
        print(f"|{' '.join(display_buffer[y])}|")

    error_a = state.get("error_A", 0.0)
    print("-" * (width * 2 + 2))
    print(f"Счет (S): {state['score']} | Ошибка (A): {error_a:.2f}")
    print(
        f"Текущая: {state['current_piece_type']} | Следующая: {state['next_piece_type']}"
    )

    time.sleep(0.05)  # Небольшая задержка для восприятия
