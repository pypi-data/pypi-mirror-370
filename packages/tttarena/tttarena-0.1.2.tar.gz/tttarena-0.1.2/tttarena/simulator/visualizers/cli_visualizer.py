import os
from typing import Dict, Any, List
from .base_visualizer import BaseVisualizer

def clear_console():
    """Очищает консоль в зависимости от ОС."""
    os.system("cls" if os.name == "nt" else "clear")

class CliVisualizer(BaseVisualizer):
    """Визуализатор для отрисовки в консоли."""

    def __init__(self):
        self.game_state: Dict[str, Any] = {}
        self.target_curve: List[float] = []
        self.running = True

    def update_state(self, state: Dict[str, Any]):
        """Обновляет внутреннее состояние визуализатора."""
        self.game_state = state
        self.target_curve = self.game_state.get("target_curve", []) # Получаем из game_state

    def handle_events(self):
        """Для CLI нет событий для обработки."""
        pass

    def render(self):
        """Отрисовывает текущее состояние игры в консоли."""
        board_grid = self.game_state.get("board", [])
        target_curve = self.game_state.get("target_curve")
        height = len(board_grid)
        width = len(board_grid[0])

        clear_console()

        print("-" * (width * 2 + 2))

        display_buffer = [["." for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                if board_grid[y, x] != 0: # Используем индексацию NumPy
                    display_buffer[y][x] = "■"

        if target_curve and len(target_curve) == width:
            for x in range(width):
                target_h = round(target_curve[x])
                if 0 < target_h <= height:
                    y = height - target_h
                    if display_buffer[y][x] == ".":
                        display_buffer[y][x] = "*"

        for y in range(height):
            print(f"|{' '.join(display_buffer[y])}|")

        error_a = self.game_state.get("error_A", 0.0)
        score = self.game_state.get("score", 0)
        current_piece = self.game_state.get("current_piece_type", "N/A")
        next_piece = self.game_state.get("next_piece_type", "N/A")
        rps = self.game_state.get("rps", 0.0)

        print("-" * (width * 2 + 2))
        print(f"Счет (S): {score} | Ошибка (A): {error_a:.2f}")
        print(f"Текущая: {current_piece} | Следующая: {next_piece}")
        print(f"RPS: {rps:.2f}")

    def get_speed_delay(self) -> float:
        return 0.00

    def is_running(self) -> bool:
        return self.running

    def quit(self):
        pass
