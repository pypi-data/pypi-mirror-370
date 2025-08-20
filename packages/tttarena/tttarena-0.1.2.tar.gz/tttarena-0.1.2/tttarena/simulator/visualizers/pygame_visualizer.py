try:
    import pygame
    import sys
except ImportError:
    raise ImportError("Pygame is not installed. Please run `pip install pygame` to use PygameVisualizer.")
from typing import Dict, Any, List
from .base_visualizer import BaseVisualizer


CELL_SIZE = 30
BOARD_WIDTH_CELLS = 10
BOARD_HEIGHT_CELLS = 20

SCREEN_WIDTH = CELL_SIZE * BOARD_WIDTH_CELLS + 400
SCREEN_HEIGHT = CELL_SIZE * BOARD_HEIGHT_CELLS + 40
SCREEN_TITLE = "TTT Arena Pygame Simulator"


COLOR_BACKGROUND = (30, 30, 30)  
COLOR_GRID = (80, 80, 80)       
COLOR_TEXT = (240, 240, 240)    
COLOR_TARGET_CURVE = (255, 200, 0, 150)


PIECE_COLORS = {
    "I": (0, 200, 200),   
    "O": (200, 200, 0),   
    "T": (150, 0, 150),   
    "L": (255, 120, 0),   
    "J": (0, 0, 200),     
    "S": (0, 150, 0),     
    "Z": (200, 0, 0),     
    0: (40, 40, 40),      
}

COLOR_EMPTY_CELL_BORDER = (60, 60, 60) 
COLOR_FILLED_CELL_BORDER = (200, 200, 200) 


class PygameVisualizer(BaseVisualizer):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.game_state: Dict[str, Any] = {}
        self.target_curve: List[float] = []
        self.speed = 1.0  
        self.running = True

        self.slider_rect = pygame.Rect(SCREEN_WIDTH - 200, 50, 150, 20)
        self.slider_dragging = False

    def update_state(self, state: Dict[str, Any]):
        """Обновляет состояние для отрисовки."""
        self.game_state = state
        self.target_curve = self.game_state.get("target_curve", [])

    def _draw_grid(self):
        """Рисует сетку игрового поля."""
        for i in range(BOARD_WIDTH_CELLS + 1):
            x = (i * CELL_SIZE) + 20
            pygame.draw.line(self.screen, COLOR_GRID, (x, 20), (x, SCREEN_HEIGHT - 20), 1)
        for i in range(BOARD_HEIGHT_CELLS + 1):
            y = (i * CELL_SIZE) + 20
            pygame.draw.line(self.screen, COLOR_GRID, (20, y), (20 + BOARD_WIDTH_CELLS * CELL_SIZE, y), 1)

    def _draw_board(self):
        """Рисует ячейки на игровом поле."""
        board = self.game_state.get("board", [])

        for y, row in enumerate(board):
            for x, cell_value in enumerate(row):
                rect = pygame.Rect(
                    20 + x * CELL_SIZE,
                    20 + (BOARD_HEIGHT_CELLS - 1 - y) * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                color = PIECE_COLORS.get(cell_value, COLOR_BACKGROUND)
                pygame.draw.rect(self.screen, color, rect)

                if cell_value != 0:
                    pygame.draw.rect(self.screen, COLOR_FILLED_CELL_BORDER, rect, 2) 
                else:
                    pygame.draw.rect(self.screen, COLOR_EMPTY_CELL_BORDER, rect, 1) 

    def _draw_target_curve(self):
        """Подсвечивает целевую кривую."""
        if not self.target_curve:
            return
        
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill(COLOR_TARGET_CURVE[:3]) 
        s.set_alpha(COLOR_TARGET_CURVE[3]) 

        for x, y_val in enumerate(self.target_curve):
            y_cell = BOARD_HEIGHT_CELLS - 1 - int(y_val)
            if 0 <= y_cell < BOARD_HEIGHT_CELLS:
                
                self.screen.blit(s, (
                    20 + x * CELL_SIZE,
                    20 + y_cell * CELL_SIZE
                ))
                
                pygame.draw.rect(self.screen, (255, 255, 255), (
                    20 + x * CELL_SIZE,
                    20 + y_cell * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                ), 1) 

    def _draw_info_panel(self):
        """Рисует правую панель с метриками."""
        x_base = 20 + BOARD_WIDTH_CELLS * CELL_SIZE + 50
        y_base = SCREEN_HEIGHT - 50

        self._draw_text("METRICS", x_base, y_base, font_size=20, bold=True)
        
        metrics = {
            "Score (S)": self.game_state.get("score", 0),
            "Error (A)": self.game_state.get("error_A", 0.0),
            "Lines Cleared": self.game_state.get("total_lines_cleared", 0),
            "Pieces": self.game_state.get("piece_index", 0),
            "RPS": self.game_state.get("rps", 0.0),
        }

        for i, (label, value) in enumerate(metrics.items()):
            y = y_base - 40 * (i + 1)
            text = f"{label}: {value:.2f}" if isinstance(value, float) else f"{label}: {value}"
            self._draw_text(text, x_base, y)

        self._draw_text("Speed", self.slider_rect.x - 60, self.slider_rect.y - 5)

        
        current_piece_type = self.game_state.get("current_piece_type", None)
        next_piece_type = self.game_state.get("next_piece_type", None)

        if current_piece_type:
            self._draw_text(f"Current: {current_piece_type}", x_base, y_base - 40 * (len(metrics) + 1))
            self._draw_piece_preview(current_piece_type, x_base + 100, y_base - 40 * (len(metrics) + 1) - 10)

        if next_piece_type:
            self._draw_text(f"Next: {next_piece_type}", x_base, y_base - 40 * (len(metrics) + 2))
            self._draw_piece_preview(next_piece_type, x_base + 100, y_base - 40 * (len(metrics) + 2) - 10)

    def _draw_piece_preview(self, piece_type: str, x_offset: int, y_offset: int):
        """Рисует миниатюру фигуры."""
        
        
        shapes = {
            "I": [(0, 0), (1, 0), (2, 0), (3, 0)],
            "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
            "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
            "L": [(0, 0), (1, 0), (2, 0), (2, 1)],
            "J": [(0, 0), (1, 0), (2, 0), (0, 1)],
            "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
            "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
        }
        
        piece_shape = shapes.get(piece_type, [])
        color = PIECE_COLORS.get(piece_type, COLOR_BACKGROUND)
        preview_cell_size = CELL_SIZE // 2 

        for dx, dy in piece_shape:
            pygame.draw.rect(self.screen, color, (
                x_offset + dx * preview_cell_size,
                y_offset - dy * preview_cell_size, 
                preview_cell_size,
                preview_cell_size
            ))
            pygame.draw.rect(self.screen, COLOR_FILLED_CELL_BORDER, (
                x_offset + dx * preview_cell_size,
                y_offset - dy * preview_cell_size,
                preview_cell_size,
                preview_cell_size
            ), 1)

    def _draw_slider(self):        
        pygame.draw.rect(self.screen, COLOR_GRID, self.slider_rect, 1) 
        handle_x = self.slider_rect.x + self.slider_rect.width * self.speed
        pygame.draw.rect(self.screen, COLOR_TEXT, (handle_x - 5, self.slider_rect.y - 5, 10, self.slider_rect.height + 10))

    def _draw_text(self, text, x, y, color=COLOR_TEXT, font_size=24, bold=False):
        font = pygame.font.Font(None, font_size)
        if bold:
            font.set_bold(True)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def handle_events(self):
        """Обрабатывает события Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.slider_rect.collidepoint(event.pos):
                    self.slider_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.slider_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.slider_dragging:
                    self.speed = (event.pos[0] - self.slider_rect.x) / self.slider_rect.width
                    self.speed = max(0.0, min(1.0, self.speed))

    def render(self):
        self.screen.fill(COLOR_BACKGROUND)
        self._draw_grid()
        self._draw_board()
        self._draw_target_curve()
        self._draw_info_panel()
        self._draw_slider()
        pygame.display.flip()

    def get_speed_delay(self):
        max_delay = 0.5
        return max_delay * (1.0 - self.speed)

    def is_running(self):
        return self.running

    def quit(self):
        pygame.quit()
